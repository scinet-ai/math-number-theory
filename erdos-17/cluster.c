/* cluster.c (v2) — exhaustive classification of primes as cluster / non-cluster
 * (Erdős #17, OEIS A038134 / A038133), single block [lo, hi), single thread.
 *
 * Definition: odd prime p is a CLUSTER prime iff every even n with 0 < n <= p-3
 * is a difference q1 - q2 of two primes q1, q2 <= p.  (2 is excluded; p=3 is
 * vacuously a cluster prime.)
 *
 * Mathematical core (proof in README.md):
 *   For even m >= 2 let k(m) = least odd prime k with m + k prime
 *   (q2 = 2 never helps: m even => m + 2 even composite).
 *   m is a difference of two primes <= P  iff  m + k(m) <= P.
 *   p non-cluster <=> exists odd COMPOSITE j, 9 <= j <= p-2, with k(p-j) > j
 *   (j = p - m; if j were prime then m + j = p would give k(m) <= j).
 *   "k(m) > j" <=> no odd prime k <= j has m + k prime.
 *
 * Algorithm per sub-segment (odd-number bitmap B, prefix/suffix MARGIN):
 *   1. sieve: mod-15015 presieve pattern (3,5,7,11,13) + segmented Eratosthenes;
 *   2. p-side pass: for each prime p, one 128-bit AND per odd composite j <= 255
 *      against the window of primes within 254 below p; primes passing all j
 *      are "survivors";
 *   3. m-side pass: shift-OR covered mask finds all heavy even m (k(m) > 251);
 *      exact k(m) by scalar scan; survivors p in (m + 255, m + k(m)) are demoted
 *      (j = p - m is automatically composite: j prime would force k(m) <= j).
 *   Blocks with j <= 255 are exactly the p-side; blocks with j >= 257 require
 *   k(m) > j >= 257 > 251, i.e. a heavy m => exactly the m-side.
 *
 * Output: one CSV line on stdout:
 *   lo,hi,odd_primes,cluster,noncluster,min_cluster,max_cluster,fnv_cluster,
 *   heavy,max_km,argmax_km,demoted,samp_nc_p,samp_nc_j,samp_dem_p,samp_dem_j,
 *   first_cl,last_cl,secs
 * Options: --emit-cluster-list  (cluster primes to stderr, for b-file diff)
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

typedef uint64_t u64;
typedef uint32_t u32;

#define MARGIN 65536ULL                 /* numbers of prefix/suffix slack      */
#define SEG_BITS (1ULL<<25)             /* odd-bitmap bits per sub-segment     */
#define SEG_SPAN (SEG_BITS*2ULL)        /* numbers per sub-segment             */
#define BASE_LIM 5000000ULL             /* base sieve limit; supports hi<=2.5e13 */
#define KV 251                          /* covered-pass odd-prime threshold    */
#define JMAX 255                        /* p-side j-table upper bound          */
#define WHEEL 15015                     /* 3*5*7*11*13 presieve period (bits)  */
#define MAX_SURV (1u<<22)

static u32 *base_primes; static u32 n_base, base_skip;
static u32 *odd_primes_small; static u32 n_odd_small;  /* odd primes < 65536 */
static u32 idx_257;                      /* index of 257 in odd_primes_small  */
static uint8_t comp_small[65536];        /* 1 if odd composite (or 1)         */
static u64 patw[WHEEL];                  /* presieve word starting at A mod WHEEL */

/* p-side j-table masks */
static u64 mask_lo[128], mask_hi[128]; static int jtab[128]; static int n_jtab;

