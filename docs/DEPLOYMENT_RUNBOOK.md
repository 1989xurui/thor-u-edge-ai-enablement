# Thor-U 全流程安装与部署 Runbook（分模式执行）

**复现资源与许可证：**[官方下载与 SHA256 校验指南](DOWNLOAD_AND_REPRODUCE.md) · [项目 MIT 原创授权](../LICENSE) · [NVIDIA/第三方许可排除](../THIRD_PARTY_NOTICES.md)。先下载/核验，不等于已经取得 OEM 6.8 独立冷启动资格。

**用户诉求：从原厂 6.1 基础上增加 6.8，然后加载 R39/CUDA 并运行 Edge-LLM。** 但不能把“复制 Git 源码”“通过 RAM kexec”“持久双启动安装”混为同一事件。

## 安装模式总表

| 模式 | 当前事实 | 操作者能做什么 | 阻断 |
|---|---|---|---|
| D0：安装 GitHub 工程资料 | 公开仓可匿名克隆 | clone + SHA + 只读检测 | 需 Git/HTTPS 网络或可信离线副本 |
| D1：在现有 6.8 RAM 实验会话研究 | A1 历史 Kernel/GPU/CUDA PASS | 当下设备复核、隔离维护后单项资格 | 冷重启/无人值守 NO GO |
| D2：从 6.1 kexec 到 RAM 6.8 | 历史实现过 | 仅审查原始工程、恢复、单次执行 Gate | 不能当万能安装方法 |
| D3：OEM RAM cold boot 6.8 | 当前平台工具/物理通路阻断 | 离线对齐官方支持与 board/signature | NO GO |
| D4：持久增加独立 6.8 启动项 | NOT IMPLEMENTED | 只读 OEM boot slot/签名/物理恢复调查 | NO GO |
| D5：Edge 27B 生产发布 | 8K 限定资格 | 新隔离 Candidate，分层验收 | 全量质量/长稳/回退未完成 |

## 第一部分：开发电脑下载与核验（安全）

公开 GitHub 仓库可直接通过 HTTPS 匿名读取：

~~~sh
git clone https://github.com/1989xurui/thor-u-edge-ai-enablement.git
cd thor-u-edge-ai-enablement
python3 tools/verify_manifest.py
python3 tools/check_repo_release.py
python3 tools/check_program_readiness.py --summary
~~~

公开仓库正常无需 GitHub 账号或 Token；请勿将访问凭证写入仓库或脚本。上述动作均不触及车机。Program Gate 的 HOLD 是当前准确结果。

## 第二部分：在目标车机“安装研发资料”，不是安装新内核

先使用已有安全现场链路进行**只读**设备识别：

~~~sh
uname -m
uname -r
cat /proc/sys/kernel/random/boot_id
grep -E 'MemTotal|MemAvailable' /proc/meminfo
df -h /zeekr_data /zeekr_map 2>/dev/null
~~~

如果车机能通过 HTTPS 访问公开仓库，且有足够持久空间、不会影响正在运行的系统，才在新、未占用的隔离目录克隆：

~~~sh
# Do not run against the OEM read-only root; dedicated persistent data only
git clone https://github.com/1989xurui/thor-u-edge-ai-enablement.git \
  /zeekr_data/thor-u-edge-ai-enablement-src

cd /zeekr_data/thor-u-edge-ai-enablement-src
python3 tools/verify_manifest.py
bash tools/preflight_thor_readonly.sh
~~~

执行结果是文档、源代码、证据和检查工具落地，不会修改 Boot ROM/DTB/Kernel/GPU 驱动、不会编译/加载 Engine、不具备第二永久启动环境。

## 第三部分：目标仍是原厂 6.1 时的正确推进

**P00 Golden → P01 救援 → P02 离线准备 6.8 → P03 Guest/IVC DTB → P04 独立启动 Gate。**

在 P04 的真实 OEM slot、签名、board config、USB/MCU 和冷恢复没通过前，允许继续做的仅是源码/物料/boot 模式只读调查和模拟流程。即使 Image/DTB 已备好，也不得写 OEM boot slot/firmware、kexec、tegrareset 或假装存在 PC GRUB/EFI 双启动。

参考 [6.1→6.8 增量设计](BOOT_6_1_TO_6_8.md) 与 [历史 G4D 失败证据](evidence_history/G4D1_PUBLIC_RCM_AND_BARRIERS.md)。

