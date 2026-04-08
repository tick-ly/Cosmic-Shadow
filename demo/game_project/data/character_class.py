"""
职业/兵种类数据
CharacterClassSO - 对应 Unity 的 CharacterClassSO
"""

from dataclasses import dataclass
from enum import Enum


class UnitScale(Enum):
    """单位规模"""
    SOLO = "单兵"     # 1人
    SQUAD = "小队"    # 5-10人
    PLATOON = "排"    # 30-50人
    COMPANY = "连"    # 100-200人
    BATTALION = "营"  # 300-1000人


class CombatRole(Enum):
    """战斗角色"""
    ASSAULT = "突击"      # 冲锋陷阵
    SUPPORT = "支援"      # 辅助治疗
    RECON = "侦察"       # 侦查探测
    COMMAND = "指挥"      # 指挥协调
    ENGINEER = "工程"    # 工事设备
    SPECIAL = "特殊"     # 超能力单位


@dataclass
class StatModifier:
    """属性修正（加值）"""
    health: int = 0
    energy: int = 0
    attack: int = 0
    defense: int = 0
    speed: int = 0
    evasion: int = 0


@dataclass
class CharacterClassSO:
    """职业/兵种类数据"""
    id: str
    name: str
    description: str

    # 规模与角色
    scale: UnitScale = UnitScale.SQUAD
    role: CombatRole = CombatRole.ASSAULT

    # 基础属性
    base_health: int = 100
    base_energy: int = 50
    base_attack: int = 20
    base_defense: int = 10
    base_speed: int = 5
    base_evasion: int = 10

    # 移动
    move_range: int = 3
    move_type: str = "ground"  # ground / air / naval / space

    # 特殊能力
    can_use_compromise: bool = False  # 是否能使用物理妥协
    compromise_affinity: str = "none"  # 妥协亲和维度

    # 修正
    stat_modifier: StatModifier = None

    def __post_init__(self):
        if self.stat_modifier is None:
            self.stat_modifier = StatModifier()

    def get_max_health(self) -> int:
        return self.base_health + self.stat_modifier.health

    def get_max_energy(self) -> int:
        return self.base_energy + self.stat_modifier.energy


# ==================== 预设职业 ====================

def create_infantry_class() -> CharacterClassSO:
    """创建基础步兵职业"""
    return CharacterClassSO(
        id="class_infantry",
        name="步兵",
        description="最基础的战斗单位，平衡型，可适应各种战场",
        scale=UnitScale.SQUAD,
        role=CombatRole.ASSAULT,
        base_health=100,
        base_energy=50,
        base_attack=20,
        base_defense=15,
        base_speed=5,
        base_evasion=10,
        move_range=3,
        move_type="ground",
        can_use_compromise=False,
    )


def create_assault_class() -> CharacterClassSO:
    """创建突击手职业（可使用物理妥协）"""
    return CharacterClassSO(
        id="class_assault",
        name="突击手",
        description="高机动性近战单位，可使用重力妥协能力",
        scale=UnitScale.SQUAD,
        role=CombatRole.ASSAULT,
        base_health=80,
        base_energy=100,
        base_attack=30,
        base_defense=8,
        base_speed=8,
        base_evasion=15,
        move_range=5,
        move_type="ground",
        can_use_compromise=True,
        compromise_affinity="gravity",
        stat_modifier=StatModifier(health=-10, energy=30, attack=10, evasion=5),
    )


def create_commander_class() -> CharacterClassSO:
    """创建指挥官职业"""
    return CharacterClassSO(
        id="class_commander",
        name="指挥官",
        description="指挥协调型单位，可为友军提供增益，降低敌方效率",
        scale=UnitScale.SOLO,
        role=CombatRole.COMMAND,
        base_health=120,
        base_energy=80,
        base_attack=10,
        base_defense=20,
        base_speed=3,
        base_evasion=5,
        move_range=2,
        move_type="ground",
        can_use_compromise=False,
    )


def create_recon_class() -> CharacterClassSO:
    """创建侦察兵职业"""
    return CharacterClassSO(
        id="class_recon",
        name="侦察兵",
        description="高机动侦查单位，视野开阔，可探测隐匿目标",
        scale=UnitScale.SOLO,
        role=CombatRole.RECON,
        base_health=60,
        base_energy=70,
        base_attack=15,
        base_defense=5,
        base_speed=10,
        base_evasion=25,
        move_range=6,
        move_type="air",
        can_use_compromise=False,
    )


def create_psychic_class() -> CharacterClassSO:
    """创建念动师职业（物理妥协专精）"""
    return CharacterClassSO(
        id="class_psychic",
        name="念动师",
        description="可使用时空妥协能力的特殊单位，高风险高回报",
        scale=UnitScale.SOLO,
        role=CombatRole.SPECIAL,
        base_health=50,
        base_energy=150,
        base_attack=35,
        base_defense=3,
        base_speed=4,
        base_evasion=8,
        move_range=3,
        move_type="ground",
        can_use_compromise=True,
        compromise_affinity="spacetime",
        stat_modifier=StatModifier(health=-20, energy=60, attack=15, defense=-5),
    )
