# 《宇宙之影》V2 基础策划案索引

更新时间：2026-07-02

## 保留的设计内核

V2 重做保留以下基础策划方向，旧 Unity 工程代码只作为参考，不作为新架构的继承来源。

1. 物理妥协能力
   - 来源：`demo/超能力技能系统-物理妥协版.md`
   - V2 用法：所有高影响行动都通过成功率、现实债务、反噬与冷却构成风险决策。
2. 现实债务
   - 来源：`demo/动态事件系统与局部现实债务方案.md`、`demo/作战系统设计-风险管理战斗.md`
   - V2 用法：债务影响技能成功率、失败后果、任务失败压力和 UI 警告。
3. 风险管理战斗
   - 来源：`demo/作战系统设计-风险管理战斗.md`
   - V2 用法：战斗不是堆资源，而是“是否承担风险、承担多大风险、失败能否接受”的连续判断。
4. 海陆空节点移动
   - 来源：`demo/海陆空沙盘移动与探索机制方案.md`
   - V2 用法：节点、路线、单位领域与通行限制进入核心规则层。
5. 5 分钟战术任务
   - 来源：`demo/5分钟快节奏战术任务方案.md`
   - V2 用法：首个 MVP 只验证短任务闭环：进入任务、移动、技能判定、目标推进、撤离或失败。

## V2 首版范围

- 不迁移旧 `UnityProject/` 的场景、UI 绑定和临时代码。
- 不在首版做完整大战略、联网、大规模战地地图或复杂 AI。
- 先实现可配置的单任务闭环，再决定哪些旧算法或地形资产迁入。

## 交付物定义

- `UnityProjectV2/`：新的 Unity 工程。
- `UnityProjectV2/Assets/_ProjectV2/Scripts/Core/`：纯 C# 规则层。
- `UnityProjectV2/Assets/_ProjectV2/Scripts/Data/`：ScriptableObject 数据层。
- `UnityProjectV2/Assets/_ProjectV2/Scripts/Runtime/`：Unity 运行时桥接。
- `UnityProjectV2/Assets/_ProjectV2/Scripts/UI/`：最小 HUD 与风险评估面板。
- Unity 菜单：`Shadow/V2/Create Sample MVP Assets And Scene`，用于生成首版样例资产和测试场景。
