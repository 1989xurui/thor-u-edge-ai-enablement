# Thor G5：解除阻塞与完成验收的方案

2026-10-07。方案基于冻结 Phase27/28、本次 Phase29 RAM 证据、同版本 595.78 源码及冻结模块。本文是后续执行方案；没有据此新增实机实验。G5 仍 NOT_PASS。

## 推荐决策

先准备 **Phase29 补证轮：SEC2/GSP 已有读取值及 SMMU 原始事件关联**。本轮唯一变化是观测覆盖，所有功能输入保持基线。无需先取得 0x83d 错误码表，就能检查主机等待是否掩盖了访问错误，或者取得实际 DMA fault 的证据。这不能保证解决 0x83d；没有 fault 也不证明 DMA 正确。

上一阶段 BLOCKED 的准确范围应为：现有证据不足以选择功能 patch 或判决 B/C。下面新增的原版函数观测是一条可继续准备的取证路线，尚未通过 live probe Gate。不能把新的方案本身作为 G5 进度或通过证据。

## 第一阶段：原版模块扩展观测

冻结 nvidia.ko SHA256：`d617c6890534caa273e575763aff07c279e8a1f03c3b1fbb55d82d1bd1b98258`。

离线确认的候选点：

| 观测 | 候选位置 | 数据边界 |
|---|---|---|
| SEC2 mailbox0 原值 | `_ksec2IsCmdhandlingCompleted_GB10B+0x28`，x0 低32位 | 在原版 regRead032 返回后、与等待值比较前记录，不新增 MMIO |
| GSP HWCFG2 原值 | `_ksec2IsGspTargetMaskReleased+0x30`，x0 低32位 | 在原版 osDevReadReg032 返回后、掩码前记录，不新增 MMIO |
| scratch error 原值 | `kgspFmcCheckForErrorCode_GH100+0x24`，x0 低32位 | 在原版读取返回后、转为 bool 前记录，不套用于 mailbox0 |
| init RPC 实际状态 | `kgspSendInitRpcs_IMPL` 入口/返回 | 记录是否实际执行及返回值，不调用新的 RPC |
| EMEM 写入游标变化 | `ksec2SendPacket_GB10B` 中已有 EMEMC 读取返回点 | 补足发送端检查，不把游标变化当接收端字节一致 |
| SMMU 实际事件 | `arm_smmu_handle_evt(smmu, evt)` 入口 | 仅复制内核已读取到 CPU RAM 的四个事件字；按目标内核定义解析 |

目标 vmlinux 确认保留 `arm_smmu_handle_evt` 和 evtq_thread 符号。上述 nvidia 候选点也存在于冻结模块。偏移只对该 SHA 的模块有效；实时加载模块/指令与探针支持性仍须验证，任何不匹配即停止。

### Gate

1. 重新核验当前 boot_id、内核、模块/固件 SHA、translated SMMU、INTx、无 heap override、原 heap 基线、持久文件系统只读和设备健康。
2. 核对 live 符号、指令、寄存器值存活范围，确认函数没有 kprobe blacklist/instrumentation 限制；探针只记录已有返回值或 CPU RAM，不主动访问受保护寄存器。
3. 给 SMMU 事件关联保留 smmu identity、原始事件、SID、时间、地址；包括非 0x10100 SID 的异常，避免错过 FMC 可能走另一 stream 的证据。只在本次有限窗口采集，不给所有 IRQ 加密集日志。
4. 原有 boot args / COT / WPR / IOVA 证据保持可关联；采样尽量少，记录丢失、nmissed、溢出和观测引入的时序影响，不能用有明显干扰的轨迹做精确延迟或稳定性结论。
5. 确认外部 supervisor 的完成标记、退出码和最多一次 tegrareset 逻辑均正确。上一轮修正脚本未执行；不能未经复核直接启动。
6. Gate 全部满足后，该补证轮仅触发一次 nvidia-smi，RAM-only 保存原始输出；结束立即撤销探针。若异常按既定恢复规范处理，不反复触发。

### 判决与停止规则

