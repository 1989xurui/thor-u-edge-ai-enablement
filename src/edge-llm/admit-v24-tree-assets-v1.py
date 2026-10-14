"""Current read-only admission for original qualified Tree assets; no model load or production-default writes."""
import hashlib,json,os,pathlib,shutil
R=pathlib.Path('/zeekr_data/nvidia-native-ai-v2');out=R/'V24-tree-assets-v1-admission.json';assert not out.exists()
selection=json.loads(pathlib.Path('/v2/V24-tree-mainline-selection.json').read_text());repair=pathlib.Path(selection['qualified_Runtime'])
boot=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip();assert boot=='9d74daba-0347-489c-9192-2d117806cbe7'
owners=[]
for proc in pathlib.Path('/proc').glob('[0-9]*'):
    try:
        for fd in(proc/'fd').iterdir():
            try:
                target=os.readlink(fd)
                if target.startswith(('/dev/nvidia','/dev/nvhost','/dev/nvgpu','/dev/dri')):owners.append(dict(pid=proc.name,path=target))
            except OSError:pass
    except OSError:pass
assert not owners,owners
manifest=json.loads((repair/'variants.json').read_text());row=manifest['variants'][0];native=repair/row['extension']
with native.open('rb')as file:assert hashlib.file_digest(file,'sha256').hexdigest()==selection['native_runtime_sha256']
policy=R/'runtime/repairs/tree-prefix-alignment-v1/libthor_tree_prefix_policy.so';assert hashlib.sha256(policy.read_bytes()).hexdigest()=='3aaf2df16653992750ff5bfcef65ad6c4250d0d3a7bf4a1a388ed6186ee91c68'
builds={role:json.loads((R/name).read_text())for role,name in [('base','S1-shared200k-base-build-v2-result.json'),('draft','S1-shared200k-draft-build-result.json')]}
engines=[]
for tier,capacity in [(65536,66560),(204800,205824)]:
    view=repair/f'engine-view-{tier}'
    for role in ['base','draft']:
        file=view/f'spec_{role}.engine';config=json.loads((view/f'{role}_config.json').read_text())
        assert file.stat().st_size==builds[role]['engine_bytes']and file.resolve()==pathlib.Path(builds[role]['engine_dir'])/f'spec_{role}.engine'
        assert config['builder_config']['max_kv_cache_capacity']==capacity and config['kv_cache_dtype']=='fp16'
        engines.append(dict(tier=tier,role=role,path=str(file),resolved=str(file.resolve()),bytes=file.stat().st_size,verified_prior_full_sha256=builds[role]['engine_sha256'],capacity=capacity,kv_dtype='fp16'))
selected=R/'runtime/config/native-mtp8k-selected-runtime.json';before=hashlib.sha256(selected.read_bytes()).hexdigest()
memory={line.split(':')[0]:int(line.split()[1])*1024 for line in pathlib.Path('/proc/meminfo').read_text().splitlines()}
result=dict(status='PASS_CURRENT_ORIGINAL_TREE_ASSETS_READONLY_ADMISSION',boot_id=boot,GPU_FD_owners=owners,native_runtime_sha256=selection['native_runtime_sha256'],
    engines=engines,policy_sha256=hashlib.sha256(policy.read_bytes()).hexdigest(),production_selected_file_sha256=before,
    production_selected=json.loads(selected.read_text()),MemAvailable_bytes=memory['MemAvailable'],DATA_free_bytes=shutil.disk_usage(R).free,MAP_free_bytes=shutil.disk_usage('/zeekr_map').free,
    Engine_recompiled=False,model_GPU_loaded=False,Golden_changed=False,production_default_changed=False,DFlash2='FROZEN_BACKUP')
assert hashlib.sha256(selected.read_bytes()).hexdigest()==before
out.write_text(json.dumps(result,indent=2));(pathlib.Path('/v2/export')/out.name).symlink_to(out);print(json.dumps({k:v for k,v in result.items()if k not in['engines','production_selected']}),flush=True)
