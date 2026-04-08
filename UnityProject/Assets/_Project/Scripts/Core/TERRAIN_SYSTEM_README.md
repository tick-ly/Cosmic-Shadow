# 地形战斗系统 - 扩展文档

## 概述

基于"海陆空沙盘移动与探索机制方案"，扩展了Unity战斗系统，新增地形系统、单位分类、移动规则和战争迷雾机制。

---

## 核心系统

### 1. 地形系统 (TerrainSystem)

#### 地形类型

| 地形 | 描述 | 防御加成 | 适合单位 |
|------|------|----------|----------|
| **Land** (陆地) | 内陆区域 | +10% | 陆军 |
| **Sea** (水域) | 海洋区域 | 0% | 海军 |
| **Coastal** (沿海) | 陆海交界 | +15% | 陆军/海军 |

#### 路线类型

| 路线 | 描述 | 可用单位 |
|------|------|----------|
| **LandRoute** (陆路) | 公路/铁路 | 陆军 |
| **SeaRoute** (航道) | 航道 | 海军 |
| **AirRoute** (空路) | 空中航线 | 空军 |

**实现文件**: `TerrainEnums.cs`, `MapNode.cs`

---

### 2. 单位分类系统

#### 单位领域 (UnitDomain)

| 领域 | 移动范围 | 作战半径 | 视野 | 移动规则 |
|------|----------|----------|------|----------|
| **Land** (陆军) | 2格 | - | 2格 | 陆路、沿海 |
| **Sea** (海军) | 3格 | - | 3格 | 海路、沿海 |
| **Air** (空军) | - | 4格 | 4格 | 作战半径内任意地形 |

#### 单位编制 (UnitScale)

| 编制 | 特性 | 地形限制 | 超能力 |
|------|------|----------|--------|
| **Squad** (队伍) | 受地形严格限制 | ✓ 严格 | ✗ 无 |
| **Individual** (单兵) | 可跨越地形 | ✗ 宽松 | ✓ 有 |

**实现文件**: `CombatUnit.cs`

---

### 3. 移动规则系统

#### 常规移动

```
陆军队伍:
  ✓ 陆地 → 陆地 (通过陆路)
  ✓ 陆地 → 沿海 (通过陆路)
  ✗ 陆地 → 水域 (禁止)

海军队伍:
  ✓ 水域 → 水域 (通过航道)
  ✓ 水域 → 沿海 (通过航道)
  ✗ 水域 → 陆地 (禁止)

空军队伍:
  ✓ 任意地形 (作战半径内)
```

#### 单兵单位特权

单兵单位（超能力者）可以无视地形限制：

```csharp
// 陆战单兵跨越海洋
MovementValidation validation = unit.CanMoveTo(currentNode, seaNode, routeType);

if (validation.RequiresAbilityUse)
{
    // 使用超能力跨越地形
    unit.AddRealityDebt(validation.AbilityDebtCost); // +30点现实债务
    unit.ExecuteMovement(seaNode, usedAbilityToCross: true);
}
```

**实现文件**: `MovementManager.cs`

---

### 4. 战争迷雾系统

#### 节点可见性

| 状态 | 描述 | 显示 |
|------|------|------|
| **Hidden** (未探索) | 完全不可见 | 问号(?) |
| **Fogged** (迷雾) | 已探索但无视野 | 地形信息，无动态 |
| **Visible** (可见) | 当前有视野 | 完整信息 |

#### 视野计算

```csharp
// 单位视野范围
陆军: 2格
海军: 3格
空军: 4格

// 视野更新
当单位移动时，自动更新周围节点的可见性
单位所在的节点和相邻节点变为Visible
离开的节点变为Fogged
```

**实现文件**: `MapNode.cs`, `MapManager.cs`

---

### 5. 地形战斗系统

#### 地形成功率修正

```
最终成功率 = 基础成功率
           + 攻击者地形加成 (x20转换为百分比)
           - 防守者地形加成 (x15转换为百分比)
           - 节点防御加成 (x10转换为百分比)
```

#### 地形伤害修正

```
最终伤害 = 基础伤害 × 地形加成

陆军在陆地: 1.15x
海军在海洋: 1.20x
空军在任何地形: 1.10x
```

**实现文件**: `TerrainCombatResolver.cs`

---

## 使用示例

### 1. 创建地图

```csharp
MapManager mapManager = MapManager.Instance;
mapManager.SetMapSize(10, 10);
mapManager.SetSeed(12345);
mapManager.SetTerrainRatios(
    land: 0.5f,     // 50%陆地
    sea: 0.3f,      // 30%海洋
    coastal: 0.2f   // 20%沿海
);
mapManager.GenerateMap();
```

### 2. 创建单位

