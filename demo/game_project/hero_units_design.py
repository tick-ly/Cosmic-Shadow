"""
宇宙之影 - 英雄单位设计
Hero Units Design Based on Original Novel

基于原文《无穷重阻》设定设计的英雄单位

原文核心设定：
1. 阶段系统：平阶段 → 魔阶段 → 神阶段
2. 血统能力：基础/进阶/精英超能
3. 能力类型：预测、空间操控、时间操控、现实扭曲
4. 代价系统：现实债务、疲劳、反噬
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class AbilityTier(Enum):
    """超能等级"""
    BASIC = "基础超能"
    ADVANCED = "进阶超能"
    ELITE = "精英超能"

class EvolutionStage(Enum):
    """进化阶段"""
    BASIC = "基础阶段"  # 普通能力使用
    MAGIC = "魔阶段"    # 能力大幅增强，代价增加
    DIVINE = "神阶段"   # 接近全能，极大代价

class HeroRole(Enum):
    """英雄定位"""
    PREDICTOR = "预测者"      # 战术洞察
    SPATIAL = "空间使者"      # 空间操控
    TEMPORAL = "时间行者"     # 时间操控
    REALITY = "现实扭曲者"    # 现实操控
    COMMANDER = "指挥官"      # 团队辅助
    BALANCER = "均衡者"       # 多重能力

@dataclass
class HeroAbility:
    """英雄能力定义"""
    name: str
    tier: AbilityTier
    description: str
    effect_type: str  # damage_boost, prediction, spatial, etc.
    effect_value: int
    cooldown: int
    reality_debt: int
    success_rate: int
    duration: int

@dataclass
class HeroUnit:
    """英雄单位定义"""
    name: str
    codename: str  # 代号
    role: HeroRole
    evolution_stage: EvolutionStage

    # 基础属性
    max_health: int
    max_energy: int
    base_armor: int
    base_speed: int

    # 能力
    abilities: List[HeroAbility]

    # 特性
    traits: List[str]  # 特性标签
    passive_effects: Dict[str, int]  # 被动效果

    # 代价系统
    debt_multiplier: float  # 债务倍率
    fatigue_resistance: int  # 抗疲劳

# ==================== 英雄单位设计 ====================

# 1. 预测者系列
PREDICTOR_HERO = HeroUnit(
    name="预言者",
    codename="零号-预言",
    role=HeroRole.PREDICTOR,
    evolution_stage=EvolutionStage.MAGIC,

    max_health=800,
    max_energy=500,
    base_armor=30,
    base_speed=70,

    abilities=[
        HeroAbility(
            name="战术预判",
            tier=AbilityTier.BASIC,
            description="预判敌方战术意图，提前做出应对",
            effect_type="prediction_tactical",
            effect_value=85,
            cooldown=2,
            reality_debt=15,
            success_rate=85,
            duration=0
        ),
        HeroAbility(
            name="战场感知",
            tier=AbilityTier.ADVANCED,
            description="全面感知战场态势，洞察敌方弱点",
            effect_type="prediction_combat",
            effect_value=95,
            cooldown=3,
            reality_debt=25,
            success_rate=80,
            duration=3
        ),
        HeroAbility(
            name="命运凝视",
            tier=AbilityTier.ELITE,
            description="窥视命运线，在关键时刻改变战局",
            effect_type="prediction_fate",
            effect_value=100,
            cooldown=5,
            reality_debt=50,
            success_rate=70,
            duration=2
        ),
    ],

    traits=["战术家", "洞察者", "冷静判断"],
    passive_effects={"detection_range": 500, "prediction_accuracy": 10},

    debt_multiplier=1.2,
    fatigue_resistance=40
)

# 2. 空间使者系列
SPATIAL_HERO = HeroUnit(
    name="空间行者",
    codename="维度行者",
    role=HeroRole.SPATIAL,
    evolution_stage=EvolutionStage.MAGIC,

    max_health=1000,
    max_energy=600,
    base_armor=40,
    base_speed=90,

    abilities=[
        HeroAbility(
            name="空间折叠",
            tier=AbilityTier.BASIC,
            description="瞬间移动到目标位置，无视距离",
            effect_type="spatial_teleport",
            effect_value=100,
            cooldown=3,
            reality_debt=30,
            success_rate=80,
            duration=0
        ),
        HeroAbility(
            name="维度斩击",
            tier=AbilityTier.ADVANCED,
            description="跨越空间发起攻击，无视防御",
            effect_type="spatial_attack",
            effect_value=200,
            cooldown=4,
            reality_debt=50,
            success_rate=75,
            duration=0
        ),
        HeroAbility(
            name="空间锁链",
            tier=AbilityTier.ELITE,
            description="将敌人困在折叠空间中",
            effect_type="spatial_trap",
            effect_value=150,
            cooldown=6,
            reality_debt=80,
            success_rate=65,
            duration=3
        ),
    ],

    traits=["空间操控", "高速移动", "无视防御"],
    passive_effects={"evasion": 20, "spatial_awareness": 30},

    debt_multiplier=1.5,
    fatigue_resistance=30
)

# 3. 时间行者系列
TEMPORAL_HERO = HeroUnit(
    name="时间操控者",
    codename="时间零",
    role=HeroRole.TEMPORAL,
    evolution_stage=EvolutionStage.DIVINE,

    max_health=600,
    max_energy=800,
    base_armor=20,
    base_speed=60,

    abilities=[
        HeroAbility(
            name="时间减缓",
            tier=AbilityTier.BASIC,
            description="减慢局部时间流速",
            effect_type="time_slow",
            effect_value=50,
            cooldown=3,
            reality_debt=25,
            success_rate=75,
            duration=2
        ),
        HeroAbility(
            name="时间回溯",
            tier=AbilityTier.ADVANCED,
            description="回溯短暂时光，修正错误",
            effect_type="time_rewind",
            effect_value=100,
            cooldown=5,
            reality_debt=60,
            success_rate=60,
            duration=0
        ),
        HeroAbility(
            name="时间冻结",
            tier=AbilityTier.ELITE,
            description="冻结区域内所有时间",
            effect_type="time_stop",
            effect_value=300,
            cooldown=8,
            reality_debt=100,
            success_rate=50,
            duration=1
        ),
    ],

    traits=["时间操控", "高风险高回报", "脆弱但致命"],
    passive_effects={"time_resistance": 30, "reaction_speed": 25},

    debt_multiplier=2.0,
    fatigue_resistance=20
)

# 4. 现实扭曲者系列
REALITY_WARPER = HeroUnit(
    name="现实扭曲者",
    codename="悖论",
    role=HeroRole.REALITY,
    evolution_stage=EvolutionStage.DIVINE,

    max_health=1200,
    max_energy=400,
    base_armor=50,
    base_speed=40,

    abilities=[
        HeroAbility(
            name="重力反转",
            tier=AbilityTier.BASIC,
            description="反转局部重力场",
            effect_type="gravity_flip",
            effect_value=60,
            cooldown=4,
            reality_debt=35,
            success_rate=70,
            duration=2
        ),
        HeroAbility(
            name="因果改写",
            tier=AbilityTier.ADVANCED,
            description="改变事件因果关系",
            effect_type="causality_rewrite",
            effect_value=180,
            cooldown=6,
            reality_debt=70,
            success_rate=55,
            duration=1
        ),
        HeroAbility(
            name="现实重构",
            tier=AbilityTier.ELITE,
            description="完全重构局部现实",
            effect_type="reality_remake",
            effect_value=500,
            cooldown=10,
            reality_debt=150,
            success_rate=40,
            duration=0
        ),
    ],

    traits=["现实操控", "高破坏力", "代价沉重"],
    passive_effects={"armor_boost": 20, "reality_instability": 15},

    debt_multiplier=2.5,
    fatigue_resistance=15
)

# 5. 指挥官系列
COMMANDER_HERO = HeroUnit(
    name="战场指挥官",
    codename="统帅",
    role=HeroRole.COMMANDER,
    evolution_stage=EvolutionStage.BASIC,

    max_health=1500,
    max_energy=700,
    base_armor=60,
    base_speed=30,

    abilities=[
        HeroAbility(
            name="战术指挥",
            tier=AbilityTier.BASIC,
            description="指挥部队协调作战",
            effect_type="tactical_command",
            effect_value=30,
            cooldown=2,
            reality_debt=10,
            success_rate=90,
            duration=3
        ),
        HeroAbility(
            name="全军光环",
            tier=AbilityTier.ADVANCED,
            description="为全军提供属性增幅",
            effect_type="aura_buff",
            effect_value=50,
            cooldown=4,
            reality_debt=20,
            success_rate=85,
            duration=4
        ),
        HeroAbility(
            name="战争统御",
            tier=AbilityTier.ELITE,
            description="全面接管战场指挥",
            effect_type="war_command",
            effect_value=100,
            cooldown=6,
            reality_debt=40,
            success_rate=75,
            duration=5
        ),
    ],

    traits=["团队辅助", "光环效果", "战场控制"],
    passive_effects={"morale_boost": 20, "communication_range": 1000},

    debt_multiplier=0.8,
    fatigue_resistance=60
)

# 6. 均衡者系列 - 多重能力组合
BALANCER_HERO = HeroUnit(
    name="均衡者",
    codename="平衡点",
    role=HeroRole.BALANCER,
    evolution_stage=EvolutionStage.MAGIC,

    max_health=900,
    max_energy=550,
    base_armor=35,
    base_speed=65,

    abilities=[
        HeroAbility(
            name="能力平衡",
            tier=AbilityTier.BASIC,
            description="平衡自身状态",
            effect_type="stat_balance",
            effect_value=40,
            cooldown=2,
            reality_debt=15,
            success_rate=85,
            duration=3
        ),
        HeroAbility(
            name="双重领域",
            tier=AbilityTier.ADVANCED,
            description="同时施展两种能力",
            effect_type="dual_ability",
            effect_value=120,
            cooldown=5,
            reality_debt=45,
            success_rate=70,
            duration=2
        ),
        HeroAbility(
            name="完美均衡",
            tier=AbilityTier.ELITE,
            description="达到能力完美平衡状态",
            effect_type="perfect_balance",
            effect_value=200,
            cooldown=8,
            reality_debt=80,
            success_rate=60,
            duration=3
        ),
    ],

    traits=["多面手", "适应性强", "平衡发展"],
    passive_effects={"ability_synergy": 15, "debt_reduction": 10},

    debt_multiplier=1.3,
    fatigue_resistance=45
)

# 7. 神阶段英雄 - 超越者
DIVINE_HERO = HeroUnit(
    name="超越者",
    codename="神上之神",
    role=HeroRole.BALANCER,
    evolution_stage=EvolutionStage.DIVINE,

    max_health=2000,
    max_energy=1000,
    base_armor=80,
    base_speed=100,

    abilities=[
        HeroAbility(
            name="全能感知",
            tier=AbilityTier.BASIC,
            description="感知一切存在",
            effect_type="omniscience",
            effect_value=100,
            cooldown=3,
            reality_debt=50,
            success_rate=80,
            duration=0
        ),
        HeroAbility(
            name="维度跨越",
            tier=AbilityTier.ADVANCED,
            description="跨越所有维度",
            effect_type="dimension_hop",
            effect_value=250,
            cooldown=5,
            reality_debt=100,
            success_rate=65,
            duration=1
        ),
        HeroAbility(
            name="现实主宰",
            tier=AbilityTier.ELITE,
            description="成为现实的主宰",
            effect_type="reality_dominance",
            effect_value=800,
            cooldown=15,
            reality_debt=200,
            success_rate=40,
            duration=2
        ),
    ],

    traits=["全能", "超越限制", "神级存在"],
    passive_effects={
        "all_stats_boost": 50,
        "debt_immunity": 20,
        "ability_multiplier": 2.0
    },

    debt_multiplier=3.0,
    fatigue_resistance=10
)

# ==================== 英雄单位注册表 ====================

HERO_REGISTRY = {
    "predictor": PREDICTOR_HERO,
    "spatial": SPATIAL_HERO,
    "temporal": TEMPORAL_HERO,
    "reality": REALITY_WARPER,
    "commander": COMMANDER_HERO,
    "balancer": BALANCER_HERO,
    "divine": DIVINE_HERO,
}

def get_hero_by_role(role: HeroRole) -> List[HeroUnit]:
    """根据角色获取英雄"""
    return [h for h in HERO_REGISTRY.values() if h.role == role]

def get_heroes_by_tier(tier: AbilityTier) -> List[HeroUnit]:
    """根据能力等级获取英雄"""
    result = []
    for hero in HERO_REGISTRY.values():
        for ability in hero.abilities:
            if ability.tier == tier:
                result.append(hero)
                break
    return result

def get_heroes_by_stage(stage: EvolutionStage) -> List[HeroUnit]:
    """根据进化阶段获取英雄"""
    return [h for h in HERO_REGISTRY.values() if h.evolution_stage == stage]

# ==================== 英雄能力演示系统 ====================

class HeroAbilitySystem:
    """英雄能力系统"""

    def __init__(self):
        self.active_heroes = []
        self.ability_cooldowns = {}

    def create_hero_instance(self, hero_key: str) -> Optional[HeroUnit]:
        """创建英雄实例"""
        hero = HERO_REGISTRY.get(hero_key)
        if hero:
            self.active_heroes.append(hero)
        return hero

    def use_ability(self, hero: HeroUnit, ability_index: int) -> Dict:
        """使用英雄能力"""
        if ability_index >= len(hero.abilities):
            return {"success": False, "reason": "能力不存在"}

        ability = hero.abilities[ability_index]

        # 检查冷却
        cooldown_key = f"{hero.codename}_{ability.name}"
        if cooldown_key in self.ability_cooldowns:
            remaining = self.ability_cooldowns[cooldown_key]
            if remaining > 0:
                return {
                    "success": False,
                    "reason": f"能力冷却中，剩余{remaining}回合"
                }

        # 计算实际成功率
        debt_penalty = int((hero.debt_multiplier - 1) * 30)
        actual_success = max(20, ability.success_rate - debt_penalty)

        # 判定是否成功
        import random
        success = random.randint(1, 100) <= actual_success

        result = {
            "success": success,
            "hero": hero.name,
            "ability": ability.name,
            "ability_tier": ability.tier.value,
            "actual_success_rate": actual_success
        }

        if success:
            result["effect"] = {
                "type": ability.effect_type,
                "value": ability.effect_value,
                "description": ability.description
            }
            result["cost"] = {
                "reality_debt": ability.reality_debt,
                "duration": ability.duration
            }

            # 设置冷却
            self.ability_cooldowns[cooldown_key] = ability.cooldown
        else:
            # 失败后果
            result["failure"] = {
                "backlash_debt": ability.reality_debt // 2,
                "backlash_damage": ability.effect_value // 4
            }

        return result

    def reduce_cooldowns(self):
        """减少所有冷却"""
        keys_to_remove = []
        for key in self.ability_cooldowns:
            self.ability_cooldowns[key] -= 1
            if self.ability_cooldowns[key] <= 0:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.ability_cooldowns[key]

    def get_hero_stats(self, hero: HeroUnit) -> Dict:
        """获取英雄状态"""
        return {
            "name": hero.name,
            "codename": hero.codename,
            "role": hero.role.value,
            "stage": hero.evolution_stage.value,
            "health": f"{hero.max_health}",
            "energy": f"{hero.max_energy}",
            "armor": hero.base_armor,
            "speed": hero.base_speed,
            "debt_multiplier": hero.debt_multiplier,
            "fatigue_resistance": hero.fatigue_resistance,
            "traits": hero.traits,
            "abilities_count": len(hero.abilities)
        }

def print_hero_card(hero: HeroUnit):
    """打印英雄卡片"""
    print("=" * 60)
    print(f"[英雄] {hero.name}")
    print(f"[代号] {hero.codename}")
    print(f"[定位] {hero.role.value}")
    print(f"[阶段] {hero.evolution_stage.value}")
    print("-" * 60)
    print(f"[基础属性]")
    print(f"  生命: {hero.max_health}")
    print(f"  能量: {hero.max_energy}")
    print(f"  装甲: {hero.base_armor}")
    print(f"  速度: {hero.base_speed}")
    print("-" * 60)
    print(f"[能力列表]")
    for i, ability in enumerate(hero.abilities):
        print(f"  [{i+1}] {ability.name} ({ability.tier.value})")
        print(f"      效果: {ability.description}")
        print(f"      威力: {ability.effect_value}")
        print(f"      冷却: {ability.cooldown} | 代价: {ability.reality_debt} | 成功率: {ability.success_rate}%")
    print("-" * 60)
    print(f"[特性] {', '.join(hero.traits)}")
    print(f"[债务倍率] {hero.debt_multiplier}x | [抗疲劳] {hero.fatigue_resistance}")
    print("=" * 60)

def demo_all_heroes():
    """演示所有英雄"""
    print("\n" + "=" * 70)
    print("[宇宙之影] 英雄单位图鉴")
    print("=" * 70)

    print("\n[按角色分类]")
    print("-" * 70)
    for role in HeroRole:
        heroes = get_hero_by_role(role)
        if heroes:
            print(f"\n【{role.value}】")
            for hero in heroes:
                print(f"  - {hero.name} ({hero.codename})")

    print("\n" + "=" * 70)
    print("[详细英雄卡片]")
    print("=" * 70)

    for hero in HERO_REGISTRY.values():
        print_hero_card(hero)
        print()

    # 演示能力系统
    print("\n" + "=" * 70)
    print("[英雄能力系统演示]")
    print("=" * 70)

    system = HeroAbilitySystem()

    # 创建英雄实例
    predictor = system.create_hero_instance("predictor")
    if predictor:
        print(f"\n[创建英雄] {predictor.name}")
        print(f"[英雄状态]")
        stats = system.get_hero_stats(predictor)
        for key, value in stats.items():
            print(f"  {key}: {value}")

        # 使用能力
        print("\n[使用能力]")
        result = system.use_ability(predictor, 1)  # 使用第二个能力
        print(f"尝试使用: {result.get('ability', '未知')}")
        print(f"结果: {'成功' if result['success'] else '失败'}")

        if result['success']:
            print(f"效果: {result['effect']['description']}")
            print(f"实际成功率: {result['actual_success_rate']}%")
            print(f"代价: {result['cost']['reality_debt']}点现实债务")
        else:
            print(f"失败原因: {result.get('reason', result.get('failure', '未知'))}")

if __name__ == "__main__":
    demo_all_heroes()
