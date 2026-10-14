# G3_5_PRE_G4_HARDENING_REPORT — THOR-U R39.2.1

- 日期: 2026-10-06
- 范围: 对 G4 RAM-only kexec 包做执行前最后一次加固；**只改离线构建产物**
- 本任务**绝对未执行 G4**：无 kexec / reboot / flash / bootburn / RCMBOOT / UFS 写 / BCT・PCT・BPMP 修改 / 车机 DTB 修改 / R4 停机；车机零操作（本阶段全部为本地离线工作）

---

```
G0 = PASS
G1 = PASS
G2 = PASS
G3 = PASS

G3.5_MODULE_SIGNATURE = PASS
G3.5_USB_NETWORK      = PASS
G3.5_INITRD_G4A       = PASS
G3.5_CMDLINE_AUDIT    = PASS
G3.5_PACKAGE_HASH     = PASS

READY_FOR_G4_EXECUTION = YES

CURRENT_BLOCKER =
无阻断项。三项须知（均已写入文档、不阻断）：
1) 恢复口径已修正 —— Primary rollback = 物理冷断电 → 原 DRIVE boot chain → Kernel 6.1 Golden；
   Bootburn RCMBOOT -R = TOOL_NOT_AVAILABLE_YET（本机无 bootburn），**不得**计入当前恢复能力；
2) 运行时协议协商（VS_CONFIGINFO 握手等）按设计由 G4A 实测裁决（本包即为其准备）；
3) G4A 网络为 Secondary 调试面（USB RTL8153 静态 IP），网络失败不影响 G4A 判定。

G4_PACKAGE =
05_initrd/out/g4_package_g35/

NEXT_ACTION =
在业主批准的维护窗口内，用 g4_package_g35 执行一次 RAM-only G4A kexec
（Image-6.8.12-prod-g35 + initrd-g4a-minimal.img + p3960-live.dtb + cmdline-g4a.txt；
串口 console 为主通道；机器将驻留 initrd shell 并打印 G4A_BOOT_GATE_PASS/FAIL 与 10 项证据）。
```

---

## 1. 已审核发现的两个问题的修正结果

### 1.1 MODULE_SIG_FORCE（G3.5_MODULE_SIGNATURE = PASS）

| 项 | 修正前（G3 包） | 修正后（g35 包） |
|---|---|---|
| CONFIG_MODULE_SIG_FORCE | **=y**（风险：未签名 tegra_vblk.ko 会被拒载） | **`# ... is not set`**（artifact config 第 757 行实证） |
| CONFIG_MODULE_SIG / SIG_ALL / SIG_KEY | =y / not set / ""（保留不动） | =y / not set / ""（不建立正式签名体系） |

- 处理：`scripts/config -d MODULE_SIG_FORCE` + `olddefconfig` + 全量重建（Image/modules/modpost）。
- 验证：config delta 596 行已存档 `03_kernel68/G3_5_CONFIG_DELTA.diff`；`grep -n MODULE_SIG_FORCE` → `# CONFIG_MODULE_SIG_FORCE is not set`；
  `tegra_vblk.ko` vermagic `6.8.12-prod-g78272943bba3 SMP preempt mod_unload modversions aarch64`、**无 unresolved symbols**（modpost 干净）。

### 1.2 管理网络驱动缺失（G3.5_USB_NETWORK = PASS）

生产管理口实证（G0 冻结 lsmod）：`enx00e04c680f84` ← `r8152`(+`r8153_ecm`,`cdc_ether`,`usbnet`)；live DT 主机节点 `usb@a80aa10000` = `nvidia,tegra264-xusb`（status okay），padctl = `nvidia,tegra264-xusb-padctl`。

按 R39.2.1 Kconfig 用 `scripts/config` + `olddefconfig` 自动解决依赖（未硬写）：

```
CONFIG_USB=y
CONFIG_USB_XHCI_HCD=y
CONFIG_USB_XHCI_TEGRA=y        （match 表含 nvidia,tegra264-xusb，xhci-tegra.c 已源证）
CONFIG_USB_RTL8152=y
CONFIG_USB_RTL8153_ECM=y       （生产 r8153_ecm 路径，独立符号）
CONFIG_USB_USBNET=y
CONFIG_USB_NET_CDCETHER=y
CONFIG_PHY_TEGRA_XUSB=y        （padctl 支持 nvidia,tegra264-xusb-padctl，原本已 =y）
```

上述全部为 **builtin**（=y），已进入 Image（Image 增大 753,664 B，sha `482a7c41…`）。

## 2. G4A initrd 逻辑修正（G3.5_INITRD_G4A = PASS）

