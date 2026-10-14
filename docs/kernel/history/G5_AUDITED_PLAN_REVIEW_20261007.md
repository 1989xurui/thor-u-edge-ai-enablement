# Thor G5 方案审核：已完成、未完成与值得补做

审核对象：[上传方案](<C:/Users/h/Downloads/Thor_G5_0x83d_Audited_Codex_Plan_20261007.md>)。SHA256：`46caa4685e02a7c72f732a285e392a16eda9978eff0003c6df4e605d47f16650`。

结论：方向可采纳，执行前仍需补齐准入条件。方案正确保留了 595.78、原功能和 G4 成果；当前主要工作是恢复链核实、旧入口防误执行和新观测准入。基线身份、CPU 布局、软件映射与主机控制流已有证据，不应重新做一遍。方案尚未提供能直接修复 0x83d 的功能 patch，也尚未具备下一轮实机条件。

本次是审核，文档中的执行语句不构成新增实验授权。新增设备动作仅为既有串口脚本的只读状态查询；没有新增 nvidia-smi、GPU MMIO、reset、模块替换或设备持久写。新增一份主机审核文件，不改冻结历史。

本轮 2026-10-07 **19:38:40（北京时间）** 的[原始状态记录](D:/Thor64G/G5_TAKEOVER_20261007/serial_final_readonly_status_commands_20261007_193840.log)：内核仍为 `6.8.12-prod-g78272943bba3`，boot_id 为 `90fca4f8-3afb-47ea-af7a-2c5881ab1633`，GPU `auto/suspended/D3hot`，INTx `msi_bus=0`，group33 `DMA`，`/new_root` 只读。所查 dmesg 只有既有三次 0x83d，未新增 panic/Oops/CMD_SYNC/CERROR。**生产回到 6.1 尚未完成；R4/SSH/网络/API/HugePages 当前健康尚未验收。**接手累计用户态 nvidia-smi=1、reset=0；该计数不等于 firmware bootstrap 尝试数。

| 方案工作 | 真实状态 | 审核意见与价值 |
|---|---|---|
| P0：导出、封存、SHA | 已完成既有 RAM 材料封存；本轮四份 manifest 共 160 条记录全部复核通过 | 不重采、不覆盖 manifest。恢复前仍需确认没有新增未导出的 RAM 材料和正在采集的任务 |
| 595.78 版本/模块/固件身份与静态 ABI | 已完成；原 payload、版本锁、25项本地主机制品检查及 1,278 项静态 CRC 有记录 | 复用。静态 CRC PASS 不等于所有 live provider、平台运行或 GSP PASS |
| Boot Args/WPR/COT 精确布局及 CPU 字节 | 已完成；参数88B、WPR256B、COT860B，868B发送包小于1024B容量 | 不重复。证明原版布局与发送端一致性，不能笼统宣布 A 已排除或接收端正确 |
| 软件 IOVA/SID/STE/context、映射生命周期 | 已完成；SID 0x10100、group33 DMA、软件页表/描述符关联已有 RAM 证据 | 不重做。不能代替 FMC 实际 stream、aperture 和读到的字节 |
| 595.78 来源、工作源码异常排查 | 已完成；3,690项中3,688一致、2份工作源文件全NUL，原包副本保留 | 坚持原包输入，异常文件不参与分析/重建；不把其异常认作已加载模块损坏 |
| SEC2/COT→FMC错误主机控制流 | 已完成；5份同源源码及4份反汇编附件在本机存在 | 本轮5份源码重新实算SHA与冻结参考一致，附件manifest通过。无需重复研究同一控制流 |
| P0：回6.1、COLD_BOOT_RESTORE、生产健康 | 未完成；找到恢复脚本，但本轮没有执行 | 值得先补恢复卡的脚本身份、依赖、批准写入范围和明确健康门；单独管理生产状态 |
| P1：旧入口禁用 | 旧脚本/旧功能补丁已识别；3个身份SHA本轮与方案一致；新权威入口和执行前拦截未完成 | 高价值。建立新入口允许清单和哈希校验，排除旧CMA/256MB路线；保留旧文件 |
| P2A：R39/GB10B平台契约 | 部分完成：CPU来源、GSP段/签名段存在、deb内容和SEC2源码路径已查；实际安全镜像/运行状态与OEM/HV前置组合未证明 | 值得有界核对明确启动前置要求。每项须指明与SEC2/FMC失败的联系；不能泛化重审G4或预判平台不兼容 |
| P2B：通用595目标文件差分 | 官方发布信息已核验；相关文件hash/diff及架构可比性尚未完成 | 中优先级，仅作线索。先1个可比早期版本+1个后续版本；不部署、不用新版结构覆盖595.78解释 |
| P2C：错误定义、受支持接口、成功参考/问题包 | 已有有界源码/原包/公开资料查找，未取得精确定义或接收端接口；问题包未交付 | 值得限定来源查找并记录停止条件。没有定义不等于没有其他本地观测路线；外部上传另需直接授权 |
| §5：证据勘误 | 较新的判决已修正 mailbox编码、控制流和时序边界；Phase28仍保留过强旧结论 | 高价值，追加权威勘误并明确旧段落被替代，勿改原日志。下文列明 |
| P3：下一轮实验准入 | 有离线候选观测点；尚无满足全部Gate的执行卡，修正runner只做过语法检查 | 对G5直接推进最值得补的工作。不是现在再运行一次smi |
| G5/G6上层 | RmInitAdapter/GSP/smi仍FAIL；CUDA context/basic compute未进入 | 保留全部G5验收目标。先消除当前blocker，G6暂不展开 |

