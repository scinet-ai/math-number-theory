/* erdos699.c — exhaustive verification of Erdős #699 (Erdős–Szekeres) and census of
 * strong-form exceptions.
 *
 * Question (weak form, the open problem): for every 1 <= i < j <= n/2, is there a prime
 * p >= i with p | gcd(C(n,i), C(n,j))?  A counterexample disproves the conjecture.
 * Strong form (p > i) is known to fail in a few cases; we census every failure.
 * Note p >= i and p > i differ only when i is itself prime.
 *
 * Method, per n (all independent, sharded by n-range):
 *   - Divisibility by Kummer: p | C(n,i) iff subtracting i from n in base p borrows,
 *     i.e. some base-p digit of i exceeds n's digit. The NON-divisible i form a digit
 *     box (every digit e_k <= d_k); we enumerate that box directly to build, for a
 *     prime p, the bitmask over j in [0, n/2] of p | C(n,j). Masks are built LAZILY —
 *     only for primes that actually get applied in a cover check.
 *   - An incremental valuation sweep (C(n,i) = C(n,i-1)*(n-i+1)/i, factored by SPF
 *     sieve) maintains v_p(C(n,i)) for all p and a bitset PB of primes with v_p > 0.
 *     The primes >= i dividing C(n,i) are streamed from PB in ascending order.
 *   - Cover check: uncovered j's start as (i, n/2]; stream primes p >= i dividing
 *     C(n,i) ascending, uncovered &= ~mask_p, stop at zero. Anything left after the
 *     stream ends is a WEAK counterexample ("W n i j" — would disprove the
 *     conjecture; expected: none).
 *   - Strong census: when i is prime and i | C(n,i), redo the cover streaming only
 *     p > i; leftovers are strong-form failures ("S n i j" — the pair shares p = i
 *     but no larger prime). Known: i=2 (certain powers of 2), a few i=3, and (28,5,14).
 *   - Sylvester–Schur cross-check: every C(n,i), i <= n/2, must have a prime factor
 *     > i ("A n i" anomaly if not — machinery bug, not math, if it ever fires).
 *
 * Output: census/anomaly lines on stdout; final "CERT lo hi pairs=... weak=... strong=..."
 * summary. Usage: erdos699 N_MAX n_lo n_hi
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <inttypes.h>

typedef uint64_t u64;

static uint32_t *spf;          /* smallest prime factor, to N_MAX */
static int *primes, nprimes;   /* primes <= N_MAX */
static int *pidx_ge;           /* pidx_ge[x] = first prime index k with primes[k] >= x */
static int *pcount;            /* #primes <= x */
static int NMAX;

static void die(const char *m){ fprintf(stderr,"FATAL: %s\n",m); exit(2); }

static void sieve_init(void){
    spf = calloc((size_t)NMAX+1, sizeof(uint32_t));
    if(!spf) die("spf alloc");
    for (long long i=2;i<=NMAX;i++) if(!spf[i]) for (long long j=i;j<=NMAX;j+=i) if(!spf[j]) spf[j]=(uint32_t)i;
    primes = malloc(((size_t)NMAX/8+64)*sizeof(int));
    pcount = malloc(((size_t)NMAX+2)*sizeof(int));
    pidx_ge = malloc(((size_t)NMAX+2)*sizeof(int));
    if(!primes||!pcount||!pidx_ge) die("sieve tables alloc");
    nprimes=0; pcount[0]=0; pcount[1]=0;
    for (int i=2;i<=NMAX;i++){ if(spf[i]==(uint32_t)i) primes[nprimes++]=i; pcount[i]=nprimes; }
    pidx_ge[NMAX+1]=nprimes;
    int k=nprimes;
    for (int x=NMAX;x>=0;x--){
        if (x>=2 && spf[x]==(uint32_t)x) k = pcount[x]-1;
        pidx_ge[x]=k;
    }
}

