"""
舰队数据
Fleet - 对应 Unity 的 FleetPrefab
"""

from dataclasses import dataclass, field
from typing import List, Optional
from data.unit_data import CombatUnitDataSO


@dataclass
class Fleet:
    """舰队（多个单位组成的队伍）"""
    id: str
    name: str

    # 组成单位
    units: List[CombatUnitDataSO] = field(default_factory=list)

    # 位置（当前所在节点ID）
    current_node_id: Optional[str] = None
    # 地图坐标（用于渲染）
    map_x: float = 0.0
    map_y: float = 0.0

    # 队伍
    team: str = "player"  # player / enemy / neutral

    # 状态
    is_selected: bool = False
    has_acted: bool = False  # 本回合是否已行动

    # 移动路径（用于动画）
    path: List[str] = field(default_factory=list)  # 节点ID列表

    @property
    def total_health(self) -> int:
        return sum(u.health for u in self.units)

    @property
    def total_max_health(self) -> int:
        return sum(u.max_health for u in self.units)

    @property
    def is_alive(self) -> bool:
        return all(u.is_alive() for u in self.units)

    def add_unit(self, unit: CombatUnitDataSO):
        self.units.append(unit)

    def get_status_summary(self) -> str:
        alive = [u for u in self.units if u.is_alive()]
        return (
            f"[{self.name}] 单位数: {len(alive)}/{len(self.units)} "
            f"总HP: {self.total_health}/{self.total_max_health} "
            f"位置: 节点{self.current_node_id}"
        )

    def move_to(self, node_id: str, path: List[str]):
        """移动到目标节点"""
        self.current_node_id = node_id
        self.path = path
        self.has_acted = True

    def reset_turn(self):
        """重置回合状态"""
        self.has_acted = False


# ==================== 预设舰队 ====================

def create_player_fleet(start_node: str = "node_0") -> Fleet:
    """创建玩家初始舰队"""
    from data.unit_data import create_test_ally_unit, create_commander_unit
    from data.character_class import create_assault_class, create_recon_class, create_psychic_class
    from data.skill_data import create_gravity_nullify, create_basic_attack, create_time_slow

    commander = create_commander_unit()
    infantry = create_test_ally_unit()
    infantry.name = "步兵班"
    infantry.map_x = 0
    infantry.map_y = 0

    assault = CombatUnitDataSO(
        id="ally_assault_01",
        name="重力突击组",
        description="可使用重力妥协能力的突击单位",
        character_class=create_assault_class(),
        team="player",
        health=80,
        max_health=80,
        map_x=0,
        map_y=0,
        skills=[create_basic_attack(), create_gravity_nullify()],
    )

    psychic = CombatUnitDataSO(
        id="ally_psychic_01",
        name="时空念动师",
        description="可使用时空妥协能力的特殊单位",
        character_class=create_psychic_class(),
        team="player",
        health=50,
        max_health=50,
        map_x=0,
        map_y=0,
        skills=[create_basic_attack(), create_time_slow()],
    )

    fleet = Fleet(
        id="player_fleet_main",
        name="主力舰队",
        units=[commander, infantry, assault, psychic],
        current_node_id=start_node,
        team="player",
    )
    return fleet


def create_enemy_fleet(start_node: str = "node_3") -> Fleet:
    """创建敌军舰队"""
    from data.unit_data import create_test_enemy_unit
    from data.character_class import create_assault_class
    from data.skill_data import create_basic_attack, create_gravity_nullify

    enemy1 = create_test_enemy_unit()
    enemy2 = CombatUnitDataSO(
        id="enemy_assault_02",
        name="敌军重力组",
        description="敌方突击单位",
        character_class=create_assault_class(),
        team="enemy",
        health=80,
        max_health=80,
        map_x=0,
        map_y=0,
        skills=[create_basic_attack(), create_gravity_nullify()],
    )

    fleet = Fleet(
        id="enemy_fleet_01",
        name="敌军先遣队",
        units=[enemy1, enemy2],
        current_node_id=start_node,
        team="enemy",
    )
    return fleet
