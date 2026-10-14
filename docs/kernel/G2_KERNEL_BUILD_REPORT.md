# G2 KERNEL BUILD REPORT — Kernel 6.8 + HV/vblk 离线构建验证

- 日期: 2026-10-06
- 判定: **G2 = PASS**（构建与静态绑定层；运行时协议协商留 G4）
- 构建主机: WSL2 Ubuntu 24.04.4（12 vCPU / 859GB free / ext4），工具链 aarch64-linux-gnu-gcc 13（详见 G1_TOOLCHAIN_REPORT.md）

## 1. 配置方法（G2.1）

- 基线: `make ARCH=arm64 O=kbuild tegra_prod_defconfig`（R39.2.1 生产风格 defconfig，LOCALVERSION="-prod"）
- 叠加 P3960 6.1 GOS 必要选项（`scripts/config` 片段）：
  `TEGRA_HV_DRIVER / TEGRA_IVC / VIRTIO / VIRTIO_BLK / SCSI_UFSHCD(_PLATFORM) / EXT4_FS / PCI_TEGRA / TEGRA_BPMP / TEGRA_IOMMU_SMMU / MODULES` → `olddefconfig`
- **G2_CONFIG_DELTA.diff（29 行，仅 3 处实际变化）**：`PCI_TEGRA=y`、`VIRTIO_BLK=y`、`TEGRA_IOMMU_SMMU=y`；
  其余（TEGRA_HV_DRIVER / TEGRA_IVC / UFSHCD / EXT4_FS / TEGRA_BPMP / MODULES）在 tegra_prod_defconfig 基线中已为 `=y`（Kconfig default / ARCH_TEGRA 依赖满足）。
- 结果核验（kbuild/.config）：全部目标选项 `=y`；`CONFIG_LOCALVERSION="-prod"`；kernelrelease = **6.8.12-prod-g78272943bba3**。

## 2. 第一轮 HV/vblk 编译（G2.2）

| 目标 | 结果 | 证据 |
|---|---|---|
| kernel `drivers/virt/tegra/`（tegra_hv.o + tegra_hv_ivc.o，builtin） | **PASS**（仅 1 个无害 warning：`ivc_dump defined but not used`） | kbuild/hv_smoke.log |
| nv-oot `tegra_vblk.ko`（6 源文件组合） | **PASS** 342,872 B | oot4_vblk.log |
| nv-oot `tegra_hv_mtd.ko` | **PASS** 88,952 B | oot4_mtd.log |
| nv-oot `tegra_hv_vblk_oops.ko` | **PASS** 92,232 B | oot4_oops.log |
| nv-oot `tegra_hv_pm_ctl.ko` / `tegra_hv_vcpu_yield.ko` / `ivc-cdev.ko` / `userspace_ivc_mempool.ko` | **PASS**（105,912 / 79,600 / 84,760 / 72,376 B） | oot5_virt.log |
| nv-oot `tegra_hv.ko`（真实 HV 实现，模块形态） | **按官方设计排除**（见 §3） | modpost 证据 |

无 unresolved symbol（modpost 干净）；依赖链由 builtin 内核导出满足（新 .ko 的 `depends` 为空即此含义）。

### 2.1 conftest 机制排障（关键操作知识，已固化）

nv-oot 驱动依赖 `scripts/conftest/` 生成的 `nvidia/conftest.h`。构建中发现并解决了两个环境陷阱：

1. `conftest.sh` 第 9 行自带 `cd $SCRIPTDIR` → 编译测试的 `#include "conftest/headers.h"` 只能在**脚本旁目录**解析；
   将生成物放到独立 obj 目录会导致 **全部函数/类型测试假性失败**（连锁 %undef/%define 假判决）。
2. 正确生成命令（在本 clone 中已执行）：
   `make -f scripts/conftest/Makefile src=scripts/conftest obj=scripts/conftest NV_KERNEL_SOURCES=<kernel> NV_KERNEL_OUTPUT=<kbuild> NV_KERNEL_MODULES="tegra_vblk ..." ARCH=arm64 CC=aarch64-linux-gnu-gcc all`
   并将 `conftest.h` 模板放至 `scripts/conftest/nvidia/conftest.h`。
