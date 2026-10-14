import hashlib,json,pathlib,subprocess
P=pathlib.Path('/mnt/d/Thor64G/THOR_NVIDIA_NVFP4_20261013');S=P/'scripts';A=P/'artifacts';out=A/'libthor_spec_graph_cost.so'
run=subprocess.run(['aarch64-linux-gnu-g++-13','-std=c++17','-O2','-Wall','-Wextra','-fPIC','-shared',str(S/'spec-graph-cost.cpp'),'-I/work/a1/cuda-u2/toolkit/include','-L/work/a1/ram-root/a1/lib','-Wl,-z,defs','-Wl,--no-as-needed','-lcudart','-lcuda','-Wl,--as-needed','-ldl','-pthread','-o',str(out)],capture_output=True,text=True)
(P/'evidence/spec-graph-cost-build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
v=dict(status='PUBLIC_CUDA_GRAPH_COST_OBSERVER_COMPILED_ONLY',source_sha256=hashlib.sha256((S/'spec-graph-cost.cpp').read_bytes()).hexdigest(),library_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),bytes=out.stat().st_size,scope='Classify actual captured graphs by kernel names,then CUDA events on native graph replays;no private ABI or CUPTI requirement;not a benchmark result')
(P/'evidence/spec-graph-cost-package.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
