# Thor-U NVIDIA 原生 AI 完整集成 V2

更新：2026-10-14T12:09:45.221453+08:00。完整目标仍在执行；当前整个平台判决 **NO-GO（验收未完成）**。

当前用户优先级：**TensorRT Edge-LLM 长期主线，全部统一8K；200K暂缓。**
当前选中8K资格候选：内置MTP K7/verify8＋14SM GDN＋Graph＋原生前缀缓存。冷Decode55.444、热Decode55.504tok/s；冷Prefill基座GPU2036.967tok/s，冷TTFT4.291664s、热TTFT0.138552s。目标验证轮数54→48，接受率96.91%→95.24%，以实际有效吞吐选择K7，较保存K6约快6.7%；全部输出IDs一致。仅重编约686MiB内置Draft，原目标Engine硬链接复用，K6和原GDN回退保留。 短64输出成本诊断已完成：K6/K7均验证10轮，K7多做Draft，Graph GPU总成本增加5.56%；不能外推为所有输出长度都提速。完整368输出的55.44/55.50tok/s资格结果保留，其Graph内验证GPU分项仍未测量。 原生Attention精确形状算子已通过：T1约0.137ms、T8约0.160ms，CPU最大误差小于6.1e-6，非插入位置KV逐位保持。T8实际目标图16个Attention节点、grid[1,8,1]，普通Decode为4CTA；不能只看CTA少就认定它主导延迟。按隔离成本乘16粗估2.57ms/约2.8%短测目标验证时间，非整模型归因或提速上限，暂后置split-KV。Python CUDA绑定未被现有图实例化拦截器捕获，几何证据来自此前实际整模型图；不重复已通过算子测量。 原始CuTe FP4尺度映射在实际检查点首次暴露2.73%相对误差，已修复为保留E4M3块尺度编码、将原激活全局尺度合并至alpha；原始FP4权重/激活保持。两种实际形状M1/M8通过，CuTe最大相对误差0.04569%。实际CuTe常驻网格已是14CTA；M8 up约慢1.04%、down约快0.64%，两up加down仅粗估整体慢0.47%，未视为完整MLP/模型归因，不替换当前目标；保留修复及小幅down算子候选。 新增Tree-MTP候选：官方启动脚本为8步、Top-2、16验证节点；约40%增益来自不同模型/硬件的特定Agent负载相对3步线性MTP，不能套到当前K7。现机只读接口审计通过，实际基座tree标志false、两Engine容量8，本地14SM GDN仅线性cap8，Tree实机准入NO-GO；需先证明分支GDN/Conv快照与接受叶恢复。 16节点Tree状态组件现已通过：GDN实际输出是压缩kNorm/g/beta/v重放数据，不能按线性完整快照复制。原生验证后，用公开NVIDIA重放内核的独立NVRTC13.2移植体在GPU提交两条接受分支，再由原生phase3继续解码，状态误差不超过1.49e-8；Conv快照/提交/继续状态逐位一致。单层验证GDN0.090095ms、Conv0.019446ms，均为算子口径。源码与安装wheel版本仍不一致；本轮验证了实际数据格式兼容，并未调用安装LLMRuntime的整树接受流程。Conv首次失败为参考函数误含外层SiLU，修正后复用原Engine，GDN不重测。 独立bounded16 Tree状态适配器已跨进程序列化通过：声明Prefill最大8448时，GDN/Conv中间缓冲首维仍为16；实跑32-token Prefill→16节点验证→叶14提交→原生单步继续解码，GDN提交/继续状态误差分别5.78e-7/3.60e-7，Conv状态逐位一致。8448只是容量检查，本轮未执行8K模型推理。 安装版LLMRuntime的Tree8/Top2/16节点调度已在四层目标跑通23轮，24个输出与保存的同目标普通解码逐一一致；345个Draft提议中接受数为0，只验证根节点提交/继续，不能称为完整接受分支或性能PASS。实机发现接受阶段固定提交9位置，K7旧Draft容量8不足；仅重编同检查点内置Draft至16，四层目标和普通解码对照未重跑。 普通原FP4非MTP回退计划已无损归档到D，完整源SHA和解压SHA均为24c6084b9ce6；复核无消费者后仅回收该生成Engine。该回退需从归档恢复再使用，现机K7/K6及原生GDN MTP回退仍保留。 64层Tree目标已一次构建成功并真实生成：冷8K语义Oracle通过，335个Draft token接受、413次Graph replay成功；但输出381token从首token就与冻结368token不一致，故Tree严格验收及提速判决NO-GO，58.48tok/s仅为诊断数字。相同新Engine的普通解码12token和Tree缓存旁路12token均与K7相同，问题已缩小到HybridMTP分块Prefill/前缀缓存衔接；不能据此认定模型不匹配。 随后同一Tree Engine仅执行一轮完整缓存旁路8K：8207输入、368自然结束输出与K7逐token完全一致，324个Draft token接受/44轮、395次Graph replay成功，正式通过该单样本C1旁路验收。Decode57.278tok/s、TTFT3.924s、GPU冷Prefill2115.198tok/s、完整请求10.333s。相对保存K7冷测Decode+3.307%、请求耗时降低5.311%；缓存策略不同且非同时A/B，不能泛化。Tree候选保留，K7仍为默认；Tree缓存路径单独NO-GO。
8K同输入8207、同输出368逐token一致；以下为保存K7冷测与新Tree缓存旁路冷测，缓存策略不同且非同时A/B。
|指标|K7冷请求|Tree旁路冷请求|变化|
|---|---:|---:|---:|
|有效Decode|55.444tok/s|57.278tok/s|+3.31%|
|TTFT|4.292s|3.924s|-8.57%|
|完整请求耗时|10.913s|10.333s|-5.31%|
|C1完整请求输出吞吐|33.723tok/s|35.614tok/s|+5.61%|
|Base GPU冷Prefill|4029.028ms|3880.015ms|-3.70%|
|Base GPU冷Prefill吞吐|2036.967tok/s|2115.198tok/s|+3.84%|
|Draft GPU冷Prefill|217.400ms|208.292ms|-4.19%|
|目标验证轮数|48|44|实际计数|
|接受Draft token数|320|324|实际计数|
|提议Draft token数|336|660|实际计数|
|成功Graph replay数|383|395|实际计数|
|最低可用RAM|31.859GiB|30.553GiB|不同运行条件|
|最低GPU可用|31.827GiB|30.118GiB|不同运行条件|
|观察峰值Tj|63.843C|58.656C|不同运行条件|
K7热前缀已通过：TTFT0.138552s、完整请求6.752074s、Decode55.504078tok/s，复用8203token仅计算4token。Tree热缓存尚未通过，不能把旁路冷测当热缓存对照；Tree C2未测试，Graph内目标验证GPU成本未测。Tree初始化6.262s对K7的6.182s、Graph捕获1.124s对1.107s，没有启动时间优势。温度与内存为不同时间观察值，不能推断散热或能效收益。