## 第四部分：目标已经是经过授权的 RAM 6.8，会话内 GPU/CUDA 接入

1. 不凭历史 boot_id 认当前系统。重新在现场只读读取 Kernel release、boot_id、原根只读状态、GPU/UMD/firmware 与网络资源。
2. 确认独占维护 owner、在途请求清空、原 R4 Golden/生产不被影响。启动 guard 未绑定当前 boot_id 时即 HOLD。
3. 对照 A1 证据做模块 CRC/vermagic/firmware identity 和 CUDA libcuda/cudart 版本锁，不通过不装载。
4. 只有获得一次受控、可恢复的实际 GPU 单轮验证资格，才在隔离窗口运行相关准入脚本。仓库**没有自动装驱动/重启/激活器**。
5. 原始目标 rootfs、固件和车控资产只读/不变，保证失败候选可单独停止，不能自动“恢复”到错误的 OS。

## 第五部分：TensorRT Edge-LLM 安装分叉

**官方支持场景**：NVIDIA DRIVE Thor / DriveOS 7.2 / CUDA 13.3，官方手册指定在 DriveOS SDK 容器内编译后部署到 target，CMake EMBEDDED_TARGET=auto-thor。此路线可能需合法 SDK/权限，与现有 7.0.3 车机不是同一个环境。

**本机实验场景**：6.8 RAM + R39 595.78 + CUDA13.2 / TensorRT10.16.x / Edge0.11.0。离线锁住 installed wheel、TensorRT plugin 和 NVFP4 权重，再隔离构建 target-only 8K → 原生 Draft/K7 → Graph/Prefix → Tree 候选，**不覆盖已有引擎**。如果已有历史 K7 资格和 SHA 一致，复用测试；不要重新编几十 GiB 或启动新的 200K 测试来凑“安装成功”。

官方 CMake 示例（仅适合真实 DriveOS 7.2 SDK 环境；不是当前自定义组合的安装命令）：

~~~sh
cmake -S . -B build \
  -DCMAKE_BUILD_TYPE=Release \
  -DTRT_PACKAGE_DIR=/usr \
  -DCMAKE_TOOLCHAIN_FILE=cmake/aarch64_linux_toolchain.cmake \
  -DEMBEDDED_TARGET=auto-thor \
  -DCUDA_CTK_VERSION=13.3 \
  -DENABLE_CUTE_DSL=ALL
cmake --build build
~~~

原环境 CUDA 13.2/DriveOS 7.0.3 不得直接复制此配置假定官方认可。Engine build/target/run 命令应使用版本匹配的实际源码/wheel，以及严格固定的输入/输出记录。

## 第六部分：设备存储、内存与隔离

- 车机可用约58GiB Linux UMA，27B 20.42GiB + Engine 16.39GiB 是**持久磁盘占用**，不是直接的运行 RAM 累加。
- 官方 build 约 20–50GB temporary，历史已有模型/Engine+Draft；部署前在目标持久分区做空间预算，不在只读 OEM 根安装软件。
- RAM/温控守护：MemAvailable≥5GiB、GPU≥2GiB、Tj<95°C、持久余量≥12GiB；单独测量 C1 8K 和后续功能。
- 一套活动 GPU Candidate/Worker；Python/CLI/Script 研究复制不会带来额外模型权重，也不能向生产端口接管流量。

## 第七部分：上线与退出

使用 [ACCEPTANCE_AND_RELEASE.md](ACCEPTANCE_AND_RELEASE.md) 的严格 8K→MTP→Tool→缓存→持续性能→故障/恢复→冷启动/生产 Gate。缺失任何一环即报告 **EXPERIMENTAL_NOT_FOR_PRODUCTION**，并保留原系统/R4/Golden。

对于真正持久 6.8 双启动，需要回到 P04/P11：独立 OEM boot chain、双向 cold boot、故障回退、签名合法性。当前即使 GitHub 安装与模型 8K 资格 PASS，也不能据此宣称 D4/D5 通过。

### 不应执行的命令类别

未经真实冷启动/恢复/OEM 授权，禁止 flash/bootburn/kexec/tegrareset、改分区/slot、覆写 OEM DTB、替换固件、在生产时运行 nvidia-smi 初始化测试或重启在途模型。参考仓库中历史源码不可直接复制即运行；LAN IP 曾被脱敏，需自行合规重新配置。

完整工程恢复见 [RECOVERY_AND_TROUBLESHOOTING.md](RECOVERY_AND_TROUBLESHOOTING.md)。
