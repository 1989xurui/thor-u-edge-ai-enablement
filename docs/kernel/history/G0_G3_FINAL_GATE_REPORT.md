# G0_G3_FINAL_GATE_REPORT — THOR-U R39.2.1 GOS BOOT GATE

- 日期: 2026-10-06
- 任务: 证明「P3960 现有 DRIVE Boot/BPMP/PCT/Hypervisor + R39.2.1 Kernel 6.8 + tegra_hv/vblk + initrd」已准备到可安全进入一次 **RAM-only kexec** 启动测试
- 目标机: `nvidia@192.0.2.222`（Tegra264 / p3960-0010 / p3960-10-sw01 / DRIVE OS 7.0.3 GOS）
- 证据根目录: `E:\Thor64G_AI\THOR_U_R39_GOS_BOOT_GATE_20261006\`

---

```
G0 = PASS
G1 = PASS
G2 = PASS
G3 = PASS

CURRENT_BLOCKER =
无阻断项。G4 前置提示（非阻断，均为设计内残留）：
1) 构建工具链为 Ubuntu GCC 13.x（生产为 Buildroot 13.2.0）——仅影响复现精度，不影响本次门禁结论；
2) 运行时协议协商（VS_CONFIGINFO 握手/多设备并发）按方案设计留待 G4 实测裁决；
3) kexec 用户态工具为动态链接（libzstd/libz/libc），G4 阶段须在生产 rootfs 内运行（已记录依赖）。

READY_FOR_G4 =
YES

CONFIDENCE =
HIGH（G0–G3 全部验收项有文件级证据；运行时行为的最终判定归属 G4 本身）

RECOMMENDED_NEXT_ACTION =
召开 G4 评审并（在业主批准的维护窗口内）执行单次 RAM-only kexec：
  资产 = 05_initrd/out/g4_package/（Image-6.8.12-prod + initrd-minimal.img + p3960-live.dtb + cmdline 候选 A + kexec），
  全程只读挂根、不刷 UFS、不改 boot chain、不换 OpenRM。

  > **Amend 2026-10-06（G3.5）**：恢复口径修正 —— Primary rollback = 物理冷断电 → 原 DRIVE boot chain → 原 Kernel 6.1 Golden；
  > Bootburn `RCMBOOT -R` 状态 = **TOOL_NOT_AVAILABLE_YET**（本机无 bootburn/bootburn.py）。详见
  > `00_live_baseline/G0_RECOVERY_READINESS_AMENDMENT.md`；本 G3.5 版 G4 包改用 `05_initrd/out/g4_package_g35/`。