3. 修正后关键判定（与 6.8.12 事实手工复核一致）：
   `OPEN_HAS_GENDISK_ARG`✓`#define`、`RELEASE_HAS_NO_MODE_ARG`✓、`CLASS_CREATE_HAS_NO_OWNER_ARG`✓、`TEGRA_IVC_STRUCT_HAS_IOSYS_MAP`✓、
   `QUEUE_LIMITS_STRUCT_HAS_FEATURES` = `#undef`（**正确**：6.8 的 `struct queue_limits` 无 features 字段 → 派生宏 `NV_BLOCK_USE_QUEUE_LIMITS_SET` 按要求关闭）。

## 3. tegra_hv 形态判定（官方等价性证明）

- 生产 6.1 与 R39 官方配置同构：**HV 核心 builtin**（`CONFIG_TEGRA_HV_DRIVER=y`）+ OOT 侧模块化组件。
- `NV_OOT_TEGRA_HV_SKIP_BUILD=y` 存在于 `configs/Makefile.config.noble`（本内核对应 flavor）与 nvmainline/fuzzing/oot 配置 → 官方在 noble 上**不构建**真实 HV 模块。
- 实证：不 skip 时 modpost 报 `'tegra_hv_ivc_*' exported twice. Previous export was in vmlinux`（17 个符号）→ 与 builtin 共存**架构性禁止**。
- 按官方方式（skip=y）构建 → **PASS**：`tegra_hv.ko`（dummy 变体 26,880 B）+ pm_ctl/vcpu_yield/ivc-cdev/mempool 全 PASS。

## 4. 全量 Kernel 构建（G2.4）

- `make -j12 Image modules dtbs`：**PASS**，0 errors，5 warnings；耗时 ≈10 分钟。
- 产物：`arch/arm64/boot/Image` = 22,692,352 B（sha256 `587cd14c5bb6a4a0d412cb9ff15db0da3cdca71d874fb98d8e19918d63af240a`）；内核模块 137 个。
- 无 T4000 DTB 产出目标；目标仍是 P3960 现网 DT + 6.8 绑定兼容（见 §5）。

## 5. P3960 live DT 识别验证（G2 验收第 5 项）

新构建的 `tegra_vblk.ko` modinfo：

```
alias: of:N*T*Cnvidia,tegra-hv-storageC*
alias: of:N*T*Cnvidia,tegra-hv-storage
vermagic: 6.8.12-prod-g78272943bba3 SMP preempt mod_unload modversions aarch64
depends:            (空 — 由 builtin 导出满足)
```

`tegra_hv_pm_ctl.ko` → `of:N*T*Cnvidia,tegra-hv-pm-ctl`；`tegra_hv_vcpu_yield.ko` → `of:N*T*Cnvidia,tegra-hv-vcpu-yield`
——与 live DT 的 17 处 `nvidia,tegra-hv-storage` 等节点逐一对应（完整矩阵见 `04_hv_vblk/G2_HV_PROTOCOL_MATRIX.md`）。

## 6. G2 验收对照

| 验收项 | 结果 |
|---|---|
| Kernel Image build PASS | ✅ |
| tegra_hv.ko PASS | ✅（builtin 核心 PASS + 官方 dummy 模块 PASS；真实模块与 builtin 互斥有据） |
| tegra_vblk.ko PASS | ✅ |
| no unresolved symbol | ✅ |
| dependency chain complete | ✅（modpost 干净；`depends:` 空=builtin 提供） |
| P3960 live DT properties 被新 driver 识别 | ✅（OF alias 命中 + 协议矩阵） |

## 7. 制品与哈希

见 `03_kernel68/G2_ARTIFACT_SHA256SUMS.txt`（Image、.config、8 个 .ko）。
依赖关系：`03_kernel68/G2_MODULE_DEPENDENCY.json`。

## 8. 限制与风险（G4 前请注意）

1. 工具链为 Ubuntu GCC 13.x（生产为 Buildroot 13.2.0）——G2/G3 验证门可接受，正式复现建议官方工具链。
2. 本轮构建 **未启用** `CONFIG_MODULE_SIG_ALL`（生产为 sha512 签名）；G4 载入的是“新内核+新模块”自洽组合，不涉及旧签名校验。
3. 非 RT 内核（PREEMPT），GOS 启动门不依赖 RT。
4. 未包含 nvgpu/显示等 GPU 栈（按方案禁区）。
5. 运行时协议协商（VS_CONFIGINFO 握手、多设备并发）必须由 G4 实测裁决——静态证据充分但非运行时证明。
