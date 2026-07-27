/*
 * scan_least_consecutive_residues.c
 *
 * For every prime p in [p_lo, p_hi], compute
 *     r(k, m, p) = least r >= 1 such that r, r+1, ..., r+m-1 are all
 *                  k-th power residues modulo p
 * (Erdos problem #436 notation; Lambda(k,m) = limsup over p of r(k,m,p)).
 *
 * Definition details (taken literally from the problem statement):
 *   - "n is a k-th power residue mod p" means n == x^k (mod p) for some x.
 *     This includes x == 0, so any n divisible by p counts as a residue.
 *     For the primes and r-values that matter here r << p, so this
 *     convention never differs from the classical (nonzero) one.
 *   - The set of nonzero k-th power residues mod p equals the set of d-th
 *     power residues where d = gcd(k, p-1): n is one iff
 *     n^((p-1)/d) == 1 (mod p).  When d = 1 every n is a residue and
 *     r(k,m,p) = 1; such primes are counted but not scanned.
 *   - If no run of m consecutive residues exists among r = 1..p (one full
 *     period, including the wrap value p == 0 which is a residue), then
 *     none exists at all; such primes are reported as NORUN (r infinite).
 *     Only small primes can do this and they never affect the limsup.
 *
 * While scanning with target run length m, the program also records the
 * first run of every length 2..m, so one pass at m=3 yields both
 * r(k,2,p) and r(k,3,p).  The r(k,2,p) data doubles as a validation
 * against the published values Lambda(2,2)=9, Lambda(3,2)=77,
 * Lambda(5,2)=7888, Lambda(7,2)=1649375.
 *
 * Output (plain text, one record per line, flushed as produced):
 *   REC  k m p r          -- new running maximum of r(k,m,p) in this range
 *   NORUN k p             -- no run of length m exists mod p (small p only)
 *   CKPT k m p_done max argmax nprimes   -- checkpoint after each segment
 *   TOP  k m r p          -- final: the largest r values seen, descending
 *   HIST k m bucket count -- final: histogram, bucket b counts r in [2^b, 2^(b+1))
 *   SUM  k m p_lo p_hi nprimes_scanned nprimes_trivial max argmax sum_r
 *
 * Usage: scan_least_consecutive_residues k m p_lo p_hi
 *
 * Exact integer arithmetic throughout (64-bit with 128-bit products).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef uint64_t u64;
typedef __uint128_t u128;

static u64 mulmod(u64 a, u64 b, u64 p) { return (u64)((u128)a * b % p); }

static u64 powmod(u64 base, u64 exp, u64 p) {
    u64 result = 1;
    base %= p;
    while (exp) {
        if (exp & 1) result = mulmod(result, base, p);
        base = mulmod(base, base, p);
        exp >>= 1;
    }
    return result;
}

static u64 gcd64(u64 a, u64 b) { while (b) { u64 t = a % b; a = b; b = t; } return a; }

#define MAX_M 8
#define TOP_KEEP 40
#define HIST_BUCKETS 64

typedef struct { u64 r, p; } RP;

/* per run-length (2..m) stats */
static u64 run_max[MAX_M + 1], run_argmax[MAX_M + 1];
static RP  top[MAX_M + 1][TOP_KEEP];
static int top_n[MAX_M + 1];
static u64 hist[MAX_M + 1][HIST_BUCKETS];
static u128 sum_r[MAX_M + 1];

static int bucket_of(u64 r) { int b = 0; while (r >>= 1) b++; return b; }

static void top_insert(int m, u64 r, u64 p) {
    int n = top_n[m];
    if (n == TOP_KEEP && r <= top[m][n - 1].r) return;
    int i = (n < TOP_KEEP) ? n : TOP_KEEP - 1;
    while (i > 0 && top[m][i - 1].r < r) { top[m][i] = top[m][i - 1]; i--; }
    top[m][i].r = r; top[m][i].p = p;
    if (top_n[m] < TOP_KEEP) top_n[m]++;
}

