/*
 * search_character_assignments.c
 *
 * Exhaustive backtracking search over completely multiplicative functions
 *     f : {1,2,3,...} -> Z/k   (additive notation; f(1)=0, f(ab)=f(a)+f(b))
 * for the largest possible position of the first run of m consecutive
 * integers r, r+1, ..., r+m-1 with f == 0 on all of them.
 *
 * Why this computes Lambda(k,m) = limsup_p r(k,m,p)  (Erdos #436):
 *   For a prime p == 1 (mod k), the k-th power residue character gives such
 *   an f (f(n) = index of n mod k), and n is a k-th power residue iff
 *   f(n) = 0.  Hence if EVERY f has a zero-run of length m starting at or
 *   before B, then r(k,m,p) <= B for every prime p > B+m-1 with p == 1
 *   (mod k)  (unconditional upper bound; primes p !== 1 mod k with
 *   gcd(k,p-1)=1 have r=1).  Conversely, by the theorem of Mills
 *   ("Characters with preassigned values", Canad. J. Math. 15 (1963)),
 *   for odd k any assignment of character values at finitely many primes is
 *   realized by infinitely many primes p, so a single f whose first
 *   zero-run of length m starts at r proves Lambda(k,m) >= r.
 *   Therefore: if the search tree is finite, the maximum death position
 *   equals Lambda(k,m) exactly (for odd k; for k=2 the same holds because
 *   every quadratic sign pattern on finitely many primes is realizable by
 *   Dirichlet's theorem).  This is precisely the method used by
 *   Lehmer-Lehmer-Mills-Selfridge (1962) to prove Lambda(3,3) = 23532.
 *
 * Search organization:
 *   Integers are processed in increasing order.  At a prime q the value
 *   f(q) in {0,...,k-1} is a free choice (branch); at a composite the value
 *   is forced.  A branch dies when the first zero-run of length m appears;
 *   the death position r is recorded.  Global symmetry: multiplying every
 *   f(q) by a unit of Z/k maps valid assignments to valid assignments and
 *   preserves zero sets, so the first prime given a nonzero value may be
 *   restricted to value 1.  Nonzero choices are tried before 0 so that deep
 *   branches are found early.
 *   A branch that survives past n_cap is reported as SURVIVOR (the search
 *   then stops: no exact value is obtainable with this cap).
 *
 * Optional root restriction, for splitting the tree across processes:
 *   --fix c1,c2,...,cf pins the choices at the first f primes 2,3,5,...
 *   (values in Z/k).  The union of the standard root set covers the whole
 *   tree modulo symmetry.
 *
 * Output:
 *   BEST k m r            -- new maximum death position (first zero-run at r)
 *   CERT-FILE path        -- certificate of the best branch written there
 *                            (lines "q value", primes q <= r+m-1)
 *   SURVIVOR k m n_cap    -- some f has no zero-run of length m up to n_cap
 *   NODES total           -- integers stepped (search size)
 *   EXHAUSTED yes|no      -- whether the whole (sub)tree was searched
 *   FINAL k m best nodes exhausted
 *
 * Usage: search_character_assignments k m n_cap node_budget [--fix list] [--cert path]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef uint32_t u32;
typedef uint64_t u64;

static u32 *smallest_factor;   /* smallest prime factor, index up to n_cap */
static uint8_t *value;         /* f(n) along the current branch */

typedef struct {
    u32 q;              /* the prime at this decision point */
    uint8_t choice_idx; /* index into its choice order */
    uint8_t n_choices;
    uint8_t first_nonzero_slot; /* 1 if no nonzero value existed before this prime */
    uint8_t fixed;      /* 1 if pinned by --fix */
} Frame;

