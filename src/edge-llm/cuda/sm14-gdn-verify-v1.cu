// C1 SM110 candidate. Read resident state once; preserve every verify snapshot.
// One CTA per (V head,32-column tile); state columns are mathematically independent.
__device__ __forceinline__ float fp16(unsigned short x){float r;asm("cvt.f32.f16 %0, %1;":"=f"(r):"h"(x));return r;}
__device__ __forceinline__ unsigned short half_rn(float x){unsigned short r;asm("cvt.rn.f16.f32 %0, %1;":"=h"(r):"f"(x));return r;}
__device__ __forceinline__ float exponential(float x){float r;float y=x*1.4426950408889634f;asm("ex2.approx.ftz.f32 %0, %1;":"=f"(r):"f"(y));return r;}
__device__ __forceinline__ float logarithm(float x){float r;asm("lg2.approx.ftz.f32 %0, %1;":"=f"(r):"f"(x));return r*0.6931471805599453f;}
__device__ __forceinline__ float inverse_sqrt(float x){float r;asm("rsqrt.approx.ftz.f32 %0, %1;":"=f"(r):"f"(x));return r;}
extern "C" __global__ void thor_sm14_gdn_verify_v1(
 const unsigned short* q,const unsigned short* k,const unsigned short* v,
 const unsigned short* a,const unsigned short* b,const float* alog,
 const unsigned short* dt,const float* resident,const int* state_indices,
 unsigned short* output,float* snapshots,int T,int H,int HV,int poolRows){
 const int tid=threadIdx.x,lane=tid%32,warp=tid/32;
 const int head=blockIdx.x/4,vtile=blockIdx.x%4,kh=head/(HV/H);
 const int k_local=lane/4,v_local=lane%4,col=vtile*32+warp*4+v_local;
 const int slot=state_indices[0];
 if(T<1||T>8||H!=16||HV!=48||poolRows<1||slot<0||slot>=poolRows)return;
 __shared__ float Q[8][128],K[8][128],G[8],B[8],norm[16];
 float state[16];
 #pragma unroll
 for(int i=0;i<16;i++)state[i]=resident[((slot*HV+head)*128+(i*8+k_local))*128+col];
 // Match the native kernel's eight-warp butterfly norm reduction and scale order.
 for(int t=0;t<T;t++){
  float sq=0,sk=0;
  if(tid<128){float x=fp16(q[(t*H+kh)*128+tid]),y=fp16(k[(t*H+kh)*128+tid]);Q[t][tid]=x;K[t][tid]=y;sq=x*x;sk=y*y;}
  #pragma unroll
  for(int offset=16;offset>=1;offset/=2){sq+=__shfl_xor_sync(0xffffffff,sq,offset);sk+=__shfl_xor_sync(0xffffffff,sk,offset);}
  if(lane==0){norm[warp]=sq;norm[warp+8]=sk;}
  if(tid==0){float x=fp16(a[t*HV+head])+fp16(dt[head]);float soft=x>20?x:logarithm(1+exponential(x));G[t]=exponential(-exponential(alog[head])*soft);B[t]=1/(1+exponential(-fp16(b[t*HV+head])));}
  __syncthreads();
  if(warp==0){sq=lane<8?norm[lane]:0;sk=lane<8?norm[lane+8]:0;
   #pragma unroll
   for(int offset=4;offset>=1;offset/=2){sq+=__shfl_xor_sync(0xffffffff,sq,offset);sk+=__shfl_xor_sync(0xffffffff,sk,offset);}
   if(lane==0){norm[0]=inverse_sqrt(sq+1e-6f);norm[1]=inverse_sqrt(sk+1e-6f);}
  }
  __syncthreads();
  if(tid<128){Q[t][tid]=Q[t][tid]*0.08838834764831845f*norm[0];K[t][tid]*=norm[1];}
  __syncthreads();
 }
 for(int t=0;t<T;t++){
  float hk=0;
  #pragma unroll
  for(int i=0;i<16;i++){state[i]*=G[t];hk+=state[i]*K[t][i*8+k_local];}
  #pragma unroll
  for(int offset=16;offset>=4;offset/=2)hk+=__shfl_xor_sync(0xffffffff,hk,offset);
  float correction=(fp16(v[(t*HV+head)*128+col])-hk)*B[t];correction=__shfl_sync(0xffffffff,correction,v_local);
  float hq=0;
  #pragma unroll
  for(int i=0;i<16;i++){
   int row=i*8+k_local;state[i]+=K[t][row]*correction;hq+=state[i]*Q[t][row];
   snapshots[((t*HV+head)*128+row)*128+col]=state[i];
  }
  #pragma unroll
  for(int offset=16;offset>=4;offset/=2)hq+=__shfl_xor_sync(0xffffffff,hq,offset);
  if(k_local==0)output[(t*HV+head)*128+col]=half_rn(hq);
 }
 // Resident input stays read-only; the native runtime commits accepted snapshots.
}
