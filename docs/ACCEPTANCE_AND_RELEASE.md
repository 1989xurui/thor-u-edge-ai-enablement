# Thor-U 全链验收、性能、回退与 Release Gate

## 1. 准入规则

每项 Gate 必须同时满足：明确版本与 boot_id、原始输入/输出、实际执行的作用域、Hash、质量/资源观测、失败处理、反证、负责人判决。**报告中的“有源码”“能 import”“生成 Engine”“测试脚本结束”均不自动构成实际功能 PASS。**

### 机器可读状态

权威跨阶段工作计划见 ../manifest/PROGRAM_GATES.json；专门的 6.1+6.8 永久引导风险门见 ../manifest/BOOT_6_1_TO_6_8_GATES.json。

在开发机可执行：

~~~bash
python3 tools/check_program_readiness.py --summary
python3 tools/check_dual_boot_readiness.py
python3 tools/verify_manifest.py
python3 tools/check_repo_release.py
~~~

HOLD 返回 2 是正确行为，表示工程发布阻断，而不是要求自动执行更多高风险测试。

## 2. 从 Kernel 到 AI 的验收矩阵

| Gate | 测试 / 最低证据 | 历史结果 | 不能外推 |
|---|---|---|---|
| A00 Hardware | T264 P3960、14 SM、64GB、DriveOS/OEM rootfs、真实 boot_id | Golden/A1 历史有记录 | 当前设备仍运行此版本 |
| A01 Golden | 6.1 内核、DTB、ro root、原件 Hash 与恢复工具 | 历史只读取证 PASS | 无条件自动恢复 |
| A02 6.8 Kernel | 精确 G35/Image/Kconfig、13,943 导出符号、vermagic | 历史构建 PASS | 完整官方固件/独立冷启 |
| A03 HV/IVC/vblk | DTB/HVD/IVMK、IVC #59-80、vblk、/new_root ro 双轮 | G4E2 RAM 双轮 PASS | OEM 签名/持久启动 |
| A04 启动方式 | 6.1 warm→6.8 / cold RCM / persistent 分别记录 | RAM kexec PASS | cold 或可选双启动 PASS |
| A05 NvGPU | R39 595.78、DRM/host1x/MC/firmware/ABI CRC | A1 RAM PASS | 全部 NvGPU 模式稳定 |
| A06 CUDA | cuInit、context、HtoD、SM110 Kernel、DtoH、65536 oracle | A1 RAM PASS | 其它 CUDA/NVFP4 模型 |
| A07 TensorRT | 用户库/plugin/engine 精确匹配、device profile、numerical oracle | 不同组件已有有界 PASS | 整体模型完全 PASS |
| A08 Edge target-only | checkpoint SHA、真实 27B 8K、所有输出 Token IDs | 指定样本有范围限定 PASS | 工具/多样本全质量 |
| A09 MTP K7 | K7+FP16 KV+Graph+Prefix，同目标参考 ID | 55.444 cold / 55.504 hot t/s 资格 | 一般速度或生产 |
| A10 Tree | 8K 368 output IDs，同条件 A/B/缓存状态 | 57.278 t/s 单旁路样本 PASS | Tree 热缓存/C2/200K PASS |
| A11 工作负载 | JSON、工具调用、长 thinking、取消/会话隔离、API/SSE | 只部分历史研究 | 真实 Agent 全栈 |
| A12 长稳/恢复 | 内存、温度、故障/冷启动、回 6.1、生产流量 | 未完整验收 | RELEASE |
| A13 官方授权 | 合法 SDK/firmware/boot/slot/签名、分发许可 | 不完整 | 安装第二永久系统 |

### 阶段早停

- A02 FAIL → 不装载 R39，先处理 Kernel/ABI。
- A03 FAIL → 停止 6.8 后续 Guest/GPU；不得修改 Hypervisor 安全域补救。
- A05/A06 FAIL → 不进入 TensorRT/Engine。
- A07/A08 FAIL → 不进入 MTP/Tree/200K。
- A09/A10 质量 FAIL → 退出候选、记录错误、保留原 K7/Golden。
- A12/A13 FAIL → 严禁标为生产/冷启动/双系统安装完成。