static void build_small(void){
    static uint8_t c[BASE_LIM+1];
    for(u64 i=2;i*i<=BASE_LIM;i++) if(!c[i]) for(u64 j=i*i;j<=BASE_LIM;j+=i) c[j]=1;
    base_primes = malloc(400000*sizeof(u32));
    odd_primes_small = malloc(7000*sizeof(u32));
    for(u64 i=2;i<=BASE_LIM;i++) if(!c[i]){
        if(i>2) base_primes[n_base++]=(u32)i;
        if(i>2 && i<65536) odd_primes_small[n_odd_small++]=(u32)i;
    }
    base_skip=5;                          /* skip 3,5,7,11,13 (presieved) */
    for(u32 i=1;i<65536;i+=2) comp_small[i]=1;
    for(u32 i=0;i<n_odd_small;i++) comp_small[odd_primes_small[i]]=0;
    comp_small[1]=1;
    for(u32 i=0;i<n_odd_small;i++) if(odd_primes_small[i]==257){ idx_257=i; break; }
    /* presieve pattern: D[A]=1 iff 2A+1 divisible by 3,5,7,11,13 (A mod WHEEL) */
    static uint8_t D[WHEEL+64];
    const int pr[5]={3,5,7,11,13};
    for(int i=0;i<5;i++){
        int q=pr[i], a0=(q-1)/2;          /* 2a+1 = q  => first odd multiple */
        for(int a=a0;a<WHEEL+64;a+=q) D[a]=1;
    }
    for(int r=0;r<WHEEL;r++){
        u64 w=0;
        for(int b=0;b<64;b++){ int a=r+b; if(a>=WHEEL) a-=WHEEL; if(!D[a]) w|=1ULL<<b; }
        patw[r]=w;
    }
    /* j-table: odd composite j in [9, JMAX]; mask bit 127-(j-k)/2, odd prime k<j */
    for(int j=9;j<=JMAX;j+=2){
        if(!comp_small[j]) continue;
        u64 lo=0,hi=0;
        for(u32 i=0;i<n_odd_small && odd_primes_small[i]<(u32)j;i++){
            int pos=127-(j-(int)odd_primes_small[i])/2;
            if(pos<64) lo|=1ULL<<pos; else hi|=1ULL<<(pos-64);
        }
        jtab[n_jtab]=j; mask_lo[n_jtab]=lo; mask_hi[n_jtab]=hi; n_jtab++;
    }
}

/* reference classifier for small odd primes (needs p < 3000) */
static int is_cluster_ref(u64 p){
    for(u64 n=2;n+3<=p;n+=2){
        int ok=0;
        for(u32 i=0;i<n_odd_small;i++){
            u64 q2=odd_primes_small[i]; if(q2+n>p) break;
            if(!comp_small[q2+n]){ ok=1; break; }
        }
        if(!ok) return 0;
    }
    return 1;
}

static inline u64 get64(const u64*w, u64 bitidx){
    u64 wi=bitidx>>6, b=bitidx&63;
    u64 r=w[wi]>>b;
    if(b) r |= w[wi+1]<<(64-b);
    return r;
}

/* covered-pass shift lists as compile-time constants:
   odd primes k<=251, s=(k-1)/2:  s<64 and s>=64 groups */
#define SHL(F) F(1)F(2)F(3)F(5)F(6)F(8)F(9)F(11)F(14)F(15)F(18)F(20)F(21)F(23)\
F(26)F(29)F(30)F(33)F(35)F(36)F(39)F(41)F(44)F(48)F(50)F(51)F(53)F(54)F(56)F(63)
#define SHH(F) F(65)F(68)F(69)F(74)F(75)F(78)F(81)F(83)F(86)F(89)F(90)F(95)\
F(96)F(98)F(99)F(105)F(111)F(113)F(114)F(116)F(119)F(120)F(125)

