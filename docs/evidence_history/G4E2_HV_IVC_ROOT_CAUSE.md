> **Historical frozen evidence**, not current live state. Sanitized network identifiers. Source SHA256 retained in manifest/SUPPLEMENTAL_EVIDENCE.json. Do not execute commands from this report on a vehicle.

# G4E2_HV_IVC_REHANDSHAKE_AUDIT — HV/IVC Guest Re-handshake 审计门 终报

- 日期: 2026-10-07 00:1x +08；性质: **纯只读审计**（ZERO kexec / ZERO reboot / ZERO tegrareset / ZERO HV 调用）
- 交付物: `14_g4e2/G4E2_6P1_HV_BASELINE.md`、`G4E2_6P8_FAILURE_TIMELINE.md`、`G4E2_HV_STATE_DIFF.md`、`G4E2_PM_CTL_SEMANTICS.md`、`G4E2_GUEST_SHUTDOWN_HANDSHAKE.md`、`G4E2_IVMK_LIFECYCLE.md`、`G4E2_FIX_LOCATION.md`、`G4E2_NEXT_EXPERIMENT.md` + 实验载荷 `14_g4e2/build/k68b.dtb`
- 会话/证据: `14_g4e2/g4e2_a1.log`、`g4e2_b1.log`、`g4e2_c1/c2/c3.log`；复用 `13_g4c2/g4c2_exec_capture3.log`、`g4c2_g4e*.log`

```

G4C2                  = PASS

HV_DRIVER_6P8         = PASS   （tegra_hv.c 全链成功：hyp_read_gid + hyp_read_ivc_info + info page 校验 + mempools）
HVD_6P8               = FAIL   （tegra_hv_ivc.c 从未绑定——全日志 0 条建表输出、get_hvd not initialized ×9）
IVMK_6P8              = NULL   （下游清理噪音：mempool_unreserve(NULL) ×17；非独立断点——见 F 文档）
IVC_6P8               = FAIL   （66 通道表从未建立；reserve 59..80 全失败）
VBLK_6P8              = FAIL   （0 个 /dev/vblkdev*；rootfs 未挂）

FIRST_DIVERGENCE = DT 节点 `nvidia,tegra_hv_ivc` 缺位 ⇒ 6.8 新代 IVC 机器驱动
                   (tegra_hv_ivc.c) platform probe 不绑定。三重独立证据：
                   ① live OEM DT 与 k68 DTB 该 compatible 均 0 匹配；
                   ② 驱动源码 match 表/of_find 均硬查该 compatible（6.8 树 :509/:1154）；
                   ③ 6.8 全量日志 0 条建表输出（若驱动曾运行必留痕）。
                   旁证：HV 侧服务 kexec 后实测完好（上表 HV_DRIVER_6P8=PASS）。

HV_GUEST_HANDSHAKE = CONFIRMED（模型定案）
                    · 正常 reboot/shutdown：无"释放 IVC/HVD/IVMK"握手，也不需要（PSCI/VM 复位隐式清理）；
                    · 命令面唯一实体 = HV→guest 下行代理 nv_virtual_shutdown.service（/usr/bin/nv_linux_shutdown
                      轮询 /dev/tegra_hv_pm_ctl，处理 NORMAL_SHUTDOWN/REBOOT/SUSPEND/RESUME）——方向相反、与释放无关；
                    · kexec 后 HV 按请求服务（实证）⇒ 交接不需要任何 6.1 侧预告/释放动作。

PRE_KEXEC_HV_PREPARE = NOT_FOUND（无任何对应官方 API；亦无必要——见上两行）

EARLY_6P8_REATTACH   = AVAILABLE（条件达成：DTB 单节点注入即可让 IVC 机器绑定；
                       载荷候选 k68b.dtb 已冻结，字节级"仅 +1 节点"证明在案；待单次实验验证）

TRIGGER_SYS_REBOOT_SEMANTICS = PLATFORM_RESET
                   （hyp_guest_reset(SYS_REBOOT_INIT_CMD)=系统级状态迁移、重走 OEM 启动链；
                     明确非"IVC 重新初始化"；受 PCT is_privileged 限制）

FIX_LOCATION = EARLY_6P8

G4E2_NEXT_EXPERIMENT_READY = YES（设计+载荷+预注册判据齐备：`G4E2_NEXT_EXPERIMENT.md`）

PERSISTENT_WRITE = ZERO
KEXEC_COUNT      = ZERO
REBOOT_COUNT     = ZERO

CURRENT_BLOCKER = 无（审计门闭环）。执行门待授权窗口 + 车机操作者互斥检查。

NEXT_ACTION     = 执行 G4E2 单变量实验（kexec 载荷换 k68b.dtb，sha 5259c4c1……）

CONFIDENCE      = HIGH
```

## 核心结论链（一段话）

6.8 kexec 后并非"HV 没重协商"——HV 侧数据与 HVC 实测完全可用；真正的断点是 **6.1/7.0.3 代与 6.8 代的 tegra_hv 驱动分裂**：新代把 IVC 机器拆到独立驱动 `tegra_hv_ivc.c`，其绑定条件是 DT 中存在 `nvidia,tegra_hv_ivc` 节点（通道表仍由 HVC 从 HV 取），而 OEM 老 GOS DT 只有旧代 `nvidia,tegra-hv` 节点 ⇒ 绑定不触发 ⇒ HVD/IVC/vblk/rootfs 全链缺席。**修复=在 kexec 载荷 DTB 注入该节点（EARLY_6P8，单变量，RAM-only）**。

## 附：本门产出对照（方案 §五~§十二 逐项）

| 方案节 | 产出 | 落点 |
|---|---|---|
| A 基线 | 6.1 probe 序/设备/API/通道 66 条/vblk 全表/DT 结构 | G4E2_6P1_HV_BASELINE.md |
| B 时间线 | 0.75s→20.9s→122s→157s→initrd shell + 词频反证 | G4E2_6P8_FAILURE_TIMELINE.md |
| C 差分 | 10 步生命周期表 + 第一因 + 证伪表 + 代差结构图 | G4E2_HV_STATE_DIFF.md |
| D pm_ctl | 5 问逐一（trigger_sys_reboot=系统复位；无 IVC 重置面） | G4E2_PM_CTL_SEMANTICS.md |
| E 握手 | nv_virtual_shutdown 全链定位 + 方向判定 + 终判 | G4E2_GUEST_SHUTDOWN_HANDSHAKE.md |
| F IVMK | 定义为 mempool cookie；五假说裁定=E；NULL 系噪音 | G4E2_IVMK_LIFECYCLE.md |
| G 修复位 | 四选一裁定 = EARLY_6P8（含备选实现） | G4E2_FIX_LOCATION.md |
| H 实验 | 单变量/判据/执行序/安全分析/冻结件清单 | G4E2_NEXT_EXPERIMENT.md |
| 终报 | 本文件（固定字段全填） | 07_reports/G4E2_HV_IVC_REHANDSHAKE_AUDIT.md |

## Early-Stop 检查（方案 §十三）

本门全部结论均**无需**：写 PCT/BCT/HV 配置、改 A/B/C、改 fuse、替换 OEM Hypervisor、不可恢复 Guest reset、未知私有 API。**未触发任何 Early-Stop 条件。**
