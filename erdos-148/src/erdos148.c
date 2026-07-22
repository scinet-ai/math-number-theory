/* erdos148.c — exact counting of Egyptian-fraction representations of 1.
 *
 * F(k)  = #{ 1 = 1/n_1 + ... + 1/n_k,  1 <= n_1 <  n_2 <  ... <  n_k }   (OEIS A006585)
 * Fm(k) = #{ 1 = 1/x_1 + ... + 1/x_k,  0 <  x_1 <= x_2 <= ... <= x_k }   (OEIS A002966)
 *
 * Method: depth-first search over denominators in increasing order with the exact
 * per-level bounds
 *     n > q/p                (else the remainder would be <= 0 with terms left)
 *     n <= j*q/p             (else even j copies of 1/n cannot reach p/q)
 * and the final TWO levels closed in O(d(q^2)) via the classical divisor identity:
 * 1/a + 1/b = p/q  (gcd(p,q)=1)  <=>  (pa - q)(pb - q) = q^2.  Writing d = pa - q,
 * solutions correspond one-to-one to divisors d | q^2 with d ≡ -q (mod p); a < b
 * iff d < q (a = b iff d = q).  The factorization of q is maintained incrementally
 * down the tree (each chosen n is factored by a smallest-prime-factor sieve), so
 * q^2's divisors are enumerated without ever factoring large integers.
 * Denominators at the closed levels may reach the Sylvester bound (~10^13 for k=8);
 * they are never enumerated explicitly.
 *
 * Modes:
 *   -k K -v distinct|multi          count for k = K
 *   --prefix a,b,c                  count only the subtree with the first terms fixed
 *   --enum D                        print the depth-D prefixes the DFS visits (sharding)
 *   --naive2                        replace the divisor closure with a trial loop at j==2
 *                                   (independent formula path; for cross-validation)
 *   --sieve N                       sieve limit (default 2e7)
 *
 * All arithmetic in unsigned/signed __int128 where products appear; hard runtime
 * guards (exit != 0) rather than silent wraparound anywhere an assumption could fail.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <inttypes.h>

typedef uint64_t u64;
typedef __uint128_t u128;
typedef __int128 i128;

#define MAXF 48            /* max distinct primes tracked in q */

typedef struct { u64 p; int e; } Fac;

static uint32_t *spf = NULL;   /* smallest prime factor */
static u64 sieve_max = 20000000ULL;

static int g_multi = 0;        /* 0: strictly increasing; 1: non-decreasing */
static int g_naive2 = 0;       /* use trial loop instead of divisor closure at j==2 */
static int g_enum_depth = 0;   /* if >0: print prefixes at this depth instead of counting */
static int g_k = 0;

static u64 total = 0;          /* solution count */
static u64 st_j2 = 0;          /* #closure calls */
static u64 st_div = 0;         /* #divisor leaves visited */
static u64 st_nodes = 0;       /* #DFS nodes */

static u64 g_prefix[16]; static int g_nprefix = 0;

static void die(const char *msg) { fprintf(stderr, "FATAL: %s\n", msg); exit(2); }

static void build_sieve(void) {
    spf = malloc((sieve_max + 1) * sizeof(uint32_t));
    if (!spf) die("sieve alloc");
    memset(spf, 0, (sieve_max + 1) * sizeof(uint32_t));
    for (u64 i = 2; i <= sieve_max; i++)
        if (!spf[i])
            for (u64 j = i; j <= sieve_max; j += i)
                if (!spf[j]) spf[j] = (uint32_t)i;
}

static u128 gcd128(u128 a, u128 b) { while (b) { u128 t = a % b; a = b; b = t; } return a; }

