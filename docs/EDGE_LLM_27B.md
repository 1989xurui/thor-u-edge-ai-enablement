# TensorRT Edge-LLM 0.11.0 + NVFP4 27B：从权重到推理的完整流程

**可复现下载入口**：[TensorRT Edge-LLM v0.11.0 ARM64 Wheel 3 种 Python ABI、Pinned NVIDIA 27B 模型三分片以及 SHA](DOWNLOAD_AND_REPRODUCE.md)。先做 R0/R1 复现，随后才按隔离实验 Gate 进行设备上的 NVIDIA/CUDA/Edge 资格验证；原创 MIT 不覆盖模型及 NVIDIA binary。

**研究栈**：DRIVE Thor T264 SM110 / 14SM / Linux 6.8 RAM / NvGPU 595.78 / CUDA 13.2 U2 / TensorRT 10.16.x / Edge-LLM 0.11.0。

本方案用于隔离实验和正确性验收，不能把本机非官方版本组合包装为 NVIDIA 官方 DriveOS 7.2 + CUDA 13.3 支持版本。

## 1. 两套“支持情况”必须分开

**NVIDIA 官方**：TensorRT Edge-LLM v0.11.0 在 DRIVE Thor 官方矩阵中以 DriveOS 7.2 + CUDA 13.3、DRIVE SDK container 构建、部署 build/ 到 target 作为支持路径。资料：https://nvidia.github.io/TensorRT-Edge-LLM/0.11.0/user_guide/getting_started/installation.html

**本机实际研究**：DriveOS 7.0.3 原件、Kernel 6.8.12 RAM 暖启动、R39.2.1 NvGPU595.78、CUDA13.2.86，加装 TensorRT10.16.x/Edge v0.11.0 进行实验。即使基础 27B 已有实机结果，也**不是官方支持组合或已完成生产验收**。

## 2. 整体推理链

~~~mermaid
flowchart TB
  MODEL["固定 checkpoint: 27B NVFP4"] --> LOCK["权重 shards / tokenizer / revision SHA"]
  LOCK --> TRT["隔离 TensorRT + Edge-LLM runtime<br/>ABI/SM110/plugin 精确锁版"]
  TRT --> TARGET["Build target 64-layer engine<br/>原权重量化配置"]
  TARGET --> OFF["8K C1 target-only 数值/质量"]
  OFF --> MTP["内置 Draft / K7/Graph/Prefix"]
  MTP --> TREE["Tree8/Top2/16 node 候选<br/>缓存旁路单样本"]
  TREE --> FULL["冻结多样本质量/性能/复用/恢复"]
  FULL --> DEPLOY["完整 Gate PASS 后，才可发布"]
~~~

### 精确 checkpoint

- nvidia/Qwen3.8-27B-NVFP4@fed99d815f4e8c7c616dd3dd6780076e26d5fb61。
- 三份权重共 21,921,697,280 bytes ≈20.42GiB；2194 tensors，量化层 401（208 FP8、193 NVFP4）；模型含 48 GDN + 16 full-attention（来源为本机冻结研究记录）。
- Tokenizer SHA 历史 0997f410c57a1f4e53b09e4be8f4a172d90edd9564368fb0847030937229b9f3。
- 模型及 19 文件传输历史 SHA 匹配；仓库没有存储真实权重，也没有当前车机独立重新读取计算的证明。

## 3. 上游软件版本与插件 ABI

确认 TensorRT 10.16.x 的**确切小版本**、Edge wheel 0.11.0 的 compiled revision、源 commit、SM110 plugin artifact。历史 source 95515c2… 与 installed wheel 74f8732… 不相等；不能仅用源码内容推断二进制相同。

最小组件顺序（全部有实例/数值证据才往下走）：

1. CUDA device SM110、driver/runtime library SONAME 实际映射。
2. NVRTC/nvJitLink、CUDA Graph、BF16/FP8/NVFP4 cuBLASLt、CuTe/FA4 目标形状。
3. TensorRT plugin load、TensorRT Engine 构建、反序列化与创建 execution context。
4. 真实 27B Target 模型 forward/prefill/Decode。
5. 原生 Draft 与 target pairing、Target/Draft KV 为 FP16 及 GDN/Conv 状态语义。
6. Prefix / Agent tool / SSE/SDK（后续 Gate）及取消重用，不抢 R4 Golden。

**历史故障**：完整 Engine 曾能构建但 execution context SIGSEGV；旧 TensorRT10.16.2.10 与之后 Wheel 匹配的 10.16.0.72 都有不同阶段失败。后续经过专门的数值边界、GDN 和 MTP 研究才有有界成功样本；不能拿失败轮作为通用构建操作步骤，也不能把所有差异一概忽略。

