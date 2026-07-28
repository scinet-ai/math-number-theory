/* Stage C: certify that none of the given exact integers X_1..X_k has a prime
 * factor in [lo, hi]. Streams primes with libprimesieve, tests mpz_tdiv_ui.
 *
 * Usage: certify lo hi xfile1 [xfile2 ...]
 * Prints: any divisor hit (=> FAIL), plus "#primes tested", first and last
 * prime (integrity check against pi(x) tables), and checkpoint lines every
 * ~30s so a killed run certifies a prefix range.
 * Exit 0 = no prime in [lo,hi] divides any X. Exit 1 = a divisor was found.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <gmp.h>
#include <primesieve.h>

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: %s lo hi xfile...\n", argv[0]); return 2; }
    uint64_t lo = strtoull(argv[1], 0, 10), hi = strtoull(argv[2], 0, 10);
    int k = argc - 3;
    mpz_t *X = malloc(k * sizeof(mpz_t));
    for (int i = 0; i < k; i++) {
        FILE *f = fopen(argv[3 + i], "r");
        if (!f) { perror(argv[3 + i]); return 2; }
        mpz_init(X[i]);
        if (mpz_inp_str(X[i], f, 10) == 0) { fprintf(stderr, "bad int %s\n", argv[3+i]); return 2; }
        fclose(f);
    }
    primesieve_iterator it;
    primesieve_init(&it);
    primesieve_jump_to(&it, lo, hi);
    uint64_t p, count = 0, first = 0, last = 0;
    int fail = 0;
    time_t t0 = time(0), tlast = t0;
    while ((p = primesieve_next_prime(&it)) <= hi) {
        if (!first) first = p;
        last = p; count++;
        for (int i = 0; i < k; i++)
            if (mpz_divisible_ui_p(X[i], p)) {
                printf("DIVISOR: prime %llu divides %s\n", (unsigned long long)p, argv[3+i]);
                fail = 1;
            }
        if ((count & 0xFFFFF) == 0) {
            time_t t = time(0);
            if (t - tlast >= 30) {
                printf("CHECKPOINT: tested %llu primes, at p=%llu (%llus)\n",
                       (unsigned long long)count, (unsigned long long)p,
                       (unsigned long long)(t - t0));
                fflush(stdout);
                tlast = t;
            }
        }
    }
    primesieve_free_iterator(&it);
    printf("RANGE [%llu,%llu]: tested %llu primes (first %llu, last %llu), %s\n",
           (unsigned long long)lo, (unsigned long long)hi, (unsigned long long)count,
           (unsigned long long)first, (unsigned long long)last,
           fail ? "DIVISOR FOUND" : "no divisor of any input");
    return fail;
}