```csharp
// 陆军队伍
CombatUnit landSquad = new CombatUnit(
    "陆军作战队",
    BloodlineTier.Low,
    null,
    UnitDomain.Land,
    UnitScale.Squad,
    100
);

// 英雄单位（单兵超能力者）
CombatUnit hero = new CombatUnit(
    "零号实验体",
    BloodlineTier.Low,
    null,
    UnitDomain.Land,
    UnitScale.Individual,  // 单兵编制
    100
);
```

### 3. 单位移动

```csharp
// 移动单位
MovementResult result = MovementManager.Instance.MoveUnit(unit, targetNode);

if (result.Success)
{
    Debug.Log($"成功移动到 {targetNode.NodeName}");

    if (result.AbilityUsed)
    {
        Debug.Log($"使用超能力跨越地形，债务+{result.AbilityDebtCost}");
    }

    if (result.ExplorationTriggered)
    {
        Debug.Log($"发现新区域: {targetNode.NodeName}");
    }
}
else
{
    Debug.Log($"移动失败: {result.ErrorMessage}");
}
```

### 4. 地形战斗

```csharp
// 在特定节点进行战斗
CombatResult result = TerrainCombatResolver.ResolveTerrainCombat(
    attacker,
    defender,
    skill,
    battleNode
);

Debug.Log($"战斗发生: {battleNode.NodeName} ({battleNode.Terrain})");
Debug.Log($"地形修正: {result.TerrainBonus}%");
Debug.Log($"结果: {(result.Success ? "成功" : "失败")}");
```

### 5. 占领节点

```csharp
NodeCaptureResult result = TerrainCombatResolver.CaptureNode(attacker, targetNode);

if (result.Success)
{
    Debug.Log($"成功占领 {targetNode.NodeName}");
    Debug.Log($"控制权: {result.PreviousOwner} → {result.NewOwner}");
}
```

---

## 核心机制集成

### 物理妥协 × 地形跨越

单兵单位跨越不兼容地形时，使用"物理妥协"机制：

```
陆战单兵跨越海洋:
  1. 触发"冰封海面"或"空间折跃"
  2. 增加现实债务 +30
  3. 成功移动到海洋节点

代价系统:
  - 债务过高(>800)时无法使用
  - 失败时债务增加1.5倍
  - 需要权衡风险与收益
```

### 战争迷雾 × 探索机制

```
探索流程:
  1. 单位移动到Hidden节点
  2. 节点变为Visible
  3. 解锁节点信息（地形、资源、驻军）
  4. 相邻节点变为Fogged（显示轮廓）
  5. 单位离开后节点变为Fogged
```

---

## 文件列表

### 核心逻辑层 (Core/)

- `TerrainEnums.cs` - 地形、路线、可见性枚举
- `MapNode.cs` - 地图节点数据模型
- `CombatUnit.cs` - 战斗单位（扩展）
- `TerrainCombatResolver.cs` - 地形战斗结算器

### 系统管理层 (Systems/)

- `MapManager.cs` - 地图管理器
- `MovementManager.cs` - 移动管理器
- `TerrainCombatDemo.cs` - 演示脚本

### 数据配置层 (Data/)

- `CombatUnitDataSO.cs` - 单位数据模板

---

## 与Python原型的对应关系

| Python原型 | Unity扩展 | 说明 |
|-----------|----------|------|
| 基础节点 | MapNode + TerrainType | 增加地形属性 |
| 基础单位 | CombatUnit + Domain/Scale | 增加海陆空分类 |
| 基础移动 | MovementManager + 地形规则 | 增加地形限制 |
| 无视野系统 | FogOfWar系统 | 新增战争迷雾 |
| 无地形加成 | TerrainCombatResolver | 新增地形战斗加成 |

---

## 设计亮点

### ✅ 策略性增强

- 地形限制迫使玩家考虑单位搭配
- 战争迷雾增加探索乐趣
- 地形加成影响战斗策略

### ✅ 与核心机制完美融合

- 单兵跨越地形使用"现实债务"机制
- 地形战斗加成与技能系统结合
- 视野系统与移动系统联动

### ✅ 数据驱动

- 所有单位可通过ScriptableObject配置
- 地形比例可调
- 平衡性易于调整

---

## 后续扩展方向

### 阶段二扩展

- [ ] 特殊地形（山地、森林、城市）
- [ ] 天气系统影响移动
- [ ] 补给线系统
- [ ] 多层地图（地下、水下）

### UI系统

- [ ] 地形可视化（不同颜色/图标）
- [ ] 移动路径预览
- [ ] 战争迷雾视觉效果
- [ ] 地形信息面板

---

**状态**: ✅ 扩展完成
**日期**: 2026年3月25日
**新增文件**: 7个核心文件
**代码行数**: ~1500行
