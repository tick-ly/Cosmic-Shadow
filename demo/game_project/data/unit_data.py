"""
战斗单位数据
CombatUnitDataSO - 对应 Unity 的 CombatUnitDataSO
"""

from dataclasses import dataclass, field
from typing import List, Optional
from data.character_class import CharacterClassSO, create_infantry_class, create_assault_class
from data.skill_data import SkillData, create_basic_attack


@dataclass
class CombatUnitDataSO:
    """战斗单位数据"""
    id: str
    name: str
    description: str

    # 职业
    character_class: CharacterClassSO = field(default_factory=create_infantry_class)

    # 技能列表
    skills: List[SkillData] = field(default_factory=list)

    # 队伍归属
    team: str = "player"   # player / enemy / neutral

    # 状态
    health: int = 100
    max_health: int = 100
    energy: int = 50
    max_energy: int = 50

    # 位置（在地图上的位置）
    map_x: int = 0
    map_y: int = 0

    # 现实债务（超能力单位特有）
    reality_debt: int = 0

    def is_alive(self) -> bool:
        return self.health > 0

    def take_damage(self, damage: int) -> int:
        """受到伤害，返回实际伤害"""
        actual = max(0, damage - self.character_class.base_defense)
        self.health = max(0, self.health - actual)
        return actual

    def heal(self, amount: int) -> int:
        """治疗，返回实际治疗量"""
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        return self.health - old_health

    def use_skill(self, skill_index: int) -> bool:
        """使用技能"""
        if 0 <= skill_index < len(self.skills):
            skill = self.skills[skill_index]
            if skill.can_use(self.reality_debt):
                skill.use()
                return True
        return False

    def get_status_summary(self) -> str:
        health_pct = self.health / self.max_health if self.max_health > 0 else 0
        return (
            f"[{self.name}] {self.character_class.name} "
            f"HP: {self.health}/{self.max_health} (${health_pct * 100:.0f}%) "
            f"Debt: {self.reality_debt}"
        )


# ==================== 预设单位 ====================

def create_test_ally_unit() -> CombatUnitDataSO:
    """创建测试友军单位"""
    unit = CombatUnitDataSO(
        id="ally_infantry_01",
        name="友军步兵小队",
        description="测试用友军步兵单位",
        character_class=create_infantry_class(),
        team="player",
        health=100,
        max_health=100,
        energy=50,
        max_energy=50,
        map_x=5,
        map_y=10,
        skills=[create_basic_attack()],
    )
    return unit


def create_test_enemy_unit() -> CombatUnitDataSO:
    """创建测试敌军单位"""
    unit = CombatUnitDataSO(
        id="enemy_assault_01",
        name="敌军突击小队",
        description="测试用敌军突击单位",
        character_class=create_assault_class(),
        team="enemy",
        health=80,
        max_health=80,
        energy=100,
        max_energy=100,
        map_x=15,
        map_y=10,
        skills=[create_basic_attack()],
    )
    return unit


def create_commander_unit() -> CombatUnitDataSO:
    """创建指挥官单位"""
    from data.character_class import create_commander_class
    from data.skill_data import create_reality_anchor
    unit = CombatUnitDataSO(
        id="player_commander_01",
        name="指挥官",
        description="玩家指挥官单位",
        character_class=create_commander_class(),
        team="player",
        health=120,
        max_health=120,
        energy=80,
        max_energy=80,
        map_x=3,
        map_y=10,
        skills=[create_basic_attack(), create_reality_anchor()],
    )
    return unit
