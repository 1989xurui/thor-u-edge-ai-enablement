#!/usr/bin/env python3
"""Offline 110-file source provenance check; no remote, device or vendor access."""
from pathlib import Path
import csv,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parent.parent
M=ROOT/"manifest"
metadata=json.loads((M/"SOURCE_MAP.json").read_text(encoding="utf-8"))
orig=json.loads((M/"SOURCE_FILES.json").read_text(encoding="utf-8"))
supp=json.loads((M/"SUPPLEMENTAL_EVIDENCE.json").read_text(encoding="utf-8"))
expected={f["dest"] for f in orig["files"]}|{f["relative_path"] for f in supp["included"]}
if metadata.get("schema")!="THOR_U_SOURCE_MAP_V1":
    sys.exit("FAIL: source map schema mismatch")
with (M/"SOURCE_MAP_FILES.tsv").open("r",encoding="utf-8",newline="") as file:
    rows=list(csv.DictReader(file,delimiter="\t"))
errors=[]
registered={r["id"] for r in metadata["source_roots"]}
sources=set()
base_url="https://github.com/1989xurui/thor-u-edge-ai-enablement/blob/main/"
sha=lambda b:hashlib.sha256(b).hexdigest()
for row in rows:
    rel=row["repository_relative_path"]
    if row["root_id"] not in registered:errors.append("unknown source root: "+rel)
    if Path(rel).is_absolute() or ".." in Path(rel).parts or "\\" in rel:
        errors.append("unsafe repo path: "+rel)
        continue
    if rel in sources:errors.append("duplicate destination: "+rel)
    sources.add(rel)
    dest=ROOT/rel
    if not dest.is_file():
        errors.append("missing mapped export: "+rel)
        continue
    for k in ["frozen_source_sha256","published_file_sha256"]:
        if not re.fullmatch(r"[0-9a-f]{64}",row[k]):errors.append("bad SHA: "+rel)
    if sha(dest.read_bytes())!=row["published_file_sha256"]:
        errors.append("export SHA mismatched: "+rel)
    if not row["repository_url"].startswith(base_url):
        errors.append("unexpected source-map URL: "+rel)
    if row["current_local_source_status"] not in (
        "CURRENT_SOURCE_EQUALS_EXPORT_BASELINE",
        "SOURCE_CHANGED_AFTER_EXPORT",
        "SOURCE_READ_FAILED",
        "SOURCE_NOT_CURRENTLY_AVAILABLE"
    ):errors.append("unrecognized original source status: "+rel)
if sources!=expected:
    errors.append("published source mapping set unequal to SOURCE_FILES + SUPPLEMENTAL_EVIDENCE")
if len(rows)!=metadata["mapped_published_files"]:
    errors.append("row count mismatches source map summary")
if len(orig["files"])!=metadata["published_primary_selected"]:
    errors.append("primary count mismatched")
if len(supp["included"])!=metadata["published_supplemental_historical"]:
    errors.append("historical supplement count mismatched")
from collections import Counter
if dict(Counter(r["root_id"] for r in rows))!=metadata["by_root"]:
    errors.append("root counts mismatched")
changed=sum(r["current_local_source_status"]=="SOURCE_CHANGED_AFTER_EXPORT" for r in rows)
print(json.dumps({"status":"PASS" if not errors else "FAIL",
    "published_source_files_checked":len(rows),
    "first_pass":len(orig["files"]),
    "historical_supplements":len(supp["included"]),
    "original_sources_changed_since_archive":changed,
    "no_device_or_vendor_access":True,
    "errors":errors[:30]},ensure_ascii=False,indent=2))
sys.exit(1 if errors else 0)
