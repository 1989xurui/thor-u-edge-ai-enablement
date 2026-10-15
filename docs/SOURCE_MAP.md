# SOURCE_MAP：三个本机研发目录的真实源码入口

**来源核查日期：2026-10-15 · 公开源码地图 v1**

这份文档解决三个问题：本机 D:/E: 路径究竟是什么、在哪里可以找到已经发布的文件、去哪里取得缺失的 NVIDIA/模型上游来源。

**结论：三个 Windows 路径不是可下载的网址，不是分别独立的 GitHub 仓库，也不是完整公开镜像。** 三个目录的根部没有独立 .git/origin；它们只是同一台 Windows 研发电脑的本地工作区。真正公开入口是当前仓库下的 src、docs、patches、evidence 与 manifest。

**新增：**获取官方源代码、三个精确 SHA256 的 Edge-LLM ARM64 wheel、固定版本 NVIDIA 27B 模型及分阶段复现步骤，请阅读 [DOWNLOAD_AND_REPRODUCE.md](DOWNLOAD_AND_REPRODUCE.md)。原创项目部分的 [MIT LICENSE](../LICENSE) 和 [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) 为授权边界，第三方素材不自动改为 MIT。

## 1. 三套本机来源与 GitHub 对应表

| 本机工作区（Windows） | 核心任务 | GitHub 公开位置 | 本机只读目录扫描* | 对应发布文件 |
|---|---|---|---:|---:|
| **D:\Thor64G\THOR_U_A1_NVGPU_R39_20261013** | A1 Kernel 6.8、R39 NvGPU、CUDA13.2 | [Kernel 构建代码](../src/kernel-gpu)、[内核证据](../evidence/kernel)、[CUDA 证据](../evidence/cuda)、[Kernel 报告](kernel) | 755 文件、约 37.234 GiB | **28** |
| **D:\Thor64G\THOR_NVIDIA_NVFP4_20261013** | TensorRT Edge-LLM、NVFP4 27B、K7/Tree | [Edge 源码](../src/edge-llm)、[质量/性能证据](../evidence/edge)、[技术报告](edge) | 4,937 文件、约 22.172 GiB | **59** |
| **E:\Thor64G_AI\THOR_U_R39_GOS_BOOT_GATE_20261006** | G0-G5、kexec、HV/IVC/vblk、RCM 和冷启动限制 | [启动报告](kernel/history)、[启动源证据](evidence_history)、[Kernel 配置差异](../patches/kernel) | 25,353 文件、约 5.175 GiB | **19** |
| 附加来源：历史 G5 及 Golden 6.1 | 早期失败机制及原厂保护证据 | [历史 G5](kernel/history)、[Golden 报告](evidence_history) | 不属于以上三个目录 | **4** |

*以上文件数/容量为一次只读元数据扫描，不跟随符号链接；不会实时更新，也不代表所有文件有权公开。三目录约有 31,045 个文件、总计约 64.58 GiB，里面大量是源码树、固件/驱动包、模型、Engine、编译输出或原始日志。GitHub 只收录了其中经过筛选的一小部分。*

**逐文件、带链接和 SHA256 的权威表：** [SOURCE_MAP_FILES.tsv](../manifest/SOURCE_MAP_FILES.tsv)（110 行）和 [SOURCE_MAP.json](../manifest/SOURCE_MAP.json)（来源根目录、分类统计、官方 URL）。每行包含：

- root_id（哪个本机来源）、source_relative_path（原目录下的相对路径）
- repository_relative_path 和 repository_url（GitHub 中可以实际打开的位置）
- frozen_source_sha256（归档时对应的原始文件 SHA）
- published_file_sha256（脱敏后的公开文件 SHA）
- transformation（是否移除原有 LAN IP、MAC 等）、current_local_source_status（本机源文件是否已发生变化）

本轮已对全部 110 项公开文件逐一核验 SHA，全部存在且与既有 manifest 对应。

## 2. 来源与 GitHub 的结构关系

~~~mermaid
flowchart LR
  A["A1 Kernel/NvGPU/CUDA<br/>D: local"] --> K["src/kernel-gpu<br/>23 files"]
  A --> KC["evidence/kernel/cuda<br/>and kernel reports"]
  B["Edge NVFP4/Tree<br/>D: local"] --> E["src/edge-llm<br/>36 files"]
  B --> ER["evidence/edge 21<br/>docs/edge 2"]
  C["G4/G5 HV/Boot<br/>E: local"] --> CR["boot reports and diffs"]
  K --> GH["GitHub curated<br/>source and evidence"]
  KC --> GH
  E --> GH
  ER --> GH
  CR --> GH
  O["Official NVIDIA / HF<br/>upstream dependencies"] -. "Links and version SHA only" .-> GH
