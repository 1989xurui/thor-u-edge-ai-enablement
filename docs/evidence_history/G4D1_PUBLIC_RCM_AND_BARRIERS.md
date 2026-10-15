> **Historical frozen evidence**, not current live state. Sanitized network identifiers. Source SHA256 retained in manifest/SUPPLEMENTAL_EVIDENCE.json. Do not execute commands from this report on a vehicle.

# G4D1_G4D2_G4E_G5_FINAL_REPORT（G4→G5 连续执行 · 终版）

- 日期: 2026-10-06
- 范围: G4D.1 PUBLIC T264 RCM PROBE → G4D.2 PUBLIC RCM RAM-BOOT FEASIBILITY → G4E COLD-BOOT Kernel 6.8 → G5 OPENRM GPU GATE
- 纪律: 每门 PASS 才进入下一门；第一次失败立即停；不刷 Jetson 板级镜像；不改 Golden；不绕 Secure Boot；不开放 PMC scratch 写权限。

## 状态汇总（终版）

```
G4D1_PUBLIC_RCM = FAIL
    （PUBLIC_T264_RCM_DETECT = FAIL · 分类 FAIL_RCM(物理传输面) · 三次实测两种接线）

G4D2_RAM_BOOT   = NOT_ENTERED（前置门未过；预研证据见 §3，预期 FAIL/BLOCKED_BY_SIGNATURE）

G4E_COLD_BOOT_1 = NOT_EXECUTED
G4E_COLD_BOOT_2 = NOT_EXECUTED
G4E_REPEATABILITY = NOT_EXECUTED

G5_OPENRM       = NOT_EXECUTED
G5_GPU_10DE2B00 = NOT_EXECUTED
G5_14SM         = NOT_EXECUTED
G5_CUDA_READY   = NOT_EXECUTED

READY_FOR_G6 = NO

CURRENT_BLOCKER =
RCM USB 物理传输面不可达：车机两个可及 USB-C 口均不承载 Thor xudc（设备口）。
实测（3 次）RCM 均成功进入（tegrarecovery+tegrareset → GOS 下线），
但 Windows 侧全程无任何新 USB 设备（含 0955 APX / 未知设备）。
⇒ 公开 tegrarcm_v2 无物理通道可触达 BootROM。公开工具链路线在 G4D.1 到达硬边界。

NEXT_ACTION =
由业主确认硬件侧路线（二选一）：
  A) 将 Thor USB 设备口（xudc，D+/D-）物理引出到 PC —— 恢复 G4D.1 探测能力；
  B) 改走 DRIVE SDK / MCU 官方路径（bootburn.py，`-R` RCM boot，需 NGC 授权）——
     注意此路径超出"公开工具链"设定（本报告 §3 的板级 BCT/签名墙预研同样适用）。

CONFIDENCE = HIGH（传输面结论为 3 次实测；G4D.2 预研为源码级证据）
```

## 1. G4D.1 执行全记录（PUBLIC T264 RCM PROBE）

### 1.1 软件侧（✅ 全部完成）
| 项 | 结果 | 证据 |
|---|---|---|
| BSP 下载 | ✅ 1,287,223,769 B 全量（官方直链，无需登录） | `11_g4d1_rcm/downloads/*.sha256` |
| 工具冻结（8 件） | ✅ sha256sum -c 全 OK | `11_g4d1_rcm/tools_frozen/`（tegrarcm_v2 `0a221ac9…`） |
| MANIFEST | ✅ 生成 | `11_g4d1_rcm/G4D1_PUBLIC_RCM_TOOL_MANIFEST.json` |
| CLI 实测修正 | ✅ 无 `--list`；只读集 = `--uid/--isapplet/--ismb2` | 管道烟测日志 |
| 烟测 | ✅ WSL 内可执行（无缺库） | 同上 |
| 探测脚本/runbook | ✅ | `_tools/g4d1_probe_run.sh`、`README_G4D1_PROBE_PLAN.md`、`_tools/G4D1_MCU_console.ps1` |

