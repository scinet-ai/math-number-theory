/* Stage B sieve for the Ismailescu-Son Lucas sequence x_{n+2}=x_{n+1}+x_n.
 *
 * Input: binary uint64 triples (p, x0 mod p, x1 mod p).
 * For each prime p in [triple index lo, hi) iterate the recurrence mod p for
 * n = 0..N and set bit n of a bitmap whenever x_n == 0 (mod p).
 * Output: bitmap file of (N+1+7)/8 bytes; bit n set <=> some processed prime
 * divides x_n. Checkpoints the bitmap + a progress file every CHUNK primes.
 *
 * Usage: sieve input.bin output.bitmap N lo hi
 * Exact integer arithmetic only; deterministic.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

static void save(const char *path, const uint8_t *bm, size_t bytes,
                 const char *prog, long done, long hi) {
    char tmp[4096];
    snprintf(tmp, sizeof tmp, "%s.tmp", path);
    FILE *f = fopen(tmp, "wb");
    if (!f) { perror("fopen"); exit(2); }
    fwrite(bm, 1, bytes, f);
    fclose(f);
    rename(tmp, path);
    f = fopen(prog, "w");
    fprintf(f, "%ld / %ld primes done\n", done, hi);
    fclose(f);
}

int main(int argc, char **argv) {
    if (argc != 6) { fprintf(stderr, "usage: %s in.bin out.bitmap N lo hi\n", argv[0]); return 2; }
    const char *inpath = argv[1], *outpath = argv[2];
    long N = atol(argv[3]), lo = atol(argv[4]), hi = atol(argv[5]);

    FILE *f = fopen(inpath, "rb");
    if (!f) { perror("input"); return 2; }
    fseek(f, 0, SEEK_END);
    long ntrip = ftell(f) / 24;
    if (hi > ntrip) hi = ntrip;
    fseek(f, lo * 24, SEEK_SET);
    uint64_t *trip = malloc((size_t)(hi - lo) * 24);
    if (fread(trip, 24, (size_t)(hi - lo), f) != (size_t)(hi - lo)) { fprintf(stderr, "short read\n"); return 2; }
    fclose(f);

    size_t bytes = (size_t)(N + 1 + 7) / 8;
    uint8_t *bm = calloc(bytes, 1);
    char prog[4096];
    snprintf(prog, sizeof prog, "%s.progress", outpath);

    const long CHUNK = 4000;
    for (long i = 0; i < hi - lo; i++) {
        uint64_t p = trip[3 * i], a = trip[3 * i + 1], b = trip[3 * i + 2];
        if (a == 0) bm[0] |= 1;
        if (b == 0 && N >= 1) bm[0] |= 2;
        for (long n = 2; n <= N; n++) {
            uint64_t s = a + b;
            if (s >= p) s -= p;
            a = b; b = s;
            if (s == 0) bm[n >> 3] |= (uint8_t)(1u << (n & 7));
        }
        if ((i + 1) % CHUNK == 0)
            save(outpath, bm, bytes, prog, lo + i + 1, hi);
    }
    save(outpath, bm, bytes, prog, hi, hi);
    return 0;
}
