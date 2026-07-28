/* erdos700.c — f(n) = min_{1<k<=n/2} gcd(n, C(n,k)) for all composite n in a range.
 *
 * Erdős–Szekeres #700: (a) characterise composite n with f(n) = n/P(n) (P = largest
 * prime factor); (b) infinitely many composite n with f(n) > sqrt(n)?; (c) is
 * f(n) <<_A n/(log n)^A?
 *
 * Exact computation via Kummer: for p^a || n, v_p(C(n,k)) = number of carries when
 * adding k and n-k in base p. Only primes dividing n matter for the gcd:
 *   gcd(n, C(n,k)) = prod_{p^a || n} p^min(a, carries_p(k)).
 * Facts used:
 *   - f(n) | n and f(n) > 1 (Erdős–Szekeres: interior entries of a Pascal row share
 *     factors; gcd(n, C(n,k)) = gcd(C(n,1), C(n,k)) > 1). So f(n) >= q, the smallest
 *     prime factor of n — the k-scan early-exits the moment the running min hits q.
 *   - Carries counted digit-by-digit: adding k and n-k in base p, carry chain
 *     determined by digits of k vs digits of n (borrow criterion): c_p(k) = number of
 *     borrow positions when subtracting k from n in base p.
 *
 * Output: "F n f" for every composite n (full table, binary-compact would be nicer but
 * text keeps the artifact greppable; we gzip it), plus "BIG n f sqrt" lines whenever
 * f(n) > sqrt(n), plus a CERT line. Usage: erdos700 N n_lo n_hi [report_all(0|1)]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

typedef uint64_t u64;
typedef long long ll;

static void die(const char *m){ fprintf(stderr,"FATAL: %s\n",m); exit(2); }

static uint32_t *spf;
static ll NMAX;

int main(int argc, char **argv){
    if (argc<4) die("usage: erdos700 N n_lo n_hi [report_all]");
    NMAX = atoll(argv[1]);
    ll nlo = atoll(argv[2]), nhi = atoll(argv[3]);
    int report_all = (argc>4)? atoi(argv[4]) : 0;
    if (nhi>NMAX) die("bad range");
    spf = calloc((size_t)NMAX+1, sizeof(uint32_t));
    if (!spf) die("spf alloc");
    for (ll i=2;i<=NMAX;i++) if(!spf[i]) for (ll j=i;j<=NMAX;j+=i) if(!spf[j]) spf[j]=(uint32_t)i;

    long long composites=0, bigs=0;
    for (ll n=nlo;n<=nhi;n++){
        if (n<4 || spf[n]==(uint32_t)n) continue;      /* skip primes (f(p)=p, trivial) */
        composites++;
        /* factor n */
        ll pr[16]; int ex[16]; int np=0; ll x=n;
        while (x>1){ ll p=spf[x]; int e=0; while (x%p==0){x/=p;e++;} pr[np]=p; ex[np]=e; np++; }
        ll q = pr[0];                                   /* smallest prime factor: floor */
        /* digits of n base p, per prime (precompute) */
        int nd[16][44]; int nl[16];
        for (int t=0;t<np;t++){ ll y=n; int L=0;
            while (y){ nd[t][L++]=(int)(y%pr[t]); y/=pr[t]; } nl[t]=L; }
        ll best=-1;
        for (ll k=2;k<=n/2;k++){
            ll g=1;
            for (int t=0;t<np && g<((best<0)?n:best);t++){
                ll p=pr[t];
                /* carries adding k,(n-k) base p == borrows subtracting k from n */
                int carries=0, borrow=0; ll kk=k;
                for (int d=0; d<nl[t] && (kk||borrow); d++){
                    int kd = (int)(kk%p); kk/=p;
                    int ndg = nd[t][d] - borrow;
                    if (ndg < kd){ borrow=1; carries++; }
                    else borrow=0;
                }
                if (carries){ int c = carries<ex[t]? carries:ex[t];
                    for (int e=0;e<c;e++) g*=p; }
            }
            if (best<0 || g<best){ best=g; if (best==q) break; }
        }
        if (report_all) printf("F %lld %lld\n", n, best);
        if ((double)best*best > (double)n){ printf("BIG %lld %lld\n", n, best); bigs++; }
    }
    printf("CERT %lld %lld composites=%lld bigs=%lld\n", nlo, nhi, composites, bigs);
    return 0;
}
