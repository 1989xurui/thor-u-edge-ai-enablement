import pathlib,subprocess,re
for f in pathlib.Path('/work/a1/ram-root/a1/lib').glob('libnv*.so*'):
 if f.is_symlink():continue
 lines=subprocess.check_output(['strings',str(f)],text=True).splitlines()
 matches=[l for l in lines if re.search(r'/dev/|/sys/|/proc/|igpu|nvgpu|NVRM_|NVGPU_|getenv|os-release|NvRmGpuDiscover|failed to open',l,re.I)]
 if matches:print(f.name+'\n'+'\n'.join(matches[:90]))
