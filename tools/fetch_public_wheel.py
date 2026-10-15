#!/usr/bin/env python3
"""Explicit opt-in fetch of one SHA-pinned PyPI NVIDIA Edge-LLM aarch64 wheel.

Default is a print-only list. Never installs, runs, or accesses a vehicle.
"""
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import argparse, hashlib, json, os, sys

ROOT=Path(__file__).resolve().parent.parent
m=json.loads((ROOT/"manifest/DOWNLOAD_LOCK.json").read_text(encoding="utf-8"))
wheels={v["python_abi"]:v for v in m["downloads"] if v["kind"]=="wheel"}
p=argparse.ArgumentParser()
p.add_argument("--list",action="store_true",help="List public pinned wheel options, with no downloads")
p.add_argument("--python",choices=sorted(wheels),help="Python ABI: cp310/cp311/cp312")
p.add_argument("--download",action="store_true",help="Explicitly download exactly one pinned wheel")
p.add_argument("--out",type=Path,help="Mandatory external-assets output folder when downloading")
args=p.parse_args()

if not args.download:
    print(json.dumps({"status":"DRY_RUN_ONLY","wheels":[{
        "python":key,"filename":v["filename"],"bytes":v["bytes"],
        "sha256":v["sha256"],"url":v["url"]} for key,v in sorted(wheels.items())],
        "next":"Use --python cp311 --download --out <non-repo-folder> to fetch one wheel, only on trusted dev host."},ensure_ascii=False,indent=2))
    sys.exit(0)
if not args.python or not args.out:
    p.error("--download requires both --python and --out")
entry=wheels[args.python]
url=entry["url"]
assert urlparse(url).hostname=="files.pythonhosted.org" and url.startswith("https://")
out=args.out.expanduser().resolve()
# Never place huge wheels inside the source checkout (Git safety).
if out==ROOT or ROOT in out.parents:
    p.error("--out must be outside the repository to avoid accidental Git binary upload")
out.mkdir(parents=True,exist_ok=True)
final=out/entry["filename"]
if final.is_symlink() or final.exists():
    p.error("Refusing to overwrite an existing output; verify it with tools/verify_download_lock.py")
temp=out/(entry["filename"]+".partial")
if temp.exists() or temp.is_symlink():
    p.error("Partial output already exists; inspect/clean it manually before retrying.")
digest=hashlib.sha256()
total=0
try:
    with urlopen(Request(url,headers={"User-Agent":"Thor-U-Verified-Artifact-Fetch"}),timeout=30) as response:
        if urlparse(response.geturl()).hostname!="files.pythonhosted.org":
            raise RuntimeError("Unexpected download redirect host")
        if response.status!=200:
            raise RuntimeError("Unexpected HTTP status")
        with temp.open("xb") as f:
            for chunk in iter(lambda:response.read(2*1024*1024),b""):
                total+=len(chunk)
                if total>entry["bytes"]:
                    raise RuntimeError("Download exceeded locked file size")
                digest.update(chunk)
                f.write(chunk)
    if total!=entry["bytes"] or digest.hexdigest()!=entry["sha256"]:
        raise RuntimeError("Download byte count/SHA256 does not match pinned PyPI distribution")
    temp.rename(final)
    print(json.dumps({"status":"PINNED_DOWNLOAD_VERIFIED","file":str(final),
                      "bytes":total,"sha256":digest.hexdigest(),
                      "installed":False,"device_changed":False},ensure_ascii=False))
except Exception as e:
    try:temp.unlink(missing_ok=True)
    except OSError:pass
    print("DOWNLOAD_NOT_VERIFIED:",type(e).__name__,file=sys.stderr)
    sys.exit(1)
