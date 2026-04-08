# 宇宙之影：核心循环执行 Backlog

## 说明

本 Backlog 基于 [CORE_LOOP_ONE_PAGER.md](D:/program/univers/UnityProject/Assets/_Project/Scripts/Core/CORE_LOOP_ONE_PAGER.md) 拆解，目标是把当前项目从“已有地图、战斗、资源原型”推进到“可持续迭代的战略主循环”。

原则：

- 先闭环，再扩内容
- 先资源回写，再扩战斗复杂度
- 先目标系统，再扩地图密度和异常种类

状态约定：

- `P0` 必做，阻塞主循环
- `P1` 高优先级，显著提升可玩性
- `P2` 中优先级，支撑扩展和内容生产

---

## 里程碑 0：稳定当前基础层

目标：

- 把当前可运行原型整理成可继续迭代的底盘

### M0-1 修复 MapManager 双层地图重构残余

- 优先级：`P0`
- 现状：
  当前 [MapManager.cs](D:/program/univers/UnityProject/Assets/_Project/Scripts/Systems/MapManager.cs) 已经进入双层地图改造中，但还没有闭合到可稳定编译、可稳定使用的状态。
- 任务：
  - 完成 `TerrainCell` 与 `MapNode` 的正式绑定
  - 清理 `MapManager` 中旧单层坐标逻辑
  - 确保 `GenerateNodes` / `GenerateConnections` / `GetNodeAtPosition` 语义一致
  - 确保 `GameUIManager`、`PlayerCommander`、`AnomalyFortress` 不再依赖拼接 `node_x_y`
- 验收标准：
  - 项目可编译
  - 打开地图场景可生成地图
  - 点击地图、据点生成、异常刷新不会因坐标层错位而失败

### M0-2 统一战略坐标与世界坐标

- 优先级：`P0`
- 依赖：`M0-1`
- 任务：
  - 明确 `MapNode.CoordinateX/Y` 只代表策略网格坐标
  - 明确 `MapNode.WorldX/Y` 只代表世界显示坐标
  - 统一所有距离计算基于策略坐标
  - 统一所有渲染/摆放基于世界坐标
- 验收标准：
  - 路径、视野、移动成本不受视觉缩放影响
  - 调整 `terrainCellsPerNode` 后，移动和距离规则不变

### M0-3 建立最小开发场景

- 优先级：`P1`
- 任务：
  - 固定一个用于主循环验证的测试场景
  - 场景中只保留地图、回合、目标、基础战斗入口
  - 移除或隔离演示脚本对主循环验证的干扰
- 现有入口参考：
  - [SceneInitializer.cs](D:/program/univers/UnityProject/Assets/_Project/Scripts/Systems/SceneInitializer.cs)
  - [GameDemo.cs](D:/program/univers/UnityProject/Assets/_Project/Scripts/Systems/GameDemo.cs)
  - [TerrainCombatDemo.cs](D:/program/univers/UnityProject/Assets/_Project/Scripts/Systems/TerrainCombatDemo.cs)
- 验收标准：
  - 团队只需要一个场景就能验证主循环
  - 演示逻辑与正式主循环逻辑分离

---

## 里程碑 1：区域目标系统

目标：

- 让地图上的行动具备明确的战略意义

### M1-1 定义区域目标数据模型

- 优先级：`P0`
- 任务：
  - 新增 `RegionObjective` 或等价数据结构
  - 定义目标类型：
    - `Primary`
    - `Stabilization`
    - `Anomaly`
    - `Supply`
  - 为目标定义：
    - 占领收益
    - 压制影响
    - 债务风险
    - 是否区域推进必需
- 推荐落点：
  - `Core/` 放纯数据结构
  - `Data/` 放 ScriptableObject 配置
- 验收标准：
  - 一个节点可以拥有明确目标类型
  - 目标收益不再写死在 Manager 逻辑里

### M1-2 为 MapNode 绑定目标元数据

- 优先级：`P0`
- 依赖：`M1-1`
- 任务：
  - 在 `MapNode` 或独立绑定层中记录目标引用
  - 提供查询接口：
    - 获取节点目标
    - 判断是否主目标
    - 判断是否稳定目标
- 验收标准：
  - UI 可以直接读取节点目标类型
  - 战斗结算可以根据目标类型回写不同资源

