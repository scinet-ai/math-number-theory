/* packer.c — exhaustive verification of the Gyarfas tree packing conjecture
 * (Erdos problem #743) for a fixed board size n.
 *
 * The conjecture: any family of trees T_2, ..., T_n with |T_k| = k packs
 * (edge-disjointly, hence exactly) into the complete graph K_n.
 *
 * This program sweeps EVERY family for the given n: the top tree T_n is fixed
 * by the command-line index top_index (one "chunk" per unlabeled tree on n
 * vertices), and all combinations of unlabeled trees at sizes n-1 down to 2
 * are enumerated in lexicographic order of their file indices.
 *
 * Symmetry reduction (exact, no loss): T_n has n vertices, so any embedded
 * copy of it is a spanning tree of K_n. Aut(K_n) = S_n acts transitively on
 * the copies of any fixed spanning tree, so WLOG T_n is embedded by the
 * identity map (tree vertex i -> board vertex i). Every packing of a family
 * is equivalent under S_n to one extending this canonical embedding, and
 * conversely. So a family packs iff the remaining trees T_{n-1},...,T_2 pack
 * into K_n minus the canonical copy of T_n.
 *
 * Per family:
 *   fast path  — greedy first-fit: place trees in decreasing size, taking the
 *                first embedding found in a fixed deterministic order; shared
 *                across families with a common prefix of large trees.
 *   fallback   — if greedy dies, an independent complete backtracking search
 *                over all embeddings of T_{n-1}..T_2 (largest first), from
 *                scratch, for each affected family. Exhaustion = the family
 *                does NOT pack = counterexample to the conjecture.
 *
 * Result codes per family:
 *   0 packed by shared greedy      1 packed by backtracking search
 *   2 NO PACKING EXISTS (counterexample!)   3 undecided (node cap hit)
 *
 * Output (out_dir/):
 *   chunk_NNN.txt   — counts per code, running FNV-1a hash of all witnesses,
 *                     list of every family with code >= 1
 *   sample_NNN.txt  — full packing witness for every sample_stride-th family
 *                     plus every family with code >= 1. Witness format: one
 *                     line "family_index  idx(n-1) .. idx(2)  <m hex chars>"
 *                     where hex char at position e is the size of the tree
 *                     using board edge e (edges of K_n in lexicographic
 *                     order (0,1),(0,2),...,(n-2,n-1); sizes 2..11 print as
 *                     2..9,a,b).
 *
 * Deterministic: no randomness; embedding order is ascending board vertex;
 * tree order is the order in the trees_KK.txt files.
 *
 * Build: clang -O2 -o packer packer.c
 * Usage: packer n top_index trees_dir out_dir sample_stride node_cap
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <inttypes.h>

#define MAXN 11
#define MAXM 55            /* C(11,2) */
#define MAXTREES 235       /* trees on 11 vertices */

typedef struct { int k; uint8_t par[MAXN]; } Tree;

static int nboard, medges;                 /* n and C(n,2) */
static uint64_t edge_bit[MAXN][MAXN];      /* board edge (u,v) -> single-bit mask */
static int edge_index[MAXN][MAXN];
static Tree trees[MAXN + 1][MAXTREES];     /* trees[k][i], sizes 2..n */
static int ntrees[MAXN + 1];

static uint8_t label[MAXM];                /* per-edge tree size of current packing */
static int cur_family[MAXN + 1];           /* chosen tree index per size */

static uint64_t fam_counter;               /* families completed in this chunk */
static uint64_t count_code[4];
static uint64_t witness_fnv = 0xcbf29ce484222325ULL;
static uint64_t sample_stride, node_cap, node_count;
static FILE *sample_file, *chunk_file;

/* ---------- input ---------- */

static void load_trees(const char *dir) {
    char path[512], line[256];
    for (int k = 2; k <= nboard; k++) {
        snprintf(path, sizeof path, "%s/trees_%02d.txt", dir, k);
        FILE *f = fopen(path, "r");
        if (!f) { fprintf(stderr, "cannot open %s\n", path); exit(2); }
        int cnt = 0;
        while (fgets(line, sizeof line, f)) {
            Tree *t = &trees[k][cnt];
            t->k = k;
            t->par[0] = 0;
            char *p = line;
            for (int v = 1; v < k; v++) {
                long pv = strtol(p, &p, 10);
                if (pv < 0 || pv >= v) { fprintf(stderr, "bad parent in %s\n", path); exit(2); }
                t->par[v] = (uint8_t)pv;
            }
            cnt++;
        }
        fclose(f);
        ntrees[k] = cnt;
    }
}

/* ---------- witness recording ---------- */

static void fnv_fold_labels(void) {
    for (int e = 0; e < medges; e++) {
        witness_fnv ^= label[e];
        witness_fnv *= 0x100000001b3ULL;
    }
}