int main(int argc, char **argv) {
    if (argc != 5) {
        fprintf(stderr, "usage: %s k m p_lo p_hi\n", argv[0]);
        return 2;
    }
    u64 k = strtoull(argv[1], 0, 10);
    int m = (int)strtoull(argv[2], 0, 10);
    u64 p_lo = strtoull(argv[3], 0, 10);
    u64 p_hi = strtoull(argv[4], 0, 10);
    if (k < 2 || m < 2 || m > MAX_M || p_hi < p_lo) { fprintf(stderr, "bad args\n"); return 2; }

    /* base primes up to sqrt(p_hi) for the segmented sieve */
    u64 sqrt_hi = 2;
    while (sqrt_hi * sqrt_hi < p_hi) sqrt_hi++;
    char *base_comp = calloc(sqrt_hi + 1, 1);
    u64 *base_primes = malloc((sqrt_hi + 1) * sizeof(u64));
    u64 n_base = 0;
    for (u64 i = 2; i <= sqrt_hi; i++) {
        if (!base_comp[i]) {
            base_primes[n_base++] = i;
            for (u64 j = i * i; j <= sqrt_hi; j += i) base_comp[j] = 1;
        }
    }

    const u64 SEG = 1000000;
    char *seg = malloc(SEG);
    u64 nprimes_scanned = 0, nprimes_trivial = 0;

    for (u64 lo = p_lo; lo <= p_hi; lo += SEG) {
        u64 hi = lo + SEG - 1;
        if (hi > p_hi) hi = p_hi;
        u64 width = hi - lo + 1;
        memset(seg, 0, width);
        if (lo == 0) { if (width > 0) seg[0] = 1; if (width > 1) seg[1] = 1; }
        if (lo == 1) seg[0] = 1;
        for (u64 bi = 0; bi < n_base; bi++) {
            u64 q = base_primes[bi];
            if (q * q > hi) break;
            u64 start = (lo + q - 1) / q * q;
            if (start < q * q) start = q * q;
            for (u64 j = start; j <= hi; j += q) seg[j - lo] = 1;
        }
        for (u64 off = 0; off < width; off++) {
            if (seg[off]) continue;
            u64 p = lo + off;
            if (p < 2) continue;
            u64 d = gcd64(k, p - 1);
            if (d == 1) { nprimes_trivial++; continue; }  /* every n is a k-th power: r=1 */
            u64 e = (p - 1) / d;
            int run = 0;
            u64 first_of_len[MAX_M + 1] = {0};
            u64 limit = p + (u64)m - 1;
            for (u64 n = 1; n <= limit; n++) {
                u64 nm = n % p;
                int is_res = (nm == 0) ? 1 : (powmod(nm, e, p) == 1);
                if (is_res) {
                    run++;
                    if (run >= 2 && run <= m && !first_of_len[run])
                        first_of_len[run] = n - (u64)run + 1;
                    if (run == m) break;
                } else run = 0;
            }
            nprimes_scanned++;
            for (int mm = 2; mm <= m; mm++) {
                u64 r = first_of_len[mm];
                if (!r) { if (mm == m) { printf("NORUN %llu %llu\n", (unsigned long long)k, (unsigned long long)p); fflush(stdout); } continue; }
                sum_r[mm] += r;
                hist[mm][bucket_of(r)]++;
                top_insert(mm, r, p);
                if (r > run_max[mm]) {
                    run_max[mm] = r; run_argmax[mm] = p;
                    printf("REC %llu %d %llu %llu\n", (unsigned long long)k, mm,
                           (unsigned long long)p, (unsigned long long)r);
                    fflush(stdout);
                }
            }
        }
        printf("CKPT %llu %d %llu %llu %llu %llu\n", (unsigned long long)k, m,
               (unsigned long long)hi, (unsigned long long)run_max[m],
               (unsigned long long)run_argmax[m], (unsigned long long)nprimes_scanned);
        fflush(stdout);
    }

    for (int mm = 2; mm <= m; mm++) {
        for (int i = 0; i < top_n[mm]; i++)
            printf("TOP %llu %d %llu %llu\n", (unsigned long long)k, mm,
                   (unsigned long long)top[mm][i].r, (unsigned long long)top[mm][i].p);
        for (int b = 0; b < HIST_BUCKETS; b++)
            if (hist[mm][b])
                printf("HIST %llu %d %d %llu\n", (unsigned long long)k, mm, b,
                       (unsigned long long)hist[mm][b]);
        printf("SUM %llu %d %llu %llu %llu %llu %llu %llu %llu\n",
               (unsigned long long)k, mm, (unsigned long long)p_lo, (unsigned long long)p_hi,
               (unsigned long long)nprimes_scanned, (unsigned long long)nprimes_trivial,
               (unsigned long long)run_max[mm], (unsigned long long)run_argmax[mm],
               (unsigned long long)(u64)sum_r[mm]);
    }
    fflush(stdout);
    free(base_comp); free(base_primes); free(seg);
    return 0;
}
