> **Historical frozen evidence**, not current live state. Sanitized network identifiers. Source SHA256 retained in manifest/SUPPLEMENTAL_EVIDENCE.json. Do not execute commands from this report on a vehicle.

# G4D_DU_READ_ONLY_GATE_REPORT — DRIVE Update / A-B-C Boot Chain 只读门（终报）

- 日期: 2026-10-06；执行: 车机串口只读会话 du_s1…du_s7（`11_g4d_du/du_s*.log` + `_tools/du_s*_cmds.txt`）
- 门目标: 零写入/零重启条件下，确认 DriveOS 7.0.3 是否提供合法的 A/B/C 链更新入口，使 Kernel6.8 Candidate 可未来部署到非活动链且不依赖 APX/RCM
- 关联交付: `11_g4d_du/G4D_DU_COMPONENT_MATRIX.md` / `G4D_DU_BOOTCHAIN_EVIDENCE.md` / `G4D_DU_UPDATE_PATH_MAP.md` / `G4D_DU_GOLDEN_RECOVERY_MAP.md` / `G4D_DU_K68_DEPLOYMENT_PLAN.md`

```
DRIVE_UPDATE_COMPONENTS = PASS
（DU V3 八组件全栈在位运行：dulink_router/dumaster/ctx_store/dubhc_plugin/bootmgr/du_auth/du_decomp/dutii.t26x
 + sample_driveupdate 工具；哈希/许可/单元/依赖/配置全部登记）

BOOTCHAIN_QUERY         = FAIL
（工具在位但官方链查询被平台级阻断：bootmgr→DU_MCC→TACP→Aurix:5001 返回 Error 0x9，
  -q 客户端挂起；旁路只读到 TII 原始值 "0"（无法解码为 A/B）。部分查询成功：part_ver/du_list/du_read 只读面可用）

ACTIVE_CHAIN            = UNKNOWN
（raw "0"；旁证指向 A：[gos-a 插件独占本 VM + /tii/ver/active_bootchain="0" + 默认读 A_pvit]——映射未证实，不猜）
INACTIVE_CHAIN          = UNKNOWN
（对应侧应为 B，但取链阻断，无确认）
CHAIN_C                 = PRESENT
（/tii/C_pvit 数据在位可读；用途=L1PT/recovery 语义 INFERRED；状态/内容未解读）

UPDATE_ENTRYPOINT       = CONFIRMED
（DULink 命名空间 14 节点实列；/tii 26 子节点；NVSCI 通道对 a..m；du-client 通道 i；root 可调用）
GUEST_UPDATE_AGENT      = CONFIRMED
（部署状态机 RESTORE_CTX / RL_DORMANT；installer+TII 安装能力在栈内；ctx_store 于 /dev/vblkdev60）

GOLDEN_CHAIN            = UNKNOWN
（旁证指向 A；门规不猜）
GOLDEN_ROLLBACK         = CONDITIONAL
（机制骨架在栈内 [Get/Set/Next/Default/expect/BHC]；但链读取平台级失效、零写入未演练、C 链属 L1PT 高风险域）

K68_DEPLOYMENT_FORMAT   = PARTIAL
（分区映射与写入机制已知：kernel / kernel-dtb / ramdisk 独立分区 + TII 分区级安装；
 但 DU_PACKAGE_FORMAT = BLOCKED —— DUPKG 打包器/规格不在车内（仅消费端），不得伪造）
SIGNATURE_REQUIREMENT   = KNOWN
（NVDU-SIG / RSA3K / SHA256；du_auth 经 PKCS#11 以 DT auth-key 验签；无合法 NVIDIA/OEM 签名链在手）

G4D_DU                  = CONDITIONAL
（A/B/C 架构+更新入口确认存在；缺：DUPKG builder/规格、合法签名、host 打包工具——
 与门规 CONDITIONAL 定义逐字吻合；另叠加平台链查询 0x9 阻断）

READY_FOR_G4E           = NO

CURRENT_BLOCKER =
① 链查询/控制通道平台级失效：bootmgr DU_MCC_GetActive/GetDefaultBootChain → Error 0x9（Aurix TACP:5001 路径）；
② DUPKG 打包/签名/host 工具链缺失（须 DRIVE OS SDK/NGC 官方渠道，车上无任何实体）；
③ /chosen/driveupdate 策略 allow-read-activechain=0 / allow-read-inactivechain=0（DT 层面关闭读）。

NEXT_ACTION =
G4D-DU2：编制"补齐 DU 打包/签名/host 工具链"取得与验证方案（DRIVE OS SDK via NGC 官方渠道；
含 DUPKG 规格、签名流程、链控通道 0x9 的只读诊断设计）——仍不接触车机、不写任何链。

PERSISTENT_WRITE = ZERO
REBOOT_COUNT = ZERO
CONFIDENCE = HIGH
（栈/入口/分区/通道事实均为一手只读实测；链状态按门规如实标 UNKNOWN）
```

## 安全边界执行说明（透明记录）

- 全程仅: 文件搜索/版本查询/--help/只读查询（query_bootchain、part_ver、du_list、du_read）/DT 与配置读取/日志读取/二进制 strings/ldd/sha256sum/stat。
- 未执行任何：安装/update/activate/commit/写链/切链/改默认链/写 QSPI/UFS/BCT/reboot/kexec/tegrareset。
- 透明记录两处进程级事件（均无持久写）：`-q` 查询挂起后经 SIGTERM（timeout）与 Ctrl+C 终止；期间 bootmgr/dumaster 内部重试日志（0x9/0x2100001）随会话出现、随终止停止。
- 门规 §11 触发点：确认"需 OEM 签名但无合法签名链"⇒ 未做任何安装尝试即停（记录于 K68 方案文档 §3）。

## 关键证据索引

| 证据 | 位置 |
|---|---|
| 七轮原始会话（含每命令 SEND/RX 逐字节） | `11_g4d_du/du_s1.log` … `du_s7.log` + `_tools/du_s*_cmds.txt` |
| 组件哈希/权限/依赖 | du_s3（5 件）+ du_s6（4 件）；矩阵文档 §1 |
| 链查询失败实证（journal 0x9 全链） | du_s5 命令 13（命令表 C3） |
| part_ver 52 条 A_pvit 清单 / B/C_pvit 可读 | du_s6 命令 6 / du_s7 命令 6-7 |
| /tii 节点树 + active_bootchain="0" + state=RESTORE_CTX + RL_DORMANT | du_s6 命令 3-5；du_s7 命令 2-4 |
| tacp.cfg（Aurix bootchain 端口 5001） | du_s7 命令 1 |
| live DT 策略实读（allow-read-*、update-info） | du_s5 命令 14；du_s6 命令 9 |
| G0 冻结 DT 佐证（chosen/driveupdate 全节点） | `00_live_baseline/G0_DEVICE_TREE/live-p3960.dts` 7094-7423 |

## 结论一句话

**GOS 内确有完整的 DRIVE Update V3 栈与 A/B/C 链管理入口（CONFIRMED），但链状态读取当前被平台级阻断（0x9）、包构建与签名工具链在车外 ⇒ G4D_DU = CONDITIONAL，READY_FOR_G4E = NO；下一步只补"打包/签名/宿主链"与"链控通道诊断设计"，绝不重做 Kernel6.8、不写任何链。**
