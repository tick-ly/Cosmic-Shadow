# 宇宙之影 - Unity项目快速入门

## 快速开始

### 1. 在Unity中打开项目

将此文件夹作为Unity项目打开，或将其内容复制到现有Unity项目的Assets文件夹。

### 2. 创建场景

1. 创建新场景：`File -> New Scene`
2. 添加空GameObject，命名为"GameManager"
3. 添加`GameManager`脚本
4. 添加空GameObject，命名为"GameDemo"
5. 添加`GameDemo`脚本

### 3. 运行演示

点击Play按钮，你将看到：
- 控制台日志显示角色创建过程
- 战斗系统自动运行演示
- 屏幕下方出现控制面板

### 4. 使用控制面板

在Game View中，你可以：
- **重新初始化演示**: 重置角色和战斗
- **使用技能**: 演示技能系统
- **基础攻击**: 进行无风险攻击
- **敌人回合**: 敌人发起攻击
- **休息**: 恢复疲劳和债务

## 创建自定义内容

### 创建技能数据

1. 右键Project窗口：`Create -> Shadow of the Universe -> Skill Data`
2. 填写技能信息：
   - **技能ID**: 唯一标识符
   - **技能名称**: 显示名称
   - **血统等级**: Low/Medium/High
   - **基础成功率**: 10-95
   - **伤害数值**: 成功和失败时的伤害
   - **现实债务**: 使用代价
   - **冷却时间**: 回合数

### 创建角色类别

1. 右键Project窗口：`Create -> Shadow of the Universe -> Character Class`
2. 配置血统属性：
   - **基础属性**: 生命、速度、护甲
   - **血统特性**: 债务倍率、抗疲劳
   - **技能容量**: 各级技能槽数量

### 在代码中使用

```csharp
using ShadowOfTheUniverse.Core;
using ShadowOfTheUniverse.Data;

// 加载ScriptableObject
SkillDataSO skillData = Resources.Load<SkillDataSO>("Skills/MySkill");
CharacterClassSO classData = Resources.Load<CharacterClassSO>("Classes/MyClass");

// 创建角色
Character hero = new Character("英雄名", BloodlineTier.Low, classData);

// 创建并添加技能
SkillBase skill = skillData.CreateSkillInstance();
hero.AddSkill(skill);

// 使用技能
CombatResult result = CombatResolver.ResolveSkillUse(hero, skill, enemy);
```

## 核心概念

### 现实债务系统

每次使用超能力都会增加"现实债务"：
- 债务越高，成功率越低
- 债务达到1000时触发危机
- 休息可以减少债务

### 风险管理

技能使用有风险，需要权衡：
- **高成功率**: 安全但效果较小
- **低成功率**: 危险但效果强大
- **连续使用**: 成功率递减
- **疲劳状态**: 额外成功率惩罚

### 战斗策略

1. 监控现实债务和疲劳度
2. 合理选择技能等级
3. 适时休息恢复
4. 风险过高时使用基础攻击

## 事件系统

订阅游戏事件：

```csharp
// 订阅事件
EventManager.Instance.Subscribe(GameEvents.SKILL_SUCCESS, OnSkillSuccess);
EventManager.Instance.Subscribe(GameEvents.DEBT_WARNING, OnDebtWarning);

// 事件处理函数
private void OnSkillSuccess(object data)
{
    BattleEventData eventData = data as BattleEventData;
    Debug.Log($"技能成功: {eventData.SkillUsed.Name}");
}

// 取消订阅
EventManager.Instance.Unsubscribe(GameEvents.SKILL_SUCCESS, OnSkillSuccess);
```

### 可用事件

- `GameEvents.GAME_START` - 游戏开始
- `GameEvents.BATTLE_START` - 战斗开始
- `GameEvents.SKILL_USE` - 技能使用
- `GameEvents.SKILL_SUCCESS` - 技能成功
- `GameEvents.SKILL_FAILURE` - 技能失败
- `GameEvents.DEBT_WARNING` - 债务警告
- `GameEvents.DEBT_CRITICAL` - 债务危机

## 调试技巧

### 查看战斗日志

在`BattleManager`中启用`showCombatLog`：
```csharp
[SerializeField] private bool showCombatLog = true;
```

### 使用GameManager调试面板

运行时在Game View左上角会显示调试信息：
- 游戏状态
- 当前回合
- 暂停/恢复按钮

### 查看实时战斗状态

运行时在Game View右上角显示：
- 角色生命值
- 现实债务
- 疲劳度

## 常见问题

**Q: 技能总是失败？**
A: 检查角色的现实债务和疲劳度，这些因素会降低成功率。

**Q: 如何修改成功率的计算方式？**
A: 修改`SkillBase.GetModifiedSuccessRate()`方法。

**Q: 如何添加新的血统等级？**
A: 在`CoreEnums.cs`中添加新的`BloodlineTier`枚举值。

**Q: 如何自定义战斗UI？**
A: 订阅`GameEvents`中的战斗事件，根据事件数据更新UI。

## 下一步

- 阅读完整文档：`Scripts/Core/README.md`
- 查看迁移进度：`MIGRATION_REPORT.md`
- 研究原始Python代码：`../demo/game_project/`

## 技术支持

如有问题，请查看：
1. 代码注释
2. README文档
3. 迁移计划文档
