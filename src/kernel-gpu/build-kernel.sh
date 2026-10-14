#!/bin/bash
set -uo pipefail
W=/work/a1
P=/mnt/d/Thor64G/THOR_U_A1_NVGPU_R39_20261013
date -Is > "$P/logs/kernel-build-start.txt"
make -C "$W/source/kernel/kernel-noble" O="$W/build/kernel-original" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- CC=aarch64-linux-gnu-gcc -j10 Image modules > "$P/logs/kernel-build.log" 2>&1
rc=$?
printf '%s\n' "$rc" > "$P/logs/kernel-build.exit"
date -Is > "$P/logs/kernel-build-end.txt"
tail -8 "$P/logs/kernel-build.log"
echo KERNEL_BUILD_RC=$rc
exit "$rc"