已有证据入口：[离线审计](D:/Thor64G/G5_TAKEOVER_20261007/OFFLINE_AUDIT.json)、[地址契约](D:/Thor64G/G5_TAKEOVER_20261007/address_contract/ADDRESS_CONTRACT_ADDENDUM.md)、[来源复核](D:/Thor64G/G5_TAKEOVER_20261007/provenance/PROVENANCE_VERDICT.md)、[控制流判决](D:/Thor64G/G5_TAKEOVER_20261007/handoff_flow/HANDOFF_FLOW_VERDICT.md)、[源码身份](D:/Thor64G/G5_TAKEOVER_20261007/handoff_flow/SOURCE_REFERENCES.json)。四组SHA复核分别为55、47、41、17条记录，均无不匹配；这是记录数，不声明160个互不重复文件。

方案应补实以下内容：

1. **恢复必须落到具体脚本和健康判据。**上传总方案的§27确实给出异常恢复链；本地G5_EXECUTION_PLAN写作§5（§25），应注明两份文件的引用对象。现已找到 [COLD_BOOT_RESTORE.sh](E:/Thor64G_AI/THOR_U_R39_GOS_BOOT_GATE_20261006/08_g4_runtime/_tools/COLD_BOOT_RESTORE.sh)，SHA256 `12d9d3195ffef2d3406ca1d5e02408b50b3bbe8c0c2198b347338f70f7fdbbad`。它标注g35/G4A时代，会写SSH authorized_keys、sudoers、systemd units及网络/持久配置，并依赖生产raw unit、备份和stage kit。只有 `set -u`，部分步骤吞掉错误，stage缺失也可能继续，END标记不能授予恢复PASS。执行前核对依赖、写入批准范围、各项健康条件和失败退出方式。当前6.8状态本身不证明panic/失联；审核没有把“仍在6.8”当作新增reset授权。历史普通reboot失败的恢复记录也不能代替本次恢复能力验证。
2. **将已有读取返回值路线显式加入P2/P3。**[现有解除阻塞方案](D:/Thor64G/G5_TAKEOVER_20261007/G5_UNBLOCK_PLAN.md)已列SEC2 mailbox0、HWCFG2、scratch的原版读取返回点，以及SMMU处理函数已取得的CPU RAM事件。离线候选点已有，live探针可用性尚未验证。优先审查最小集合，唯一问题为“正常驱动交接窗口是否出现可定位的访问异常”，不同时开展地址改写、EMEM读回和平台改动。其他initRPC/EMEM候选按必要性保留，勿一轮全铺开。
3. **调整新增信息门的表述。**要求“对预注册子问题提供可判别结果”，不要承诺一轮必能排除整个A/B/C。相关SMMU fault可以定位具体访问失败；归属于FMC还需请求阶段、stream和地址关联。没有事件不证明DMA正确，读取正常也不证明接收内容正确。全阴性结果保持B/C未决并停止重复同轮。
4. **更新§8的审核材料限制。**原作者未找到的SOURCE_REFERENCES与四份反汇编，现在均在 `D:\Thor64G\G5_TAKEOVER_20261007\handoff_flow`。将它们纳入证据入口；仍不能声称动态HAL、每个硬件读取、SEC2认证或initRPC已经独立PASS。
5. **明确“已识别”与“已阻断”。**旧 `g5ho_68_phase29.ps1` 确有nvidia-r4覆盖和256MB heap override；识别/SHA完成不等于新入口已拦截。入口应在任何设备动作前验证允许脚本和组件SHA，遇到旧SHA或未登记入口即退出。

