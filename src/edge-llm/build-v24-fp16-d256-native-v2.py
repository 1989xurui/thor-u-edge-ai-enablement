import argparse, datetime, hashlib, json, pathlib, subprocess, time
parser=argparse.ArgumentParser();parser.add_argument('--attempt',type=int,default=1);attempt=parser.parse_args().attempt
P=pathlib.Path('/mnt/d/Thor64G/THOR_NVIDIA_NVFP4_20261013')
W=pathlib.Path('/work/native-v2/worktrees/perf-v21-prefix-state')
artifact=W/'cpp/kernels/cuteDSLArtifact/aarch64/sm_110'
source=P/'scripts/v24-fp16-d256-native-v2.cpp'
out=P/'artifacts/libthor_v24_fp16_d256_native_v2.so'
receipt=P/f'evidence/V24-fp16-d256-native-v2-build-attempt{attempt}.json'
assert not out.exists() and not receipt.exists()
style='{BasedOnStyle: LLVM, IndentWidth: 4, BreakBeforeBraces: Allman, ColumnLimit: 120, PointerAlignment: Right}'
subprocess.run(['/work/native-v2/venv/bin/clang-format','-style='+style,'-i',str(source)],check=True)
argv=['aarch64-linux-gnu-g++-13','-std=c++17','-O2','-fPIC','-shared','-Wall','-Wextra','-Werror',
    str(source),'-isystem','/work/a1/cuda-u2/toolkit/include','-isystem',str(artifact/'include'),
    '-isystem',str(W/'cpp/kernels/contextAttentionKernels'),str(artifact/'libcutedsl_aarch64.a'),
    '-L/work/a1/cuda-u2/toolkit/lib','-L/work/a1/ram-root/a1/lib','-lcudart','-l:libcuda.so.1',
    '-Wl,-z,defs','-Wl,--exclude-libs,ALL','-o',str(out)]
start=time.monotonic()
with(P/f'evidence/V24-fp16-d256-native-v2-build-attempt{attempt}.log').open('w')as log:
    done=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT)
record=dict(status='PASS_AARCH64_SM110_FP16_D256_WRAPPER_BUILD_ONLY'if done.returncode==0 else'FAIL_WRAPPER_BUILD',
    returncode=done.returncode,command=argv,elapsed_s=time.monotonic()-start,
    timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    source_SHA=hashlib.sha256(source.read_bytes()).hexdigest(),
    pinned_artifact_archive_SHA=hashlib.sha256((artifact/'libcutedsl_aarch64.a').read_bytes()).hexdigest(),
    pinned_artifact_metadata_SHA=hashlib.sha256((artifact/'metadata.json').read_bytes()).hexdigest(),
    artifact_metadata=json.loads((artifact/'metadata.json').read_text()),
    library_SHA=hashlib.sha256(out.read_bytes()).hexdigest()if done.returncode==0 else None,
    library_bytes=out.stat().st_size if done.returncode==0 else None,
    numerical_or_GPU_tested=False,quantization_changed=False,KV='FP16',Engine_recompiled=False,
    original_plugin_replaced=False,original_Runtime_changed=False,interposition=False)
receipt.write_text(json.dumps(record,indent=2));print(json.dumps({k:record[k]for k in ['status','returncode','elapsed_s','library_SHA','library_bytes']}))
raise SystemExit(done.returncode)
