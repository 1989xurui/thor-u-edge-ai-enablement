#!/usr/bin/env python3
"""Offline gate report only: no device, storage, boot, firmware or network action."""
from pathlib import Path
import json
import sys

root = Path(__file__).resolve().parent.parent
cfg = json.loads((root / "manifest/BOOT_6_1_TO_6_8_GATES.json").read_text(encoding="utf-8"))

if cfg.get("policy", {}).get("preserve_61") is not True:
    sys.exit("INVALID: Original 6.1 preservation is not mandatory.")

print("THOR 6.1 + 6.8 BOOT_ADMISSION - DOCUMENTED EVIDENCE ONLY")
print("Current documented decision:", cfg["overall"])
print("Evidence date:", cfg["evaluated_date"])
for mode in cfg["modes"]:
    print("MODE",mode["id"],"=",mode["status"])
for gate in cfg["gates"]:
    print("GATE",gate["id"],"=",gate["status"])

blocked = [g["id"] for g in cfg["gates"] if g["status"] not in {"PASS", "PASS_VERIFIED_CURRENT"}]
if blocked:
    print("HOLD: no persistent 6.8 boot install, cold boot or boot-slot writes permitted")
    print("Unmet or limited gates: " + ", ".join(blocked))
    sys.exit(2)
print("All listed gates satisfied on paper; still requires external independent live verification.")
