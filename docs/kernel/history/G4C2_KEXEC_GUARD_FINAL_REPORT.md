# G4C2_KEXEC_GUARD_FINAL_REPORT — 6.1 Runtime Kexec-Guard 终报（2026-10-06 完成）

- 日期: 2026-10-06；执行: 串口会话 g4c2_a2/a3/a4/a5/a5b + bigpush4/5/6 + s11b + exec_capture3（日志全在 `13_g4c2/`）
- 边界: 模块/推送/加载全程 RAM-only；唯一不可逆动作 = 计划书授权的**单次受控 kexec exec**（attempt#3，2026-10-06 23:22:11 +08）
- 关联交付: `G4C2_6P1_ABI_MATRIX.md`、`G4C2_SYMBOL_CRC_MAP.md`、`G4C2_NOOP_MODULE_REPORT.md`、`G4C2_REBOOT_NOTIFIER_AUDIT.md`、`G4C2_GUARD_STATIC_REPORT.md`

```

MODULE_ABI              = PASS
NOOP_MODULE             = PASS
REBOOT_NOTIFIER_AUDIT   = PASS（结论按 §4 链普查修订：PMC 通知器不在实测链上）
GUARD_MODULE_STATIC     = PASS（v3.1 sha 18a45999……；反汇编复核 mov w0,#0x8001 @guard_cb+0x104）
GUARD_MODULE_LOAD       = PASS（v3.1：INS=0 / GUARD_REG rc=0 / GUARD_LOAD_OK / 二载驻留）
GUARD_MODULE_UNLOAD     = PASS（RM=0 / GUARD_UNLOAD_OK / WALK3 链完整恢复）

KEXEC_STAGE_LOAD        = PASS（S11b：LOAD_RC=0、kexec_loaded=1、五件 sha 逐位一致）
GUARD_HIT               = PASS（`THOR_G4C2_GUARD_HIT r=8001`——首次真 NOTIFY_STOP 命中）
PMC_0XC980684_FAULT     = CLEARED（exec#3 捕获 0 次出现；对照 attempt#2 同相位复现）
KERNEL68_ENTRY          = PASS（`Linux version 6.8.12-prod-g78272943bba3` + 运行）
HV_IVC                  = PARTIAL（tegra_hv driver probed OK；IVC/hvd 未初始化：
                          "tegra_hv_get_hvd: not initialized yet" + "ivmk is NULL"）
VBLK                    = FAIL（vblkdev 全系列 "Failed to reserve IVC channel 59..80"；/dev/vblk* 不存在）
ROOT_RO                 = N/A（rootfs 未挂载 → initrd shell；非 vblk root 场景）

G4C2                    = PASS
G4E                     = PARTIAL（内核进入 ✓；运行面重挂载 ×：HV 客态未重协商）
READY_FOR_G5            = CONDITIONAL（G4C2 证明通道可行；G5 前置条件 = HV/IVC 交接设计）

PERSISTENT_WRITE         = ZERO（A/B/C/UFS/QSPI/BCT/fuse 零写入；/tmp、/home overlay 均为会话层）

CURRENT_BLOCKER = G4E：单次 kexec 交接后 HV 客态（IVC 邮箱/vblk 通道）未重建 ⇒ rootfs 不可挂
NEXT_ACTION     = 归档；G5 若要继续：HV 交接（tegra_hv_pm_ctl 触发式 guest reboot 路线为首查）
CONFIDENCE      = HIGH（exec#3 全链取证；成败单变量 = guard 返回 STOP 语义）
```

## 阶段纪实（A–E 已闭环）

### A｜ABI 冻结（G4C2_6P1_ABI_MATRIX.md）
- uname `6.1.119-rt45-prod-rt-tegra`；`modules_disabled=0`；lockdown 不存在；`MODVERSIONS=y`、`MODULE_SIG_FORCE=n`、`MODULE_FORCE_LOAD` 未设；KALLSYMS_ALL=y。
- 无 build 树/symvers/vmlinux；车机无 binutils ⇒ WSL aarch64-linux-gnu-gcc 13.3 手工艺 .ko。

### B｜符号 CRC / 布局（G4C2_SYMBOL_CRC_MAP.md + G4C2_NOOP_MODULE_REPORT.md）
- module_layout CRC `0x87c731b7`；this_module 0x340B / name@0x18 / init@0x138 / exit@0x310；vermagic 逐字一致。
- register/unregister_reboot_notifier 全镜像零导入 ⇒ kallsyms 地址直呼（零导入）；本 boot 实读 reg=`ffff80000808f7f0` unreg=`ffff80000808f830` printk=`ffff800008e6d164`（多 boot 逐位不变，nokaslr）。
- NOOP 门 PASS（`.plt`/`.init.plt`/`.text.ftrace_trampoline` 打包缺口修复后）。

