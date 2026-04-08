# 《宇宙之影》开发任务清单：从底层框架到可玩 Demo

基于当前 Unity 项目的差距评估，为了将现有的底层逻辑转变为一个能正常运行且可玩的白盒 Demo，特制定以下分级任务列表。团队成员可以按照此清单的优先级逐步推进。

---

## 🟥 第一阶段：消除阻碍，让项目“跑起来” (P0 - 紧急且重要)
*目标：解决所有的报错、空引用，确保点击 Unity 的 Play 按钮后不会报错崩溃。*

### 1. 场景与资产初始化
> ⚠️ 以下为 **Unity Editor 手动操作**，代码层面已就绪（见各脚本）。

- [x] **代码层已就绪（待编辑器实例化）：**
  - [x] `ScriptableObject` 脚本已完整：`SkillDataSO`、`CharacterClassSO`、`CombatUnitDataSO`
  - [x] `PlayerCommander` 脚本已存在
  - [x] `MapManager` 已整合到 `Scripts/Systems/`
  - [x] `AnomalyFortress` 空间折叠系统已完成（含 `SpatialFoldRegistry`）
- [ ] **Unity Editor 操作（需手动完成）：**
  - [ ] 创建初始场景：在 `Assets/Scenes/` 下新建 `MainMapScene.unity`
  - [ ] 配置 ScriptableObject 数据：右键 Create → 基于已有 SO 脚本创建 `.asset` 文件并填入测试数据
  - [ ] 制作 Prefab：创建 `FleetPrefab`（Cube/Sphere）和 `NodePrefab`
  - [ ] 绑定引用：将 SO 资产和 Prefab 拖拽赋值到各脚本的 SerializeField 上

### 2. 修复代码冲突与编译错误
- [x] **解决 MapManager 冲突：** 删除旧版的 `Scripts/Strategy/MapManager.cs`，保留并重构 `Scripts/Systems/MapManager.cs`。
- [x] **修复私有字段访问：** 修改 `MapManager`，提供 `IReadOnlyDictionary<string, MapNode> AllNodes` 属性供外部调用。

---

## 🟧 第二阶段：核心系统整合与可视化 (P1 - 核心体验)
*目标：让底层的 85% 战斗逻辑和 70% 地图逻辑真正在画面上表现出来。*

### 1. 地图与寻路系统补全
- [ ] **接入 A* 寻路：** 修改 `MovementManager.FindPath()` 方法，废弃基础 BFS，全面调用写好的 `AStarPathfinder.cs` 进行路径计算。
- [x] **沙盘可视化：** 
  - [x] 在 `MapManager` 中编写代码，游戏启动时根据数据自动实例化 `NodePrefab`。
  - [x] 使用 `LineRenderer` 组件将相连的节点连线，形成可视化地图网络。
- [ ] **单位移动表现：** 让 `FleetPrefab` 能够沿着 A* 计算出的路径，在节点之间平滑移动（使用协程或 DOTween）。

### 2. 基础 UI 框架搭建 (替代 OnGUI)
> ⚠️ **Canvas 层级创建需在编辑器中手动完成**，代码逻辑已全部实现。

- [x] **代码层已完整实现：**
  - [x] `GameUIManager.cs` — 中央 UI 管理器，集成 HUD + 信息面板 + 战斗日志
  - [x] `PlayerCommander.cs` — 集成 UI 调用（选择单位/节点时自动弹出面板）
  - [x] `CombatUnitModel.cs` — 移动时通过 EventManager 推送日志
  - [x] `GameState.cs` — 资源变化时自动推送 `CREDITS_CHANGED` / `SUPPRESSION_CHANGED` 事件
  - [x] `EventManager.cs` — 新增 `CREDITS_CHANGED` / `SUPPRESSION_CHANGED` / `UNIT_MOVED` 事件常量
  - [x] 射线检测：已由 `PlayerCommander.HandleClick()` 实现
- [ ] **Unity Editor 操作（需手动完成）：**
  - [ ] 在场景中创建 UGUI Canvas + EventSystem
  - [ ] 创建 HUD 面板（顶部）：3个 TextMeshProUGUI（信用点、妥协值、回合）+ 1个 Image（妥协条）
  - [ ] 创建节点/单位信息面板（右侧）：Panel + Title/Body Text + 绑定到 GameUIManager
  - [ ] 创建战斗报告面板（右下角）：ScrollRect + Text + 绑定到 GameUIManager
  - [ ] 在场景中放置 `GameUIManager` 对象并拖拽绑定各面板引用

---

## 🟨 第三阶段：游戏循环闭环 (P2 - 完整性)
*目标：加入缺失的 0% 模块，让游戏具备完整的“开始-游玩-保存-退出”流程。*

### 1. 流程控制与主菜单
- [ ] **制作 MainMenu 场景：** 包含“开始游戏”、“加载游戏”、“设置”、“退出”按钮。
- [ ] **场景切换逻辑：** 实现从主菜单加载 `MainMapScene` 的过渡。

### 2. 存档与读档系统 (Save/Load)
- [ ] **GameState 序列化：** 将当前的 `GameState`、各节点的现实债务浓度、各单位的位置与血量状态提取为可序列化数据类。
- [ ] **本地存储：** 实现基于 JSON (如 `JsonUtility` 或 `Newtonsoft.Json`) 的本地文件读写逻辑。

---

## 🟩 第四阶段：视觉与听觉包装 (P3 - 润色)
*目标：告别白盒，应用“对立美学”，提升游戏质感。*

### 1. 视觉表现 (Visuals)
- [ ] **Shader 与材质：** 替换掉默认的白模材质。为安全节点赋予蓝色发光材质，为死区赋予扭曲/黑色材质。
- [ ] **引入 Post-Processing (后期处理)：** 
  - [ ] 配置 Global Volume，添加 Bloom、Color Grading。
  - [ ] 编写脚本：根据全局或局部“现实债务”数值，动态增加 Chromatic Aberration（色差）和 Lens Distortion（镜头畸变），实现“故障艺术”效果。

### 2. 音效反馈 (Audio)
- [ ] **音频管理器 (AudioManager)：** 搭建基础的音效播放系统。
- [ ] **核心音效实装：** 
  - [ ] UI 交互音效（点击、警报）。
  - [ ] 战斗结算音效（开火、受击）。
  - [ ] 物理妥协技能释放时的“空间扭曲/重低音”特效声。
  - [ ] 两套背景音乐（常规沙盘 BGM vs 高债务状态下变调压抑的 BGM）。
