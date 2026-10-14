import pathlib,subprocess,shutil,json,hashlib,tarfile
P=pathlib.Path('/mnt/d/Thor64G/THOR_NVIDIA_NVFP4_20261013');W=pathlib.Path('/work/native-v2');R=W/'ops-root';(R/'lib').mkdir(parents=True,exist_ok=True)
roots=[W/'components'/n for n in ['libcublas','cuda_nvrtc','libnvjitlink']];incs=[]
for root in roots:
 incs.extend(root.glob('*/include'))
 for f in root.glob('*/lib/*.so*'):
  target=R/'lib'/f.name
  if f.is_symlink():
   if target.is_symlink():target.unlink()
   target.symlink_to(f.readlink())
  else:shutil.copy2(f,target)
nvroot=pathlib.Path('/work/a1/cuda-u2/toolkit');libs=[str(R/'lib'),'/work/a1/ram-root/a1/lib']
args=['aarch64-linux-gnu-g++-13','-std=c++17','-O2','-Wall',str(P/'scripts/native-ops.cpp'),'-I'+str(nvroot/'include')]+['-I'+str(x)for x in incs]+['-L'+x for x in libs]+['-Wl,-rpath-link,'+':'.join(libs),'-lcudart','-lcuda','-lcublasLt','-lnvrtc','-lnvJitLink','-ldl','-lpthread','-o',str(R/'native-ops')]
r=subprocess.run(args,capture_output=True,text=True);(P/'evidence/native-ops-build.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr[-2000:]
manifest={str(f.relative_to(R)):hashlib.file_digest(f.open('rb'),'sha256').hexdigest()for f in R.rglob('*')if f.is_file()and not f.is_symlink()};(R/'SHA256SUMS').write_text(''.join(v+'  '+k+'\n'for k,v in manifest.items()))
subprocess.run(['tar','cf',str(P/'artifacts/native-ops.tar'),'.'],cwd=R,check=True)
record=dict(build_exit=r.returncode,files=manifest,archive_bytes=(P/'artifacts/native-ops.tar').stat().st_size,archive_sha256=hashlib.file_digest((P/'artifacts/native-ops.tar').open('rb'),'sha256').hexdigest(),libraries_origin='official CUDA13.2 Update2 redist; cuBLAS13.4.1.3 independently versioned')
(P/'evidence/native-ops-package.json').write_text(json.dumps(record,indent=2));print(json.dumps(dict(build_exit=0,archive_bytes=record['archive_bytes'],archive_sha256=record['archive_sha256'])))
