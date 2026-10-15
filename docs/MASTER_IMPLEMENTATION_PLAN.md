# Thor-U Full Engineering Program：6.1 → 6.8 → R39 GPU/CUDA → Edge-LLM

**全流程总方案 V1，2026-10-15。硬件：DRIVE Thor T264 / P3960-0010 / AArch64 / 14 SM / 64GB UMA。**

## 0. 交付分三个层次（不能混淆）

**源代码与文档已归档**：本仓选中的原创文件、差异、验收报告、资产索引和 Gate 工具在 GitHub。  
**可重建**：新主机持有合法完整官方输入、Kernel 源、R39/NvGPU 用户态/固件、工具链和模型时，能生成与冻结版本 ABI/数值匹配的工作制品；需独立重建验证。  
**可安装并生产**：真正保留 6.1 且新增独立 6.8，能独立冷启动并回退，全部 NVIDIA/CUDA/Edge 资格通过；**当前 NO_GO**。

## 1. 完整结构

~~~mermaid
flowchart TD
  BASE["P00 原版 6.1 Golden / DriveOS7.0.3"] --> SRC["P01-P03 离线锁版、构建 6.8、DTB、initrd"]
  SRC --> BOOT{"P04：启动方式与恢复 Gate"}
  BOOT -->|"历史通过"| RAM["6.1 kexec → 6.8 RAM"]
  BOOT -->|"SDK/硬件仍阻断"| RCM["OEM RAM cold boot"]
  BOOT -->|"签名/独立启动未解"| PER["新增可选择 6.8 永久启动项"]
  RAM --> GPU["P05 R39 NvGPU 595.78 / host1x / DRM"]
  GPU --> CUDA["P06 CUDA 13.2 U2 基础计算"]
  CUDA --> EDGE["P07 TensorRT + Edge-LLM 0.11.0"]
  EDGE --> MODEL["P08 NVFP4 27B / 原生 MTP K7 / Tree"]
  MODEL --> QA["P09-P11 质量、性能、稳定、回退"]
  QA --> RELEASE["P12 版本冻结和 GitHub 交付"]
~~~

### 不变的红线

- 原 OEM 6.1 内核、根分区、启动链、Hypervisor/IVC 安全域、厂商固件、Golden、R4 服务和用户凭证保持原样。
- 严禁未经授权的 flash、bootburn、冷启动槽位写入、kexec、覆写驱动/模型或设备重启。
- 不把公开 Jetson Thor 的 P3834 板级镜像/BCT 当成 DRIVE Thor P3960 的官方包。
- 任何 Gate 失败只归档证据和下一可行安全措施，不无限自动重试，不宣称成功。

## 2. 全流程 13 阶段和严格输入输出

| ID | 目标 | 输入 | 操作/证据 | 阶段产物 | 当前 |
|---|---|---|---|---|---|
| P00 | 当前设备基线 | 原 6.1 Golden | 只读硬件、boot_id、分区、网络、固件/温度 | BASELINE、源 SHA | HISTORICAL_PASS；现场需复核 |
| P01 | 原厂保护和恢复 | OEM 6.1 及合法恢复工具 | 双份校验、只读原件、现场串口/冷断电恢复演练 | GOLDEN_LOCK、RECOVERY_CARD | PARTIAL |
| P02 | 6.8 构建输入冻结 | Linux 6.8.12 源、R39.2.1 源、交叉工具链 | 固定 commit、Kconfig、模块符号、许可 | SOURCE_LOCK、BUILD_MANIFEST | 历史构建 PASS；独立复现待验 |
| P03 | Kernel Guest/HV 适配 | Image、DTB、initrd、cmdline | IVC/vblk、PMC scratch、OEM DT 源关系、SHA | K68_PAYLOAD、DTB_DIFF | RAM 路线历史 PASS |
| P04 | 新增启动/回退 | OEM host boot slot、RCM、板型、签名和恢复 | 先只读解析，后才考虑单独 6.8 入口 | BOOT_MAP、SIGNATURE_MATRIX、RECOVERY | **BLOCKED** |
| P05 | NVIDIA GPU 595.78 | kernel Module.symvers、host1x/DRM、firmware | vermagic、CRC、模块依赖、原版 UMD 映射 | NVIDIA_ABI_GATE | A1 RAM PASS |
| P06 | CUDA 13.2 U2 | libcuda R39、cudart/nvcc 13.2.86 | cuInit、context、memcpy、SM110 kernel、65536 CPU oracle | CUDA_BASIC_RESULT | A1 基础计算 PASS |
| P07 | TensorRT/Edge 层 | TensorRT 10.16.x、Edge 0.11.0 | runtime/wheel/git revision、plugin、CuTe/FA 组件检查 | EDGE_NATIVE_GATE | PARTIAL |
| P08 | NVFP4 27B 模型 | 指定 27B checkpoint、tokenizer、引擎构建输入 | 固定精度/Engine、K7/Graph/cache；严格隔离 | MODEL_AND_ENGINE_LOCK | 8K 有限定通过 |
| P09 | 数值/语义质量 | 冻结 8K 及 XHigh/工具负载 | 同输入 Token IDs、GDN/Conv/KV/日志、拒绝无效候选 | QUALITY_GATE | FULL_PENDING |
| P10 | 速度/资源 | C1/8K 冷热、长输入、内存/温度 | 匹配条件 A/B、TTFT、Prefill、Decode、资源守护 | PERFORMANCE_GATE | PARTIAL |
| P11 | 长稳与故障恢复 | 冷/热重启、Engine/服务恢复、故障注入 | 双向冷启、保底回原厂 6.1、服务依赖、无 OOM | RECOVERY_STABILITY_GATE | NO_GO |
| P12 | 发布并交接 | 完整 SHA/许可/回退/验收记录 | 只读审核→私有 Git→全新克隆→冻结标签 | RELEASE_MANIFEST、DOCS | 源档案可交付 |

