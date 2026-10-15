#!/usr/bin/env python3
"""Offline program readiness. Exit 2 means correctly blocked. Zero device actions."""
from pathlib import Path
import argparse,json,sys

ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser()
p.add_argument("--summary",action="store_true")
p.add_argument("--json",action="store_true")
args=p.parse_args()
program=json.loads((ROOT/"manifest/PROGRAM_GATES.json").read_text(encoding="utf-8"))
boot=json.loads((ROOT/"manifest/BOOT_6_1_TO_6_8_GATES.json").read_text(encoding="utf-8"))
assert program["schema"]=="THOR_U_FULL_PROGRAM_GATES_V1"
assert boot["policy"]["preserve_61"] is True and program["protect_original_61"] is True
assert program["allow_boot_activation_from_this_repo"] is False
stages=program["stages"]
ids=[s["id"] for s in stages]
assert len(ids)==len(set(ids)) and all(s["id"].startswith("P") for s in stages)
by={s["id"]:s for s in stages}
mandatory=program["mandatory_device_release"]
assert mandatory and all(s in by for s in mandatory)
required=program["required_status_for_release"]
blocking=[s for s in stages if s["id"] in mandatory and s["status"]!=required]
persistent=next(x for x in boot["modes"] if x["id"]=="P_ADDITIVE_PERSISTENT")
if persistent["status"]!="PASS_CURRENT_VERIFIED" and not blocking:
    raise SystemExit("INVALID: cannot qualify device release without a proven independent boot.")
missing=[]
for s in stages:
    for e in s.get("evidence",[]):
        if e.startswith("/") or ".." in Path(e).parts or not (ROOT/e).is_file():
            missing.append((s["id"],e))
if missing:
    print("INVALID evidence paths:",missing,file=sys.stderr)
    sys.exit(1)
verdict="HOLD_NOT_PRODUCTION" if blocking else "DOCUMENTED_GATES_PASS_PENDING_LIVE_RECHECK"
result={"program_verdict":verdict,"boot_additive_persistent":persistent["status"],
        "historical_not_live_state":program["current_device_boot_not_revalidated"],
        "blocking_stages":[{"id":s["id"],"status":s["status"],"next":s["next"]} for s in blocking],
        "device_boot_or_flash_authorized":False,"allowed_next":program["next_safe_action"]}
if args.json:print(json.dumps(result,ensure_ascii=False,indent=2))
else:
    print("THOR_U_FULL_PROGRAM",verdict)
    print("PRESERVE_ORIGINAL_6_1=YES; BOOT/FLASH_AUTOMATION=DISABLED")
    for s in stages:print(f'{s["id"]:3s} {s["status"]:30s} {s["title"]}')
    print("BLOCKING_COUNT=",len(blocking))
    print("NEXT_SAFE_ACTION=",program["next_safe_action"])
sys.exit(2 if blocking else 0)
