# Thor-U 架构图：6.1 Golden + 6.8 实验内核 + NVIDIA Edge AI

> 读图规则：**实线表示已经出现过的功能链路或已知组件依赖；虚线表示历史条件执行/未来设想**。PASS 只能用于限定的历史实测。不要把图中“目标路径”理解为已经配置完成的双启动系统。

## 1. 引导与运行时分层

```mermaid
flowchart TB
    F["原厂 Boot ROM / 安全链 / Hypervisor<br/>受 OEM 控制，保留原件"]
    G61["原厂 GOS 6.1.119<br/>DriveOS 7.0.3 · Golden"]
    S61["原厂 / R4 既有服务<br/>根分区与恢复资源受保护"]
    K68["实验 Linux 6.8.12<br/>A1 kexec RAM 暖启动 PASS"]
    IVC["6.8 Guest Hypervisor / IVC / vblk<br/>需要匹配 DTB / initrd / ABI"]
    NGPU["NVIDIA R39 NvGPU 595.78<br/>DRM / host1x / GSP / INTx"]
    CUDA["CUDA 13.2 U2<br/>A1 基础数值计算 PASS"]
    TRT["TensorRT + Edge-LLM<br/>27B NVFP4 8K 范围性资格结果"]
    COLD["未来：独立 6.8 冷启动入口<br/>NOT IMPLEMENTED / NO-GO"]
    BOOT["OEM 槽位、签名、恢复验证<br/>宿主侧资料未闭环"]
    F --> G61
    G61 --> S61
    G61 -. "历史维护窗口：kexec<br/>非持久双启动" .-> K68
    K68 --> IVC --> NGPU --> CUDA --> TRT
    F -. "仅在官方受支持路径通过后" .-> BOOT
    BOOT -. "满足所有 Gate 才允许" .-> COLD
    COLD -. "与 A1 不是同一验收" .-> K68
    classDef done fill:#dcfce7,stroke:#228a50,color:#19482c;
    classDef waiting fill:#fef3c7,stroke:#b45309,color:#713f12;
    class G61,K68,CUDA done;
    class COLD,BOOT waiting;
```

**状态解释：**6.1 Golden 的历史只读取证与 A1 6.8 RAM 会话均已存在；但“可选择的第二个 6.8 永久启动项”从未成功安装或验收。历史断电回到 6.1 的证据不等于未来任何系统状态下都能自动回退。

## 2. 从 6.1 新增 6.8 的两条路径（不可混称）

```mermaid
flowchart TD
    A["原有 Linux 6.1<br/>不覆盖原厂 boot / DTB / rootfs"]
    B{"6.8 安装模式"}
    RAM["模式 R：kexec 到 RAM 6.8<br/>A1 已证明特定会话"]
    RC["模式 C：官方 RAM cold boot<br/>需 SDK / RCM / 签名 / 物理通道"]
    ADD["模式 P：6.8 独立持久启动项<br/>目标；尚未实现"]
    CHECK["只读确认 boot slot + OEM policy<br/>6.1 恢复、物理救援和冷启验收"]
    HOLD["未闭环：停止，不执行启动写操作"]
    A --> B
    B -->|现有历史| RAM
    B -->|备选研究| RC
    B -->|长期目标| CHECK
    CHECK -->|任意门失败| HOLD
    CHECK -->|全部真实 PASS 之后| ADD
    classDef blocked fill:#fef3c7,stroke:#b45309,color:#713f12;
    class ADD,RC,HOLD blocked;
```

- **模式 R (RAM kexec)：**两个内核不会同时运行；6.8 被当前 6.1 交接进入 RAM，未新增永久启动项。kexec 是一次状态转移，不能假定任何重新启动都回到 6.1。
- **模式 C (cold RAM)：**与模式 R 不同；需要 OEM 支持的主机侧 RAM 加载流程。历史公共 RCM USB 物理传输面不可达，不得宣称本机已有此功能。
- **模式 P (独立持久)：**必须先用官方/获授权工具确认真实启动链和可用的独立装载入口（不假定 EFI、GRUB 或可见 A/B Guest 槽位），再设计非覆盖的 6.8 自有镜像位置与启动选择/回滚。当前是设计目标，代码仓库不包含可执行安装器。

## 3. GitHub 工程结构

```mermaid
flowchart LR
    SRC["PC 离线原始来源<br/>Kernel / ABI / Edge 证据"] --> REPO["GitHub 私有研究库<br/>源码和 SHA 清单"]
    REPO --> DOC["docs/<br/>安装与状态说明"]
    REPO --> PATCH["patches/ + src/<br/>差异和研究脚本"]
    REPO --> EVID["evidence/ + manifest/<br/>限定验收与完整性"]
    REPO --> PREF["tools/preflight<br/>仅只读，不能激活内核"]
    MODEL["原厂固件、NVIDIA 软件包、模型/Engine<br/>合法独立来源，非 GitHub 归档"]
    MODEL -. "离线版本与 SHA 匹配" .-> TARGET["受控车机目标环境<br/>内核、GPU、CUDA、Edge 分门验收"]
    PREF --> TARGET
```

## 4. 决策与取证边界

| 条件 | 现状 | 允许行为 |
|---|---|---|
| 6.1 Golden 原厂内核/只读分区 | 历史取证 PASS | 只读对比，不覆盖 |
| 6.1 -> 6.8 RAM kexec | A1 历史 PASS（限具体会话） | 记录证据；不得从文档自动重做 |
| R39 GPU + CUDA 13.2 | A1 基础计算 PASS | 仅在隔离维护窗口做后续资格化 |
| RCM 冷 RAM | 公共 RCM 传输面 FAIL；官方工具依赖未闭环 | NO GO |
| 6.8 独立持久启动与菜单 | NOT IMPLEMENTED | NO GO，禁止猜测槽位和写入 |
| Kernel 6.8 + Edge-LLM 生产切换 | 完整质量和冷启动仍 NO GO | 保留现有生产环境 |

技术方案、门槛和回退依赖见 [BOOT_6_1_TO_6_8.md](BOOT_6_1_TO_6_8.md)；用户操作路径见 [INSTALL_ON_THOR.md](INSTALL_ON_THOR.md)。
