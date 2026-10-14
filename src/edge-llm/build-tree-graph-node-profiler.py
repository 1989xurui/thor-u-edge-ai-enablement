"""Existing task G++13/CUDA public helper build;no engine/kernel change."""
import hashlib,json,os,pathlib,subprocess
P=pathlib.Path('/mnt/d/Thor64G/THOR_NVIDIA_NVFP4_20261013');W=pathlib.Path('/work/native-v2/worktrees/perf-v21-prefix-state')
source=W/'tools/thor_perf/treeGraphNodeProfiler.cpp';source.write_bytes((P/'scripts/tree-graph-node-profiler.cpp').read_bytes())
header=W/'tools/thor_perf/treeGraphRegions.h';header.write_bytes((P/'scripts/tree-graph-regions.h').read_bytes())
os.environ['TRT_PACKAGE_DIR']='/work/native-v2/qualified-trt-root'
output=P/'artifacts/libthor_tree_graph_node_profiler.so'
command=['aarch64-linux-gnu-g++-13','-std=c++17','-O2','-Wall','-Wextra','-Werror','-fPIC','-shared',str(source),'-I/work/a1/cuda-u2/toolkit/include','-L/work/a1/ram-root/a1/lib','-Wl,-z,defs','-Wl,--no-as-needed','-lcudart','-lcuda','-Wl,--as-needed','-ldl','-pthread','-o',str(output)]
p=subprocess.run(command,capture_output=True,text=True);(P/'evidence/tree-graph-node-profiler-build.log').write_text(p.stdout+p.stderr)
receipt=dict(status='PASS_ARM_PUBLIC_GRAPH_NODE_PROFILER_BUILD_ONLY'if p.returncode==0 else'FAIL_ARM_GRAPH_PROFILER_BUILD',build_command=command,build_exit_code=p.returncode,
    source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),region_header_sha256=hashlib.sha256(header.read_bytes()).hexdigest(),artifact_sha256=hashlib.sha256(output.read_bytes()).hexdigest()if output.exists()else None,worktree=str(W),
    unit_runtime='NOT_YET_TESTED',kernel_substitution=False,scope='Public graph clone preserves original ordinary and PDL edges;adds convex PDL region events;last verify replay only;not per-kernel or throughput qualification')
(P/'evidence/tree-graph-node-profiler-build-result.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt));assert p.returncode==0,p.stderr[-2000:]
unit_source=W/'tools/thor_perf/treeGraphNodeProfilerUnit.cpp';unit_source.write_bytes((P/'scripts/tree-graph-node-profiler-unit.cpp').read_bytes())
unit=P/'artifacts/treeGraphNodeProfilerUnit'
unit_command=['aarch64-linux-gnu-g++-13','-std=c++17','-O2','-Wall','-Wextra','-Werror',str(unit_source),'-I/work/a1/cuda-u2/toolkit/include','-L/work/a1/ram-root/a1/lib','-lcudart','-ldl','-o',str(unit)]
p=subprocess.run(unit_command,capture_output=True,text=True);(P/'evidence/tree-graph-node-profiler-unit-build.log').write_text(p.stdout+p.stderr)
v=dict(status='PASS_ARM_TINY_GRAPH_UNIT_BUILD_ONLY'if p.returncode==0 else'FAIL_ARM_GRAPH_UNIT_BUILD',build_command=unit_command,build_exit_code=p.returncode,artifact_sha256=hashlib.sha256(unit.read_bytes()).hexdigest()if unit.exists()else None,source_sha256=hashlib.sha256(unit_source.read_bytes()).hexdigest(),GPU_runtime='NOT_TESTED')
(P/'evidence/tree-graph-node-profiler-unit-build-result.json').write_text(json.dumps(v,indent=2));print(json.dumps(v));assert p.returncode==0,p.stderr[-2000:]
