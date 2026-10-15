# AGENTS.md — Instructions for AI coding agents and engineering assistants

This is a **public GitHub research repository**. Original project contributions are licensed **MIT** to the extent their respective contributors own copyright. Third-party material keeps its own terms; read [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). **Lack of OEM DRIVE SDK access is NOT a reason to refuse unrelated offline/source tasks.**

## Primary objective

Reproduce and advance the publicly auditable chain while retaining original DriveOS 7.0.3 / Kernel6.1.119 Golden:

- Linux6.8.12 G35 host build / IVC / virtual block / RAM-kexec historical validation
- NVIDIA R39.2.1 NvGPU595.78 / host1x / DRM / CUDA13.2 Update2
- TensorRT Edge-LLM0.11.0 / NVIDIA Qwen3.8-27B-NVFP4 / target + MTP K7 / Tree
- Accurate PASS / FAIL / HOLD, SHA, CPU numeric oracle, rollback and reproducibility

There are different completion levels. R0 repository and provenance checks can run on a normal PC. R1 public artifacts can be fetched from officially verified sources and independently hashed. R2 kernel/driver builds require separate SDK and source dependencies. R3 vehicle RAM boot requires explicit physical-maintenance qualification. R4 independent cold boot / persistent dual-boot and production is currently NO_GO.

**Never reclassify R0/R1 success as R3/R4 success.**

## Default executable safe workflow (DO THIS, no GPU or account needed)

~~~sh
python3 tools/verify_manifest.py
python3 tools/check_source_map.py
python3 tools/verify_download_lock.py
python3 tools/check_repo_release.py
python3 tools/fetch_public_wheel.py --list
~~~

Once the user requests real upstream assets: use [DOWNLOAD_AND_REPRODUCE.md](docs/DOWNLOAD_AND_REPRODUCE.md) and the pinned manifest. Ask for permission/available disk when about to download large assets, and use a directory OUTSIDE this Git repository. Do not silently download 20GiB models, build huge Engines, install NVIDIA packages or launch hardware experiments.

### Correct HOLD handling

~~~sh
python3 tools/check_dual_boot_readiness.py
python3 tools/check_program_readiness.py --summary
~~~

Both return code **2** on the 2026-10-15 snapshot. This is an expected engineering admission result. Record the unmet named Gate and continue with permitted static work: source/ABI audit, documentation, patch review, checksum, legal official URL verification, CPU-only fixtures. Do not keep retrying the same unavailable OEM/RCM operations.

## Files to start from

1. docs/START_HERE.md
2. docs/MASTER_IMPLEMENTATION_PLAN.md
3. docs/SOURCE_MAP.md and manifest/SOURCE_MAP_FILES.tsv
4. docs/DOWNLOAD_AND_REPRODUCE.md and manifest/DOWNLOAD_LOCK.json
5. docs/ASSET_AND_VERSION_LOCK.md
6. docs/BOOT_6_1_TO_6_8.md and manifest/PROGRAM_GATES.json
7. docs/ACCEPTANCE_AND_RELEASE.md / docs/RECOVERY_AND_TROUBLESHOOTING.md

The source paths D:/Thor64G/THOR_U_A1_NVGPU_R39_20261013, D:/Thor64G/THOR_NVIDIA_NVFP4_20261013, E:/Thor64G_AI/THOR_U_R39_GOS_BOOT_GATE_20261006 are **local historical workspaces**, NOT public git remotes. Use SOURCE_MAP to retrieve public samples and upstream references.

## Licensing: work on the correct code

- Contributor-owned original scripts/docs/gates are MIT under LICENSE.
- NVIDIA upstream TensorRT Edge-LLM is Apache-2.0; NVIDIA Jetson Linux has file-by-file source licenses; TensorRT binaries/DRIVE OEM SDK have separate NVIDIA terms; model repo has its own license.
- Preserve existing third-party SPDX, copyright headers and NOTICE, and never silently relicense third-party code as MIT.
- Two historically excluded NVIDIA-attributed source paths must remain excluded until source rights are independently reviewed (manifest/REVIEW_REQUIRED.json).
- Only add original code or safely licensed material; never commit raw driver/firmware, installed wheel files, model weight shards, TensorRT engines, HSM/private keys, confidential logs/identifiers or credential-bearing config.
- When a third-party input is not public/redistributable, document exact official download location, version SHA and user-acquisition step; never invent a mirror link.

## Safety and operating restrictions

- Original OEM 6.1 boot, DTB, initrd, Hypervisor, firmware, security domains, partition table, Golden and active R4 service are protected.
- NO automatic kexec, tegrareset, reboot, bootburn, flash, write-to-slot, OEM certificate/signature manipulation, UFS repartition, drive firmware override or production service switch.
- No unauthorized attempts to bypass signing/security/RCM hardware restrictions. Do not run Jetson T4000/P3834 flash images on DRIVE P3960.
- Never initialize GPU or rerun expensive 200K benchmarks on a live system just to recreate archived data.
- Require a separately authorized, isolated, bounded hardware-maintenance window, one GPU owner and independently verified recovery before any target-side modification.
- If actions are blocked, return only actual evidence and a concrete legal/technical next safe step.

## Required output from every agent

Report the exact scope and status honestly:

~~~text
CURRENT_HEAD:
PLATFORM_VARIANT:
SOURCE_AND_WHEEL_REVISIONS:
MODE: R0_STATIC / R1_PUBLIC_FETCH / R2_HOST_BUILD / R3_RAM_EXPERIMENT / R4_COLD_PRODUCTION
REPRODUCTION_RESULT: PASS / FAIL / HOLD
VERIFIED_ARTIFACTS_AND_SHA:
DEVICE_OPERATIONS: NONE unless separately authorized
UNMET_EXTERNAL_DEPS:
QUALITY_AND_STABILITY_LIMITATIONS:
ROLLBACK_EVIDENCE:
NEXT_SAFE_ACTION:
~~~

Do not edit historical PASS/FAIL evidence to "fix" a result. Add versioned report/manifest deltas and validate fresh clone, SHA, source map and LICENSE/third-party exclusions after every commit.
