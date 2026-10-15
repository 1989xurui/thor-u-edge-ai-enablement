> **Historical frozen evidence**, not current live state. Sanitized network identifiers. Source SHA256 retained in manifest/SUPPLEMENTAL_EVIDENCE.json. Do not execute commands from this report on a vehicle.

# G4D_DU2_HARD_GATE_REPORT — Bootchain Mode + DUPKG + Signature 硬门终报

- 日期: 2026-10-06；执行: 车机只读会话 du2_s1…s4（`12_g4d_du2/du2_s*.log`）+ COM5 只读（readNvRam/version）+ 免登录官方文档 + 本地 R39.2.1 冻结工具 + 公开研究代理（no-account 口径）
- 边界合规: **ZERO WRITE / ZERO FLASH / ZERO SLOT SWITCH / ZERO BOOTCHAIN SET / ZERO DUPKG INSTALL / ZERO REBOOT / ZERO KEXEC / ZERO TEGRARESET** 全程保持；未绕签、未 patch verifier、未动 fuse/BCT/PCT/HV；触发 §13 早停条件（"需要未知 OEM 私钥"）后即止。
- 关联交付: `12_g4d_du2/G4D_DU2_{BOOTCHAIN_MODE, CHAIN_ENUM_MAP, DUPKG_SPEC, HOST_TOOL_MINSET, OEM_OTA_EVIDENCE, SIGNATURE_LAYERS, MARKER_BOOT_PLAN, INACTIVE_CHAIN_DEPLOYMENT_DESIGN}.md`

## 四问直接回答（本门总目标）

1. **链选择模式**：GPIO（INFERRED-HIGH）。官方默认 GPIO、marker 需 `setbtchnsel` 显式切换；本车 GPIO 模式控制面整链在配置（tacp.cfg `AURIX_BOOTCHAIN_PORT=5001`、mcc_daemon、bootmgr MCC/I2C）；bootmgr 的 `DU_MCC` 0x9 与 IST 超时 = 该通道**在本车停用**（mcc_daemon 启动 2min33s 后主动退出），**不是"A/B 不可用"**。
2. **DUPKG 格式/builder**：格式 = PARTIAL（结构到"容器/元数据/命令/鉴权"层已恢复，见 SPEC 文档）；builder = **BLOCKED**（dupkg.py/模板/HSM 签名 = PDK-only，官方论坛证据；无社区副本；无账号不可得）。
3. **两层独立认证**：**是（CONFIRMED）**。Layer 1 = DUPKG 包鉴权（du_auth：NVDU-SIG/RSA3K/SHA256/块哈希表/PKCS#11/DT auth-key）；Layer 2 = 引导链认证（BCH 8×OEM-signed + PVIT sha512 + BRBCT OEM 密钥 + ratchet），**kernel/kernel-dtb 在 Layer 2 覆盖内**（官方原文："Guest OS binaries including kernel"）。
4. **K68 合法签名路径**：**不存在（无账号/无密钥前提下）** ⇒ BOOT_IMAGE_AUTH = REQUIRED_BUT_BLOCKED。

## 最终判定（门 §14 固定字段）

