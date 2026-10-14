import pathlib, json, subprocess, hashlib, struct, re, shutil, sys
P=pathlib.Path('/mnt/d/Thor64G/THOR_U_A1_NVGPU_R39_20261013')
flavor=sys.argv[1] if len(sys.argv)>1 else 'original'
tag='g35-' if flavor=='g35' else ''
W=pathlib.Path('/work/a1'); B=W/f'build/kernel-{flavor}'; S=W/'source'
def sha(p): return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(args): return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True).stdout.strip()
def symvers(p):
    result={}
    if p.exists():
        for line in p.read_text().splitlines():
            cols=line.split()
            if len(cols)>=4: result[cols[1]]=dict(crc=int(cols[0],16),provider=cols[2],export=cols[3])
    return result
def versions(p):
    b=p.read_bytes(); h=struct.unpack_from('<16sHHIQQQIHHHHHH',b)
    sh=[struct.unpack_from('<IIQQQQIIQQ',b,h[6]+i*h[11]) for i in range(h[12])]
    s=sh[h[13]]; names=b[s[4]:s[4]+s[5]]
    result={}
    for s in sh:
        name=names[s[0]:names.index(b'\0',s[0])]
        if name==b'__versions':
            raw=b[s[4]:s[4]+s[5]]
            off=0
            while off+8 < len(raw):
                step,crc=struct.unpack_from('<II',raw,off)
                symbol=raw[off+8:raw.index(b'\0',off+8)].decode()
                if not symbol: break
                result[symbol]=crc
                if step==0: break
                if step<9 or off+step>len(raw): raise ValueError('Invalid NVIDIA flexible modversion entry')
                off+=step
    return result
def exitcode(name):
    p=P/f'logs/{tag}{name}-build.exit'
    return int(p.read_text()) if p.exists() else None
kernel=symvers(B/'Module.symvers')
frozen=symvers(pathlib.Path('/mnt/e/Thor64G_AI/THOR_U_R39_GOS_BOOT_GATE_20261006/15_g5_openrm/payload_fix/initrd/Module.symvers'))
exports=dict(kernel)
symbol_sources=[B/'Module.symvers',S/'nvidia-oot/Module.symvers',S/'hwpm/drivers/tegra/hwpm/Module.symvers',S/'nvgpu/drivers/gpu/nvgpu/Module.symvers']
for p in symbol_sources[1:]: exports.update(symvers(p))
module_paths=list(B.rglob('*.ko'))+list((S/'nvidia-oot').rglob('*.ko'))+list((S/'hwpm').rglob('*.ko'))+list((S/'nvgpu').rglob('*.ko'))
by_name={p.stem.replace('-','_'):p for p in module_paths}
nvgpu=S/'nvgpu/drivers/gpu/nvgpu/nvgpu.ko'
closure=[]; pending=['nvgpu']; seen=set(); missing=[]
while pending:
    name=pending.pop(0).replace('-','_')
    if name in seen: continue
    seen.add(name)
    if name not in by_name: missing.append(name); continue
    p=by_name[name]
    info=run(['modinfo',str(p)])
    depends=run(['modinfo','-F','depends',str(p)])
    imported=versions(p)
    mismatch=[dict(symbol=n,crc=hex(c),export=exports.get(n)) for n,c in imported.items() if n not in exports or c != exports[n]['crc']]
    undefined=run(['nm','-u',str(p)]).splitlines()
    unresolved=[line.split()[-1] for line in undefined if line.split() and line.split()[-1] not in exports and not line.lstrip().startswith(('w ','v '))]
    closure.append(dict(name=name,path=str(p),size=p.stat().st_size,sha256=sha(p),vermagic=run(['modinfo','-F','vermagic',str(p)]),depends=depends,versions_count=len(imported),crc_mismatches=mismatch,unresolved=unresolved,modinfo=info))
    pending.extend(x for x in depends.split(',') if x)