### M1-3 在地图生成时分配区域目标

- 优先级：`P0`
- 依赖：`M1-2`
- 任务：
  - 每张图至少生成：
    - 1 个主目标
    - 2 到 3 个稳定目标
    - 1 到 2 个异常目标
    - 若干普通节点
  - 目标位置应有简单约束：
    - 主目标不要贴边
    - 稳定目标分散布局
    - 异常目标可偏远或危险地形
- 验收标准：
  - 每次生成地图都能形成可识别的战略取舍
  - 目标分布不是纯随机噪声

### M1-4 区域推进判定

- 优先级：`P0`
- 依赖：`M1-3`
- 任务：
  - 新增区域完成条件
  - 默认规则：
    - 占领主目标
    - Suppression 未失控
  - 失败规则：
    - Suppression 达到上限
    - 核心单位不可恢复
    - 关键异常彻底失控
- 验收标准：
  - 玩家知道本局什么时候算赢、什么时候算输
  - 战略层不再只是无限漫游

---

## 里程碑 2：战略资源结算

目标：

- 把行动结果正式回写到 `Credits / Suppression / Reality Debt`

### M2-1 建立统一战略回合结算器

- 优先级：`P0`
- 任务：
  - 新增 `StrategyTurnResolver` 或等价系统
  - 每回合统一处理：
    - 基础压制增长
    - 控制点收益
    - 区域目标奖励
    - 债务外溢
    - 异常扩散
- 现有状态入口参考：
  - [GameState.cs](D:/program/univers/UnityProject/Assets/_Project/Scripts/Core/GameState.cs)
- 验收标准：
  - 同一回合内资源变化只通过一个系统集中结算
  - 不再由多个 Manager 分散改 `GameState`

### M2-2 明确三资源职责边界

- 优先级：`P0`
- 依赖：`M2-1`
- 任务：
  - `Credits`：
    - 部署
    - 补给
    - 扫描
    - 稳定行动
  - `Suppression`：
    - 全局倒计时
    - 失守惩罚
    - 区域拖延惩罚
  - `RealityDebt`：
    - 单位级爆发代价
    - 中高债务后外溢到战略层
- 验收标准：
  - 每个资源至少有 3 个明确输入和 3 个明确输出
  - 不再出现“资源都能解决一切”的重叠设计

### M2-3 战斗结果回写战略层

- 优先级：`P0`
- 依赖：`M1-2`, `M2-1`
- 任务：
  - 战斗结束后统一回写：
    - 节点控制权变化
    - Credits 变化
    - Suppression 变化
    - Debt 后果
  - 目标节点战斗与普通节点战斗区别结算
- 现有入口参考：
  - [BattleManager.cs](D:/program/univers/UnityProject/Assets/_Project/Scripts/Systems/BattleManager.cs)
- 验收标准：
  - 战斗不再是独立小游戏
  - 每次战斗都能改变战略局面

### M2-4 债务外溢系统

- 优先级：`P1`
- 依赖：`M2-2`
- 任务：
  - 定义低、中、高债务阶段
  - 高债务时触发：
    - 技能失控
    - 区域事件
    - Suppression 上升
  - 允许少量高收益玩法，但必须留下长期后果
- 验收标准：
  - 玩家可以“赌”，但不能无成本连赌
  - Debt 对战略层有真实威胁

---

## 里程碑 3：双层地图正式化

目标：

- 让地图密度提升成为设计收益，而不是系统负担

### M3-1 完成 terrain cells / strategy nodes 双层查询接口

- 优先级：`P0`
- 任务：
  - 提供 terrain cell 查询
  - 提供 strategy node 查询
  - 提供世界坐标到 strategy node 的反查
  - 提供 strategy node 到所属 terrain cells 的查询
- 验收标准：
  - 地貌、事件、渲染可以查 terrain cells
  - 移动、战斗、目标可以查 strategy nodes

### M3-2 地图渲染从“按节点画格”切到“按 terrain cell 画格”

- 优先级：`P1`
- 依赖：`M3-1`
- 任务：
  - fallback 渲染按 terrain cell 绘制
  - Tilemap 入口按 terrain cell 写入
  - strategy node 只负责据点和交互层