细节分别见 BUILD_KERNEL_GPU_CUDA、EDGE_LLM_27B、DEPLOYMENT_RUNBOOK 和 ACCEPTANCE_AND_RELEASE。

## 3. 三条启动路线，必须分别记录

**R：6.1→kexec→6.8 RAM**：已有 A1 历史单会话通过。二者不同时运行，不是持久双系统。G4E2 两次重复 RAM 的 HV/IVC/vblk PASS；A1 6.8/NvGPU/CUDA 实测通过，但原始 firmware/GSP 状态可能跨 kexec 继承。

**C：受支持的 OEM RAM-only 冷启动**：需要 DRIVE 官方主机工具和对应板型/传输面。G4D1 公共 RCM USB 在当前可接接口 FAILED；官方 bootburn -R 还需要实际工具、认证链和板级兼容。**未执行/不得自动重试**。

**P：永久非覆盖式第二 6.8**：必须由 OEM/受支持 host 启动控制面证明独立 6.8 入口、签名、安全镜像位置、回退计数和恢复；当前 Guest 不暴露真实 host-only GOS 槽位，完整授权签名输入缺失。**NOT IMPLEMENTED**。文件拷到数据盘绝不代表“已安装第二内核”。

## 4. 最关键的阻断与优先级

**P0：OEM 启动/签名/恢复**；若无法合法获得并验证 host boot slot 与签名能力，结论保持 HOLD，不绕过安全验证。

**P1：可重建闭包**：从头锁定 Kernel 6.8.12 commit、G35 .config、13,943 导出符号、R39 OOT 模块及 595.78 UMD/firmware 的批次；本仓缺少受限软件二进制，不能声称开箱即用。

**P1：Edge 运行时与权重**：本地 source commit 不等于 installed wheel commit；TensorRT/plugins 的动态库版本必须逐项冻结。仅一个 8K Tree 样本不构成全业务性能增益或完整质量。

**P2：200K/多模态/Agent/C2/长期稳定**：先冻结 8K 单用户质量，再按 Gate 扩展；历史 200K 冷测试代价巨大，已 PASS 的相同条件不再无意义重跑。

## 5. 并行与恢复规则

可并行：离线源码 provenance、许可检查、报告整合、官方文档检索、单独的 host 代码审查、资产 SHA、静态测试。不可并行：同车机 GPU 两个模型/实验、两个维护 owner、模型自动恢复与驱动加载、kexec 与生产用户请求。唯一 GPU owner + 明确维护窗口。

任一阶段 FAILED：保存原始失败日志，确认新 boot_id 和资源状态，不改 Golden，不立即重跑；将风险/尚缺材料写到 manifest/PROGRAM_GATES.json 的下一版本评审中。

## 6. 成功定义与数值边界

- G35 Kernel 6.8.12 的历史模块/符号 CRC 13,943 项闭合，只证明其构建与目标 ABI；独立冷启动未得资格。
- CUDA 13.2 U2 的 65536 数字精确正确，不能推出 TensorRT 所有算子或 27B 全质量。
- 8K K7 的已存有效 Decode 55.444 tok/s、Tree 缓存旁路 57.278 tok/s：缓存条件和时间不同，不称泛化 +3.3%。
- 200K 原生历史冷 TTFT 207.935 s、Decode 32.315 tok/s；目标 ≤180 s、≥36 tok/s 尚未达到。
- 系统保护线：MemAvailable ≥5 GiB、GPU pool ≥2 GiB、Tj <95°C、持久可用 ≥12 GiB；Engine 构建另留空间。
- 只有**独立可回退 6.8 冷启动 + NVIDIA/Edge 实际完整功能 + 质量 + 长稳 + 安全回退**同时通过才可标记 PRODUCTION_PASS。

## 7. 报告结构与人工交接

每次产出记录 CURRENT_SCOPE、SOURCE_DATE、HARDWARE/BOOT_ID、CURRENT_SHA、SOURCE_VERSION、GATES、TEST_MODE、NUMERIC_QUALITY、PERFORMANCE、RESOURCE_FLOOR、ROLLBACK_READY、BLOCKERS、NEXT_SAFE_ACTION。所有历史结论必须标明当时版本和测试范围，不得自动提升为当前验收。
