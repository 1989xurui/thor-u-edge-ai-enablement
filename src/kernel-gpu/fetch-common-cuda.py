import pathlib,json,urllib.request,hashlib,subprocess,shutil,re
P=pathlib.Path('/mnt/d/Thor64G/THOR_U_A1_NVGPU_R39_20261013');W=pathlib.Path('/work/a1')
text=(P/'inputs/Packages-som-r39.2.txt').read_text()
block=next(b for b in text.split('\n\n') if b.startswith('Package: nvidia-l4t-cuda\n') and '\nVersion: 39.2.1-20260806224157\n' in b)
m=dict(l.split(': ',1) for l in block.splitlines() if ': ' in l and not l.startswith(' '))
url='https://repo.download.nvidia.com/jetson/som/'+m['Filename'];dest=P/'inputs/debs'/pathlib.Path(m['Filename']).name
if not dest.exists():urllib.request.urlretrieve(url,dest)
sha=hashlib.file_digest(dest.open('rb'),'sha256').hexdigest();assert sha==m['SHA256']
stage=W/'stage'/dest.stem;subprocess.run(['dpkg-deb','-x',str(dest),str(stage)],check=True)
files=list(stage.rglob('libnvcucompat.so*'));assert files
for f in files:
 if f.is_file() and not f.is_symlink():shutil.copy2(f,P/'artifacts'/f.name);print(subprocess.check_output(['readelf','-d',str(f)],text=True))
(P/'logs/cuda-common-package-verification.json').write_text(json.dumps(dict(url=url,sha256=sha,official_sha_match=True,files=[str(f) for f in files]),indent=2))
print(json.dumps(dict(package=m['Package'],size=dest.stat().st_size,sha_match=True)))
