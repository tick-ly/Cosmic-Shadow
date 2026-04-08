# -*- coding: utf-8 -*-
"""
宇宙之影 - 英雄单位集成模块
将V2版本英雄单位与现代战争战斗系统集成
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from hero_units_v2 import (
    HeroUnit, Ability, UnitLevel, UnitType, HeroRole, AbilityCategory,
    HERO_REGISTRY, get_hero_by_level, get_hero_by_role
)
from modern_warfare_system import (
    Operator, Ability as CombatAbility, AbilityEffect, AbilityTier,
    MachineScale, WarfareUnit, EvolutionStage
)

def create_operator_from_hero(hero: HeroUnit) -> Operator:
    """
    从英雄单位创建操作员

    将V2英雄单位转换为可参与战斗系统的Operator实例
    """
    # 根据单位级别确定能力等级
    tier_map = {
        UnitLevel.GRADE_C: AbilityTier.BASIC,
        UnitLevel.GRADE_B: AbilityTier.BASIC,
        UnitLevel.GRADE_A: AbilityTier.ADVANCED,
        UnitLevel.GRADE_S: AbilityTier.ELITE
    }

    # 根据角色确定是否为指挥官
    is_commander = hero.role == HeroRole.COMMAND

    # 创建操作员
    operator = Operator(
        name=hero.codename,
        ability_tier=tier_map.get(hero.level, AbilityTier.BASIC),
        is_commander=is_commander
    )

    # 覆盖基础属性
    operator.combat_skill = hero.firepower
    operator.technical_skill = hero.detection
    operator.command_skill = hero.communication if is_commander else operator.command_skill

    # 设置现实债务和疲劳
    operator.reality_debt = 0
    operator.fatigue = 0
    operator.morale = 100

    # 设置能量倍率（影响超能消耗）
    operator.energy_cost_multiplier = hero.energy_cost_multiplier

    return operator

def create_warfare_unit_from_hero(hero: HeroUnit) -> WarfareUnit:
    """
    从英雄单位创建战争单位

    根据英雄的科幻类型确定单位规模
    """
    # 根据单位类型确定规模
    scale_map = {
        "机甲": MachineScale.INDIVIDUAL,
        "装甲": MachineScale.SQUAD,
        "载具": MachineScale.SQUAD,
        "战舰": MachineScale.LEGION
    }

    scale = scale_map.get(hero.unit_type, MachineScale.INDIVIDUAL)
    operator = create_operator_from_hero(hero)

    # 创建战争单位
    unit = WarfareUnit(
        name=hero.codename,
        scale=scale,
        operator=operator
    )

    # 覆盖基础属性
    unit.max_health = hero.health
    unit.current_health = hero.health
    unit.base_armor = hero.armor

    # 根据规模调整
    if scale == MachineScale.LEGION:
        unit.mobility = hero.speed // 3
        unit.communication_range = 2000
    elif scale == MachineScale.SQUAD:
        unit.mobility = hero.speed // 2
        unit.communication_range = 500
    else:
        unit.mobility = hero.speed
        unit.communication_range = 100

    # 设置能量倍率
    unit.energy_cost_multiplier = hero.energy_cost_multiplier

    return unit

def convert_ability_to_combat_ability(ability: Ability, tier: AbilityTier) -> CombatAbility:
    """将V2能力转换为战斗系统能力"""
    effect = AbilityEffect(
        name=ability.name,
        tier=tier,
        description=ability.description,
        success_rate=ability.success_rate,
        reality_debt=ability.cost,
        duration=ability.duration
    )

    # 根据效果类型设置增强效果
    if ability.effect_type == "damage":
        effect.damage_boost = ability.effect_value
    elif ability.effect_type == "heal":
        effect.repair_rate = ability.effect_value
    elif ability.effect_type == "buff":
        effect.damage_boost = ability.effect_value
        effect.defense_boost = ability.effect_value // 2
    elif ability.effect_type == "debuff":
        effect.damage_boost = -ability.effect_value // 2

    return CombatAbility(ability.name, tier, effect)

def add_hero_abilities_to_operator(operator: Operator, hero: HeroUnit):
    """
    将英雄能力添加到操作员

    根据英雄级别添加对应等级的能力
    """
    for ability in hero.abilities:
        # 确定能力等级
        tier = AbilityTier.BASIC
        if hero.level == UnitLevel.GRADE_A:
            tier = AbilityTier.ADVANCED
        elif hero.level == UnitLevel.GRADE_S:
            tier = AbilityTier.ELITE

        combat_ability = convert_ability_to_combat_ability(ability, tier)
        operator.add_ability(combat_ability)

def get_hero_ability_info(hero: HeroUnit) -> List[Dict]:
    """获取英雄能力信息（用于UI显示）"""
    info = []
    for i, ability in enumerate(hero.abilities):
        info.append({
            "index": i,
            "name": ability.name,
            "category": ability.category.value,
            "description": ability.description,
            "effect_type": ability.effect_type,
            "effect_value": ability.effect_value,
            "cost": ability.cost,
            "success_rate": ability.success_rate,
            "cooldown": ability.cooldown
        })
    return info

def print_hero_combat_card(hero: HeroUnit):
    """打印用于战斗系统的英雄卡片"""
    unit = create_warfare_unit_from_hero(hero)
    operator = unit.operator

    print("=" * 70)
    print(f"[型号] {hero.designation} | [代号] {hero.codename}")
    print(f"[类型] {hero.unit_type} | [级别] {hero.level.value} | [定位] {hero.role.value}")
    print("-" * 70)
    print(f"[战斗属性]")
    print(f"  生命: {unit.max_health} | 装甲: {unit.base_armor} | 机动: {unit.mobility}")
    print(f"  火力: {operator.combat_skill} | 探测: {operator.technical_skill}")
    print(f"  通讯: {operator.command_skill} | 能量倍率: {hero.energy_cost_multiplier}x")
    print("-" * 70)
    print(f"[能力列表]")
    for i, ability in enumerate(hero.abilities):
        print(f"  [{i+1}] {ability.name} ({ability.category.value})")
        print(f"      威力: {ability.effect_value} | 消耗: {ability.cost} | 成功率: {ability.success_rate}%")
    print("-" * 70)
    print(f"[特性] {', '.join(hero.traits)}")
    print("=" * 70)

class HeroCombatSystem:
    """英雄战斗系统"""

    def __init__(self):
        self.active_units: Dict[str, WarfareUnit] = {}
        self.hero_registry = HERO_REGISTRY

    def deploy_hero(self, hero_key: str) -> Optional[WarfareUnit]:
        """部署英雄单位"""
        hero = self.hero_registry.get(hero_key)
        if not hero:
            return None

        unit = create_warfare_unit_from_hero(hero)
        add_hero_abilities_to_operator(unit.operator, hero)
        self.active_units[hero_key] = unit

        return unit

    def get_hero_unit(self, hero_key: str) -> Optional[WarfareUnit]:
        """获取已部署的英雄单位"""
        return self.active_units.get(hero_key)

    def list_deployed_heroes(self) -> List[str]:
        """列出已部署的英雄"""
        return list(self.active_units.keys())

def demo_hero_combat_integration():
    """演示英雄单位与战斗系统集成"""
    print("\n" + "=" * 70)
    print("[英雄单位战斗系统集成演示]")
    print("=" * 70)

    combat_system = HeroCombatSystem()

    # 按级别展示英雄
    print("\n[可部署英雄]")
    for level in UnitLevel:
        heroes = get_hero_by_level(level)
        if heroes:
            print(f"\n【{level.value}】")
            for hero in heroes:
                print(f"  {hero.codename} - {hero.role.value} - {hero.unit_type}")

    # 部署英雄并展示战斗卡片
    print("\n" + "=" * 70)
    print("[英雄战斗卡片]")
    print("=" * 70)

    deploy_keys = ["gamma_7", "sigma_3", "omega_12", "alpha_1", "delta_5", "pi_9", "tau_4"]
    for key in deploy_keys:
        hero = HERO_REGISTRY.get(key)
        if hero:
            print_hero_combat_card(hero)
            print()

    # 部署并进行简单战斗测试
    print("\n" + "=" * 70)
    print("[战斗部署测试]")
    print("=" * 70)

    # 部署S级英雄
    alpha = combat_system.deploy_hero("alpha_1")
    if alpha:
        print(f"\n[部署] {alpha.name}")
        print(f"  生命: {alpha.max_health}")
        print(f"  装甲: {alpha.base_armor}")
        print(f"  机动: {alpha.mobility}")
        print(f"  通讯: {alpha.operator.command_skill}")
        print(f"  能力数: {len(alpha.operator.abilities)}")

        # 使用能力测试
        print("\n[能力测试]")
        if alpha.operator.abilities:
            ability = alpha.operator.abilities[0]
            print(f"  能力: {ability.name} ({ability.tier.value})")
            print(f"  成功率: {ability.effect.success_rate}%")
            print(f"  现实债务: {ability.effect.reality_debt}")

    # 部署空间型英雄
    pi = combat_system.deploy_hero("pi_9")
    if pi:
        print(f"\n[部署] {pi.name}")
        print(f"  生命: {pi.max_health}")
        print(f"  装甲: {pi.base_armor}")
        print(f"  速度: {pi.mobility}")
        print(f"  能量倍率: {pi.energy_cost_multiplier}x")

    print("\n" + "=" * 70)
    print("[集成完成] 英雄单位已与现代战争系统集成")
    print("=" * 70)

if __name__ == "__main__":
    demo_hero_combat_integration()
