/* cluster.c — exhaustive classification of primes as cluster / non-cluster
 * (Erdős #17, OEIS A038134 / A038133), single block [lo, hi), single thread.
 *
 * Definition: odd prime p is a CLUSTER prime iff every even n with 0 < n <= p-3
 * is a difference q1 - q2 of two primes q1, q2 <= p.  (2 is excluded; p=3 is
 * vacuously a cluster prime.)
 *
 * Mathematical core (proved in README):
 *   For even m let k(m) = least odd prime k with m + k prime
 *   (q2 = 2 never helps: m even => m+2 even).  Let f(m) = m + k(m).
 *   m is a difference of two primes <= P  iff  f(m) <= P.
 *   p non-cluster  <=>  exists even m <= p-3 with f(m) > p
 *                  <=>  exists odd COMPOSITE j (9 <= j <= p-2) with k(p-j) > j,
 *   because j = p - m prime would give m + j = p, i.e. k(m) <= j.
 *   "k(p-j) > j" <=> no odd prime k <= j has p - j + k prime
 *               <=> no prime q < p at even distance e = j - k with k = j - e prime.
 *
 * Algorithm per block:
 *   1. segmented odd-bitmap sieve of Eratosthenes;
 *   2. p-side: for each prime p, test all odd composite j <= 255 with one
 *      128-bit AND per j against the window of primes within 254 below p;
 *   3. m-side: vector shift-OR pass finds all "heavy" even m with k(m) > 251;
 *      for those, exact k(m) by scalar scan, and every prime p = m + j with
 *      odd composite j in (255, k(m)) is marked non-cluster ("marks").
 *   Blocks j <= 255 are exactly the p-side; blocks j >= 257 require
 *   k(m) > j >= 257 > 251, i.e. a heavy m => exactly the m-side.  QED.
 *
 * Output: one CSV line on stdout:
 *   lo,hi,odd_primes,cluster,noncluster,min_cluster,max_cluster,fnv_cluster,
 *   heavy,max_km,argmax_km,marks,first_nc_p,first_nc_j,first_cl,last_cl,secs
 * Options: --emit-cluster-list  (prints cluster primes to stderr, for b-file diff)
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
#define KV 251                          /* vector-covered odd-prime threshold  */
#define JMAX 255                        /* p-side j-table upper bound          */

static u32 *base_primes; static u32 n_base;
static u32 *odd_primes_small; static u32 n_odd_small;  /* odd primes < 65536 */
static u32 idx_257;                      /* index of 257 in odd_primes_small  */
static uint8_t comp_small[65536];        /* 1 if odd composite (or 1)          */

/* p-side j-table masks */
static u64 mask_lo[128], mask_hi[128]; static int jtab[128]; static int n_jtab;
/* covered-pass shifts: (k-1)/2 for odd primes k <= KV */
static int shifts[64]; static int n_shifts;

static void build_small(void){
    static uint8_t c[BASE_LIM+1];
    for(u64 i=2;i*i<=BASE_LIM;i++) if(!c[i]) for(u64 j=i*i;j<=BASE_LIM;j+=i) c[j]=1;
    base_primes = malloc(400000*sizeof(u32));
    odd_primes_small = malloc(7000*sizeof(u32));
    for(u64 i=2;i<=BASE_LIM;i++) if(!c[i]){
        if(i>2) base_primes[n_base++]=(u32)i;
        if(i>2 && i<65536) odd_primes_small[n_odd_small++]=(u32)i;
    }
    for(u32 i=1;i<65536;i+=2) comp_small[i]=1;
    for(u32 i=0;i<n_odd_small;i++) comp_small[odd_primes_small[i]]=0;
    comp_small[1]=1;
    for(u32 i=0;i<n_odd_small;i++) if(odd_primes_small[i]==257){ idx_257=i; break; }
    /* covered shifts */
    for(u32 i=0;i<n_odd_small && odd_primes_small[i]<=KV;i++)
        shifts[n_shifts++]=(odd_primes_small[i]-1)/2;
    /* j-table: odd composite j in [9, JMAX]; mask bit position 127-(j-k)/2 for
       odd prime k < j */
    for(int j=9;j<=JMAX;j+=2){
        if(!comp_small[j]) continue;
        u64 lo=0,hi=0;
        for(u32 i=0;i<n_odd_small && odd_primes_small[i]<(u32)j;i++){
            int e2=(j-(int)odd_primes_small[i])/2;   /* e/2 in [1,(j-3)/2] */
            int pos=127-e2;
            if(pos<64) lo|=1ULL<<pos; else hi|=1ULL<<(pos-64);
        }
        jtab[n_jtab]=j; mask_lo[n_jtab]=lo; mask_hi[n_jtab]=hi; n_jtab++;
    }
}

