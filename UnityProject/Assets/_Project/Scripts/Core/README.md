# 宇宙之影 - Unity项目

《宇宙之影》Unity迁移项目，基于Python原型的完整重构。

## 项目架构

### 核心原则

1. **MVC架构**：数据与表现严格分离
2. **数据驱动**：使用ScriptableObject配置游戏数据
3. **事件驱动**：模块间通过EventManager解耦通信

### 目录结构

```
Assets/_Project/
├── Scripts/
│   ├── Core/           # 纯C#核心逻辑（Model层）
│   ├── Data/           # ScriptableObject数据模板
│   ├── Systems/        # 系统管理器（Controller层）
│   └── UI/            # UI脚本（View层）
├── Prefabs/           # 预制体
├── Resources/         # 资源文件
└── Scenes/           # 场景文件
```

## 核心系统

### 1. 角色系统 (Character.cs)

纯C#类，管理角色数据和状态：
- 血统等级 (BloodlineTier)
- 现实债务 (RealityDebt) - 核心代价机制
- 疲劳度 (Fatigue)
- 生命值 (Health)

### 2. 技能系统 (SkillBase.cs)

实现"物理妥协"核心机制：
- 基础成功率
- 连续使用惩罚 (-5%每次)
- 债务惩罚 (>500时-10%)
- 疲劳惩罚 (>70时-15%)
- 风险等级动态计算

### 3. 战斗系统 (CombatResolver.cs)

RNG判定和战斗结算：
- 技能使用判定
- 成功/失败效果
- 反噬机制
- 战斗日志生成

### 4. 数据配置 (ScriptableObject)

- `SkillDataSO.cs` - 技能数据模板
- `CharacterClassSO.cs` - 角色血统模板

### 5. 事件系统 (EventManager.cs)

全局事件管理，用于模块解耦：
- 游戏流程事件
- 战斗事件
- 角色事件
- UI事件

## 使用指南

### 创建技能数据

1. 在Project窗口右键：`Create -> Shadow of the Universe -> Skill Data`
2. 填写技能信息：
   - 技能名称和描述
   - 血统等级
   - 基础成功率
   - 伤害数值
   - 现实债务代价
   - 冷却时间

### 创建角色类别

1. 在Project窗口右键：`Create -> Shadow of the Universe -> Character Class`
2. 配置血统属性：
   - 基础属性（生命、速度、护甲）
   - 血统特性（债务倍率、抗疲劳）
   - 技能容量

### 代码示例

```csharp
// 创建角色
CharacterClassSO classData = // 加载ScriptableObject
Character hero = new Character("零号实验体", BloodlineTier.Low, classData);

// 创建技能
SkillDataSO skillData = // 加载ScriptableObject
SkillBase skill = skillData.CreateSkillInstance();
hero.AddSkill(skill);

// 使用技能
CombatResult result = CombatResolver.ResolveSkillUse(hero, skill, enemy);

// 检查结果
if (result.Success)
{
    Debug.Log("技能成功！");
}
else
{
    Debug.Log("技能失败，发生反噬！");
}
```

## 迁移进度

- [x] 核心枚举定义
- [x] Character数据模型
- [x] GameState全局状态
- [x] SkillBase技能系统
- [x] CombatResolver战斗系统
- [x] ScriptableObject数据模板
- [x] EventManager事件系统

- [ ] Unity Manager脚本
- [ ] 地图系统
- [ ] UI系统
- [ ] 特效系统

## 技术栈

- Unity 2022.3+
- C# 10
- ScriptableObject数据驱动
- 事件驱动架构

## 核心机制

### 物理妥协系统

每次使用超能力都是对物理法则的妥协：
- 使用能力会增加"现实债务"
- 债务过高会降低成功率
- 失败时会触发反噬
- 需要平衡风险与收益

### 风险等级

- **安全** (≥85%): 低代价，可频繁使用
- **低风险** (≥70%): 适度使用
- **中等风险** (≥50%): 需谨慎
- **高风险** (≥30%): 危险
- **极高风险** (<30%): 可能导致严重后果