static void write_witness_line(int code) {
    fprintf(sample_file, "%" PRIu64 " %d ", fam_counter, code);
    for (int k = nboard - 1; k >= 2; k--) fprintf(sample_file, "%d ", cur_family[k]);
    fputc(' ', sample_file);
    for (int e = 0; e < medges; e++) fputc("0123456789ab"[label[e]], sample_file);
    fputc('\n', sample_file);
}

static void record_family(int code) {
    count_code[code]++;
    if (code <= 1) fnv_fold_labels();
    if (code >= 1) {
        fprintf(chunk_file, "nongreedy %" PRIu64 " code %d family", fam_counter, code);
        for (int k = nboard - 1; k >= 2; k--) fprintf(chunk_file, " %d", cur_family[k]);
        fputc('\n', chunk_file);
        write_witness_line(code);
    } else if (fam_counter % sample_stride == 0) {
        write_witness_line(code);
    }
    fam_counter++;
}

/* ---------- greedy first-fit embedding ---------- */

static int embed_first_rec(const Tree *T, int t, uint64_t freem,
                           uint16_t used, uint8_t *map, uint64_t *placed) {
    if (t == T->k) return 1;
    int pb = map[T->par[t]];
    for (int v = 0; v < nboard; v++) {
        if (used & (uint16_t)(1u << v)) continue;
        uint64_t b = edge_bit[pb][v];
        if (!(freem & b)) continue;
        map[t] = (uint8_t)v;
        *placed |= b;
        if (embed_first_rec(T, t + 1, freem, used | (uint16_t)(1u << v), map, placed))
            return 1;
        *placed &= ~b;
    }
    return 0;
}

/* Finds the first embedding of T into the free-edge set; writes edge labels. */
static int embed_first(const Tree *T, uint64_t freem, uint64_t *out_edges) {
    uint8_t map[MAXN];
    for (int r = 0; r < nboard; r++) {
        uint64_t placed = 0;
        map[0] = (uint8_t)r;
        if (embed_first_rec(T, 1, freem, (uint16_t)(1u << r), map, &placed)) {
            *out_edges = placed;
            for (int e = 0; e < medges; e++)
                if (placed & (1ULL << e)) label[e] = (uint8_t)T->k;
            return 1;
        }
    }
    return 0;
}

/* ---------- complete backtracking search (fallback), one family ---------- */

#define SOLVE_OK 1
#define SOLVE_FAIL 0
#define SOLVE_CAP (-1)

static int solve_level(int k, uint64_t freem);

/* enumerate embeddings of tree at size `level`; on each complete placement,
 * recurse into the next level; backtrack across levels */
static int place_rec(const Tree *T, int t, uint64_t freem, uint64_t placed,
                     uint16_t used, uint8_t *map, int level) {
    if (t == T->k) {
        for (int e = 0; e < medges; e++)
            if (placed & (1ULL << e)) label[e] = (uint8_t)T->k;
        return solve_level(level - 1, freem & ~placed);
    }
    int pb = map[T->par[t]];
    for (int v = 0; v < nboard; v++) {
        if (used & (uint16_t)(1u << v)) continue;
        uint64_t b = edge_bit[pb][v];
        if (!(freem & b)) continue;
        if (++node_count > node_cap) return SOLVE_CAP;
        map[t] = (uint8_t)v;
        int r = place_rec(T, t + 1, freem, placed | b, used | (uint16_t)(1u << v), map, level);
        if (r != SOLVE_FAIL) return r;
    }
    return SOLVE_FAIL;
}

static int solve_level(int k, uint64_t freem) {
    if (k == 1) return SOLVE_OK;           /* all trees down to size 2 placed */
    const Tree *T = &trees[k][cur_family[k]];
    uint8_t map[MAXN];
    for (int r = 0; r < nboard; r++) {
        if (++node_count > node_cap) return SOLVE_CAP;
        map[0] = (uint8_t)r;
        int res = place_rec(T, 1, freem, 0, (uint16_t)(1u << r), map, k);
        if (res != SOLVE_FAIL) return res;
    }
    return SOLVE_FAIL;
}

/* Complete search for the current family from the canonical-T_n position.
 * Returns result code 1, 2 or 3. */
static int full_solve(uint64_t mask_after_top) {
    node_count = 0;
    int r = solve_level(nboard - 1, mask_after_top);
    if (r == SOLVE_OK) return 1;
    if (r == SOLVE_CAP) return 3;
    return 2;                              /* exhausted: no packing exists */
}

static uint64_t mask_after_top_global;

/* greedy failed at some level: run the complete search for every family in
 * the affected block (all index combinations at sizes below_k-1 .. 2),
 * preserving lexicographic family order */
static void fallback_enum(int k) {
    if (k == 1) {
        /* full_solve scribbles on the shared witness array; the greedy sweep
         * above us still relies on its own labels, so save and restore */
        uint8_t saved[MAXM];
        memcpy(saved, label, sizeof label);
        int code = full_solve(mask_after_top_global);
        if (code == 2) {
            fprintf(chunk_file, "COUNTEREXAMPLE candidate at family %" PRIu64 "\n", fam_counter);
            fflush(chunk_file);
            fprintf(stderr, "COUNTEREXAMPLE candidate: no packing for family %" PRIu64 "\n", fam_counter);
        }
        record_family(code);
        memcpy(label, saved, sizeof label);
        return;
    }
    for (int i = 0; i < ntrees[k]; i++) {
        cur_family[k] = i;
        fallback_enum(k - 1);
    }
}

