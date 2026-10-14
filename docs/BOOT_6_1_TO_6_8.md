# 6.1 Golden 基础上新增 Linux 6.8：增量双路径方案

## 目标与当前判决

**目标**：在不覆盖 NVIDIA DRIVE Thor T264 原有 DriveOS 7.0.3 / Linux `6.1.119-rt45-prod-rt-tegra` 和 Golden 的前提下，新增受控 Linux `6.8.12` AI 实验运行环境，进一步探索 NVGPU 595.78、CUDA 13.2 U2、TensorRT Edge-LLM。长期才考虑两个独立可选启动路径。

**当前结论（2026-10-15 文档审核）：**已有 6.1 → RAM kexec → 6.8.12 → R39/NvGPU → CUDA 基础计算的限定历史 PASS；**没有新增可永久启动的第二 6.8、没有已验收的 6.1/6.8 启动菜单、没有独立 6.8 冷启动。**不要以本仓库安装文件和状态来证明车机正在运行某个版本。

架构图请看 [ARCHITECTURE.md](ARCHITECTURE.md)。

## 设备历史基线（非当前 live 读数）

| 项目 | 记录 | 来源 |
|---|---|---|
| 型号 | p3960-0010 / T264，14 SM，64GB UMA | Golden 2026-09-01 |
| 原厂 Guest | Ubuntu 24.04.1、DriveOS 7.0.3、Kernel 6.1.119-rt45-prod-rt-tegra | Golden 2026-09-01 |
| 原厂用户空间 | CUDA 12.8、TensorRT 10.10.x（原件记录精确版本） | Golden 2026-09-01 |
| 原厂根分区 | `/dev/vblkdev0`（4 GiB，read-only） | Golden |
| 实验 Kernel | `6.8.12-prod-g78272943bba3`，RAM/kexec 暖启动 | A1 2026-10-13 |
| 实验计算 | NvGPU 595.78、CUDA 13.2.86 context/拷贝/Kernel/数值 PASS | A1 |

不把曾经的原厂 6.1 Golden 历史 PASS 当作目前立即断电可安全复原的保证：实际 boot/slot、冷复位、生产依赖和恢复凭据必须在新的现场窗口复核。

## 不能混淆的三种“新增 6.8”

### R. 6.1 → 6.8 RAM kexec（历史已验证，有边界）

- 既有 Guest 6.1 作为历史出发点，使用一次经人工资格化的内核内存交接，进入另一份 Linux 6.8 实验会话；没有在启动菜单注册 6.8。
- 需要完整的 6.8 Image、DTB、initrd、cmdline、Hypervisor/IVC/vblk 关系与 ABI 匹配；A1 的 Kernel 版本只对应其固定证据 SHA。
- 历史 G4E 解决 `nvidia,tegra_hv_ivc` 绑定、IVC 通道与只读 vblk 挂载。历史 A1 在 6.8 RAM 会话中加载原版 NvGPU 及依赖并完成 CUDA 13.2 基础数值验证。
- RAM kexec 不意味着安全冷启、独立启动、自动重启恢复或生产可用。重跑需单次维护许可、保留所有仍可访问的恢复通道；仓库**不提供 kexec 启动器**。

### C. 官方 RAM-only cold boot（候选，未完成）

- 和从运行中 6.1 kexec 不同，此路径从受支持的外部/OEM 主机启动接口把实验 6.8 加载到 RAM；不应重写 Golden。
- 旧 G4D 的 bootburn/SDK host 组件获取及 host-only 槽位解析均为 PARTIAL；G4D1 公共 RCM 进入成功但两个可接 USB-C 无 APX 设备，`PUBLIC_T264_RCM_DETECT=FAIL`。
- 缺完整官方硬件通路、板级配置和签名/授权前仍 NO_GO。不能把 Jetson Thor 的 BCT/镜像当成 p3960 DRIVE Thor 的替代品，也不能靠推测固件地址。

### P. 在 6.1 基础上真正新增独立 6.8 持久启动路径（设计目标，未实施）

必须找到**受 OEM/平台支持的真实第二启动入口**，而非假设有 UEFI/GRUB。Guest 侧 GOS boot slots 是 HOST_ONLY，当前本仓库没有合法且完整的独立引导修改/回退装置。即使把 6.8 文件放入 `/zeekr_data` 目录，也只代表“文件存在”，不代表能冷启动。

设计上需保持：原 6.1 镜像、DTB、initrd、boot 配置和安全域**完全不修改**；独立 6.8 载荷必须有单独的完整版本锁、完整 boot/driver/固件依赖；启动选择权必须来自受支持的 OEM/Hypervisor 机制。未取得这些前仅做离线差分、签名/兼容性分析和恢复演练，不做车机启动写操作。

