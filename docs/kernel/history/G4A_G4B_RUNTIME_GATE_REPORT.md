# G4A_G4B_RUNTIME_GATE_REPORT — THOR-U R39.2.1 RAM-only 实机验证

- 日期: 2026-10-06
- 执行包: `05_initrd/out/g4_package_g35/`（SHA256 全核对 PASS）
- 结论总表（按方案规定格式）:

```
G4A = FAIL
G4B = NOT_EXECUTED   （方案门规则：只有 G4A = PASS 且已冷启动返回 6.1 Golden 才可进入 G4B）

KERNEL68_RUNTIME = FAIL        （kexec 交接中止; Kernel 6.8 从未获得控制权）
HV_IVC_RUNTIME   = NOT_REACHED
VBLK_RUNTIME     = NOT_REACHED
ROOT_RO_RUNTIME  = NOT_REACHED

REPEATABILITY = NOT_APPLICABLE （G4B 未执行）

READY_FOR_G5 = NO

CURRENT_BLOCKER =
kexec --exec 交接在本机 DRIVE OS 7.0.3 GOS 上触发 EL2 未处理写(two 次不同场景同一 IPA)：
  GID 0: Unhandled access of size 4 for write / Fault IPA 0xc980684 / ESR_EL2=0x9393004f
  (EC=0x24 data abort from lower EL, WnR=1 写, DFSC=0x0F stage-2 permission fault L3, VM VCPU 2)
→ Tegra Report Error (0x8200/0x800f0000/0x20) → EPS 全核 fatal → 客机用户态永久卡死(hung tasks);
→ 6.8 内核无任何执行痕迹（无 Linux banner / 无 earlycon 输出）⇒ 交接在机器切换路径即被平台拒绝。
该故障与 2026-09-29 普通 reboot 失败 **同一故障点**（同一 Fault IPA 0xc980684，VCPU 7）——
⇒ 本平台上“任何原地内核切换路径（kexec 与 reboot）都被同一 EL2 写拒绝阻断”，需要平台级根因与
   HV 许可的 teardown/握手（或 OEM 指引）后才能再谈成功启动。

NEXT_ACTION =
对 0xc980684 写拒绝做根因取证与修复方案评审（对照 09-29 reboot 与本次 kexec 两份串口捕获，
定位发起该写的客机路径；评估 tegra_hv/vcpu-yield 握手或 OEM 支持的交接机制），评审通过前不再执行第二次 kexec。
```

---

## 1. G4A 执行记录

| 步骤 | 结果 | 证据 |
|---|---|---|
| G4A-0 预检 | PASS — 6.1.119-rt45-prod-rt-tegra / root=/dev/vblkdev0 / KEXEC+KEXEC_FILE=y / R4+API active / kexec_loaded=0 | `08_g4_runtime/G4A_PRECHECK.txt` |
| G4A-1 暂存 | PASS — 6 文件入 `/tmp/thor-g4a/`，**目标机 sha256 与冻结清单逐字节一致** | `08_g4_runtime/G4A_STAGE_LOAD.txt` |
| G4A-2 kexec --load（单次） | PASS — `LOAD_RC=0`，`/sys/kernel/kexec_loaded=1` | 同上 |
| Console 就绪 | PASS — COM6 端到端活体校验（/dev/kmsg 标记实时捕获）；捕获脚本 WritesToSerial=0 | run_20261006_141723/COM6.bin |
| G4A-3 kexec --exec（单次，14:17:50） | **FAIL — 见 §2** | 捕获与哈希见 §3 |

安全约束遵守：只 LOAD/EXEC 各一次；未重试、未换参数；未 flash/bootburn/RCMBOOT/改 DTB/动 UFS。

## 2. 失败时间线（COM6 原始捕获摘录）

```
[103574.400556] G4_CONSOLE_LIVENESS_141736            (console 活体标记)
[103589.046002] G4A_EXEC_MARKER_141750                (sync 后 exec 边界标记)
GID 0: Unhandled access of size 4 for write.
Access size: 0x4 ; Fault IPA: 0xc980684 ; ESR_EL2: 0x9393004f
VM Error, VM ID 0x0 ; VM VCPU ID 0x2 ; Failed to handle data abort!
Tegra Report Error / Reporter ID 0x8200 / Error code 0x800f0000 / attr 0x20
[103593.03] [EPS]fatal error cpu:0..15 (×16) → SEH/Safetyservice fault records
[103795.46] INFO: task systemd:1 blocked for more than 120 seconds (journal/network/health.sh 同时)
[104037.16] 持续 hung-task（每 ~121s 一报，直至断电）
（无任何 6.8 内核输出：无 "Linux version"、无 earlycon、无 kexec 交接打印）
```

- 故障后机器状态：内核仍活、**用户态永久卡死**（SSH 死、SSH端口无应答；网络仅内核 ICMP 残留）。
- 分类（按方案 FAIL 类别最接近者）：**FAIL_KERNEL（交接失败的 kexec handoff）**；因新内核从未启动，
  方案中逐项 `uname/cmdline/dmesg/...` 的“失败机内证据”在 6.8 侧不可得，以**串口原始捕获 + 6.1 侧状态**替代（下表）。