### 1.2 物理侧（❌ FAIL · 三次实测）
| # | 时间 | 接线 | RCM 进入 | APX 上机 |
|---|---|---|---|---|
| 1 | 17:08 | 仅调试 C↔C（CH342,COM5/6） | ✅（GOS 下线） | ❌ 无任何新设备 |
| 2 | 17:31 | 调试 C↔C + 另一口 C→USB | ✅ | ❌ |
| 3 | 17:40 | 同上（业主复插确认） | ✅ | ❌（0955/未知/非OK 全空） |

- T-0.5 零状态预检 PASS：NvShell `help` 实锤 `tegrarecovery [x1] [on|off]`、`tegrareset [x1] [h]` 在列。
- 全部进入/退出均走文档钦定原语；`tegrarecovery x1 off`+`tegrareset x1` 三次均恢复 GOS。
- 证据归档：`11_g4d1_rcm/evidence/G4D1_FAIL_TRANSPORT.txt` + `mcu_*.log` + `COM6_*.bin` + `serial_*.log`。
- 判定：`PUBLIC_T264_RCM_DETECT = FAIL`（任务书：公共工具无法识别 BootROM ⇒ G4D1=FAIL，停止）。
- 推证：调试口 = CH342 UART 桥（USB-serial 外设，非设备口）；另一口此前可带动 C→网口适配器 ⇒ host 口。
  RCM 数据面未向客侧引出（与官方"imaging 经 MCU 串口(bootburn.py)"一致）。

## 2. 边界遵守声明

全程无 flash / erase / write / BCT 更新 / MB1 下载执行 / slot 修改 / UFS 写；
无 kexec / 普通 reboot 测试 / PMC scratch 写（继承 G4A/G4C 冻结纪律）；
未改动 Golden / BSP / BCT / PCT / BPMP / 分区；所有 USB 侧操作仅枚举与只读探测（探测未获机会执行即有判定）。

## 3. G4D.2 预研结论（未正式进入；供决策参考）

- `tegraflash.py` 原生含 `rcmboot`（"Boot kernel without flashing"，需 `--bct/--cfg`，BSP 带 `flash_l4t_t264_rcmboot.xml`）。
- 公开 BSP 的 T264 板级配置 = **P3834/P4071（Jetson Thor T4000 开发板）**：
  `EMC_BCT=tegra264-p3834-0000-sdram-bct-l4t.dts` 等 ⇒ **无 P3960 配置**；用 T4000 BCT 属任务禁令。
- rcmboot 布局含 `oem_sign` 分区；公开 mb1/bl31/applet 为 Jetson 签名体系 ⇒ 生产熔断设备需 DRIVE/OEM 密钥。
- 详件：`11_g4d1_rcm/G4D2_SECURE_BOOT_MATRIX.md`（§4b）。

## 4. 车机状态（恢复）

- 三次进入 RCM 后均已执行退出（`tegrarecovery x1 off`+`tegrareset x1`），GOS 6.1 正常冷启动。
- 冷启动定制恢复（与 09-16 已知清单一致）：
  - SSH 公钥 / sudoers NOPASSWD / 网络([REDACTED_PRIVATE_IPV4]) / hugepages(20992,含 sysctl.d 持久化) —— 本次已恢复；
  - R4 三单元 + stack-health 计时器 —— 经 `COLD_BOOT_RESTORE.sh` 恢复（终态核验见 recovery 日志）。
- 遗留观察：本 boot 中 **RTL8153（车机 USB 网卡）未在线**（enx 接口缺失）——与本次拔插线缆相关，请业主检查该 USB 适配器是否松动（不属本任务边界，仅供注意）。

## 5. 结论与后续

公开 T264 工具链（tegrarcm_v2 等）已完整取得、冻结、并具备执行能力；`tegrarecovery/tegrareset` 进入/退出通道全程可用；
**唯一缺环 = Thor RCM USB 设备面未到达本机**。此缺环为物理/平台设计层面（非工具或操作问题），
在硬件路径打通（引出 xudc）或改用 DRIVE SDK/MCU 官方路径之前，G4D.2/G4E/G5 无执行前提。
