# Thor-U 6.1 → 6.8 → NVIDIA → Edge 全流程执行与验收清单

勾选规则：仅在**实际完成并有证据**时才能 [x]，历史限定 PASS 不能自动提升为当前 LIVE PASS。截止 2026-10-15，本表不是设备现场状态。

## Phase 0：仓库、原件、宿主

- [x] MIT LICENSE（原创作者拥有权利的部分）和第三方许可排除说明已经建立；不存在对全部 NVIDIA 原始软件的 MIT 重授权。
- [x] 官方上游/ARM64 PyPI wheel/模型 SHA 下载清单、无设备变更的 R0 验收及 AI 助手 AGENTS.md 已就绪。
- [ ] 不同目标硬件及厂商 SDK 全量重建与 GPU/模型验收，保持分阶段 HOLD。

- [x] 建立 GitHub 工程仓库，筛选公开安全内容，现已公开并保留已审核的归档证据。
- [x] 统一 START_HERE、主方案、架构图、Gate、Kernel/GPU/Edge 构建与安装手册。
- [x] README/安装指南包含 6.1/6.8 结构图与各模式实际状态。
- [x] 录入 Golden 6.1、G4E2、G4D、A1 等历史核心报告（脱敏、保留源 SHA）。
- [ ] 当前现场重新只读确认设备 boot_id/Golden/串口/网络/分区与保护服务；**不由本 Git 任务触发**。
- [ ] 取得所有必要的、许可合法且版本匹配的完整二进制/官方物料，完成物料 SHA/源码闭包。

## Phase 1：Kernel 6.8 与启动

- [x] 历史 G35 Linux 6.8.12 构建、13943 导出符号闭包有原始记录。
- [x] 历史 RAM kexec 下 6.8、HVD/IVMK/IVC/vblk/rootfs ro 通过双轮 G4E2。
- [ ] 在全新合法宿主独立重建 Kernel Image/DTB/initrd/Modules 并对齐 SHA/ABI。
- [ ] 获得受支持 OEM P3960 host-only 启动槽/签名/Recovery 的真实授权信息。
- [ ] 新 6.8 独立 cold boot + 原版 6.1 双向启动和现场恢复 **当前 NO_GO**。
- [ ] 非覆盖持久双系统入口，不猜槽位，不换 OEM BCT/固件。

## Phase 2：R39 NVIDIA / CUDA

- [x] 历史 A1 6.8 RAM 下 Nvidia NvGPU595.78+DRM依赖/INTx、CUDA13.2 U2 基础数值 PASS。
- [ ] 独立 cold boot 的 GPU/GSP/ACR 与 MSI/ITS 以及长期故障恢复资格化。
- [ ] 逐一核对所有许可来源的 libcuda、libnvcucompat、firmware 与目标实际 ABI。
- [ ] 超出 basic CUDA compute 的所有 NVIDIA 上层包保持单独 Gate。

## Phase 3：Edge-LLM/27B

- [x] 历史 NVIDIA NVFP4 27B、K7、Tree 8K cache bypass 有范围限定的结果及 SHA/报告。
- [ ] 清洁宿主与精确 TensorRT10.16.x/Edge0.11.0 已安装 wheel/plugin 源一致性复核。
- [ ] 完整同 cache-policy K7/Tree 公平 A/B 质量+速度；完整工具、JSON、Agent、SSE、热前缀。
- [ ] 200K、C2、VLM/视觉/多模态、长稳/恢复按成本门由小到大；不重复不必要的 200K 全冷。
- [ ] 原 R4 Golden/模型和车辆相关服务保持不受干扰。

## Phase 4：发布

- [x] 脱敏与许可证隔离、仓库 SHA、一份离线可执行 Gate / 只读审计方案。
- [ ] 具备完整 Kernel 独立 cold boot、OEM 签名合法性和黄金恢复合同。
- [ ] 所有阶段满足 PASS_CURRENT_VERIFIED，才从 PUBLIC_RESEARCH_ARCHIVE 改为 RELEASE_READY。
- [ ] 系统级和推理级回退实测，发布后最小健康观察、故障通知、独立恢复验证。

所有当前状态由 manifest/PROGRAM_GATES.json 和 manifest/BOOT_6_1_TO_6_8_GATES.json 判定；打勾只表示证据类型，不替代那两个机器可读文件的 verdict。

## 下一项值得执行的工作

继续做 **合法 OEM host boot/slot/签名/冷启动/恢复机制**的只读资料审计，同时离线整理可重建输入，不做新的 6.8 reboot/kexec/flash，也不为了已有基础 CUDA PASS 再重复 GPU 测试。

统一 Codex 执行提示词见 PROJECT_HANDOFF_AND_PROVENANCE.md。
