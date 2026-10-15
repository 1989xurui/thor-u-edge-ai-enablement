> **Historical frozen evidence**, not current live state. Sanitized network identifiers. Source SHA256 retained in manifest/SUPPLEMENTAL_EVIDENCE.json. Do not execute commands from this report on a vehicle.

# G4D_COLD_BOOT_PREPARATION_REPORT — THOR-U｜Direct Cold-Boot 6.8 落地准备门

- 日期: 2026-10-06
- 范围: 只做 A（host 工具链）/ B（boot-slot 只读审计）/ C（Cold-Boot 镜像冻结）；**零持久写入**；未执行 flash/bootburn/RCMBOOT/reboot/kexec/slot 切换。
- 证据根: `10_g4d_coldboot/`（含 raw/）+ `06_coldboot_image/`

```
HOST_TOOLCHAIN = PARTIAL
  （LEVEL 1 能力已由官方文档证实：bootburn.py + `-R`=RCM RAM 引导 + board_config 合法含 p3960-10-sw01；
    工具实体尚未取得——本机 D:/E:/车机全盘零发现；获取=业主 NGC 官方渠道，不得旁路）

BOOT_SLOT_AUDIT = PARTIAL
  （Guest 侧已榨干：GOS_KERNEL_SLOT_VISIBILITY = HOST_ONLY（release 文件/fuse/partlabel/nvbootctrl/EFI/
    ttyACM/flash 工具全 ABSENT，禁猜分区）；Asymmetric A/B 与 ratchet 集已取证；
    host 侧槽位号/retry 计数待 SDK 工具只读解析）

GOLDEN_ROLLBACK = PASS
  （G4E 走 RAM-only RCM 引导=不写盘 ⇒ 失败=物理冷断电即回 6.1 Golden；另有 09-29/10-06 两次冷断电
    回退实证 + COLD_BOOT_RESTORE.sh 售后恢复；写单槽变体=禁止）

PMC_SCRATCH_FIX = PASS
  （p3960-gos-k68.dtb：删 PMC scratch aperture（官方可选设计，缺失即不注册 reboot notifier 且跳过
    scratch sysfs 注册）；dtc 往返验证 + 编译 + 回读 scratch=0；sha 0d7a0bdd…）

COLD_BOOT_IMAGE = PASS
  （06_coldboot_image/ 六件套构建冻结、全 SHA256 可核；Image/initrd/cmdline 与 g35 装载件逐字节同源；
    DTB 为唯一新增安全修正件）

READY_FOR_G4E = NO
  （§十五 必要条件逐条核：合法可用 host 工具 ✗（PARTIAL）；明确 boot/slot 结构 ✗（PARTIAL）；
    Golden 恢复方法 ✓；镜像冻结 ✓；PMC scratch 消除 ✓；initrd 只读验证 ✓；SHA256 ✓；零持久写入 ✓）

CURRENT_BLOCKER =
  取得 DRIVE OS 7.0.3 SDK host 工具链（bootburn -R / drive-foundation / p3960-10-sw01 board config，
  官方 NGC 通道）并完成 host 侧 boot 镜像/slot 只读解析。之前不得写任何启动槽位。

RECOVERY_METHOD =
  主：RAM-only RCM 引导零写盘 → 失败幂等回归（物理冷断电即回 Chain A / 6.1 Golden）；
  辅：物理冷断电路径（两次实证）+ `/zeekr_data/thor-ai/production/scripts/COLD_BOOT_RESTORE.sh`；
  后备：Asymmetric A/B 与 Chain-C（厂端，待工具复核）。

NEXT_ACTION =
  走官方 NGC 渠道取得 DRIVE OS 7.0.3 SDK host 包并在隔离主机落地登记
  （bootburn.py/drive-foundation/board_config 的版本+SHA256+license 回填矩阵）。

CONFIDENCE = HIGH
```

---

## 1. 三项工作台账

