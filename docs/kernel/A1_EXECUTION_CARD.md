# A1 实际结果 — 2026-10-13

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