- 新流程（`initrd_src/init-g4a`）：Kernel6.8 → HV/IVC → tegra_vblk → `/dev/vblkdev0` → `mount -t ext4 -o ro` → 验证 root 内容（读 `/new_root/etc/os-release`）→ 打印 **10 项证据** → 判定 → **驻留调试 shell**。
- 自动检查项（全部上屏并在 `/tmp/g4a_evidence.txt` 留档）：①uname ②cmdline ③hv/ivc dmesg ④vblk dmesg ⑤vblkdev0 存在 ⑥size ⑦ro 挂载 ⑧/proc/mounts ro ⑨os-release ⑩`G4A_BOOT_GATE_PASS`（失败则 `G4A_BOOT_GATE_FAIL`+诊断）。
- **禁止项实证**：包内 `/init` token 扫描 `switch_root|/sbin/init` = **0 命中**；无 rw_overlay/usr_fs 处理；无 fsck 调用（零写盘行为）；shell 退出只重生成 shell，**永不自动关机/重启**。
- 调试网络（仅 debug 版）：接口存在时静态 `192.0.2.222/24` + telnetd；**网络失败不判 FAIL**（console=Primary，USB-Eth=Secondary）。
- 静态复验：cpio 可展开（68/74 成员）；`sh -n`（qemu-aarch64+busybox 1.37.0 static）= **PASS**；`modules.dep` 与 `tegra_vblk.ko`（正确 version 路径 `lib/modules/6.8.12-prod-g78272943bba3/extra/`）均在；debug 含 hv 家族 7 模块；busybox 276 applets 含 ip/ifconfig/udhcpc/telnetd/dmesg/lsmod/modprobe/mount/cat/sh/tee/setsid。

## 3. cmdline 重新审核（G3.5_CMDLINE_AUDIT = PASS）

- 产出 `05_initrd/G3_5_CMDLINE_AUDIT.md`（含逐参数 parser 取证与保留/删除理由）与 `cmdline-g4a.txt`（Candidate A）。
- 关键红线遵守：**未改名** —— `tegra_keep_boot_clocks` 保持原名原值（R39 全树无 parser；不改写为 `keep_boot_clocks=1`）；同类（`aurixfw/board_name/pct/pct_variant/tegraid/gpt_sector/sdhci_tegra.en_boot_part_access/disable_android_paranoid_network/verity/earlyprintk`）一律保持或按案删除。
- 与生产差异仅：删 5 个 userspace-init 专用参数（`usr_fs/usr_fs2/rw_overlay/nvlog/du_ctx`，G4A 明确禁止进入生产 userspace）+ 调试抬升（loglevel 4→7、log_buf_len 1M→4M）。
- 源证保留项：`console=ttyUTC0`（SERIAL_TEGRA_TCU_CONSOLE=y）、`earlycon=tegra_utc,…`（tegra-utc.c OF_EARLYCON_DECLARE）、`gpt`（efi.c `__setup`）、`nokaslr`（arm64 kaslr_early）、`clk_ignore_unused/pci=…/iomem=relaxed/debugfs=on`（core 参数）。

## 4. 包哈希冻结（G3.5_PACKAGE_HASH = PASS）

`05_initrd/out/g4_package_g35/`（全部 size/SHA256/role/commit 见包内 `G3_5_PACKAGE_MANIFEST.json` 与 `SHA256SUMS.txt`）：

| 文件 | size | SHA256（前 16） |
|---|---|---|
| Image-6.8.12-prod-g35 | 23,446,016 | `482a7c419b6903fc…` |
| initrd-g4a-minimal.img | 1,125,592 | `18ce10caeb55a033…` |
| initrd-g4a-debug.img | 1,280,940 | `8479c4c0c9e3fc0e…` |
| cmdline-g4a.txt | 471 | `d0db32095f3d5254…` |
| p3960-live.dtb | 240,612 | `ca2f914bbfdbc622…` |
| tegra_vblk.ko | 342,872 | `739e0fb01baebaa9…` |
| kexec (2.0.32 aarch64) | 199,200 | `86cb93d12fa37582…` |
| kernel-6.8.12-prod-g35.config | 185,960 | `3df259fa1f0be026…` |

- 旧 G3 包（`g4_package/`）**逐字节未动**（复验 initrd-minimal.img 仍为 `e1caed96…`）。
- kernelrelease 保持 `6.8.12-prod-g78272943bba3`（`-g35` 仅为制品标签；确保 kernel 与 module vermagic 一致）。
- 证据修正（2025/2075）：全库复核**不存在 "2075" 引用**；现行报告与 `G0_LIVE_BASELINE.json` 均为 **2025** 条证据索引，无需替换。
- Recovery 表述修正：见 `00_live_baseline/G0_RECOVERY_READINESS_AMENDMENT.md`；`07_reports/G0_G3_FINAL_GATE_REPORT.md` 对应句已同步 amend。

## 5. READY_FOR_G4_EXECUTION = YES 必要条件核对

| 条件 | 证据 | 结果 |
|---|---|---|
| MODULE_SIG_FORCE=n | g35 config 第 757 行 | ✅ |
| tegra_vblk 可加载条件完整 | vermagic 匹配 + alias `nvidia,tegra-hv-storage` + 无 unresolved + 未签名可载 | ✅ |
| USB RTL8153 管理链已进入 Kernel | 7 个 CONFIG 全 =y（builtin） | ✅ |
| 串口 console 保留 | SERIAL_TEGRA_TCU(_CONSOLE)=y + cmdline `console=ttyUTC0,115200` | ✅ |
| initrd 第一轮不 switch_root | token 扫描 0 命中 + 驻留 shell 设计 | ✅ |
| vblk root 只读挂载逻辑完整 | init-g4a 全流程 + 10 项证据 + FAIL 诊断 | ✅ |
| 新 package SHA256 全部核对 | SHA256SUMS.txt（8 文件） | ✅ |
| 旧 Golden/boot/UFS 零修改 | 本阶段车机零操作；旧包未覆盖 | ✅ |

**边界声明**：本任务终点即加固包生成完成；执行 kexec 的动作属于 G4A，本轮未执行、不得由本任务自行执行。
