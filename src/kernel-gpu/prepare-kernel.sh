#!/bin/bash
set -euo pipefail
W=/work/a1
P=/mnt/d/Thor64G/THOR_U_A1_NVGPU_R39_20261013
K=$W/source/kernel/kernel-noble
B=$W/build/kernel-original
chown -R root:root "$K"
git -C "$K" config core.bare false
git -C "$K" config core.filemode true
git -C "$K" config core.ignorecase false
git -C "$K" update-ref refs/heads/a1-locked 78272943bba3a47e633b28963b0cda60de503500
git -C "$K" symbolic-ref HEAD refs/heads/a1-locked
git -C "$K" ls-tree -r --format='%(objectmode) %(path)' HEAD | sed '/^120000 /d;s/^[^ ]* //' > "$W/kernel-tracked-paths.txt"
(cd "$K" && git hash-object -w --stdin-paths < "$W/kernel-tracked-paths.txt" > "$W/kernel-materialized-blobs.txt")
while IFS= read -r -d '' link; do
  readlink -n "$link" | git -C "$K" hash-object -w --stdin >> "$W/kernel-materialized-blobs.txt"
done < <(find "$K" -type l -print0)
git -C "$K" reset --mixed HEAD > "$P/logs/kernel-git-reset.log"
git -C "$K" status --porcelain -uno > "$P/logs/kernel-git-status.txt"
test ! -s "$P/logs/kernel-git-status.txt"
git -C "$K" rev-parse HEAD HEAD^{tree} > "$P/logs/kernel-git-identity.txt"
mkdir -p "$B"
cp /mnt/e/Thor64G_AI/THOR_U_R39_GOS_BOOT_GATE_20261006/03_kernel68/artifacts/kernel-6.8.12-prod.config "$B/.config"
cp "$B/.config" "$P/inputs/target-original.config"
make -C "$K" O="$B" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- CC=aarch64-linux-gnu-gcc-13 olddefconfig > "$P/logs/kernel-olddefconfig.log" 2>&1
diff -u "$P/inputs/target-original.config" "$B/.config" > "$P/logs/kernel-config-delta.diff" || true
make -s -C "$K" O="$B" ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- CC=aarch64-linux-gnu-gcc-13 kernelrelease | tee "$P/logs/kernelrelease.txt"
echo KERNEL_PREPARE_READY
