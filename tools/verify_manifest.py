#!/usr/bin/env python3
"""Offline file integrity and accidental secret/binary gate. No car access."""
from pathlib import Path
import hashlib
import re
import sys

root=Path(__file__).resolve().parent.parent
manifest=root/"manifest"/"SHA256SUMS.txt"
if not manifest.is_file():
    sys.exit("FAIL: SHA256SUMS.txt missing")
line_count=0
bad=[]
for line in manifest.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    if "  " not in line:
        bad.append(("manifest syntax",line[:75]))
        continue
    expect,rel=line.split("  ",1)
    p=root/rel
    if not re.fullmatch(r"[0-9a-f]{64}",expect):
        bad.append(("sha field",rel))
        continue
    if ".." in Path(rel).parts or p.is_symlink() or not p.is_file():
        bad.append(("unsafe path / missing",rel))
        continue
    data=p.read_bytes()
    actual=hashlib.sha256(data).hexdigest()
    if expect!=actual:
        bad.append(("sha mismatch",rel))
    if len(data)>2_000_000:
        bad.append(("oversize >2MB",rel))
    if b"\0" in data:
        bad.append(("binary NUL",rel))
    line_count+=1
# Check for important untracked files, except git internals and the output summary.
expected={x.split("  ",1)[1] for x in manifest.read_text(encoding="utf-8").splitlines() if "  " in x}
ignored={"manifest/SHA256SUMS.txt","manifest/BUILD_SUMMARY.json"}
actual={p.relative_to(root).as_posix() for p in root.rglob("*")
        if p.is_file() and ".git" not in p.relative_to(root).parts}
for extra in sorted(actual-expected-ignored):
    bad.append(("untracked file",extra))
for missing in sorted(expected-actual):
    bad.append(("unmatched",missing))
if bad:
    print("FAIL: integrity violations =",len(bad))
    for kind,p in bad[:30]:
        print(kind,p)
    sys.exit(1)
print("PASS: SHA256_FILES=",line_count)
print("PASS: REPOSITORY_TEXT_ONLY=YES")
print("NOTE: Integrity does NOT authorize firmware flashing, driver or model promotion.")
