#!/usr/bin/env python3
"""Static repo integrity/secret/link checks, not a device/production gate."""
from pathlib import Path
import json,re,subprocess,sys

ROOT=Path(__file__).resolve().parent.parent
required=[
"README.md","docs/START_HERE.md","docs/MASTER_IMPLEMENTATION_PLAN.md",
"docs/ARCHITECTURE.md","docs/BOOT_6_1_TO_6_8.md",
"docs/ASSET_AND_VERSION_LOCK.md","docs/BUILD_KERNEL_GPU_CUDA.md",
"docs/EDGE_LLM_27B.md","docs/DEPLOYMENT_RUNBOOK.md",
"docs/ACCEPTANCE_AND_RELEASE.md","docs/RECOVERY_AND_TROUBLESHOOTING.md",
"docs/PROJECT_HANDOFF_AND_PROVENANCE.md","docs/OFFICIAL_REFERENCES.md",
"docs/INSTALL_ON_THOR.md","manifest/PROGRAM_GATES.json",
"manifest/BOOT_6_1_TO_6_8_GATES.json",
"manifest/OFFLINE_REQUIRED_ASSETS.json","manifest/SUPPLEMENTAL_EVIDENCE.json"
]
errors=[]
for rel in required:
    if not (ROOT/rel).is_file():errors.append("missing: "+rel)
program=json.loads((ROOT/"manifest/PROGRAM_GATES.json").read_text(encoding="utf-8"))
boot=json.loads((ROOT/"manifest/BOOT_6_1_TO_6_8_GATES.json").read_text(encoding="utf-8"))
if program.get("protect_original_61") is not True or program.get("allow_boot_activation_from_this_repo") is not False:
    errors.append("boot safety policy mismatch")
if boot["policy"].get("preserve_61") is not True:
    errors.append("Golden protection missing")
persistent=[x for x in boot["modes"] if x["id"]=="P_ADDITIVE_PERSISTENT"]
if len(persistent)!=1 or persistent[0]["status"]=="PASS_CURRENT_VERIFIED":
    errors.append("dual boot falsely completed")
links=0
for rel in required:
    if not rel.endswith(".md") or not (ROOT/rel).is_file():continue
    txt=(ROOT/rel).read_text(encoding="utf-8-sig")
    for uri in re.findall(r"(?<!!)\[[^\]]+\]\(([^)\s]+)\)",txt):
        if uri.startswith(("https://","http://","mailto:","#")):continue
        target=(ROOT/rel).parent/uri.split("#",1)[0]
        links+=1
        if not target.is_file():errors.append("broken link: "+rel+" -> "+uri)
    if rel in {"README.md","docs/INSTALL_ON_THOR.md","docs/ARCHITECTURE.md","docs/MASTER_IMPLEMENTATION_PLAN.md","docs/EDGE_LLM_27B.md"}:
        if "mermaid" not in txt:errors.append("architecture diagram missing "+rel)
sensitive=[
re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----",re.I),
re.compile(r"(?:github_" + r"pat_[A-Za-z0-9_]{16,}|gh[pousr]_[A-Za-z0-9]{18,}|sk-[A-Za-z0-9_-]{18,}|AKIA[0-9A-Z]{16})"),
re.compile(r"(?i)authorization\s*[:=]\s*['\"]?Bearer\s+[A-Za-z0-9._~-]{12,}"),
]
count=0
for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.relative_to(ROOT).parts:continue
    b=path.read_bytes(); rel=path.relative_to(ROOT).as_posix()
    if len(b)>2_000_000:errors.append("oversized "+rel)
    if b"\0" in b:errors.append("binary "+rel)
    decoded=b.decode("utf-8","replace")
    if any(p.search(decoded) for p in sensitive):errors.append("possible credential "+rel)
    count+=1
check=subprocess.run([sys.executable,str(ROOT/"tools/verify_manifest.py")],cwd=ROOT,capture_output=True,text=True)
if check.returncode:errors.append("SHA manifest fail: "+check.stdout[:200])
result={"result":"STATIC_ARCHIVE_PASS" if not errors else "STATIC_ARCHIVE_FAIL","files_seen":count,
    "docs_links_checked":links,"manifest_integrity":"PASS" if check.returncode==0 else "FAIL",
    "independent_cold_boot":False,"production_released":False,"errors":errors[:40]}
print(json.dumps(result,ensure_ascii=False,indent=2))
sys.exit(0 if not errors else 1)
