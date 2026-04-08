"""
数据模块
Data - 对应 Unity 的 ScriptableObject 资产
"""

from data.skill_data import (
    SkillData, SkillType, SkillTarget, CompromiseDimension,
    RealityDebtCost,
    create_basic_attack, create_gravity_nullify,
    create_time_slow, create_reality_anchor,
)
from data.character_class import (
    CharacterClassSO, UnitScale, CombatRole, StatModifier,
    create_infantry_class, create_assault_class,
    create_commander_class, create_recon_class, create_psychic_class,
)
from data.unit_data import (
    CombatUnitDataSO,
    create_test_ally_unit, create_test_enemy_unit, create_commander_unit,
)
from data.fleet import (
    Fleet,
    create_player_fleet, create_enemy_fleet,
)
from data.node import (
    StarNode, NodeType, DebtLevel,
    create_test_star_map, get_node_by_id,
)

__all__ = [
    # skill_data
    "SkillData", "SkillType", "SkillTarget", "CompromiseDimension", "RealityDebtCost",
    "create_basic_attack", "create_gravity_nullify", "create_time_slow", "create_reality_anchor",
    # character_class
    "CharacterClassSO", "UnitScale", "CombatRole", "StatModifier",
    "create_infantry_class", "create_assault_class",
    "create_commander_class", "create_recon_class", "create_psychic_class",
    # unit_data
    "CombatUnitDataSO",
    "create_test_ally_unit", "create_test_enemy_unit", "create_commander_unit",
    # fleet
    "Fleet",
    "create_player_fleet", "create_enemy_fleet",
    # node
    "StarNode", "NodeType", "DebtLevel",
    "create_test_star_map", "get_node_by_id",
]