/* reference classifier for small odd primes (needs p < 3000) */
static int is_cluster_ref(u64 p){
    /* every even n <= p-3 must be q1-q2, q1,q2 odd primes <= p */
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

typedef struct { u64 p; u32 j; } Mark;
static int cmp_mark(const void*a,const void*b){
    u64 x=((const Mark*)a)->p, y=((const Mark*)b)->p;
    return x<y?-1:(x>y?1:0);
}

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
    Mark *marks = malloc(sizeof(Mark)*(1u<<23)); u64 n_marks_total=0;

    /* accumulators */
    u64 c_odd=0,c_cl=0,c_nc=0,min_cl=0,max_cl=0,fnv=1469598103934665603ULL;
    u64 heavy=0,max_km=0,arg_km=0;
    u64 first_nc=0; u32 first_nc_j=0; u64 first_cl=0,last_cl=0;

    for(u64 sub_lo=LO; sub_lo<HI; sub_lo+=SEG_SPAN){
        u64 sub_hi = sub_lo+SEG_SPAN<HI ? sub_lo+SEG_SPAN : HI;
        u64 seg_base = sub_lo>=MARGIN ? sub_lo-MARGIN : 0;      /* even */
        u64 seg_top  = sub_hi+MARGIN;                            /* even */
        u64 nbits=(seg_top-seg_base)/2, nwords=(nbits+63)/64;
        memset(B,0xff,(nwords+2)*8);
        /* clear tail bits beyond nbits */
        if(nbits&63) B[nwords-1] &= (~0ULL)>>(64-(nbits&63));
        B[nwords]=0; B[nwords+1]=0;
        if(seg_base==0) B[0]&=~1ULL;                             /* 1 not prime */
        /* sieve odds in [seg_base, seg_top) */
        for(u32 bi=0;bi<n_base;bi++){
            u64 q=base_primes[bi];
            if(q*q>=seg_top) break;
            u64 s=q*q;
            if(s<seg_base){ s=((seg_base+q)/ (2*q))*(2*q)+q; if(s<seg_base+1) s+=2*q; }
            /* s = smallest odd multiple of q >= max(q^2, seg_base+1) */
            for(u64 t=(s-seg_base-1)/2; t<nbits; t+=q) B[t>>6]&=~(1ULL<<(t&63));
        }

        /* ---- m-side: covered pass + heavy handling ---- */
        u64 n_marks=0;
        u64 m_start = sub_lo>=MARGIN ? sub_lo-MARGIN : 2;
        u64 t_lo=(m_start-seg_base)/2, t_hi=(sub_hi-seg_base)/2;
        u64 w_lo=t_lo>>6, w_hi=(t_hi+63)>>6;
        for(u64 w=w_lo;w<w_hi;w++){
            u64 c=0; const u64 b0=B[w],b1=B[w+1],b2=B[w+2];
            for(int si=0;si<n_shifts;si++){
                int s=shifts[si];
                if(s<64) c |= (b0>>s)|(b1<<(64-s));
                else     c |= (b1>>(s-64))|(b2<<(128-s));
            }
            u64 h=~c;
            if(w==w_lo && (t_lo&63)) h &= (~0ULL)<<(t_lo&63);
            if(w==w_hi-1 && (t_hi&63)) h &= (~0ULL)>>(64-(t_hi&63));
            while(h){
                int b=__builtin_ctzll(h); h&=h-1;
                u64 t=(w<<6)+b;               /* even m = seg_base + 2t */
                u64 m=seg_base+2*t;
                if(m<2) continue;
                heavy++;
                /* exact k(m), k >= 257 */
                u64 km=0;
                for(u32 i=idx_257;i<n_odd_small;i++){
                    u64 k=odd_primes_small[i], tt=t+(k-1)/2;
                    if(tt>=nbits){ break; }
                    if(B[tt>>6]>>(tt&63)&1){ km=k; break; }
                }
                if(!km){ fprintf(stderr,"FATAL k(m) overflow m=%llu\n",(unsigned long long)m); return 3; }
                if(km>max_km){ max_km=km; arg_km=m; }
                /* mark primes p=m+j, odd composite j in (255,km) */
                for(u64 j=257;j<km;j+=2){
                    if(!comp_small[j]) continue;
                    u64 tt=t+(j-1)/2;
                    if(B[tt>>6]>>(tt&63)&1){
                        u64 p=m+j;
                        if(p>=sub_lo&&p<sub_hi){
                            if(n_marks<(1u<<23)){ marks[n_marks].p=p; marks[n_marks].j=(u32)j; n_marks++; }
                            else { fprintf(stderr,"FATAL marks overflow\n"); return 3; }
                        }
                    }
                }
            }
        }
        qsort(marks,n_marks,sizeof(Mark),cmp_mark);
        n_marks_total+=n_marks;

        /* ---- p-side ---- */
        u64 pt_lo=(sub_lo-seg_base)/2, pt_hi=(sub_hi-seg_base)/2;
        u64 pw_lo=pt_lo>>6, pw_hi=(pt_hi+63)>>6, mi=0;
        for(u64 w=pw_lo;w<pw_hi;w++){
            u64 x=B[w];
            if(w==pw_lo && (pt_lo&63)) x &= (~0ULL)<<(pt_lo&63);
            if(w==pw_hi-1 && (pt_hi&63)) x &= (~0ULL)>>(64-(pt_hi&63));
            while(x){
                int b=__builtin_ctzll(x); x&=x-1;
                u64 t=(w<<6)+b, p=seg_base+2*t+1;
                c_odd++;
                int cluster; u32 wit_j=0;
                if(p<3000){
                    cluster=is_cluster_ref(p);
                    if(!cluster) wit_j=0; /* ref gives no witness; fine for p<3000 */
                    /* still must consult marks pointer to keep it in sync */
                    while(mi<n_marks&&marks[mi].p<p) mi++;
                    if(mi<n_marks&&marks[mi].p==p){ /* consistent */ }
                } else {
                    while(mi<n_marks&&marks[mi].p<p) mi++;
                    if(mi<n_marks&&marks[mi].p==p){ cluster=0; wit_j=marks[mi].j; }
                    else{
                        cluster=1;
                        u64 lo64=get64(B,t-127), hi64=get64(B,t-63);
                        for(int ji=0;ji<n_jtab;ji++){
                            if(((lo64&mask_lo[ji])|(hi64&mask_hi[ji]))==0){
                                cluster=0; wit_j=(u32)jtab[ji]; break;
                            }
                        }
                    }
                }
                if(cluster){
                    c_cl++; if(!min_cl)min_cl=p; if(p>max_cl)max_cl=p;
                    if(!first_cl)first_cl=p; last_cl=p;
                    fnv^=p; fnv*=1099511628211ULL;
                    if(emit) fprintf(stderr,"%llu\n",(unsigned long long)p);
                } else {
                    c_nc++;
                    if(!first_nc){ first_nc=p; first_nc_j=wit_j; }
                }
            }
        }
    }
    double secs=(double)(clock()-t0)/CLOCKS_PER_SEC;
    printf("%llu,%llu,%llu,%llu,%llu,%llu,%llu,%016llx,%llu,%llu,%llu,%llu,%llu,%u,%llu,%llu,%.2f\n",
        (unsigned long long)LO,(unsigned long long)HI,
        (unsigned long long)c_odd,(unsigned long long)c_cl,(unsigned long long)c_nc,
        (unsigned long long)min_cl,(unsigned long long)max_cl,(unsigned long long)fnv,
        (unsigned long long)heavy,(unsigned long long)max_km,(unsigned long long)arg_km,
        (unsigned long long)n_marks_total,
        (unsigned long long)first_nc,first_nc_j,
        (unsigned long long)first_cl,(unsigned long long)last_cl,secs);
    return 0;
}
