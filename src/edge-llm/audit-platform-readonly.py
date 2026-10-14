import json,pathlib,platform,shutil
root=pathlib.Path('/zeekr_data/nvidia-native-ai-v2')
mounts=[line.split()for line in pathlib.Path('/proc/mounts').read_text().splitlines()]
firmware=pathlib.Path('/lib/firmware/nvidia/gb10b/prod_test_nsr')
record=dict(kernel=platform.release(),boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            mounts=[dict(source=m[0],path=m[1],filesystem=m[2],options=m[3])for m in mounts if m[1]in['/','/new_root','/zeekr_data','/zeekr_map']],
            block_devices=[p.name for p in pathlib.Path('/sys/block').iterdir()],
            efi_runtime_present=pathlib.Path('/sys/firmware/efi').exists(),efi_variables_present=pathlib.Path('/sys/firmware/efi/efivars').exists(),
            firmware_source=str(firmware.resolve()),firmware_files=sorted(p.name for p in firmware.iterdir()),
            firmware_search_path=pathlib.Path('/sys/module/firmware_class/parameters/path').read_text().strip(),
            original_boot_entries=sorted(p.name for p in pathlib.Path('/new_root/boot').iterdir())if pathlib.Path('/new_root/boot').is_dir()else[],
            persistent_free_bytes={p:shutil.disk_usage(p).free for p in['/zeekr_data','/zeekr_map']},
            independent_kernel68_cold_boot='NOT_PROVEN',current_boot_method='A1 RAM kexec session',
            cold_boot_remaining='Approved recoverable persistent boot path has not been validated; current RAM success does not prove it',
            firmware_write_performed=False,bootchain_write_performed=False)
(root/'platform-readonly-audit.json').write_text(json.dumps(record,indent=2));print(json.dumps({k:record[k]for k in ['kernel','boot_id','independent_kernel68_cold_boot','persistent_free_bytes']}))
