# -*- coding: utf-8 -*-
"""
宇宙之影 - 战场地形系统
Terrain System for Modern Warfare Combat
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import random

class TerrainType(Enum):
    """地形类型"""
    PLAINS = "平原"           # 开阔地形
    MOUNTAIN = "山地"         # 高地优势
    JUNGLE = "丛林"           # 隐蔽但视野受限
    URBAN = "城市"            # 复杂建筑
    DESERT = "沙漠"           # 极端环境
    SNOW = "雪地"             # 寒冷环境
    SWAMP = "沼泽"            # 通行困难
    COASTAL = "海岸"          # 登陆作战
    SPACE_STATION = "太空站"   # 科幻地形
    ORBITAL = "轨道"          # 轨道作战区

class WeatherCondition(Enum):
    """天气状况"""
    CLEAR = "晴朗"
    RAINY = "下雨"
    STORMY = "暴风雨"
    FOGGY = "大雾"
    NIGHT = "夜间"
    SANDSTORM = "沙尘暴"
    SNOWSTORM = "暴风雪"
    SPACE_VOID = "真空"

@dataclass
class TerrainModifier:
    """地形修正值"""
    defense_bonus: int = 0        # 防御加成（百分比）
    speed_penalty: int = 0         # 速度惩罚（百分比）
    detection_penalty: int = 0     # 侦查范围惩罚（百分比）
    accuracy_penalty: int = 0      # 精度惩罚（百分比）
    communication_penalty: int = 0  # 通讯效率惩罚（百分比）
    armor_bonus: int = 0           # 装甲加成
    stealth_bonus: int = 0         # 隐蔽加成
    morale_modifier: int = 0       # 士气修正

@dataclass
class Terrain:
    """地形定义"""
    terrain_type: TerrainType
    name: str
    description: str
    modifiers: TerrainModifier
    movement_cost: int            # 移动消耗（行动点数）
    sight_range_modifier: float   # 视野范围修正
    cover_effectiveness: float    # 掩体效果（0-1）
    can_fortify: bool = False     # 是否可以筑防
    special_abilities: List[str] = None

    def __post_init__(self):
        if self.special_abilities is None:
            self.special_abilities = []

class BattlefieldZone:
    """战场区域"""
    def __init__(self, name: str, terrain: Terrain, position: Tuple[int, int]):
        self.name = name
        self.terrain = terrain
        self.position = position  # (x, y) 坐标
        self.occupying_units: List[str] = []  # 单位名称列表
        self.fortification_level: int = 0  # 筑防等级 0-3
        self.is_contested: bool = False    # 是否被争夺
        self.last_controlled_by: str = None  # 上次控制方

    def apply_terrain_modifiers(self, unit) -> Dict:
        """应用地形修正到单位"""
        mods = self.terrain.modifiers
        result = {
            "defense_bonus": mods.defense_bonus,
            "speed_penalty": mods.speed_penalty,
            "detection_penalty": mods.detection_penalty,
            "accuracy_penalty": mods.accuracy_penalty,
            "communication_penalty": mods.communication_penalty,
            "stealth_bonus": mods.stealth_bonus
        }

        # 筑防加成
        if self.fortification_level > 0:
            fort_bonus = self.fortification_level * 15
            result["defense_bonus"] += fort_bonus
            result["stealth_bonus"] += fort_bonus // 2

        # 争夺状态惩罚
        if self.is_contested:
            result["morale_penalty"] = 20
        else:
            result["morale_penalty"] = 0

        return result

    def get_cover_bonus(self) -> float:
        """获取掩体加成"""
        base_cover = self.terrain.cover_effectiveness
        fort_bonus = self.fortification_level * 0.1
        return min(0.8, base_cover + fort_bonus)

    def fortify(self, level: int = 1):
        """筑防"""
        if self.terrain.can_fortify:
            self.fortification_level = min(3, self.fortification_level + level)
            return True
        return False

class Battlefield:
    """战场"""
    def __init__(self, name: str, width: int = 1000, height: int = 1000):
        self.name = name
        self.width = width
        self.height = height
        self.zones: Dict[str, BattlefieldZone] = {}
        self.weather = WeatherCondition.CLEAR
        self.turn_count = 0
        self.control_points: Dict[str, str] = {}  # 区域控制状态

        # 创建默认区域
        self._create_default_zones()

    def _create_default_zones(self):
        """创建默认区域布局"""
        zone_configs = [
            ("A1", TerrainType.PLAINS, "开阔平原", (0, 0)),
            ("A2", TerrainType.MOUNTAIN, "北部山地", (0, 1)),
            ("B1", TerrainType.URBAN, "城市废墟", (1, 0)),
            ("B2", TerrainType.JUNGLE, "密林地带", (1, 1)),
            ("C1", TerrainType.DESERT, "沙漠戈壁", (2, 0)),
            ("C2", TerrainType.SWAMP, "湿地沼泽", (2, 1)),
            ("D1", TerrainType.COASTAL, "海岸线", (3, 0)),
            ("D2", TerrainType.SNOW, "冰封高原", (3, 1)),
        ]

        for zone_id, terrain_type, name, pos in zone_configs:
            terrain = TERRAIN_REGISTRY.get(terrain_type)
            if terrain:
                zone = BattlefieldZone(name, terrain, pos)
                self.zones[zone_id] = zone

    def get_zone(self, zone_id: str) -> Optional[BattlefieldZone]:
        """获取区域"""
        return self.zones.get(zone_id)

    def get_all_zones(self) -> List[BattlefieldZone]:
        """获取所有区域"""
        return list(self.zones.values())

    def set_weather(self, weather: WeatherCondition):
        """设置天气"""
        old_weather = self.weather
        self.weather = weather
        return old_weather

    def update_weather(self):
        """更新天气（回合结束时）"""
        weather_transitions = {
            WeatherCondition.CLEAR: [WeatherCondition.RAINY, WeatherCondition.FOGGY],
            WeatherCondition.RAINY: [WeatherCondition.STORMY, WeatherCondition.CLEAR],
            WeatherCondition.FOGGY: [WeatherCondition.CLEAR, WeatherCondition.RAINY],
            WeatherCondition.STORMY: [WeatherCondition.RAINY, WeatherCondition.CLEAR],
            WeatherCondition.SANDSTORM: [WeatherCondition.CLEAR],
            WeatherCondition.SNOWSTORM: [WeatherCondition.SNOW, WeatherCondition.CLEAR],
            WeatherCondition.NIGHT: [WeatherCondition.CLEAR],
            WeatherCondition.SPACE_VOID: [WeatherCondition.SPACE_VOID],
        }

        possible_weathers = weather_transitions.get(self.weather, [self.weather])
        self.weather = random.choice(possible_weathers)

    def get_weather_modifiers(self) -> Dict:
        """获取天气修正"""
        weather_effects = {
            WeatherCondition.CLEAR: {
                "detection": 0, "accuracy": 0, "speed": 0, "communication": 0
            },
            WeatherCondition.RAINY: {
                "detection": -20, "accuracy": -10, "speed": -10, "communication": -15
            },
            WeatherCondition.STORMY: {
                "detection": -40, "accuracy": -25, "speed": -30, "communication": -35
            },
            WeatherCondition.FOGGY: {
                "detection": -50, "accuracy": -15, "speed": -5, "communication": -10
            },
            WeatherCondition.NIGHT: {
                "detection": -30, "accuracy": -20, "speed": 0, "communication": -5
            },
            WeatherCondition.SANDSTORM: {
                "detection": -60, "accuracy": -30, "speed": -40, "communication": -40
            },
            WeatherCondition.SNOWSTORM: {
                "detection": -50, "accuracy": -25, "speed": -35, "communication": -30
            },
            WeatherCondition.SPACE_VOID: {
                "detection": 20, "accuracy": 10, "speed": 0, "communication": -50
            },
        }
        return weather_effects.get(self.weather, weather_effects[WeatherCondition.CLEAR])

    def check_zone_control(self) -> Dict[str, int]:
        """检查区域控制状态"""
        control = {}
        for zone_id, zone in self.zones.items():
            if zone.occupying_units:
                # 简单计数逻辑
                control[zone_id] = len(zone.occupying_units)
        return control

    def get_zone_distance(self, zone1: str, zone2: str) -> int:
        """计算区域间距离（米）"""
        z1 = self.zones.get(zone1)
        z2 = self.zones.get(zone2)
        if not z1 or not z2:
            return 1000

        dx = z1.position[0] - z2.position[0]
        dy = z1.position[1] - z2.position[1]
        return int((dx**2 + dy**2)**0.5 * 250)  # 每格约250米

class TerrainSystem:
    """地形系统管理器"""

    def __init__(self):
        self.terrains = TERRAIN_REGISTRY
        self.active_battlefields: Dict[str, Battlefield] = {}

    def create_battlefield(self, name: str, terrain_config: Dict[str, TerrainType] = None) -> Battlefield:
        """创建战场"""
        battlefield = Battlefield(name)
        self.active_battlefields[name] = battlefield
        return battlefield

    def apply_terrain_to_unit(self, unit, zone: BattlefieldZone) -> Dict:
        """应用地形效果到单位"""
        base_mods = zone.apply_terrain_modifiers(unit)

        # 地形对不同规模单位的影响不同
        scale_effects = {
            "INDIVIDUAL": {"speed_penalty": 1.5, "stealth_bonus": 1.5},
            "SQUAD": {"speed_penalty": 1.2, "stealth_bonus": 1.2},
            "LEGION": {"speed_penalty": 1.0, "stealth_bonus": 0.5}
        }

        unit_scale = str(unit.scale).split('.')[-1] if hasattr(unit.scale, 'value') else "INDIVIDUAL"
        scale_mod = scale_effects.get(unit_scale, scale_effects["INDIVIDUAL"])

        # 调整修正值
        result = {}
        for key, value in base_mods.items():
            if key in scale_mod:
                result[key] = int(value * scale_mod[key])
            else:
                result[key] = value

        return result

    def calculate_terrain_defense(self, unit, zone: BattlefieldZone) -> int:
        """计算地形防御加成"""
        mods = zone.apply_terrain_modifiers(unit)
        base_armor = unit.base_armor

        defense_bonus = mods.get("defense_bonus", 0)
        armor_bonus = zone.terrain.modifiers.armor_bonus
        cover = zone.get_cover_bonus()

        total_defense = base_armor + armor_bonus + int(base_armor * (defense_bonus + cover * 50) / 100)
        return total_defense

    def can_unit_move_to_zone(self, unit, from_zone: BattlefieldZone, to_zone: BattlefieldZone) -> bool:
        """检查单位是否可以移动到区域"""
        move_cost = to_zone.terrain.movement_cost
        speed = unit.mobility

        # 速度不足
        if speed < move_cost * 10:
            return False

        # 特殊地形限制
        terrain_type = to_zone.terrain.terrain_type
        unit_scale = str(unit.scale).split('.')[-1] if hasattr(unit.scale, 'value') else "INDIVIDUAL"

        # 大型单位限制
        if unit_scale == "LEGION" and terrain_type in [TerrainType.SWAMP, TerrainType.JUNGLE]:
            return False

        return True

    def get_terrain_advantage(self, attacker_zone: BattlefieldZone, defender_zone: BattlefieldZone) -> Dict:
        """获取地形优势分析"""
        attacker_mods = attacker_zone.terrain.modifiers
        defender_mods = defender_zone.terrain.modifiers

        advantage = {
            "attacker_bonus": attacker_mods.stealth_bonus,
            "defender_bonus": defender_mods.defense_bonus + defender_mods.armor_bonus,
            "defender_cover": defender_zone.get_cover_bonus() * 100,
            "recommendation": ""
        }

        net_bonus = advantage["defender_bonus"] - advantage["attacker_bonus"]
        if net_bonus > 20:
            advantage["recommendation"] = "防守方地形优势明显，建议包围或诱敌"
        elif net_bonus < -20:
            advantage["recommendation"] = "进攻方地形有利，可发起强攻"
        else:
            advantage["recommendation"] = "双方地形条件相当，正面交战可行"

        return advantage

# ==================== 地形注册表 ====================

TERRAIN_REGISTRY = {
    # 平原 - 开阔地形，无特殊加成/惩罚
    TerrainType.PLAINS: Terrain(
        terrain_type=TerrainType.PLAINS,
        name="开阔平原",
        description="平坦开阔的地形，视野良好，适合大规模装甲集群推进",
        modifiers=TerrainModifier(
            defense_bonus=0,
            speed_penalty=0,
            detection_penalty=0,
            accuracy_penalty=0,
            communication_penalty=0,
            armor_bonus=0,
            stealth_bonus=0,
            morale_modifier=0
        ),
        movement_cost=1,
        sight_range_modifier=1.2,
        cover_effectiveness=0.1,
        can_fortify=True,
        special_abilities=["装甲冲锋", "大规模集结"]
    ),

    # 山地 - 高地优势，防御强但机动差
    TerrainType.MOUNTAIN: Terrain(
        terrain_type=TerrainType.MOUNTAIN,
        name="北部山地",
        description="崎岖山地，提供天然高度优势和良好掩体，但机动困难",
        modifiers=TerrainModifier(
            defense_bonus=25,
            speed_penalty=40,
            detection_penalty=-10,
            accuracy_penalty=-5,
            communication_penalty=-20,
            armor_bonus=15,
            stealth_bonus=20,
            morale_modifier=10
        ),
        movement_cost=3,
        sight_range_modifier=1.5,
        cover_effectiveness=0.5,
        can_fortify=True,
        special_abilities=["高地视野", "居高临下"]
    ),

    # 丛林 - 隐蔽好但视野差
    TerrainType.JUNGLE: Terrain(
        terrain_type=TerrainType.JUNGLE,
        name="密林地带",
        description="茂密丛林，提供极佳隐蔽，但视野受限，不适合重装单位",
        modifiers=TerrainModifier(
            defense_bonus=15,
            speed_penalty=35,
            detection_penalty=-40,
            accuracy_penalty=-25,
            communication_penalty=-30,
            armor_bonus=0,
            stealth_bonus=40,
            morale_modifier=-5
        ),
        movement_cost=3,
        sight_range_modifier=0.4,
        cover_effectiveness=0.6,
        can_fortify=False,
        special_abilities=["丛林伏击", "渗透作战"]
    ),

    # 城市 - 复杂环境
    TerrainType.URBAN: Terrain(
        terrain_type=TerrainType.URBAN,
        name="城市废墟",
        description="破碎的城市建筑群，建筑提供掩体，但视野受限，需要清理",
        modifiers=TerrainModifier(
            defense_bonus=20,
            speed_penalty=50,
            detection_penalty=-30,
            accuracy_penalty=-15,
            communication_penalty=-25,
            armor_bonus=10,
            stealth_bonus=25,
            morale_modifier=-10
        ),
        movement_cost=4,
        sight_range_modifier=0.5,
        cover_effectiveness=0.7,
        can_fortify=True,
        special_abilities=["建筑巷战", "逐屋争夺", "狙击点位"]
    ),

    # 沙漠 - 极端环境
    TerrainType.DESERT: Terrain(
        terrain_type=TerrainType.DESERT,
        name="沙漠戈壁",
        description="炎热沙漠，视野开阔但通行困难，补给消耗大",
        modifiers=TerrainModifier(
            defense_bonus=5,
            speed_penalty=25,
            detection_penalty=10,
            accuracy_penalty=-10,
            communication_penalty=-15,
            armor_bonus=0,
            stealth_bonus=-20,
            morale_modifier=-15
        ),
        movement_cost=2,
        sight_range_modifier=1.3,
        cover_effectiveness=0.05,
        can_fortify=False,
        special_abilities=["沙尘隐蔽", "热成像干扰"]
    ),

    # 雪地 - 寒冷环境
    TerrainType.SNOW: Terrain(
        terrain_type=TerrainType.SNOW,
        name="冰封高原",
        description="寒冷冰雪地形，机动受限，装备效率下降",
        modifiers=TerrainModifier(
            defense_bonus=10,
            speed_penalty=35,
            detection_penalty=-15,
            accuracy_penalty=-20,
            communication_penalty=-10,
            armor_bonus=5,
            stealth_bonus=15,
            morale_modifier=-5
        ),
        movement_cost=3,
        sight_range_modifier=1.1,
        cover_effectiveness=0.3,
        can_fortify=True,
        special_abilities=["冰雪伪装", "极地作战"]
    ),

    # 沼泽 - 通行极难
    TerrainType.SWAMP: Terrain(
        terrain_type=TerrainType.SWAMP,
        name="湿地沼泽",
        description="泥泞沼泽，严重限制机动，但提供良好隐蔽",
        modifiers=TerrainModifier(
            defense_bonus=20,
            speed_penalty=60,
            detection_penalty=-35,
            accuracy_penalty=-20,
            communication_penalty=-25,
            armor_bonus=0,
            stealth_bonus=35,
            morale_modifier=-20
        ),
        movement_cost=5,
        sight_range_modifier=0.5,
        cover_effectiveness=0.4,
        can_fortify=False,
        special_abilities=["伏击圣地", "毒气区域"]
    ),

    # 海岸 - 两栖作战
    TerrainType.COASTAL: Terrain(
        terrain_type=TerrainType.COASTAL,
        name="海岸线",
        description="海滩地形，登陆作战区，暴露风险高",
        modifiers=TerrainModifier(
            defense_bonus=-10,
            speed_penalty=20,
            detection_penalty=0,
            accuracy_penalty=-5,
            communication_penalty=-10,
            armor_bonus=-5,
            stealth_bonus=-10,
            morale_modifier=5
        ),
        movement_cost=2,
        sight_range_modifier=1.0,
        cover_effectiveness=0.15,
        can_fortify=True,
        special_abilities=["两栖登陆", "海上补给线"]
    ),

    # 太空站 - 科幻地形
    TerrainType.SPACE_STATION: Terrain(
        terrain_type=TerrainType.SPACE_STATION,
        name="太空站",
        description="空间站内部，失重环境，复杂管道系统",
        modifiers=TerrainModifier(
            defense_bonus=15,
            speed_penalty=0,
            detection_penalty=20,
            accuracy_penalty=5,
            communication_penalty=-40,
            armor_bonus=10,
            stealth_bonus=10,
            morale_modifier=0
        ),
        movement_cost=1,
        sight_range_modifier=0.8,
        cover_effectiveness=0.4,
        can_fortify=True,
        special_abilities=["失重机动", "管道渗透", "舱壁战斗"]
    ),

    # 轨道 - 太空作战
    TerrainType.ORBITAL: Terrain(
        terrain_type=TerrainType.ORBITAL,
        name="轨道作战区",
        description="地球轨道区域，真空环境，视野极远",
        modifiers=TerrainModifier(
            defense_bonus=0,
            speed_penalty=0,
            detection_penalty=30,
            accuracy_penalty=10,
            communication_penalty=-60,
            armor_bonus=0,
            stealth_bonus=-30,
            morale_modifier=10
        ),
        movement_cost=1,
        sight_range_modifier=3.0,
        cover_effectiveness=0.0,
        can_fortify=False,
        special_abilities=["轨道轰炸", "失重战斗", "热能散热"]
    ),
}

def print_terrain_info(terrain_type: TerrainType):
    """打印地形信息"""
    terrain = TERRAIN_REGISTRY.get(terrain_type)
    if not terrain:
        return

    print("=" * 60)
    print(f"[地形] {terrain.name}")
    print(f"[类型] {terrain.terrain_type.value}")
    print(f"[描述] {terrain.description}")
    print("-" * 60)
    print(f"[效果修正]")
    mods = terrain.modifiers
    print(f"  防御加成: {mods.defense_bonus:+.0f}%")
    print(f"  速度惩罚: {mods.speed_penalty:+.0f}%")
    print(f"  侦查惩罚: {mods.detection_penalty:+.0f}%")
    print(f"  精度惩罚: {mods.accuracy_penalty:+.0f}%")
    print(f"  通讯惩罚: {mods.communication_penalty:+.0f}%")
    print(f"  装甲加成: {mods.armor_bonus:+.0f}")
    print(f"  隐蔽加成: {mods.stealth_bonus:+.0f}%")
    print(f"  士气修正: {mods.morale_modifier:+.0f}")
    print("-" * 60)
    print(f"[地形属性]")
    print(f"  移动消耗: {terrain.movement_cost}")
    print(f"  视野修正: {terrain.sight_range_modifier:.1f}x")
    print(f"  掩体效果: {terrain.cover_effectiveness:.0%}")
    print(f"  可筑防: {'是' if terrain.can_fortify else '否'}")
    print(f"[特殊能力] {', '.join(terrain.special_abilities)}")
    print("=" * 60)

def print_battlefield_status(battlefield: Battlefield):
    """打印战场状态"""
    print("\n" + "=" * 70)
    print(f"[战场] {battlefield.name}")
    print(f"[天气] {battlefield.weather.value}")
    print(f"[回合] {battlefield.turn_count}")
    print("=" * 70)
    print("[区域状态]")
    print("-" * 70)

    weather_mods = battlefield.get_weather_modifiers()

    for zone_id, zone in battlefield.zones.items():
        status = "争夺中" if zone.is_contested else "控制中"
        fort = f"筑防{zone.fortification_level}级" if zone.fortification_level > 0 else "无筑防"
        units = f"单位:{','.join(zone.occupying_units)}" if zone.occupying_units else "无单位"

        print(f"\n[{zone_id}] {zone.name} {status}")
        print(f"  地形: {zone.terrain.name} | {fort}")
        print(f"  {units}")
        print(f"  掩体: {zone.get_cover_bonus():.0%} | 防御: +{zone.terrain.modifiers.defense_bonus}%")

    print("-" * 70)
    print(f"[天气效果]")
    print(f"  侦查: {weather_mods['detection']:+.0f}% | 精度: {weather_mods['accuracy']:+.0f}%")
    print(f"  速度: {weather_mods['speed']:+.0f}% | 通讯: {weather_mods['communication']:+.0f}%")
    print("=" * 70)

def demo_terrain_system():
    """演示地形系统"""
    print("\n" + "=" * 70)
    print("[宇宙之影] 战场地形系统演示")
    print("=" * 70)

    # 展示所有地形
    print("\n[地形类型总览]")
    for terrain_type in TerrainType:
        terrain = TERRAIN_REGISTRY.get(terrain_type)
        if terrain:
            print(f"  {terrain_type.value}: {terrain.name}")

    # 详细展示主要地形
    print("\n[详细地形信息]")
    main_terrains = [TerrainType.PLAINS, TerrainType.MOUNTAIN, TerrainType.URBAN, TerrainType.JUNGLE]
    for terrain_type in main_terrains:
        print_terrain_info(terrain_type)
        print()

    # 创建战场
    print("\n" + "=" * 70)
    print("[战场系统演示]")
    print("=" * 70)

    terrain_system = TerrainSystem()
    battlefield = terrain_system.create_battlefield("前线战场")

    # 部署单位到区域
    battlefield.zones["A1"].occupying_units.append("Gamma-7")
    battlefield.zones["A2"].occupying_units.append("Alpha-1")
    battlefield.zones["B1"].occupying_units.append("Sigma-3")
    battlefield.zones["B2"].occupying_units.append("敌军小队")

    # 筑防测试
    battlefield.zones["A2"].fortify(2)
    battlefield.zones["B1"].fortify(1)

    # 标记争夺区域
    battlefield.zones["B1"].is_contested = True

    # 打印战场状态
    print_battlefield_status(battlefield)

    # 地形优势分析
    print("\n[地形优势分析]")
    advantage = terrain_system.get_terrain_advantage(
        battlefield.zones["A1"],
        battlefield.zones["B1"]
    )
    print(f"  进攻方隐蔽加成: +{advantage['attacker_bonus']}%")
    print(f"  防守方防御加成: +{advantage['defender_bonus']}%")
    print(f"  防守方掩体效果: {advantage['defender_cover']:.0f}%")
    print(f"  [建议] {advantage['recommendation']}")

    # 天气效果
    print("\n[天气变化模拟]")
    weathers = list(WeatherCondition)
    for i in range(4):
        battlefield.turn_count = i + 1
        print(f"\n回合 {battlefield.turn_count}: {battlefield.weather.value}")
        weather_mods = battlefield.get_weather_modifiers()
        print(f"  侦查: {weather_mods['detection']:+.0f}% | 速度: {weather_mods['speed']:+.0f}%")
        battlefield.update_weather()

    print("\n" + "=" * 70)
    print("[地形系统演示完成]")
    print("=" * 70)

if __name__ == "__main__":
    demo_terrain_system()
