import hashlib,json,os,pathlib,shutil
R=pathlib.Path('/zeekr_data/nvidia-native-ai-v2');out=R/'V24-tree-regression-terminal-v1.json';assert not out.exists()
for label in ['64','200']:
    guard=json.loads((R/f'V24-tree-target-only{label}-v1-guard-result.json').read_text())
    assert guard['returncode']==0 and not guard['stop_reason']and not pathlib.Path('/proc/'+str(guard['child_PID'])).exists()
owners=[]
for proc in pathlib.Path('/proc').glob('[0-9]*'):
    try:
        for fd in(proc/'fd').iterdir():
            try:
                name=os.readlink(fd)
                if name.startswith(('/dev/nvidia','/dev/nvhost','/dev/nvgpu','/dev/dri')):owners.append(dict(pid=proc.name,path=name))
            except OSError:pass
    except OSError:pass
assert not owners,owners
selected=R/'runtime/config/native-mtp8k-selected-runtime.json';digest=hashlib.sha256(selected.read_bytes()).hexdigest()
assert digest==json.loads((R/'V24-tree-assets-v1-admission.json').read_text())['production_selected_file_sha256']
memory={line.split(':')[0]:int(line.split()[1])*1024 for line in pathlib.Path('/proc/meminfo').read_text().splitlines()}
mounts=[line for line in pathlib.Path('/proc/mounts').read_text().splitlines()if' /new_root 'in line];assert all(' ro,'in line for line in mounts)
result=dict(status='PASS_CPU_ONLY_V24_TREE_TERMINAL_PROTECTION_CHECK',boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),GPU_FD_owners=owners,
    MemAvailable_bytes=memory['MemAvailable'],DATA_free_bytes=shutil.disk_usage(R).free,MAP_free_bytes=shutil.disk_usage('/zeekr_map').free,
    thermal_mC={(p/'type').read_text().strip():int((p/'temp').read_text())for p in pathlib.Path('/sys/class/thermal').glob('thermal_zone*')},new_root_mounts=mounts,
    production_default_sha256=digest,production_default_changed=False,Golden_changed=False,production_health='UNPROVEN;preexisting exclusive RAMmaintenance',production_restore_attempted=False)
out.write_text(json.dumps(result,indent=2));(pathlib.Path('/v2/export')/out.name).symlink_to(out);print(json.dumps(result),flush=True)