int main(int argc,char**argv){
    if(argc<3){ fprintf(stderr,"usage: %s lo hi [--emit-cluster-list]\n",argv[0]); return 2; }
    u64 LO=strtoull(argv[1],0,10), HI=strtoull(argv[2],0,10);
    int emit = (argc>3 && !strcmp(argv[3],"--emit-cluster-list"));
    if(LO%2||HI%2){ fprintf(stderr,"bounds must be even\n"); return 2; }
    if(HI+MARGIN > BASE_LIM*BASE_LIM){ fprintf(stderr,"hi too large\n"); return 2; }
    clock_t t0=clock();
    build_small();

    u64 nwords_alloc = SEG_BITS/64 + 2*(MARGIN/128) + 16;
    u64 *B = malloc(nwords_alloc*8);
    u64 *surv = malloc(MAX_SURV*8);       /* survivor primes (absolute values) */
    uint8_t *dem = malloc(MAX_SURV);      /* demoted flags */

    u64 c_odd=0,c_cl=0,c_nc=0,min_cl=0,max_cl=0,fnv=1469598103934665603ULL;
    u64 heavy=0,max_km=0,arg_km=0,n_dem_total=0;
    u64 samp_nc=0; u32 samp_nc_j=0; u64 samp_dem=0; u32 samp_dem_j=0;
    u64 first_cl=0,last_cl=0;

    for(u64 sub_lo=LO; sub_lo<HI; sub_lo+=SEG_SPAN){
        u64 sub_hi = sub_lo+SEG_SPAN<HI ? sub_lo+SEG_SPAN : HI;
        u64 seg_base = sub_lo>=MARGIN ? sub_lo-MARGIN : 0;      /* even */
        u64 seg_top  = sub_hi+MARGIN;                            /* even */
        u64 nbits=(seg_top-seg_base)/2, nwords=(nbits+63)/64;
        /* fill with presieve pattern: bit t <-> A = seg_base/2 + t */
        {
            u64 T0=seg_base/2;
            u32 r=(u32)((T0)%WHEEL);
            for(u64 j=0;j<nwords+2;j++){
                B[j]=patw[r];
                r+=64; if(r>=WHEEL) r-=WHEEL;
            }
        }
        if(nbits&63) B[nwords-1] &= (~0ULL)>>(64-(nbits&63));
        B[nwords]=0; B[nwords+1]=0;
        if(seg_base==0){
            B[0]&=~1ULL;                                         /* 1 not prime */
            B[0]|=(1ULL<<1)|(1ULL<<2)|(1ULL<<3)|(1ULL<<5)|(1ULL<<6); /* 3 5 7 11 13 */
        }
        /* sieve remaining base primes */
        for(u32 bi=base_skip;bi<n_base;bi++){
            u64 q=base_primes[bi];
            if(q*q>=seg_top) break;
            u64 s=q*q;
            if(s<seg_base) s=((seg_base+q)/(2*q))*(2*q)+q;
            for(u64 t=(s-seg_base-1)/2; t<nbits; t+=q) B[t>>6]&=~(1ULL<<(t&63));
        }

        /* ---- p-side pass: classify by j-table; collect survivors ---- */
        u64 n_surv=0;
        u64 pt_lo=(sub_lo-seg_base)/2, pt_hi=(sub_hi-seg_base)/2;
        u64 pw_lo=pt_lo>>6, pw_hi=(pt_hi+63)>>6;
        for(u64 w=pw_lo;w<pw_hi;w++){
            u64 x=B[w];
            if(w==pw_lo && (pt_lo&63)) x &= (~0ULL)<<(pt_lo&63);
            if(w==pw_hi-1 && (pt_hi&63)) x &= (~0ULL)>>(64-(pt_hi&63));
            while(x){
                int b=__builtin_ctzll(x); x&=x-1;
                u64 t=(w<<6)+b, p=seg_base+2*t+1;
                c_odd++;
                int cluster;
                if(p<3000) cluster=is_cluster_ref(p);
                else{
                    cluster=1;
                    u64 lo64=get64(B,t-127), hi64=get64(B,t-63);
                    for(int ji=0;ji<n_jtab;ji++){
                        if(((lo64&mask_lo[ji])|(hi64&mask_hi[ji]))==0){
                            cluster=0;
                            if(!samp_nc){ samp_nc=p; samp_nc_j=(u32)jtab[ji]; }
                            break;
                        }
                    }
                }
                if(cluster){
                    if(n_surv>=MAX_SURV){ fprintf(stderr,"FATAL surv overflow\n"); return 3; }
                    surv[n_surv]=p; dem[n_surv]=0; n_surv++;
                } else c_nc++;
            }
        }

        /* ---- m-side pass: heavy m, demote survivors ---- */
        u64 m_start = sub_lo>=MARGIN ? sub_lo-MARGIN : 2;
        u64 t_lo=(m_start-seg_base)/2, t_hi=(sub_hi-seg_base)/2;
        u64 w_lo=t_lo>>6, w_hi=(t_hi+63)>>6, si=0;
        for(u64 w=w_lo;w<w_hi;w++){
            const u64 b0=B[w],b1=B[w+1],b2=B[w+2];
            u64 c=0;
#define FL(S) c|=(b0>>S)|(b1<<(64-S));
#define FH(S) c|=(b1>>(S-64))|(b2<<(128-S));
            SHL(FL) SHH(FH)
#undef FL
#undef FH
            u64 h=~c;
            if(w==w_lo && (t_lo&63)) h &= (~0ULL)<<(t_lo&63);
            if(w==w_hi-1 && (t_hi&63)) h &= (~0ULL)>>(64-(t_hi&63));
            while(h){
                int b=__builtin_ctzll(h); h&=h-1;
                u64 t=(w<<6)+b;
                u64 m=seg_base+2*t;
                if(m<2) continue;
                heavy++;
                u64 km=0;
                for(u32 i=idx_257;i<n_odd_small;i++){
                    u64 k=odd_primes_small[i], tt=t+(k-1)/2;
                    if(tt>=nbits) break;
                    if(B[tt>>6]>>(tt&63)&1){ km=k; break; }
                }
                if(!km){ fprintf(stderr,"FATAL k(m) overflow m=%llu\n",(unsigned long long)m); return 3; }
                if(km>max_km){ max_km=km; arg_km=m; }
                /* demote survivors p in (m+255, m+km) */
                while(si<n_surv && surv[si]<=m+255) si++;
                for(u64 s2=si; s2<n_surv && surv[s2]<m+km; s2++){
                    if(!dem[s2]){
                        dem[s2]=1;
                        if(!samp_dem){ samp_dem=surv[s2]; samp_dem_j=(u32)(surv[s2]-m); }
                    }
                }
            }
        }

        /* ---- finalize sub-segment ---- */
        for(u64 i2=0;i2<n_surv;i2++){
            if(dem[i2]){ c_nc++; n_dem_total++; continue; }
            u64 p=surv[i2];
            c_cl++; if(!min_cl)min_cl=p; if(p>max_cl)max_cl=p;
            if(!first_cl)first_cl=p; last_cl=p;
            fnv^=p; fnv*=1099511628211ULL;
            if(emit) fprintf(stderr,"%llu\n",(unsigned long long)p);
        }
    }
    double secs=(double)(clock()-t0)/CLOCKS_PER_SEC;
    printf("%llu,%llu,%llu,%llu,%llu,%llu,%llu,%016llx,%llu,%llu,%llu,%llu,%llu,%u,%llu,%u,%llu,%llu,%.2f\n",
        (unsigned long long)LO,(unsigned long long)HI,
        (unsigned long long)c_odd,(unsigned long long)c_cl,(unsigned long long)c_nc,
        (unsigned long long)min_cl,(unsigned long long)max_cl,(unsigned long long)fnv,
        (unsigned long long)heavy,(unsigned long long)max_km,(unsigned long long)arg_km,
        (unsigned long long)n_dem_total,
        (unsigned long long)samp_nc,samp_nc_j,
        (unsigned long long)samp_dem,samp_dem_j,
        (unsigned long long)first_cl,(unsigned long long)last_cl,secs);
    return 0;
}