当前可用主线基线：**原NVFP4权重＋原FP4激活的数值边界修复引擎，完整27B真实8K已通过**。A16旧生成计划经SHA与无消费者检查后回收，保留全部配置、脚本、日志、成绩与原FP4工作引擎。
原FP4激活修复模式已完成完整27B真实8K：输入8207、输出368，严格质量PASS；TTFT3.862063秒、有效Decode12.419476tok/s。原权重及原FP4 QDQ未改，新增本地逐字节一致的输入边界。CUDA实测仅13.2；不宣称全部13.x兼容或厂商认证。
路线复核记录保留：曾出现MRoPE诊断裁剪、CLI内部参数、快照超内存、插件字段生命周期、内置检查点参数及draft Profile边界问题。已逐项按实际wheel核对；当前阶段以MTP运行时凭据和完整27B构建/配对结果为准。正式ONNX流程同样调用快照插件，不盲换入口或CUDA栈。详见evidence/mtp-route-reassessment.json。
完整27B原生MTP配对8K质量已通过；同输出IDs=True，本单样本Decode变化309.51%；原始计数、GPU阶段范围和全部输出见evidence/native-mtp-paired8k-result.json。不外推一般吞吐或生产验收。 关闭诊断计时的Graph对照已完成；Decode变化11.28%，本样本推荐Graph=True，真实回放与同ID证据保留。
原生GDN＋MTP前缀缓存8K已通过：冷TTFT4.253966秒→热0.139564秒，复用8203、重算4token；base GPU Prefill 3989.515155→101.183487ms。冷/热Decode 49.749008/49.825114tok/s，368输出IDs与原普通/原MTP基线全部相同。真实Graph回放各377次。快照预算约312.52MiB，仍仅单进程、单可信域、重复前缀样本；跨工具/多轮Agent尚未验收。
C2双C1实例功能已通过；共享原生profiling关闭后计时警告217→0，热缓存总有效Decode 49.466116tok/s（修复前44.330559），每请求约24.75tok/s，热TTFT均约0.246秒。每个请求368IDs相同，各复用8203token，实际Graph总回放754次。最低MemAvailable7.651GiB，最高Tj67.718℃。总吞吐未证明超过保存的C1约49.8tok/s，默认并发仍1；原生batch2未验证，混合MTP缓存发布契约目前仅batch1。
底层14SM初始审计：公开CUDA接口读取10个原生捕获图、3196个kernel节点，全部名称解析成功。原GDN MTP每线程200寄存器、每块256线程，理论每SM只能驻留1块，48块至少4批；几何审计不能单独证明耗时占比或提速。NVFP4已使用Blackwell系列块缩放GEMM，kernel名称中的sm100不等于错误架构。CUPTI13.2.86因权限不足35在模型加载前停止；未改权限。初始几何审计最高Tj59.281℃。 随后新增实际T7隔离算子计时：均值0.315651ms，输出与全部7个状态快照参考检查通过，驻留池未改；48层粗估15.151ms、约占保存验证间隔15.62%，只作候选收益筛选。 14SM本地GDN候选现已接入完整27B真实8K：寄存器200→48/线程，算子配对耗时0.313408→0.184486ms。冷Decode51.962、热Decode52.014tok/s，较保存的原GDN单轮约快4.4%；两次368输出IDs与原基线完全相同，实际新GDN图节点48个，每响应377次Graph回放。冷Prefill基座GPU2053.521tok/s，冷TTFT4.254865s、热TTFT0.138301s。保留原GDN回退；选中该8K资格候选，未宣称生产或新后端C2通过。
先完成ABI/原检查点/最小Engine/真实8K，再比较原生NVFP4 GEMM/GEMV、SM110 GDN Decode与内置MTP。
统一验收单请求有效Decode、C1/C2总吞吐、TTFT、冷Prefill、热缓存Prefill；基础8K稳定后再比较DFlash2/外部Draft等加速。
vLLM的实测收益保留为对照，不能替代Edge主线验收；所有8K加速比较结束后才考虑200K。

