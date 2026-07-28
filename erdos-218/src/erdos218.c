/*
 * erdos218.c — Erdős problem #218 (prime-gap monotonicity) tabulation tool.
 *
 * Enumerates consecutive prime gaps d_n = p_{n+1} - p_n over a value range
 * and tallies, for every consecutive-prime triple (p, q, r) whose FIRST
 * element p lies in [lo, hi):
 *      gt : d2 > d1   (i.e. r - q > q - p)   -> contributes to rho_>
 *      eq : d2 = d1                          -> contributes to rho_= and E(N)
 *      lt : d2 < d1                          -> contributes to rho_<
 *
 * Attribution by first prime of the triple makes value-range shards
 * disjoint and exactly mergeable: summing any contiguous set of CERT
 * windows starting at lo=2 up to boundary x gives the exact tallies over
 * all n <= pi(x)  (n indexes gaps: d_n vs d_{n+1}, first prime p_n).
 * Invariant: every prime in [lo, hi) starts exactly one triple, hence
 * per window  primes == gt + eq + lt.
 *
 * Output (stdout, canonical, integers only — diffable against naive218.py):
 *   CERT1 lo=A hi=B primes=P first=F last=L next=X gt=G eq=E lt=T
 *   TOTAL1 lo=A hi=B primes=P gt=G eq=E lt=T
 *   EQ n=I p=P gap=D            (only with --print-eq K and lo == 2)
 * Human-readable summary goes to stderr.
 *
 * Stitch check when merging shards: next= of a window must equal first= of
 * the following window (both are actual primes, computed independently).
 *
 * Build (own segmented sieve, no dependencies):
 *   cc -O2 -o erdos218 src/erdos218.c -lm
 * Build (primesieve backend, independent generator for cross-validation
 * and for production speed):
 *   cc -O2 -DUSE_PRIMESIEVE -I/opt/homebrew/include -L/opt/homebrew/lib \
 *      -o erdos218-ps src/erdos218.c -lprimesieve -lm
 *
 * Usage:
 *   erdos218 --lo A --hi B [--cert-width W] [--print-eq K]
 *   erdos218 --selftest            (== --lo 2 --hi 1000000 --cert-width 100000)
 *
 * The sieve automatically continues past hi until the two primes following
 * the last in-range prime have been seen (needed to complete the final
 * triples); no slack parameter is required.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

#ifdef USE_PRIMESIEVE
#include <primesieve.h>
#endif

typedef uint64_t u64;

/* ------------------------------------------------------------------ */
/* CERT windows                                                        */
/* ------------------------------------------------------------------ */
typedef struct {
    u64 primes, first, last, gt, eq, lt;
} Win;

static u64 LO, HI, W;          /* range [LO, HI), cert window width W   */
static u64 nW;                 /* number of cert windows                */
static Win *wins;
static u64 next_after;         /* first prime >= HI                     */
static u64 print_eq;           /* how many EQ lines still to print      */
static u64 total_gt, total_eq, total_lt, total_primes;
static u64 gen_count;          /* primes generated so far (stream index)*/
static int done;

static u64 prev2, prev1;       /* sliding triple window                 */

static inline void classify(u64 p, u64 q, u64 r)
{
    u64 d1 = q - p, d2 = r - q;
    Win *w = &wins[(p - LO) / W];
    if (d2 > d1)      { w->gt++; total_gt++; }
    else if (d2 == d1) {
        w->eq++; total_eq++;
        if (print_eq && LO == 2) {
            /* n = pi(p): p was the (gen_count - 2)-th prime generated,
             * and generation started at 2, so its index is gen_count-2. */
            printf("EQ n=%llu p=%llu gap=%llu\n",
                   (unsigned long long)(gen_count - 2),
                   (unsigned long long)p, (unsigned long long)d1);
            print_eq--;
        }
    }
    else              { w->lt++; total_lt++; }
}

/* feed one prime (strictly increasing) into the triple machinery */
static inline void emit_prime(u64 cur)
{
    gen_count++;
    if (prev2) {
        /* prev2 < prev1 < cur are consecutive primes */
        if (prev2 >= LO && prev2 < HI)
            classify(prev2, prev1, cur);
    }
    if (cur >= LO && cur < HI) {
        Win *w = &wins[(cur - LO) / W];
        w->primes++; total_primes++;
        if (!w->first) w->first = cur;
        w->last = cur;
    } else if (cur >= HI && !next_after) {
        next_after = cur;
    }
    prev2 = prev1;
    prev1 = cur;
    if (prev2 >= HI) done = 1;   /* every triple with first prime < HI done */
}

/* ------------------------------------------------------------------ */
/* Prime generation                                                    */
/* ------------------------------------------------------------------ */
#ifdef USE_PRIMESIEVE

static void run_stream(void)
{
    primesieve_iterator it;
    primesieve_init(&it);
    u64 start = LO < 2 ? 2 : LO;
    primesieve_jump_to(&it, start, HI + 1048576);
    while (!done) {
        u64 p = primesieve_next_prime(&it);
        if (p == PRIMESIEVE_ERROR) {
            fprintf(stderr, "primesieve iterator error\n");
            exit(1);
        }
        emit_prime(p);
    }
    primesieve_free_iterator(&it);
}

#else /* own segmented sieve of Eratosthenes */

#define SEG_SPAN  ((u64)1 << 23)          /* numbers per segment          */

