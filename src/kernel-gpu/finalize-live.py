import pathlib,json,hashlib,re,datetime
P=pathlib.Path(r'D:\Thor64G\THOR_U_A1_NVGPU_R39_20261013');E=P/'logs/live/evidence'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
log=(E/'a1-board-fw.log').read_text(encoding='utf-8');trace=(E/'a1-board-fw-trace.log').read_text(encoding='utf-8');ctx=(E/'runtime-context.txt').read_text(encoding='utf-8')
assert 'A1_NATIVE_CUDA_U2_COMPUTE_PASS' in log and '+++ exited with 0 +++' in trace
assert all(x in log for x in ['DRIVER_VERSION=13020','RUNTIME_VERSION=13020','DEVICE=Thor SM=110','RUNTIME_DEVICE_COUNT rc=0 count=1'])
assert '6.8.12-prod-g78272943bba3' in ctx and '9d74daba-0347-489c-9192-2d117806cbe7' in ctx
sha_lines=(E/'live-SHA256SUMS').read_text(encoding='utf-8').splitlines();actual=dict((l.split(None,1)[1].strip(),l.split(None,1)[0]) for l in sha_lines)
assert actual['/a1/modules/nvgpu.ko']=='a09deb9b37b8294c0b2a58239df14832eb15f8ead96aa0baa00543998befdf04'
assert actual['/a1/lib/libcuda.so.1.1']=='b2e91cba26490f5261454afc07240862e30ff583029915a495dd508261dabcd5'
assert actual['/a1/lib/libnvcucompat.so']=='4dfc10198f67422f0b46d8daaa019d3d52a50b4a9a6489cc3ec364f757e48ad2'
u2=read(P/'logs/cuda-u2-component-verification.json');assert len(u2)==6
result=dict(status='PASS_NATIVE_CUDA_13_2_U2_BASIC_COMPUTE_ONLY',kernel='6.8.12-prod-g78272943bba3',boot_id='9d74daba-0347-489c-9192-2d117806cbe7',boot_method='kexec_RAM_initrd; original root mounted read-only',device='Thor GB10B 10de:2b00 SM110',nvcc='13.2.86; official CUDA 13.2 Update2 redistrib_13.2.2',driver_api_version=13020,runtime_api_version=13020,driver='R39.2.1 NvGPU libcuda595.78',runtime_file='libcudart.so.13.2.86',checks=['cuInit','driver and runtime device count=1','SM11.0','cuCtxCreate_v2','cuMemAlloc_v2','HtoD copy','CUDA13.2.86 nvcc sm_110 cubin load','cuLaunchKernel','cuCtxSynchronize','DtoH copy','65536 integers equal input+17','module unload, memory free, context destroy','actual mapped libraries recorded'],exit_code=0,full_trace_lines=len(trace.splitlines()),ioctl_records=trace.count('ioctl('),repairs=['Add SHA-verified same-batch nvidia-l4t-cuda/libnvcucompat.so; DT_NEEDED alone missed dlopen dependency','Add matched tegra-drm + DRM/nvhwpm closure; all1547 imported CRCs resolved','Set RAM firmware_class search path to /lib/firmware/nvidia and map exact original DRIVE prod_test_nsr 5file group read-only; no file renaming or signature modification'],kernel_transitions=1,nvgpu_module_loads=1,cuda_probe_processes=5,probe_results_in_order=['999 missing libnvcucompat','999 traced diagnosis, no GPU ioctl','801 missing host1x DRM','100 missing board NSR netlist','0 actual numeric compute PASS'],interrupt_path='documented NvGPU INTx fallback; RAM pci bridge msi_bus=0; GICv3 SPI187 IRQ211',limitations=['ITS/LPI warnings remain; MSI not qualified','Independent cold boot not proven; firmware/GSP state inherited across kexec possible','No persistent installation or autonomous startup','No cuBLAS/NVFP4, graphs, long-run, 27B or 200K acceptance'],A1='GO_BASIC_NATIVE_RAM / NO_GO_PRODUCTION_COLD_BOOT',A2='DEFERRED_BY_USER_NOT_AUDITED',current_state='KEEP_6_8_RAM_PER_USER; R4 production services intentionally stopped; exclusive host lease retained',firmware_contract='Board original prod_test_nsr firmware accepted for this warm native compute; public R39 firmware-only configuration failed missing required board group',DRIVE_HV_contract='HV/IVC storage read-only mount, host1x DRM, NvGPU bind, GIC INTx and bounded native compute observed; cold GSP/ACR bootstrap and ITS ownership unproven',CUDA_userspace_ABI='PASS_FOR_OBSERVED_BASIC_COMPUTE_ONLY; all NVIDIA UMD libraries from R39.2.1, U2 cudart; no CUDA12 mapped',golden='No writes to Golden, model, original firmware or boot configuration',evidence_archive_sha256='6ae5d1671154365fc6b3796e4931c66660a101b0cef85e5daa0fcd2e803db4f1',next_action='Read-only audit of an independently bootable and recoverable Kernel6.8 path preserving Golden; no further repetitive CUDA smoke tests')
(P/'A1_NATIVE_RUNTIME_RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
d=read(P/'A1_BUILD_ABI_VERDICT.json');d['GPU_INITIALIZATION']='PASS_OBSERVED_WARM_RAM';d['CUDA_13_2_U2_NATIVE']=result['status'];d['runtime_result']='A1_NATIVE_RUNTIME_RESULT.json';d['additional_userspace_required_module_closure']=read(P/'logs/drm-closure-abi.json');d['production_admission']='NO_GO_PRODUCTION_COLD_BOOT';d['actual_car_state']=result['current_state'];(P/'A1_BUILD_ABI_VERDICT.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
b=read(P/'A1_BASELINE_AND_ASSETS.json');b['current_runtime_result']='A1_NATIVE_RUNTIME_RESULT.json';b['additional_common_cuda_package']=read(P/'logs/cuda-common-package-verification.json');b['CUDA_U2_components']=u2;b['vehicle_preflight']='logs/vehicle-root-preflight.json and logs/vehicle-final-read.json';b['scope_update']='User explicitly authorized exclusive vehicle operations and repairs; requested no restore until final abandonment; original document offline-only scope superseded by direct user requests';(P/'A1_BASELINE_AND_ASSETS.json').write_text(json.dumps(b,ensure_ascii=False,indent=2),encoding='utf-8')
with (P/'A1_FIRMWARE_HV_MATRIX.tsv').open('a',encoding='utf-8') as f:
 f.write('\nLIVE_WARM_COMPUTE\tDRIVE original gb10b/prod_test_nsr five-file group, RO RAM mapping\tPASS_BASIC_OBSERVED\tNo independent cold bootstrap evidence; public R39 package lacks group\n')
 f.write('LIVE_HV_ABI\tHV storage, host1x DRM, NvGPU INTx, R39 UMD + CUDA U2\tPASS_BASIC_OBSERVED\tITS/MSI and autonomous cold boot remain unqualified\n')
card='''# A1 实际结果 — 2026-10-13

**GO_BASIC_NATIVE_RAM；NO_GO_PRODUCTION_COLD_BOOT。**

- 82 项历史 SHA、17 个 R39.2.1 官方包 SHA 已核对；D 盘干净 WSL 重建成功。
- 精确 G35 Kernel6.8.12 构建与13,943项历史导出符号一致；NvGPU及依赖 CRC 闭合。补建 host1x DRM 闭包8模块、1547导入CRC无冲突。
- 已在车机 **6.8.12-prod-g78272943bba3** 下实际加载 NvGPU。仅一次 kexec、一次 NvGPU加载，期间保持现场修复依赖。
- **原生 CUDA13.2 Update2 基础计算 PASS**：官方13.2.86 nvcc生成SM110 cubin；595.78 NvGPU libcuda + 13.2.86 cudart；Context、alloc、HtoD、真实Kernel、同步、DtoH、65536项数值核对全部成功，exit0。
- 修复：同批次 libnvcucompat.so、host1x DRM及依赖、RAM固件搜索路径，以及原厂只读 prod_test_nsr 5文件组的精确映射。没有覆盖原厂固件，没有改签名或改固件名冒充另一安全域。
- 本次只证明该暖启动RAM会话的基础计算。ITS/LPI告警仍存在，使用 NvGPU 官方INTx回退。独立冷启动、冷GSP/ACR启动、长期稳定、cuBLAS/NVFP4/27B/200K均未验收。
- 当前仍保留 **6.8 RAM 会话与独占维护**，R4服务按授权暂停；按用户要求不恢复6.1。Golden、模型、原厂固件和启动配置未改写。
- A2：用户暂缓，未作R610/R615技术判决。

唯一下一动作：只读核查可独立启动、可可靠回退的6.8启动路径；不再重复CUDA基础烟测。

权威证据：[运行结果](A1_NATIVE_RUNTIME_RESULT.json)、[原始日志](logs/live/evidence/a1-board-fw.log)、[系统调用跟踪](logs/live/evidence/a1-board-fw-trace.log)、[当前环境和中断](logs/live/evidence/runtime-context.txt)、[实机SHA](logs/live/evidence/live-SHA256SUMS)。
'''
(P/'A1_EXECUTION_CARD.md').write_text(card,encoding='utf-8');print(json.dumps(dict(status=result['status'],A1=result['A1'],A2=result['A2'],runtime_evidence_verified=True)))