已完成：复用 A1 Kernel6.8.12 +R39 NvGPU595.78 +原生 CUDA13.2U2 基础计算结果；未重复旧 PASS。
SM110 上 NVRTC+nvJitLink、BF16/FP8/NVFP4 cuBLASLt 计算与 CPU 参考一致；TensorRT10.16.2.10 矩阵乘法及 Edge0.11.0 的 CuTe LayerNorm 实机通过。
这些是组件结果，不能冒充 27B 生成、整模型提速或生产验收。

唯一模型：`nvidia/Qwen3.8-27B-NVFP4@fed99d815f4e8c7c616dd3dd6780076e26d5fb61`。
三分片 20.42GiB，2194 张量，401 量化层（208 FP8、193 NVFP4），48 GDN+16 完整注意力，含原模型 MTP 与视觉。
E 盘只读核验并直接传车机；D 盘未复制完整模型。源盘 exFAT 的 Full Repair Needed 仍存在，本任务未写入或修复 E 盘。

持久部署：`/zeekr_data/nvidia-native-ai-v2/models/nvidia-Qwen3.8-27B-NVFP4-fed99d`，19 个文件 SHA 全部一致；隔离运行库也已落到新目录。
部署后持久可用 36.45GiB，原主数据/R4/Golden/API/固件未覆盖。
用户已明确免除逐项授权，后续继续在本目标范围推进。

