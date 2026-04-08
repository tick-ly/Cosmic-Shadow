# 宇宙之影 - 战场地形系统

## 概述

基于原文《无穷重阻》的科幻设定，实现了完整的战场地形系统，为战斗提供战术深度和环境影响。

## 地形类型

### 基础地形

| 地形 | 特点 | 防御加成 | 速度惩罚 | 适用单位 |
|------|------|----------|----------|----------|
| 平原 | 开阔地形 | 0% | 0% | 装甲集群 |
| 山地 | 高地优势 | +25% | +40% | 防御阵地 |
| 丛林 | 隐蔽良好 | +15% | +35% | 渗透部队 |
| 城市 | 复杂建筑 | +20% | +50% | 巷战单位 |
| 沙漠 | 极端环境 | +5% | +25% | 沙漠部队 |
| 雪地 | 寒冷地形 | +10% | +35% | 极地部队 |
| 沼泽 | 通行困难 | +20% | +60% | 轻型单位 |
| 海岸 | 两栖作战 | -10% | +20% | 登陆部队 |

### 科幻地形

| 地形 | 特点 | 特殊能力 |
|------|------|----------|
| 太空站 | 失重环境 | 管道渗透、舱壁战斗 |
| 轨道 | 真空环境 | 轨道轰炸、热能散热 |

## 天气系统

| 天气 | 侦查 | 精度 | 速度 | 通讯 |
|------|------|------|------|------|
| 晴朗 | 0% | 0% | 0% | 0% |
| 下雨 | -20% | -10% | -10% | -15% |
| 暴风雨 | -40% | -25% | -30% | -35% |
| 大雾 | -50% | -15% | -5% | -10% |
| 夜间 | -30% | -20% | 0% | -5% |
| 沙尘暴 | -60% | -30% | -40% | -40% |
| 暴风雪 | -50% | -25% | -35% | -30% |
| 真空 | +20% | +10% | 0% | -50% |

## 核心类

### TerrainSystem
```python
class TerrainSystem:
    def apply_terrain_to_unit(unit, zone) -> Dict  # 应用地形效果
    def calculate_terrain_defense(unit, zone) -> int  # 计算防御加成
    def can_unit_move_to_zone(unit, from_zone, to_zone) -> bool  # 检查移动可行性
    def get_terrain_advantage(attacker_zone, defender_zone) -> Dict  # 地形优势分析
```

### Battlefield
```python
class Battlefield:
    def get_zone(zone_id) -> BattlefieldZone  # 获取区域
    def set_weather(weather)  # 设置天气
    def update_weather()  # 更新天气（回合结束）
    def get_weather_modifiers() -> Dict  # 获取天气修正
    def check_zone_control() -> Dict  # 检查区域控制
```

### BattlefieldZone
```python
class BattlefieldZone:
    def apply_terrain_modifiers(unit) -> Dict  # 应用地形修正
    def get_cover_bonus() -> float  # 获取掩体加成
    def fortify(level) -> bool  # 筑防
```

## 使用示例

```python
from terrain_system import *

# 创建地形系统
terrain_system = TerrainSystem()
battlefield = terrain_system.create_battlefield("前线战场")

# 获取区域
zone = battlefield.get_zone("A1")

# 应用地形效果
mods = terrain_system.apply_terrain_to_unit(unit, zone)
print(f"防御加成: {mods['defense_bonus']}%")
print(f"掩体效果: {zone.get_cover_bonus():.0%}")

# 地形优势分析
advantage = terrain_system.get_terrain_advantage(attacker_zone, defender_zone)
print(f"建议: {advantage['recommendation']}")

# 设置天气
battlefield.set_weather(WeatherCondition.STORMY)
```

## 战斗集成

```python
from terrain_combat_demo import TerrainEnhancedCombat

# 创建地形战斗
combat = TerrainEnhancedCombat("北部战线")

# 部署单位到区域
combat.assign_unit_to_zone(unit, "A1")

# 运行战斗
combat.run_terrain_battle(friendly_units, enemy, max_turns=10)
```

## 文件结构

```
D:\program\univers\demo\game_project\
├── terrain_system.py        # 地形系统核心
├── terrain_combat_demo.py    # 地形战斗演示
├── modern_warfare_system.py  # 战斗系统（已集成地形）
└── TERRAIN_SYSTEM_SUMMARY.md # 本文档
```

## 设计亮点

1. **多维度地形效果**：防御、速度、侦查、精度、通讯、隐蔽
2. **筑防系统**：可升级的防御工事
3. **动态天气**：回合结束时天气变化，影响所有地形效果
4. **科幻地形**：太空站和轨道环境，特殊能力加成
5. **战术建议**：地形优势分析为玩家提供决策支持

---

**状态**: ✅ 完成
**版本**: 1.0
**日期**: 2026-03-25