~~~

注意：架构图中的上游虚线表示依赖链接，不表示 GitHub 内含完整第三方代码、GPU 驱动、NVIDIA SDK 或模型权重。

## 3. A1 Kernel 6.8 / R39 GPU / CUDA13.2：源码如何取得？

### 当前仓库已公开

| 内容 | 点击打开 | 边界 |
|---|---|---|
| 精简的 A1 构建/审计/SM110 测试源码 | [src/kernel-gpu](../src/kernel-gpu) | 23 个文件，不是完整 Linux kernel tree |
| A1 的 Kernel 6.8 / Nvidia ABI / firmware 验收 | [evidence/kernel](../evidence/kernel) | 核心历史报告和 checksum，不包含二进制内核或完整 .ko |
| CUDA 数值计算的历史实机结果 | [A1_NATIVE_RUNTIME_RESULT.json](../evidence/cuda/A1_NATIVE_RUNTIME_RESULT.json) | A1 RAM 会话 65536 项 CPU oracle PASS |
| 源码构建与版本说明 | [BUILD_KERNEL_GPU_CUDA.md](BUILD_KERNEL_GPU_CUDA.md) | G35、Module.symvers、DRM/host1x、NvGPU、CUDA 的门槛 |

A1 历史版本：Kernel **6.8.12-prod-g78272943bba3**；源码 commit **78272943bba3a47e633b28963b0cda60de503500**；G35 config SHA **3df259fa1f0be026af15e15e5133eb609a1e3e47f663313bc01b20afafe5b50b**；NvGPU **R39.2.1 / 595.78**；CUDA **13.2.86 Update2**。

### 真正公开上游（并不是你本地研发目录的镜像）