原 FP4 激活路径的完整 64 层文本引擎构建状态：**PASS_FULL_LLM_ENGINE_BUILD_ONLY**。
192.0.2.165 已成功构建 17,599,439,228 bytes 的完整 Engine；修复了原写出路径的整份 bytes 拷贝峰值，并实测原生流式写出回调。
该原精度 Engine 能反序列化；但 USER_MANAGED 执行上下文创建发生 SIGSEGV，该路径尚未产生模型输出。
相同阶段已通过 GDB 及独立 Python 加载路径定位，故不能把编译成功计为 27B 兼容成功。
按 Edge wheel 配套版本隔离部署 TensorRT10.16.0.72，已完成匹配的 17,599,751,492 bytes 完整 Engine 构建（472.13秒）。
匹配版本的原生初始化仍 SIGSEGV(-11)，8.00秒内退出，最低 MemAvailable约37.99GiB，最高Tj58.187℃，没有生成任何 token。
独立 STATIC 上下文也崩溃，排除仅由 USER_MANAGED 分配方式导致；流式写出和版本配套修复均已落地，但不能解决现有上下文故障。
小型 Edge W4A16 GEMV(M=1)与GEMM(M=128)结果误差0；小型GDN预填充8步与解码1步均通过CPU数值参考。这些结果不代表完整模型兼容。
官方 `--num-decoder-layer 1` 原权重诊断图构建成功（982,443,228 bytes），19个I/O张量仍在上下文创建崩溃。
GDB明确记录libnvinfer内部空指针读取（si_addr=0x10，x0=0，故障指令ldr x0,[x0,#16]）；闭源函数无可用符号，不能臆测具体内部根因。
单变量关闭辅助流已实测aux_streams=0，982,350,388-byte单层引擎仍在同阶段SIGSEGV。该修复无效，不继续完整模型重编。
新增隔离输出 `/zeekr_map/nvidia-native-ai-v2/`，原 thor-ai 数据目录保留；主数据和 Map 两个卷分别执行12GiB保护线。
CUDA13.2 配套 cuBLASLt 独立版本为13.4.1.3，不能据此称为 CUDA13.4。
Edge wheel 使用原 NVIDIA SM110 二进制，版本0.11.0；源 tag95515c2与wheel编译revision74f8732分别记录，未混称。
实际平台仍是 DRIVE7.0.3 +R39 NvGPU，使用明确标注的本地实验平台绑定；没有伪装为官方 DRIVE7.2/Jetson 平台认证。
CuTe DSL4.7.1的原生FA4已在真实SM110/14SM、head256/GQA6/pagedKV下即时编译执行，CPU参考最大误差0.000189。编译前端报告CUDA13.3；实际CUDA运行库仍13.2.86，未新增第二套CUDA运行库。

保护线：MemAvailable≥5GiB、GPU可用≥2GiB、Tj<95℃、车机持久可用≥12GiB、D可用≥10GiB。
BPMP thermal 观察模块匹配6.8.12 CRC与vermagic，只恢复温度观察；未替换 GPU 驱动/固件/中断方案。
设备仍为 A1 RAM 启动，boot_id `9d74daba-0347-489c-9192-2d117806cbe7`。独立冷启动 **NOT_PROVEN**。
设备 RAM 系统时钟未校时；日志1970时间为该启动时钟，排序采用 uptime 与本机采集时间。

|冻结对照|Prefill tok/s|Decode tok/s|TTFT s|完整请求 s|
|---|---:|---:|---:|---:|
|R4 V45 8K|1240.923|55.227|6.630|13.076|
|R4 V45 200K|659.636|35.061|296.958|301.239|
|NVIDIA27B 8K（MTP OFF）|1271.835*|12.224|6.483|36.507|
|NVIDIA27B 8K（vLLM Graph ON /MTP OFF）|原生阶段口径|12.463|7.299|35.062|
|NVIDIA27B 8K（vLLM Graph ON /MTP K7）|原生阶段口径|50.787|8.488|14.775|
|Edge NVFP4-A16 8K（Graph OFF /MTP OFF）|GPU阶段计时未采集|11.087|4.980|38.085|
|Edge NVFP4-A16 8K（Graph capture成功 /MTP OFF）|GPU阶段计时未采集|10.939|5.070|38.620|
|Edge 原FP4激活数值边界修复8K（Graph OFF /MTP OFF）|GPU阶段计时未采集|12.419|3.862|33.414|
|Edge 原FP4 8K（MTP_OFF，诊断事件ON）|2097.013**|11.750|3.954|35.191|
|Edge 原FP4 8K（MTP_ON_K6，诊断事件ON）|2107.622**|48.115|3.916|11.545|
|Edge 原FP4 8K（MTP_K6_GRAPH_OFF，诊断事件OFF）|未计时|43.597|3.940|12.360|
|Edge 原FP4 8K（MTP_K6_GRAPH_ON，诊断事件OFF）|未计时|48.517|3.900|11.466|
|Edge 原FP4 8K（原生缓存 COLD_CACHE_EMPTY）|2057.142**|49.749|4.254|11.633|
|Edge 原FP4 8K（原生缓存 WARM_SAME_PREFIX）|39.532**|49.825|0.140|7.507|


原普通解码Engine的12.419476tok/s保留。新MTP Engine关闭MTP的11.749563tok/s是另一编译Profile及诊断输出下的对照，下降5.39%；各项开销尚未隔离，不能全归因于计时。启用内置MTP为48.115256tok/s，原始计数accepted314/proposed324=96.91%，同368个输出IDs。
**GPU冷Prefill数值只计base Engine区间，不能与R4或vLLM阶段口径直接比较。draft Prefill位于首token之后，不能将其简单加到TTFT。有效Graph配对只关闭新增诊断事件，保留原生profiling以获得验收计数，须以该配对的OFF/ON判断Graph收益。首次关闭profiling导致原生计数全零，已保留失败记录，不将其速度作为完整验收结果。

V45 runtime SHA `3f0a46a4982a358f7fb5137944cd6a5a13aac3beed8e9c618e5ec700acbe8468`。
对照来自其冻结非 thinking fixture；未重跑 R4，未将已拒 GEN276 的质量或成绩归给 V45。
V45启用线性K7；本次NVIDIA基线MTP OFF，输出368而V45为357 tokens。*NVIDIA Prefill为原生调度阶段口径，不能据此宣称对R4的因果性能提升。
新增Graph-only与Graph+MTP K7均输出347 tokens且token IDs逐一相同；K7有效Decode为前者4.075倍，最高Tj67.062℃。
这是单个冻结8K样本的实测，不外推为一般文本吞吐。K15虽测得64.368tok/s，但把opening键写成.opening，严格质量FAIL，弃用。
原生MTP计数draft302/accepted305存在截断边界不一致，保留原始值，不能报告超过100%的接受率。

已实测的8K/64K与GDN、PagedKV、JSONSchema、FA4、原生MTP和重复前缀缓存范围见组件矩阵；200K暂缓，FP8KV、DFlash2、C2、Tools/Streaming/Agent、视觉、API/恢复/冷启动仍须逐项验收。Graph和Prefix按各自独立配对凭据判决。
未验收项见唯一组件矩阵 `COMPONENT_MATRIX.csv`；注册插件或存在配置字段不算功能 PASS。

vLLM审计找到精确NVIDIA权重变体；正式0.31.0 ARM wheel在本机完成官方SHA核验和ELF检查，核心库包含SM110 Cubin并依赖CUDA13。
该原包已隔离部署到车机，仍只使用唯一原模型权重；本机运行结果与主机二进制检查分开记录。
Torch2.13.0+cu130与Triton3.7.1已部署到新Map目录，原生FP16矩阵计算和Triton即时编译均通过实机CPU参考。
实际加载库已确认：原R39 libcuda、cudart13.2.86、cuBLAS/cuBLASLt13.4.1.3、NVRTC/nvJitLink13.2.86；编译版本cu130不冒充实际运行版本。
最小原生C编译器/Python3.12头文件已通过本机真实编译链接；ptxas使用经官方SHA核验的CUDA13.2.86。
vLLM原包保持不改，使用标准platform_plugins入口绑定本启动已验证的DRIVE/SM110/14SM CUDA平台。当前PCI入口实际枚举10de:22e6，不能拿历史2B00标记替代当前PCI枚举。
完整27B文本模型现已在实机生成并通过基础中英JSON、金额、8K与64K锚点质量检查。
实际GPU参数20,150,573,584 bytes；融合后129个CutlassNvFp4LinearKernel、128个CutlassFP8ScaledMMLinearKernel及96个未量化小门控线性层均记录，模型无CPU卸载。
原始表格冻结样本在256-token上限被缩进/换行截断，保留FAIL；不含答案枚举的JSONSchema紧凑格式变体以182 tokens通过，不冒充原始格式PASS。
8K：输入8207、输出368，TTFT6.482876秒，解码12.223613tok/s；64K：输入65112、输出34，TTFT176.765032秒，解码9.980348tok/s。均为MTP/Graph/Prefix OFF。
200K原Triton路径触及900秒总时限停止；FA4新路径短解码通过，但200K在182.03秒达到95.218℃触发保护。两轮均无完整200K输出，不能报告PASS；后者当前阻碍是持续满载散热。
vLLM Prefill为原生scheduled-to-first-token阶段时间，包含首token计算；R4等价GPU-eval计时未证明，不混用两种口径。
原始权重未改；实际运行分派以本次ModelOpt配置与内核记录为准，历史recipe的W4A16描述不能替代本次执行记录。
原config.json明确group_0权重/激活为静态FP8，group_1权重/激活为静态FP4、group16；ignore为mtp*和mtp.layers.0*。本次实际为混合FP8与NVFP4原生计算，不能概括为全模型W4A16。
DFlash2需要额外drafter，当前固定权重条件缺少该关键条件；不能把原模型MTP张量存在计为MTP推理通过。

以下保留旧无边界图的诊断历史；新增数值边界修复的当前判决见开头。已确认TensorRT Python10.16.0.72与实际单一libnvinfer API101600一致。保留982443228-byte旧计划映射仍SIGSEGV，streamable_weights=0，未证明与缓冲区生命周期有关。
仅固化原值FP16门控权重得到983421948-byte一层图（I/O19→17），仍在上下文创建SIGSEGV，此修复无效。
不含Edge自定义节点的TensorRT FP8 QDQ GEMM（N5120/K6144，M1/8）已真实执行且CPU参考误差0，不能把整体问题笼统归为FP8不支持。
原始官方IHostMemory序列化一层对照已完成（982378348 bytes），跨进程上下文仍SIGSEGV；移除流式适配器和显式创建CUDA主上下文均未修复。
已通过跨进程数值核验：NVFP4 W4A16、GDN小图、ALIASED_PLUGIN_IO配置对照、实际10240通道/width4状态卷积、模型实际16个QK头/48个V头的GDN双Profile切换（8步Prefill与1步Decode）。这些是组件证据，不能冒充完整8K。
原TensorRT FP4 QDQ路径也已独立通过N128/K128、M1/M8，CPU参考误差0；不能笼统归因为NVFP4/FP8或GDN不支持。
省略词表投影的一层图267097644 bytes仍在上下文SIGSEGV；进一步省略MLP/post-attention norm后，原权重GDN复合子图116085908 bytes的跨进程上下文创建通过。范围收敛到加入MLP及其归一化/编译融合交互，尚非已证明的闭源内部根因。
保留原精度的async_policy0编译策略实测无效，982360548-byte一层图仍SIGSEGV。
NVIDIA原包NVFP4-A16仅替换MLP路径后，986583372-byte完整单层图首次创建上下文成功；原生LLMRuntime实测13-token Prefill及4-token Decode成功。原始FP4权重不变，MLP激活由FP4改为FP16，不能冒充原W4A4路径PASS；单层输出不作质量判决。
完整64层8K候选已完成构建及真实生成验证；192个MLP线性层使用NVFP4-A16，其余208个FP8投影、原NVFP4 LM-head与所有GDN保留，版本与精度差异单独验收。
完整候选实测构建成功：17,886,857,140 bytes，SHA256 `969f425e3235d3669bdcb020035639fc704ba1e8d4351342fcaaf91d7e9d5072`。
原生Edge LLMRuntime现已完成完整27B真实8K：8207输入/368输出，严格冻结质量PASS；TTFT4.980294秒、有效Decode11.086611tok/s、请求38.084701秒。作业总峰值Tj79.843℃，未触发保护。
与vLLM原8K基线的368个输出token IDs逐一相同；本单样本TTFT降低约23.18%，Decode较12.223613tok/s下降约9.30%，不能宣称整体提速，也不把TTFT倒数冒充GPU Prefill速率。
Edge官方CUDA Graph API返回true且完成同一8K质量检查；输出token IDs仍逐一相同，Decode10.939426tok/s、TTFT5.070234秒，观察到Decode下降1.33%。保留配置/原始结果，默认Graph OFF，未单独计数实际replay。
尝试保留原FP4线性权重/激活、使用TensorRT官方mark_debug限制3个MLP输出融合，接口接受但随后的TensorRT构建SIGSEGV，无生成引擎。该mark_debug方案NO-GO；具体闭源内部根因未确认，不能将NVFP4-A16成功冒充原W4A4兼容PASS。
保留原FP4精度的NVIDIA CuTe GEMM插件在N256/K256、M1/M128跨进程数值误差0，但替换真实单层3个MLP GEMM后，上下文仍SIGSEGV；此路径未获准完整模型重建。
本轮新增数值一致的MLP输入边界：本地C++ V3插件仅执行CUDA逐字节拷贝，不改变原FP4权重、激活QDQ或校准尺度；逐字节随机FP16位型（含NaN载荷）跨进程通过。982829548-byte完整单层图上下文首次在原FP4激活精度通过，原生13-token Prefill/4-token Decode也通过。
原FP4激活修复模式已完成完整27B真实8K：输入8207、输出368，严格质量PASS；TTFT3.862063秒、有效Decode12.419476tok/s。原权重及原FP4 QDQ未改，新增本地逐字节一致的输入边界。CUDA实测仅13.2；不宣称全部13.x兼容或厂商认证。
修复后的完整引擎：17601822188 bytes，SHA256 `24c6084b9ce6b4c097c0785cf557b108f4edb8918bd3f93b4ba965b43f212261`；目录 `/zeekr_map/nvidia-native-ai-v2/engines/candidate-fp4-boundary-c1-8k`。本地边界插件已持久保存在独立runtime/repairs/fp4-boundary-v1，源码/二进制SHA及原始失败复现均保留；独立冷启动尚未验收。
本轮与A16及vLLM原8K的368个输出token IDs逐一相同；有效Decode较A16的11.086611tok/s提高12.02%，TTFT下降22.45%。这是同一冻结样本的一轮实测，不外推一般吞吐；GPU阶段Prefill计时仍缺。详见evidence/edge-original-fp4-8k-comparison.json。
当前唯一下一步：Repair the native Tree HybridMTP split-Prefill/PrefixCache interaction with targeted component state/logit comparison;preserve qualified bypass8K and K7 without rerunning their accepted fixtures。不重测已通过的K7及Tree旁路8K。200K/DFlash2/外部Draft当前不执行。
空间处理：先前回收本任务旧10.16.2失败运行的17599439228-byte生成引擎。本轮原FP4修复单层通过后，又复核旧Map完整失败引擎17599751492 bytes的SHA与无消费者状态后回收，该历史阶段保留A16引擎、原模型、复现小图/日志和R4/Golden；当前A16生成计划状态见开头与evidence/native-mtp-full-space-preparation.json。旧回收凭据为evidence/native-fp4-full-space-preparation.json。
外置风扇/散热器由用户确认存在。95℃为任务自设保护线；实际tj-thermal为全芯片最高温，Linux仅暴露125℃critical阈值，不能据此许可125℃持续运行。
Linux没有风扇转速/PWM接口；定制MTS MCU未公开官方开发板fan命令。尚缺满载分区温度/功耗，不能仅凭95℃峰值认定GPU散热根因。
[官方Edge0.11矩阵](https://nvidia.github.io/TensorRT-Edge-LLM/0.11.0/user_guide/getting_started/support-matrix.html)列DRIVE7.2/CUDA13.3，本机仍是DRIVE7.0.3混合R39/CUDA13.2实验栈，不宣称厂商认证。
[TensorRT11 DRIVE迁移文档](https://docs.nvidia.com/deeplearning/tensorrt/11.4.0/api/migration/tensorrt-10x-to-11x-driveos.html)要求较新DRIVE7.2.x和CUDA13.3U1或更高，不能将通用SBSA包直接混装为本机官方升级。

流式构建使用 NVIDIA [Builder API](https://docs.nvidia.com/deeplearning/tensorrt/10.13.2/_static/python-api/infer/Core/Builder.html)；实际部署版本和回调行为以实机记录为准。
