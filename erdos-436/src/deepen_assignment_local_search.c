/*
 * deepen_assignment_local_search.c
 *
 * Heuristic search for a completely multiplicative f : {1..B} -> Z/k whose
 * FIRST run of m consecutive zeros is as late as possible (or absent).
 *
 * Purpose (Erdos #436): each such f, restricted to the primes <= B, is a
 * certificate that Lambda(k,m) >= (position of its first zero run), via the
 * theorem of Mills (Canad. J. Math. 15 (1963)): for odd k, any assignment
 * of k-th power character values at finitely many primes is realized by
 * infinitely many primes p.  The certificate is verified independently by
 * verify_certificate.py; this program also re-derives f from the prime
 * assignment before writing the certificate, so bookkeeping bugs cannot
 * produce an invalid certificate.
 *
 * Method: steepest-ascent local search with random kicks.
 *   state    : values f(q) in Z/k at primes q <= B (composites forced).
 *   objective: position r of the first window of m consecutive zeros.
 *   move     : pick the current first window; for each element x of the
 *              window take its largest prime factor q (falling back to all
 *              prime factors of the window if every largest factor is
 *              tiny), and for each nonzero delta consider f(q) += delta.
 *              Score each candidate by the resulting first-window position,
 *              computable in O(B/q) because only multiples of q change.
 *              Take the best candidate (ties random); if no candidate
 *              improves, take the least-bad one (the walk must move).
 *   stall    : after `kick_after` moves without a new best, apply a random
 *              multi-prime kick; the global best assignment is kept aside.
 *
 * Output: BEST lines as the record improves, then a certificate file in
 * the same format as search_character_assignments.
 *
 * Usage: deepen_assignment_local_search k m B seconds seed cert_path
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

typedef uint32_t u32;
typedef uint64_t u64;

static u64 rng_state;
static u64 rng_next(void) {
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 7;
    rng_state ^= rng_state << 17;
    return rng_state;
}

static u32 K, M;
static u64 B;
static u32 *largest_factor;   /* largest prime factor of n */
static uint8_t *fval;         /* f(n) for n = 1..B (current state) */
static uint8_t *prime_val;    /* f(q) for primes (indexed by q), current */
static uint8_t *best_prime_val;
static char *is_prime;

