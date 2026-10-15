> **Historical frozen evidence**, not current live state. Sanitized network identifiers. Source SHA256 retained in manifest/SUPPLEMENTAL_EVIDENCE.json. Do not execute commands from this report on a vehicle.

# G4E2_K68B_SINGLE_VARIABLE_FINAL — k68b.dtb 单变量 HV/IVC/vblk 实验终报

- 日期: 2026-10-07 02:5x +08；执行: RUN1c（有效 RUN1）+ RUN2 双轮；全程 RAM-only
- 制品: Guard v3.1 `18a45999…` / kexec-tools 2.0.32 `86cb93d1…` / Image `482a7c41…` / initrd `18ce10ca…` / cmdline `d0db3209…` / **DBT 载荷 k68bz `3a3834d9ff4208e6e42e032b600be7e1abd6491ff44b71e2082a8cde6e3190ac`**
- 证据: `14_g4e2/g4e2_exec_run1c.log`、`g4e2_eval_run1c.log`、`g4e2_obs_run1c.log`；`g4e2_exec_run2.log`、`g4e2_eval_run2.log`、`g4e2_mark_run2.log`；装载/终门/恢复日志全套

```

DTB_SINGLE_VARIABLE      = PASS

G4C2_GUARD               = PASS
KERNEL68_ENTRY           = PASS

HV_IVC_DRIVER_BIND       = PASS
HVD                      = PASS
IVMK                     = PASS
IVC_59_80                = PASS
VBLK                     = PASS
ROOT_RO                  = PASS

G4E2_RUN1                = PASS
G4E2_RUN2                = PASS

G4E                      = PASS
READY_FOR_G5             = YES

PERSISTENT_WRITE         = ZERO

RECOVERY_TO_6P1          = PASS

CURRENT_BLOCKER = 无（本门闭环；6.1 Golden 保险原样保留）

NEXT_ACTION = G5 = OpenRM / GPU 10de:2b00 / 14SM Gate（冻结制品同谱系）

CONFIDENCE = HIGH
```

## 判定标准核对（方案 §二十一）

| 判据 | RUN1c | RUN2 | 证据 |
|---|---|---|---|
| Kernel 6.8 | PASS | PASS | `6.8.12-prod-g78272943bba3` ×2 |
| HV IVC driver bind | PASS | PASS | `/proc/device-tree/tegra_hv_ivc` + `/sys/bus/platform/{drivers,devices}` 均在 |
| HVD | PASS | PASS | "not initialized"/"get_hvd" 失败 = **0**；`tegra_hv_ivc: added ivc256…69…` 建表全谱 |
| IVMK | PASS | PASS | "ivmk is NULL" = **0** |
| IVC 59..80 | PASS | PASS | "Failed to reserve IVC" = **0**；`get config data from ivc #59..80`/`send config cmd` 实测通信 |
| vblk | PASS | PASS | `/dev/vblkdev0/1/6-12/30/33/34/37-40/60(+ctl/ffu)`；`/proc/partitions` 16 设备（容量表见 STORAGE_OBSERVATION） |
| root-ro | PASS | PASS | `/dev/vblkdev0 on /new_root type ext4 (ro,relatime)`；`/new_root/etc/os-release` = Ubuntu 24.04.1 LTS |

**双轮一致性**：同制品同命令，结果逐项一致（连装载基址 0x819f3000 / dtb 尺寸 226930 / vblk 时序 122-123s 均复现）⇒ §十八 重复性门 PASS。

## 载荷谱系（单变量证明）

```
k68.dtb (0d7a0bdd…)        原冻结（去 scratch 版；无 tegra_hv_ivc 节点）
k68b.dtb (5259c4c1…)       = k68 + root 级单节点 {compatible="nvidia,tegra_hv_ivc"; interrupt-parent=<0x01>; status="okay";}
k68bz.dtb (3a3834d9…)      = k68b + kaslr-seed 置 0（工具安全门要求"种子已消费"形态；nokaslr 下无运行影响）
```
- `G4E2_DTB_DIFF_FINAL.txt`：k68→k68b diff = 恰 6 行新增；k68b→k68bz diff = 恰 1 行（种子）。
- 运行时旁证：6.8 树 `pmc reg=48B/3 条 + reg-names "pmc wake misc"`（=k68 系签名，非 live 的 4 条含 scratch）⇒ 载荷确凿送达。

## 本轮新发现的两道装载机制门（必须记录）

1. **kexec-tools 2.0.32（Ubuntu build）arg 解析敏感**：`--dtb=` 仅在命令尾部带 `-d`（debug）的调用形态下实际生效（`dtb_user` 被嵌入；debug 行 `dtb: base …, size 36f72h (226930)`）；无 `-d` 时**静默回落到主内核当前树**（read_1st_dtb，live 树）且 LOAD_RC=0——这是 RUN1(首轮) 全程使用 live 树、节点从未生效的根因。
2. **候选 DTB 必须过 `setup_2nd_dtb` 的 kaslr-seed 安全门**：种子非零直接 `EINVAL`（RC=255）。冻 k68/k68b 携带 bootloader 种子（0x7c913a39…）⇒ 必须置零（k68bz）。

## 过程归档（两次无效轮次，按纪律不计）

- **run1a**（01:33）：装载未生效（`--dtb` 静默回落 live）→ 6.8 树无节点 → 六层中 L2 以下全 FAIL → 归类 `FAIL_DTB_DELIVERY`（装置缺陷，非假设证伪）。0xc980684=0、guard 正常。
- **run1b**（01:36）：tegrareset 恢复后**漏装 guard** 直接 exec → GUARD=0 → 0xc980684 复现 + hang（再次实证"无 guard→scratch 写→fault"因果）→ 归类 `FAIL_GUARD`（我方纪律失误）。恢复后修复流程：**终门必须独立会话且人工阅读后才允许 exec**。
- **RUN1c/RUN2**（02:09 / 02:44）：完整通过（见上表）。

## 恢复与生产回场（§十七）

- 每轮后 MCU `tegrareset x1` → 6.1 Golden 冷启动复检 → `COLD_BOOT_RESTORE.sh`：
  NOPASSWD ✓ / R4 单元安装+启动 ✓ / `v23 health OK after 36s` ✓ / 59221 端口 ✓ / HugePages 20992 ✓ / SSH pubkey(nvidia) 700-600 ✓ / llama-server 载入中（正常节奏）✓
- RECOVERY_TO_6P1 = PASS；6.1 Stage-0 保险原样保留。

## 纪律核对

```
A/B/C boot chain / UFS / QSPI / BCT/BRBCT/PCT / Hypervisor / fuse / OEM boot firmware = 零写入
kexec 次数 = 2 次有效（RUN1c/RUN2）+ 2 次无效轮（run1a 装载缺陷 / run1b 守卫缺装，均在纪律框架内单次发生、不连试）
唯一持久变化 = 无（全部暂存会话层；tegrareset 后归零）
```
