import pathlib, subprocess, hashlib, json, re, gzip
P=pathlib.Path('/mnt/d/Thor64G/THOR_U_A1_NVGPU_R39_20261013')
W=pathlib.Path('/work/a1')
S=W/'stage'
def digest(p): return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(args): return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True).stdout
index=gzip.decompress((P/'inputs/Packages-som-r39.2.gz').read_bytes()).decode()
stanzas=[dict(line.split(': ',1) for line in part.splitlines() if ': ' in line and not line.startswith(' ')) for part in index.split('\n\n')]
packages=[]
for p in sorted((P/'inputs/debs').glob('*.deb')):
    matches=[s for s in stanzas if s.get('Filename','').endswith('/'+p.name)]
    expected=matches[0].get('SHA256') if matches else None
    sha=digest(p)
    packages.append(dict(file=p.name,sha256=sha,official_sha256=expected,match=sha==expected,control=run(['dpkg-deb','-f',str(p)])))
libs=[p for p in S.rglob('*') if p.is_file() and re.match(r'lib(cuda|nvrm_).*\.so',p.name)]
elf=[]
for p in libs:
    dyn=run(['readelf','-d',str(p)])
    needed=re.findall(r'Shared library: \[(.*?)\]',dyn)
    elf.append(dict(path=str(p),sha256=digest(p),needed=needed,dependency_files={n:[str(q) for q in libs if q.name==n] for n in needed if n.startswith('libnvrm_')}))
fw=[]
for p in S.rglob('*'):
    if p.is_file() and '/firmware/' in str(p) and ('/gb10b/' in str(p) or '/ga10b/' in str(p)):
        fw.append(dict(path=str(p),name=p.name,size=p.stat().st_size,sha256=digest(p)))
ref=next(S.glob('nvidia-l4t-kernel-nvgpu*/lib/modules/*/updates/nvgpu.ko'))
mod=dict(path=str(ref),sha256=digest(ref),modinfo=run(['modinfo',str(ref)]),symbols=run(['nm',str(ref)]))
(P/'logs/static-contract.json').write_text(json.dumps(dict(packages=packages,elf=elf,firmware=fw,reference_module=mod),indent=2))
print(json.dumps(dict(package_count=len(packages),all_package_sha_match=all(p['match'] for p in packages),gb10b_files=sum('/gb10b/' in p['path'] for p in fw),library_files=len(elf),reference_2b00='d00002B00' in mod['modinfo'])))
