#!/bin/bash
set -euo pipefail
W=/work/a1
P=/mnt/d/Thor64G/THOR_U_A1_NVGPU_R39_20261013
mkdir -p "$W/stage" "$P/logs/package"
for p in "$P"/inputs/debs/*.deb; do
  [ -s "$p" ] || continue
  n=$(basename "$p" .deb)
  [ -f "$P/logs/package/$n.contents" ] && [ -d "$W/stage/$n" ] && continue
  mkdir -p "$W/stage/$n"
  dpkg-deb -f "$p" > "$P/logs/package/$n.control"
  dpkg-deb -c "$p" > "$P/logs/package/$n.contents"
  dpkg-deb -e "$p" "$W/stage/$n/DEBIAN"
  dpkg-deb -x "$p" "$W/stage/$n"
  sha256sum "$p"
  touch "$W/stage/$n/.audit-complete"
done
find "$W/stage" -type f \( -name '*.ko*' -o -name '*.bin' -o -name 'libcuda.so*' -o -name '*symvers*' \) > "$P/logs/package/payload-files.txt"
echo PACKAGE_AUDIT_DONE
