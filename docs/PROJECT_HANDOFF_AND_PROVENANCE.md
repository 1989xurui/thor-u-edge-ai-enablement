# 全工程交接、原始证据、后续协同工作规范

## 1. 单一负责人与三类权限

本项目下一阶段建议以**一个执行 owner**管理 Codex/工程工作流，不再拆出互相抢锁的三个无人监管 agent。一个人/智能体可以调用构建、驱动、CUDA、推理、测试各类专项检查，但实时设备 GPU/Boot 始终只有一个 Owner。

| 权限级别 | 可自动做 | 不可自动做 |
|---|---|---|
| S0 纯离线/只读 | 读文档、索引、离线代码对比、哈希、Python/JSON/Markdown 检查 | 改车机 |
| S1 隔离研发主机 | WSL 内从合法来源编译，建立临时产物，核对 ABI，保留原件 | 改 OEM 安全签名或车机正式服务 |
| S2 车机维护授权后单次 | 严格前置 Gate、独占、指定次数的隔离测试 | 自动持续 kexec、Boot slot 写、生产恢复竞争 |
| S3 固件/持久 Boot | 需合法受支持 OEM 工具、物理救援、回退与独立 Gate，另行授权 | 当前无执行资格 |

程序不会生成能在当前设备绕开签名/BootROM/厂商权限的工具。

## 2. 统一资料地图

| 项目块 | 权威本机资产根（2026-10-15） | GitHub 归档 |
|---|---|---|
| OEM 6.1 Golden | E:\Thor64G_Backup\GoldenBoard_2026-09-01 | docs/evidence_history/GOLDEN_BOARD_READONLY_20260901.md |
| G0-G5 / 6.8 Hypervisor/IVC/kexec | E:\Thor64G_AI\THOR_U_R39_GOS_BOOT_GATE_20261006 | docs/evidence_history、docs/kernel/history、patches/kernel |
| A1 6.8 + NvGPU595.78 + CUDA13.2 | D:\Thor64G\THOR_U_A1_NVGPU_R39_20261013 | src/kernel-gpu、evidence/kernel/cuda、docs/kernel |
| TensorRT Edge/NVFP4/Tree | D:\Thor64G\THOR_NVIDIA_NVFP4_20261013 | src/edge-llm、evidence/edge、docs/edge |
| 原 27B 模型/Engine | 历史设备 /zeekr_data/nvidia-native-ai-v2 / /zeekr_map/nvidia-native-ai-v2 | 不复制权重/Engine；归档版本 Hash |
| R4 llama.cpp/网关旧环境 | E:\Thor64G_AI\R4\Host_Assets（D 入口 Junction） | 原件保留；不纳入此核心技术仓 |

**重要**：本仓并没有扫描/备份全部 D/E/WSL/车机数据。历史失败/成功需要可追溯原日志，但大型日志和二进制只用 manifest 记录位置和 SHA，不能将当前轻量 Git 仓库作为全机器灾备。

## 3. 仓库资料优先级

- **唯一流程入口**：docs/START_HERE.md → MASTER_IMPLEMENTATION_PLAN.md。
- **最新技术事实**：docs/STATUS_AND_ACCEPTANCE.md 与各阶段最终 verdict。
- **实时 / 冻结状态分离**：manifest/PROGRAM_GATES.json 是截至发布日期的分阶段判决，不反映未来设备实时。
- **原始可追溯报告**：docs/evidence_history 和 evidence/cuda、evidence/edge。
- **SHA/来源与安全记录**：manifest/SOURCE_FILES.json、SUPPLEMENTAL_EVIDENCE.json、SHA256SUMS.txt、REVIEW_REQUIRED.json、SANITIZATION_REPORT.json。
- **默认配置建议**：保持 K7/原 R4 Golden 基线；Tree 与 200K 的新增结果只能做 Candidate，不替换。

## 4. 如何继续时不重复浪费时间