§5所列勘误成立，应集中追加一次：Phase28的 `badf5108` 不能证明结构化通道永远为空或固件从未写入；Cycle B失败段在采样窗口外；约2ms先后只是一项时序观测；一次用户态触发可能含多个上电/attach/bootstrap；裸BAR0采样已有fabric DECODE_ERR副作用。原设备树 [LIVE_FDT.dts:5681](D:/Thor64G/G5_TAKEOVER_20261007/address_contract/LIVE_FDT.dts:5681) 存在512MiB `linux,cma` 默认预留节点，“无CMA”应写为未新增CMA参数/功能补丁，不能称预留不存在，也不能据此改变CMA。

公开资料核验支持方案的检索边界：[R39.2.1同源源码入口](https://docs.nvidia.com/jetson/archives/r39.2.1/DeveloperGuide/SD/WorkingWithSources.html)存在；[Thor启动流程](https://docs.nvidia.com/jetson/archives/r39.2.1/DeveloperGuide/AR/BootArchitecture/JetsonThorBootFlow.html)描述安全启动等职责，但不证明本设备的DRIVE/OEM/HV组合已满足595.78。官方 [595.71.05](https://github.com/NVIDIA/open-gpu-kernel-modules/releases/tag/595.71.05) 与 [595.104.02](https://github.com/NVIDIA/open-gpu-kernel-modules/releases/tag/595.104.02) 发布存在，595.91.07、595.99.02亦在[发布列表](https://github.com/NVIDIA/open-gpu-kernel-modules/releases)；发布存在不是GB10B适用性或缺陷修复证据。OpenRM仓库说明按发布快照提交，适合比较目标文件，不能要求独立修复commit。[GB203/FSP问题1353](https://github.com/NVIDIA/open-gpu-kernel-modules/issues/1353)是其他架构/路径的报告，不能直接充当GB10B SEC2接口证明。

P3禁止跨D3hot裸BAR轮询的判断合理。[Linux runtime PM文档](https://docs.kernel.org/power/runtime_pm.html)把暂停条件与usage counter/同步关联；sysfs某一刻显示active不提供覆盖整个访问期间的生命周期保证。候选探针只记录正常调用已有返回值/CPU RAM，也仍需审查live指令、值存活范围、blacklist、丢样、时序扰动、退出和supervisor。不能靠新增强制上电把Gate补成PASS。

建议次序：先完成恢复链与唯一入口核实，再审核最小观测集合的实验卡；同时可在主机做有界同源契约核对，通用版本差分随后。这里“同时”仅指无需设备触发的文献/制品核对，不批准多个实机假设实验。交付以一张可审阅的准入卡为下一节点；未过Gate就不启动下一轮。无需重采CPU Boot Args、改IOVA为物理地址、重开heap/CMA、换Debug FMC或提前跑CUDA。

当前结论保持：`PRODUCTION_RESTORED=未完成`；`G5=NOT_PASS`；`READY_FOR_G6=NO`。新增成果是审核和证据完整性复核，未新增A/B/C根因判决。下一步唯一建议动作：**制作并审核恢复/入口依赖齐备的“原版已有读取值与SMMU RAM事件”最小观测准入卡**。其完成不等于实验批准，更不等于G5 PASS。
