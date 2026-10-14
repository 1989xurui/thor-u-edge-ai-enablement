# Thor-U Edge AI Enablement

**Linux Kernel 6.8.12 · NVIDIA R39 NvGPU 595.78 · CUDA 13.2 Update 2 · TensorRT Edge-LLM / NVFP4 / Tree-MTP**

An independent engineering research archive for NVIDIA DRIVE Thor T264 (AArch64, 14 SM, 64GB unified memory). It documents the experimental GPU bring-up, kernel/driver ABI work, native CUDA validation, and LLM inference optimization path.

> IMPORTANT: Not an official NVIDIA platform release. No claim of a qualified cold boot, production-grade Edge-LLM deployment, or official DRIVE SDK certification.

## Current evidence, not marketing

| Layer | Evidence-based outcome | Remaining boundary |
|---|---|---|
| Linux 6.8.12 / R39 | A1 RAM-booted kernel with NvGPU 595.78 loaded | Standalone cold boot NOT PROVEN |
| CUDA 13.2 U2 | Context, device memory, copy, kernel launch and result verification PASS in A1 session | Does not certify all CUDA APIs or long-term stability |
| TensorRT Edge-LLM | 27B NVFP4 / 8K native inference verified for bounded fixtures | Full quality, independent recovery, production release NO-GO |
| Tree-MTP | 8K cache-bypass sample 57.278 tok/s; K7 frozen comparison 55.444 tok/s | Non-simultaneous, different cache conditions; no broad speedup claim |
| 200K experimental | Limited recall-ID checks and native profiler evidence | Quality / sustained performance / production pending |

Source records date: 2026-10-13 to 2026-10-15. These are snapshots, NOT assertions about the device's present active services.

## What is in this repository?

- docs/kernel/: build reports, ABI and cold-boot handoff history
- src/kernel-gpu/: authored build, ABI audit and numeric validation helpers
- patches/kernel/: captured kernel config deltas, not an installation patch set
- src/edge-llm/: host-specific Edge-LLM research scripts and diagnostic logic
- evidence/: curated, reduced source-linked original research evidence
- manifest/: source provenance, SHA-256, redaction and exclusions
- docs/INSTALL_ON_THOR.md: safe onboarding and installation boundaries
- tools/preflight_thor_readonly.sh: zero-change target inspection
- tools/verify_manifest.py: offline file-integrity check

## What is NOT included?

No model weights (.safetensors/.gguf), TensorRT engines, firmware, NVIDIA redistributable packages, proprietary driver source trees, API credentials, database snapshots, WSL virtual disks, or active deployment secrets. Their versions and hashes may be referenced as technical evidence.

Some source snapshots had private LAN IP literals replaced with RFC5737 documentation IPs (192.0.2.x). These files are tagged in manifest/SOURCE_FILES.json. They are **NOT drop-in executable deployment artifacts**; operators must provide qualified target configuration and review them.

Files derived from NVIDIA-copyrighted sources have been held back for explicit license and attribution review. This snapshot is a private research work-in-progress, not a self-contained kernel or driver build.

## Start here

1. Read docs/STATUS_AND_ACCEPTANCE.md and docs/RESOURCE_BUDGET.md.
2. On an already-qualified target, read docs/INSTALL_ON_THOR.md, then execute only tools/preflight_thor_readonly.sh.
3. On a developer workstation, run python tools/verify_manifest.py. This does not access the vehicle.
4. Do not run old source build / flash / kernel activation scripts just because they are archived.

Official references:
- https://nvidia.github.io/TensorRT-Edge-LLM/0.11.0/user_guide/getting_started/installation.html
- https://github.com/NVIDIA/TensorRT-Edge-LLM
- https://developer.nvidia.com/drive/downloads

**Publication policy:** keep private until source rights, secret scanning, reproduction contract, and supported/unsupported install boundaries are reviewed.
