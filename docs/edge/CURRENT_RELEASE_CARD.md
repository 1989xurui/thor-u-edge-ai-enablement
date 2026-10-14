# Thor-U V2.4 当前状态

唯一主线：原始 NVIDIA Qwen3.8-27B NVFP4、TensorRT Edge-LLM、Tree-MTP 8/2/16、FP16 KV。K7/R4 Golden、生产默认及原 Engine 保留；DFlash2 冻结备用。

原 Runtime bb83eafd 的 8K/64K/200K 三个固定召回样例 Token IDs 范围 GO。首次 Verify 已记录 GDN/Conv/Logits 浮点差异，未宣称数值等价。完整质量、持续性能、独立启动/恢复与生产发布仍 NO_GO。

200K 原生历史基线：冷 TTFT 207.9347 秒、Decode 32.3149 tok/s。目标 ≤180 秒及 ≥36 tok/s，尚未达到；本轮没有新增提速成绩。

本轮完成官方 IProfiler 的 Tree 冷 Prefill 诊断，Graph OFF、仅校验每段首 Token。8K 收到1547条层计时；200K输入195686、23个primer加最终请求共24项Token检查一致，48次Base及48次Draft enqueue完整。诊断 Runtime为58bd3b86，原插件8fb2fb35，未重编Engine或数值Kernel。

Base诊断层计时193.686秒，其中Attention101.685秒（52.5%）、Matrix Multiply42.691秒、Fused FC14.160秒、未映射插件16.953秒、其它18.197秒。IProfiler区间不等于独占Kernel时间，不能直接换算原生提速或收益承诺。

200K脚本末尾误把一次请求当作一次enqueue，原FAIL/exit1记录保留。96次enqueue与24项Token检查均已完成，离线按缓存边界的两次enqueue重新核验通过，无需重跑。GPU峰值65.406°C，最低UMA15.747GiB，无新增GPU错误。

全局CUDA拦截器v3虽然通过CPU转发测试，车机却在模型初始化前SIGSEGV；该路线NO_GO并停止使用。官方层Profiler已工作。原插件包含SM110 D256分页变体，但具体实际分派仍待证明；当前源码与原插件完整对应关系未证明，不能盲目替换整个插件。

主机原仲裁器独占心跳已按用户确认恢复到第365代；device_lock_bound仍false，未将旧设备绑定证据报告为当前生产通过。终态GPU无占用、/new_root只读、默认SHA未变，未做中途生产恢复。CUDA13.x通用兼容性未报PASS。

唯一下一动作：用有边界的官方跟踪接口确认原FP16 D256 Attention实际分派及tile配置，再决定一个SM110/14SM候选；不重复完整200K测试、不再使用全局CUDA拦截。

证据：evidence/V24-tree-layer-profiler-v2-200K-offline-adjudication.json。此前历史发布卡保留于evidence/V24-release-card-before-layer-profile-v2.md；BENCHMARK_RESULTS.csv仍26行，未写入诊断耗时。

## 当前 D256 算子判决

原插件的FP16算子与显式NVIDIA SM110因果分页核心已同输入核验。三项小样本和64K/200K缓存规模的8192查询均通过数值门槛；两种显式核心的完整输出逐位一致。14SM及加载内核的binary版本110由公开CUDA接口实际读取。

|缓存档位|原插件pipeline ms|uniform因果core ms|packed因果core ms|packed耗时变化|
|---|---:|---:|---:|---:|
|64K|162.756|161.137|161.991|+0.530%|
|200K|504.518|502.525|505.880|+0.668%|

两种core按五组交替A/B采样，GPU时钟一致。packed切换NO_GO；原插件含QKNorm/Rope/KV更新，跨pipeline/core差距只是理论上界，不能报告为净提速。GPU峰值63.812°C，无新增GPU错误。未重测整模型性能或完整质量。

CUPTI无上下文准入成功，但真实CUDA上下文的callback注册返回35（INSUFFICIENT_PRIVILEGES）；推理请求未执行，未修改权限。原整模型内核分派仍未证实，不能用单算子调用替代该证明。

已提取并反汇编实际调用的固定AOT对象：因果uniform核心168寄存器/线程、本地1320字节/线程，静态504条LDL和367条STL；这些不是动态耗时比例，部分可能仅属于尾部/回退路径。此前noncausal dense入口误选及ELF程序头截断均为诊断工具错误，原始失败记录保留，已修正。

下一唯一候选：C1/Hq24/Hkv4/D256/14SM与nativeNHD strides常量专用化，保持现有FP16数学和因果mask。源码仅已准备，尚未AOT编译或GPU验证；先修复隔离的主机编译依赖并生成一个候选，再由实际SASS/数值/净收益决定是否继续。原模型速度仍沿用207.9347秒/32.3149tok/s；180秒/36tok/s目标未达到。