## 3. 证据与哈希（08_g4_runtime/）

| 文件 | SHA256 |
|---|---|
| `console_capture/run_20261006_141723/COM6.bin`（全程：liveness→exec→故障→hung→断电→冷启动→登录） | 16c2372b6a16d5b829e56ad73528e5490da25ce0cb6bf1ca890bac6bd5c05545 |
| `g4a_fail_evidence/COM6_exec_capture.bin`（故障段快照） | 421341835608f425e1d6e28c2dcf322e33545b14fe490299d0e72a3aab0e0e74 |
| `g4a_fail_evidence/COM5_full_run_capture.bin`（物理恢复期间亦有数据） | 593cca1decbf52f770fcc9a101517917cd4434c4700e26f43456b04bfd39445f |
| `g4a_fail_evidence/G4A_FAILURE_BLOCK.txt` / `G4A_RECOVERY_BOOT_BLOCK.txt` | 文本切分（utf-8） |

## 4. 恢复（物理冷断电 → 6.1 Golden → 生产重建 → 验证）

1. **物理冷断电**（业主现场执行，14:35 前后）→ 冷启动走原 DRIVE boot chain → **Kernel 6.1 Golden**（横幅+多用户+登录提示全部捕获）。
2. 冷启动后发现**该机已知跨断电定制丢失现象**（与 2026-09-16 `/home` 丢失审计同现象，根因未明）：
   `/home/nvidia/.ssh`（密钥）、`/etc/sudoers.d` NOPASSWD、`/etc/systemd/network/10-thor-ai-enx.network`、
   `/etc/sysctl.d/99-z-thor-ai-hugepages.conf`（大页回退到 10240）、`/etc/systemd/system/thor-r4-*.service` **全部缺失**。
3. 重建（全部用车上既有母本/PC 侧持久化素材，无新造内容）：
   - 串口 console 登录（nvidia）→ 恢复公钥（Sep-16 已验收流程，0700/0600，指纹一致）；
   - 一次性密码恢复 NOPASSWD drop-in（`visudo -cf` parsed OK）；
   - 持久化重放：`R4_Persistence_20260912` 套件 → `10-thor-ai-enx.network`(.243/24+GW .1 metric10+DNS)、
     resolved/timesyncd drop-ins、大页 20992、`thor-ai-network-route.service`（全部按原安装器脚本执行并留备份）；
   - R4 单元：从 `_change_vision_promotion_20260923_160358/systemd/*.raw` 安装
     `thor-r4-v23`(+`20-logging.conf` drop-in)/`thor-r4-api`/`thor-r4-admin` + `thor-r4-stack-health.timer`（pre-gateway-v2 母本），
     `daemon-reload` + `systemd-analyze verify` + enable + start。
4. **恢复验证（G4A_POST_RECOVERY_SNAPSHOT，15:41:50）**：
   - 全部服务 active（v23/api/admin/watchdog timer/route/timesyncd）；
   - 监听：`18443+18444+18080 @192.0.2.222`、`59221 @127.0.0.1`；
   - 网络：enx=`192.0.2.222/24`、默认路由 `via 192.0.2.128`（proto static metric10 与 09-12 STATE 同构）、DNS=.1；
   - HugePages=20992；NTP synchronized=yes；`kexec_loaded=0`；
   - 探测：`/health/live`=200、`/health/ready`=200、admin 18444=200、`/props.modalities`={vision:true,video:true}；
   - v23 冷启动健康耗时 36s；模型 = Radix-NATIVE-FP8-319f741cce68-v1（entrypoint 自检 SHA 全过）。
5. **固化**：`/zeekr_data/thor-ai/production/scripts/COLD_BOOT_RESTORE.sh`（755，持久区）——
   供未来每次冷启动后一键重建（密钥/NOPASSWD/单元/网络/大页/起栈/验证）。

## 5. G4B 决策

按方案门规则（G4A 非 PASS 不得进入 G4B）+ “禁止连续重复 kexec”→ **G4B 未执行**；本报告为终点。

## 6. 结论与建议

- **G4 路线的 RAM-only kexec 在当前 DRIVE OS 7.0.3 平台被一个 EL2 层写拒绝卡住**，且与 09-29 reboot 失败同源——
  这不是 Kernel 6.8 构建或 initrd 的问题（预制件全链路已验证），而是**平台交接路径问题**。
- 建议路径（唯一下一动作）：两份捕获（09-29 + 本次）比对做根因；在得到 HV 许可的 teardown/交接方案（或 OEM 指引）前，
  **不进行第二次 kexec**，G5（OpenRM/GPU）保持冻结。
- 本机生产中已恢复；今后任何冷启动后请先跑 `COLD_BOOT_RESTORE.sh`（或按 README 串口路径）再对外提供服务。
