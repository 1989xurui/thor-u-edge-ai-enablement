# 故障恢复、问题诊断与禁止误操作

## 1. 恢复优先级

**原版 6.1 Golden > 车载安全和网络/物理救援 > 实验 6.8 内核 > NVIDIA CUDA > 27B 性能。** 任何实验不能牺牲原厂恢复通道。

原厂 6.1/DRIVE 7.0.3 的 boot+Hypervisor+RO root 不属于此次 GitHub 交付。历史若出现 kexec RAM 会话异常，有过人工通过 MCU reset/断电返回 6.1 的证据，但**不保证任意冷启动故障均可自动恢复**。实际硬件、现场串口、网络、Golden 来源和启动链必须在每轮开始前复核。

## 2. 按第一故障分类处理，而不是盲目重复测试

| 现象 | 历史首次原因或待判因 | 正确处理 | 禁止做什么 |
|---|---|---|---|
| 6.8 kexec 后 EL2/PMC scratch fault | 6.8 DT aperture / scratch 写权限不匹配 | 回到已冻结 DTB 历史证据，只做离线单变量对照 | 改 EL2 权限、跳过 guard |
| 6.8 boot 进入但 HVD/IVC/vblk 全无 | tegra_hv_ivc 节点缺失导致新机器驱动未绑定 | 核对 G4E2 6.8 DTB 的 compatible 和实际载荷 SHA | 乱改 Hypervisor、重新格式化盘 |
| kexec 传入自定义 DTB 却仍是旧 DT | 历史 kexec-tools 参数解析/seed 门 | 记录版本、真实 DT 读取 Hash，离线诊断 | 把 LOAD_RC=0 当作真实生效 |
| RCM 设备进 recovery，但 PC 不识别 APX | 该机可接 USB-C 非 Thor xudc 设备口；公共 RCM FAIL | 停止公共 USB 路线，等待授权 OEM/MCU 通路 | 用 Jetson T4000 BCT 假装 P3960 |
| 官方 boot slot / 第二链不明 | HOST_ONLY、GPIO 模式推断、OEM 签名/HSM 依赖 | 只读 OEM 资料核对，保留 6.1 | 猜 A/B 槽位、写 BCH/BRBCT |
| OpenRM/GSP 曾报 0x83d | 老 Phase27-31 未定位全部固件/内存交接，存在多种可能 | 用后来的 A1 实测和当前精确 boot_id 区分 | 把老失败当永远失败，或忽略所有相应风险 |
| NvGPU 加载但 CUDA 返回初始化错误 | 可能缺 libnvcucompat、host1x/DRM 依赖或板级固件路径 | 逐项核同版 UMD/CRC/firmware 路径和原始日志 | 换签名、改 firmware 名称/来源掩盖 |
| TensorRT Engine 可 build，runtime SIGSEGV | 历史 10.16.x 与插件/USER_MANAGED/上下文异常 | 对比 Engine 与实际 wheel/SONAME，保留 GDB 证据；小样排因 | 报“已通过整模型”或继续盲目全量重编 |
| Tree 输出不一致、热缓存异常 | Hybrid MTP Prefix/GDN/Conv 状态与缓存边界未全合格 | 恢复冻结 K7、隔离单个失败场景、对照 ID | 用 57 tok/s 单样替换生产 |
| 27B OOM、MemAvailable 逼近 5GiB | 权重/Engine/Draft/KV/Graph 共同占 UMA | 只停新 Candidate、释放其独立资源，核对当前内存 | 同机加第二 Worker、盲目 kill 原服务 |
| E/D 主机路径/文件不一致 | 旧 D Junction 指向 E，迁移/卷历史问题 | 校验真实目标与 SHA、保留 manifest | 重复归档 Junction 或删源数据 |

## 3. 统一故障闭环

1. **STOP**：保留现场，不自动无限尝试。先确认是否仍有车辆/生产关键进程请求，限制高风险动作。
2. **CAPTURE**：记录 boot_id、Kernel、执行时间(可能车机 RAM 时钟显示 1970，应带 uptime)、单一候选 PID、退出码和对应标准输出/错误。
3. **CLASSIFY**：核对第一失败阶段：Host/Boot/IVC/Driver/CUDA/TensorRT/Checkpoint/MTP/API/Resource。
4. **COMPARE**：以相同 SHA/版本和冻结 Golden/成功 Engine 作单变量对照；不将别的实验会话日志混入。
5. **ROLLBACK**：优先撤销独立实验进程/Engine；Kernel/boot 级问题必须走本设备已经真实资格化的恢复机制，不能假设任意系统都会被 tegrareset 修好。
6. **REPORT**：给出 PASS/FAIL/HOLD、原始证据位置、能否安全重复、下一最低风险验证任务。

## 4. 6.1 与 6.8 双路径恢复不能混淆

### 6.1 → 6.8 kexec RAM
6.1 在发生交接后不再同时运行；6.8 是新的内核运行会话。过去断电返回 6.1 是特定 OEM 启动条件的历史证据。若现场无法确认远程/物理救援能力或 6.1 原厂状态，禁止开始新一轮交接。

### OEM RAM-only cold boot
需经过授权的 DRIVE SDK/MCU/RCM host 方式，正确板级配置/签名和恢复。公共 RCM USB 实测无物理设备通路，不能把新固件盲写到 UFS。

### 真正的 6.1 + 持久独立 6.8
必须有受支持的独立启动入口和 boot owner；否则并不存在“选 6.8 失败自动回原 6.1”功能。此时正确结果是 BOOT_ADDON_BLOCKED，不是发布安装说明与猜测默认启动项。

## 5. 何时请求外部依赖

需要 OEM 签名、P3960 board config、Boot/slot 枚举、DRIVE SDK 专有工具或完整原厂固件，必须走允许的授权渠道，不能公开寻找 OEM 私钥或改安全域来绕过。完全无授权资源时，本项目可以完成离线研究/源码证据归档，但只能保留新的持久双启动门为 HOLD。

## 6. 恢复报告卡（复制此模板）

~~~text
TIME_UTC:
DEVICE_ID_CLASS: Thor T264/P3960
BOOT_ID / KERNEL:
STAGE: P00-P12
CURRENT_HASHES:
OPERATING_MODE: OEM_6P1 / EXPERIMENTAL_RAM_6P8 / INDEPENDENT_6P8
FIRST_ERROR:
RAW_EVIDENCE:
RESOURCE_STATE:
AFFECTED_PRODUCTION_SERVICE: NO/YES/UNKNOWN
GOLDEN_UNTOUCHED: PROVEN/UNKNOWN
ROLLBACK_ROUTE: PROVEN/NOT_PROVEN
DECISION: PASS/FAIL/HOLD
NEXT_SAFE_ACTION:
~~~

出问题时先写结论，后续再定义一次有界实验，不重启运行中的正常生产会话。
