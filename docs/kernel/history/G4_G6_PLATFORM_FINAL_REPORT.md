# G4_G6_PLATFORM_FINAL_REPORT — P3960 Thor-U 平台底层终报（G4→G6）

- 生成中（G4 已收口；G5/G6 段随进度填充）；字段格式遵循总提示词 §28
- 日期: 2026-10-07；执行根: `THOR_U_R39_GOS_BOOT_GATE_20261006/`

```

G4E_RUN1 = PASS
G4E_RUN2 = PASS

G4_REPEATABILITY = PASS
G4 = PASS

STORAGE_TOPOLOGY = COMPLETE（G4_STORAGE_TOPOLOGY.md；lsblk 原生输出延后 G5 顺带补采）


G5_PCI_GPU = _PENDING_
G5_OPENRM = _PENDING_
G5_GSP = _PENDING_

G5_GPC = _PENDING_
G5_TPC = _PENDING_
G5_SM = _PENDING_

G5_UMA = _PENDING_
G5_GPU_CLOCK = _PENDING_
G5_BASIC_COMPUTE = _PENDING_

G5 = _PENDING_


G6_CUINIT = _PENDING_
G6_DEVICE_COUNT = _PENDING_
G6_RUNTIME = _PENDING_

G6_UNIFIED_MEMORY = _PENDING_
G6_GEMM = _PENDING_
G6_CUTLASS = _PENDING_
G6_CUTE = _PENDING_
G6_NVFP4 = _PENDING_

G6 = _PENDING_

READY_FOR_G7 = _PENDING_

6P1_GOLDEN = HEALTHY

PERSISTENT_BOOT_MODIFICATION = ZERO

CURRENT_BLOCKER = G5-A：R39.2.1 包解包与 OpenRM 制品盘点进行中

NEXT_ACTION = 完成 R39.2.1 解包 → 冻结 OpenRM 版本锁（G5_OPENRM_VERSION_LOCK.json）

CONFIDENCE = HIGH（G4 段）
```

## G4 段摘要（已收口）

- **G4E_RUN1/RUN2 双轮 PASS**（2026-10-07 02:09 / 02:44，同制品 6 件 sha 冻结一致）：
  GUARD_HIT r=8001 / 0xc980684=0 / 6.8.12 / tegra_hv_ivc bind / HVD/IVMK 零错误 /
  IVC 59..80 通信 / `/dev/vblkdev0..60` / `/new_root ext4 (ro,relatime)` + os-release 可读。
- 载荷冻结谱系：k68(`0d7a0bdd`) → k68b(`5259c4c1`) → **k68bz(`3a3834d9…`)**；装载机制门：`--dtb` 需带 `-d` 才生效 + kaslr-seed 置零安全门（详见 `07_reports/G4E2_K68B_SINGLE_VARIABLE_FINAL.md`）。
- G4 核心制品自此冻结（6.1→Guard→kexec→6.8→HV/IVC/vblk/rootfs），除明确回归不再研究。

## G5 段（进行中）

- 制品源就位：`Jetson_Linux_R39.2.1_aarch64.tbz2`（1.2GB，本地，sha 核验件在案）
- 待盘点：nv_tegra/l4t_deb_packages/*openrm*、GSP firmware、kernel-open 源、nvgpu 隔离面

## G6 段（未开始）

- 待 G5 PASS 后进入（CUDA 13.x 版本锁 → Driver API → Runtime → UMA → 算子 → CUTLASS/CuTe → 稳定性）