- 出现与 handoff 窗口、具体地址和设备相关的 translation/access/permission fault：可定位实际访问失败；若要归属于 FMC，还需 stream/请求阶段的关联证据。按新错误优先规则处理。
- 出现寄存器访问错误返回或不可信读值：先把实际可访问性列为第一 blocker；使用 595.78/目标内核的错误模式解释，不猜其他返回码。
- scratch 出现非零：使用它自己的同版本编码规则记录，并与 mailbox 分开，新的首个错误接管定位。
- 全部主机返回正常且无 SMMU fault，仍为 0x83d：仅证明这些观察未发现异常，不将 B 排除或 C 标为已证明。停止本轮，进入第二阶段，不重复相同实验。

## 第二阶段：接收端内容/地址观测

若第一阶段不能定位，必须补 SEC2/FMC 实际接收或读取证据。优先寻找同版本支持的诊断方法。候选包括 SEC2 EMEM 提交内容读回、FMC 读取参数快照、实际 aperture/stream 的诊断输出。

这些方法**尚未证明可安全执行**。尤其 EMEM 读回可能需要改读取游标，涉及 MMIO 写入、时序和固件并发；仅把它叫“readback”并不能当成无副作用。必须先明确：

- 同版本访问权限、生命周期、读操作副作用和锁/游标恢复方法；
- 能在 receiver 消费/清除前取得正确时刻的数据；
- 不覆盖输入、不扰动 secure firmware、不改变 SMMU 模式或持久状态；
- 如需 RAM-only 诊断组件，独立说明它的用途、访问范围、退出/恢复方法；不默认替换 nvidia.ko；
- 有校验的原始字节与 CPU 参数、完整 COT、WPR 及有关地址逐项比较。

无法满足这些 Gate，则这条接收端实验不可执行，资料/支持接口成为实际依赖。此时需要的是 **精确 595.78 的诊断文档、错误码或受支持接口**，并不要求升级驱动、获取 DRIVE SDK 账号或刷启动固件。可以先处理本机已有或公开资料。

## 第三阶段：只修被证明的缺口

| 判决 | 修复范围 | 必须保留的对照 |
|---|---|---|
| A：具体构造/拷贝字段违反 595.78 契约 | 该字段、长度或拷贝顺序的最小修复 | 修改前后 CPU 字节、接收字节及错误结果 |
| B：实际 aperture/SID/IOVA/可见性错误 | 被证实的映射、缓存同步或交接语义修复 | 实际请求和读回证据；translated SMMU 保持 |
| C：实际内容/映射正确但格式或认证拒绝 | 同版本被证实的 ABI/WPR/安全格式兼容点 | 正确内容、实际映射、明确拒绝阶段与修复后结果 |

不因“低地址”“零字段”“没有 IOMMU 日志”或其他版本案例选择 patch。物理地址替换 IOVA、重开 heap/CMA 路线、绕过认证、换 Debug FMC 都不是当前推荐方案。

任何功能 patch 均独立一轮、单变量、带原版对照和可恢复原件。若是 workaround，必须检查 595.78 标准功能、性能和稳定性副作用；证据不充分不得声称无损，也不为追求一条 smi 成功牺牲标准能力。异常工作源文件须使用已验证原包建立新的构建输入，不从 NUL 文件直接重建。

## 第四阶段：完整 G5 验收

严格依次通过：RmInitAdapter → GSP firmware boot → nvidia-smi → CUDA context → CUDA basic compute。

验收材料至少包含：

- payload/version/kernel symbol CRC 及 live 加载对象匹配；6.1→6.8 handoff 的冻结证据；
- RM/GSP 成功的原始状态与日志，NVML/PCI topology 与 CUDA Driver 的设备身份/实际 CC 交叉核对；
- context 创建与释放成功；同版 libcuda 上实际 PTX JIT、小规模确定性运算与 CPU 结果一致，记录分配、传输、同步和错误返回；
- 无新增 panic、fatal IOMMU、reset loop；需要 workaround 时，补齐相应功能/性能/稳定性验证和风险边界；
- 原始输出、脚本、版本、SHA manifest 和最终逐项验收表，全部未知项保持未通过。

只有上述证据齐备，才设 G5=PASS、READY_FOR_G6=YES。G6 CUDA 13.2 上层生态和模型任务仍在本目标之外。

## 当下的具体下一步

先完成第一阶段的离线探针定义、实时符号/指令核对与 supervisor Gate；准备好一轮可审阅执行包后，再进入新的单次取证轮。暂不实施功能修复。此方案提供推进路径，不承诺每轮必然得到固件侧可见性或 G5 PASS。
