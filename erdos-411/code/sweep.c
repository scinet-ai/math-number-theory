/* Erdos #411 sweep: find all raw multiplier hits g_r(x) = c*x (c >= 2)
 * for LO <= x <= HI, 1 <= r <= R, where g(n) = n + phi(n).
 *
 * Independent C implementation (second implementation; cross-checked against
 * the pure-Python probe.py on overlapping ranges).
 *
 * phi via: uint32 sieve up to SIEVE_N for small values; beyond that trial
 * division by sieved primes then Brent-Pollard rho + deterministic
 * Miller-Rabin (base set valid for all n < 3.3e24) with 128-bit mulmod.
 * Per-thread memo cache exploits orbit merging.
 *
 * Output: lines "H x r c" (raw hits), plus "# ..." progress to stderr.
 * Usage: ./sweep LO HI R SIEVE_N NTHREADS
 * Safety: for x <= 1e7, r <= 40, orbit values < 2^40 * x <= 1.1e19 < 2^64.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>

typedef uint64_t u64;
typedef unsigned __int128 u128;

static u64 LO, HI, SIEVE_N;
static int R, NTHREADS;
static uint32_t *sphi;      /* sphi[i] = phi(i) for i <= SIEVE_N */
static uint32_t *primes;    /* primes up to 100000 for trial division */
static int nprimes;

static void build_sieve(void) {
    sphi = malloc((SIEVE_N + 1) * sizeof(uint32_t));
    if (!sphi) { fprintf(stderr, "sieve alloc failed\n"); exit(1); }
    for (u64 i = 0; i <= SIEVE_N; i++) sphi[i] = (uint32_t)i;
    for (u64 i = 2; i <= SIEVE_N; i++)
        if (sphi[i] == i)                     /* i prime */
            for (u64 j = i; j <= SIEVE_N; j += i)
                sphi[j] -= sphi[j] / i;
    /* trial-division primes up to 1e5 */
    int cap = 10000; primes = malloc(cap * sizeof(uint32_t)); nprimes = 0;
    for (u64 i = 2; i <= 100000 && i <= SIEVE_N; i++)
        if (sphi[i] == i - 1) {
            if (nprimes == cap) { cap *= 2; primes = realloc(primes, cap * sizeof(uint32_t)); }
            primes[nprimes++] = (uint32_t)i;
        }
}

static inline u64 mulmod(u64 a, u64 b, u64 m) { return (u64)((u128)a * b % m); }
static u64 powmod(u64 a, u64 e, u64 m) {
    u64 r = 1; a %= m;
    while (e) { if (e & 1) r = mulmod(r, a, m); a = mulmod(a, a, m); e >>= 1; }
    return r;
}
static int is_prime(u64 n) {
    if (n < 2) return 0;
    static const u64 small[] = {2,3,5,7,11,13,17,19,23,29,31,37};
    for (int i = 0; i < 12; i++) { if (n % small[i] == 0) return n == small[i]; }
    u64 d = n - 1; int s = 0;
    while (!(d & 1)) { d >>= 1; s++; }
    for (int i = 0; i < 12; i++) {
        u64 x = powmod(small[i], d, n);
        if (x == 1 || x == n - 1) continue;
        int ok = 0;
        for (int j = 0; j < s - 1; j++) {
            x = mulmod(x, x, n);
            if (x == n - 1) { ok = 1; break; }
        }
        if (!ok) return 0;
    }
    return 1;
}
static u64 rho(u64 n) {                       /* Brent; n odd composite, no small factors */
    if (!(n & 1)) return 2;
    for (u64 c = 1;; c++) {
        u64 x = 2, y = 2, d = 1, q = 1, ys = 2;
        int r = 1, m = 128;
        while (d == 1) {
            x = y;
            for (int i = 0; i < r; i++) y = (mulmod(y, y, n) + c) % n;
            int k = 0;
            while (k < r && d == 1) {
                ys = y;
                int lim = m < r - k ? m : r - k;
                for (int i = 0; i < lim; i++) {
                    y = (mulmod(y, y, n) + c) % n;
                    q = mulmod(q, x > y ? x - y : y - x, n);
                }
                u64 a = q, b = n;             /* gcd */
                while (b) { u64 t = a % b; a = b; b = t; }
                d = a; k += m;
            }
            r <<= 1;
        }
        if (d == n) {
            d = 1;
            while (d == 1) {
                ys = (mulmod(ys, ys, n) + c) % n;
                u64 a = ys > x ? ys - x : x - ys, b = n;
                while (b) { u64 t = a % b; a = b; b = t; }
                d = a;
            }
        }
        if (d != n) return d;
    }
}
/* phi of arbitrary n (n > SIEVE_N); returns phi(n) */
static u64 phi_factor(u64 n) {
    u64 res = 1;
    for (int i = 0; i < nprimes && (u64)primes[i] * primes[i] <= n; i++) {
        u64 p = primes[i];
        if (n % p == 0) {
            res *= p - 1; n /= p;
            while (n % p == 0) { res *= p; n /= p; }
        }
    }
    if (n == 1) return res;
    if (n <= SIEVE_N) return res * sphi[n];
    if (is_prime(n)) return res * (n - 1);
    /* n composite, all prime factors > 1e5 (or > last trial prime) */
    u64 stack[16]; int sp = 0; stack[sp++] = n;
    u64 fac[16]; int nf = 0;
    while (sp) {
        u64 m = stack[--sp];
        if (m <= SIEVE_N) { /* handled multiplicatively only if coprime — do full split instead */ }
        if (is_prime(m)) { fac[nf++] = m; continue; }
        u64 d = rho(m);
        stack[sp++] = d; stack[sp++] = m / d;
    }
    /* combine equal primes */
    for (int i = 0; i < nf; i++) {
        if (fac[i] == 0) continue;
        u64 p = fac[i], e = 1;
        for (int j = i + 1; j < nf; j++)
            if (fac[j] == p) { e++; fac[j] = 0; }
        res *= p - 1;
        for (u64 k = 1; k < e; k++) res *= p;
    }
    return res;
}

