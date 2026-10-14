"""Small ARM C++ TensorRT V3 boundary; no device/kernel/source rebuild."""
import hashlib,json,pathlib,subprocess
P=pathlib.Path('/mnt/d/Thor64G/THOR_NVIDIA_NVFP4_20261013');W=pathlib.Path('/work/native-v2')
source=P/'scripts/fp4-boundary-plugin.cpp';output=P/'artifacts/libthor_fp4_boundary.so'
headers=W/'components/libnvinfer-headers-dev/usr/include/aarch64-linux-gnu'
cuda=pathlib.Path('/work/a1/cuda-u2/toolkit/include')
libs=[W/'qualified-trt-root/lib',pathlib.Path('/work/a1/ram-root/a1/lib')]
command=['aarch64-linux-gnu-g++-13','-std=c++17','-O2','-Wall','-Wextra','-fPIC','-shared',str(source),'-I'+str(headers),'-I'+str(cuda)]+['-L'+str(p)for p in libs]+['-Wl,-rpath-link,'+':'.join(map(str,libs)),'-Wl,-z,defs','-l:libnvinfer.so.10','-lcudart','-o',str(output)]
r=subprocess.run(command,text=True,capture_output=True)
(P/'evidence/fp4-boundary-build.log').write_text(r.stdout+r.stderr,encoding='utf-8')
assert r.returncode==0,r.stderr[-3000:]
inspect=subprocess.run(['aarch64-linux-gnu-readelf','-d',str(output)],capture_output=True,text=True,check=True).stdout
receipt=dict(status='PASS_HOST_ARM_SHARED_LIBRARY_BUILD_ONLY',source_sha256=hashlib.file_digest(source.open('rb'),'sha256').hexdigest(),library_sha256=hashlib.file_digest(output.open('rb'),'sha256').hexdigest(),library_bytes=output.stat().st_size,compiler='aarch64-linux-gnu-g++-13',implementation='FP16 bitwise CUDA device-to-device copy only; original Q/DQ and weights unchanged',dynamic_section=inspect)
(P/'evidence/fp4-boundary-package.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8');print(json.dumps(receipt))
