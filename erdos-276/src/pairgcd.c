/* C4: pairwise coprimality of the survivor terms.
 * Usage: pairgcd k nsplit file1 file2 ...
 * Tests gcd(X_i, X_j) for all i<j with i % nsplit == k.
 * Prints any pair with gcd > 1 (=> FAIL) and a final count line.
 * Exit 0 = all tested pairs coprime. */
#include <stdio.h>
#include <stdlib.h>
#include <gmp.h>

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: %s k nsplit files...\n", argv[0]); return 2; }
    int k = atoi(argv[1]), nsplit = atoi(argv[2]), n = argc - 3;
    mpz_t *X = malloc(n * sizeof(mpz_t));
    for (int i = 0; i < n; i++) {
        FILE *f = fopen(argv[3 + i], "r");
        if (!f) { perror(argv[3 + i]); return 2; }
        mpz_init(X[i]);
        mpz_inp_str(X[i], f, 10);
        fclose(f);
    }
    mpz_t g;
    mpz_init(g);
    long tested = 0;
    int fail = 0;
    for (int i = k; i < n; i += nsplit)
        for (int j = i + 1; j < n; j++) {
            mpz_gcd(g, X[i], X[j]);
            tested++;
            if (mpz_cmp_ui(g, 1) != 0) {
                gmp_printf("NONTRIVIAL GCD %Zd between %s and %s\n", g, argv[3+i], argv[3+j]);
                fail = 1;
            }
        }
    printf("split %d/%d: tested %ld pairs, %s\n", k, nsplit, tested,
           fail ? "NONTRIVIAL GCD FOUND" : "all coprime");
    return fail;
}
