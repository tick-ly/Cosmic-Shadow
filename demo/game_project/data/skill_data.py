"""
技能数据
SkillData - 对应 Unity 的 SkillDataSO
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class SkillType(Enum):
    """技能类型"""
    ATTACK = "攻击"           # 攻击技能
    DEFENSE = "防御"         # 防御技能
    SUPPORT = "支援"         # 支援技能
    PHYSICS_COMPROMISE = "物理妥协"  # 物理妥协技能（核心特色）


class SkillTarget(Enum):
    """技能目标"""
    SELF = "自身"
    SINGLE_ENEMY = "单体敌人"
    ALL_ENEMIES = "全体敌人"
    SINGLE_ALLY = "单体友军"
    ALL_ALLIES = "全体友军"
    AREA = "区域"


class CompromiseDimension(Enum):
    """妥协维度（物理法则向哪个方向妥协）"""
    NONE = "无"
    GRAVITY = "重力"         # 重力削弱/消除
    ELECTROMAGNETISM = "电磁" # 电磁力修改
    NUCLEAR_FORCE = "核力"   # 强力/弱力修改
    THERMODYNAMICS = "热力学" # 温度/能量守恒打破
    SPACETIME = "时空"        # 空间/时间操控
    CAUSALITY = "因果"        # 因果律修改


@dataclass
class RealityDebtCost:
    """现实债务代价"""
    min_cost: int = 10      # 最低代价
    max_cost: int = 30      # 最高代价
    base_success_rate: float = 0.85  # 基础成功率


@dataclass
class SkillData:
    """技能数据"""
    id: str
    name: str
    description: str
    skill_type: SkillType
    target: SkillTarget

    # 能力参数
    power: int = 10          # 技能强度
    range_val: int = 3      # 范围（格数）
    cooldown: int = 1       # 冷却回合
    current_cooldown: int = 0

    # 物理妥协相关
    compromise_dimension: CompromiseDimension = CompromiseDimension.NONE
    debt_cost: RealityDebtCost = field(default_factory=RealityDebtCost)
    backlash_risk: float = 0.1  # 反噬风险 (0-1)

    # 视觉效果（预留）
    icon: str = ""

    def use(self) -> bool:
        """使用技能，返回是否成功（是否进入冷却）"""
        if self.current_cooldown > 0:
            return False
        self.current_cooldown = self.cooldown
        return True

    def update_cooldown(self):
        """更新冷却"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def can_use(self, current_debt: int, max_debt: int = 1000) -> bool:
        """检查技能是否可用"""
        if self.current_cooldown > 0:
            return False
        if self.debt_cost.min_cost + current_debt > max_debt:
            return False
        return True


# ==================== 预设技能 ====================

def create_basic_attack() -> SkillData:
    """创建基础攻击技能"""
    return SkillData(
        id="skill_basic_attack",
        name="基础攻击",
        description="标准的物理攻击，无特殊效果",
        skill_type=SkillType.ATTACK,
        target=SkillTarget.SINGLE_ENEMY,
        power=15,
        range_val=1,
        cooldown=0,
        compromise_dimension=CompromiseDimension.NONE,
        debt_cost=RealityDebtCost(min_cost=0, max_cost=0, base_success_rate=1.0),
        backlash_risk=0.0,
        icon="⚔"
    )


def create_gravity_nullify() -> SkillData:
    """创建重力消除技能（物理妥协）"""
    return SkillData(
        id="skill_gravity_nullify",
        name="重力消除",
        description="在局部空间内消除重力法则，物体失去重量，可使重装单位漂浮",
        skill_type=SkillType.PHYSICS_COMPROMISE,
        target=SkillTarget.SINGLE_ENEMY,
        power=20,
        range_val=2,
        cooldown=2,
        compromise_dimension=CompromiseDimension.GRAVITY,
        debt_cost=RealityDebtCost(min_cost=15, max_cost=40, base_success_rate=0.75),
        backlash_risk=0.15,
        icon="⬇"
    )


def create_time_slow() -> SkillData:
    """创建时间减缓技能（物理妥协）"""
    return SkillData(
        id="skill_time_slow",
        name="时间减缓",
        description="减缓目标区域的时间流速，敌方行动延迟，我方获得战术优势",
        skill_type=SkillType.PHYSICS_COMPROMISE,
        target=SkillTarget.AREA,
        power=25,
        range_val=3,
        cooldown=3,
        compromise_dimension=CompromiseDimension.SPACETIME,
        debt_cost=RealityDebtCost(min_cost=30, max_cost=60, base_success_rate=0.65),
        backlash_risk=0.20,
        icon="⏱"
    )


def create_reality_anchor() -> SkillData:
    """创建现实锚定技能"""
    return SkillData(
        id="skill_reality_anchor",
        name="现实锚定",
        description="将自身锚定在现实维度，抵抗现实债务的扭曲效果",
        skill_type=SkillType.DEFENSE,
        target=SkillTarget.SELF,
        power=0,
        range_val=0,
        cooldown=4,
        compromise_dimension=CompromiseDimension.NONE,
        debt_cost=RealityDebtCost(min_cost=10, max_cost=25, base_success_rate=0.90),
        backlash_risk=0.05,
        icon="⚓"
    )
