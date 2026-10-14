import pathlib, struct, json, hashlib, re
root = pathlib.Path(r'D:\Thor64G\THOR_U_A1_NVGPU_R39_20261013')
stage = pathlib.Path(r'\\wsl.localhost\Thor-A1-R39-20261013\work\a1\stage')
results=[]
def audit(p):
    b=p.read_bytes()
    if b[:6] != b'\x7fELF\x02\x01': return
    h=struct.unpack_from('<16sHHIQQQIHHHHHH', b)
    shoff,shsize,shnum,shstrndx=h[6],h[11],h[12],h[13]
    sh=[struct.unpack_from('<IIQQQQIIQQ',b,shoff+i*shsize) for i in range(shnum)]
    strh=sh[shstrndx]; names=b[strh[4]:strh[4]+strh[5]]
    def z(s,o): return s[o:s.index(b'\0',o)].decode(errors='replace')
    secs={z(names,s[0]):(s,b[s[4]:s[4]+s[5]]) for s in sh}
    r=dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),size=len(b),machine=h[2])
    if '.modinfo' in secs:
        vals=secs['.modinfo'][1].split(b'\0')
        r['modinfo']=[x.decode(errors='replace') for x in vals if x.startswith((b'vermagic=',b'depends=',b'alias=',b'signer=',b'sig_key='))]
        r['signature_trailer']=b.endswith(b'~Module signature appended~\n')
    if '.dynamic' in secs:
        s,raw=secs['.dynamic']; strings=sh[s[6]]; strings=b[strings[4]:strings[4]+strings[5]]
        r['needed']=[z(strings,v) for tag,v in struct.iter_unpack('<QQ',raw) if tag==1]
    syms=secs.get('.symtab',secs.get('.dynsym'))
    if syms:
        s,raw=syms; strings=sh[s[6]]; strings=b[strings[4]:strings[4]+strings[5]]
        r['pci_tables']=[]
        r['cuda_exports']=[]
        for off in range(0,len(raw),s[9]):
            name,info,other,idx,value,size=struct.unpack_from('<IBBHQQ',raw,off)
            name=z(strings,name)
            if re.search(r'pci.*(ids|table)',name,re.I) and idx < len(sh) and size:
                sec=sh[idx]; data=b[sec[4]+value:sec[4]+value+size]
                stride=40 if size%40==0 else 32
                r['pci_tables'].append(dict(symbol=name,size=size,stride=stride,entries=[list(struct.unpack_from('<6IQ',data,i)) for i in range(0,len(data)-stride+1,stride)]))
            if name in ('cuInit','cuDriverGetVersion','cuCtxCreate','cuCtxCreate_v2','cuCtxCreate_v3','cuGetProcAddress','cuGetProcAddress_v2'):
                r['cuda_exports'].append(name)
    if 'libcuda' in p.name:
        r['driver_versions']=sorted({v.decode() for v in re.findall(rb'Version [0-9]{3}\.[0-9.]+',b)})
        r['nvgpu_strings']=sorted({v.decode(errors='replace') for v in re.findall(rb'/dev/[^\x00\s]{1,120}',b) if b'gpu' in v or b'nvhost' in v})[:30]
    return r
for p in stage.rglob('*'):
    if p.is_file() and (p.name in ('nvgpu.ko','host1x-fence.ko','mc-utils.ko','nvmap.ko','libcuda.so.1.1')):
        results.append(audit(p))
(root/'logs/reference-elf.json').write_text(json.dumps(results,indent=2))
for r in results:
    print(pathlib.Path(r['path']).name, json.dumps({k:v for k,v in r.items() if k in ('modinfo','pci_tables','driver_versions','needed','cuda_exports')}))