static double now_seconds(void) {
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

/* recompute fval[1..B] from prime_val: exact, used at init and snapshots */
static void recompute_all(void) {
    fval[1] = 0;
    for (u64 n = 2; n <= B; n++) {
        u32 q = largest_factor[n];
        fval[n] = (n == q) ? prime_val[n]
                           : (uint8_t)((fval[n / q] + prime_val[q]) % K);
    }
}

/* first n with fval[n..n+M-1] all zero (window start), or 0 if none in [1, B-M+1] */
static u64 first_zero_window(void) {
    u32 run = 0;
    for (u64 n = 1; n <= B; n++) {
        if (fval[n] == 0) { run++; if (run >= M) return n - M + 1; }
        else run = 0;
    }
    return 0;
}

/* Apply f(q) += delta to fval incrementally: multiples of q^e gain e*delta. */
static void apply_flip(u32 q, u32 delta) {
    prime_val[q] = (uint8_t)((prime_val[q] + delta) % K);
    for (u64 pe = q; pe <= B; pe *= q) {
        for (u64 n = pe; n <= B; n += pe)
            fval[n] = (uint8_t)((fval[n] + delta) % K);
        if (pe > B / q) break;  /* avoid overflow */
    }
}

/* Score a candidate flip (q, delta) given the current first window is at
 * old_r (window [old_r, old_r+M-1]).  Only multiples of q change value, so
 * after the flip the first window is the minimum of:
 *   - any all-zero window that includes a multiple of q, and
 *   - the old window at old_r if it still is all zero.
 * Simulate cheaply: value of n after flip = fval[n] + delta * v_q(n).      */
static inline uint8_t val_after(u64 n, u32 q, u32 delta) {
    u32 add = 0; u64 t = n;
    while (t % q == 0) { add += delta; t /= q; }
    return (uint8_t)((fval[n] + add) % K);
}

static u64 score_flip(u32 q, u32 delta, u64 old_r) {
    u64 best = 0;
    /* windows touching a multiple of q */
    for (u64 u = q; u <= B; u += q) {
        u64 lo = (u >= M) ? u - M + 1 : 1;
        for (u64 s = lo; s <= u && s + M - 1 <= B; s++) {
            int allz = 1;
            for (u32 j = 0; j < M; j++)
                if (val_after(s + j, q, delta) != 0) { allz = 0; break; }
            if (allz) { if (!best || s < best) best = s; goto have_from_multiples; }
        }
        if (best && u > best + M) break;
    }
have_from_multiples:
    /* the old window survives unless one of its elements changed to nonzero */
    if (old_r) {
        int allz = 1;
        for (u32 j = 0; j < M; j++)
            if (val_after(old_r + j, q, delta) != 0) { allz = 0; break; }
        if (allz && (!best || old_r < best)) best = old_r;
    }
    return best;  /* 0 = no zero window at all (ideal) */
}

int main(int argc, char **argv) {
    if (argc != 7) {
        fprintf(stderr, "usage: %s k m B seconds seed cert_path\n", argv[0]);
        return 2;
    }
    K = (u32)atoi(argv[1]);
    M = (u32)atoi(argv[2]);
    B = strtoull(argv[3], 0, 10);
    double seconds = atof(argv[4]);
    rng_state = strtoull(argv[5], 0, 10);
    if (!rng_state) rng_state = 88172645463325252ULL;
    const char *cert_path = argv[6];

    largest_factor = malloc((B + 1) * sizeof(u32));
    fval = malloc(B + 1);
    is_prime = calloc(B + 1, 1);
    prime_val = calloc(B + 1, 1);
    best_prime_val = calloc(B + 1, 1);
    if (!largest_factor || !fval || !is_prime || !prime_val || !best_prime_val) {
        fprintf(stderr, "out of memory\n"); return 3;
    }
    for (u64 n = 0; n <= B; n++) largest_factor[n] = 0;
    for (u64 q = 2; q <= B; q++) {
        if (largest_factor[q] == 0) {
            is_prime[q] = 1;
            for (u64 n = q; n <= B; n += q) largest_factor[n] = (u32)q;
        }
    }

    /* initial assignment: f(q) = 1 at every prime */
    for (u64 q = 2; q <= B; q++) if (is_prime[q]) prime_val[q] = 1;
    recompute_all();

    u64 best_r = 0;               /* best (largest) first-window position seen */
    int best_is_survivor = 0;
    u64 iters = 0, kicks = 0, since_best = 0;
    const u64 kick_after = 3000;
    double t0 = now_seconds();

    while (now_seconds() - t0 < seconds) {
        iters++;
        u64 r = first_zero_window();
        if (r == 0) {
            /* survivor within the window: certificate proves first window > B-M+1 */
            memcpy(best_prime_val, prime_val, B + 1);
            best_r = B; best_is_survivor = 1;
            printf("SURVIVOR %u %u %llu iters=%llu\n", K, M, (unsigned long long)B,
                   (unsigned long long)iters);
            fflush(stdout);
            break;
        }
        if (r > best_r) {
            best_r = r; best_is_survivor = 0; since_best = 0;
            memcpy(best_prime_val, prime_val, B + 1);
            printf("BEST %u %u %llu iters=%llu\n", K, M, (unsigned long long)r,
                   (unsigned long long)iters);
            fflush(stdout);
        } else if (++since_best >= kick_after) {
            /* stall: restart from the best state and kick it */
            memcpy(prime_val, best_prime_val, B + 1);
            u64 kick_span = B / 8 > 100 ? B / 8 : B;  /* small primes have global effect */
            for (int i = 0; i < 12; i++) {
                u64 q;
                do { q = 2 + rng_next() % kick_span; } while (!is_prime[q]);
                prime_val[q] = (uint8_t)(rng_next() % K);
            }
            recompute_all();
            since_best = 0; kicks++;
            continue;
        }

        /* candidate flips from the current first window */
        u32 cq[64]; u32 cd[64]; int nc = 0;
        for (u32 j = 0; j < M; j++) {
            u64 x = r + j;
            if (x < 2) continue;
            u32 q = largest_factor[x];
            for (u32 d = 1; d < K && nc < 64; d++) { cq[nc] = q; cd[nc] = d; nc++; }
        }
        /* if all largest factors are small, add every prime factor of the window */
        int all_small = 1;
        for (u32 j = 0; j < M; j++) if (r + j >= 2 && largest_factor[r + j] > 50) all_small = 0;
        if (all_small) {
            for (u32 j = 0; j < M; j++) {
                u64 x = r + j;
                while (x >= 2 && nc < 60) {
                    u32 q = largest_factor[x];
                    while (x % q == 0) x /= q;
                    for (u32 d = 1; d < K && nc < 60; d++) { cq[nc] = q; cd[nc] = d; nc++; }
                }
            }
        }
        if (nc == 0) break;

        u64 best_score = 0; int best_i = -1; u32 nties = 0;
        for (int i = 0; i < nc; i++) {
            u64 s = score_flip(cq[i], cd[i], r);
            u64 sc = (s == 0) ? B + 1 : s;   /* no window at all is best */
            if (best_i < 0 || sc > best_score) { best_score = sc; best_i = i; nties = 1; }
            else if (sc == best_score && rng_next() % (++nties) == 0) best_i = i;
        }
        apply_flip(cq[best_i], cd[best_i]);
    }

    /* snapshot: rebuild from best_prime_val exactly and confirm before writing */
    memcpy(prime_val, best_prime_val, B + 1);
    recompute_all();
    u64 check_r = first_zero_window();
    FILE *cf = fopen(cert_path, "w");
    if (!cf) { fprintf(stderr, "cannot write %s\n", cert_path); return 3; }
    if (best_is_survivor || check_r == 0) {
        fprintf(cf, "# k=%u m=%u no_zero_run_of_length_m_up_to=%llu\n", K, M,
                (unsigned long long)B);
        printf("FINAL %u %u survivor B=%llu iters=%llu kicks=%llu\n", K, M,
               (unsigned long long)B, (unsigned long long)iters, (unsigned long long)kicks);
    } else {
        fprintf(cf, "# k=%u m=%u first_zero_run_at=%llu\n", K, M,
                (unsigned long long)check_r);
        printf("FINAL %u %u best=%llu iters=%llu kicks=%llu\n", K, M,
               (unsigned long long)check_r, (unsigned long long)iters,
               (unsigned long long)kicks);
    }
    for (u64 q = 2; q <= B; q++)
        if (is_prime[q]) fprintf(cf, "%llu %u\n", (unsigned long long)q, prime_val[q]);
    fclose(cf);
    printf("CERT-FILE %s\n", cert_path);
    return 0;
}