1. 先只读比较本机当前 Git commit 与上次交接 commit，并查看 PROGRAM_GATES 的 highest blocking phase。
2. 已有 A1 基础 CUDA 数值 PASS 不再无条件重做；后续只补最近一次确认必要且证据缺失的 Gate。
3. 旧 R39/GSP 0x83d 失败证据要和 2026-10-13 以后 A1 成功分开引用；同样新版 6.8 RAM 正常并不抹去 cold GSP 未验收风险。
4. 8K/27B 主线优先，只有同条件净收益和完整质量证据才测试长上下文或其他引擎；减少 200K 冷 Prefill 反复等待。
5. 原 G4D1 RCM USB physical FAIL / DUPKG & OEM auth BLOCKED 不能通过重复软件扫描突破；需要实际新物理授权/主机工具事实才改变 Gate。
6. 任何修改先写入新候选文件/分支，验证并保留原件，不直接覆盖 OEM 6.1、黄金服务和原权重。
7. 新证据必须记录源文件、hash、版本、测试作用域、与旧结论冲突处理；更新综合状态而不是在历史文档中悄悄改 FAIL。

## 5. GitHub 编辑/发布工作流

仓库附带手动触发的 GitHub Actions 静态验收 (.github/workflows/offline-validation.yml)；没有自动重启/升级/监测车机的 CI。先跑本地 SHA 与来源审计，再考虑推送。

~~~text
read source evidence (read only)
    → explicit file allowlist
    → secret / license / path scanner
    → sanitized staging copy + source/export SHA
    → static checks + source scripts syntax
    → Git private branch / PR (optional)
    → independent reviewer or gate
    → push main
    → fresh clone + manifest check
    → publish commit SHA + remaining blockers
~~~

文件可能含公司 LAN、用户名、内部保存路径，源码还可能含 NVIDIA copyright。不可把 GitHub Private 当成无限制许可。Native NVIDIA 的专有二进制、模型权重、签名/Key、车机分区镜像和 WSL VHDX 都排除。

首次源归档已有 19 个内网 IP 脱敏文件、2 个供应商版权内容仍待许可审查、2 个原路径失效。新增历史报告同样脱敏；详情见相应 manifest。**脱敏过的源码可能不再可直接运行，执行前需合法恢复环境并二次审查**。

## 6. 可以交给后续 Codex 的单一任务提示词

> 只处理 GitHub 私有项目 1989xurui/thor-u-edge-ai-enablement，以 docs/START_HERE.md、MASTER_IMPLEMENTATION_PLAN.md、PROGRAM_GATES.json 为唯一任务入口。唯一目标是保留 DriveOS7.0.3/Linux6.1 Golden 并逐步实现实验 Linux6.8.12→R39 NvGPU595.78→CUDA13.2→TensorRT Edge-LLM27B 的可重建、可安装、可恢复闭环。先逐项复核当前源码/Hash/设备状态，明确过去 PASS 与目前阻断，优先补真正的 Boot slot/签名/独立 cold boot 事实，不执行未获准的 kexec、刷写或生产切换。所有实验必须有界、单变量、GPU 独占、质量先于速度，已通过的重复测试不重跑。按 P00-P12 更新状态、明确来源与回退，避免新建重复项目仓库。完成每轮后提交 SHA、证据、未达项和下一最低风险动作。

## 7. 最终闭环的验收样式

~~~text
CURRENT_RELEASE: PRIVATE_RESEARCH
GIT_COMMIT:
CURRENT_DEVICE_BOOT_ID: NOT_READ_IN_THIS_RELEASE
GOLDEN_6P1: HISTORICAL_PROTECTED
KERNEL_6P8_RAM: HISTORICAL_SCOPED_PASS
KERNEL_6P8_INDEPENDENT_COLD: NO_GO
OEM_DUAL_BOOT_ENTRY: NOT_IMPLEMENTED
NVGPU_CUDA_BASIC: HISTORICAL_SCOPED_PASS
EDGE_27B_8K: QUALIFIED_SCOPED_CANDIDATE
EDGE_FULL_QUALITY_PRODUCTION: NO_GO
MANIFEST_SHA: ...
NEW_EVIDENCE:
NEXT_SAFE_ACTION:
~~~