## 具体门槛：通过前禁止进入下一层

| Gate | 必须解决的问题 | 当前 |
|---|---|---|
| B0 原始备份 | 6.1 Golden + rootfs/DTB/原启动链来源、SHA、授权恢复工具核对 | 历史 Golden PASS；即时恢复条件待复核 |
| B1 6.8 完整载荷 | 源码、ABI/Kconfig、Image+DTB+initrd+cmdline 和许可来源一一对应 | 历史 A1 已冻结；Git 仅源代码/报告，**缺可部署镜像** |
| B2 独立启动入口 | OEM host 侧 boot/slot/签名/回滚/设备口完整拓扑 | PARTIAL / BLOCKED |
| B3 硬件恢复 | 原厂 cold boot、供电复位、物理串口、失败修复演练真实可执行 | 历史特定场景有记录；当下待验证 |
| B4 非覆盖式 6.8 | 6.8 独立位置、全部哈希、未碰原厂 6.1 与安全相关分区 | NOT IMPLEMENTED |
| B5 两次独立冷启 | 6.8 独立冷启及重复、GPU 初始化、从 6.8 选择/复归 6.1 | NOT ENTERED |
| B6 CUDA/Edge 发布 | CUDA 固定数值、NVFP4 27B、8K/200K、API、质量稳定性 | CUDA 基础在 A1 RAM PASS；生产 NO GO |

**Early-stop**：任何 B2/B3/B4 不合格，禁止执行 kexec、新增引导入口、bootburn、刷写、改槽位、OEM firmware/DTB 覆盖、HV 安全域变更。`tools/check_dual_boot_readiness.py` 是离线报告器，不能操作车机。

## 非覆盖安装设计流程（仅计划）

1. 冻结 6.1 Golden 的**只读**身份与来源；获取签名的可恢复完整原件和授权方式，并复核现场远程/物理恢复链。
2. 离线锁定 6.8.12 Image/DTB/initrd/cmdline、G35 ABI、R39 NvGPU/DRM/host1x 依赖与 CUDA 13.2；无实际文件的部分标为未就绪，不能用 manifest 代替。
3. 由 OEM/授权工具只读枚举 Hypervisor/GOS 启动入口、A/B (如存在) 的真实映射与回退计数。Guest 系统没有暴露 EFI 并不能证明具备 PC 双启动能力。
4. 如且仅如官方机制支持独立且不覆盖 6.1 的新引导目标，在开发主机完成 6.8 isolated payload 的 hash/dry-run 比较；若只能覆盖唯一启动项则拒绝方案。
5. 首先完成独立冷启动与返回 6.1 的功能和失效注入验收，再在受控 6.8 会话按 ABI→NvGPU→CUDA→TensorRT→Edge-LLM 顺序验收；生产/车辆安全服务隔离。
6. 通过全部 Gate 后才可把方案升级为可用安装/选择说明；当前仅提供证据保留、结构图和只读预检。

## 恢复策略：区分设计与已实测

- **6.1 保留**是配置策略；历史部分冷断电回到 6.1 曾得到验证，但未来异常、断电、当前系统状态并未统一试验。不要承诺所有情况“自动回原版”。
- **6.8 kexec 失败**不能依赖内核自行修复；恢复路径必须在操作前现场确认，尤其 Hypervisor/串口/网络与 boot slot 状态。
- **6.8 独立启动失败**只有在 OEM 入口与救援方法经验证后才可配置错误计数/回退策略。当前不存在可执行的自动恢复模块。
- 不得删除/覆盖 Golden、R4、原厂安全相关分区、签名固件；安装过程不得触动汽车控制相关服务。

## 来源索引

- 6.1 Golden 原始报告（未上传完整原厂文件）: `E:\Thor64G_Backup\GoldenBoard_2026-09-01\GOLDEN_BOARD_REPORT.md`。
- A1：本仓库 `docs/kernel/A1_EXECUTION_CARD.md`；本机 `D:\Thor64G\THOR_U_A1_NVGPU_R39_20261013`。
- kexec / RAM 6.8：`docs/kernel/history/G4_G6_PLATFORM_FINAL_REPORT.md`；额外详细报告本机 `E:\Thor64G_AI\THOR_U_R39_GOS_BOOT_GATE_20261006\07_reports`。
- 公开 RCM 障碍和冷启准备：本机 `G4D1_G4D2_G4E_G5_FINAL_REPORT.md`、`G4D_COLD_BOOT_PREPARATION_REPORT.md`；证据未全部纳入此轻量仓库。
- Edge：`docs/edge/CURRENT_RELEASE_CARD.md` 和 `docs/STATUS_AND_ACCEPTANCE.md`；不是生产安装授权。
