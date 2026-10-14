#!/bin/bash
set -euo pipefail
W=/work/a1
P=/mnt/d/Thor64G/THOR_U_A1_NVGPU_R39_20261013
K=$W/source/kernel/kernel-noble
B=$W/build/kernel-g35
test ! -e "$B" || exit 91
cp -a "$W/build/kernel-original" "$B"
cp /mnt/e/Thor64G_AI/THOR_U_R39_GOS_BOOT_GATE_20261006/03_kernel68/artifacts_g35/kernel-6.8.12-prod-g35.config "$B/.config"
cp "$B/.config" "$P/inputs/target-g35.config"
make -C "$K" O="$B" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- olddefconfig > "$P/logs/g35-olddefconfig.log" 2>&1
cmp "$P/inputs/target-g35.config" "$B/.config"
date -Is > "$P/logs/g35-kernel-build-start.txt"
set +e
make -C "$K" O="$B" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j10 Image modules > "$P/logs/g35-kernel-build.log" 2>&1
rc=$?
echo "$rc" > "$P/logs/g35-kernel-build.exit"
date -Is > "$P/logs/g35-kernel-build-end.txt"
tail -6 "$P/logs/g35-kernel-build.log"
echo G35_KERNEL_BUILD_RC=$rc
exit "$rc"
