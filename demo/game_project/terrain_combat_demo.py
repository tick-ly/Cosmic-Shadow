# -*- coding: utf-8 -*-
"""
宇宙之影 - 地形增强战斗系统演示
Terrain-Enhanced Combat System Demo
"""

from modern_warfare_system import (
    ModernCombatSystem, WarfareUnit, EnemyForce, MachineScale, Operator, Ability, AbilityEffect, AbilityTier
)
from terrain_system import (
    TerrainSystem, TerrainType, WeatherCondition, BattlefieldZone,
    TERRAIN_REGISTRY, print_terrain_info, print_battlefield_status
)
import random
import time

class TerrainCombatPlugin:
    """
    地形战斗插件 — 可与 ModernCombatSystem 组合使用

    用法:
        cs = ModernCombatSystem(enable_terrain=True, battlefield_name="北部战线")
        cs.terrain.assign_unit_to_zone(unit, "A2")
        # 攻击时自动应用地形修正
    """

    def __init__(self, battlefield_name: str = "默认战场"):
        self.terrain_system = TerrainSystem()
        self.battlefield = self.terrain_system.create_battlefield(battlefield_name)
        self.turn = 0

    def assign_unit_to_zone(self, unit: WarfareUnit, zone_id: str) -> bool:
        """将单位分配到区域"""
        zone = self.battlefield.get_zone(zone_id)
        if zone:
            unit.current_zone = zone_id
            zone.occupying_units.append(unit.name)
            return True
        return False

    def apply_terrain_effects(self, unit: WarfareUnit) -> dict:
        """应用地形效果到单位"""
        zone_id = getattr(unit, 'current_zone', None)
        if not zone_id:
            return {}

        zone = self.battlefield.get_zone(zone_id)
        if not zone:
            return {}

        return self.terrain_system.apply_terrain_to_unit(unit, zone)

    def calculate_terrain_damage_modifier(self, attacker: WarfareUnit, defender: WarfareUnit) -> float:
        """计算地形修正的伤害倍数（攻防双方地形综合）"""
        attacker_zone_id = getattr(attacker, 'current_zone', None)
        defender_zone_id = getattr(defender, 'current_zone', None)

        attacker_mod = 1.0
        defender_mod = 1.0

        if attacker_zone_id:
            attacker_zone = self.battlefield.get_zone(attacker_zone_id)
            if attacker_zone:
                attacker_mod = 1.0 + attacker_zone.terrain.modifiers.stealth_bonus / 100

        if defender_zone_id:
            defender_zone = self.battlefield.get_zone(defender_zone_id)
            if defender_zone:
                mods = defender_zone.apply_terrain_modifiers(defender)
                defender_mod = 1.0 - (defender_zone.get_cover_bonus() + mods.get("defense_bonus", 0) / 100)

        return attacker_mod / max(0.5, defender_mod)

    def terrain_attack_modifier(self, attacker: WarfareUnit) -> dict:
        """获取攻击方地形修正"""
        zone_id = getattr(attacker, 'current_zone', None)
        if not zone_id:
            return {"accuracy_mod": 0, "damage_mod": 0}

        zone = self.battlefield.get_zone(zone_id)
        if not zone:
            return {"accuracy_mod": 0, "damage_mod": 0}

        mods = zone.terrain.modifiers
        weather_mods = self.battlefield.get_weather_modifiers()

        accuracy_mod = mods.accuracy_penalty + weather_mods.get("accuracy", 0)
        damage_mod = mods.stealth_bonus

        return {
            "accuracy_mod": accuracy_mod,
            "damage_mod": damage_mod,
            "terrain_name": zone.terrain.name
        }

    def terrain_defense_modifier(self, defender: WarfareUnit) -> dict:
        """获取防守方地形修正"""
        zone_id = getattr(defender, 'current_zone', None)
        if not zone_id:
            return {"defense_mod": 0, "cover_bonus": 0.0}

        zone = self.battlefield.get_zone(zone_id)
        if not zone:
            return {"defense_mod": 0, "cover_bonus": 0.0}

        mods = zone.apply_terrain_modifiers(defender)
        weather_mods = self.battlefield.get_weather_modifiers()

        defense_mod = mods.get("defense_bonus", 0)
        speed_penalty = mods.get("speed_penalty", 0) + weather_mods.get("speed", 0)
        detection_mod = mods.get("detection_penalty", 0) + weather_mods.get("detection", 0)

        return {
            "defense_mod": defense_mod,
            "cover_bonus": zone.get_cover_bonus() * 100,
            "speed_penalty": speed_penalty,
            "detection_mod": detection_mod,
            "terrain_name": zone.terrain.name,
            "fort_level": zone.fortification_level
        }


