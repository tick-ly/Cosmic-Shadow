# 宇宙之影：基于人设驱动的敌军 AI 行为模式方案

## 一、 核心理念：人设即权重 (Persona as Weights)

我们采用**“效用 AI (Utility AI)”**的架构来驱动敌军指挥官。
*   **机制：** AI 在做决策时，会给所有可能的行动（如：进攻、防守、呼叫增援、撤退）打分。分数最高的行动将被执行。
*   **人设驱动：** 所谓的“人设”，本质上就是一组**权重参数（Weights）**。我们利用大语言模型（LLM）在开发阶段，根据一段文字描述，自动生成这套权重参数，从而形成独特的决策树。

## 二、 双层 AI 架构 (Macro & Micro AI)

为了适应 5 分钟快节奏任务，AI 分为两层：

1. **宏观指挥官 AI (Macro Commander AI)：**
   *   **职责：** 负责全局调度。决定把兵力派往哪个节点、何时呼叫增援、是否启动全图警戒。
   *   **人设体现：** 不同的指挥官有不同的战略偏好（如：铁血督军、多疑战术家、狂热信徒）。
2. **微观小队 AI (Micro Squad AI)：**
   *   **职责：** 负责节点内的具体战术动作。
   *   **状态机：** 遵循经典的 `巡逻 (Patrol) -> 警觉 (Alert) -> 追击/交战 (Combat) -> 丢失目标 (Search)` 逻辑。

## 三、 动态压力升级 (Dynamic Escalation)

为了配合 5 分钟的单局时长，指挥官 AI 拥有一个**“焦虑值 (Anxiety Level)”**。
*   随着时间推移，或者玩家破坏了关键设施，指挥官的焦虑值会上升。
*   焦虑值会动态改变决策权重。例如，一个原本“谨慎”的指挥官，在焦虑值达到 100% 时，也会不顾一切地发起“全军冲锋”，从而在关卡的最后 1 分钟将游戏推向高潮。

## 四、 数据结构建议 (ScriptableObject)

团队可以使用以下数据结构来配置不同的人设：

```csharp
using UnityEngine;

namespace ShadowOfTheUniverse.AI
{
    [CreateAssetMenu(fileName = "NewCommanderPersona", menuName = "Shadow/AI/Commander Persona")]
    public class CommanderPersonaSO : ScriptableObject
    {
        public string commanderName;
        [TextArea] public string personaDescription;

        [Header("战略偏好权重 (0.0 - 1.0)")]
        [Range(0f, 1f)] public float weightAggression;    // 进攻倾向
        [Range(0f, 1f)] public float weightDefense;       // 防守倾向
        [Range(0f, 1f)] public float weightRecon;         // 侦察倾向
        [Range(0f, 1f)] public float weightSelfDestruct;  // 焦土/同归于尽倾向

        [Header("动态压力响应")]
        public float anxietyIncreaseRate; // 随时间增加的焦虑值速率
        public AnimationCurve aggressionOverAnxiety; // 焦虑值如何影响进攻倾向的曲线
    }
}
```

## 五、 AI 辅助生成管线 (LLM Prompt Template)

为了快速生成上述数据，团队成员可以使用以下 Prompt 模板向 ChatGPT（或 Claude 等大模型）提问，直接获取配置数据。

**【复制以下内容发送给大语言模型】**

> 你现在是《宇宙之影》这款大战略战术游戏的 AI 设计师。游戏中的敌军指挥官使用“效用 AI (Utility AI)”进行决策。
> 
> 请根据我提供的【指挥官背景描述】，为该指挥官生成一组效用 AI 的权重参数。
> 
> **参数定义（取值范围 0.00 到 1.00）：**
> *   `weightAggression`: 进攻倾向（越高越喜欢主动出击和包围）。
> *   `weightDefense`: 防守倾向（越高越喜欢收缩防线、保护核心节点）。
> *   `weightRecon`: 侦察倾向（越高越喜欢派出小股部队开视野、巡逻）。
> *   `weightSelfDestruct`: 焦土倾向（越高越倾向于使用污染武器，甚至牺牲友军来阻挡玩家）。
> *   `anxietyIncreaseRate`: 焦虑值随时间增加的速率（0.01 到 0.10，越高代表越容易失去冷静）。
> 
> **【指挥官背景描述】：**
> （在这里输入你的描述，例如：“他是一个极度偏执的老将，曾经在一次伏击中失去了半个军团，从此不再信任任何情报，只相信绝对的防御和火力覆盖。”）
> 
> **请严格以 JSON 格式输出结果，不要包含任何其他解释性文字：**
> ```json
> {
>   "commanderName": "生成一个符合设定的名字",
>   "weightAggression": 0.0,
>   "weightDefense": 0.0,
>   "weightRecon": 0.0,
>   "weightSelfDestruct": 0.0,
>   "anxietyIncreaseRate": 0.0
> }
> ```