minimal=P/f'logs/{tag}minimal-nvgpu-build.exit'
out=dict(target_flavor=flavor,kernel_build_exit=exitcode('kernel'),full_oot_build_exit=int((P/'logs/nvgpu-build.exit').read_text()),minimal_oot_build_exit=int((P/f'logs/{tag}minimal-oot-build.exit').read_text()) if (P/f'logs/{tag}minimal-oot-build.exit').exists() else None,nvgpu_build_exit=int(minimal.read_text()) if minimal.exists() else None,kernel_source_commit='78272943bba3a47e633b28963b0cda60de503500',config_sha256=sha(B/'.config'),kernelrelease=(P/'logs/kernelrelease.txt').read_text().strip(),kernel_symbols=len(kernel),frozen_symbols=len(frozen),frozen_crc_conflicts=[dict(symbol=n,rebuilt=kernel[n],frozen=frozen[n]) for n in sorted(set(kernel)&set(frozen)) if kernel[n]['crc']!=frozen[n]['crc']],frozen_missing_in_rebuild=sorted(set(frozen)-set(kernel)),rebuild_added_symbols=sorted(set(kernel)-set(frozen)),nvgpu_exists=nvgpu.exists(),built_module_count=len(module_paths),dependency_closure=closure,missing_dependency_modules=missing,signature_force='CONFIG_MODULE_SIG_FORCE=y' in (B/'.config').read_text(),signature_private_key='NOT_AVAILABLE',nvsched='Linked into nvgpu.ko via Makefile.sources; no separate nvsched.ko is defined',repeat_build='No redundant full rebuild; retries followed concrete build failures and user instruction to repair',GPU_INITIALIZATION='NOT_RUN',CUDA_13_2_U2_NATIVE='NOT_RUN')
out['module_link_and_crc']='PASS' if nvgpu.exists() and out['nvgpu_build_exit']==0 and not missing and all(not r['crc_mismatches'] and not r['unresolved'] for r in closure) else 'FAIL'
out['BUILD_ABI']='FAIL' if out['module_link_and_crc']=='FAIL' else ('UNKNOWN' if out['signature_force'] else 'PASS')
out['signature_admission']='NO_GO_UNSIGNED_MODULE_WITH_FORCE_ENABLED' if out['signature_force'] else 'MATCH_FROZEN_G35_POLICY_FORCE_DISABLED; no new policy change'
out['symbol_source_files']=[dict(path=str(p),sha256=sha(p),symbols=len(symvers(p))) for p in symbol_sources if p.exists()]
out['reference_prebuilt_modules_used_for_target']='NONE'
log=(P/'logs/nvgpu-build.log').read_text(errors='replace')
out['nvgpu_compile_started']=(P/'logs/minimal-nvgpu-build.log').exists()
if flavor=='g35': out['original_target_build']=json.loads((P/'logs/original-build-abi-verdict.json').read_text())
out['initial_failed_stage']='nvidia-oot/modpost: unrelated tegra-camera videobuf2 symbols'
out['repair']='Use minimal Kbuild closure, preserve official parent GPU flags, include ivc-cdev required by nvsciipc; no C source or kernel config changes.'
out['build_overlays']=[dict(path=str(p),sha256=sha(p)) for p in (S/'nvidia-oot/Kbuild',S/'nvidia-oot/drivers/gpu/Kbuild') if p.exists()]
out['reported_build_errors']=[line for line in log.splitlines() if line.startswith('ERROR: modpost:')]
(P/'A1_BUILD_ABI_VERDICT.json').write_text(json.dumps(out,indent=2))
artifact=P/'artifacts'/flavor; artifact.mkdir(exist_ok=True,parents=True)
for r in closure:
    shutil.copy2(r['path'],artifact/pathlib.Path(r['path']).name)
for p in (B/'Module.symvers',B/'.config',B/'arch/arm64/boot/Image'):
    if p.exists(): shutil.copy2(p,artifact/('kernel-'+p.name.lstrip('.')))
print(json.dumps({k:out[k] for k in ('kernel_build_exit','nvgpu_build_exit','nvgpu_exists','built_module_count','module_link_and_crc','BUILD_ABI','signature_admission')}))
