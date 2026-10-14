#!/bin/bash
set -uo pipefail
W=/work/a1
P=/mnt/d/Thor64G/THOR_U_A1_NVGPU_R39_20261013
date -Is > "$P/logs/nvgpu-build-start.txt"
make -C "$W/source" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- KERNEL_HEADERS="$W/source/kernel/kernel-noble" KERNEL_OUTPUT="$W/build/kernel-original" kernel_name=noble NVIDIA_DISPLAY_MODULE_TARGETS= NPROC=10 modules > "$P/logs/nvgpu-build.log" 2>&1
rc=$?
printf '%s\n' "$rc" > "$P/logs/nvgpu-build.exit"
date -Is > "$P/logs/nvgpu-build-end.txt"
tail -12 "$P/logs/nvgpu-build.log"
echo NVGPU_BUILD_RC=$rc
exit "$rc"
