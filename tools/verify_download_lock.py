#!/usr/bin/env python3
"""Validate pinned public download metadata and optionally SHA-check local downloads.

Default only reads repository JSON and does not use the network/GPU/target device.
"""
from pathlib import Path
import argparse, hashlib, json, re, sys
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description="Offline manifest/schema and optional local SHA256 validation")
p.add_argument("--directory",type=Path,help="Directory containing previously downloaded wheels/model files")
p.add_argument("--include-large",action="store_true",help="Stream-hash large model shards if present (may read >20 GiB)")
p.add_argument("--require-all-wheels",action="store_true",help="Fail if all three pinned ARM64 wheels are not present")
p.add_argument("--require-model",action="store_true",help="Require all three model shard files and SHA256, implies --include-large")
p.add_argument("--require-wheel",choices=("cp310","cp311","cp312"),help="Require one specific ARM64 wheel and SHA256")
args=p.parse_args()
if (args.require_model or args.require_wheel or args.require_all_wheels) and not args.directory:
    p.error('Requirements need --directory for local SHA verification')
m=json.loads((ROOT/"manifest/DOWNLOAD_LOCK.json").read_text(encoding="utf-8"))
errors=[];checks=[];identifiers=set()
if m.get("schema")!="THOR_U_VERIFIED_PUBLIC_DOWNLOADS_V1":
    errors.append("Unexpected manifest schema")
def valid_sha(value):
    return isinstance(value,str) and bool(re.fullmatch(r"[0-9a-f]{64}",value))
for entry in m["downloads"]:
    ident=entry["id"]
    if ident in identifiers:errors.append("Duplicate download ID "+ident)
    identifiers.add(ident)
    for field in ("url","archive","clone"):
        if field not in entry:continue
        parsed=urlparse(entry[field])
        if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password:
            errors.append("Unsafe URL: "+ident+"/"+field)
    if entry["kind"]=="wheel":
        if not valid_sha(entry.get("sha256")):errors.append("Missing wheel SHA: "+ident)
        if not isinstance(entry.get("bytes"),int) or entry["bytes"]<1000000:
            errors.append("Invalid wheel size: "+ident)
        if entry["filename"]!=Path(urlparse(entry["url"]).path).name:
            errors.append("Wheel URL name mismatch: "+ident)
        if urlparse(entry["url"]).hostname!="files.pythonhosted.org":
            errors.append("Untrusted wheel host: "+ident)
for shard in m["model_shards"]:
    if not valid_sha(shard.get("sha256")):errors.append("Missing shard SHA")
    if shard.get("bytes",0)<100000000:errors.append("Invalid shard size")
if sum(x["bytes"] for x in m["model_shards"])!=21921697280:
    errors.append("Model shard totals differ from frozen experiment")
if m["constraints"]["persistent_dual_boot_qualified"] is not False:
    errors.append("Publication must not claim cold boot qualification")
if m["constraints"]["edge_full_model_quality_and_production_qualified"] is not False:
    errors.append("Publication must not claim production qualification")
if args.directory:
    folder=args.directory.expanduser()
    if not folder.is_dir():
        errors.append("Provided directory does not exist")
    else:
        paths=[(e["filename"],e["bytes"],e["sha256"]) for e in m["downloads"] if e["kind"]=="wheel"]
        paths.extend((e["filename"],e["bytes"],e["sha256"]) for e in m["model_shards"])
        for name,expected_bytes,expected_sha in paths:
            f=folder/name
            if not f.exists():
                checks.append({"file":name,"result":"MISSING"})
                if args.require_all_wheels and name.endswith(".whl"):errors.append("Required wheel absent: "+name)
                if args.require_model and name.endswith(".safetensors"):errors.append("Required model shard absent: "+name)
                if args.require_wheel and name.endswith(".whl") and ("-"+args.require_wheel+"-") in name:errors.append("Requested wheel absent: "+name)
                continue
            if not f.is_file() or f.is_symlink():
                errors.append("Not a regular non-symlink file: "+name);continue
            size=f.stat().st_size
            if size!=expected_bytes:
                errors.append("Size mismatch for "+name);continue
            if f.suffix==".safetensors" and not args.include_large and not args.require_model:
                checks.append({"file":name,"result":"SIZE_PASS_SHA_DEFERRED_USE_INCLUDE_LARGE"})
                continue
            dig=hashlib.sha256()
            with f.open("rb") as handle:
                for part in iter(lambda:handle.read(4*1024*1024),b""):
                    dig.update(part)
            if dig.hexdigest()!=expected_sha:
                errors.append("SHA mismatch for "+name)
            else:
                checks.append({"file":name,"result":"SIZE_AND_SHA_PASS"})
print(json.dumps({"status":"PASS" if not errors else "FAIL",
  "manifest_schema":m.get("schema"),
  "download_records":len(m["downloads"]),
  "arm64_wheels":sum(e["kind"]=="wheel" for e in m["downloads"]),
  "model_shards":len(m["model_shards"]),
  "network_access":False,
  "device_access":False,
  "local_file_checks":checks,
  "errors":errors[:30]},ensure_ascii=False,indent=2))
sys.exit(1 if errors else 0)
