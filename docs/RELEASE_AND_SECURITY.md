# Repository release and safety policy

This repository is a **private, source-centric research archive** as of 2026-10-15, not a public binary distribution or an executable installer.

- No credentials, authentication tokens, company passwords, signing keys, SSH keys or live SQLite databases.
- No model weights, Engine binaries, firmware, NVIDIA proprietary driver/source archives, compressed SDK packages or WSL VHDX.
- Selected source files with private LAN IP literals have only documentation-range IP replacements. Their SHA-256 source and transformed hashes are recorded; redacted scripts are not runnable production configurations.
- Two vendor-copyright source files were withheld for explicit license/provenance review. Apache-2.0 references or licensed source content must keep corresponding required attribution and license texts before any future public release.
- Do not upload source snippets from NVIDIA proprietary SDK materials merely because the destination repository is private.
- The 6.1 -> 6.8 historical kexec RAM experiment is not an independent permanent boot path. No executable dual boot, cold RAM boot, host slot remap, firmware flashing or image activation is authorized by this repository. See docs/BOOT_6_1_TO_6_8.md for HOLD gates.
- Read REVIEW_REQUIRED.json before treating the snapshot as comprehensive. Missing files must not be represented as fully backed up.
- GitHub Actions include one **manual-only** workflow in .github/workflows/offline-validation.yml. It verifies SHA/static documentation and asserts that cold boot and full program gates still return HOLD. It never connects to a vehicle, runs GPU tests, prints credentials, or deploys models.
- Each source-evidence item must be tied to a date, code SHA, model SHA, exact software stack and a PASS/FAIL/HOLD decision with its experimental scope.
- The original R4 llama.cpp and API gateway project are intentionally outside scope.
- A private source archive is not a replacement for verified offline golden images, proprietary firmware backup or boot-recovery assets.
- Do not put blanket MIT/Apache licensing on mixed-origin files until full authorship and third-party rights have been confirmed.

Ready-to-publish gates:
1. Local SHA check 100% PASS.
2. No 100MB Git blobs / no binary weights/SDK.
3. Automated credential/privacy scan PASS on every staged file.
4. Manual review of CODE provenance and LICENSE requirements.
5. Distinct kernel/CUDA/Edge completion decisions and explicit unsupported paths.
6. Isolated clone on another workstation + manifest check PASS.
7. Git remote repository confirmed PRIVATE before first push.