```
BOOTCHAIN_SELECTION_MODE = GPIO
  （INFERRED-HIGH；直读本车模式行需上电 COM5 捕获，超出 ZERO REBOOT 边界，未做）

CHAIN_ENUM_MAPPING = PARTIAL
ACTIVE_CHAIN       = UNKNOWN   （三源原始值均为 "0"：/tii/ver/active_bootchain、ctx last_bootchain、update-info；
                                旁证强指向 A：gos-a 插件独占、默认读 A_pvit；"0"→A 映射无权威证据）
INACTIVE_CHAIN     = UNKNOWN

DUPKG_FORMAT   = PARTIAL        （结构已恢复；字段全集与打包器未公开）
DUPKG_BUILDER  = BLOCKED        （PDK-only + 密钥面 OEM_ONLY）

OEM_OTA_SAMPLE = NOT_FOUND      （ota_cache/ddi/parameter 空；/zeekr_plt 全空骨架；全盘无 dupkg/du_master/auth_conf 实体）

DUPKG_AUTH     = BLOCKED        （authenticated package 需 HSM/PKC 私钥；DUPKG_AUTH_KEY_OWNER = unknown/platform）
BOOT_IMAGE_AUTH = REQUIRED_BUT_BLOCKED
  （官方：kernel 属认证对象；BCH=8×OEM-signed；BRBCT 内嵌引导链认证密钥；
    满足需 NVIDIA/OEM 私钥+HSM —— 无合法来源 ⇒ 依门 §10 判定并停止部署设计）

MARKER_BOOT_PATH = NOT_APPLICABLE   （本车 GPIP 模式；即使 marker 亦被 Layer2 阻断）

G4D_DU2              = BLOCKED_BY_BOOT_AUTH
READY_FOR_G4D_DU3    = NO        （DU3 前提[离线生成合法 DUPKG]不成立）
READY_FOR_G4E        = NO

CURRENT_BLOCKER =
① 冷启动链认证（Layer 2）：修改后的 kernel/kernel-dtb(/ramdisk) 需要被 BRBCT/熔丝链承认的
   NVIDIA/OEM 签名（BCH/PVIT/RSA + ratchet）——我方无密钥、无 HSM、无账号；
② DUPKG 打包器（dupkg.py/模板/create_bsp）为 PDK-only——无公开/社区获取路径；
③ 本车 GPIO 链控通道（bootmgr→DU_MCC→mcc_daemon→Aurix:5001）当前停用
   （mcc_daemon 已退出；0x9/IST 超时同源）——即便有合法包，换链时序面也需先修复。

NEXT_ACTION =
出具并归档 G4D-DU2 终判（BLOCKED_BY_BOOT_AUTH），正式关闭 DRIVE Update / A-B-C 部署路线；
后续由业主决策是否转向官方通道（NVIDIA/Zeekr 持钥方）。本门不执行任何车机写入。

PERSISTENT_WRITE = ZERO
REBOOT_COUNT     = ZERO
CONFIDENCE       = HIGH
```

## 证据索引

| 内容 | 位置 |
|---|---|
| 会话原始日志（每命令 SEND/RX 逐字节） | `12_g4d_du2/du2_s1.log` … `du2_s4.log` + `_tools/du2_s*_cmds.txt` |
| MCU 只读（readNvRam 模板/版本；命令表 88 条） | `11_g4d1_rcm/evidence/mcu_raw_20261006_1902…/1903…` + `170755` |
| mcc_daemon/bootmgr/dutii/du_auth/ctx_store/DUS 字符串（含偏移） | du2_s2/s3/s4 |
| ctx（NVDUCTX 1.2.0）与 /tii 节点实测 | du2_s2/s4 |
| 官方文档原文（免登录复核） | DU V3 Developer Guide / Authentication and Validation / Grouping a Secure Boot Chain / BootChainProcess8 / Asymmetric Steps（7.0.3）|
| 本地公开工具对照（bch pcp 388B、--boot_chain、--cust_info、--minratchet） | `11_g4d1_rcm/tools_frozen/` |
| K68 三件套哈希 | Image `482a7c419b6903fce27ea3a05c2a1eeb801e4f4b95c9b409b33d439db8b81f19`；dtb `0d7a0bdd29f48be08090c1b72607ccc5d77a8ee71d5a6e2082c3fceff8c5d64e`；initrd `18ce10caeb55a0339126b354f0ce4254a20aa9f16102315ffd372863a51ef04a` |

## 一句话结论

**DRIVE Update / A-B 更新机制的"机械面"在车上完整（DU V3 全栈 + TII/BRBCT/marker 命令 + GPIO 链控配置），但对"自建 Kernel6.8"这条路：真正的硬门是冷启动链级认证（BCH/PVIT/BRBCT-OEM-key + ratchet）——无 NVIDIA/OEM 密钥与 HSM 不可满足；叠加打包器 PDK-only 与本车链控通道停用 ⇒ `G4D_DU2 = BLOCKED_BY_BOOT_AUTH`，本路线在无账号约束下关闭。**
