/* forest_check_plugin.c  (round 2: the FOREST case of Erdos #993)
 *
 * OUTPROC plugin for nauty's gentreeg.  Streams every unlabeled tree T of
 * order k and, for each polynomial q in a preloaded "q-set", forms the
 * product  p_T(x) * q(x)  exactly in uint64 arithmetic and tests it for
 * unimodality (and, as a by-product, log-concavity).
 *
 * The q-set for order k is the set of DISTINCT independence polynomials of
 * forests on m = 1 .. 30-k vertices all of whose components have at most k
 * vertices (built exactly by build_qsets.py, with generating-function
 * cross-checks).  Every disconnected forest F on <= 30 vertices factors as
 * F = T + Q where T is a maximum component (order k) and Q = F - T has
 * <= 30-k vertices and components of order <= k; its independence polynomial
 * is p_T * poly(Q).  So sweeping k = 1..29 with these q-sets checks the
 * independence sequence of EVERY forest on <= 30 vertices that is not a
 * single tree (single trees were exhausted by round 1 through order 30).
 *
 * Tree DP: identical to round 1 (independence_check_plugin.c), which was
 * brute-force cross-checked on all 436 trees of order <= 11 and reproduces
 * the published order-26 record.
 *
 * Overflow: any coefficient of p_T * q counts independent sets of one size
 * in a forest on <= 30 vertices, so it is < C(30,15) < 2^28.  The convolution
 * accumulates nonnegative partial sums bounded by the final coefficient.
 * Individual products p_i * q_j < 2^28 * 2^28 = 2^56.  Everything fits in
 * uint64_t with a wide margin; a runtime guard aborts if any product
 * coefficient reaches 2^41.
 *
 * Output:
 *   stdout: "NONUNIMODAL k=... par=... q=... seq=..."  (counterexample!)
 *           "NONLOGCONCAVE ..." (first SAVE_LIMIT per run; by-product)
 *   stderr: "FCHECK k=... trees=... qpolys=... checks=... nonunimodal=...
 *            nonlogconcave=... hash=... gentreeg_nout=... cpu=..."
 *   hash = order-independent sum over (tree, q) pairs of FNV-1a of the
 *   product sequence.
 *
 * Env:  QSET_FILE  path to the q-set file:
 *         line 1:  "NQ <count> K <k> BUDGET <b>"
 *         then per line: "<len> <c0> <c1> ... <c_{len-1}>"
 */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

void forest_summary(unsigned long long nout, double cpu);

#define MAXVERT 40
#define MAXCOEF 44
#define SAVE_LIMIT 200
#define COEF_GUARD (1ULL << 41)

static uint64_t excluded[MAXVERT + 1][MAXCOEF];
static uint64_t included[MAXVERT + 1][MAXCOEF];
static int deg_excluded[MAXVERT + 1];
static int deg_included[MAXVERT + 1];

/* ---- q-set ---- */
static uint64_t (*qcoef)[MAXCOEF] = NULL;
static int *qdeg = NULL;
static int nq = 0;
static int qset_k = -1, qset_budget = -1;

static unsigned long long trees_checked = 0;
static unsigned long long product_checks = 0;
static unsigned long long nonunimodal_count = 0;
static unsigned long long nonlogconcave_count = 0;
static unsigned long long saved_examples = 0;
static uint64_t sequence_hash_sum = 0;
static int current_order = -1;

void forest_init(void)
{
    const char *path = getenv("QSET_FILE");
    FILE *fh;
    int i, k, len;

    if (!path) { fprintf(stderr, "FATAL: QSET_FILE not set\n"); exit(2); }
    fh = fopen(path, "r");
    if (!fh) { fprintf(stderr, "FATAL: cannot open %s\n", path); exit(2); }
    if (fscanf(fh, "NQ %d K %d BUDGET %d", &nq, &qset_k, &qset_budget) != 3) {
        fprintf(stderr, "FATAL: bad q-set header\n"); exit(2);
    }
    if (nq < 1) { fprintf(stderr, "FATAL: empty q-set\n"); exit(2); }
    qcoef = malloc((size_t)nq * sizeof(*qcoef));
    qdeg = malloc((size_t)nq * sizeof(*qdeg));
    if (!qcoef || !qdeg) { fprintf(stderr, "FATAL: q-set alloc\n"); exit(2); }
    for (i = 0; i < nq; ++i) {
        if (fscanf(fh, "%d", &len) != 1 || len < 1 || len > MAXCOEF) {
            fprintf(stderr, "FATAL: bad q-set entry %d\n", i); exit(2);
        }
        qdeg[i] = len - 1;
        for (k = 0; k < len; ++k) {
            unsigned long long c;
            if (fscanf(fh, "%llu", &c) != 1) {
                fprintf(stderr, "FATAL: bad q-set coeff %d/%d\n", i, k); exit(2);
            }
            qcoef[i][k] = c;
        }
        if (qcoef[i][qdeg[i]] == 0 || qcoef[i][0] != 1) {
            fprintf(stderr, "FATAL: q-set poly %d not normalised\n", i); exit(2);
        }
    }
    fclose(fh);
}

static void print_exception(FILE *f, const char *label, const int *par, int n,
                            int qidx, const uint64_t *coef, int degree)
{
    int i;
    fprintf(f, "%s k=%d par=", label, n);
    for (i = 1; i <= n; ++i) fprintf(f, "%s%d", i == 1 ? "" : ",", par[i]);
    fprintf(f, " q=");
    for (i = 0; i <= qdeg[qidx]; ++i)
        fprintf(f, "%s%llu", i == 0 ? "" : ",", (unsigned long long)qcoef[qidx][i]);
    fprintf(f, " seq=");
    for (i = 0; i <= degree; ++i)
        fprintf(f, "%s%llu", i == 0 ? "" : ",", (unsigned long long)coef[i]);
    fprintf(f, "\n");
    fflush(f);
}