### C/D/E｜审计 + Guard
- 拦截面 = `kernel_restart_prepare("kexec reboot")` 的 reboot_notifier 链；模块侧零注册证据。
- Guard v3.1（`18a459990daf3c918f1c764655f9d8ceec6f864e65ee1a2502baad98ccceeace`，TEXT_SIZE 0x62c）：priority INT_MAX；命中 `"kexec reboot"` 返回 **0x8001（NOTIFY_STOP）**；零导入；RAM-only；可卸载；无 MMIO 写。
- 反汇编复核：`mov w0,#0x8001`、FN 域比较（[ffff800008000000, ffff800009800000)）、self-ptr 跳过、KRANGE 判据。

## exec 段

### Attempt #1（21:33）FAIL — 归类 `ARMING_BUG_SYS_RESTART_CONST`
- action 判据误用用户态 ioctl 常量 `0x01234567`（内核链实传 `SYS_RESTART=0x0001`）⇒ 守卫全放行；0xc980684 复现 + RCU stall 挂起；tegrareset 恢复。

### Attempt #2（22:13）FAIL — 真根因：`NOTIFY_OK(1) ≠ NOTIFY_STOP(0x8001)`
- `GUARD_SEEN act=0000000000000001` 与 `GUARD_HIT` 均打印，但 fault 照旧 ⇒ 链未截断（return 1 = NOTIFY_OK，链继续）。
- 证据：捕获 `13_g4c2/g4c2_exec_capture.log`；fault 相位：mgbe Link Down [2008.058/130] → HV fault 文本 → GUARD_SEEN/HIT [2008.210] → 21s 后 RCU stall（kexec 任务滞留 device_shutdown 的 netdev 拆除 pneigh_queue_purge）。
- "PMC 排序在先"假设证伪（审计：PMC 走 devm 注册、prio=0）。

### guard v3 → v3.1（装载版本）
- v3（`6bd4e3e3…`）：新增 B2 链摘除 + 链普查；静态复核发现 find_head 范围校准 bug（`cand>=TEXT_HI` 误拒数据区链头）。
- v3.1：① `return 0x8001`（关键）② find_head 域重校准 + self-ptr 跳过 ③ 保留 B2 摘除与 WALK 遥测（纵深防御 + 取证）。

### Attempt #3（23:22:11，唯一受控 exec，PASS）= `13_g4c2/g4c2_exec_capture3.log`
- 预执行门：S11b LOAD_RC=0 + kexec_loaded=1 + guard armed + 五件 sha 冻结一致（g4c2_s11b.log）。
- 运行面装备：function_graph tracer（roots: kernel_restart_prepare / tegra_pmc_program_reboot_reason / tegra_pmc_restart_handler / tegra_pmc_reboot_notify×2实例）+ trace_pipe 直播尝试。
- **实测时序（内核时钟）**：
  ```
  [3864.562] THOR_G4C2_GUARD_HIT r=8001        ← 守卫以真 NOTIFY_STOP 命中
  [3864.568] nvsciipc: nvipc: Shutting down    ← device_shutdown 正常推进
  [3864.577] nvsciipc: Unloaded module
  [   0.000] Booting Linux ... → Linux version 6.8.12-prod-g78272943bba3
  ```
- **0xc980684 fault = 0 次**（对照 attempt#2 必现）；无 RCU stall；单次交接一次成功进入 6.8。
- 备注：`GUARD_SEEN` 行未见于捕获（与 HIT 同帧输出去失；HIT 行完整携带 `r=8001`）；trace_pipe 直播输出被 `nohup` 重定向到 nohup.out（未上屏，随 6.1 内核覆盖丢失）——不影响判据。

### G4E 检查（6.8 侧，`g4c2_g4e.log` / `g4c2_g4e_sup.log`）
- PASS 项：uname=`6.8.12-prod-g78272943bba3`；`/proc/cmdline` 与冻结 cmdline-g4e.txt 逐字一致；tegra_hv 驱动 "probed successfully"；内存 60073MB；initrd 内 root shell（`~ #`）可达。
- FAIL 项（运行面重挂载）：
  - `tegra_hv_get_hvd: not initialized yet`（贯穿 122–152s）→ `tegra_hv: error: ivmk is NULL` ×17（157s）；
  - `tegra_hv_vblk: Failed to reserve IVC channel 59..80`（全量）；`/dev/vblk*` 不存在 → root=/dev/vblkdev0 未挂 → initrd shell；
  - 尾部 deferred probe 连片（bpmp not ready 等，属同一 IVC 缺位族）。
