# Download & Reproduce / 下载、校验与复现实验

**Updated 2026-10-15 · Public project · MIT for original contributor-owned work; vendor licenses unchanged.**  
This is a reproducibility contract and verified download index, **NOT an automated DRIVE P3960 firmware installer**.

## 0. Choose a reproducibility level

| Level | Reproduces | Public files sufficient? | Status |
|---|---|---|---|
| **R0** | Clone archive, parse docs/source map, all offline SHA/gates | YES | PASS using public repo |
| **R1** | Fetch exact upstream Edge-LLM v0.11.0 / PyPI wheel / 27B model shards and SHA check | Requires Internet, compatible host, disk and license acceptance | SHA/links specified; each user must download/verify |
| **R2** | Build precise Kernel 6.8.12 G35, R39 NvGPU, CUDA13.2, TensorRT plugins on a new host | NO; missing complete external vendor/toolchain inputs | PARTIAL / qualified independently |
| **R3** | Enter experimental RAM-booted 6.8 and run actual A1 CUDA / 27B 8K test | NO; requires supported device, original firmware/runtime, recovery plan and controlled access | HISTORICAL_SCOPED_PASS, not a general installer |
| **R4** | Independent 6.8 cold boot, persistent dual boot and full production Edge-LLM | NO; OEM bootchain/signing/RCM/rollback, full quality | **BLOCKED/NO_GO** |

**Project MIT license does not authorize flashing OEM assets, distributing NVIDIA binaries, signing vendor firmware or bypassing security.** See [LICENSE](../LICENSE), [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) and [AGENTS.md](../AGENTS.md).

## 1. R0: reproduce the public research archive on any suitable development computer

~~~sh
git clone https://github.com/1989xurui/thor-u-edge-ai-enablement.git
cd thor-u-edge-ai-enablement

python3 tools/verify_manifest.py
python3 tools/check_source_map.py
python3 tools/verify_download_lock.py
python3 tools/check_repo_release.py

# These are expected to exit 2 / HOLD, not failure of documentation:
python3 tools/check_dual_boot_readiness.py
python3 tools/check_program_readiness.py --summary
~~~

No DRIVE SDK account, model weight, GPU or vehicle is needed for R0. The last two scripts correctly flag unknown OEM/production conditions, and should NOT block code inspection or offline reproducibility tasks.

## 2. Exact public upstream source and artifact addresses

