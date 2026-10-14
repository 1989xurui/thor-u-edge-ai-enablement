#include <cuda.h>
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <stdint.h>
#include <string.h>
#define CHECK(x) do { CUresult e=(x); if(e!=CUDA_SUCCESS){printf("FAIL %s code=%d\n",#x,e);return 10;} } while(0)
#define LOAD(name,type) type name=(type)dlsym(h,#name); if(!name){printf("FAIL missing %s\n",#name);return 11;}
typedef CUresult (*Finit)(unsigned);typedef CUresult(*Fver)(int*);typedef CUresult(*Fget)(CUdevice*,int);
typedef CUresult(*Fname)(char*,int,CUdevice);typedef CUresult(*Fattr)(int*,CUdevice_attribute,CUdevice);
typedef CUresult(*Fctx)(CUcontext*,unsigned,CUdevice);typedef CUresult(*Fdestroy)(CUcontext);
typedef CUresult(*Falloc)(CUdeviceptr*,size_t);typedef CUresult(*Ffree)(CUdeviceptr);
typedef CUresult(*Fcopyin)(CUdeviceptr,const void*,size_t);typedef CUresult(*Fcopyout)(void*,CUdeviceptr,size_t);
typedef CUresult(*Fmod)(CUmodule*,const char*);typedef CUresult(*Ffunc)(CUfunction*,CUmodule,const char*);
typedef CUresult(*Flaunch)(CUfunction,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned,CUstream,void**,void**);
typedef CUresult(*Fsync)(void);typedef CUresult(*Funload)(CUmodule);
int main(int argc,char**argv){
 setvbuf(stdout,NULL,_IONBF,0); if(argc!=2)return 2;
 void*h=dlopen("/a1/lib/libcuda.so.1",RTLD_NOW|RTLD_LOCAL);if(!h){printf("FAIL driver load %s\n",dlerror());return 3;}
 LOAD(cuInit,Finit);LOAD(cuDriverGetVersion,Fver);LOAD(cuDeviceGetCount,Fver);LOAD(cuDeviceGet,Fget);LOAD(cuDeviceGetName,Fname);LOAD(cuDeviceGetAttribute,Fattr);
 LOAD(cuCtxCreate_v2,Fctx);LOAD(cuCtxDestroy_v2,Fdestroy);LOAD(cuMemAlloc_v2,Falloc);LOAD(cuMemFree_v2,Ffree);
 LOAD(cuMemcpyHtoD_v2,Fcopyin);LOAD(cuMemcpyDtoH_v2,Fcopyout);LOAD(cuModuleLoad,Fmod);LOAD(cuModuleGetFunction,Ffunc);LOAD(cuLaunchKernel,Flaunch);LOAD(cuCtxSynchronize,Fsync);LOAD(cuModuleUnload,Funload);
 int v=0,count=0;CHECK(cuDriverGetVersion(&v));printf("DRIVER_VERSION=%d\n",v);if(v<13020)return 4;
 void*rt=dlopen("/a1/lib/libcudart.so.13",RTLD_NOW|RTLD_LOCAL);if(!rt){printf("FAIL runtime load %s\n",dlerror());return 5;}
 int(*rtver)(int*)=dlsym(rt,"cudaRuntimeGetVersion");int(*rtcount)(int*)=dlsym(rt,"cudaGetDeviceCount");int rv=0;
 if(!rtver||!rtcount||rtver(&rv)||rv<13020){printf("FAIL runtime version %d\n",rv);return 6;}printf("RUNTIME_VERSION=%d\n",rv);
 CHECK(cuInit(0));CHECK(cuDeviceGetCount(&count));printf("DRIVER_DEVICES=%d\n",count);if(count!=1)return 7;
 int rc=rtcount(&count);printf("RUNTIME_DEVICE_COUNT rc=%d count=%d\n",rc,count);if(rc||count!=1)return 8;
 CUdevice d;CHECK(cuDeviceGet(&d,0));char name[256];CHECK(cuDeviceGetName(name,sizeof(name),d));int major,minor;
 CHECK(cuDeviceGetAttribute(&major,CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR,d));CHECK(cuDeviceGetAttribute(&minor,CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR,d));
 printf("DEVICE=%s SM=%d%d\n",name,major,minor);if(major!=11||minor!=0)return 9;
 CUcontext ctx;CHECK(cuCtxCreate_v2(&ctx,0,d));CUdeviceptr ptr;const unsigned n=65536;size_t bytes=n*sizeof(unsigned);unsigned*host=malloc(bytes);if(!host)return 12;
 for(unsigned i=0;i<n;i++)host[i]=i;
 CHECK(cuMemAlloc_v2(&ptr,bytes));CHECK(cuMemcpyHtoD_v2(ptr,host,bytes));CUmodule mod;CUfunction f;
 CHECK(cuModuleLoad(&mod,argv[1]));CHECK(cuModuleGetFunction(&f,mod,"a1_add"));void*params[]={&ptr,(void*)&n};
 CHECK(cuLaunchKernel(f,(n+255)/256,1,1,256,1,1,0,0,params,0));CHECK(cuCtxSynchronize());CHECK(cuMemcpyDtoH_v2(host,ptr,bytes));
 for(unsigned i=0;i<n;i++)if(host[i]!=i+17){printf("FAIL numeric %u actual=%u\n",i,host[i]);return 13;}
 CHECK(cuModuleUnload(mod));CHECK(cuMemFree_v2(ptr));CHECK(cuCtxDestroy_v2(ctx));free(host);
 FILE*maps=fopen("/proc/self/maps","r");char line[1024];if(maps){while(fgets(line,sizeof(line),maps))if(strstr(line,"/a1/lib/"))fputs(line,stdout);fclose(maps);}
 puts("A1_NATIVE_CUDA_U2_COMPUTE_PASS");return 0;
}
