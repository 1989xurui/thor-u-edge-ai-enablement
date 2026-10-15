> **Historical frozen evidence**, not current live state. Sanitized network identifiers. Source SHA256 retained in manifest/SUPPLEMENTAL_EVIDENCE.json. Do not execute commands from this report on a vehicle.

# G4C_PMC_COLD_BOOT_DECISION_REPORT — PMC SCRATCH0 / Cold-Boot Path Decision Gate

- 日期: 2026-10-06
- 范围: 只分析/设计；**未执行任何 kexec / reboot / flash / bootburn / PMC MMIO 写 / DTB・BCT・PCT・BPMP・UFS・boot slot 修改**。
- 证据根: `E:\Thor64G_AI\THOR_U_R39_GOS_BOOT_GATE_20261006\09_g4c_pmc\`（含 raw/ 原始证据）

```
PMC_SCRATCH0_ROOT_CAUSE = CONFIRMED

KEXEC_BYPASS_FEASIBLE = NO

DIRECT_COLD_BOOT_FEASIBLE = CONDITIONAL

RECOMMENDED_PATH = B_DIRECT_COLD_BOOT

READY_FOR_NEXT_GATE = YES

NEXT_GATE = G4D（Route B 落地准备门，单一动作）：
  取得 DRIVE host 工具链（bootburn/drive-foundation）＋ boot slot 只读核实（GOS kernel 槽位/ratchet 布局与回滚路径）
  ＋ 冻结“6.8 GOS 镜像（含去 PMC scratch 的 DTB）打包方案”；三者齐备前不写任何槽位。

CURRENT_BLOCKER =
无阻断分析；执行侧阻塞（Route B 前置）：本机缺 bootburn/drive-foundation/RCM loader 与 p3960 board config，
GOS kernel 槽位布局 guest 不可见（需只读核实）；kexec 路线已被根因排除（平台级写拒绝，重试必然复现）。

