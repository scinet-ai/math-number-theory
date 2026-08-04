/* Erdos #388 exhaustive collision sweep — independent C implementation.
 *
 * Enumerates every block of k >= 4 consecutive integers starting at s >= smin
 * with product <= N = 10^exp (exp <= 38 so N < 2^128), via a k-way merge
 * (binary min-heap over one stream per length k; for fixed k the product is
 * strictly increasing in s). Emits the same certificate as sweep.py:
 * per-k counts, total, checksum (sum of product mod 2^61-1), and every
 * collision pair classified DISJOINT / OVERLAP.
 *
 * Exactness: all arithmetic is unsigned __int128. Products are bounded by
 * 2N <= 2*10^38 < 2^129? NO — see guards: a stored product is always <= N
 * < 2^127; the one speculative next-product computation p/s*(s+k) is
 * <= p * (1 + k/s) <= 2^127 * small only when s >= k; for s < k the direct
 * recomputation loop guards overflow by early division test. exp <= 36
 * keeps every intermediate < 10^38 < 2^127. Compile: cc -O2 -o sweep sweep.c
 *
 * Usage: ./sweep EXP [SMIN]
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

typedef unsigned __int128 u128;
typedef unsigned long long u64;

#define MOD ((1ULL << 61) - 1)
#define MAXK 64
#define MAXGROUP 64

static void print_u128(u128 x, char *buf) {
    char tmp[64]; int i = 0;
    if (x == 0) { strcpy(buf, "0"); return; }
    while (x > 0) { tmp[i++] = '0' + (int)(x % 10); x /= 10; }
    int j = 0; while (i > 0) buf[j++] = tmp[--i];
    buf[j] = 0;
}

/* heap entry: current product p of block [s, s+k-1] */
typedef struct { u128 p; u64 s; int k; } Ent;

static Ent heap[MAXK + 1];
static int hn = 0;

static void heap_push(Ent e) {
    int i = ++hn; heap[i] = e;
    while (i > 1 && heap[i].p < heap[i/2].p) {
        Ent t = heap[i]; heap[i] = heap[i/2]; heap[i/2] = t; i /= 2;
    }
}
static Ent heap_pop(void) {
    Ent top = heap[1];
    heap[1] = heap[hn--];
    int i = 1;
    for (;;) {
        int l = 2*i, r = 2*i+1, m = i;
        if (l <= hn && heap[l].p < heap[m].p) m = l;
        if (r <= hn && heap[r].p < heap[m].p) m = r;
        if (m == i) break;
        Ent t = heap[i]; heap[i] = heap[m]; heap[m] = t; i = m;
    }
    return top;
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s EXP [SMIN]\n", argv[0]); return 1; }
    int exp = atoi(argv[1]);
    u64 smin = (argc > 2) ? strtoull(argv[2], NULL, 10) : 1;
    if (exp < 2 || exp > 36) { fprintf(stderr, "EXP must be in [2,36]\n"); return 1; }
    u128 N = 1; for (int i = 0; i < exp; i++) N *= 10;

    /* seed one stream per k while the initial product (start smin) fits */
    u64 counts[MAXK + 1]; memset(counts, 0, sizeof counts);
    int kmax = 0;
    for (int k = 4; k <= MAXK; k++) {
        u128 p = 1; int ok = 1;
        for (u64 i = smin; i < smin + (u64)k; i++) {
            if (p > N / i) { ok = 0; break; }   /* p*i would exceed N */
            p *= i;
        }
        if (!ok || p > N) break;
        Ent e = { p, smin, k };
        heap_push(e);
        kmax = k;
    }

    u64 total = 0, checksum = 0;
    /* collision group buffer */
    u128 prev_p = 0; int prev_valid = 0;
    Ent group[MAXGROUP]; int gn = 0;
    char b1[64], b2[64];

    long long ndisjoint = 0, noverlap = 0;

    while (hn > 0) {
        Ent e = heap_pop();
        total++;
        counts[e.k]++;
        checksum = (checksum + (u64)(e.p % MOD)) % MOD;

        if (prev_valid && e.p == prev_p) {
            if (gn < MAXGROUP) group[gn++] = e;
        } else {
            if (gn > 1) {
                for (int i = 0; i < gn; i++) for (int j = i + 1; j < gn; j++) {
                    Ent a = group[i], b = group[j];
                    if (b.s < a.s || (b.s == a.s && b.k < a.k)) { Ent t = a; a = b; b = t; }
                    u64 e1 = a.s + a.k - 1;
                    const char *kind = (e1 < b.s) ? "DISJOINT" : "OVERLAP";
                    if (e1 < b.s) ndisjoint++; else noverlap++;
                    print_u128(prev_p, b1);
                    printf("collision %s: %s = [%llu..%llu] = [%llu..%llu]\n",
                           kind, b1, a.s, e1, b.s, b.s + b.k - 1);
                }
            }
            gn = 0; group[gn++] = e;
            prev_p = e.p; prev_valid = 1;
        }

        /* advance this stream: next start s+1, product p/s*(s+k) */
        u128 np = e.p / e.s * (u128)(e.s + (u64)e.k);
        if (np <= N) {
            Ent nxt = { np, e.s + 1, e.k };
            heap_push(nxt);
        }
    }
    if (gn > 1) {
        for (int i = 0; i < gn; i++) for (int j = i + 1; j < gn; j++) {
            Ent a = group[i], b = group[j];
            if (b.s < a.s || (b.s == a.s && b.k < a.k)) { Ent t = a; a = b; b = t; }
            u64 e1 = a.s + a.k - 1;
            const char *kind = (e1 < b.s) ? "DISJOINT" : "OVERLAP";
            if (e1 < b.s) ndisjoint++; else noverlap++;
            print_u128(prev_p, b1);
            printf("collision %s: %s = [%llu..%llu] = [%llu..%llu]\n",
                   kind, b1, a.s, e1, b.s, b.s + b.k - 1);
        }
    }

    print_u128(N, b2);
    printf("# sweep.c  N=%s  smin=%llu  kmax=%d\n", b2, smin, kmax);
    for (int k = 4; k <= kmax; k++) printf("count k=%d: %llu\n", k, counts[k]);
    printf("total: %llu\n", total);
    printf("checksum: %llu\n", checksum);
    printf("disjoint_pairs: %lld  overlap_pairs: %lld\n", ndisjoint, noverlap);
    return 0;
}
