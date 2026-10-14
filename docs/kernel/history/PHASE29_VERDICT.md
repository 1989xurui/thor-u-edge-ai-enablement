# Thor G5 接手与 Phase29 冻结判决

日期：2026-10-07。G5 目标保持 ACTIVE；G5=NOT_PASS，READY_FOR_G6=NO。

## 判决

Phase29 单轮取证完成，唯一一次 nvidia-smi 返回 6，输出 `No devices were found`；GSP-FMC 仍报 `0x83d`，RmInitAdapter 返回 `(0x62:0x55:2168)`。本轮没有发现新第一 blocker；MSI fallback 与失败后的 leftover mapping 已存在于旧轮日志。

**已证明：CPU 侧已采样参数稳定，交接地址与软件 IOMMU 映射一致。尚未证明：FMC 使用同一地址空间并实际读取到这些字节。A/B/C 最终因果归类仍未解决，不能据此宣告 C。**

| 分支 | 本轮证据 | 判决 |
|---|---|---|
| A：CPU 内容错误 | 完整 88 字节结构符合 595.78 布局，WPR/LibOS 指针与 descriptor 一致，关键尺寸与标识自洽；交接前、49 次轮询、释放前的参数和已采样元数据完全一致 | 未发现构造/覆盖错误；固件所要求的全部语义尚未证明正确，不能彻底排除 A |
| B：GPU/FMC 地址或内容错误 | COT、memdesc IOVA、内核 map 记录一致；3 个关键对象均映射到 CPU backing 页；未在失败前解除这些映射 | 软件地址对应已证明；实际 DMA aperture、Stream ID、缓存可见性和 FMC 读取内容未证明，B 仍保留 |
| C：内容映射均正确仍被拒绝 | 没有 FMC 内容读回或等价证据 | 前提未满足；ABI、firmware、WPR、安全格式只可保留为未证明候选 |

H2 继续作为下一步优先检查的高置信候选，含义收窄为 **FMC 访问所用地址空间/aperture 与软件映射的关系**；不是已经证明的根因。不实施 patch。

## 唯一版本基准与离线门

读取只读 source 挂载中的 595.78 `version.mk`、`gspifpub.h`、GH100 GSP 和 GB10B SEC2 代码。未借用新版结构。

用同一版本头文件及 AArch64 GCC 13.3 编译布局常量：

| GSP_FMC_BOOT_PARAMS 成员 | 字节偏移 |
|---|---:|
| initParams | 0 |
| bootGspRmParams.target / descSize | 8 / 12 |
| gspRmDescOffset | 16 |
| wprCarveoutOffset / Size | 24 / 32 |
| bIsGspRmBoot / bInstInSysMode | 36 / 37 |
| gspRmParams.target / bootArgsOffset | 40 / 48 |
| gspSpdmParams.target / payloadOffset / size | 56 / 64 / 72 |
| gspRmMemParams | 80 |
| sizeof / alignment | 88 / 8 |

`NvBool=1`，enum=4。WPR meta=256 字节，LibOS region=32 字节。SEC2 COT 是 packed 860 字节；boot args offset 成员位于 852。

595.78 SEC2 路径交给 FMC 的地址来自 `memdescGetPhysAddr(..., AT_GPU, 0)`。translated 模式下有匹配 IOVAMAPPING 时使用 IOVA，否则相关函数可能回退物理 PTE，必须核对实际 descriptor。旧轮 `0xffefb000` 是当轮 AT_GPU 交接值；本轮地址已变化，不能将旧值当 CPU 物理 RAM 直接读取，也不能凭本轮反推旧值对应的物理页。

离线 Phase28 证据 SHA 9/9、冻结 manifest 中 25/25 条目匹配可用本地原件。4 个 OpenRM 模块及实际依赖 drm.ko 的共 1,278 条 symbol CRC 与目标导出表匹配，ARM64/vermagic 门通过；静态导出表检查不等于全部提供者已在设备上加载。实际本轮加载 nvidia、nvidia_uvm、drm，不展开 modeset/drm 上层任务。

## 单轮现场证据

设备 kernel=`6.8.12-prod-g78272943bba3`，boot_id=`90fca4f8-3afb-47ea-af7a-2c5881ab1633`。全程同一 boot。translated SMMU、INTx、原始 nvidia.ko/固件保持原状态，RegistryDwords 为空，没有 heap override。内核原有 CMA 配置存在；本轮未启用 CMA 实验路线。

| 对象 | 实际 IOVA | CPU 物理 backing | 映射建立时刻 | 解除时刻 |
|---|---|---|---:|---:|
| FMC boot params（88 字节，页映射 4096） | 0xb7edf000 | 0x14948e000 | 4777.802169 | 4777.852148 |
| WPR meta（256 字节，分配页 4096） | 0xbfffe000 | 0x14948d000 | 4777.802172 | 4777.840132 |
| LibOS args（分配页 4096，采样前 128） | 0xb7efe000 | 0x14948c000 | 4777.802174 | 4777.840145 |

