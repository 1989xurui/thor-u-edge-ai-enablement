# Thor-U resource budget — capacity and memory

Evidence scope: frozen A1 RAM boot and Edge-LLM experiments through 2026-10-15. Values below are from different sessions and are not additive or directly interchangeable.

## A. GitHub package versus original host assets

Local source inventories (recursive Windows file sizes, original directories):
- D:/Thor64G/THOR_NVIDIA_NVFP4_20261013: approximately 21,852 MiB (~21.3 GiB).
- D:/Thor64G/THOR_U_A1_NVGPU_R39_20261013: approximately 37,519 MiB (~36.6 GiB).
- Combined original archives: ~57.9 GiB, mostly NOT suitable for Git.
- Curated source, reports, and validations: measure from manifest/BUILD_SUMMARY.json after finalization. Target <100 MiB, and no single file >=2 MB.

## B. Model and Engine disk

- Original NVIDIA 27B NVFP4 checkpoint: three shards totaling ~21,921,697,280 bytes, approximately 20.42 GiB.
- Historic full TensorRT engine: ~17,599,751,492 bytes, approximately 16.39 GiB.
- Both stored together: approximately 36.81 GiB, not counting runtimes, alternate engines, draft engine, temporary buffers, ONNX or build outputs.
- Official TensorRT Edge-LLM source build guide: expect approximately 20–50 GB for ONNX files and engines (platform/workflow dependent).
- A new clean installation that builds engines may therefore need 50–90 GiB or more of temporary/persistent storage; this is capacity planning, not a measured universal minimum.
- GitHub archive contains none of these large binary files.

## C. Unified memory / operational limits

T264 device has 64 GB unified memory; historic Linux available system memory is near 58 GiB. The OS, GPU, model weights, KV state, graph/runtime caches, and allocations share this memory.

- Measured 8K native K7 sample: minimum MemAvailable ~31.859 GiB. Against 58 GiB usable, total in-use at that snapshot was ~26 GiB (including operating system and other activity).
- Measured 200K profiler sample: minimum MemAvailable ~15.747 GiB; total occupied ~42 GiB relative to a 58 GiB reference.
- Practical 8K one-process planning: ~26–32 GiB overall use; 200K experiments can approach ~40–45 GiB. These are rough empirical budgets, NOT isolated model allocation measurements.
- Draft configurations, longer contexts, batch/concurrency, caching, kernel profile and different target processes may materially change consumption.
- Minimum safety constraints from this project's operating policy: MemAvailable >=5 GiB; GPU available pool >=2 GiB; temperature <95°C; persistent free storage >=12 GiB before any isolated deployment.

Official guide says available device memory before inference should be at least deployed model size +2 GB, and explicitly warns KV/draft/sequence/batch add overhead. That lower bound alone is NOT sufficient to certify this 27B target.

## D. Three independent numbers to track

1. Git package size: file bytes and hashes from manifest/BUILD_SUMMARY.json.
2. Persistent device storage: df -h on the actual intended partition, counting copy-on-write and temporary Engine build needs.
3. Runtime memory: live /proc/meminfo and GPU allocation evidence with the exact engine/input length, no second model and stable C1 owner.

Never infer deployability from Git size alone. Never add device RAM to disk free space.
