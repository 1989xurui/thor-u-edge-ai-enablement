import pathlib, subprocess, re, json, hashlib
P=pathlib.Path('/mnt/d/Thor64G/THOR_U_A1_NVGPU_R39_20261013')
S=pathlib.Path('/work/a1/stage')
index={}
for p in S.rglob('*'):
    if p.is_file() and '.so' in p.name:
        index.setdefault(p.name,[]).append(p)
start=next(S.glob('nvidia-l4t-cuda-nvgpu*/opt/nvidia/l4t-gpu-libs/nvgpu/libcuda.so.1.1'))
queue=[start]; seen=set(); result=[]
while queue:
    p=queue.pop(0).resolve()
    if str(p) in seen: continue
    seen.add(str(p))
    dynamic=subprocess.check_output(['readelf','-d',str(p)],text=True)
    versions=subprocess.check_output(['readelf','-V',str(p)],text=True)
    header=subprocess.check_output(['readelf','-h',str(p)],text=True)
    needed=re.findall(r'Shared library: \[(.*?)\]',dynamic)
    deps={n:[str(x) for x in index.get(n,[])] for n in needed}
    result.append(dict(path=str(p),sha256=hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),aarch64='AArch64' in header,needed=deps,glibc_requirements=sorted(set(re.findall(r'Name: (GLIBC_[\d.]+)',versions)))))
    for n in needed:
        if n in index: queue.append(index[n][0])
out=dict(native_compute='NOT_RUN',ioctl_runtime_abi='UNKNOWN',nodes=result,external_sonames=sorted({n for r in result for n,paths in r['needed'].items() if not paths}))
(P/'logs/userspace-abi-closure.json').write_text(json.dumps(out,indent=2))
print(json.dumps(dict(closure_nodes=len(result),external_sonames=out['external_sonames'],all_aarch64=all(r['aarch64'] for r in result))))