| Component | Verified official entry | Version / license | Can reproduce directly? |
|---|---|---|---|
| NVIDIA TensorRT Edge-LLM source | [Tag v0.11.0](https://github.com/NVIDIA/TensorRT-Edge-LLM/tree/v0.11.0) | Commit 95515c2f87fba8982db5a519f9022277667b3cc9, Apache-2.0 | Public source; local compiled wheel revision differs |
| Edge-LLM v0.11.0 ARM64 wheels | [PyPI release](https://pypi.org/project/tensorrt-edgellm/0.11.0/) | Apache-2.0, CPython 3.10/3.11/3.12 manylinux_2_39_aarch64 | Direct SHA-verified wheel download possible, but not self-contained |
| 27B NVFP4 exact model | [NVIDIA Qwen3.8-27B-NVFP4 pinned revision](https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/tree/fed99d815f4e8c7c616dd3dd6780076e26d5fb61) | Revision fed99d815f4e8c7c616dd3dd6780076e26d5fb61, model card Apache-2.0 | Download and validate separate 20.42GiB weights |
| CUDA Toolkit 13.2 U2 | [Official CUDA 13.2.2 archive](https://developer.nvidia.com/cuda-13-2-2-download-archive) | CUDA Toolkit 13.2.2, NVIDIA EULA | Choose official host/target package; not a DRIVE 7.0.3 driver replacement |
| Jetson Linux R39.2.1 source | [Kernel customization guide](https://docs.nvidia.com/jetson/archives/r39.2.1/DeveloperGuide/SD/Kernel/KernelCustomization.html) and [download archive](https://developer.nvidia.com/embedded/jetson-linux-archive) | R39.2.1 source includes file-specific GPL/vendor terms | Kernel/OOT source possible; NOT a P3960 DRIVE signed cold-boot package |
| TensorRT 10.16.0.72 | [NVIDIA PyPI version page](https://pypi.org/project/tensorrt/10.16.0.72/) | NVIDIA proprietary distribution terms | Package index, not proof of a full matching AArch64 runtime |
| DRIVE Thor 7.0.3 host boot tools | [NVIDIA DRIVE Thor Bootburn guide](https://developer.nvidia.com/docs/drive/drive-os/7.0.3/public/drive-os-linux-sdk/getting-started/flash_steps_for_Thor_SOC.html) | OEM/DRIVE SDK authorization, signing/board config requirements | Documentation link only; NO public universal firmware installer |

**Important:** The version of a PyPI wheel or Git tag is not proof that its TensorRT/CUDA/SM110 binaries match the ones in the A1 session. The historical installed Edge wheel reported revision **74f8732a7e8d1377e34471ad2652988346f18813**, different from upstream v0.11.0 source commit above.

### Pinned Edge-LLM v0.11.0 public AArch64 wheels (PyPI hashes)

Choose **one** wheel matching Python ABI on a compatible AArch64 Linux host (glibc 2.39+).

| Python | Size (bytes) | SHA256 | Official direct file |
|---|---:|---|---|
| cp310 | 447,051,288 | 9bb4383ef013a2108d2c077c8758a1a1ecbb2995ac9450ae02d5611dcecba611 | [PyPI wheel cp310](https://files.pythonhosted.org/packages/90/8b/2a8e32f3fd7bf25446eb777ffd0bc8f8583b699a0de2eb3b5bc599cc45be/tensorrt_edgellm-0.11.0-cp310-cp310-manylinux_2_39_aarch64.whl) |
| cp311 | 447,058,774 | 21a66a57de5264bcf24e3e699e3e7b660e9541409d978cb5e76fe92e890b9c33 | [PyPI wheel cp311](https://files.pythonhosted.org/packages/c0/1f/2b46c643045322cf06b1f895b1111fc4f5eeb3fc38c025762d35773311ea/tensorrt_edgellm-0.11.0-cp311-cp311-manylinux_2_39_aarch64.whl) |
| cp312 | 447,070,745 | 9e6722a5a250d0ba18665911a908aecfc9684722b9d56d944efe31fe6c889d9b | [PyPI wheel cp312](https://files.pythonhosted.org/packages/c2/07/32efeb227b4b4c952b051ab9b990b21146756296b5ee65450de827cc5072/tensorrt_edgellm-0.11.0-cp312-cp312-manylinux_2_39_aarch64.whl) |

The wheel download links and SHA values were checked against NVIDIA's PyPI 0.11.0 release metadata. **We did not download or run the 447MB packages during this documentation update.** Installation dependencies remain separate.

Recommended developer-host workflow (only if you want the file):

~~~sh
# By default prints trusted URLs and SHA values, WITHOUT network access
python3 tools/fetch_public_wheel.py --list

# Explicit opt-in: fetch ONE pinned wheel outside the Git checkout,
# with byte count and SHA256 verification, no installation:
python3 tools/fetch_public_wheel.py --python cp311 --download --out ../external-assets/edge-wheel

# Offline check after download:
python3 tools/verify_download_lock.py --directory ../external-assets/edge-wheel --require-wheel cp311
~~~

Choose cp310/cp311/cp312 for your environment. Running this on Windows can **download** the wheel, but cannot execute it; it targets AArch64 Linux manylinux_2_39. Never put it under your Git repository, overwrite the target runtime or run pip directly in the OEM read-only root.

## 3. Download pinned 27B model weight shards (~20.42 GiB)

The official model page lists three Safetensors weight shards, tokenizer, config, preprocessor, and model license. Use the upstream Hugging Face CLI from a **development machine** and a destination with sufficient free space (recommend >35GiB free for this operation, more if building Engines).

~~~sh
python3 -m pip install --upgrade huggingface_hub

# Download EXACT release commit into an external working folder
hf download nvidia/Qwen3.8-27B-NVFP4 \
  --revision fed99d815f4e8c7c616dd3dd6780076e26d5fb61 \
  --local-dir ../external-assets/qwen-nvfp4

# Stream-hash the three large shards (can read 20+ GiB)
python3 tools/verify_download_lock.py \
  --directory ../external-assets/qwen-nvfp4 \
  --require-model
~~~

Pinned weight file SHA256:

| Filename | Bytes | SHA256 |
|---|---:|---|
| model-00001-of-00003.safetensors | 9,965,652,544 | 7d0fd155118901373eb0fd13ed3aae68f95be747bc205be72ebc41739c25ee80 |
| model-00002-of-00003.safetensors | 9,985,757,064 | 98a7e9486baa860c792c9463a770cb9d017696bdd17606300a5b9334149f4c27 |
| model-00003-of-00003.safetensors | 1,970,287,672 | 0506ad35dc21469708e7813bd76c592cef08bd0317b4a1fe899745ebe2435271 |

SHA values come from the historical frozen Thor-U asset record and must be **rechecked by downloaders**; do not assume another model revision or replacement shard is equivalent. Model card indicates Apache-2.0; the project's MIT does not relicense those NVIDIA weights. Target/Draft TensorRT Engines (potentially >16GiB) are **not provided**.

## 4. Reproduce upstream TensorRT Edge-LLM 0.11.0 source version

~~~sh
git clone https://github.com/NVIDIA/TensorRT-Edge-LLM.git ../external-assets/TensorRT-Edge-LLM
git -C ../external-assets/TensorRT-Edge-LLM checkout --detach v0.11.0
git -C ../external-assets/TensorRT-Edge-LLM rev-parse HEAD

# EXPECT exact hash:
# 95515c2f87fba8982db5a519f9022277667b3cc9
~~~

Next, use the official [0.11.0 installation guide](https://nvidia.github.io/TensorRT-Edge-LLM/0.11.0/user_guide/getting_started/installation.html) with a **platform matching the NVIDIA support matrix**, an appropriate TensorRT binary and Python ABI.

The historical **DRIVE 7.0.3 + Linux 6.8 kexec + CUDA13.2 + TensorRT 10.16.x + Edge0.11.0** combination is an independently researched stack, **not an officially supported DRIVE 7.2/CUDA13.3 preset**. Rebuilding v0.11.0 upstream with official instructions on other hardware does NOT guarantee A1 byte-identical Engines or the saved K7/Tree scores. Reproduce by progressively matching source patches, ABI, model input lengths, quantization, Graph/MTP/cache and output IDs.

## 5. R2/R3: what must be supplied for exact Thor A1 reproduction

Read [SOURCE_MAP.md](SOURCE_MAP.md), [ASSET_AND_VERSION_LOCK.md](ASSET_AND_VERSION_LOCK.md), [BUILD_KERNEL_GPU_CUDA.md](BUILD_KERNEL_GPU_CUDA.md), and [EDGE_LLM_27B.md](EDGE_LLM_27B.md).

External dependencies **not in GitHub**:
- A complete, license-compliant Kernel 6.8.12 source tree at commit 78272943bba3a47e633b28963b0cda60de503500, G35 config SHA and matching build toolchain;
- NVIDIA R39.2.1 NvGPU/host1x/DRM OOT closure with exact vermagic/symbol CRC plus lawful corresponding 595.78 user libraries/firmware;
- official CUDA13.2.86 runtime/compiler and target-appropriate GPU;
- matching TensorRT 10.16.x, Edge 0.11.0 installed wheel/plugins plus pinned model and separately generated engine;
- OEM-specific DRIVE P3960 boot and recovery credentials/tools/signatures for any truly independent cold-boot path.

**Do not cross-flash DRIVE Thor with Jetson T4000/P3834 boot components.** Historical A1 validated 6.8 RAM entry and basic CUDA compute, and historical Edge K7/Tree have scoped 8K token-ID measurements. None prove reproducible DRIVE 6.8 cold boot or full model quality on another board.

## 6. Verification and honest publish claims

Run offline:

~~~sh
python3 tools/verify_manifest.py
python3 tools/verify_download_lock.py
python3 tools/check_source_map.py
python3 tools/check_repo_release.py
~~~

Ready:
- Repo files/HASH/schema: **can be independently reproduced without SDK/GPU**.
- PyPI wheel/source/model downloads: **public verified links and hashes; actual download/install is user-dependent**.
- Clean-host build, target CUDA and 27B quality: **not automatically validated by this repository**.
- Persistent 6.8 boot / production: **NOT QUALIFIED**.

A missing firmware/SDK/model dependency must yield a precise HOLD and a lawful next action, **not a fabricated success** or an instruction to bypass OEM security. See [AGENTS.md](../AGENTS.md) for assistant execution policy.
