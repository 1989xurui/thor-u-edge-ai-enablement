"""CPU only: current device, protected defaults, existing diagnostic Runtime and original plugin."""
import hashlib,json,os,pathlib,shutil,struct,time
R=pathlib.Path('/zeekr_data/nvidia-native-ai-v2');out=R/'V24-layer-profiler-v1-cpu-admission.json';assert not out.exists()
boot=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip();assert boot=='9d74daba-0347-489c-9192-2d117806cbe7'
owners=[]
for proc in pathlib.Path('/proc').glob('[0-9]*'):
    try:
        for fd in(proc/'fd').iterdir():
            try:
                path=os.readlink(fd)
                if path.startswith(('/dev/nvidia','/dev/nvhost','/dev/nvgpu','/dev/dri')):owners.append(dict(pid=proc.name,path=path))
            except OSError:pass
    except OSError:pass
assert not owners,owners
entries=[]
for folder,expected in [('dynamic-kv-v1','bb83eafdc835bf03e27970cdaa082b53773230560f7fa9711818d10c665cae2e'),
    ('quality-observer-v1','58bd3b864e5658558315a7d0e50700f579f70ebf787de39019284f4c7d818033')]:
    repair=R/'runtime/repairs'/folder;manifest=json.loads((repair/'variants.json').read_text());row=manifest['variants'][0]
    binary=repair/row['extension'];data=binary.read_bytes();sha=hashlib.sha256(data).hexdigest()
    assert sha==expected and data[:4]==b'\x7fELF'and struct.unpack_from('<H',data,18)[0]==183
    plugin=repair/row['plugin']
    with plugin.open('rb')as f:plugin_sha=hashlib.file_digest(f,'sha256').hexdigest()
    assert plugin_sha=='8fb2fb35b60b097c3a3f30c54fdb45d65c30469147c49ac61bb76468fa650c63'
    enabled=b'THOR_PREFILL_LAYER_TRACE'in data
    if folder=='quality-observer-v1':assert enabled
    entries.append(dict(folder=folder,extension=str(binary),extension_SHA=sha,bytes=len(data),ELF='AArch64',
        public_layer_profiler_present=enabled,plugin_path=str(plugin),plugin_SHA=plugin_sha,plugin_inode=plugin.stat().st_ino,plugin_device=plugin.stat().st_dev))
selected=R/'runtime/config/native-mtp8k-selected-runtime.json';sha=hashlib.sha256(selected.read_bytes()).hexdigest()
assert sha=='dac9a3d306e14c40e51f24c93f44333f32e2ac93e905dbdc5c8630415890ce36'
mounts=[line for line in pathlib.Path('/proc/mounts').read_text().splitlines()if' /new_root 'in line];assert all(' ro,'in line for line in mounts)
memory={line.split(':')[0]:int(line.split()[1])*1024 for line in pathlib.Path('/proc/meminfo').read_text().splitlines()}
result=dict(status='PASS_CPU_ONLY_CURRENT_DEVICE_AND_EXISTING_PUBLIC_LAYER_PROFILER_ASSETS',boot_id=boot,kernel=os.uname().release,
    GPU_FD_owners=owners,Runtime_assets=entries,MemAvailable_bytes=memory['MemAvailable'],DATA_free_bytes=shutil.disk_usage(R).free,
    MAP_free_bytes=shutil.disk_usage('/zeekr_map').free,new_root_mounts=mounts,production_default_SHA=sha,production_default_changed=False,
    Golden_changed=False,source_matches_full_wheel=False,diagnostic_Runtime_only=True,production_health='UNPROVEN;preexisting exclusive RAMmaintenance',
    global_CUDA_interposer='V2_AND_V3_NO_GO_NOT_LOADED',device_monotonic_s=time.monotonic(),device_checked=True,result_checked=True)
out.write_text(json.dumps(result,indent=2));(pathlib.Path('/v2/export')/out.name).symlink_to(out);print(json.dumps(result),flush=True)