/* out = factors(q) ∪ factors(n), minus the valuations of g; g must be fully consumed. */
static int merge_factors(const Fac *qf, int nqf, u64 n, u128 g, Fac *out) {
    int m = 0;
    for (int i = 0; i < nqf; i++) out[m++] = qf[i];
    if (n > sieve_max) { fprintf(stderr, "FATAL: n=%" PRIu64 " exceeds sieve %" PRIu64 "\n", n, sieve_max); exit(4); }
    u64 x = n;
    while (x > 1) {
        u64 pr = spf[x]; int e = 0;
        while (x % pr == 0) { x /= pr; e++; }
        int found = -1;
        for (int i = 0; i < m; i++) if (out[i].p == pr) { found = i; break; }
        if (found >= 0) out[found].e += e;
        else { if (m >= MAXF) die("MAXF overflow"); out[m].p = pr; out[m].e = e; m++; }
    }
    u128 gg = g;
    for (int i = 0; i < m && gg > 1; i++)
        while (out[i].e > 0 && gg % out[i].p == 0) { gg /= out[i].p; out[i].e--; }
    if (gg != 1) die("gcd not consumed by tracked factorization");
    int w = 0;
    for (int i = 0; i < m; i++) if (out[i].e > 0) out[w++] = out[i];
    return w;
}

/* ---- j == 2 closure: count divisors d | q^2, dlow <= d < q (or <= q), d ≡ -q (mod p) ---- */
static u64 cl_p;               /* p (fits u64; guarded) */
static u128 cl_q;
static u64 cl_target;          /* (-q) mod p */
static i128 cl_dlow;
static int cl_le;              /* allow d == q (multi variant) */
static u64 cl_cnt;

static void divrec(const Fac *qf, int i, int nqf, u128 d, u64 dmod) {
    if (d > cl_q) return;                      /* every deeper product only grows d */
    if (i == nqf) {
        st_div++;
        if ((i128)d >= cl_dlow && (d < cl_q || (cl_le && d == cl_q)) && dmod == cl_target)
            cl_cnt++;
        return;
    }
    u64 pr = qf[i].p; int e2 = 2 * qf[i].e;
    u128 dd = d; u64 mm = dmod;
    for (int t = 0; ; t++) {
        divrec(qf, i + 1, nqf, dd, mm);
        if (t == e2) break;
        dd *= pr;
        if (cl_p > 1) mm = (u64)(((u128)mm * pr) % cl_p);
        if (dd > cl_q) break;                  /* monotone in t: all further t fail too */
    }
}

static u64 count2_closure(u128 p, u128 q, u64 last, const Fac *qf, int nqf) {
    if (p > 0x7fffffffffffffffULL) die("p exceeds 2^63 at closure");
    cl_p = (u64)p; cl_q = q;
    u64 qmodp = cl_p == 1 ? 0 : (u64)(q % cl_p);
    cl_target = cl_p == 1 ? 0 : (cl_p - qmodp) % cl_p;
    u64 amin = g_multi ? last : last + 1;
    i128 dlow = (i128)((u128)cl_p * amin) - (i128)q;
    if (dlow < 1) dlow = 1;
    cl_dlow = dlow; cl_le = g_multi; cl_cnt = 0;
    divrec(qf, 0, nqf, (u128)1, cl_p == 1 ? 0 : 1 % cl_p);
    return cl_cnt;
}

/* Independent formula path: trial loop over a, checking q*a % (p*a - q) == 0. */
static u64 count2_naive(u128 p, u128 q, u64 last) {
    u64 amin = g_multi ? last : last + 1;
    u64 lo = (u64)(q / p) + 1; if (lo < amin) lo = amin;
    u128 hi128 = 2 * q / p;
    if (hi128 > 0xffffffffffffffffULL) die("naive2 range exceeds u64");
    u64 hi = (u64)hi128, cnt = 0;
    for (u64 a = lo; a <= hi; a++) {
        u128 d = (u128)p * a - q;
        u128 num = q * a;
        if (num % d == 0) {
            u128 b = num / d;
            if (g_multi ? (b >= a) : (b > a)) cnt++;
        }
    }
    return cnt;
}