## 4. 两种 Engine 构建路线

**官方 C++/ONNX 受支持路线**：按照官方平台 support matrix 使用对应 SDK、CUDA 和 TensorRT；checkpoint → （可选量化）→ ONNX → TensorRT engine → C++ runtime。需目标系统支持，导出/量化也有独立 CPU/GPU 内存要求。

**本机实验 ONNX-less / Python builder 路线**：严格限定原 NVFP4 checkpoint、安装 Wheel/plugin、Target/Draft profile，在隔离目录运行。仓库 src/edge-llm 内脚本是历史阶段性实验/固定目录，不是另一台车机可直接执行的 Universal Installer。

官方上游在其支持设备/正确依赖条件下的参考命令形态（**不适用于未经资格化的本机 7.0.3/13.2 组合**）：

~~~sh
# Example ONLY in a fully qualified upstream environment
tensorrt-edgellm-build \
  --model-dir /path/to/verified-nvfp4-checkpoint \
  --engine-dir /path/to/new-isolated-engine-directory \
  --max-input-len 8192 --max-kv-cache-capacity 8192 \
  --max-batch-size 1

# Native Qwen integrated MTP is contained in target checkpoint
tensorrt-edgellm-build \
  --model-dir /path/to/verified-nvfp4-checkpoint \
  --engine-dir /path/to/new-isolated-engine-directory \
  --spec-type mtp
~~~

Build flags/outputs and support must be checked against the EXACT local 0.11.0 wheel/CLI. Do not simultaneously build in the active production engine directory; never overwrite Golden/R4/model or an existing qualified Engine.

## 5. 历史 8K 质量/性能数据的正确使用

| 测试项 | 冻结数据 | 可以认定 | 不能认定 |
|---|---|---|---|
| 原 FP4 输入边界修复、MTP OFF | Decode 12.419tok/s、TTFT3.862s | 相应 Engine 8K 样本通过 | 该路径为最佳速度 |
| 选中 K7 + 14SM GDN + Graph + cache | 8K cold Decode55.444，hot55.504tok/s | 冻结一个 368 token 样本，同 ID 证据 | 已完整生产稳定 |
| Tree 8K cache bypass | Decode57.278tok/s、TTFT3.924s、368 token IDs 相同 | 单 C1 缓存旁路样本 PASS | 在公平热缓存条件下通用胜过 K7 |
| Tree 200K 诊断 | cold TTFT207.935s、decode32.315tok/s | 限定 profile 和 token check 数据 | 达到 TTFT≤180s / Decode≥36tok/s 目标 |

冷/热并不可以混为同一基线；不同 Engine Profile/采样/Cache/Prompt、诊断事件都会使速度结果失去因果意义。K7 仍为回退与冻结默认候选，Tree 在完整质量/生产 Gate 前不得取代默认。

## 6. 生产之前必过的最小严格验收

- 模型权重/Tokenizer/Runtime/Engine/Plugin SHA 完整匹配，配置唯一。
- 先 8K C1 同模型同Prompt/采样设置，逐 Token 及完整 JSON/文本校验；不可只验证某个文件存在或插件注册。
- FP16 KV、GDN/Conv State、PageKV 的数值边界，在已冻结的相应器件/样本中按实际契约验证；不要推断一切逐字节相同。
- K7 ↔ Tree 要同 cache policy、同 batch、同输入长度、同时段 GPU 频率/温度/资源条件下配对。
- 原生前缀缓存（同信任域）不能跨会话混用；取消、重连、复用、在途请求、单例 C1 必须稳定。
- 200K、视觉/多模态、C2、Agent/tool/API、热启动、冷启动、24h 长稳分别为独立 Gate；未通过不写 PASS。
- 守护 MemAvailable≥5GiB、GPU pool≥2GiB、Tj<95°C、各持久分区空闲≥12GiB；按完整编译需要更多空间。

## 7. 模型持久位置与本仓不同

历史车机隔离位置：/zeekr_data/nvidia-native-ai-v2/models/nvidia-Qwen3.8-27B-NVFP4-fed99d，以及 /zeekr_map/nvidia-native-ai-v2/ 的 Engine/Runtime 区。不要把过去磁盘路径存在等同于当前环境仍相同，也不在原有目录直接清理或重构。部署前必须做车机当前空间、文件锁、是否存在 in-flight GPU job、维护 owner 的只读确认。

源代码和证据在 src/edge-llm、docs/edge、evidence/edge；所有源/插件与版本限制必须由交接负责人校对。下一步见 [验收](ACCEPTANCE_AND_RELEASE.md)。