- [NVIDIA Jetson Linux R39.2.1 Kernel Source / Customization](https://docs.nvidia.com/jetson/archives/r39.2.1/DeveloperGuide/SD/Kernel/KernelCustomization.html)：指向官方 source archive、kernel / NVIDIA OOT 源码取得方式，必须按本机版本/commit/配置/补丁逐项核对。
- [Jetson Linux 官方版本档案](https://developer.nvidia.com/embedded/jetson-linux-archive)：R39.2.1 的发行与源码入口，**不是 DRIVE Thor P3960 的独立签名冷启动包**。
- [NVIDIA DRIVE OS 7.0.3 Thor / Bootburn 官方文档](https://developer.nvidia.com/docs/drive/drive-os/7.0.3/public/drive-os-linux-sdk/getting-started/flash_steps_for_Thor_SOC.html)：真正的 DRIVE Thor OEM 启动约束与获授权 SDK/板级工具入口。

**不可以**直接把 Jetson Thor T4000/P3834 的板级 BCT、Boot 镜像和固件用于 DRIVE Thor P3960。

## 4. TensorRT Edge-LLM / NVFP4 27B：源码和模型从哪里来？

### 当前仓库已公开

| 内容 | GitHub 地址 | 规模 |
|---|---|---:|
| 本机实验的 Python/CUDA/Tree 构建与诊断代码 | [src/edge-llm](../src/edge-llm) | 36 个原来源文件 |
| 原生 K7/Tree/性能/质量证据 | [evidence/edge](../evidence/edge) | 21 个文件 |
| 发布快照与总技术报告 | [docs/edge](edge) | 2 个文件 |
| 精确模型/Engine 构建说明 | [EDGE_LLM_27B.md](EDGE_LLM_27B.md) | 研发流程 |

### 公开上游地址

- [NVIDIA TensorRT Edge-LLM GitHub](https://github.com/NVIDIA/TensorRT-Edge-LLM)：上游代码，实验使用 Edge v0.11.0。**源码 commit 95515c2f87fba8982db5a519f9022277667b3cc9 与实际安装 wheel 的编译 revision 74f8732a7e8d1377e34471ad2652988346f18813 不一致**；普通 clone main 无法重现你当时已安装的 wheel/plugin。
- [官方支持矩阵](https://github.com/NVIDIA/TensorRT-Edge-LLM/blob/main/docs/source/user_guide/getting_started/support-matrix.md)：DRIVE Thor 官方对应 **DriveOS 7.2 / CUDA13.3**；本车 **DriveOS7.0.3 / Kernel6.8 RAM / CUDA13.2** 是独立研究组合。
- [NVIDIA Qwen3.8-27B-NVFP4 固定 revision 模型](https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/tree/fed99d815f4e8c7c616dd3dd6780076e26d5fb61)：已核实的模型公开来源。权重三分片约 20.42 GiB，本仓**不复制模型权重或 TensorRT Engine**。

### 注意：4 份本机原始文件后续又更新了

逐字节比较发现 Edge 来源下四项与已发布归档的原始 SHA 不同：

| 本地 Edge 根目录 | GitHub 冻结快照 |
|---|---|
| RELEASE_CARD.md | [docs/edge/CURRENT_RELEASE_CARD.md](edge/CURRENT_RELEASE_CARD.md) |
| CANDIDATE_VERDICT.json | [evidence/edge/CANDIDATE_VERDICT.json](../evidence/edge/CANDIDATE_VERDICT.json) |
| EVIDENCE_INDEX.tsv | [evidence/edge/EVIDENCE_INDEX.tsv](../evidence/edge/EVIDENCE_INDEX.tsv) |
| RUN_STATE.json | [evidence/edge/RUN_STATE.json](../evidence/edge/RUN_STATE.json) |

这些是**源工作区较发布快照的新变化**，不代表 GitHub 丢失文件或 SHA 错误。本次只补全来源说明，不自动覆盖历史冻结验证资料。若要同步最新技术结论，需另做差异、许可、敏感信息和证据质量验收。

## 5. E 盘 Boot/G4/G5：在哪里看到启动源码和结论？

- [启动历史和 G5 核心报告](kernel/history)：原 Kernel/HV/RCM、GSP0x83d 的实验报告。
- [精选 G4D/RCM/OEM 身份和 Golden 报告](evidence_history)：8 个经过网络信息脱敏的报告，其中 7 个来自 E Boot 研究目录，另一个来自 Golden。
- [Kernel 配置差异](../patches/kernel)：G2 和 G3.5 的配置片段；**不是完整适合一键安装的 6.8 系统 patchset**。
- [6.1 基础上新增 6.8 的启动/回退设计](BOOT_6_1_TO_6_8.md)：RAM kexec 已有历史成功；独立 cold boot、A/B 实际槽位与认证仍未完成。

E Boot 工作目录包含的许多编译对象/供应商包/大日志/私有设备信息不在公开仓库内，**不存在“完整 E 盘启动目录可下载网址”**。OEM Bootburn 的受支持入口见上文 DRIVE 官方文档。

另有 **D:\Thor64G\G5_TAKEOVER_20261007** 来源的 3 个历史 G5 文件，以及 **E:\Thor64G_Backup\GoldenBoard_2026-09-01** 的 1 份 6.1 Golden 摘要。这两份是补充来源，不属于用户指定的三个目录。

## 6. 尚未收录的内容与原因

初次筛选明确有 **4 条待审记录**：2 个 NVIDIA 第三方代码版权来源尚待确认，2 个历史路径不存在。详见 [REVIEW_REQUIRED.json](../manifest/REVIEW_REQUIRED.json)。

更多无法随意再分发的依赖详见 [OFFLINE_REQUIRED_ASSETS.json](../manifest/OFFLINE_REQUIRED_ASSETS.json)：原厂固件/签名包、完整 Kernel Image/DTB/initrd、R39 用户库和 firmware、TensorRT/Edge wheel/插件、NVFP4 模型、Target/Draft Engine。**公开源码≠已取得商业/厂商分发许可证。**

## 7. 其他开发者如何使用而不混淆来源？

~~~bash
git clone https://github.com/1989xurui/thor-u-edge-ai-enablement.git
cd thor-u-edge-ai-enablement
python3 tools/verify_manifest.py
python3 tools/check_source_map.py
python3 tools/check_repo_release.py
~~~

三条命令验证公开归档，不访问车机，也不加载 GPU 或刷写固件。

随后按 [ASSET_AND_VERSION_LOCK.md](ASSET_AND_VERSION_LOCK.md) 的 SHA/版本锁自行从合法来源取得缺失物料，再根据 [DEPLOYMENT_RUNBOOK.md](DEPLOYMENT_RUNBOOK.md) 对照自己的设备。**本仓仍然无法独立安装第二个可冷启动的 6.8 系统。** 运行 boot/program 准入脚本返回 HOLD（退出码 2）是符合当前事实的正常结果。