/* ---------- the shared-prefix greedy sweep ---------- */

static void sweep(int k, uint64_t freem) {
    if (k == 1) {                          /* every tree placed greedily */
        record_family(0);
        return;
    }
    for (int i = 0; i < ntrees[k]; i++) {
        cur_family[k] = i;
        uint64_t placed;
        if (embed_first(&trees[k][i], freem, &placed))
            sweep(k - 1, freem & ~placed);
        else
            fallback_enum(k - 1);          /* greedy dead under this prefix */
    }
}

/* ---------- main ---------- */

int main(int argc, char **argv) {
    if (argc != 7) {
        fprintf(stderr,
            "usage: %s n top_index trees_dir out_dir sample_stride node_cap\n", argv[0]);
        return 2;
    }
    nboard = atoi(argv[1]);
    int top_index = atoi(argv[2]);
    const char *trees_dir = argv[3], *out_dir = argv[4];
    sample_stride = strtoull(argv[5], NULL, 10);
    if (sample_stride == 0) sample_stride = 1;
    node_cap = strtoull(argv[6], NULL, 10);
    if (nboard < 3 || nboard > MAXN) { fprintf(stderr, "n out of range\n"); return 2; }

    medges = nboard * (nboard - 1) / 2;
    int idx = 0;
    for (int u = 0; u < nboard; u++)
        for (int v = u + 1; v < nboard; v++) {
            edge_index[u][v] = edge_index[v][u] = idx;
            edge_bit[u][v] = edge_bit[v][u] = 1ULL << idx;
            idx++;
        }

    load_trees(trees_dir);
    if (top_index < 0 || top_index >= ntrees[nboard]) {
        fprintf(stderr, "top_index out of range (0..%d)\n", ntrees[nboard] - 1);
        return 2;
    }

    uint64_t expected = 1;
    for (int k = 2; k < nboard; k++) expected *= (uint64_t)ntrees[k];

    char path[512], tmp[520];
    snprintf(path, sizeof path, "%s/chunk_%03d.txt", out_dir, top_index);
    snprintf(tmp, sizeof tmp, "%s.tmp", path);
    chunk_file = fopen(tmp, "w");
    if (!chunk_file) { perror("chunk file"); return 2; }
    char spath[512], stmp[520];
    snprintf(spath, sizeof spath, "%s/sample_%03d.txt", out_dir, top_index);
    snprintf(stmp, sizeof stmp, "%s.tmp", spath);
    sample_file = fopen(stmp, "w");
    if (!sample_file) { perror("sample file"); return 2; }

    /* canonical embedding of the top tree: tree vertex i -> board vertex i */
    const Tree *top = &trees[nboard][top_index];
    uint64_t full = (medges == 64) ? ~0ULL : ((1ULL << medges) - 1);
    uint64_t top_edges = 0;
    for (int v = 1; v < nboard; v++) top_edges |= edge_bit[top->par[v]][v];
    for (int e = 0; e < medges; e++)
        if (top_edges & (1ULL << e)) label[e] = (uint8_t)nboard;
    mask_after_top_global = full & ~top_edges;
    cur_family[nboard] = top_index;

    fprintf(chunk_file, "n %d top_index %d expected_families %" PRIu64
            " sample_stride %" PRIu64 " node_cap %" PRIu64 "\n",
            nboard, top_index, expected, sample_stride, node_cap);

    sweep(nboard - 1, mask_after_top_global);

    fprintf(chunk_file, "families %" PRIu64 "\n", fam_counter);
    fprintf(chunk_file, "greedy %" PRIu64 " backtrack %" PRIu64
            " unsat %" PRIu64 " undecided %" PRIu64 "\n",
            count_code[0], count_code[1], count_code[2], count_code[3]);
    fprintf(chunk_file, "witness_fnv 0x%016" PRIx64 "\n", witness_fnv);
    fprintf(chunk_file, "complete %s\n", fam_counter == expected ? "yes" : "NO");
    fclose(chunk_file);
    fclose(sample_file);
    if (fam_counter != expected) {
        fprintf(stderr, "chunk %d: family count mismatch!\n", top_index);
        return 3;
    }
    rename(tmp, path);
    rename(stmp, spath);
    printf("chunk %3d: families %" PRIu64 " greedy %" PRIu64 " backtrack %" PRIu64
           " unsat %" PRIu64 " undecided %" PRIu64 " fnv 0x%016" PRIx64 "\n",
           top_index, fam_counter, count_code[0], count_code[1],
           count_code[2], count_code[3], witness_fnv);
    return (count_code[2] || count_code[3]) ? 1 : 0;
}