static void run_stream(void)
{
    /* base primes up to sqrt of a bound comfortably past HI (the stream
     * stops within one prime gap past HI, far less than 2^20). */
    u64 bound = HI + ((u64)1 << 20);
    u64 blim = (u64)sqrtl((long double)bound) + 2;
    unsigned char *bs = calloc(blim + 1, 1);
    if (!bs) { fprintf(stderr, "oom base sieve\n"); exit(1); }
    for (u64 i = 2; i * i <= blim; i++)
        if (!bs[i])
            for (u64 j = i * i; j <= blim; j += i) bs[j] = 1;
    u64 nbase = 0;
    for (u64 i = 3; i <= blim; i++) if (!bs[i]) nbase++;
    u64 *base = malloc(nbase * sizeof(u64));
    if (!base) { fprintf(stderr, "oom base list\n"); exit(1); }
    {
        u64 k = 0;
        for (u64 i = 3; i <= blim; i++) if (!bs[i]) base[k++] = i;
    }
    free(bs);

    u64 start = LO < 2 ? 2 : LO;
    if (start <= 2) { emit_prime(2); start = 3; }
    if (!(start & 1)) start++;            /* first odd candidate          */

    u64 nbits = SEG_SPAN / 2;             /* odd numbers per segment      */
    unsigned char *seg = malloc(nbits);
    if (!seg) { fprintf(stderr, "oom segment\n"); exit(1); }

    for (u64 segLo = start; !done; segLo += SEG_SPAN) {
        u64 segHi = segLo + SEG_SPAN;     /* covers odds in [segLo,segHi) */
        memset(seg, 0, nbits);
        for (u64 b = 0; b < nbase; b++) {
            u64 p = base[b];
            if (p * p >= segHi) break;
            u64 m = p * p;
            if (m < segLo) {
                m = ((segLo + p - 1) / p) * p;
                if (!(m & 1)) m += p;     /* odd multiples only           */
            }
            for (; m < segHi; m += 2 * p)
                seg[(m - segLo) >> 1] = 1;
        }
        for (u64 i = 0; i < nbits; i++) {
            if (!seg[i]) {
                emit_prime(segLo + 2 * i);
                if (done) break;
            }
        }
    }
    free(seg);
    free(base);
}

#endif

/* ------------------------------------------------------------------ */
int main(int argc, char **argv)
{
    LO = 0; HI = 0; W = 0; print_eq = 0;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--selftest")) {
            LO = 2; HI = 1000000; if (!W) W = 100000;
        } else if (!strcmp(argv[i], "--lo") && i + 1 < argc) {
            LO = strtoull(argv[++i], NULL, 10);
        } else if (!strcmp(argv[i], "--hi") && i + 1 < argc) {
            HI = strtoull(argv[++i], NULL, 10);
        } else if (!strcmp(argv[i], "--cert-width") && i + 1 < argc) {
            W = strtoull(argv[++i], NULL, 10);
        } else if (!strcmp(argv[i], "--print-eq") && i + 1 < argc) {
            print_eq = strtoull(argv[++i], NULL, 10);
        } else {
            fprintf(stderr, "unknown arg: %s\n", argv[i]);
            return 2;
        }
    }
    if (LO < 2) LO = 2;
    if (HI <= LO) {
        fprintf(stderr,
            "usage: %s --lo A --hi B [--cert-width W] [--print-eq K] | --selftest\n",
            argv[0]);
        return 2;
    }
    if (!W) W = HI - LO;
    if (print_eq && LO != 2) {
        fprintf(stderr, "--print-eq requires --lo 2 (global prime index)\n");
        return 2;
    }
    nW = (HI - LO + W - 1) / W;
    if (nW > 50000000ULL) {
        fprintf(stderr, "too many cert windows (%llu); raise --cert-width\n",
                (unsigned long long)nW);
        return 2;
    }
    wins = calloc(nW, sizeof(Win));
    if (!wins) { fprintf(stderr, "oom windows\n"); return 1; }

    run_stream();

    if (!done) { fprintf(stderr, "internal error: stream ended early\n"); return 1; }

    /* sanity: per-window invariant primes == gt+eq+lt */
    for (u64 k = 0; k < nW; k++) {
        Win *w = &wins[k];
        if (w->primes != w->gt + w->eq + w->lt) {
            fprintf(stderr, "INVARIANT VIOLATION window %llu\n",
                    (unsigned long long)k);
            return 1;
        }
    }

    for (u64 k = 0; k < nW; k++) {
        Win *w = &wins[k];
        u64 wlo = LO + k * W;
        u64 whi = wlo + W; if (whi > HI) whi = HI;
        u64 nx = 0;
        for (u64 j = k + 1; j < nW && !nx; j++) nx = wins[j].first;
        if (!nx) nx = next_after;
        printf("CERT1 lo=%llu hi=%llu primes=%llu first=%llu last=%llu "
               "next=%llu gt=%llu eq=%llu lt=%llu\n",
               (unsigned long long)wlo, (unsigned long long)whi,
               (unsigned long long)w->primes, (unsigned long long)w->first,
               (unsigned long long)w->last, (unsigned long long)nx,
               (unsigned long long)w->gt, (unsigned long long)w->eq,
               (unsigned long long)w->lt);
    }
    printf("TOTAL1 lo=%llu hi=%llu primes=%llu gt=%llu eq=%llu lt=%llu\n",
           (unsigned long long)LO, (unsigned long long)HI,
           (unsigned long long)total_primes, (unsigned long long)total_gt,
           (unsigned long long)total_eq, (unsigned long long)total_lt);

    fprintf(stderr,
        "# [%llu,%llu) primes=%llu gt=%llu eq=%llu lt=%llu "
        "rho_>=%.9Lf rho_==%.9Lf rho_<=%.9Lf (window-local)\n",
        (unsigned long long)LO, (unsigned long long)HI,
        (unsigned long long)total_primes, (unsigned long long)total_gt,
        (unsigned long long)total_eq, (unsigned long long)total_lt,
        (long double)total_gt / total_primes,
        (long double)total_eq / total_primes,
        (long double)total_lt / total_primes);
    free(wins);
    return 0;
}