- 验收标准：
  - 地图视觉密度提升
  - 策略节点数量不需要同步暴涨

### M3-3 事件和异常按双层结构重做

- 优先级：`P1`
- 依赖：`M3-1`
- 任务：
  - 地形异常优先作用于 terrain cells
  - 战略异常优先作用于 strategy nodes
  - 明确哪些效果是视觉层，哪些是规则层
- 现有入口参考：
  - [AnomalyFortress.cs](D:/program/univers/UnityProject/Assets/_Project/Scripts/Strategy/AnomalyFortress.cs)
- 验收标准：
  - 异常不再直接依赖单层坐标假设
  - 异常效果既可读又可结算

### M3-4 路径与视野适配双层地图

- 优先级：`P1`
- 依赖：`M3-1`
- 任务：
  - 路径仍基于 strategy nodes
  - 地貌修正来自 terrain cell 聚合结果
  - 视野表现可基于 strategy node 扩散并映射到 terrain cells
- 验收标准：
  - 双层地图不会破坏现有移动规则
  - 视觉上能体现更细地形

---

## 里程碑 4：玩家决策可读性

目标：

- 玩家能在 HUD 上理解每回合代价与收益

### M4-1 HUD 首屏增加“本回合代价预测”

- 优先级：`P1`
- 任务：
  - 显示：
    - 预计 Credits 变化
    - 预计 Suppression 变化
    - 预计 Debt 风险
  - 在执行高风险动作前给出预测
- 现有入口参考：
  - [GameUIManager.cs](D:/program/univers/UnityProject/Assets/_Project/Scripts/UI/GameUIManager.cs)
- 验收标准：
  - 玩家做决定前能看到成本
  - 高风险动作不再是黑盒

### M4-2 节点信息面板显示目标类型与结算影响

- 优先级：`P1`
- 依赖：`M1-2`
- 任务：
  - 面板新增：
    - 目标类型
    - 占领收益
    - 压制影响
    - 异常风险
- 验收标准：
  - 点开节点就知道为什么要去打它

### M4-3 战斗前预览与战后总结

- 优先级：`P2`
- 依赖：`M2-3`
- 任务：
  - 战斗前显示预期风险
  - 战斗后显示资源回写结果
- 验收标准：
  - 战斗与战略的关系对玩家是透明的

---

## 里程碑 5：内容生产管线

目标：

- 让区域、目标、异常可以靠数据迭代，而不是继续堆在代码里

### M5-1 ScriptableObject 化区域模板

- 优先级：`P1`
- 任务：
  - 新增区域模板资产
  - 配置内容包括：
    - 地图尺寸
    - 地貌比例
    - 目标配比
    - Suppression 初始压力
    - 异常池
- 验收标准：
  - 新区域不需要改代码即可生成

### M5-2 目标模板与事件模板

- 优先级：`P2`
- 任务：
  - 目标奖励、风险、占领条件数据化
  - 区域事件数据化
- 验收标准：
  - 目标和事件可以批量做内容

### M5-3 开发用调试面板

- 优先级：`P2`
- 任务：
  - 快速重开区域
  - 快速修改 Suppression
  - 快速给单位加 Debt
  - 快速标记节点完成/失守
- 验收标准：
  - 不必手改代码验证平衡

---

## 推荐执行顺序

严格建议按以下顺序推进：

1. `M0-1`
2. `M0-2`
3. `M1-1`
4. `M1-2`
5. `M1-3`
6. `M2-1`
7. `M2-2`
8. `M2-3`
9. `M3-1`
10. `M3-2`
11. `M4-1`
12. `M5-1`

原因：

- 这条链先把“为什么打、打完有什么后果、地图为什么值得细化”全部打通
- 如果跳过 `M1` 和 `M2` 直接扩地图或战斗，主循环仍然不会闭环

---

## 当前建议的第一批可执行任务

如果只做最小可玩闭环，先开这 6 项：

1. 修复 `MapManager` 双层地图重构残余
2. 新增区域目标数据结构
3. 为节点绑定目标类型
4. 地图生成时分配主目标/稳定目标/异常目标
5. 建立统一战略回合结算器
6. 战斗结果回写到 Credits / Suppression / Debt

完成这 6 项后，项目就会从“多个系统原型并存”进入“有主循环的战术游戏原型”。

