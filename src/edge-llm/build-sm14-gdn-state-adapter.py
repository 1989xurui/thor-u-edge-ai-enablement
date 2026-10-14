"""Scope the proven snapshot adapter to one qualified C1 GPU verify candidate."""
import hashlib,json,pathlib,subprocess
P=pathlib.Path('/mnt/d/Thor64G/THOR_NVIDIA_NVFP4_20261013');S=P/'scripts';A=P/'artifacts';W=pathlib.Path('/work/native-v2')
source=(S/'mtp-bounded-state.cpp').read_text()
source=source.replace('// Local TensorRT public-interface adapter. All arithmetic/state kernels remain\n// in the exact loaded NVIDIA plugin. Only unused prefill snapshot extents change.','// Isolated C1/SM110 GDN verify candidate;original serialized shape/alias contract.\n// Original NVIDIA Prefill/ordinary Decode/conv kernels remain delegated.')
source=source.replace('#include <NvInfer.h>','#include <NvInfer.h>\n#include <cuda.h>\n#include <atomic>')
source=source.replace('namespace {','namespace {\nCUfunction candidateFunction=nullptr;\nstd::atomic<unsigned long long> candidateEnqueues{0},delegatedEnqueues{0},candidateErrors{0};',1)
old='  return run()->enqueue(in,out,inputs,outputs,workspace,stream);'
new='''  if(kind==0&&in[11].dims.d[0]==5){
   // C1 only;the untouched native runtime owns acceptance and commits snapshots.
   if(!candidateFunction||in[0].dims.nbDims!=3||in[0].dims.d[1]!=16||in[0].dims.d[2]!=128||
      in[1].dims.nbDims!=3||in[1].dims.d[1]!=16||in[1].dims.d[2]!=128||
      in[2].dims.nbDims!=3||in[2].dims.d[1]!=48||in[2].dims.d[2]!=128||
      in[7].dims.nbDims!=4||in[7].dims.d[1]!=48||in[7].dims.d[2]!=128||in[7].dims.d[3]!=128||
      in[8].dims.nbDims!=1||in[8].dims.d[0]!=1||in[10].dims.nbDims!=1||in[10].dims.d[0]!=1||
      outputs[1]!=inputs[7]||in[7].type!=DataType::kFLOAT||out[2].type!=DataType::kFLOAT||
      in[0].type!=DataType::kHALF||in[1].type!=DataType::kHALF||in[2].type!=DataType::kHALF){
    std::fprintf(stderr,"SM14 GDN candidate:unsupported verify shape/alias/type\\n");candidateErrors++;return -1;
   }
   int T=static_cast<int>(in[0].dims.d[0]),H=16,HV=48,poolRows=static_cast<int>(in[7].dims.d[0]);
   if(T<1||T>8||poolRows<1||in[1].dims.d[0]!=T||in[2].dims.d[0]!=T){candidateErrors++;return -1;}
   void const* q=inputs[0];void const* k=inputs[1];void const* v=inputs[2];void const* a=inputs[3];void const* b=inputs[4];
   void const* alog=inputs[5];void const* dt=inputs[6];void const* resident=inputs[7];void const* indices=inputs[10];
   void* o=outputs[0];void* snapshots=outputs[2];
   void* params[]={&q,&k,&v,&a,&b,&alog,&dt,&resident,&indices,&o,&snapshots,&T,&H,&HV,&poolRows};
   CUresult status=cuLaunchKernel(candidateFunction,192,1,1,256,1,1,0,stream,params,nullptr);
   candidateEnqueues++;if(status!=CUDA_SUCCESS){candidateErrors++;std::fprintf(stderr,"SM14 GDN candidate launch:%d\\n",static_cast<int>(status));return -1;}
   return 0;
  }
  delegatedEnqueues++;
  return run()->enqueue(in,out,inputs,outputs,workspace,stream);'''
assert source.count(old)==1;source=source.replace(old,new)
source+='''
extern "C" bool setThorSm14GdnFunction(void* function){
 int device=-1,major=0,minor=0,sms=0;if(!function||cuCtxGetDevice(&device)!=CUDA_SUCCESS)return false;
 if(cuDeviceGetAttribute(&major,CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR,device)!=CUDA_SUCCESS||
    cuDeviceGetAttribute(&minor,CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR,device)!=CUDA_SUCCESS||
    cuDeviceGetAttribute(&sms,CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT,device)!=CUDA_SUCCESS||major!=11||minor!=0||sms!=14)return false;
 candidateFunction=static_cast<CUfunction>(function);return true;
}
extern "C" void thorSm14GdnAdapterRead(unsigned long long* out){out[0]=candidateEnqueues;out[1]=delegatedEnqueues;out[2]=candidateErrors;}
'''
path=S/'sm14-gdn-state-adapter.cpp';path.write_text(source);out=A/'libthor_sm14_gdn_state.so'
headers=W/'components/libnvinfer-headers-dev/usr/include/aarch64-linux-gnu';cuda=pathlib.Path('/work/a1/cuda-u2/toolkit/include');libs=[W/'qualified-trt-root/lib',pathlib.Path('/work/a1/ram-root/a1/lib')]
argv=['aarch64-linux-gnu-g++-13','-std=c++17','-O2','-Wall','-Wextra','-fPIC','-shared',str(path),'-I'+str(headers),'-I'+str(cuda)]+['-L'+str(v)for v in libs]+['-Wl,-rpath-link,'+':'.join(map(str,libs)),'-Wl,-z,defs','-l:libnvinfer.so.10','-lcudart','-lcuda','-o',str(out)]
done=subprocess.run(argv,capture_output=True,text=True);(P/'evidence/sm14-gdn-state-adapter-build.log').write_text(done.stdout+done.stderr);assert done.returncode==0,done.stderr
receipt=dict(status='C1_VERIFY_ADAPTER_COMPILED_NOT_QUALIFIED',library_bytes=out.stat().st_size,library_sha256=hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),source_sha256=hashlib.file_digest(path.open('rb'),'sha256').hexdigest(),implementation='Existing shape/alias/serialization contract preserved;only phase5 GDN uses qualified candidate;conv/Prefill/ordinary Decode delegated',base_engine_rebuild=False,original_plugin_binary_changed=False)
(P/'evidence/sm14-gdn-state-adapter-package.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
