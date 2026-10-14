#!/bin/bash
set -euo pipefail
W=/work/a1
mkdir -p "$W/archives" "$W/source"
cd /mnt/d/Thor64G/THOR_U_A1_NVGPU_R39_20261013/inputs/source-archives/Linux_for_Tegra/source
sha256sum *.tbz2
grep -E 'kernel_(nvgpu|oot_modules|src)' public_sources_sha.txt
for p in kernel_src.tbz2 kernel_nvgpu_src.tbz2 kernel_oot_modules_src.tbz2; do
  expected=$(cut -d ' ' -f1 "$p.sha1sum")
  printf '%s  %s\n' "$expected" "$p" | sha1sum -c -
  tar -xjf "$p" -C "$W/source"
done
find "$W/source" -maxdepth 3 -name Makefile -o -name '*.git*'
echo SOURCE_EXTRACT_DONE
