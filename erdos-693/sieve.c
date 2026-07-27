/* sieve.c — Erdős #693: maximal gap between integers in [n, n^k] having a
 * divisor in the open interval (n, 2n).
 *
 * A = { m in [n, n^k] : exists d, n < d < 2n, d | m }.
 * G(n,k) = max over consecutive elements a_i < a_{i+1} of A of (a_{i+1} - a_i).
 *
 * Method: segmented bitset. For each d in [n+1, 2n-1] mark all multiples of d
 * inside [n, n^k]; then scan the bitset for the maximal gap between set bits.
 * Work ~ log(2) * n^k marks; memory = one 16 MiB segment.
 *
 * Modes:
 *   ./sieve single <n> <k> [--append FILE] [--ckpt FILE]
 *   ./sieve range  <n_lo> <n_hi> <k> [--append FILE]
 *
 * Output line (one per n, single write() with O_APPEND, also echoed to stdout):
 *   n,k,G,gap_start,gap_end,count,seconds
 * where count = |A|, gap_start/gap_end are the witness pair (first occurrence
 * of the maximal gap), G = gap_end - gap_start.
 *
 * Checkpoint (single-n mode, every ~30 s, atomic tmp+rename), resume with the
 * same --ckpt file:  "n k next_L prev best_gap best_start count"
 *
 * Deterministic; no randomness. Build: clang -O3 -o sieve sieve.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <time.h>

#ifndef SEG_BITS_LOG
#define SEG_BITS_LOG 22
#endif
#define SEG_BITS (1ULL << SEG_BITS_LOG) /* bitset segment; 22 -> 0.5 MiB (L2-resident; benchmarked fastest for n up to 1e6, esp. with 3 concurrent workers) */

static double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static void append_line(const char *path, const char *line) {
    if (!path) return;
    int fd = open(path, O_WRONLY | O_APPEND | O_CREAT, 0644);
    if (fd < 0) { perror("open append"); exit(2); }
    ssize_t r = write(fd, line, strlen(line));
    if (r != (ssize_t)strlen(line)) { perror("write append"); exit(2); }
    close(fd);
}

/* State carried across segments for one (n,k) run */
typedef struct {
    uint64_t n, N;        /* interval is [n, N], N = n^k */
    uint64_t next_L;      /* next segment start (resume point) */
    uint64_t prev;        /* last set bit seen so far (0 = none yet) */
    uint64_t best_gap, best_start;
    uint64_t count;       /* |A| so far */
} run_state;

static void ckpt_write(const char *path, const run_state *st, int k) {
    if (!path) return;
    char tmp[4096];
    snprintf(tmp, sizeof tmp, "%s.tmp", path);
    FILE *f = fopen(tmp, "w");
    if (!f) { perror("ckpt open"); return; }
    fprintf(f, "%llu %d %llu %llu %llu %llu %llu\n",
            (unsigned long long)st->n, k,
            (unsigned long long)st->next_L, (unsigned long long)st->prev,
            (unsigned long long)st->best_gap, (unsigned long long)st->best_start,
            (unsigned long long)st->count);
    fclose(f);
    rename(tmp, path);
}

static int ckpt_read(const char *path, run_state *st, int k) {
    if (!path) return 0;
    FILE *f = fopen(path, "r");
    if (!f) return 0;
    unsigned long long n_, L_, p_, g_, s_, c_;
    int k_;
    int ok = fscanf(f, "%llu %d %llu %llu %llu %llu %llu",
                    &n_, &k_, &L_, &p_, &g_, &s_, &c_) == 7;
    fclose(f);
    if (!ok || n_ != st->n || k_ != k) return 0;
    st->next_L = L_; st->prev = p_; st->best_gap = g_;
    st->best_start = s_; st->count = c_;
    return 1;
}

