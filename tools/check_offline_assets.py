#!/usr/bin/env python3
"""Optional off-target artifact inventory: never downloads, installs, executes or flashes."""
from pathlib import Path
import json,argparse,hashlib,sys
ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser(description="Developer-host asset SHA checks only")
parser.add_argument("--map",dest="mapping",help="JSON object asset ID -> absolute local file path")
parser.add_argument("--full-hash",action="store_true",help="Explicitly read/hash mapped multi-GiB files")
args=parser.parse_args()
contract=json.loads((ROOT/"manifest/OFFLINE_REQUIRED_ASSETS.json").read_text(encoding="utf-8"))
items=contract["items"]
provided=json.loads(Path(args.mapping).read_text(encoding="utf-8")) if args.mapping else {}
if not isinstance(provided,dict):sys.exit("FAIL mapping needs an object")
results=[]
for item in items:
    name=item["id"]; path=provided.get(name);expected=item.get("expected_sha256")
    status="UNPROVIDED"
    if path:
        f=Path(path)
        if not f.is_absolute() or not f.is_file():status="INVALID_LOCAL_PATH"
        elif args.full_hash and expected:
            digest=hashlib.sha256()
            with f.open("rb") as stream:
                for block in iter(lambda:stream.read(4*1024*1024),b""):
                    digest.update(block)
            status="SHA256_PASS" if digest.hexdigest().lower()==expected else "SHA256_MISMATCH"
        else:status="PRESENT_UNVERIFIED"
    results.append({"id":name,"status":status,"known_expected_sha":bool(expected)})
print(json.dumps({"verdict":"HOLD_VENDOR_ASSETS_NOT_COMPLETE","items":results,"target_device_access":False},ensure_ascii=False,indent=2))
sys.exit(2)
