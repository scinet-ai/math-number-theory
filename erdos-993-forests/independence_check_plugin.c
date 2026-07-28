/* independence_check_plugin.c
 *
 * OUTPROC plugin for nauty's gentreeg: for every generated tree, compute the
 * independence polynomial exactly in 64-bit integers and test the coefficient
 * sequence for unimodality (the Alavi--Malde--Schwenk--Erdos conjecture,
 * Erdos problem #993) and, as a by-product, for log-concavity.
 *
 * Build (from the nauty source directory, after ./configure && make):
 *   clang -O3 -march=native -DMAXN=32 -DOUTPROC=check_tree -DSUMMARY=check_summary \
 *         -DPLUGIN_INIT='{ check_init(); }' \
 *         -o gentreeg_independence gentreeg.c independence_check_plugin.c nauty.a
 *
 * Contract with gentreeg (see comments in gentreeg.c):
 *   check_tree(FILE *f, int *par, int n) is called once per tree;
 *   vertices are 1..n and the edge set is {j, par[j]} for j = 2..n.
 *   gentreeg emits parent arrays with par[j] < j; we assert this on every
 *   vertex, so a violation would abort the run rather than corrupt results.
 *
 * Dynamic program (exact, standard):
 *   Root the tree at vertex 1.  For each vertex v keep two polynomials:
 *     excluded[v](x) = generating polynomial of independent sets in the
 *                      subtree of v that do NOT use v,
 *     included[v](x) = those that DO use v.
 *   Leaf initialisation: excluded = 1, included = x.
 *   Merging a child c into its parent p:
 *     excluded[p] *= (excluded[c] + included[c])
 *     included[p] *= excluded[c]
 *   Processing j = n, n-1, ..., 2 merges every vertex into its parent after
 *   all of its own children have been merged (valid because par[j] < j).
 *   The independence polynomial is excluded[1] + included[1].
 *
 * Overflow: every coefficient counts independent sets of a fixed size in a
 * (sub)tree on at most MAXVERT vertices, so it is bounded by
 * binomial(MAXVERT, MAXVERT/2); for MAXVERT = 31 that is C(31,15) < 2^30.
 * Intermediate convolution accumulators are partial sums of such counts and
 * obey the same bound.  Products used in the log-concavity test are < 2^60.
 * Everything therefore fits comfortably in uint64_t; a runtime guard aborts
 * if any final coefficient ever exceeds 2^40 (it cannot for n <= 31).
 *
 * Output:
 *   stdout: one line per exceptional tree --
 *     "NONUNIMODAL n=... par=... seq=..."   (a counterexample to #993!)
 *     "NONLOGCONCAVE n=... par=... seq=..." (first SAVE_LIMIT per run)
 *   stderr on exit (SUMMARY):
 *     "CHECK trees=... nonunimodal=... nonlogconcave=... hash=..."
 *   The hash is an order-independent sum over trees of an FNV-1a hash of the
 *   coefficient sequence, so per-chunk hashes can be added to give a
 *   partition-independent whole-run hash.
 */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

void check_summary(unsigned long long nout, double cpu); /* fwd decl for gentreeg's SUMMARY macro */

#define MAXVERT 40          /* max vertices supported by this plugin      */
#define MAXCOEF 44          /* poly degree can reach n-1; room to spare   */
#define SAVE_LIMIT 200      /* max NONLOGCONCAVE example lines per run    */
#define COEF_GUARD (1ULL << 40)

static uint64_t excluded[MAXVERT + 1][MAXCOEF];
static uint64_t included[MAXVERT + 1][MAXCOEF];
static int deg_excluded[MAXVERT + 1];
static int deg_included[MAXVERT + 1];

static unsigned long long trees_checked = 0;
static unsigned long long nonunimodal_count = 0;
static unsigned long long nonlogconcave_count = 0;
static unsigned long long saved_examples = 0;
static uint64_t sequence_hash_sum = 0;

void check_init(void)
{
    trees_checked = 0;
    nonunimodal_count = 0;
    nonlogconcave_count = 0;
    saved_examples = 0;
    sequence_hash_sum = 0;
}

static void print_exception(FILE *f, const char *label, const int *par, int n,
                            const uint64_t *coef, int degree)
{
    int i;
    fprintf(f, "%s n=%d par=", label, n);
    for (i = 1; i <= n; ++i) fprintf(f, "%s%d", i == 1 ? "" : ",", par[i]);
    fprintf(f, " seq=");
    for (i = 0; i <= degree; ++i)
        fprintf(f, "%s%llu", i == 0 ? "" : ",", (unsigned long long)coef[i]);
    fprintf(f, "\n");
    fflush(f);
}

