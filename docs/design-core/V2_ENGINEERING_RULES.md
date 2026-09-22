# 《宇宙之影》V2 工程规则

更新时间：2026-07-02

## 分层边界

`Core`

- 只写纯 C# 规则。
- 不引用 `UnityEngine`。
- 负责任务状态、节点图、移动规则、风险结算、胜负判断。

`Data`

- 只写 ScriptableObject 和运行时数据转换。
- 可以引用 `UnityEngine` 和 `Core`。
- 不写胜负判断、移动判定或技能结算规则。

`UI`

- 只显示状态、创建控件、转发玩家选择。
- 可以引用 `Core`。
- 不直接修改任务胜负和单位数值。

`Runtime`

- 负责 Unity 场景生命周期、输入、相机、灯光、单位/节点表现。
- 可以引用 `Core`、`Data`、`UI`。
- 不把业务规则写进 MonoBehaviour；规则必须调用 `Core` resolver。

`Editor`

- 负责样例资产、样例场景、批量生成和验证入口。
- 生成物必须可重复创建。

## 依赖方向

依赖只能按以下方向流动：

`Core <- Data <- Runtime <- Editor`

`Core <- UI <- Runtime`

禁止 `Core` 依赖 `Data`、`Runtime` 或 `UI`。

## 数据规则

- 静态配置进入 SO。
- 运行时状态进入普通 C# class。
- UI 不能直接持有 SO 并修改配置。
- 样例数据必须能通过 `Shadow/V2/Create Sample MVP Assets And Scene` 重建。

## 验收规则

- 新增脚本必须放进对应 asmdef。
- 新增 Unity 资产必须提交 `.meta`。
- `Core` 层必须能独立编译。
- 关键规则必须补 EditMode 测试。
- 旧 `UnityProject/` 默认不改动。