/* ---- DFS ---- */
static void dfs(u128 p, u128 q, int j, u64 last, const Fac *qf, int nqf, int depth) {
    st_nodes++;
    if (g_enum_depth > 0 && depth == g_enum_depth) {      /* sharding: emit prefix */
        for (int i = 0; i < depth; i++)
            printf("%" PRIu64 "%s", g_prefix[i], i + 1 < depth ? "," : "\n");
        return;
    }
    if (j == 2) {
        if (g_enum_depth > 0) die("enum depth reached j==2");
        st_j2++;
        total += g_naive2 ? count2_naive(p, q, last)
                          : count2_closure(p, q, last, qf, nqf);
        return;
    }
    u64 lo = (u64)(q / p) + 1;
    u64 nmin = g_multi ? last : last + 1;
    if (lo < nmin) lo = nmin;
    if (lo < 2) lo = 2;                    /* 1/1 leaves 0 for the j-1 >= 1 terms left */
    u128 hi128 = (u128)j * q / p;
    if (hi128 > 0x7fffffffffffffffULL) die("loop bound exceeds 2^63 (unexpected branch)");
    u64 hi = (u64)hi128;
    for (u64 n = lo; n <= hi; n++) {
        u128 P = (u128)p * n - q;          /* > 0 since n > q/p */
        u128 Q = q * n;
        u128 g = gcd128(P, Q);
        P /= g; Q /= g;
        Fac nf2[MAXF];
        int nn = merge_factors(qf, nqf, n, g, nf2);
        g_prefix[depth] = n;
        dfs(P, Q, j - 1, n, nf2, nn, depth + 1);
    }
}

int main(int argc, char **argv) {
    int k = 0; const char *variant = NULL; const char *prefix_arg = NULL;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-k") && i + 1 < argc) k = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-v") && i + 1 < argc) variant = argv[++i];
        else if (!strcmp(argv[i], "--prefix") && i + 1 < argc) prefix_arg = argv[++i];
        else if (!strcmp(argv[i], "--enum") && i + 1 < argc) g_enum_depth = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--naive2")) g_naive2 = 1;
        else if (!strcmp(argv[i], "--sieve") && i + 1 < argc) sieve_max = strtoull(argv[++i], NULL, 10);
        else { fprintf(stderr, "unknown arg: %s\n", argv[i]); return 2; }
    }
    if (k < 1 || k > 12 || !variant) die("usage: erdos148 -k K -v distinct|multi [--prefix a,b,c] [--enum D] [--naive2]");
    if (!strcmp(variant, "distinct")) g_multi = 0;
    else if (!strcmp(variant, "multi")) g_multi = 1;
    else die("variant must be distinct|multi");
    g_k = k;

    build_sieve();

    /* start from r = 1 - sum(1/prefix_i), factoring as we go */
    u128 P = 1, Q = 1;
    Fac qf[MAXF]; int nqf = 0;
    u64 last = 0; int depth = 0;
    if (prefix_arg) {
        char *s = strdup(prefix_arg), *tok;
        for (tok = strtok(s, ","); tok; tok = strtok(NULL, ",")) {
            u64 n = strtoull(tok, NULL, 10);
            if (n < 1) die("bad prefix element");
            if (depth > 0 && (g_multi ? n < last : n <= last)) die("prefix not increasing");
            i128 newP = (i128)((u128)P * n) - (i128)Q;
            if (newP <= 0) { printf("0\n"); return 0; }   /* remainder <= 0: empty subtree */
            u128 Pn = (u128)newP, Qn = Q * n;
            u128 g = gcd128(Pn, Qn);
            Pn /= g; Qn /= g;
            Fac nf2[MAXF];
            nqf = merge_factors(qf, nqf, n, g, nf2);
            memcpy(qf, nf2, sizeof(Fac) * nqf);
            P = Pn; Q = Qn;
            g_prefix[depth] = n; last = n; depth++;
        }
        free(s);
    }
    int j = k - depth;
    if (j < 1) die("prefix longer than k-1");
    if (g_enum_depth > 0 && g_enum_depth > k - 3) die("enum depth must be <= k-3");

    if (j == 1) {
        total = (P == 1 && (g_multi ? Q >= last : Q > last) && Q >= 2) ? 1 : 0;
        if (k == 1 && depth == 0) total = 1;               /* 1 = 1/1 */
    } else if (j == 2) {
        st_j2++;
        total = g_naive2 ? count2_naive(P, Q, last)
                         : count2_closure(P, Q, last, qf, nqf);
    } else {
        dfs(P, Q, j, last, qf, nqf, depth);
    }

    if (g_enum_depth == 0) {
        printf("%" PRIu64 "\n", total);
        fprintf(stderr, "stats: nodes=%" PRIu64 " j2_calls=%" PRIu64 " divisor_leaves=%" PRIu64 "\n",
                st_nodes, st_j2, st_div);
    }
    return 0;
}
