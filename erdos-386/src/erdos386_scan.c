/*
 * erdos386_scan.c — production scanner for Erdős #386 (SciNet ref 918f9da2).
 *
 * Problem: for 2 <= k <= n-2, when is C(n,k) a product of consecutive primes,
 * i.e. C(n,k) = p_i * p_{i+1} * ... * p_j (each prime to the first power)?
 * By symmetry C(n,k) = C(n,n-k), so we scan 2 <= k <= n/2 WLOG.
 *
 * Method (never touches the huge integer C(n,k) itself):
 *   Kummer/Legendre: v_p(C(n,k)) = (s_p(k) + s_p(n-k) - s_p(n)) / (p-1)
 *   where s_p is the base-p digit sum (= number of carries adding k and n-k
 *   in base p). C(n,k) is a consecutive-prime product iff
 *     (a) v_p(C(n,k)) <= 1 for every prime p <= n   (squarefree), and
 *     (b) the primes with v_p = 1 occupy consecutive indices in the ordered
 *         list of all primes (no prime > n can divide C(n,k), since C(n,k)
 *         divides n!/(k!(n-k)!) whose prime factors are all <= n).
 *   Cheap cascade: v_2 >= 2 kills almost all pairs in O(1) via popcounts;
 *   then v_3, v_5, v_7; rare survivors get the full check over all p <= n
 *   with an online contiguity test (early exit on any gap or square).
 *
 * Usage:   erdos386_scan N_LO N_HI [KMIN [KMAX]]
 *   Scans n in [N_LO, N_HI], k in [max(KMIN,2), min(KMAX, floor(n/2))].
 *   KMIN defaults to 2, KMAX to floor(n/2) (full sweep). A small KMAX (e.g.
 *   64) enables deep-n scans of the theoretically live small-k regime
 *   (solutions must have k = o(n); k = O(log^2 n) under Cramer). Shard
 *   production runs across processes by splitting [N_LO, N_HI].
 *
 * Output:  one line per solution:
 *   SOLUTION n=<n> k=<k> len=<j-i+1> primes=<p_i>*...*<p_j>
 *   plus a trailing "# STATS ..." line (pairs scanned, filter survivors,
 *   elapsed seconds) on stderr-mirrored stdout comment.
 *
 * Build:   cc -O2 -o erdos386_scan erdos386_scan.c
 * Single-threaded by design; parallelise by sharding the n-range.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

static uint32_t *primes = NULL;   /* ordered primes <= N_HI */
static int64_t nprimes = 0;

static void sieve(uint64_t limit) {
    uint8_t *comp = calloc(limit + 1, 1);
    if (!comp) { fprintf(stderr, "sieve alloc failed\n"); exit(1); }
    for (uint64_t i = 2; i * i <= limit; i++)
        if (!comp[i])
            for (uint64_t j = i * i; j <= limit; j += i) comp[j] = 1;
    int64_t cnt = 0;
    for (uint64_t i = 2; i <= limit; i++) if (!comp[i]) cnt++;
    primes = malloc(sizeof(uint32_t) * (size_t)(cnt ? cnt : 1));
    if (!primes) { fprintf(stderr, "primes alloc failed\n"); exit(1); }
    nprimes = 0;
    for (uint64_t i = 2; i <= limit; i++) if (!comp[i]) primes[nprimes++] = (uint32_t)i;
    free(comp);
}

static inline uint64_t sdig(uint64_t x, uint64_t p) {
    uint64_t s = 0;
    while (x) { s += x % p; x /= p; }
    return s;
}

/* v_p(C(n,k)) via Legendre/Kummer */
static inline uint64_t vp_binom(uint64_t n, uint64_t k, uint64_t p) {
    return (sdig(k, p) + sdig(n - k, p) - sdig(n, p)) / (p - 1);
}

/* Full exact test over all primes <= n, online contiguity. Returns 1 and
 * fills [lo_idx, hi_idx] (indices into primes[]) iff C(n,k) is a
 * consecutive-prime product. */
static int full_check(uint64_t n, uint64_t k, int64_t *lo_idx, int64_t *hi_idx) {
    int64_t lo = -1, hi = -1;
    for (int64_t i = 0; i < nprimes && primes[i] <= n; i++) {
        uint64_t p = primes[i];
        uint64_t e = vp_binom(n, k, p);
        if (e >= 2) return 0;                 /* not squarefree */
        if (e == 1) {
            if (lo < 0) { lo = i; hi = i; }
            else if (i == hi + 1) hi = i;
            else return 0;                    /* gap in the prime block */
        }
    }
    if (lo < 0) return 0;                     /* C(n,k) == 1: impossible here */
    *lo_idx = lo; *hi_idx = hi;
    return 1;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "usage: %s N_LO N_HI [KMIN]\n", argv[0]);
        return 2;
    }
    uint64_t n_lo = strtoull(argv[1], NULL, 10);
    uint64_t n_hi = strtoull(argv[2], NULL, 10);
    uint64_t kmin = (argc > 3) ? strtoull(argv[3], NULL, 10) : 2;
    uint64_t kmax = (argc > 4) ? strtoull(argv[4], NULL, 10) : UINT64_MAX;
    if (kmin < 2) kmin = 2;
    if (n_lo < 4) n_lo = 4;
    if (n_hi < n_lo) { fprintf(stderr, "empty range\n"); return 2; }

    sieve(n_hi);

    uint64_t pairs = 0, s2 = 0, s7 = 0, nsol = 0;
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    for (uint64_t n = n_lo; n <= n_hi; n++) {
        int pcn = __builtin_popcountll(n);
        uint64_t khi = n / 2;
        if (khi > kmax) khi = kmax;
        for (uint64_t k = kmin; k <= khi; k++) {
            pairs++;
            /* v_2 filter: popcount(k)+popcount(n-k)-popcount(n) = #carries */
            if (__builtin_popcountll(k) + __builtin_popcountll(n - k) - pcn >= 2)
                continue;
            s2++;
            if (vp_binom(n, k, 3) >= 2) continue;
            if (vp_binom(n, k, 5) >= 2) continue;
            if (vp_binom(n, k, 7) >= 2) continue;
            s7++;
            int64_t lo, hi;
            if (full_check(n, k, &lo, &hi)) {
                nsol++;
                printf("SOLUTION n=%llu k=%llu len=%lld primes=",
                       (unsigned long long)n, (unsigned long long)k,
                       (long long)(hi - lo + 1));
                for (int64_t i = lo; i <= hi; i++)
                    printf("%s%u", (i == lo ? "" : "*"), primes[i]);
                printf("\n");
                fflush(stdout);
            }
        }
        if ((n & 0xFFFFF) == 0)
            fprintf(stderr, "# progress n=%llu\n", (unsigned long long)n);
    }

    clock_gettime(CLOCK_MONOTONIC, &t1);
    double secs = (double)(t1.tv_sec - t0.tv_sec) + 1e-9 * (double)(t1.tv_nsec - t0.tv_nsec);
    printf("# STATS range=[%llu,%llu] kmin=%llu kmax=%s pairs=%llu v2_pass=%llu "
           "v7_pass=%llu solutions=%llu elapsed_s=%.3f rate_pairs_per_s=%.3e\n",
           (unsigned long long)n_lo, (unsigned long long)n_hi,
           (unsigned long long)kmin,
           (kmax == UINT64_MAX ? "n/2" : argv[4]), (unsigned long long)pairs,
           (unsigned long long)s2, (unsigned long long)s7,
           (unsigned long long)nsol, secs, (double)pairs / (secs > 0 ? secs : 1e-9));
    free(primes);
    return 0;
}
