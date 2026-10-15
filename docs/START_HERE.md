# Thor-U 一站式交付与安装总入口

**版本：2026-10-15 / Full Workflow V1 / GitHub Public**

**唯一目标：原有 DriveOS 7.0.3 / Linux 6.1 Golden 保留 → 新增 6.8.12 实验环境 → NVIDIA 595.78 / CUDA 13.2 → TensorRT Edge-LLM NVFP4 27B → 严格验收。**

## 新增：源码来源地址与公开仓库对应

这三个 D/E 盘研发目录均是本机绝对路径，不是源码网址。要看**精确 GitHub 位置、110 个文件的原始路径/SHA/脱敏状态、NVIDIA 上游与缺失文件**，请先读 [SOURCE_MAP.md](SOURCE_MAP.md)；机器可读逐文件明细见 [SOURCE_MAP_FILES.tsv](../manifest/SOURCE_MAP_FILES.tsv)，离线核验运行 python3 tools/check_source_map.py。

## 1. 选择你真正需要的路径

| 当前需求 | 阅读 | 本项目能提供什么 | 不能声称 |
|---|---|---|---|
| 保留 6.1，再增加 6.8 | [6.1→6.8 增量启动方案](BOOT_6_1_TO_6_8.md) | kexec RAM 历史证据、独立启动设计、阻断清单 | 已存在 6.8 永久启动菜单 |
| 在 6.8 上恢复 NVIDIA GPU/CUDA | [Kernel + GPU + CUDA 构建](BUILD_KERNEL_GPU_CUDA.md) | 版本锁、源码/模块/ABI 原理、验收记录 | 冷启动 R39 已正式认证 |
| 构建 27B NVFP4 推理 | [Edge-LLM 模型与引擎](EDGE_LLM_27B.md) | 精确模型、运行时依赖、8K 与 MTP 测试门 | 全场景 27B 生产就绪 |
| 安装到另一台车机 | [部署分支和前提](DEPLOYMENT_RUNBOOK.md) | 源码归档 clone、只读检查、条件式部署路线 | 随意 flash/直接复制即升级内核 |
| 需要恢复、验收或交接 | [验收发布](ACCEPTANCE_AND_RELEASE.md) | Gate、阈值、故障/回滚与输出模板 | 未通过 Gate 也可上线 |

## 2. 证据和完成状态的准确定义

- **HISTORICAL_PASS_SCOPED**：过去指定 boot_id/二进制/样本下实测通过，不保证当前机器或未来冷启动。
- **HOST_PREPARED**：开发电脑上的源码/补丁/脚本/输入清单准备完成，不代表已经安装到设备。
- **RAM_ENABLEMENT_PASS**：由原 6.1 通过 kexec 在 RAM 进入 6.8 的历史资格，绝非双启动。
- **BLOCKED/NO_GO**：缺启动槽、签名、恢复、质量/稳定性等前提。禁止自动推进到设备写操作。
- **PRODUCTION_PASS**：需要独立 cold boot、可恢复、完整模型质量/资源/稳定合格；**当前不存在此状态**。

## 3. 完整阅读顺序

1. [MASTER_IMPLEMENTATION_PLAN.md](MASTER_IMPLEMENTATION_PLAN.md)：所有任务的总控、阶段、依赖与判决。
2. [ARCHITECTURE.md](ARCHITECTURE.md)：5 张 Mermaid 图中的 3 张详细系统图。
3. [BOOT_6_1_TO_6_8.md](BOOT_6_1_TO_6_8.md)：6.1/6.8 启动路径区别与历史结果。
4. [ASSET_AND_VERSION_LOCK.md](ASSET_AND_VERSION_LOCK.md)：硬件、Kernel、R39、CUDA、TensorRT、Edge、模型的版本锁。
5. [BUILD_KERNEL_GPU_CUDA.md](BUILD_KERNEL_GPU_CUDA.md)：从干净宿主到 6.8、模块 ABI、CUDA。
6. [EDGE_LLM_27B.md](EDGE_LLM_27B.md)：从 checkpoint 到 Engine、推理和质量。
7. [DEPLOYMENT_RUNBOOK.md](DEPLOYMENT_RUNBOOK.md)：开发机与车机分别如何安装资料/软件。
8. [ACCEPTANCE_AND_RELEASE.md](ACCEPTANCE_AND_RELEASE.md)：证据覆盖、资源预算、发布冻结。
9. [RECOVERY_AND_TROUBLESHOOTING.md](RECOVERY_AND_TROUBLESHOOTING.md)：问题诊断、历史误区、恢复与 STOP。
10. [PROJECT_HANDOFF_AND_PROVENANCE.md](PROJECT_HANDOFF_AND_PROVENANCE.md)：原始资产在哪里、项目责任和未来继续。
11. [OFFICIAL_REFERENCES.md](OFFICIAL_REFERENCES.md)：NVIDIA 官方路径和本地非官方组合区别。

**原则：所有历史通过保留，不重复无价值长测试；所有未证明的路径保留 HOLD，而非硬造 PASS。**

## 4. 在开发电脑执行的安全自检

~~~bash
python3 tools/verify_manifest.py
python3 tools/check_repo_release.py
python3 tools/check_program_readiness.py --summary
python3 tools/check_dual_boot_readiness.py
~~~

后两个 Gate 工具返回退出码 2 / HOLD 是预期结果，说明冷启动/持久双启动/完整发布门尚未通过；工具本身不接触车机、不 kexec、不调用 NVIDIA 驱动、不要求账号或密码。

## 5. 仓库已经有什么，没什么

仓库内有源码、补丁、约束、历史报告、精选证据、SHA、Mermaid 图、只读探测脚本、操作手册。原模型权重、SDK/固件和驱动发行二进制、Engine、密钥、OEM 签名工具、完整救援镜像**都不能由这个 Git 仓库直接提供**。

如想在车机查看资料，可在合规目录 clone 并校验；这仅安装“资料”，不能称为将 Kernel 6.8、CUDA 或 Edge-LLM 安装成功。