int main(int argc, char **argv) {
    if (argc < 5) {
        fprintf(stderr, "usage: %s k m n_cap node_budget [--fix c1,c2,...] [--cert path]\n", argv[0]);
        return 2;
    }
    u64 k = strtoull(argv[1], 0, 10);
    int m = (int)strtoull(argv[2], 0, 10);
    u64 n_cap = strtoull(argv[3], 0, 10);
    u64 node_budget = strtoull(argv[4], 0, 10);
    const char *cert_path = "certificate.txt";
    int n_fixed = 0; int fixed_choice[64];
    for (int i = 5; i < argc; i++) {
        if (!strcmp(argv[i], "--fix") && i + 1 < argc) {
            char *s = argv[++i];
            while (*s && n_fixed < 64) {
                fixed_choice[n_fixed++] = atoi(s);
                while (*s && *s != ',') s++;
                if (*s == ',') s++;
            }
        } else if (!strcmp(argv[i], "--cert") && i + 1 < argc) {
            cert_path = argv[++i];
        }
    }
    if (k < 2 || k > 200 || m < 2 || m > 8 || n_cap < 100) { fprintf(stderr, "bad args\n"); return 2; }

    /* smallest-prime-factor sieve up to n_cap */
    smallest_factor = malloc((n_cap + 1) * sizeof(u32));
    value = malloc(n_cap + 1);
    if (!smallest_factor || !value) { fprintf(stderr, "out of memory\n"); return 3; }
    for (u64 i = 0; i <= n_cap; i++) smallest_factor[i] = 0;
    for (u64 i = 2; i <= n_cap; i++) {
        if (smallest_factor[i] == 0) {
            for (u64 j = i; j <= n_cap; j += i)
                if (smallest_factor[j] == 0) smallest_factor[j] = (u32)i;
        }
    }

    u64 max_frames = 0;
    for (u64 i = 2; i <= n_cap; i++) if (smallest_factor[i] == (u32)i) max_frames++;
    Frame *stack = malloc((max_frames + 2) * sizeof(Frame));
    u32 *best_prime = malloc((max_frames + 2) * sizeof(u32));
    uint8_t *best_value = malloc((max_frames + 2) * sizeof(uint8_t));
    u64 best_nprimes = 0;

    /* choice order: nonzero values first (1..k-1), then 0 */
    int order_full[256], order_limited[2] = {1, 0};
    for (u64 c = 1; c < k; c++) order_full[c - 1] = (int)c;
    order_full[k - 1] = 0;

    u64 nodes = 0, best_r = 0, sp = 0, nonzero_on_path = 0;
    int exhausted = 1, survivor = 0;
    u64 n = 1;
    value[1] = 0;

    while (1) {
        /* advance to n+1 */
        n++;
        nodes++;
        if ((nodes & ((1ULL << 31) - 1)) == 0) {
            printf("PROGRESS nodes=%llu best=%llu depth=%llu\n",
                   (unsigned long long)nodes, (unsigned long long)best_r,
                   (unsigned long long)n);
            fflush(stdout);
        }
        if (n > n_cap) {
            /* survivor: no zero-run of length m up to n_cap */
            survivor = 1; exhausted = 0;
            best_r = n_cap;  /* certificate proves first run > n_cap - m + 1 */
            best_nprimes = sp;
            for (u64 i = 0; i < sp; i++) { best_prime[i] = stack[i].q; best_value[i] = value[stack[i].q]; }
            printf("SURVIVOR %llu %d %llu\n", (unsigned long long)k, m, (unsigned long long)n_cap);
            fflush(stdout);
            break;
        }
        if (nodes > node_budget) { exhausted = 0; break; }
        if (smallest_factor[n] == (u32)n) {  /* prime: push decision */
            Frame *f = &stack[sp++];
            f->q = (u32)n;
            f->choice_idx = 0;
            f->first_nonzero_slot = (nonzero_on_path == 0);
            f->fixed = 0;
            if ((u64)(sp - 1) < (u64)n_fixed) {
                f->fixed = 1; f->n_choices = 1;
                value[n] = (uint8_t)(fixed_choice[sp - 1] % (int)k);
            } else if (f->first_nonzero_slot) {
                f->n_choices = 2;               /* symmetry: {1, 0} */
                value[n] = (uint8_t)order_limited[0];
            } else {
                f->n_choices = (uint8_t)k;      /* {1,...,k-1, 0} */
                value[n] = (uint8_t)order_full[0];
            }
            if (value[n] != 0) nonzero_on_path++;
        } else {
            u32 q = smallest_factor[n];
            uint8_t v = value[q] + value[n / q];
            value[n] = (v >= (uint8_t)k) ? (uint8_t)(v - (uint8_t)k) : v;
        }
death_check:
        /* death check: zero-run of length m ending at n.  Every assignment
         * of a value to position n (fresh advance OR a re-choice made while
         * backtracking, which jumps here) must pass through this check. */
        if (n >= (u64)m) {
            int all_zero = 1;
            for (int j = 0; j < m; j++) if (value[n - (u64)j] != 0) { all_zero = 0; break; }
            if (all_zero) {
                u64 r = n - (u64)m + 1;
                if (r > best_r) {
                    best_r = r;
                    best_nprimes = sp;
                    for (u64 i = 0; i < sp; i++) { best_prime[i] = stack[i].q; best_value[i] = value[stack[i].q]; }
                    printf("BEST %llu %d %llu\n", (unsigned long long)k, m, (unsigned long long)r);
                    fflush(stdout);
                }
                /* backtrack */
                int done = 0;
                while (1) {
                    if (sp == 0) { done = 1; break; }
                    Frame *f = &stack[sp - 1];
                    if (value[f->q] != 0) nonzero_on_path--;
                    f->choice_idx++;
                    if (f->fixed || f->choice_idx >= f->n_choices) { sp--; continue; }
                    int c = f->first_nonzero_slot ? order_limited[f->choice_idx]
                                                  : order_full[f->choice_idx];
                    value[f->q] = (uint8_t)c;
                    if (c != 0) nonzero_on_path++;
                    n = f->q;
                    nodes++;
                    if (nodes > node_budget) { exhausted = 0; done = 1; break; }
                    goto death_check;   /* the re-choice itself may complete a zero-run */
                }
                if (done) break;
            }
        }
    }

    FILE *cf = fopen(cert_path, "w");
    if (cf) {
        fprintf(cf, "# k=%llu m=%d %s=%llu\n", (unsigned long long)k, m,
                survivor ? "no_zero_run_of_length_m_up_to" : "first_zero_run_at",
                (unsigned long long)best_r);
        for (u64 i = 0; i < best_nprimes; i++)
            fprintf(cf, "%u %u\n", best_prime[i], (unsigned)best_value[i]);
        fclose(cf);
        printf("CERT-FILE %s\n", cert_path);
    }
    printf("NODES %llu\n", (unsigned long long)nodes);
    printf("EXHAUSTED %s\n", exhausted ? "yes" : "no");
    printf("FINAL %llu %d %llu %llu %s%s\n", (unsigned long long)k, m,
           (unsigned long long)best_r, (unsigned long long)nodes,
           exhausted ? "exhausted" : "budget-or-cap",
           survivor ? " survivor" : "");
    return exhausted ? 0 : 1;
}
