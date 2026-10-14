#!/bin/bash
set -euo pipefail
W=/work/a1
P=/mnt/d/Thor64G/THOR_U_A1_NVGPU_R39_20261013
cp "$P/inputs/target-original.config" "$W/build/kernel-original/.config"
make -C "$W/source/kernel/kernel-noble" O="$W/build/kernel-original" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- CC=aarch64-linux-gnu-gcc olddefconfig > "$P/logs/kernel-final-olddefconfig.log" 2>&1
cmp "$P/inputs/target-original.config" "$W/build/kernel-original/.config"
sha256sum "$W/build/kernel-original/.config"
echo EXACT_TARGET_CONFIG_MATCH
