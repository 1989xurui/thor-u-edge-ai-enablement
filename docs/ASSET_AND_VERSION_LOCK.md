# 精确资产/版本锁 + 磁盘与 UMA 内存预算

所有数值来自历史冻结记录（2026-09 至 2026-10）；不代表当前设备 live 状态。

**新增来源溯源入口**：[SOURCE_MAP.md](SOURCE_MAP.md) → [SOURCE_MAP_FILES.tsv](../manifest/SOURCE_MAP_FILES.tsv)（110 个公开文件精确来源）；厂商/权重与实际版本锁定仍按本文件执行。

## 1. 完整硬件与软件锁

| 组件 | 历史锁定身份 | 实验边界 |
|---|---|---|
| 主板 | DRIVE Thor T264 / p3960-0010，14 SM，64GB UMA | 不适用于公开 Jetson Thor P3834 板卡 |
| OEM Guest | DriveOS 7.0.3.0-40740537 / Ubuntu 24.04.1 | Golden 原系统受保护 |
| OEM Kernel | 6.1.119-rt45-prod-rt-tegra / PREEMPT_RT | 不应覆盖 |
| OEM CUDA/TRT | CUDA12.8，TensorRT 10.10.10.3 | 与 6.8 实验独立 |
| 实验 Kernel | 6.8.12-prod-g78272943bba3 | A1 RAM/kexec 历史单会话 |
| Kernel commit | 78272943bba3a47e633b28963b0cda60de503500 | 精确构建输入 |
| G35 Kernel config SHA | 3df259fa1f0be026af15e15e5133eb609a1e3e47f663313bc01b20afafe5b50b | ABI 符号历史 13943/13943 |
| NVIDIA GPU | R39.2.1 NvGPU 595.78 / UMD 同批次 | A1 RAM 基础计算 |
| CUDA U2 | nvcc、cudart13.2.86、Driver API 13020 | SM110 基础数值 PASS |
| TensorRT | 10.16.2.10 与 10.16.0.72 各出现在不同实验 | 不能混作单个已验证二进制 |
| Edge-LLM | v0.11.0、源 commit 95515c2f87fba8982db5a519f9022277667b3cc9 | 原生 8K 单项测试 |
| Edge 安装 Wheel revision | 74f8732a7e8d1377e34471ad2652988346f18813 | 与源码 commit 不同 |
| 唯一 NVFP4 模型 | nvidia/Qwen3.8-27B-NVFP4@fed99d815f4e8c7c616dd3dd6780076e26d5fb61 | 固定 27B checkpoint/Tokenizer |
| Kernel GPU PCI | 10de:2b00 / SM11.0 | 14 SM 实机观测 |

## 2. 模型与磁盘占用

- NVFP4 27B 权重三分片实际大小：9,965,652,544 + 9,985,757,064 + 1,970,287,672 = 21,921,697,280 bytes ≈20.42 GiB。
- 一份全长 TensorRT Engine 历史为 17,599,751,492 bytes ≈16.39 GiB；权重+Engine 同盘约36.81GiB。Draft、插件、压缩包、旧引擎和 ONNX/编译中间物须另计。
- 官方 Edge-LLM 源码路径指出构建期间 ONNX 与引擎约需 20–50GB 磁盘，具体取决于版本和模型；本实验多套 Engine 可能需要更高上限。
- 仓库只上传脚本、原创代码、静态/测试报告、SHA，不上传上述权重或 Engine；Git 包大小不能用于估计车机可运行的内存。

## 3. 车机 UMA 占用预算

- Linux 可用内存历史约 58 GiB，GPU 和 CPU 同属统一内存，不能把 GPU 剩余与 RAM 剩余简单相加。
- 8K 冻结一次的 MemAvailable 最低约 31.859 GiB：相对 58 GiB，整机占用约 26 GiB，不是单模型显存。
- 200K 诊断曾最小 MemAvailable 15.747 GiB：同样口径约 42 GiB 使用量，负载与缓存条件不同。
- 强制安全线：MemAvailable ≥5GiB、GPU 可用池 ≥2GiB、Tj <95°C、目标持久空间空闲 ≥12 GiB。Engine/长序列和多实例应额外预算。
- 官方推理最低可用设备内存 ≥模型大小+2GB，但 KV、Draft、并发、序列长度等都增加内存开销，这不是性能或稳定性保证。

## 4. 真正需要另行合法取得的文件

| 阶段 | 不在 GitHub 内的必需实件 | 缺失导致什么结果 |
|---|---|---|
| 6.1 Golden | 完整原厂 boot、固件、板级镜像及恢复手段 | 不能保证回退 |
| 6.8 | Kernel Image + DTB + initrd + cmdline、完整源树与工具链 | 无法独立部署 6.8 |
| 冷启动/双系统 | OEM host-only board config、boot slot、签名/authorized tool 和真实物理通路 | 不能新增永久启动项 |
| R39 GPU | 完整 R39 OOT/UMD/DRM/host1x/NvGPU/firmware 实制品 | 无法重建完整 GPU |
| CUDA | 同批次 595.78 libcuda、CUDA13.2 U2 用户库 | CUDA ABI 不可验证 |
| Edge | 对应 10.16.x TensorRT / Edge wheel / CuTe/SM110 plugin | Engine 不可资格化 |
| 27B | 精确原 NVFP4 模型权重/Tokenizer 和 Target/Draft Engine | 不能直接推理 |

GitHub 的完整方案不应依赖分享私钥、签名伪造、未授权 SDK redistribution。完整许可证、下载链接与 sha256 应人工登记到受控离线物料表。

## 5. 本机来源目录映射

- D:\Thor64G\THOR_U_A1_NVGPU_R39_20261013 ：历史 Kernel/NvGPU/CUDA。
- E:\Thor64G_AI\THOR_U_R39_GOS_BOOT_GATE_20261006 ：G0-G5 启动/HV/IVC/RCM。
- D:\Thor64G\THOR_NVIDIA_NVFP4_20261013 ：TensorRT/Edge/27B。
- E:\Thor64G_Backup\GoldenBoard_2026-09-01 ：原 6.1 Golden。
- D:\Thor64G\GitHub_Export\thor-u-edge-ai-enablement ：本 Git 仓库。
- E:\Thor64G_AI\R4\Host_Assets ：旧 R4 的主归档，部分 D 路径只是 Junction，本项目不重复复制。

**注意**：WSL VHDX、原始磁盘和专有二进制不是源码交付；源码必须按其原 Git commit、文件权限和补丁关系恢复。

## 6. 可信供应链 Checklist

每个离线制品至少登记源 URL/厂商、license、下载时间、目标架构、Git commit/tag、文件 SHA、toolchain、ABI/SONAME、是否二次构建、实机结果及与 Golden 的差异。缺任何一项则证据为 PARTIAL，不能报完全可重建。
