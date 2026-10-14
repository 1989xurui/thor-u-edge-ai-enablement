extern "C" __global__ void a1_add(unsigned* data, unsigned n) {
 unsigned i=blockIdx.x*blockDim.x+threadIdx.x;
 if(i<n)data[i]+=17;
}
