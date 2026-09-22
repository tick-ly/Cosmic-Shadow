# 《宇宙之影》V2

这是一次干净重做的 Unity 工程。旧 `UnityProject/` 保留为参考，不作为 V2 的直接代码来源。

## 首次使用

新增样板关 **灰港断讯**：打开 `Assets/_ProjectV2/Generated/Levels/Grayport/Grayport_Blackout.unity`。详见[关卡交付与验证说明](../docs/grayport/README.md)。资产和规则检查已通过，Unity 原生导入与实玩验收仍待许可证激活；以下为旧 MVP 操作入口。

1. 用 Unity `6000.4.0f1` 打开 `UnityProjectV2/`。
2. 等待 Unity 导入完成。
3. 打开场景：`Assets/_ProjectV2/Scenes/V2_MVP.unity`。
4. 进入 Play Mode。

如果样例资产或场景需要重建，运行菜单：`Shadow/V2/Create Sample MVP Assets And Scene`。

## MVP 操作

- 点击单位选择当前行动单位。
- 点击相邻节点移动。
- 到达敌对节点或目标节点后，右侧会打开风险评估面板。
- 点击技能按钮执行判定。
- 完成目标进度后移动到撤离点完成任务。

## 架构约束

- `Scripts/Core` 是纯 C# 规则层，不依赖 UnityEngine。
- `Scripts/Data` 只负责 ScriptableObject 到运行时数据的转换。
- `Scripts/Runtime` 只负责 Unity 场景表现、输入与生命周期。
- `Scripts/UI` 只显示状态并转发玩家选择，不写任务胜负规则。

## 当前首版范围

- 已实现节点地图、路线、单位移动、风险技能、任务目标进度、撤离胜利、失败阈值和 EditMode 规则测试。
- 尚未实现正式美术、存档、复杂 AI、战地式大地图和大战略长线系统。

## 测试

- EditMode 测试位于 `Assets/_ProjectV2/Tests/EditMode`。
- `Scripts/Core` 保持纯 C#，可以脱离 Unity 做编译检查。
- Unity 菜单生成器也支持 batchmode：`-executeMethod ShadowOfTheUniverse.V2.Editor.V2SampleProjectBuilder.CreateSampleMvpBatch`。