# 向后兼容别名
TerrainEnhancedCombat = TerrainCombatPlugin


def create_terrain_heroes():
    """创建适合地形的英雄单位"""
    from hero_integration import create_warfare_unit_from_hero, add_hero_abilities_to_operator
    from hero_units_v2 import HERO_REGISTRY

    # 选择地形适配英雄
    hero_configs = [
        ("gamma_7", "A1"),   # 平原 - 突击型
        ("sigma_3", "B2"),   # 丛林 - 侦察型
        ("alpha_1", "A2"),   # 山地 - 指挥型
    ]

    units = []
    for hero_key, zone_id in hero_configs:
        hero = HERO_REGISTRY.get(hero_key)
        if hero:
            unit = create_warfare_unit_from_hero(hero)
            add_hero_abilities_to_operator(unit.operator, hero)
            units.append((unit, zone_id))

    return units

def demo_terrain_combat():
    """演示地形战斗"""
    print("\n" + "=" * 80)
    print("[宇宙之影] 地形增强战斗系统演示")
    print("=" * 80)

    # 创建地形战斗系统
    terrain_combat = TerrainEnhancedCombat("北部战线")

    # 创建单位并部署
    hero_units = create_terrain_heroes()

    friendly_units = []
    for unit, zone_id in hero_units:
        terrain_combat.assign_unit_to_zone(unit, zone_id)
        friendly_units.append(unit)
        print(f"\n[部署] {unit.name} -> 区域{zone_id}")

    # 创建敌方
    enemy = terrain_combat.combat_system.create_enemy_force(MachineScale.SQUAD)

    # 筑防山地区域
    mountain_zone = terrain_combat.battlefield.get_zone("A2")
    if mountain_zone:
        mountain_zone.fortify(2)

    # 设置天气
    terrain_combat.battlefield.set_weather(WeatherCondition.CLEAR)

    # 运行战斗
    terrain_combat.run_terrain_battle(friendly_units, enemy, max_turns=6)

def demo_terrain_only():
    """仅演示地形系统（无战斗）"""
    print("\n" + "=" * 80)
    print("[地形系统详细演示]")
    print("=" * 80)

    # 展示所有科幻相关地形
    print("\n[科幻地形]")
    sci_fi_terrains = [TerrainType.SPACE_STATION, TerrainType.ORBITAL]
    for terrain_type in sci_fi_terrains:
        print_terrain_info(terrain_type)
        print()

    # 创建自定义战场
    terrain_system = TerrainSystem()
    battlefield = terrain_system.create_battlefield("轨道战役")

    # 模拟区域争夺
    battlefield.zones["D1"].occupying_units.append("Alpha-1")
    battlefield.zones["D1"].occupying_units.append("Omega-12")
    battlefield.zones["D2"].occupying_units.append("敌军轨道部队")
    battlefield.zones["D2"].is_contested = True

    # 筑防
    battlefield.zones["D1"].fortify(3)

    # 天气模拟
    battlefield.set_weather(WeatherCondition.SPACE_VOID)

    # 显示状态
    print_battlefield_status(battlefield)

    # 地形优势分析
    print("\n[轨道作战分析]")
    advantage = terrain_system.get_terrain_advantage(
        battlefield.zones["D1"],
        battlefield.zones["D2"]
    )
    print(f"  防守方优势: 防御+{advantage['defender_bonus']}%, 掩体{advantage['defender_cover']:.0f}%")
    print(f"  建议: {advantage['recommendation']}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--terrain-only":
        demo_terrain_only()
    else:
        demo_terrain_combat()