void forest_check_tree(FILE *f, int *par, int n)
{
    uint64_t child_sum[MAXCOEF];
    uint64_t new_excluded[MAXCOEF];
    uint64_t new_included[MAXCOEF];
    uint64_t poly[MAXCOEF];
    uint64_t prod[2 * MAXCOEF];
    int v, j, k, i, qi;

    if (n < 1 || n > MAXVERT) {
        fprintf(stderr, "FATAL: n=%d outside supported range\n", n); exit(2);
    }
    if (current_order < 0) {
        current_order = n;
        if (n != qset_k) {
            fprintf(stderr, "FATAL: q-set built for k=%d but stream has k=%d\n",
                    qset_k, n); exit(2);
        }
    }

    for (v = 1; v <= n; ++v) {
        excluded[v][0] = 1; deg_excluded[v] = 0;
        included[v][0] = 0; included[v][1] = 1; deg_included[v] = 1;
    }
    for (j = n; j >= 2; --j) {
        const int p = par[j];
        if (p < 1 || p >= j) {
            fprintf(stderr, "FATAL: parent array not topological: par[%d]=%d\n", j, p);
            exit(2);
        }
        const int de_c = deg_excluded[j], di_c = deg_included[j];
        const int ds_c = (de_c > di_c) ? de_c : di_c;
        const int de_p = deg_excluded[p], di_p = deg_included[p];
        for (k = 0; k <= ds_c; ++k)
            child_sum[k] = (k <= de_c ? excluded[j][k] : 0)
                         + (k <= di_c ? included[j][k] : 0);
        for (k = 0; k <= de_p + ds_c; ++k) new_excluded[k] = 0;
        for (k = 0; k <= de_p; ++k) {
            const uint64_t a = excluded[p][k];
            if (a == 0) continue;
            for (i = 0; i <= ds_c; ++i) new_excluded[k + i] += a * child_sum[i];
        }
        for (k = 0; k <= di_p + de_c; ++k) new_included[k] = 0;
        for (k = 0; k <= di_p; ++k) {
            const uint64_t a = included[p][k];
            if (a == 0) continue;
            for (i = 0; i <= de_c; ++i) new_included[k + i] += a * excluded[j][i];
        }
        deg_excluded[p] = de_p + ds_c;
        deg_included[p] = di_p + de_c;
        memcpy(excluded[p], new_excluded, (size_t)(deg_excluded[p] + 1) * sizeof(uint64_t));
        memcpy(included[p], new_included, (size_t)(deg_included[p] + 1) * sizeof(uint64_t));
    }

    const int de = deg_excluded[1], di = deg_included[1];
    int pdeg = (de > di) ? de : di;
    for (k = 0; k <= pdeg; ++k)
        poly[k] = (k <= de ? excluded[1][k] : 0) + (k <= di ? included[1][k] : 0);
    while (pdeg > 0 && poly[pdeg] == 0) --pdeg;

    /* every product p_T * q, q over the q-set */
    for (qi = 0; qi < nq; ++qi) {
        const int qd = qdeg[qi];
        const int top = pdeg + qd;
        for (k = 0; k <= top; ++k) prod[k] = 0;
        for (k = 0; k <= pdeg; ++k) {
            const uint64_t a = poly[k];
            if (a == 0) continue;
            const uint64_t *qq = qcoef[qi];
            for (i = 0; i <= qd; ++i) prod[k + i] += a * qq[i];
        }
        for (k = 0; k <= top; ++k) {
            if (prod[k] >= COEF_GUARD) {
                fprintf(stderr, "FATAL: coefficient guard tripped (k=%d)\n", n);
                exit(2);
            }
        }
        int descending = 0, unimodal = 1;
        for (k = 0; k < top; ++k) {
            if (prod[k + 1] < prod[k]) descending = 1;
            else if (prod[k + 1] > prod[k] && descending) { unimodal = 0; break; }
        }
        if (!unimodal) {
            ++nonunimodal_count;
            print_exception(f, "NONUNIMODAL", par, n, qi, prod, top);
        }
        int logconcave = 1;
        for (k = 1; k < top; ++k) {
            if (prod[k] * prod[k] < prod[k - 1] * prod[k + 1]) { logconcave = 0; break; }
        }
        if (!logconcave) {
            ++nonlogconcave_count;
            if (saved_examples < SAVE_LIMIT) {
                ++saved_examples;
                print_exception(f, "NONLOGCONCAVE", par, n, qi, prod, top);
            }
        }
        uint64_t h = 1469598103934665603ULL;
        for (k = 0; k <= top; ++k) { h ^= prod[k]; h *= 1099511628211ULL; }
        sequence_hash_sum += h;
        ++product_checks;
    }
    ++trees_checked;
}

void forest_summary(unsigned long long nout, double cpu)
{
    fprintf(stderr,
        "FCHECK k=%d trees=%llu qpolys=%d checks=%llu nonunimodal=%llu "
        "nonlogconcave=%llu hash=%016llx gentreeg_nout=%llu cpu=%.2f\n",
        current_order, trees_checked, nq, product_checks, nonunimodal_count,
        nonlogconcave_count, (unsigned long long)sequence_hash_sum, nout, cpu);
}
