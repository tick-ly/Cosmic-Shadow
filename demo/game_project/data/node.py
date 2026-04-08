"""
星系/战区节点数据
StarNode - 对应 Unity 的 NodePrefab
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class NodeType(Enum):
    """节点类型"""
    NORMAL = "普通"         # 普通节点
    STRATEGIC = "战略"      # 战略要地
    RESOURCE = "资源"        # 资源节点
    DANGER = "危险"         # 高危节点（死区/死星）
    JUMP_GATE = "跳跃门"    # 可跳转的星门
    HOME_BASE = "基地"      # 起始基地


class DebtLevel(Enum):
    """现实债务浓度"""
    SAFE = (0, "安全", (76, 175, 80))         # 绿色
    MODERATE = (1, "警戒", (255, 193, 7))    # 黄色
    HIGH = (2, "危险", (255, 152, 0))         # 橙色
    CRITICAL = (3, "临界", (244, 67, 54))   # 红色
    DEAD_ZONE = (4, "死区", (30, 30, 40))     # 黑色

    def __init__(self, level: int, label: str, color: tuple):
        self.level = level
        self.label = label
        self.color = color


@dataclass
class StarNode:
    """星系/战区节点"""
    id: str
    name: str

    # 地图位置（像素坐标）
    x: float
    y: float

    # 连接节点
    connections: List[str] = field(default_factory=list)  # 连接的节点ID列表

    # 节点属性
    node_type: NodeType = NodeType.NORMAL

    # 现实债务
    reality_debt: int = 0       # 当前债务浓度 0-1000
    debt_level: DebtLevel = DebtLevel.SAFE

    # 状态
    is_explored: bool = False
    is_selected: bool = False

    # 占领状态
    owner: str = "neutral"  # player / enemy / neutral

    # 驻军
    garrison_strength: int = 0  # 驻军强度（敌军）

    def update_debt_level(self):
        """根据债务值更新等级"""
        if self.reality_debt < 200:
            self.debt_level = DebtLevel.SAFE
        elif self.reality_debt < 400:
            self.debt_level = DebtLevel.MODERATE
        elif self.reality_debt < 600:
            self.debt_level = DebtLevel.HIGH
        elif self.reality_debt < 800:
            self.debt_level = DebtLevel.CRITICAL
        else:
            self.debt_level = DebtLevel.DEAD_ZONE

    def get_color(self) -> tuple:
        """获取渲染颜色"""
        return self.debt_level.color

    def is_passable(self) -> bool:
        """是否可通过（死区不可通过）"""
        return self.debt_level != DebtLevel.DEAD_ZONE


# ==================== 预设星图 ====================

def create_test_star_map() -> List[StarNode]:
    """创建测试星图"""
    nodes = [
        # 第一排（上方）
        StarNode("node_0", "卢安星区", x=150, y=150, node_type=NodeType.HOME_BASE,
                 owner="player", reality_debt=50, connections=["node_1", "node_3"]),
        StarNode("node_1", "γ-7中转站", x=400, y=120, node_type=NodeType.STRATEGIC,
                 reality_debt=180, connections=["node_0", "node_2", "node_4"]),
        StarNode("node_2", "卡西米尔域", x=650, y=160, node_type=NodeType.DANGER,
                 reality_debt=650, connections=["node_1", "node_5"]),

        # 第二排（中间）
        StarNode("node_3", "Ω-3前哨", x=250, y=320, node_type=NodeType.RESOURCE,
                 reality_debt=120, connections=["node_0", "node_1", "node_4", "node_6"]),
        StarNode("node_4", "量子中继站", x=480, y=300, node_type=NodeType.JUMP_GATE,
                 reality_debt=300, connections=["node_1", "node_3", "node_5", "node_7"]),
        StarNode("node_5", "深渊之门", x=720, y=340, node_type=NodeType.DANGER,
                 reality_debt=820, connections=["node_2", "node_4", "node_8"]),

        # 第三排（下方）
        StarNode("node_6", "边缘殖民地", x=180, y=480, node_type=NodeType.NORMAL,
                 reality_debt=200, connections=["node_3", "node_7"]),
        StarNode("node_7", "Σ-9贸易站", x=420, y=500, node_type=NodeType.RESOURCE,
                 owner="enemy", garrison_strength=50, reality_debt=280,
                 connections=["node_4", "node_6", "node_8"]),
        StarNode("node_8", "敌军主星", x=680, y=520, node_type=NodeType.STRATEGIC,
                 owner="enemy", garrison_strength=100, reality_debt=450,
                 connections=["node_5", "node_7"]),
    ]

    for node in nodes:
        node.update_debt_level()
        if node.owner != "neutral":
            node.is_explored = True

    return nodes


def get_node_by_id(nodes: List[StarNode], node_id: str) -> Optional[StarNode]:
    """根据ID查找节点"""
    for node in nodes:
        if node.id == node_id:
            return node
    return None
