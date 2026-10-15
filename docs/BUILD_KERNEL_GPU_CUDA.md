# 从原厂 Linux 6.1 到 Kernel 6.8.12、NVIDIA R39、CUDA 13.2 U2 的工程流程

**这是一份离线构建和受控实机资格验收手册，不是可直接刷写车机的自动安装器。** 没有冷启动/签名/恢复前不得用它在车机执行 kernel activate、kexec、tegrareset、flash、bootburn 或 insmod。

## 1. 原厂 6.1 的真实平台限制

GOS 6.1.119-rt45-prod-rt-tegra 来自 DriveOS 7.0.3 OEM Boot/Hypervisor 链，根分区 /dev/vblkdev0 历史是 4GiB ro。Host-only 启动槽、签名、GIC/ITS/IVC 都不是普通 PC 的 GRUB/EFI 场景。

旧 DT 与 6.8 新 tegra_hv_ivc 机器驱动不同，G4E2 研究定位兼容节点缺少，后来通过 RAM DTB 单变量实验令 IVMK/IVC #59..80、vblk 和 /new_root ro 双轮通过；不能拿原 6.1 DTB 直接启动新内核。

## 2. 核心源码/工具

已纳入 GitHub 的历史主机脚本：

- src/kernel-gpu/extract-sources.sh、prepare-kernel.sh、finalize-config.sh
- src/kernel-gpu/build-g35.sh、build-kernel.sh、build-nvgpu.sh、build-host1x-drm.sh
- src/kernel-gpu/verify-kernel-tree.py、audit-build.py、audit-user-abi.py
- patches/kernel/G2_CONFIG_DELTA.diff、G3_5_CONFIG_DELTA.diff
- docs/evidence_history 下原始 G4D/G4E/A1 历史报告

上述脚本依赖本机历史 WSL 路径，**不是通用脚本**。全新电脑必须先取得合法完整官方源码与交叉工具链、对应驱动/固件包，并复核精确版本。

## 3. 宿主离线构建

先只读查询是否存在完整源树；历史 WSL 参考路径：

~~~sh
uname -m
command -v aarch64-linux-gnu-gcc
command -v aarch64-linux-gnu-g++
git -C /work/a1/source/kernel/kernel-noble rev-parse HEAD
test -f /work/a1/build/kernel-original/Module.symvers
~~~

A1 冻结 commit 78272943bba3a47e633b28963b0cda60de503500，G35 config SHA 3df259fa...，Kernel release 6.8.12-prod-g78272943bba3；历史符号对照 13,943/13,943，CRC mismatch 零。若重建相同完整版本/环境，历史构建指令形态（**仅开发宿主**）：

~~~sh
make -C /work/a1/source/kernel/kernel-noble \
  O=/work/a1/build/kernel-original \
  ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- \
  CC=aarch64-linux-gnu-gcc -j10 Image modules
~~~

结束后检查内核 Image、.config、Module.symvers、version/vermagic、全部模块/符号/CRC 和编译器。原始全量 OOT build 曾部分失败而所需 minimal subset 通过，不能把“GPU 能用”扩称“整个 NVIDIA 生态已全量完成”。

## 4. DTB/initrd 和 Guest/HV 兼容门

- G4C：历史 PMC scratch 地址在 EL2 受限，修复手段是减少不适用的 DT aperture，不是改保护或绕过 Secure Boot。
- G4E2：新 6.8 tegra_hv_ivc compatible 节点、IVC/vblk 绑定、完整只读 rootfs、DTB hash 的双轮实机历史 PASS。
- 历史 kexec 的 DTB 参数/ kaslr-seed 有特定版本陷阱；复制命令前要验证目标 kexec-tools 行为，不可把过去 workaround 当安全通用安装方法。
- kexec 暖启动不能证明独立冷 GSP/ACR/MSI/ITS 稳定性；已经成功的 warm session 只对其当时 boot_id/载荷有效。

**禁止**把 Jetson T264 公共 P3834 BCT 镜像套到 P3960 DRIVE Thor，也禁止在 OEM 固件签名未证明前写入启动槽。

## 5. R39.2.1 NvGPU 595.78 OOT 驱动链

有界构建/依赖顺序：Kernel exported symbols → host1x/host1x-nvhost → tegra-drm/host1x-fence → nvmap/nvsciipc/mc-utils → nvgpu → R39 用户态 libcuda/libnvcucompat → 精确固件搜索路径。

历史 A1 构建了 host1x DRM 依赖闭包，1547 import CRC 无冲突。全套 R39 OOT / UMD / original board firmware 仍需合法来源且版本一致。核验命令应在隔离宿主对已取得的二进制运行：

~~~sh
modinfo -F vermagic /path/to/nvgpu.ko
modinfo -F depends /path/to/nvgpu.ko
readelf -h /path/to/libcuda.so
readelf -d /path/to/libcuda.so
sha256sum /path/to/nvgpu.ko
~~~

缺失 libnvcucompat.so、host1x DRM、原厂 prod_test_nsr 受许可组是历史真实故障原因。不得假装重命名/伪造签名后就有支持，固件/UEFI/签名受原厂安全策略控制。

## 6. CUDA 13.2 U2 实机准入

A1 历史已通过：libcuda 595.78 + cudart 13.2.86 + 官方 nvcc 13.2.86 为 SM110 生成 Cubin，在 6.8 RAM 实际 cuInit、1 个设备、context、HtoD、Kernel launch、同步、DtoH、释放上下文，65536 个 unsigned 数字恰等于输入加 17，exit0。

GitHub 中对应 src/kernel-gpu/a1-kernel.cu 和 a1-smoke.c。注意此门只证明 basic compute，不能推出 NVFP4 GEMM、Graph、TensorRT、27B、MSI、完整固件冷启动或长期生产。

## 7. 从 CUDA 到 TensorRT Edge-LLM 的阶段门

1. 6.8 的 boot_id、ABI、GPU 原厂模块/固件/用户库同一性重新确认。
2. 无错误的 CUDA Driver/Runtime 基础数值验证。
3. 目标 SM110 的 FP16/BF16/FP8/NVFP4 算子逐项对 CPU 参考。
4. TensorRT DLL/SONAME、CuTe/插件 ABI 与 Edge 安装 wheel 精确版本相匹配。
5. 27B 输入配置、原权重 SHA、完整文本 Engine、MTP Draft/Target 配对。
6. 固定 8K C1 输出/质量/资源，再谈 Tree、200K、视觉、API/持久发布。

高风险实机操作不作为本项目自动 workflow 的一部分。转入 [EDGE_LLM_27B.md](EDGE_LLM_27B.md) 和 [DEPLOYMENT_RUNBOOK.md](DEPLOYMENT_RUNBOOK.md)。