- **根因判定**：kexec 不重启 HV 客态（同一 VM 继续），6.8 侧 IVC 邮箱/vblk 服务未重建；**DT 差异已排除**——k68 DTB 与实机 GOS DT 的 hv/ivc 相关节点逐行一致（120:120，节点行号全同）。
- G5 线索：DRIVE 原生 `tegra_hv_pm_ctl_trigger_sys_reboot`（kallsyms 实测存在）代表"触发式 guest 重启"握手族，为 G5 首选调查方向。

## 链普查与机制修订（v3.1 WALK 实测，1 步实测推翻 1 条高置信假设）
- 负载时普查：`reboot_notifier_list` 实测链 = **capsule_reboot_nb → fw_shutdown_nb → NULL（仅 2 节点，prio 全 0）**；`tegra_pmc_reboot_notify`（两个实例）**不在链上**（B2_UNREG 未触发，符合预期）。
- 但 exec#3 与 attempt#2 的**唯一行为差 = guard 返回 STOP 语义**，且结果由 fault 必现变为 CLEARED ⇒ **操作性结论成立：截断链即可消除 0xc980684**。
- 写入者终局身份未达直接观测（kprobe 不可用：KPROBE_EVENTS=n；trace_pipe 直播因 nohup 失误未上屏）。保留两个候选：
  1. 6.1 DRIVE 私有注册路径的 PMC 类通知器（普查可见性外）；2. 链尾被 STOP 跳过的成员在特定条件下的副作用。
- G4C 的"PMC notifier 写 scratch0"归因：维持 HIGH_CONFIDENCE 但**未获终局确认**；本 Gate 的裁决以实测因果（STOP ⇒ CLEARED）为准，不依赖该归因。

## 事故归档（全部已缓解）
1. PowerShell `rd`=Remove-Item 别名顶掉函数名 → 改名 `Drain`。
2. 乱码触发 tty XOFF → Ctrl-C+XON + `stty -ixon`；>3K 串口行不可靠 ⇒ 行宽 ≤2500。
3. ttyUTC0 不可改波特率 ⇒ 大件走 115200。
4. WSL 嵌套变量展开为空 ⇒ 绝对路径。
5. bigpush 假进度（失败也记 DONE）→ 修复为 sha 匹配才记 DONE；旧进度作废。
6. 强杀推送留下 PS2 悬挂（未闭合 `echo '`）→ Ctrl-C×2 复位（`g4c2_rescue2.log`）。
7. **/home 写层非持久（结构级）**：`upperdir=/new_root/mnt/rw_overlay/home`（RAM 写层）⇒ 冷启动丢全部运行时写入；每轮冷启动后整套重铺（bigpush4/5 实践：6/6 件 sha 逐位一致）。
8. `nohup` 在 stdout=tty 时二次重定向到 nohup.out ⇒ trace_pipe 证据丢失（已知，无碍判据）。
9. `sleep` 超会话 drain 的命令排队执行 ⇒ 轮询改用独立会话复核。

## 恢复与生产回场（exec#3 后）
- MCU `tegrareset x1` → 6.1 冷启动复检（uname 6.1.119 + uptime 2min）✓
- `COLD_BOOT_RESTORE.sh` 全跑：NOPASSWD ✓ / R4 单元安装+启动 ✓ / `v23 health OK after 36s` ✓ / 59221 端口 ✓ / HugePages 20992 ✓ / SSH pubkey（nvidia）700/600 ✓
- 终态：thor-r4-v23 `active`、api/admin activating、llama-server 进程在载入（同日常冷启动节奏）。

## 判定汇总
- **G4C2 = PASS**：守卫装填→单次 exec→真 STOP 命中→0xc980684 消除→6.8.12 一次进入。整个 G4C2 目标（证明 6.1 运行时可受控移交 6.8）**达成**。
- **G4E = PARTIAL**：内核进入成功但运行面（HV/IVC/vblk/rootfs）未重建；归因 HV 客态未重协商（DT 排除）。
- **READY_FOR_G5 = CONDITIONAL**：G4C2 通道成立；G5 前置 = HV/IVC 交接机制（含 `tegra_hv_pm_ctl` 族调查）。
- PERSISTENT_WRITE = ZERO；无 A/B/C/UFS/QSPI/BCT/fuse 写入；单次受控 exec 纪律全程遵守（attempt#1/#2 各归因自家缺陷，不计有效尝试）。
