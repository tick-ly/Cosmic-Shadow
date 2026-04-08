# -*- coding: utf-8 -*-
"""
宇宙之影 - 英雄单位设计 V2
基于原文《无穷重阻》科幻设定重新设计

原文关键设定（从txt中提取）：
1. 科幻背景：机甲、装甲、载具、战舰等
2. 单位命名：编号、代号、型号（如Gamma型、Sigma型）
3. 能力分类：感知型、操控型，强化型等
4. 级别划分：初级、中级、高级、顶级
5. 科幻术语：系统、模块、终端、接口、控制、联结
6. 战斗系统：火力、机动、防御、探测、通讯、指挥
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class AbilityCategory(Enum):
    """能力分类（原文设定）"""
    PERCEPTION = "感知型"
    CONTROL = "操控型"
    ENHANCE = "强化型"
    WEAKEN = "削弱型"
    MATTER = "物质型"
    ENERGY = "能量型"
    INFORMATION = "信息型"
    SPACE = "空间型"
    TIME = "时间型"

class UnitLevel(Enum):
    """单位级别（原文中初级/中级/高级/顶级）"""
    GRADE_C = "C级"
    GRADE_B = "B级"
    GRADE_A = "A级"
    GRADE_S = "S级"

class UnitType(Enum):
    """单位类型（原文中的机甲、装甲、载具等）"""
    MECHA = "机甲"
    ARMOR = "装甲"
    VEHICLE = "载具"
    WARSHIP = "战舰"
    BASE = "基地"

class HeroRole(Enum):
    """英雄定位"""
    STRIKER = "突击型"
    SCOUT = "侦察型"
    SUPPORT = "支援型"
    COMMAND = "指挥型"
    BALANCE = "均衡型"

@dataclass
class Ability:
    """能力定义"""
    name: str
    category: AbilityCategory
    description: str
    effect_type: str
    effect_value: int
    cooldown: int
    cost: int
    success_rate: int
    duration: int

@dataclass
class HeroUnit:
    """英雄单位"""
    codename: str
    designation: str
    unit_type: str
    level: UnitLevel
    model_name: str
    health: int
    energy: int
    armor: int
    speed: int
    firepower: int
    detection: int
    communication: int
    abilities: List[Ability]
    role: HeroRole
    traits: List[str]
    energy_cost_multiplier: float = 1.0

# 1. Gamma-7 突击型机甲
GAMMA_STRIKER = HeroUnit(
    codename="Gamma-7",
    designation="Gamma型",
    unit_type="机甲",
    level=UnitLevel.GRADE_A,
    model_name="突击型Gamma机甲",
    health=1200,
    energy=600,
    armor=45,
    speed=85,
    firepower=95,
    detection=60,
    communication=70,
    abilities=[
        Ability(
            name="共振打击",
            category=AbilityCategory.ENERGY,
            description="释放高能共振波，造成范围伤害",
            effect_type="damage",
            effect_value=180,
            cooldown=3,
            cost=45,
            success_rate=85,
            duration=0
        ),
        Ability(
            name="动力增幅",
            category=AbilityCategory.ENHANCE,
            description="增幅机甲动力系统，提升火力输出",
            effect_type="buff",
            effect_value=40,
            cooldown=4,
            cost=35,
            success_rate=80,
            duration=3
        ),
        Ability(
            name="过载模式",
            category=AbilityCategory.ENERGY,
            description="超越能量极限，短时间内输出最大化",
            effect_type="damage",
            effect_value=350,
            cooldown=8,
            cost=100,
            success_rate=65,
            duration=1
        ),
    ],
    role=HeroRole.STRIKER,
    traits=["高输出", "突击专家", "能量消耗大"],
    energy_cost_multiplier=1.3
)

# 2. Sigma-3 侦察型机甲
SIGMA_SCOUT = HeroUnit(
    codename="Sigma-3",
    designation="Sigma型",
    unit_type="机甲",
    level=UnitLevel.GRADE_B,
    model_name="侦察型Sigma机甲",
    health=700,
    energy=800,
    armor=25,
    speed=95,
    firepower=50,
    detection=90,
    communication=85,
    abilities=[
        Ability(
            name="广域扫描",
            category=AbilityCategory.PERCEPTION,
            description="大范围扫描敌方单位位置",
            effect_type="utility",
            effect_value=0,
            cooldown=2,
            cost=20,
            success_rate=90,
            duration=0
        ),
        Ability(
            name="信息同步",
            category=AbilityCategory.INFORMATION,
            description="与友军共享战场信息",
            effect_type="buff",
            effect_value=30,
            cooldown=3,
            cost=25,
            success_rate=88,
            duration=4
        ),
        Ability(
            name="战术预判",
            category=AbilityCategory.PERCEPTION,
            description="预判敌方行动轨迹",
            effect_type="debuff",
            effect_value=25,
            cooldown=5,
            cost=40,
            success_rate=75,
            duration=2
        ),
    ],
    role=HeroRole.SCOUT,
    traits=["高探测", "信息专家", "生存能力弱"],
    energy_cost_multiplier=0.8
)

# 3. Omega-12 支援型载具
OMEGA_SUPPORT = HeroUnit(
    codename="Omega-12",
    designation="Omega型",
    unit_type="载具",
    level=UnitLevel.GRADE_A,
    model_name="支援型Omega载具",
    health=1500,
    energy=900,
    armor=60,
    speed=40,
    firepower=40,
    detection=70,
    communication=95,
    abilities=[
        Ability(
            name="能量传输",
            category=AbilityCategory.ENERGY,
            description="向友军传输能量，修复损伤",
            effect_type="heal",
            effect_value=120,
            cooldown=3,
            cost=50,
            success_rate=92,
            duration=0
        ),
        Ability(
            name="防御增幅",
            category=AbilityCategory.ENHANCE,
            description="增幅友军防御系统",
            effect_type="buff",
            effect_value=35,
            cooldown=4,
            cost=30,
            success_rate=88,
            duration=3
        ),
        Ability(
            name="战场指挥",
            category=AbilityCategory.INFORMATION,
            description="协调全场友军行动",
            effect_type="buff",
            effect_value=50,
            cooldown=6,
            cost=60,
            success_rate=80,
            duration=4
        ),
    ],
    role=HeroRole.SUPPORT,
    traits=["治疗专家", "指挥型", "输出能力弱"],
    energy_cost_multiplier=0.7
)

# 4. Alpha-1 指挥型战舰
ALPHA_COMMAND = HeroUnit(
    codename="Alpha-1",
    designation="Alpha型",
    unit_type="战舰",
    level=UnitLevel.GRADE_S,
    model_name="指挥型Alpha战舰",
    health=3000,
    energy=1500,
    armor=100,
    speed=30,
    firepower=120,
    detection=100,
    communication=100,
    abilities=[
        Ability(
            name="战术压制",
            category=AbilityCategory.CONTROL,
            description="全频段干扰敌方通讯",
            effect_type="debuff",
            effect_value=40,
            cooldown=5,
            cost=70,
            success_rate=85,
            duration=3
        ),
        Ability(
            name="火力覆盖",
            category=AbilityCategory.ENERGY,
            description="引导轨道火力进行打击",
            effect_type="damage",
            effect_value=280,
            cooldown=6,
            cost=90,
            success_rate=80,
            duration=0
        ),
        Ability(
            name="指挥光环",
            category=AbilityCategory.ENHANCE,
            description="旗舰级指挥光环，提升全军战力",
            effect_type="buff",
            effect_value=60,
            cooldown=8,
            cost=120,
            success_rate=75,
            duration=5
        ),
    ],
    role=HeroRole.COMMAND,
    traits=["旗舰级", "全能指挥", "移动缓慢"],
    energy_cost_multiplier=1.2
)

# 5. Delta-5 均衡型装甲
DELTA_BALANCE = HeroUnit(
    codename="Delta-5",
    designation="Delta型",
    unit_type="装甲",
    level=UnitLevel.GRADE_B,
    model_name="均衡型Delta装甲",
    health=1000,
    energy=700,
    armor=50,
    speed=65,
    firepower=70,
    detection=65,
    communication=75,
    abilities=[
        Ability(
            name="自适应护盾",
            category=AbilityCategory.MATTER,
            description="根据威胁自动调节护盾",
            effect_type="buff",
            effect_value=45,
            cooldown=3,
            cost=35,
            success_rate=85,
            duration=3
        ),
        Ability(
            name="双模式切换",
            category=AbilityCategory.CONTROL,
            description="在攻击和防御模式间切换",
            effect_type="buff",
            effect_value=30,
            cooldown=4,
            cost=40,
            success_rate=80,
            duration=2
        ),
        Ability(
            name="系统重构",
            category=AbilityCategory.INFORMATION,
            description="重构装甲系统，平衡所有属性",
            effect_type="buff",
            effect_value=50,
            cooldown=6,
            cost=55,
            success_rate=72,
            duration=3
        ),
    ],
    role=HeroRole.BALANCE,
    traits=["适应性强", "无明显短板", "无突出优势"],
    energy_cost_multiplier=1.0
)

# 6. Pi-9 空间型机甲
PI_SPATIAL = HeroUnit(
    codename="Pi-9",
    designation="Pi型",
    unit_type="机甲",
    level=UnitLevel.GRADE_S,
    model_name="空间型Pi机甲",
    health=900,
    energy=1000,
    armor=35,
    speed=100,
    firepower=110,
    detection=80,
    communication=60,
    abilities=[
        Ability(
            name="空间折叠",
            category=AbilityCategory.SPACE,
            description="短距离空间跃迁",
            effect_type="utility",
            effect_value=0,
            cooldown=2,
            cost=60,
            success_rate=85,
            duration=0
        ),
        Ability(
            name="维度斩击",
            category=AbilityCategory.SPACE,
            description="跨越空间维度攻击",
            effect_type="damage",
            effect_value=220,
            cooldown=4,
            cost=80,
            success_rate=75,
            duration=0
        ),
        Ability(
            name="空间锁链",
            category=AbilityCategory.SPACE,
            description="将目标封锁在异空间",
            effect_type="debuff",
            effect_value=150,
            cooldown=7,
            cost=110,
            success_rate=65,
            duration=2
        ),
    ],
    role=HeroRole.STRIKER,
    traits=["空间操控", "高机动", "能量消耗极高"],
    energy_cost_multiplier=1.5
)

# 7. Tau-4 时间型机甲
TAU_TEMPORAL = HeroUnit(
    codename="Tau-4",
    designation="Tau型",
    unit_type="机甲",
    level=UnitLevel.GRADE_S,
    model_name="时间型Tau机甲",
    health=800,
    energy=1200,
    armor=30,
    speed=80,
    firepower=100,
    detection=90,
    communication=70,
    abilities=[
        Ability(
            name="时间减缓",
            category=AbilityCategory.TIME,
            description="减缓局部时间流速",
            effect_type="debuff",
            effect_value=50,
            cooldown=3,
            cost=70,
            success_rate=78,
            duration=2
        ),
        Ability(
            name="时间回溯",
            category=AbilityCategory.TIME,
            description="回溯短暂时空",
            effect_type="heal",
            effect_value=100,
            cooldown=6,
            cost=90,
            success_rate=70,
            duration=0
        ),
        Ability(
            name="时间冻结",
            category=AbilityCategory.TIME,
            description="冻结目标区域时间",
            effect_type="debuff",
            effect_value=200,
            cooldown=10,
            cost=150,
            success_rate=55,
            duration=1
        ),
    ],
    role=HeroRole.SUPPORT,
    traits=["时间操控", "高风险高回报", "脆弱"],
    energy_cost_multiplier=1.8
)

# 英雄注册表
HERO_REGISTRY = {
    "gamma_7": GAMMA_STRIKER,
    "sigma_3": SIGMA_SCOUT,
    "omega_12": OMEGA_SUPPORT,
    "alpha_1": ALPHA_COMMAND,
    "delta_5": DELTA_BALANCE,
    "pi_9": PI_SPATIAL,
    "tau_4": TAU_TEMPORAL,
}

def get_hero_by_level(level: UnitLevel) -> List[HeroUnit]:
    return [h for h in HERO_REGISTRY.values() if h.level == level]

def get_hero_by_role(role: HeroRole) -> List[HeroUnit]:
    return [h for h in HERO_REGISTRY.values() if h.role == role]

def print_hero_card(hero: HeroUnit):
    print("=" * 70)
    print(f"[型号] {hero.designation} | [代号] {hero.codename}")
    print(f"[类型] {hero.unit_type} | [级别] {hero.level.value}")
    print(f"[定位] {hero.role.value}")
    print("-" * 70)
    print(f"[基础属性]")
    print(f"  生命: {hero.health} | 能量: {hero.energy} | 装甲: {hero.armor}")
    print(f"  速度: {hero.speed} | 火力: {hero.firepower}")
    print(f"  探测: {hero.detection} | 通讯: {hero.communication}")
    print("-" * 70)
    print(f"[能力列表]")
    for i, ab in enumerate(hero.abilities):
        print(f"  [{i+1}] {ab.name} ({ab.category.value})")
        print(f"      效果: {ab.description}")
        print(f"      威力: {ab.effect_value} | 消耗: {ab.cost} | 成功率: {ab.success_rate}%")
    print("-" * 70)
    print(f"[特性] {', '.join(hero.traits)}")
    print(f"[能量倍率] {hero.energy_cost_multiplier}x")
    print("=" * 70)

class HeroSystem:
    def __init__(self):
        self.active_heroes = []

    def create_hero(self, hero_key: str) -> Optional[HeroUnit]:
        hero = HERO_REGISTRY.get(hero_key)
        if hero:
            self.active_heroes.append(hero)
        return hero

    def use_ability(self, hero: HeroUnit, ability_index: int) -> Dict:
        if ability_index >= len(hero.abilities):
            return {"success": False, "reason": "能力不存在"}

        ability = hero.abilities[ability_index]
        actual_cost = int(ability.cost * hero.energy_cost_multiplier)

        import random
        roll = random.randint(1, 100)
        success = roll <= ability.success_rate

        result = {
            "success": success,
            "hero": hero.codename,
            "ability": ability.name,
            "category": ability.category.value,
            "level": hero.level.value
        }

        if success:
            result["effect"] = {
                "type": ability.effect_type,
                "value": ability.effect_value,
                "cost": actual_cost
            }
            result["message"] = f"[{hero.codename}] 使用 {ability.name}"
        else:
            result["cost"] = actual_cost // 2
            result["message"] = f"[{hero.codename}] {ability.name} 失败!"

        return result

def main():
    print("\n" + "=" * 70)
    print("[宇宙之影] 英雄单位图鉴 V2")
    print("科幻设定版本 - 基于原文设定")
    print("=" * 70)

    print("\n[按级别分类]")
    for level in UnitLevel:
        heroes = get_hero_by_level(level)
        if heroes:
            print(f"\n【{level.value}】")
            for hero in heroes:
                print(f"  {hero.codename} - {hero.model_name}")

    print("\n" + "=" * 70)
    print("[详细英雄卡片]")
    print("=" * 70)

    for hero in HERO_REGISTRY.values():
        print_hero_card(hero)
        print()

    print("\n" + "=" * 70)
    print("[能力系统演示]")
    print("=" * 70)

    system = HeroSystem()

    gamma = system.create_hero("gamma_7")
    if gamma:
        print(f"\n[启动] {gamma.codename} - {gamma.model_name}")
        print(f"[状态] 生命:{gamma.health} 能量:{gamma.energy} 装甲:{gamma.armor}")

        print("\n[能力使用测试]")
        for i in range(3):
            result = system.use_ability(gamma, i)
            print(result["message"])
            if result["success"]:
                print(f"  效果: {result['effect']['type']} +{result['effect']['value']}")
            else:
                print(f"  失败! 消耗: {result['cost']}")

if __name__ == "__main__":
    main()