CONFIDENCE = HIGH
```

---

## 1. 根因一句话（详情见 09_g4c_pmc/G4C_PMC_ROOT_CAUSE.md）

`Fault IPA 0xc980684` = **T264 PMC scratch aperture(0xc980000) + SCRATCH0 偏移(0x684)**；
kexec 与普通 reboot 都在内核切换准备阶段经过同一 **PMC reboot notifier → program_reboot_reason() → 4 字节写 scratch0**，
被 **DRIVE Hypervisor 的 stage-2 权限（ESR_EL2=0x9393004f，WnR=1，L3 permission fault）拒绝**并触发安全上报；
新 Kernel 6.8 从未获得控制权。**本机 09-29（reboot, VCPU7）与 10-06（kexec, VCPU2）为同一单点故障的两次复现**；
与 NVIDIA 官方论坛案例（DRIVE OS 7.0.3 / p3960-10-sw03，同 ESR/同 IPA 前缀）一致，官方建议 MCU 复位路径。

## 2. 关键证据索引

| 证据 | 位置 |
|---|---|
| live DT pmc 节点（scratch=0xc980000 等四段 reg） | `00_live_baseline/G0_DEVICE_TREE/live-p3960.dts:574` |
| R39 源码（.scratch0=0x684；scratch 可选→无则不注册 notifier；suppress_bind_attrs；kexec 时序） | `G4C_PMC_SOURCE_TRACE.md`（含逐段引用） |
| 运行中 6.1 kallsyms（`tegra_pmc_reboot_notify`×2、`program_reboot_reason`、`restart_handler`） | `09_g4c_pmc/raw/6.1_kallsyms_pmc.txt` |
| 双故障捕获与逐项比对 | `G4C_0929_VS_1006_FAULT_COMPARE.md` + `raw/0929_fault_block.txt` + `08_g4_runtime/g4a_fail_evidence/` |
| NVIDIA 官方论坛案例与 7.0.3/7.2.5 MCU 文档（MCU 管复位；`common_if_testapp -mcureset/-tegrareset`） | `09_g4c_pmc/raw/official_evidence_nvidia.md` |
| 车机只读侦察（无 bind/unbind；无 KEXEC_JUMP；无 common_if_testapp；无 EFI；ratchet 痕迹） | `09_g4c_pmc/raw/g4c_car_recon_out.txt` |
| 冷启动链段（MB1→…→HV-Prod-Secure/BL31→Linux 6.1） | `09_g4c_pmc/raw/coldboot_chain_segment.txt` |

## 3. 两条路线结论（详情见对应文档）

- **Route A（kexec bypass）= NO**：运行时旁路全灭（unbind 被 `suppress_bind_attrs` 禁；kexec-jump 在 arm64/本机配置不存在）；
  唯一理论变体=patch 6.1 内核，但（i）需未持有的 7.0.3 源码/工具链，（ii）**RAM-only 下无可行测试入口（Catch-22）**，
  （iii）第一站即失败、后续 PSCI/machine_shutdown 的 EL2 行为完全未知——不满足"优先 Route A"的全部前件。
- **Route B（直启 6.8）= CONDITIONAL**：与最终形态和官方"MCU/HV 管复位"架构一致；
  条件：DRIVE host 工具 + boot slot 只读核实 + **6.8 GOS DT 去 scratch aperture**（把本次根因固化进镜像，防 6.8 复现）。

## 4. 任务书 §十 七项检查（逐条结论）

| # | 问题 | 结论 | 依据/置信度 |
|---|---|---|---|
| 1 | 为何 7.2.5（Kernel6.8）可正常 reboot 而 7.0.3 fault | **未独立验证**；候选机制：(a) 7.2.5 GOS DT 不再提供 scratch aperture→notifier 不注册（驱动官方支持该可选性）；(b) HV 策略放开该写；(c) 驱动改动移除 notifier。建议取得 7.2.5 BSP 后先核对 pmc 节点 scratch reg | UNKNOWN（候选有源码级支撑 (a)/(c)） |
| 2 | 7.2.5 是否改 PMC 访问方式 | 未验证；R39(=7.2.5 世代)驱动确有"scratch 可选/无则无 notifier"设计 | HIGH_CONFIDENCE（源码在手） |
| 3 | 新 P3960 是否由 MCU/HV 负责 reset | **YES（设计上如此）**：官方文档明确 "MCU manages … reset sequence of SoC"；HV 拦截 guest 直写；官方 workaround=MCU reset | CONFIRMED（官方文档+论坛） |
| 4 | R39/Jetson T264 PMC 驱动是否适合 DRIVE GOS | 适用：compatible 即 `nvidia,tegra264-pmc`（与 live DT 相同）；其"可选 scratch"设计正是 GOS 所需；建议 6.8 GOS 复用+DT 去 scratch | HIGH_CONFIDENCE |
| 5 | `common_if_testapp -mcureset` 的 MCU/Aurix 路径 | 平台路径在（`aurixfw=AFW`；MCU 通信= Ethernet VLAN+GPIO 设计）；**工具缺失**（全盘无 common_if_testapp）→ 需 DRIVE SDK 取得 | CONFIRMED（车机只读） |
| 6 | live DT `pmc@c800000 status=okay` 是否符合 DRIVE Guest 设计 | 符合：GOS 需要 PMC 的 pinctrl/IO-pad/GPIO-AON（DT 中大量 iopad 引用）；问题不在节点，而在把 scratch aperture 暴露给了会注册写 notifier 的驱动 | HIGH_CONFIDENCE |
| 7 | 未来 6.8 GOS 是否应屏蔽 PMC scratch | **应屏蔽**（DT 省略 "scratch" reg 即自动不注册 notifier——官方可选设计）；同时评估隐藏 scratch 系 sysfs 调试 knob。此项列为 Route B 必备设计项 | CONFIRMED（机制源码级） |

## 5. 安全边界声明

- 本任务全部车机取证均只读；未执行方案禁止清单中的任何一项。
- kexec 路线（及一切 reboot 类原地切换）在平台级根因被官方修复前**保持关闭**；重试必然复现同一故障（两次同签名已证）。
- Route B 的下一步（G4D）仅含"工具获取/只读核实/设计冻结"，**不含任何槽位写入**；写入需另开执行 Gate。