三者 IOVAS=0x100、链表 next=0、PteAdjust=0；map trace 翻译结果与 descriptor 物理地址一致。映射都保留至失败后的释放阶段。COT boot 地址等于 0xb7edf000。FMC image 的 COT 地址与其 descriptor IOVA 同为 0xb7e40000（本轮未转储完整 image 内容）。

CPU boot params 解码：WPR target=1（COHERENT_SYSTEM）、WPR descSize=256、WPR addr=0xbfffe000；bIsGspRmBoot=1，bInstInSysMode=0；LibOS target=2（NONCOHERENT_SYSTEM）、addr=0xb7efe000；carveoutOffset/Size=0。零 carveout 字段不能单独判为错误，595.78 头文件允许 ACR 隐式分配 WPR 的环境忽略这些字段。WPR magic=`0xdc3aae21371a60b3`、revision=1；未证明其余字段满足 Thor 固件所有要求。

取证路径：使用原版模块的 entry/return kprobe、已有 mailbox0 读取后的指令 probe 和内核 IOMMU map/unmap tracepoint。关键指令位置由原始模块反汇编核对：`_kgspLockdownReleasedOrFmcError+0x30`，此时 x0 是驱动既有读取结果，x19 是 KernelGsp。没有新增 MMIO 读取、强行唤醒 GPU或调用自定义内核读取函数。

PRE=1、COT=1、POLL=49、RET=1、FREE=1；kprobe nmissed=0；各 CPU buffer overrun、commit overrun、dropped events 均为 0。保存完整参数 88 字节、WPR meta 256 字节、LibOS 前 128 字节；这些字节在所有已采样阶段一致。未采样 LibOS 完整页、radix3 全链、固件实际 DMA 内容。

Mailbox0 观察到地址 → 0 → 0x83d：20 次地址、28 次零、1 次 0x83d。最后地址在 4777.834691，首次零在 4777.834696，错误在 4777.834816。已观测间隔为 **125 微秒（最后地址到错误）/120 微秒（首次零到错误）**。这轮不支持沿用“精确 2ms”表述；Phase28 的 1ms 采样及其时序结论只能作为旧轮观测。Trace instrumentation、轮次和观察点不同，本轮不是性能基准，不把 mailbox 清零等同于成功读取全部参数。

## 执行与恢复审计

外部 Windows supervisor 持有 COM6/COM5，COM5 NvShell 门通过；只发送一次 nvidia-smi。没有 panic、Oops 或设备失联；reset count=0。无需触发 OEM6.1 / COLD_BOOT_RESTORE 异常恢复流程。

主机脚本结束标记误用了 `$rc__`，导致标记缺失数值。设备 trace 已明确记录 P29_END_RC=6、tracing_on=0，且 shell 已返回。因此在 timeout/reset 前终止主机等待进程；没有第二次触发，也没有为标记问题重启设备。原始脚本和日志保留供审计，修复版另存，不执行。

证据均在设备 initramfs /tmp 和 tracefs 中产生并导出到 Windows；本轮未发出设备持久写操作，/new_root 全程 ro。ro ext4 挂载状态本身不能证明先前 boot 的 journal 零写；本轮没有重新挂载或重播操作。设备 SHA 前后一致，回到原有 auto/suspended 状态。5 个 probe 与私有 trace instance 已移除；本轮挂载的 tracefs 已卸载，最终 mount 表恢复原状，boot_id 再次核对未变。RAM 证据保留。

导出压缩包 SHA256：`4ae8bcbc89f6e13a3e20d8f875dd182f0539945112271a6400e975bfc0edf352`。
原始 trace SHA256：`c229b019480c587604ea719c7119aef44a224491f3471a6a59455d78be2a53f5`。二者已独立解码校验。

## 接手目标与下一门

G5 接手目标已创建并保持 ACTIVE：595.78 上依次 RmInitAdapter → GSP boot → nvidia-smi → CUDA context → basic compute 全 PASS，形成可追溯证据后才 READY_FOR_G6=YES。当前 RmInitAdapter/GSP boot FAIL，nvidia-smi FAIL；CUDA context/basic compute 尚未执行，不能记为 FAIL 或 PASS。

下一步仍在 Phase29 范围内，先离线锁定 **GB10B FMC 使用的 DMA target/aperture、GSP/SEC2 Stream ID 与 Linux IOVAS0x100 的对应关系**，以及 coherency/copy 可见性契约。只有锁定能区分 B/C 的取证方法和单一变量 Gate 后，才设计后续单轮；不自动追加本轮 smi，不凭“映射正确”改 AT_GPU 为 AT_CPU，不展开 CMA/heap/SMMU 切换或 CUDA/NVML 上层任务。

不得把未发现错误等同于根因关闭，也不得把 H2 假设写成已证明。当前证据不足以证明任何功能 patch 必要。
