# Platform status, qualifications, and acceptance gates

Authoritative source ordering: A1_EXECUTION_CARD.md (2026-10-13); Edge CURRENT_RELEASE_CARD.md and RUN_STATE.json (latest 2026-10-14 UTC); older G5 reports document historical blockers and must not overwrite newer A1 basic CUDA evidence.

## Stage A — kernel + GPU

- Kernel: 6.8.12-prod-g78272943bba3, user experimental A1 RAM session.
- Driver: original-version NVIDIA NvGPU 595.78 loaded together with corrected host1x DRM dependencies and module/CRC closure.
- CUDA U2: 13.2.86 native context, alloc, H2D, compute, synchronization, D2H, 65,536-element numeric check passed.
- GSP/firmware pathways depend on original supported assets. No vendor firmware re-signing or authentication bypass is offered by this project.
- ITS/LPI alerts and INTx fallback exist. Standalone persistent cold boot, long endurance and cold GSP/ACR bring-up remain NOT PROVEN.
- G5 phase29 0x83d failure is historical evidence preceding A1; it is not proof that the later A1 CUDA smoke failed.

## Stage B — TensorRT native inference

- NVIDIA Qwen3.8-27B NVFP4 checkpoint pinned by source-state manifest; do not substitute a similarly named model.
- Original Target precision and Draft profile must remain tied to the exact TensorRT/Edge runtime package and plugin binary hashes.
- K7 8K native scenario: decode 55.444 tok/s, TTFT 4.292 s in its frozen reference conditions.
- Tree 8K bypass scenario: decode 57.278 tok/s, TTFT 3.924 s, and exact output IDs for a single frozen 368-token example.
- These were not matched simultaneous A/B with identical cache policies. Do not treat 3.3% as proven generalized gain.
- 200K original native diagnostic: cold TTFT 207.935 s, 32.315 tok/s decode; target <=180 s and >=36 tok/s not achieved.
- Three 8K/64K/200K recall fixtures passed scoped output-token ID checks. Full quality, stable throughput, hot-cache Tree, model start/recovery, full tooling and production remain NO-GO.

## Stage C — required release gates

1. Hardware: exact T264 board identity, memory, GPU architecture, firmware path, partition map, device boot ID, rollback image.
2. Kernel: reproducible source/ABI version lock, boot/interrupt correctness, driver/firmware interface, independent cold boot and known-safe rollback.
3. CUDA: same-build driver/runtime numerical smoke, clean GPU reset, no fatal kernel or SMMU faults.
4. TRT/Edge: exact native binary and plugin ABI, engine deserialization, full 27B output, same-checkpoint exact output checks.
5. Performance: equal-circumstances cold/hot TTFT, C1 decode, 8K then long-context; claim gains only from paired measurements.
6. Quality: fixed prompts, per-token output checks, functional tool API fixtures, cancellation/reuse, numeric attention/state boundaries.
7. Stability: bounded endurance, memory/thermal floor, recovery and rollback. No effect on vehicle safety-critical functionality.
8. Deployment: only promote a candidate after all gates; never modify original system, flash partitions or replace production services from this archive.

## Compatibility boundary

Official TensorRT Edge-LLM 0.11.0 support matrix lists DRIVE Thor: DriveOS 7.2, CUDA 13.3 in SDK container with EMBEDDED_TARGET=auto-thor. This user's experimental DriveOS 7.0.3 + Linux 6.8 RAM + CUDA 13.2 combination is not that matrix entry. It must be qualified independently. The upstream source tag and actually installed wheel revision were not identical in local research records; keep both hashes.

The Git repository is a research snapshot and cannot on its own prove a fully reproducible driver + kernel binary build. Original vendor packages and verified boot source inputs must be supplied through lawful, supported channels.