void check_tree(FILE *f, int *par, int n)
{
    uint64_t child_sum[MAXCOEF];       /* excluded[c] + included[c] */
    uint64_t new_excluded[MAXCOEF];
    uint64_t new_included[MAXCOEF];
    uint64_t poly[MAXCOEF];
    int v, j, k, i;

    if (n < 1 || n > MAXVERT) {
        fprintf(stderr, "FATAL: n=%d outside supported range\n", n);
        exit(2);
    }

    /* initialise every vertex as a bare leaf */
    for (v = 1; v <= n; ++v) {
        excluded[v][0] = 1; deg_excluded[v] = 0;
        included[v][0] = 0; included[v][1] = 1; deg_included[v] = 1;
    }

    /* merge each vertex into its parent, deepest labels first */
    for (j = n; j >= 2; --j) {
        const int p = par[j];
        if (p < 1 || p >= j) {   /* contract violated -> abort loudly */
            fprintf(stderr, "FATAL: parent array not topological: par[%d]=%d\n", j, p);
            exit(2);
        }
        const int de_c = deg_excluded[j], di_c = deg_included[j];
        const int ds_c = (de_c > di_c) ? de_c : di_c;
        const int de_p = deg_excluded[p], di_p = deg_included[p];

        for (k = 0; k <= ds_c; ++k)
            child_sum[k] = (k <= de_c ? excluded[j][k] : 0)
                         + (k <= di_c ? included[j][k] : 0);

        /* new_excluded = excluded[p] * child_sum */
        for (k = 0; k <= de_p + ds_c; ++k) new_excluded[k] = 0;
        for (k = 0; k <= de_p; ++k) {
            const uint64_t a = excluded[p][k];
            if (a == 0) continue;
            for (i = 0; i <= ds_c; ++i)
                new_excluded[k + i] += a * child_sum[i];
        }

        /* new_included = included[p] * excluded[child] */
        for (k = 0; k <= di_p + de_c; ++k) new_included[k] = 0;
        for (k = 0; k <= di_p; ++k) {
            const uint64_t a = included[p][k];
            if (a == 0) continue;
            for (i = 0; i <= de_c; ++i)
                new_included[k + i] += a * excluded[j][i];
        }

        deg_excluded[p] = de_p + ds_c;
        deg_included[p] = di_p + de_c;
        memcpy(excluded[p], new_excluded, (size_t)(deg_excluded[p] + 1) * sizeof(uint64_t));
        memcpy(included[p], new_included, (size_t)(deg_included[p] + 1) * sizeof(uint64_t));
    }

    /* full independence polynomial of the tree */
    {
        const int de = deg_excluded[1], di = deg_included[1];
        const int degree = (de > di) ? de : di;

        for (k = 0; k <= degree; ++k)
            poly[k] = (k <= de ? excluded[1][k] : 0)
                    + (k <= di ? included[1][k] : 0);

        /* trim trailing zeros (cannot occur for a valid DP, but be safe) */
        int top = degree;
        while (top > 0 && poly[top] == 0) --top;

        /* overflow guard: for n <= 31 every coefficient is < 2^30 */
        for (k = 0; k <= top; ++k) {
            if (poly[k] >= COEF_GUARD) {
                fprintf(stderr, "FATAL: coefficient guard tripped (n=%d)\n", n);
                exit(2);
            }
        }

        /* unimodality: no strict descent may be followed by a strict ascent */
        int descending = 0, unimodal = 1;
        for (k = 0; k < top; ++k) {
            if (poly[k + 1] < poly[k]) descending = 1;
            else if (poly[k + 1] > poly[k] && descending) { unimodal = 0; break; }
        }
        if (!unimodal) {
            ++nonunimodal_count;
            print_exception(f, "NONUNIMODAL", par, n, poly, top);
        }

        /* log-concavity: poly[k]^2 >= poly[k-1]*poly[k+1] for interior k */
        int logconcave = 1;
        for (k = 1; k < top; ++k) {
            if (poly[k] * poly[k] < poly[k - 1] * poly[k + 1]) { logconcave = 0; break; }
        }
        if (!logconcave) {
            ++nonlogconcave_count;
            if (saved_examples < SAVE_LIMIT) {
                ++saved_examples;
                print_exception(f, "NONLOGCONCAVE", par, n, poly, top);
            }
        }

#ifdef PRINT_ALL_SEQUENCES
        print_exception(f, "SEQ", par, n, poly, top);
#endif

        /* order-independent run hash: sum of per-tree FNV-1a hashes */
        {
            uint64_t h = 1469598103934665603ULL;
            for (k = 0; k <= top; ++k) {
                h ^= poly[k];
                h *= 1099511628211ULL;
            }
            sequence_hash_sum += h;
        }
    }

    ++trees_checked;
}

void check_summary(unsigned long long nout, double cpu)
{
    fprintf(stderr,
        "CHECK trees=%llu nonunimodal=%llu nonlogconcave=%llu hash=%016llx gentreeg_nout=%llu cpu=%.2f\n",
        trees_checked, nonunimodal_count, nonlogconcave_count,
        (unsigned long long)sequence_hash_sum, nout, cpu);
}