```

---

## 逐门证据摘要

### G0 — LIVE BASELINE + RECOVERY FREEZE = PASS

- 产出: `G0_LIVE_BASELINE.json`（2025 文件证据索引）、`G0_MODULE_MANIFEST.tsv`（11 模块闭包：sha256/modinfo/readelf/依赖）、`G0_VBLK_MAP.json`（19 设备 + DT 存储节点 + cmdline 角色）、`G0_DEVICE_TREE/`（fdt.raw + live-p3960.dts + 原始树 tar + 内容校验）、`G0_RECOVERY_READINESS.md`。
- DT 必含项逐一命中：`p3960-0010`×2、`p3960-10-sw01`×2、`nvidia,tegra-hv-storage`×17、`tegra_virt_storage` 节点×19、`hyp/ufshci/bpmp/chosen/memory` 全在；root compatible = `nvidia,p3960 nvidia,tegra264`。
- kexec 能力: `CONFIG_KEXEC=y / CONFIG_KEXEC_FILE=y / CONFIG_RELOCATABLE=y`（/proc/config.gz 实测）。
- vblk 映射（节选）: vblkdev0=/(UUID 75cd2003…)·vblkdev30=/mnt/rw_overlay·vblkdev33=/mnt/nvlog_logs·vblkdev60=du_ctx·vblkdev6/7/10/11/12 ↔ zeekr_plt/pilot/hdmap/map/data。
- 车机全只读（sudo -n 仅用于 root-only 模块读取）；零持久化更改；生产服务未受影响。

### G1 — R39.2.1 / T264 SOURCE FREEZE = PASS

- `HV_SOURCE = FOUND`；`VBLK_SOURCE = FOUND`；`T264_SUPPORT = YES`；`KERNEL_TARGET = 6.8.12`。
- 仓库锁定（commit 级）: kernel `78272943bba3`（l4t-r39.2.1-Ubuntu-nvidia-tegra-6.8.0-1021.21）；nv-oot `e71bacb7c611`（l4t/l4t-r39.2.1）；t264-public-dts `a7ee11104329`。
- 关键源码确证：kernel `drivers/virt/tegra/{tegra_hv.c,tegra_hv_ivc.c}`；nv-oot `drivers/block/tegra_virt_storage/*`（vblk 3090 行 + `tegra_virt_storage_spec.h` 490 行协议规格）、`tegra_oops_virt_storage/`、`mtd/devices/tegra_hv_mtd.c`、`virt/tegra/` 全套；DT bindings 文档在树内。
- 产出: `G1_SOURCE_LOCK.json`、`G1_SOURCE_TREE_*.txt`、`G1_HV_VBLK_SOURCE_AUDIT.md`、`G1_TOOLCHAIN_REPORT.md`、`G1_PROTOCOL_SPEC_EXCERPT.txt`、`G1_VBLK_PROP_PARSING.txt`、`G1_COMPATIBLE_STRINGS.txt`。

### G2 — KERNEL 6.8 + HV/VBLK OFFLINE BUILD = PASS

- 配置: tegra_prod_defconfig + GOS 片段 + olddefconfig；delta 仅 3 处（PCI_TEGRA/VIRTIO_BLK/TEGRA_IOMMU_SMMU；其余目标项基线已 `=y`）。
- 全量构建: **Image 22,692,352 B / 0 error / 137 内核模块**，kernelrelease `6.8.12-prod-g78272943bba3`。
- 模块: `tegra_vblk.ko`(342,872 B) + mtd/oops/pm_ctl/vcpu_yield/ivc-cdev/mempool 全 PASS；HV 核心 builtin PASS + 官方 dummy `tegra_hv.ko` PASS（真实 HV 模块与 builtin 互斥——modpost `exported twice` 实证 + 官方 `NV_OOT_TEGRA_HV_SKIP_BUILD=y`）。
- 绑定识别: 新 `tegra_vblk.ko` OF alias `of:N*T*Cnvidia,tegra-hv-storage` 命中 live DT；协议矩阵（compatible/IVC/mempool/instance/read-only/ABI）静态 PASS。
- 排障固化: nv-oot conftest 生成必须满足 `conftest.sh` 自带 `cd $SCRIPTDIR` 的路径约定（详见 G2 报告 §2.1）——否则产生全量假判决。

### G3 — BOOTABLE INITRD BUILD = PASS（静态）

- `initrd-minimal.img` 1,125,132 B（sha `e1caed96…`）/ `initrd-debug.img` 1,280,952 B（sha `435aae3e…`）。
- 依赖自动解析（depmod -b…），minimal=vblk 单模块；debug=+hv 家族 6 模块；busybox 1.37.0 static（276 applets）。
- init 流程按方案 §G3.2 五阶段实现（30s vblk 等待、禁写 fsck 语义、只读挂根、失败入 debug shell）；`sh -n` 语法 PASS（qemu 验证）。
- lsinitramfs 等价静态检查 PASS（环境无 lsinitramfs，采用 `cpio -t`，清单留档）。
- 已知替代：busybox static 无 `blkid` applet（不影响启动流；调试替代 dmesg//proc/mounts）。
- **kexec 未执行（零次）**；G4 包已就绪：`05_initrd/out/g4_package/`。

## 安全与“顺便做”复核

- 全程未 flash / 未 bootburn / 未 RCMBOOT / 未 reboot / 未 kexec / 未改 DTB / 未动 BCT/PCT/BPMP / 未动 UFS / 未停生产服务 / 未改模型。
- 未顺手执行 OpenRM / CUDA13 / TensorRT / Edge-LLM / 27B 等任何越界项。
- 早期停止规则（方案第四节）逐项检查：无一触发。

## 若进入 G4（照抄方案约束）

- G4 = kexec RAM-only Kernel6.8 boot；仍然：不刷 UFS、不改 boot chain、不换 OpenRM。
- 首轮建议：候选 A cmdline + initrd-minimal；失败则 initrd-debug（telnetd）定位 HV/IVC 与 vblk 的分界；再失败回到 G0 证据与 RCMBOOT -R 待命。