/* ---- per-n state ---- */
static u64 *maskpool;          /* nprimes x wmax bitmask pool (lazy) */
static int *built;             /* stamp per prime index */
static int stamp=0;
static int words, wmax;        /* words for j in [0, m] */
static int cur_n, cur_m;

/* base-p digits of n: p=2, n=10^5 needs 17 digits — size generously and guard hard.
 * (A 16-entry array here silently smashed the stack for every n >= 65536.) */
#define MAXDIG 40
static long long pw[MAXDIG];

static void rec_clear(u64 *mask, int k, long long acc, const int *d){
    if (k<0){ mask[acc>>6] &= ~(1ULL<<(acc&63)); return; }
    for (int e=0;e<=d[k];e++){
        long long a2 = acc + (long long)e*pw[k];
        if (a2 > cur_m) break;
        rec_clear(mask, k-1, a2, d);
    }
}

static u64 *get_mask(int k){   /* mask over j of primes[k] | C(n,j), j in [0, cur_m] */
    u64 *mask = maskpool + (size_t)k*wmax;
    if (built[k]==stamp) return mask;
    built[k]=stamp;
    int p = primes[k];
    memset(mask, 0xff, (size_t)words*8);
    int excess = words*64 - (cur_m+1);
    if (excess) mask[words-1] &= (~0ULL) >> excess;   /* clear bits beyond m */
    int d[MAXDIG], L=0; long long x=cur_n;
    while (x){ if (L>=MAXDIG) die("digit overflow"); d[L++] = (int)(x % p); x /= p; }
    pw[0]=1; for (int t=1;t<L;t++) pw[t]=pw[t-1]*p;
    rec_clear(mask, L-1, 0, d);
    return mask;
}

static int *vals;              /* v_p(C(n,i)) per prime index */
static u64 *pb; static int pbwords;   /* bitset over prime indices with v>0 */

static inline void val_add(int x, int sign){
    while (x>1){
        int pr = spf[x], e=0;
        while (x % pr == 0){ x/=pr; e++; }
        int k = pcount[pr]-1;
        int was = vals[k];
        vals[k] += sign*e;
        if (vals[k]<0) die("negative valuation");
        if (was==0 && vals[k]>0) pb[k>>6] |= 1ULL<<(k&63);
        else if (was>0 && vals[k]==0) pb[k>>6] &= ~(1ULL<<(k&63));
    }
}

/* stream set bits of pb with index >= k0 and < klim, ascending; returns next index or -1 */
static inline int pb_next(int k, int klim){
    if (k>=klim) return -1;
    int w = k>>6;
    u64 x = pb[w] & ((~0ULL)<<(k&63));
    while (1){
        if (x){
            int r = (w<<6) + __builtin_ctzll(x);
            return (r<klim)? r : -1;
        }
        if (++w > (klim-1)>>6) return -1;
        x = pb[w];
    }
}

/* --check n: verify every mask bit against the Legendre valuation formula
 * v_p(C(n,i)) = sum_k floor(n/p^k) - floor(i/p^k) - floor((n-i)/p^k) — an
 * independent divisibility criterion (digit boxes never enter). */
static int mask_selfcheck(int n){
    cur_n=n; cur_m=n/2; words=cur_m/64+1; stamp++;
    int bad=0;
    for (int k=0;k<pcount[n];k++){
        int p=primes[k];
        u64 *mk = get_mask(k);
        for (int i=0;i<=cur_m;i++){
            long long v=0;
            for (long long q=p;q<=n;q*=p) v += n/q - i/q - (n-i)/q;
            int bit = (mk[i>>6]>>(i&63))&1;
            if (bit != (v>0)){ printf("BADMASK n=%d p=%d i=%d legendre=%lld bit=%d\n",n,p,i,v,bit); bad++; }
        }
    }
    printf("MASKCHECK %d %s (%d primes x %d cols)\n", n, bad?"FAIL":"OK", pcount[n], cur_m+1);
    return bad;
}