## 3. 8K 核心对照（必须保持原口径）

| 试验 | 冻结结果 | 解释 |
|---|---|---|
| K7/14SM/Graph 8K | cold Decode55.444tok/s，TTFT4.291664s | 当前保存的短上下文参考 |
| K7 热前缀 | Decode55.504tok/s，TTFT0.138552s | 单一重复前缀有效，复用8203 tokens |
| Tree 8K 缓存旁路 | 57.278tok/s、TTFT3.924s、368 token IDs 相同 | 与 K7 非同时、缓存条件不同 |
| Tree 热缓存/完整 Agent | NO_GO / 未完整验证 | 禁止拿 bypass 结果充当热缓存收益 |
| 200K 原生 | 冷TTFT207.9347s，Decode32.3149tok/s | 目标≤180s 和 ≥36tok/s 未达 |

同一固定 sample 不代表全模型一般能力；某些量化/算子存在可接受浮点差异，不能因为最终 Token ID 一样就宣称 logits、KV、GDN State 对任意输入逐位相同。

**质量优先**：固定同一 checkpoint/tokenizer、采样参数、输出长度/停止 token、Prompt/Prefix/Batch、Engine/Plugin、GPU clock、热态、Graph/Profiler 等条件。若无法配对只写“诊断数字”，不推广为性能收益。

## 4. 最小受控验收阶梯

1. **L0 静态**：Hash、ELF、ABI、代码/JSON/脚本格式、安全许可证、全新 clone。
2. **L1 小算子**：SM110 CUDA/FP16/BF16/FP8/NVFP4/GDN/Conv 和 CPU Oracle。
3. **L2 小模型**：真实 27B 最小 8K C1、Target-only、同 token ID。
4. **L3 候选**：K7 和 Tree 各自完整样本、同 cache policy 成对对比。
5. **L4 长上下文**：只有 L0-L3 合格且存在可信收益时测试 32K→64K→200K，不重复已冻存的完整冷样。
6. **L5 功能**：工具/JSON/SSE、Medium/XHigh 思考负载、取消恢复、跨会话隔离、稳定负载。
7. **L6 生产**：独立 cold boot、双向回 Golden、原 R4 不变、密钥/文件权限/服务恢复、持续运维与 rollback。

任何早期 Gate NO_GO，后面不启动；现有 R4 对照只是参考，不默认重测或替换其服务。

## 5. 资源安全线

- 64GB UMA 实际 Linux 可用约58GiB；GPU/CPU 共同占用，不能双计。
- 空闲系统 RAM 必须 ≥5GiB；GPU pool 必须 ≥2GiB；最高 Tj <95°C；目标持久卷空闲 ≥12GiB。
- 若有 Engine 编译/权重同时驻留，需额外空间/UMA，不得用上述最低线代替完整容量估算。
- 单机 C1 优先；C2 未证明净吞吐改善前不启用生产并发。大上下文/Graph/缓存需按实际 Profile 数量限制。
- 因温度、内存、NVML 错误或 GSP/FMC fault 触发任何守护停止时，先保存证据、停止候选，禁止循环加载驱动。

## 6. 发布分支与标签

- PUBLIC_RESEARCH_ARCHIVE：公开 GitHub 保留可分享文档、代码与离线审计，不包含不可合法分享的固件/权重；非安装或生产发布。
- RAM_EXPERIMENT_QUALIFIED：只在冻结的 A1 环境和已有范围内使用。
- BOOT_ADDON_BLOCKED：没有独立 6.8 的冷态启动资格，不能宣称双系统。
- EDGE_CANDIDATE：K7/Tree 部分场景有结果；生产默认不切换。
- RELEASE_READY/PRODUCTION_PASS：**当前没有达到**；必须有完成的实际双向 cold boot 和 27B 功能/质量/稳定/恢复证据。

建议先冻结研究资料版，不创建暗示可安装的 v1.0 production tag。发布说明必须列阻断项与来源证据。
