/* sieve_fmin.c — certified table of f(a) = min{n : phi(n) = a} for all totient
 * values a <= A_max, via a segmented factoring sieve over n in [1, N].
 *
 * Certification (see computation.md, Lemma C): with R10 = prod_{p<=29} p/(p-1)
 * = 6469693230/1021870080 = 6.33119... and A_max = floor(N/R10), every n > N
 * (N <= 31# = 200560490130) has phi(n) > A_max.  Hence:
 *   (i)  every totient value a <= A_max has ALL its preimages <= N, so it is
 *        seen by the sieve and its FIRST occurrence (in increasing n) is f(a);
 *   (ii) the emitted list of a <= A_max with f(a) >= 2a is complete.
 *
 * Output (stdout), one line per event, in increasing n:
 *   E a n        first occurrence with n >= 2a          (ratio >= 2, exact)
 *   H a n        first occurrence with 19a <= 10n < 20a (1.9 <= ratio < 2)
 *   R a n        new running-record ratio n/a (exact cross-multiplied compare)
 *   DONE N A_max totients ge2 maxratio
 * Progress goes to stderr (safe to interrupt: results certified for the
 * completed prefix [1, M] with a <= M/R10).
 *
 * Usage: ./sieve_fmin [N] [tabledump]   (default N = 2^33)
 * If tabledump is given, every pair "a f(a)" (a <= A_max) is written to that
 * file (only sensible for small N; used by the independent cross-check).
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <time.h>

typedef unsigned __int128 u128;
typedef uint64_t u64;
typedef uint32_t u32;

static u64 mulinv64(u64 p) {            /* inverse of odd p mod 2^64 */
    u64 x = p;                          /* Newton: correct to 64 bits in 5 steps */
    for (int i = 0; i < 5; i++) x *= 2 - p * x;
    return x;
}

int main(int argc, char **argv) {
    u64 N = (argc > 1) ? strtoull(argv[1], 0, 10) : (1ULL << 33);
    if (N > 200560490130ULL) { fprintf(stderr, "N must be <= 31#\n"); return 1; }
    u64 A_max = (u64)(((u128)N * 1021870080ULL) / 6469693230ULL);
    /* second leg of Lemma C: omega(n) >= 11 forces phi(n) >= phi(31#) */
    if (A_max > 30656102400ULL) A_max = 30656102400ULL;
    FILE *dump = (argc > 2) ? fopen(argv[2], "w") : NULL;
    fprintf(stderr, "N=%llu A_max=%llu\n", (unsigned long long)N,
            (unsigned long long)A_max);

    /* --- primes up to sqrt(N) --- */
    u64 sq = (u64)sqrtl((long double)N) + 2;
    char *comp = calloc(sq + 1, 1);
    u32 *primes = malloc(sizeof(u32) * (sq / 8 + 64));
    u64 *pinv   = malloc(sizeof(u64) * (sq / 8 + 64));
    u64 *plim   = malloc(sizeof(u64) * (sq / 8 + 64));
    u32 np = 0;
    for (u64 i = 3; i <= sq; i += 2) {
        if (comp[i]) continue;
        primes[np] = (u32)i;
        pinv[np]   = mulinv64(i);
        plim[np]   = UINT64_MAX / i;
        np++;
        for (u64 j = i * i; j <= sq; j += 2 * i) comp[j] = 1;
    }
    free(comp);
    fprintf(stderr, "odd primes <= %llu: %u\n", (unsigned long long)sq, np);

    /* --- state --- */
    const u64 S = 1ULL << 24;
    u64 *rem = malloc(S * 8), *phv = malloc(S * 8);
    u64 *seen = calloc((A_max >> 6) + 2, 8);
    if (!rem || !phv || !seen) { fprintf(stderr, "alloc failed\n"); return 1; }
    u64 totients = 0, ge2 = 0, best_a = 1, best_n = 1;
    time_t t0 = time(0);
    u64 segdone = 0;

    for (u64 L = 1; L <= N; L += S) {
        u64 Rend = (L + S <= N) ? L + S : N + 1;   /* n in [L, Rend) */
        u64 len = Rend - L;
        for (u64 i = 0; i < len; i++) { rem[i] = L + i; phv[i] = 1; }
        /* p = 2 via ctz */
        for (u64 m = (L & 1) ? L + 1 : L; m < Rend; m += 2) {
            u64 i = m - L;
            int v = __builtin_ctzll(m);
            rem[i] >>= v;
            phv[i] <<= (v - 1);
        }
        /* odd primes with p^2 < Rend */
        for (u32 k = 0; k < np; k++) {
            u64 p = primes[k];
            if (p * p >= Rend) break;
            u64 iv = pinv[k], lim = plim[k];
            u64 m0 = ((L + p - 1) / p) * p;
            for (u64 m = m0; m < Rend; m += p) {
                u64 i = m - L;
                phv[i] *= (p - 1);
                u64 r = rem[i] * iv;        /* = rem/p (p | rem guaranteed) */
                for (;;) {
                    u64 t = r * iv;
                    if (t > lim) break;     /* p does not divide r */
                    r = t;
                    phv[i] *= p;
                }
                rem[i] = r;
            }
        }
        /* finalize + first-occurrence scan (increasing n) */
        for (u64 i = 0; i < len; i++) {
            u64 n = L + i;
            u64 a = (rem[i] > 1) ? phv[i] * (rem[i] - 1) : phv[i];
            if (a > A_max) continue;
            if (seen[a >> 6] & (1ULL << (a & 63))) continue;
            seen[a >> 6] |= 1ULL << (a & 63);
            totients++;
            if (dump) fprintf(dump, "%llu %llu\n", (unsigned long long)a,
                              (unsigned long long)n);
            if (n >= 2 * a) { ge2++; printf("E %llu %llu\n",
                (unsigned long long)a, (unsigned long long)n); }
            else if (10 * n >= 19 * a) printf("H %llu %llu\n",
                (unsigned long long)a, (unsigned long long)n);
            if ((u128)n * best_a > (u128)best_n * a) {
                best_a = a; best_n = n;
                printf("R %llu %llu %.6f\n", (unsigned long long)a,
                       (unsigned long long)n, (double)n / (double)a);
            }
        }
        segdone++;
        if ((segdone & 15) == 0 || Rend > N) {
            fflush(stdout);
            fprintf(stderr, "[%lds] done n<%llu  totients=%llu ge2=%llu best=%llu/%llu=%.6f\n",
                    (long)(time(0) - t0), (unsigned long long)Rend,
                    (unsigned long long)totients, (unsigned long long)ge2,
                    (unsigned long long)best_n, (unsigned long long)best_a,
                    (double)best_n / (double)best_a);
        }
    }
    printf("DONE %llu %llu %llu %llu %.6f\n", (unsigned long long)N,
           (unsigned long long)A_max, (unsigned long long)totients,
           (unsigned long long)ge2, (double)best_n / (double)best_a);
    fflush(stdout);
    if (dump) fclose(dump);
    return 0;
}
