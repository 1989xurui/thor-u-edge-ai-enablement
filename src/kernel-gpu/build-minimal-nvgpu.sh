#!/bin/bash
set -uo pipefail
W=/work/a1
P=/mnt/d/Thor64G/THOR_U_A1_NVGPU_R39_20261013
S=$W/source
flavor=${1:-original}
B=$W/build/kernel-$flavor
tag=
expected=70a2296c1c3aa9af0c4f6d08dd75bae19fb659ab8b36662437519c0bcf436b5d
if [ "$flavor" = g35 ]; then
  tag=g35-
  expected=3df259fa1f0be026af15e15e5133eb609a1e3e47f663313bc01b20afafe5b50b
fi
test "$(sha256sum "$B/.config" | cut -d ' ' -f1)" = "$expected" || exit 90
cp "$P/scripts/minimal-oot.Kbuild" "$S/nvidia-oot/Kbuild"
cp "$P/scripts/minimal-gpu.Kbuild" "$S/nvidia-oot/drivers/gpu/Kbuild"
date -Is > "$P/logs/${tag}minimal-build-start.txt"
make -C "$B" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j10 M="$S/nvidia-oot" CONFIG_TEGRA_OOT_MODULE=m srctree.nvidia-oot="$S/nvidia-oot" srctree.hwpm="$S/hwpm" srctree.nvconftest="$S/out/nvidia-conftest" kernel_name=noble system_type=l4t KBUILD_EXTRA_SYMBOLS="$S/hwpm/drivers/tegra/hwpm/Module.symvers" modules > "$P/logs/${tag}minimal-oot-build.log" 2>&1
rc=$?
echo "$rc" > "$P/logs/${tag}minimal-oot-build.exit"
if [ "$rc" != 0 ]; then tail -15 "$P/logs/${tag}minimal-oot-build.log"; exit "$rc"; fi
make -C "$B" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j10 M="$S/nvgpu/drivers/gpu/nvgpu" CONFIG_TEGRA_OOT_MODULE=m srctree.nvidia="$S/nvidia-oot" srctree.nvidia-oot="$S/nvidia-oot" srctree.nvconftest="$S/out/nvidia-conftest" KBUILD_EXTRA_SYMBOLS="$S/nvidia-oot/Module.symvers" modules > "$P/logs/${tag}minimal-nvgpu-build.log" 2>&1
rc=$?
echo "$rc" > "$P/logs/${tag}minimal-nvgpu-build.exit"
date -Is > "$P/logs/${tag}minimal-build-end.txt"
tail -12 "$P/logs/${tag}minimal-nvgpu-build.log"
echo MINIMAL_NVGPU_BUILD_RC=$rc
exit "$rc"
