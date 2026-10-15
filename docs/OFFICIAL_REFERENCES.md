# NVIDIA 官方文档 vs 本机实验工程：可靠参考清单

下载入口、PyPI ARM64 wheel、原始 SHA 和完整离线复现流程另见 [DOWNLOAD_AND_REPRODUCE.md](DOWNLOAD_AND_REPRODUCE.md) 及 [DOWNLOAD_LOCK.json](../manifest/DOWNLOAD_LOCK.json)；本工程的原创 MIT 授权不覆盖 NVIDIA/DRIVE/模型第三方许可。

链接及解释复核日期：2026-10-15。外部文档可能更新，应按链接内版本、发布日期和本仓实际制品核对，不把当前 main 文档的新增功能自动追溯到旧 wheel。

## 0. 三份本机研发项目与上游如何对应？

请看 [SOURCE_MAP.md](SOURCE_MAP.md) 的公开目录映射与 [110 文件 TSV](../manifest/SOURCE_MAP_FILES.tsv)。本机 D/E 路径不代表公开下载地址。

- NVIDIA Jetson Linux R39.2.1 Kernel/模块源码合法获取参考：https://docs.nvidia.com/jetson/archives/r39.2.1/DeveloperGuide/SD/Kernel/KernelCustomization.html
- NVIDIA Jetson Linux release archive：https://developer.nvidia.com/embedded/jetson-linux-archive
- NVIDIA DRIVE Thor 7.0.3 bootburn/board config 正式文档：https://developer.nvidia.com/docs/drive/drive-os/7.0.3/public/drive-os-linux-sdk/getting-started/flash_steps_for_Thor_SOC.html
- NVIDIA Qwen3.8-27B-NVFP4 固定 revision（已核实）：https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/tree/fed99d815f4e8c7c616dd3dd6780076e26d5fb61

上述上游网址**并非本机自定义 Kernel/插件/G4 启动研究的逐字节镜像**；Jetson P3834 Boot 配置也不能用于 DRIVE P3960。

## 1. NVIDIA 官方 TensorRT Edge-LLM 支持

- **v0.11.0 官方安装指南**：https://nvidia.github.io/TensorRT-Edge-LLM/0.11.0/user_guide/getting_started/installation.html
- **官方平台支持矩阵**：https://nvidia.github.io/TensorRT-Edge-LLM/user_guide/getting_started/support-matrix.html
- **官方代码**：https://github.com/NVIDIA/TensorRT-Edge-LLM
- **上游实验直接构建器参考**：https://github.com/NVIDIA/TensorRT-Edge-LLM/blob/main/docs/source/user_guide/getting_started/direct-engine-builder.md

2026-10-15 检索官方矩阵显示 DRIVE Thor 官方路径：DriveOS 7.2 / CUDA Toolkit 13.3 / DriveOS SDK 容器内构建，然后将 build/ 部署到 DRIVE 设备。JetPack 7.2 的 Thor CUDA 13.2 行属于 **Jetson Thor**，不代表本车 DRIVE Thor 的官方许可/兼容组合。

本车实验路线为原 DRIVE 7.0.3 + Linux 6.8 RAM + NVIDIA R39 NvGPU 595.78 + CUDA13.2 U2 + TensorRT10.16.x/Edge0.11.0。即使某些数值/模型 PASS，也仍是**未列入上述官方 DRIVE 7.2 配置的自有实验组合**，不能称 NVIDIA 认证的正式升级。

官方推理最低可用设备内存≥模型体积+2GB，只是最低要求，KV Cache、Draft、长输入、多模态和 batch 会增加负荷。官方源码 C++ Engine 构建临时磁盘可需 20–50GB，另需考虑模型/旧 Engine 并存。

## 2. NVIDIA DRIVE OS 7.0.3 Thor 启动与 RCM

- 官方 DRIVE OS 7.0.3 Thor Flash Steps：https://developer.nvidia.com/docs/drive/drive-os/7.0.3/public/drive-os-linux-sdk/getting-started/flash_steps_for_Thor_SOC.html
- 官方 DRIVE 下载入口：https://developer.nvidia.com/drive/downloads

官方文档中 bootburn 的 -R 表示 RCM RAM 引导，不同于刷固件；但这仍要求**真实可用的主机 SDK、对应板级配置、物理恢复链路和 OEM/签名体系**。本机 G4D1 记录两个可用 USB-C 口不提供公开 Thor APX/RMC 设备通路，G4D DU2 表示 OEM Kernel/DTB boot authentication 的授权/签名部分阻断。不能使用 Jetson T4000 P3834 的通用公开 BCT/Boot 镜像覆盖 P3960。

## 3. 需要验证的版本与许可清单

- nvidia/Qwen3.8-27B-NVFP4 的 fed99d815f4e8c7c616dd3dd6780076e26d5fb61 固定 revision 已在 NVIDIA Hugging Face 模型树核验为公开可访问，模型卡列 Apache-2.0。仍需遵守模型/基础模型条件，外部使用者自行按 SHA 验证下载权重。
- TensorRT 10.16.0.72 与 10.16.2.10 两种历史候选不能混写为同一个运行环境。
- Edge-LLM v0.11.0 source commit 与安装 wheel build revision 不一致，必须为对应 Engine/插件分别冻结。
- NVIDIA 官方驱动/firmware/DRIVE SDK、模型权重、原厂签名/密钥都不得未经许可再分发；尤其不能因本仓是 Public 就推定已获得再分发许可。
- 对未知准确 ABI 的功能，不因为名称相似就替换系统文件。不开启 Secure Boot/Auth bypass 或非受支持引导写入。

## 4. 查询资料的最小原则

如上游更新，不直接把 main 分支源码替换 A1 已验证的 2026-10 冻结制品；新兼容性功能需先做版本差异、源/ELF、ABI 和隔离数值验收，并保留旧 runtime/Engine 的 SHA+回退。

任何公开性能数字都必须检查是否同 SM 数量、统一 UMA、同模型精度、同上下文、同 MTP/Cache、同 batch，再决定是否值得本车验证。
