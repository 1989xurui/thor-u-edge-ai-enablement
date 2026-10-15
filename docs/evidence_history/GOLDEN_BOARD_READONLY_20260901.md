> **Historical frozen evidence**, not current live state. Sanitized network identifiers. Source SHA256 retained in manifest/SUPPLEMENTAL_EVIDENCE.json. Do not execute commands from this report on a vehicle.

# Golden Board Stage 1 — Read-only capture

Capture status: **PASS with visibility limitations**

## Board identity

- Hostname: `tegra-ubuntu`
- User used for capture: `nvidia`
- Model: `p3960-0010`
- Compatible: `nvidia,p3960`, `nvidia,tegra264`
- SoC: Tegra ID 38, Silicon A01
- Platform classification: NVIDIA T264 / Tegra264 / Thor-U
- RAM: 58 GiB usable / 60082 MB reported by tegrastats / 64 GB board class

## Software and AI runtime

- OS: Ubuntu 24.04.1 LTS, aarch64
- Kernel: 6.1.119-rt45-prod-rt-tegra, PREEMPT_RT
- NVIDIA rootfs version: 7.0.3.0-40740537
- CUDA runtime: 12.8, driver and libcudart present
- TensorRT: [REDACTED_PRIVATE_IPV4] runtime libraries present
- tegrastats: PASS
- nvcc/trtexec: absent; no software was installed

## Network baseline

- Thor management NIC: `enx00e04c680f84`, `[REDACTED_PRIVATE_IPV4]/24`
- MAC/driver: `[REDACTED_MAC]`, r8152, RTL8153
- Link: 1 Gbps Full Duplex
- Persistence: `/etc/systemd/network/99-nv_enx_default.network`
- Five `/etc/systemd/network` files copied read-only to `systemd-network/`
- Remote/local SHA-256 comparison: 5/5 PASS
- Automotive `mgbe*` interfaces and VLANs were not modified

## Storage baseline

- Guest-visible virtual block map: PASS
- Root: `/dev/vblkdev0`, ext4, 4 GiB, read-only
- Platform/pilot: `/dev/vblkdev6` and `/dev/vblkdev7`, read-only
- Writable data/map/overlay devices recorded with exact byte sizes and UUIDs
- No raw block content was read, copied, mounted, reformatted, or written

## Boot and security visibility

- Kernel, command line, device tree model/compatible, and full FDT SHA-256 captured
- BPMP firmware identifier: `523d292f736562a39fa1-881e2f3c37bf`
- Bootloader version: not exposed to this Linux guest
- ECID: not exposed through safe sysfs/procfs paths
- Secure Boot: unknown/not exposed; EFI runtime directory is absent and dmesg reports `UEFI not found`
- The absence of EFI variables does not prove the physical secure-boot chain is disabled

## Files in this capture

- `SYSTEM_INFO.txt`
- `HARDWARE_INFO.txt`
- `NETWORK_INFO.txt`
- `CUDA_TENSORRT.txt`
- `PARTITION_MAP.txt`
- `BOOT_SECURITY_INFO.txt`
- `FILE_HASHES.txt`
- `GOLDEN_BOARD_REPORT.md`
- `systemd-network/` — five verified read-only copies

## Safety statement

No Thor persistent file or setting was modified. No flash, bootburn, package installation, update, bootloader/DTB/fuse/partition operation, filesystem write, or network modification was performed. Sudo was used only for read access to existing metadata and files.

## Important local access note

BOSGAME's `[REDACTED_PRIVATE_IPV4]/24` secondary address is currently an ActiveStore entry designed to preserve DHCP. It will disappear after a Windows reboot or NIC reset; restore that Windows-only address before attempting a later SSH capture.

## Next safe step

Create a second offline copy of the entire `D:\Thor64G\GoldenBoard\` directory and verify every file with a BOSGAME-side SHA-256 manifest. Do not image or read raw Thor block devices until a separate, device-specific acquisition plan and storage capacity review are approved.