int main(int argc, char **argv){
    if (argc<4) die("usage: erdos699 N_MAX n_lo n_hi | N_MAX --check n");
    NMAX = atoi(argv[1]);
    int checkmode = !strcmp(argv[2], "--check");
    int nlo = checkmode ? atoi(argv[3]) : atoi(argv[2]);
    int nhi = checkmode ? nlo : atoi(argv[3]);
    if (nhi>NMAX || nlo<1) die("bad n range");
    sieve_init();
    int mmax = NMAX/2;
    wmax = mmax/64 + 1;
    maskpool = malloc((size_t)nprimes*wmax*8);
    built = calloc(nprimes, sizeof(int));
    vals = calloc(nprimes, sizeof(int));
    pbwords = nprimes/64 + 1;
    pb = calloc(pbwords, 8);
    u64 *uncov = malloc((size_t)wmax*8);
    if (!maskpool||!built||!vals||!pb||!uncov) die("alloc");
    if (checkmode) return mask_selfcheck(nlo) ? 3 : 0;

    long long pairs=0, weakfail=0, strongfail=0, anomalies=0;

    for (int n=nlo;n<=nhi;n++){
        cur_n=n; cur_m=n/2; words=cur_m/64+1; stamp++;
        memset(vals,0,(size_t)nprimes*sizeof(int));
        memset(pb,0,(size_t)pbwords*8);
        int npn = pcount[n];                 /* prime indices < npn are <= n */
        for (int i=1;i<=cur_m;i++){
            val_add(n-i+1, +1);
            val_add(i, -1);
            /* Sylvester–Schur: some prime > i divides C(n,i) */
            int kgt = pb_next(pidx_ge[i+1], npn);
            if (kgt<0){ printf("A %d %d\n", n, i); anomalies++; }
            if (i==cur_m) break;             /* no j > i left to pair with */
            pairs += cur_m - i;
            /* weak cover over j in (i, m]: stream primes >= i dividing C(n,i) */
            memset(uncov, 0, (size_t)words*8);
            for (int j=i+1;j<=cur_m;j++) uncov[j>>6] |= 1ULL<<(j&63);
            u64 rem=1;
            for (int k=pb_next(pidx_ge[i], npn); k>=0; k=pb_next(k+1, npn)){
                u64 *mk = get_mask(k);
                rem=0;
                for (int w=0;w<words;w++){ uncov[w] &= ~mk[w]; rem |= uncov[w]; }
                if (!rem) break;
            }
            if (rem){
                for (int w=0;w<words;w++){ u64 x=uncov[w];
                    while (x){ int j=(w<<6)+__builtin_ctzll(x); x&=x-1;
                        printf("W %d %d %d\n",n,i,j); weakfail++; } }
            }
            /* strong census: differs from weak only when i prime and i | C(n,i) */
            if (i>=2 && spf[i]==(uint32_t)i && vals[pcount[i]-1]>0){
                memset(uncov, 0, (size_t)words*8);
                for (int j=i+1;j<=cur_m;j++) uncov[j>>6] |= 1ULL<<(j&63);
                u64 rem2=1;
                for (int k=pb_next(pidx_ge[i+1], npn); k>=0; k=pb_next(k+1, npn)){
                    u64 *mk = get_mask(k);
                    rem2=0;
                    for (int w=0;w<words;w++){ uncov[w] &= ~mk[w]; rem2 |= uncov[w]; }
                    if (!rem2) break;
                }
                if (rem2){
                    for (int w=0;w<words;w++){ u64 x=uncov[w];
                        while (x){ int j=(w<<6)+__builtin_ctzll(x); x&=x-1;
                            printf("S %d %d %d\n",n,i,j); strongfail++; } }
                }
            }
        }
    }
    printf("CERT %d %d pairs=%lld weak=%lld strong=%lld anomalies=%lld\n",
           nlo, nhi, pairs, weakfail, strongfail, anomalies);
    return 0;
}
