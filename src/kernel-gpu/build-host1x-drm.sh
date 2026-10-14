#!/bin/bash
set -euo pipefail
W=/work/a1
P=/mnt/d/Thor64G/THOR_U_A1_NVGPU_R39_20261013
S=$W/source
B=$W/build/kernel-g35
test "$(sha256sum "$B/.config" | cut -d ' ' -f1)" = 3df259fa1f0be026af15e15e5133eb609a1e3e47f663313bc01b20afafe5b50b
cp "$S/nvidia-oot/drivers/gpu/Kbuild" "$P/logs/gpu-Kbuild-before-drm"
grep -q 'drm/tegra/' "$S/nvidia-oot/drivers/gpu/Kbuild" || echo 'obj-m += drm/tegra/' >> "$S/nvidia-oot/drivers/gpu/Kbuild"
make -C "$B" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j10 M="$S/nvidia-oot" CONFIG_TEGRA_OOT_MODULE=m srctree.nvidia-oot="$S/nvidia-oot" srctree.hwpm="$S/hwpm" srctree.nvconftest="$S/out/nvidia-conftest" kernel_name=noble system_type=l4t KBUILD_EXTRA_SYMBOLS="$S/hwpm/drivers/tegra/hwpm/Module.symvers" modules > "$P/logs/g35-host1x-drm-build.log" 2>&1
cp "$S/nvidia-oot/drivers/gpu/drm/tegra/tegra-drm.ko" "$P/artifacts/g35/" 2>/dev/null || cp "$S/nvidia-oot/drivers/gpu/drm/tegra/tegra_drm.ko" "$P/artifacts/g35/"
echo HOST1X_DRM_BUILD_PASS