/* Run one n. bits: caller-provided segment buffer. nxt: buffer of >= n u64. */
static void run_one(uint64_t n, int k, uint64_t *bits, uint64_t *nxt,
                    const char *append_path, const char *ckpt_path) {
    double t0 = now_sec(), t_ck = t0;
    run_state st;
    memset(&st, 0, sizeof st);
    st.n = n;
    st.N = n;
    for (int i = 1; i < k; i++) st.N *= n; /* n^k */
    st.next_L = n;

    int resumed = ckpt_read(ckpt_path, &st, k);
    if (resumed)
        fprintf(stderr, "[resume] n=%llu k=%d from L=%llu\n",
                (unsigned long long)n, k, (unsigned long long)st.next_L);

    uint64_t nd = 2 * n - 1 - (n + 1) + 1; /* number of divisors d in (n,2n) */
    if (2 * n - 1 < n + 1) nd = 0;

    /* init next-multiple table for segment start */
    for (uint64_t i = 0; i < nd; i++) {
        uint64_t d = n + 1 + i;
        uint64_t m = (st.next_L + d - 1) / d * d; /* smallest multiple >= next_L */
        if (m < d) m = d;
        nxt[i] = m;
    }

    while (st.next_L <= st.N) {
        uint64_t L = st.next_L;
        uint64_t R = L + SEG_BITS;                 /* exclusive */
        if (R > st.N + 1 || R < L) R = st.N + 1;   /* cap (and overflow guard) */
        uint64_t span = R - L;
        uint64_t words = (span + 63) >> 6;
        memset(bits, 0, words * 8);

        for (uint64_t i = 0; i < nd; i++) {
            uint64_t d = n + 1 + i;
            uint64_t m = nxt[i];
            for (; m < R; m += d) {
                uint64_t off = m - L;
                bits[off >> 6] |= 1ULL << (off & 63);
            }
            nxt[i] = m;
        }

        /* scan for gaps */
        for (uint64_t w = 0; w < words; w++) {
            uint64_t x = bits[w];
            if (!x) continue;
            st.count += (uint64_t)__builtin_popcountll(x);
            uint64_t base = L + (w << 6);
            while (x) {
                uint64_t b = (uint64_t)__builtin_ctzll(x);
                uint64_t m = base + b;
                if (st.prev) {
                    uint64_t g = m - st.prev;
                    if (g > st.best_gap) { st.best_gap = g; st.best_start = st.prev; }
                }
                st.prev = m;
                x &= x - 1;
            }
        }

        st.next_L = R;
        if (ckpt_path && now_sec() - t_ck > 30.0) {
            ckpt_write(ckpt_path, &st, k);
            t_ck = now_sec();
        }
        if (R == st.N + 1) break;
    }

    double el = now_sec() - t0;
    char line[512];
    snprintf(line, sizeof line, "%llu,%d,%llu,%llu,%llu,%llu,%.3f\n",
             (unsigned long long)n, k, (unsigned long long)st.best_gap,
             (unsigned long long)st.best_start,
             (unsigned long long)(st.best_start + st.best_gap),
             (unsigned long long)st.count, el);
    fputs(line, stdout);
    fflush(stdout);
    append_line(append_path, line);
    if (ckpt_path) unlink(ckpt_path);
}

int main(int argc, char **argv) {
    if (argc < 4) {
        fprintf(stderr, "usage: %s single n k [--append F] [--ckpt F]\n"
                        "       %s range n_lo n_hi k [--append F]\n",
                argv[0], argv[0]);
        return 1;
    }
    const char *append_path = NULL, *ckpt_path = NULL;
    for (int i = 1; i < argc - 1; i++) {
        if (!strcmp(argv[i], "--append")) append_path = argv[i + 1];
        if (!strcmp(argv[i], "--ckpt")) ckpt_path = argv[i + 1];
    }
    uint64_t *bits = malloc(SEG_BITS / 8);
    if (!bits) { perror("malloc bits"); return 2; }

    if (!strcmp(argv[1], "single")) {
        uint64_t n = strtoull(argv[2], NULL, 10);
        int k = atoi(argv[3]);
        uint64_t *nxt = malloc(n * sizeof(uint64_t));
        if (!nxt) { perror("malloc nxt"); return 2; }
        run_one(n, k, bits, nxt, append_path, ckpt_path);
        free(nxt);
    } else if (!strcmp(argv[1], "range")) {
        uint64_t lo = strtoull(argv[2], NULL, 10);
        uint64_t hi = strtoull(argv[3], NULL, 10);
        int k = atoi(argv[4]);
        uint64_t *nxt = malloc(hi * sizeof(uint64_t));
        if (!nxt) { perror("malloc nxt"); return 2; }
        for (uint64_t n = lo; n <= hi; n++)
            run_one(n, k, bits, nxt, append_path, NULL);
        free(nxt);
    } else {
        fprintf(stderr, "unknown mode %s\n", argv[1]);
        return 1;
    }
    free(bits);
    return 0;
}