/* per-thread memo cache: open addressing, power-of-2 size */
#define CBITS 23
#define CSIZE ((size_t)1 << CBITS)
typedef struct { u64 key, val; } centry;

static u64 phi_of(u64 n, centry *cache) {
    if (n <= SIEVE_N) return sphi[n];
    size_t h = (size_t)((n * 0x9E3779B97F4A7C15ULL) >> (64 - CBITS));
    if (cache[h].key == n) return cache[h].val;
    u64 v = phi_factor(n);
    cache[h].key = n; cache[h].val = v;
    return v;
}

typedef struct { u64 lo, hi; int tid; FILE *out; } job;

static void *worker(void *arg) {
    job *J = arg;
    centry *cache = calloc(CSIZE, sizeof(centry));
    char buf[128];
    for (u64 x = J->lo; x <= J->hi; x++) {
        u64 v = x;
        for (int r = 1; r <= R; r++) {
            if (v > 4600000000000000000ULL) {   /* g(v)<=2v: avoid u64 overflow */
                fprintf(J->out, "T %llu %d %llu\n",
                        (unsigned long long)x, r, (unsigned long long)v);
                break;
            }
            v += phi_of(v, cache);
            if (v % x == 0) {
                u64 c = v / x;
                if (c >= 2) {
                    snprintf(buf, sizeof buf, "H %llu %d %llu\n",
                             (unsigned long long)x, r, (unsigned long long)c);
                    fputs(buf, J->out);
                }
            }
        }
        if ((x & 0xFFFFF) == 0) { fprintf(stderr, "# t%d at %llu\n", J->tid, (unsigned long long)x); fflush(J->out); }
    }
    free(cache);
    return NULL;
}

int main(int argc, char **argv) {
    if (argc != 6) { fprintf(stderr, "usage: %s LO HI R SIEVE_N NTHREADS\n", argv[0]); return 1; }
    LO = strtoull(argv[1], 0, 10); HI = strtoull(argv[2], 0, 10);
    R = atoi(argv[3]); SIEVE_N = strtoull(argv[4], 0, 10); NTHREADS = atoi(argv[5]);
    build_sieve();
    fprintf(stderr, "# sieve built to %llu\n", (unsigned long long)SIEVE_N);
    pthread_t th[64]; job J[64];
    u64 span = (HI - LO + 1 + NTHREADS - 1) / NTHREADS;
    for (int t = 0; t < NTHREADS; t++) {
        char fn[64]; snprintf(fn, sizeof fn, "sweep_part_%d.txt", t);
        J[t].lo = LO + t * span;
        J[t].hi = J[t].lo + span - 1 < HI ? J[t].lo + span - 1 : HI;
        J[t].tid = t; J[t].out = fopen(fn, "w");
        pthread_create(&th[t], 0, worker, &J[t]);
    }
    for (int t = 0; t < NTHREADS; t++) { pthread_join(th[t], 0); fclose(J[t].out); }
    fprintf(stderr, "# done\n");
    return 0;
}
