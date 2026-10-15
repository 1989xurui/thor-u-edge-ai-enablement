# Third-party rights, copyright, and MIT scope

The root [MIT LICENSE](LICENSE) grants permission for **original contributions to this project, to the extent their contributors own the relevant rights and can license them**. It does not overwrite third-party copyright, license terms, firmware redistribution restrictions, model terms or vendor signing/secure-boot requirements. GitHub public visibility alone is not permission to distribute every binary.

## Repository components and license treatment

| Content | Licensing guidance | Explicit limitation |
|---|---|---|
| New original orchestration and validation scripts in tools/, repo automation, original design documentation | MIT for copyright owned by repository contributors | Preserve attribution when redistributing |
| Existing archived experimental scripts in src/kernel-gpu, src/edge-llm | MIT only for independently authored code whose rights are held by contributing authors | Embedded/transcribed upstream material remains under its applicable original license; provenance not exhaustively cleared file by file |
| Kernel configuration diffs, historical logs, manifests, screenshots/data/telemetry | No assumption that copyright/license is uniform | Based on OEM/NVIDIA/third-party underlying systems; factual SHA/log evidence is not an authorization to redistribute vendor software |
| NVIDIA TensorRT Edge-LLM upstream code | Apache-2.0 according to NVIDIA source repository | Keep original license and notice; original/reused NVIDIA code is NOT automatically relicensed MIT |
| NVIDIA Jetson Linux / R39 kernel or OOT driver source | License per respective source package, including potentially GPL and NVIDIA-specific terms | Examine each source header/package; Jetson P3834 boot assets not compatible with DRIVE P3960 |
| NVIDIA DRIVE OS, bootburn, board configs, security firmware, signed images, GPU driver binaries | OEM/NVIDIA contractual or vendor distribution terms | Not bundled here; do not distribute or bypass required authorization |
| TensorRT 10.16.x prebuilt distribution | NVIDIA proprietary license / independent packaging terms | Root MIT LICENSE does not cover TensorRT binaries |
| NVIDIA Qwen3.8-27B-NVFP4 model weights | Apache-2.0 listing at pinned official NVIDIA Hugging Face repository; check model and base-model terms | Weight shards are NOT bundled; users acquire at source and verify terms |
| PyPI tensorrt-edgellm 0.11.0 wheels | Listed Apache-2.0 on PyPI; packages have their own dependency/notice requirements | Wheels downloaded from NVIDIA/PyPI, not redistributed by this repository |
| Any external source URL / downloaded file | Its own owner and license | Merely linking a source does not transfer copyright |

### Source provenance and pending license review

The public archive is curated rather than a full copy of original D:/E: research workspaces. A previous screening kept two original paths out of the published archive because their NVIDIA-attributed code provenance requires review:

- edge/scripts/build-tree-prefix-policy.py
- edge/artifacts/native-tree-replay-v1.cu

Two other candidate paths were absent. See [REVIEW_REQUIRED.json](manifest/REVIEW_REQUIRED.json) for the precise classifications.

**Do not copy the excluded NVIDIA-attributed code into this repository merely to make reproduction easier.** If a future patch uses copied code, preserve original SPDX headers and the complete required license/NOTICE, and document source and changes in an independent reviewed contribution. The main LICENSE does not grant rights to third-party code.

### Contributor guidance

- Contribute only material you wrote or have permission to publish.
- For an original new file with no upstream source, it may carry SPDX-License-Identifier: MIT.
- If porting upstream NVIDIA/other code, retain its actual SPDX license and copyright notice; do not replace it with MIT.
- Never upload DRIVE firmware, proprietary SDK packages, kernel/driver redistributables without legal authority, OEM keys, HSM files, commercial customer information, model weights, engines or credentials.
- Preserve source and published SHA256 in [SOURCE_MAP.md](docs/SOURCE_MAP.md) and [SOURCE_MAP_FILES.tsv](manifest/SOURCE_MAP_FILES.tsv). Publicly accessible does not mean independently installable.
- Do not claim all 6.1/6.8/Edge-LLM source files were authored solely by this project's contributors unless validated.

See [DOWNLOAD_AND_REPRODUCE.md](docs/DOWNLOAD_AND_REPRODUCE.md) for lawful upstream acquisition and reproducibility limits.

This document describes the intended scope of the contributor MIT grant, not a legal certification or a determination that every previously archived code fragment is original.