| 项 | 结果 | 关键证据 |
|---|---|---|
| A 工具链 | **PARTIAL** | 官方 Flash Steps：`bootburn.py` 位于 `drive-foundation/tools/flashtools/flash/`；`-R`=RCM boot（RAM 直接引导）；`board_config` 合法标识符含 **p3960-10-sw01**；本地/车机检索=零发现；NGC 账号（xurui）+ ngc-cli 4.10.0 在位（E:\Thor_Downloads）→ 唯一合法获取通道=官方授权 → `G4D_HOST_TOOLCHAIN_MATRIX.md` |
| B slot 审计 | **PARTIAL** | 冷启动链逐级取证（MB1→…→PSC/SB/HPSE→HV-Prod-Secure/BL31→GOS boot image→Linux 6.1→vblkdev0）；guest 可见性全表（全 ABSENT）/chosen 元数据/hypervisor-mode/ratchet 固件集；**GOS kernel/DTB/initrd=HOST_ONLY、不猜分区** → `G4D_BOOT_CHAIN_MAP.md` + `G4D_SLOT_PARTITION_MAP.json` |
| C 镜像 | **PASS** | `06_coldboot_image/`：Image-6.8.12-coldboot（`482a7c41…`）/ p3960-gos-k68.dtb（`0d7a0bdd…`）/ initrd-g4e-minimal（`18ce10ca…`）/ initrd-g4e-debug（`8479c4c0…`）/ cmdline-g4e.txt（`d0db3209…`）/ SHA256SUMS + G4E_IMAGE_MANIFEST；`sha256sum -c` 全 OK → `G4D_COLD_BOOT_IMAGE_PLAN.md` + `G4D_PMC_SCRATCH_DTB_PLAN.md` |

## 2. 恢复设计要点（§十一 回答）

1. **首选 RAM-only RCMBOOT**：`bootburn -R` 不写盘 ⇒ 最坏情况=断电即回 Golden（幂等，与 10-06 kexec 实验的"零写盘-断电即回"模式同理）；
2. **已实证兜底**：物理冷断电两次实战 PASS（09-29 / 10-06），冷启动后跑 `COLD_BOOT_RESTORE.sh` 恢复售后定制（该机已知跨断电定制丢失现象）；
3. **厂端后备**：Asymmetric A/B 链与 Chain-C（MCU GPIO）——待 SDK 落地后复核启用；
4. **红线**：若某变体必须写单槽且无 A/B 可用 ⇒ G4E 禁止执行。

## 3. Early Stop 条款对照（§十二）

| 条件 | 现状 |
|---|---|
| 无法确认 Kernel/DTB 实际加载位置 | **部分**：装载者/层级已确证（HV 阶段、HOST_ONLY），具体槽位待工具 → 计入 PARTIAL |
| 无法确认 Golden 恢复方法 | 否（§2 完备） |
| 只能覆盖唯一启动 Kernel | 否（A/B 存在；且主路径零写盘） |
| 没有可用 RCM/alternate slot | 能力存在（-R）；工具未到位 → 计入 PARTIAL |
| 必须改 BPMP/BCT 才能工作 | 否 |
| 必须改 HV stage-2 权限 | 否 |
| 需要给 Guest 开放 PMC scratch 写 | 否（反向：DT 删除 aperture） |

⇒ 未触发硬性 Early Stop；**因 §十五 两条必要条件未满足，READY_FOR_G4E = NO**（框架性未就绪，而非路线被否）。

## 4. 让 READY_FOR_G4E 翻 YES 的确定性路径

1. NGC 取得 SDK → 回填矩阵（SHA/license）→ HOST_TOOLCHAIN 升 PASS；
2. SDK 工具**只读**解析 boot 镜像/槽位 → 回填 `G4D_SLOT_PARTITION_MAP.json` host_only 字段 → BOOT_SLOT_AUDIT 升 PASS；
3. 隔离主机预演 `bootburn --help`/板级 dry（不接车）确认 `-R` 零写盘语义 → 写入 G4E 预检清单；
4. 全部 SHA 复核 + 冷断电通道确认 → 提交 G4E 执行 Gate（另开）。

**本轮终点**：Kernel6.8 直接冷启动已从"理论路线"变为"具备明确工具规格、明确 guest/host 边界、明确恢复设计与冻结镜像"的方案；**在任何槽位写入或引导执行发生前，本报告即为当前终点。**
