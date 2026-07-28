/* Probable-prime check (GMP mpz_probab_prime_p, 40 reps) for decimal files.
 * Prints "<file>: probable prime|composite|certified prime (small)".
 * NOTE: probabilistic classification only - used to REPORT consistency with
 * IsSo14's primality statements, never as a certified claim. */
#include <stdio.h>
#include <gmp.h>

int main(int argc, char **argv) {
    mpz_t x;
    mpz_init(x);
    for (int i = 1; i < argc; i++) {
        FILE *f = fopen(argv[i], "r");
        if (!f) { perror(argv[i]); return 2; }
        mpz_inp_str(x, f, 10);
        fclose(f);
        int r = mpz_probab_prime_p(x, 40);
        printf("%s: %s (%zu digits)\n", argv[i],
               r == 2 ? "certified prime" : r == 1 ? "probable prime" : "composite",
               mpz_sizeinbase(x, 10));
    }
    return 0;
}
