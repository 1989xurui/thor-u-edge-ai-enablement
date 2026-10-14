#!/usr/bin/env bash
# Read-only target inventory; does not call nvidia-smi, kexec, sudo or network.
set -uo pipefail
printf '%s\n' 'THOR_PRECHECK_MODE=READ_ONLY'
printf 'DATE_UTC=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo unavailable)"
printf 'UNAME_MACHINE=%s\n' "$(uname -m 2>/dev/null)"
printf 'UNAME_KERNEL=%s\n' "$(uname -r 2>/dev/null)"
if [[ -r /proc/sys/kernel/random/boot_id ]]; then
  printf 'BOOT_ID='; cat /proc/sys/kernel/random/boot_id
fi
if [[ -r /etc/os-release ]]; then
  grep -E '^(ID|VERSION_ID|PRETTY_NAME)=' /etc/os-release | head -4
fi
if [[ -r /proc/meminfo ]]; then
  grep -E '^(MemTotal|MemAvailable|SwapTotal|SwapFree):' /proc/meminfo
fi
for p in /zeekr_data /zeekr_map /new_root; do
  if [[ -d "$p" ]]; then
    df -h "$p" 2>/dev/null | tail -1
  fi
done
if command -v nvcc >/dev/null 2>&1; then
  nvcc --version 2>/dev/null | tail -4
else
  printf '%s\n' 'NVCC=NOT_IN_PATH'
fi
printf '%s\n' 'GPU_DEVICE_NODE_CHECK_NO_INIT:'
for p in /dev/nvidiactl /dev/nvidia0 /dev/nvhost-gpu; do
  if [[ -e "$p" ]]; then printf 'EXISTS %s\n' "$p"; else printf 'MISSING %s\n' "$p"; fi
done
if command -v python3 >/dev/null 2>&1; then
  python3 --version 2>&1
fi
if command -v dpkg-query >/dev/null 2>&1; then
  dpkg-query -W 2>/dev/null |
    grep -E '^(cuda-cudart|cuda-nvcc|libnvinfer|nvidia-driver|nvidia-l4t-core)' | head -20 || true
fi
printf '%s\n' 'NO_GPU_INITIALIZATION_NO_SYSTEM_WRITES'
