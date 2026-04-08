# -*- coding: utf-8 -*-
"""
宇宙之影 - 增强地图战斗系统
功能: 移动系统 + 负重系统 + 单位属性
"""

from battlefield_map import (
    BattlefieldMap, TerrainTile, HistoricBattlefieldGenerator,
    SimplexNoise
)
from terrain_system import TerrainType, WeatherCondition
import random
from dataclasses import dataclass, field
from typing import List, Optional

# ==================== 装备系统 ====================

@dataclass
class Equipment:
    """装备"""
    name: str
    weight: float          # 重量(kg)
    damage_bonus: int = 0  # 伤害加成
    armor_bonus: int = 0   # 护甲加成
    speed_penalty: float = 0  # 速度惩罚
    special: str = ""      # 特殊效果描述

class Weapon(Equipment):
    """武器"""
    def __init__(self, name: str, weight: float, damage: int, accuracy: int = 80,
                 range_val: int = 3, fire_rate: int = 1, special: str = ""):
        super().__init__(name, weight, damage_bonus=damage, special=special)
        self.accuracy = accuracy
        self.range = range_val
        self.fire_rate = fire_rate
        self.equipment_type = "weapon"

class Armor(Equipment):
    """护甲"""
    def __init__(self, name: str, weight: float, defense: int, speed_penalty: float = 0, special: str = ""):
        super().__init__(name, weight, armor_bonus=defense, speed_penalty=speed_penalty, special=special)
        self.equipment_type = "armor"

class Supply(Equipment):
    """补给品"""
    def __init__(self, name: str, weight: float, healing: int = 0, energy: int = 0):
        super().__init__(name, weight)
        self.healing = healing
        self.energy = energy
        self.equipment_type = "supply"

# ==================== 增强战斗单位 ====================

@dataclass
class UnitStats:
    """单位属性"""
    # 基础属性
    strength: int = 10       # 力量: 影响负重和近战伤害
    agility: int = 10       # 敏捷: 影响移动距离和闪避
    endurance: int = 10     # 耐力: 影响生命值和持续战斗能力
    perception: int = 10    # 感知: 影响侦查和远程命中
    intelligence: int = 10   # 智力: 影响技能效果和判断

    # 战斗属性
    melee_damage: int = 10     # 近战伤害
    ranged_accuracy: int = 50   # 远程精度
    defense: int = 5           # 防御力
    evasion: int = 10          # 闪避率
    crit_chance: int = 5       # 暴击率

class EnhancedCombatUnit:
    """增强战斗单位"""

    # 单位类型模板
    UNIT_TYPES = {
        "scout": {
            "name": "侦察型",
            "base_stats": {"agility": 15, "perception": 14, "strength": 8},
            "move_range": 7,
            "max_load": 30,
            "base_health": 80,
            "base_energy": 100
        },
        "assault": {
            "name": "突击型",
            "base_stats": {"strength": 14, "endurance": 12, "agility": 10},
            "move_range": 5,
            "max_load": 50,
            "base_health": 120,
            "base_energy": 80
        },
        "support": {
            "name": "支援型",
            "base_stats": {"intelligence": 14, "endurance": 12, "perception": 10},
            "move_range": 4,
            "max_load": 60,
            "base_health": 100,
            "base_energy": 150
        },
        "heavy": {
            "name": "重型",
            "base_stats": {"strength": 16, "endurance": 15, "agility": 5},
            "move_range": 3,
            "max_load": 100,
            "base_health": 200,
            "base_energy": 50
        },
        "commander": {
            "name": "指挥型",
            "base_stats": {"intelligence": 15, "perception": 12, "endurance": 11},
            "move_range": 4,
            "max_load": 40,
            "base_health": 100,
            "base_energy": 120
        }
    }

    def __init__(self, name: str, x: int, y: int, unit_type: str = "assault"):
        self.name = name
        self.x = x
        self.y = y
        self.unit_type = unit_type

        # 获取类型模板
        template = self.UNIT_TYPES.get(unit_type, self.UNIT_TYPES["assault"])

        # 基础属性
        self.stats = UnitStats()
        for stat, value in template["base_stats"].items():
            setattr(self.stats, stat, value)

        # 战斗属性计算
        self.max_health = template["base_health"] + self.stats.endurance * 5
        self.health = self.max_health
        self.max_energy = template["base_energy"] + self.stats.intelligence * 3
        self.energy = self.max_energy

        # 移动属性
        self.base_move_range = template["move_range"]
        self.current_move_points = self.base_move_range
        self.max_load = template["max_load"] + self.stats.strength * 2

        # 装备
        self.weapons: List[Weapon] = []
        self.armor: Optional[Armor] = None
        self.supplies: List[Supply] = []

        # 状态
        self.moved_this_turn = False
        self.attacked_this_turn = False
        self.status_effects: dict = {}  # 状态效果

        # 移动历史（用于路径回溯）
        self.position_history: List[tuple] = []

    # ==================== 属性计算 ====================

    def get_total_weight(self) -> float:
        """获取当前负重"""
        weight = 0
        for w in self.weapons:
            weight += w.weight
        if self.armor:
            weight += self.armor.weight
        for s in self.supplies:
            weight += s.weight
        return weight

    def get_load_ratio(self) -> float:
        """获取负重比率"""
        return self.get_total_weight() / self.max_load

    def get_move_penalty_from_load(self) -> float:
        """根据负重获取移动惩罚"""
        ratio = self.get_load_ratio()
        if ratio < 0.3:
            return 0
        elif ratio < 0.6:
            return -0.1
        elif ratio < 0.8:
            return -0.25
        elif ratio < 1.0:
            return -0.4
        else:
            return -0.6  # 严重过载

    def get_actual_move_range(self) -> int:
        """获取实际移动距离"""
        base = self.base_move_range
        # 负重惩罚
        load_penalty = self.get_move_penalty_from_load()
        # 状态惩罚
        status_penalty = self.status_effects.get("slowed", 0)
        # 生命值惩罚（受伤影响移动）
        health_ratio = self.health / self.max_health
        if health_ratio < 0.3:
            base *= 0.5
        elif health_ratio < 0.6:
            base *= 0.8

        actual = int(base * (1 + load_penalty) - status_penalty)
        return max(1, actual)

    def get_defense(self) -> int:
        """获取总防御力"""
        base_def = self.stats.defense
        armor_def = self.armor.armor_bonus if self.armor else 0
        # 状态加成
        status_bonus = self.status_effects.get("defense_buff", 0)
        return base_def + armor_def + status_bonus

    def get_damage(self) -> int:
        """获取总伤害"""
        base_damage = self.stats.melee_damage
        weapon_damage = sum(w.damage_bonus for w in self.weapons)
        # 力量加成
        str_bonus = self.stats.strength // 2
        # 状态加成
        status_bonus = self.status_effects.get("damage_buff", 0)
        return base_damage + weapon_damage + str_bonus + status_bonus

    def get_accuracy(self) -> int:
        """获取远程精度"""
        base_acc = self.stats.ranged_accuracy
        weapon_acc = sum(w.accuracy for w in self.weapons) // max(1, len(self.weapons))
        perception_bonus = (self.stats.perception - 10) * 2
        return base_acc + weapon_acc + perception_bonus

    def get_evasion(self) -> int:
        """获取闪避率"""
        base_evasion = self.stats.evasion
        agility_bonus = (self.stats.agility - 10) * 2
        # 护甲惩罚（重型护甲降低闪避）
        armor_penalty = self.armor.speed_penalty * 2 if self.armor else 0
        # 状态效果
        status_mod = self.status_effects.get("evasion_buff", 0) - self.status_effects.get("evasion_debuff", 0)
        return base_evasion + agility_bonus - armor_penalty + status_mod

    # ==================== 装备管理 ====================

    def equip_weapon(self, weapon: Weapon) -> bool:
        """装备武器"""
        current_weight = self.get_total_weight()
        if current_weight + weapon.weight > self.max_load * 1.2:  # 允许20%超载
            return False
        self.weapons.append(weapon)
        return True

    def equip_armor(self, armor: Armor) -> bool:
        """装备护甲"""
        current_weight = self.get_total_weight()
        if current_weight + armor.weight > self.max_load * 1.2:
            return False
        self.armor = armor
        return True

    def add_supply(self, supply: Supply) -> bool:
        """添加补给"""
        current_weight = self.get_total_weight()
        if current_weight + supply.weight > self.max_load * 1.2:
            return False
        self.supplies.append(supply)
        return True

    def use_supply(self, index: int = 0) -> dict:
        """使用补给"""
        if index >= len(self.supplies):
            return {"success": False, "reason": "没有该补给"}

        supply = self.supplies.pop(index)
        result = {"success": True, "supply": supply.name}

        if supply.healing > 0:
            old_health = self.health
            self.health = min(self.max_health, self.health + supply.healing)
            result["healed"] = self.health - old_health

        if supply.energy > 0:
            old_energy = self.energy
            self.energy = min(self.max_energy, self.energy + supply.energy)
            result["energy_restored"] = self.energy - old_energy

        return result

    # ==================== 战斗方法 ====================

    def take_damage(self, damage: int, ignore_armor: bool = False) -> dict:
        """受到伤害"""
        actual_damage = damage

        if not ignore_armor:
            armor_def = self.armor.armor_bonus if self.armor else 0
            reduction = (self.get_defense() + armor_def) // 2
            actual_damage = max(1, damage - reduction)

        # 闪避判定
        evasion = self.get_evasion()
        if random.randint(1, 100) <= evasion:
            return {"damage": 0, "evaded": True, "message": "攻击被闪避!"}

        self.health = max(0, self.health - actual_damage)

        # 受伤效果
        if self.health < self.max_health * 0.3:
            self.status_effects["slowed"] = 1

        return {
            "damage": actual_damage,
            "evaded": False,
            "armor_absorbed": damage - actual_damage if not ignore_armor else 0,
            "message": f"受到 {actual_damage} 点伤害"
        }

    def attack(self, target: 'EnhancedCombatUnit', distance: int) -> dict:
        """攻击目标"""
        if self.energy < 10:
            return {"success": False, "reason": "能量不足"}

        self.energy -= 10

        # 计算命中率
        accuracy = self.get_accuracy()
        distance_penalty = distance * 10
        target_evasion = target.get_evasion()
        hit_chance = max(20, min(95, accuracy - distance_penalty - target_evasion // 2))

        roll = random.randint(1, 100)
        hit = roll <= hit_chance

        result = {
            "success": True,
            "hit": hit,
            "hit_chance": hit_chance,
            "roll": roll,
            "attacker": self.name,
            "target": target.name,
            "distance": distance
        }

        if hit:
            # 计算伤害
            damage = self.get_damage()
            distance_penalty = distance * 2
            actual_damage = max(5, damage - distance_penalty)

            # 暴击判定
            crit_roll = random.randint(1, 100)
            is_crit = crit_roll <= self.stats.crit_chance
            if is_crit:
                actual_damage = int(actual_damage * 1.5)
                result["critical"] = True

            damage_result = target.take_damage(actual_damage)
            result["damage"] = damage_result["damage"]
            result["evaded"] = damage_result.get("evaded", False)
            result["message"] = damage_result["message"]

            if is_crit:
                result["message"] += " 暴击!"
        else:
            result["damage"] = 0
            result["message"] = "未命中!"

        self.attacked_this_turn = True
        return result

    def move_to(self, x: int, y: int, move_cost: int = 1):
        """移动到新位置"""
        self.position_history.append((self.x, self.y))
        self.x = x
        self.y = y
        self.current_move_points -= move_cost
        self.moved_this_turn = True

    def can_move(self, move_cost: int = 1) -> bool:
        """检查是否可以移动"""
        if self.moved_this_turn:
            return False
        if self.current_move_points < move_cost:
            return False
        return True

    def is_alive(self) -> bool:
        return self.health > 0

    def reset_turn(self):
        """重置回合状态"""
        self.current_move_points = self.get_actual_move_range()
        self.moved_this_turn = False
        self.attacked_this_turn = False
        # 消耗能量
        self.energy = max(0, self.energy - 5)

    # ==================== 状态显示 ====================

    def get_status_summary(self) -> str:
        """获取状态摘要"""
        health_pct = self.health / self.max_health
        energy_pct = self.energy / self.max_energy
        load_pct = self.get_load_ratio()

        status = []
        status.append(f"[{self.name}] {self.UNIT_TYPES[self.unit_type]['name']}")
        status.append(f"  HP: {self.health}/{self.max_health} ({(health_pct*100):.0f}%)")
        status.append(f"  能量: {self.energy}/{self.max_energy} ({(energy_pct*100):.0f}%)")
        status.append(f"  移动: {self.current_move_points}/{self.get_actual_move_range()}")
        status.append(f"  负重: {self.get_total_weight():.1f}/{self.max_load}kg ({(load_pct*100):.0f}%)")

        if self.weapons:
            weapons = ", ".join([w.name for w in self.weapons])
            status.append(f"  武器: {weapons}")

        if self.armor:
            status.append(f"  护甲: {self.armor.name} (+{self.armor.armor_bonus}防御)")

        if self.status_effects:
            effects = ", ".join([f"{k}({v})" for k, v in self.status_effects.items() if v > 0])
            if effects:
                status.append(f"  状态: {effects}")

        return "\n".join(status)


# ==================== 增强地图战场 ====================

class EnhancedBattlefield:
    """增强地图战场"""

    def __init__(self, width: int = 40, height: int = 20, seed: int = None):
        self.map = BattlefieldMap(width, height, seed)
        self.units: dict[str, EnhancedCombatUnit] = {}
        self.turn = 0

        # 地形修正: (defense, speed_penalty, cover, move_cost)
        self.terrain_data = {
            TerrainTile.PLAINS: (0, 0, 0.1, 1),
            TerrainTile.WATER: (0, 100, 0.0, 99),      # 不可通行
            TerrainTile.MOUNTAIN: (25, 40, 0.5, 3),
            TerrainTile.FOREST: (15, 35, 0.6, 2),
            TerrainTile.SAND: (5, 25, 0.05, 1),
            TerrainTile.SNOW: (10, 35, 0.3, 2),
            TerrainTile.URBAN: (20, 50, 0.7, 2),
            TerrainTile.SWAMP: (20, 60, 0.4, 3),
        }

    def add_unit(self, unit: EnhancedCombatUnit):
        """添加单位"""
        self.units[unit.name] = unit
        self.map.place_unit(unit.name, unit.x, unit.y)

    def get_tile_at(self, x: int, y: int) -> int:
        """获取地形"""
        return self.map.get_tile_at(x, y)

    def get_terrain_data(self, x: int, y: int) -> tuple:
        """获取地形数据"""
        tile = self.get_tile_at(x, y)
        return self.terrain_data.get(tile, (0, 0, 0.1, 1))

    def get_move_cost(self, x: int, y: int) -> int:
        """获取移动消耗"""
        _, _, _, move_cost = self.get_terrain_data(x, y)
        return move_cost

    def get_distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """计算曼哈顿距离"""
        return abs(x2 - x1) + abs(y2 - y1)

    def find_path(self, unit: EnhancedCombatUnit, target_x: int, target_y: int) -> List[tuple]:
        """简单路径查找"""
        path = []
        x, y = unit.x, unit.y

        while (x, y) != (target_x, target_y):
            dx = 0 if x == target_x else (1 if target_x > x else -1)
            dy = 0 if y == target_y else (1 if target_y > y else -1)

            # 优先水平移动
            if dx != 0:
                nx, ny = x + dx, y
            else:
                nx, ny = x, y + dy

            # 检查是否可通行
            move_cost = self.get_move_cost(nx, ny)
            if move_cost < 99:
                x, y = nx, ny
                path.append((x, y))
            else:
                break

            if len(path) > 50:  # 防止无限循环
                break

        return path

    def render(self) -> str:
        """渲染战场"""
        lines = []
        lines.append(f"\n{'=' * (self.map.width * 3 + 2)}")
        lines.append(f"[回合 {self.turn}]")
        lines.append(f"{'=' * (self.map.width * 3 + 2)}")

        # 图例
        lines.append(".平原 #森林 ^山地 O城市 ,沙地 *雪地 ;沼泽 ~水域")

        for y in range(self.map.height):
            row = ""
            for x in range(self.map.width):
                # 检查单位
                unit_found = False
                for name, unit in self.units.items():
                    if unit.x == x and unit.y == y and unit.is_alive():
                        hp_pct = unit.health / unit.max_health
                        if hp_pct > 0.6:
                            marker = f"[{name[:2]}]"
                        elif hp_pct > 0.3:
                            marker = f"({name[:2]})"
                        else:
                            marker = f"'{name[:2]}'"
                        row += marker
                        unit_found = True
                        break

                if not unit_found:
                    tile = self.map.tiles[y][x]
                    sym = TerrainTile.SYMBOLS[tile][0]
                    row += f" {sym} "

            lines.append(row)

        lines.append(f"{'=' * (self.map.width * 3 + 2)}")

        # 单位状态
        lines.append("\n[单位状态]")
        for unit in self.units.values():
            if unit.is_alive():
                hp = unit.health / unit.max_health
                ep = unit.energy / unit.max_energy
                hp_bar = "=" * int(hp * 10) + "-" * (10 - int(hp * 10))
                lines.append(f"  {unit.name}: HP {unit.health:3d} [{hp_bar}] 能量{unit.energy:3d} 移动{unit.current_move_points} 负重{unit.get_total_weight():.0f}kg")


# ==================== 增强战斗系统 ====================

class EnhancedCombat:
    """增强战斗系统"""

    def __init__(self, battlefield: EnhancedBattlefield):
        self.battlefield = battlefield

    def run_turn(self) -> dict:
        """运行一回合"""
        self.battlefield.turn += 1
        turn_log = []

        turn_log.append(f"\n{'#' * 50}")
        turn_log.append(f"# 第 {self.battlefield.turn} 回合")
        turn_log.append(f"{'#' * 50}")

        # 重置单位状态
        for unit in self.battlefield.units.values():
            unit.reset_turn()

        # 简单AI
        for unit in self.battlefield.units.values():
            if not unit.is_alive():
                continue

            # 寻找最近的敌人
            enemies = [u for u in self.battlefield.units.values()
                      if u.name != unit.name and u.is_alive()]
            if not enemies:
                continue

            nearest = min(enemies, key=lambda e: self.battlefield.get_distance(unit.x, unit.y, e.x, e.y))
            dist = self.battlefield.get_distance(unit.x, unit.y, nearest.x, nearest.y)

            # 如果在攻击范围内，攻击
            if dist <= 3 and not unit.attacked_this_turn:
                result = unit.attack(nearest, int(dist))
                if result["hit"]:
                    turn_log.append(f"  [{result['attacker']}] 攻击 [{result['target']}] -> 命中 {result['damage']}伤害!")
                    if result.get("critical"):
                        turn_log.append(f"    -> 暴击!")
                    if not nearest.is_alive():
                        turn_log.append(f"    -> [{nearest.name}] 被击毁!")
                else:
                    turn_log.append(f"  [{result['attacker']}] 攻击 [{result['target']}] -> 未命中 (命中率{result['hit_chance']}%)")
            elif dist > 3 and unit.can_move():
                # 移动接近敌人
                path = self.battlefield.find_path(unit, nearest.x, nearest.y)
                if path and unit.current_move_points > 0:
                    next_pos = path[0]
                    move_cost = self.battlefield.get_move_cost(next_pos[0], next_pos[1])
                    if move_cost <= unit.current_move_points:
                        unit.move_to(next_pos[0], next_pos[1], move_cost)
                        tile = self.battlefield.get_tile_at(next_pos[0], next_pos[1])
                        terrain = TerrainTile.SYMBOLS[tile][1]
                        turn_log.append(f"  [{unit.name}] 移动到 ({next_pos[0]},{next_pos[1]}) [{terrain}] 剩余移动{unit.current_move_points}")

        return {"turn": self.battlefield.turn, "log": turn_log}

    def check_end(self) -> str | None:
        """检查战斗结束"""
        alive = [u for u in self.battlefield.units.values() if u.is_alive()]
        if not alive:
            return "draw"

        teams = {}
        for unit in alive:
            team = unit.name[:2] if len(unit.name) > 2 else unit.name[0]
            if team not in teams:
                teams[team] = []
            teams[team].append(unit)

        if len(teams) == 1:
            return f"{list(teams.keys())[0]}_wins"
        return None


# ==================== 预设单位创建 ====================

def create_gamma_unit(x: int, y: int) -> EnhancedCombatUnit:
    """创建Gamma-7突击型机甲"""
    unit = EnhancedCombatUnit("Gamma-7", x, y, "assault")
    unit.max_health = 120
    unit.health = 120
    unit.max_energy = 80
    unit.energy = 80

    # 装备
    unit.equip_weapon(Weapon("共振刃", 15.0, 35, 90, 1, 1, "高能共振切割"))
    unit.equip_weapon(Weapon("突击步枪", 8.0, 25, 80, 3, 2))
    unit.equip_armor(Armor("轻型护甲", 20.0, 15, 0.1, "标准配备"))

    return unit

def create_sigma_unit(x: int, y: int) -> EnhancedCombatUnit:
    """创建Sigma-3侦察型机甲"""
    unit = EnhancedCombatUnit("Sigma-3", x, y, "scout")
    unit.max_health = 70
    unit.health = 70
    unit.max_energy = 120
    unit.energy = 120

    # 装备
    unit.equip_weapon(Weapon("侦查步枪", 5.0, 20, 95, 4, 1, "高精度"))
    unit.equip_armor(Armor("侦察护甲", 8.0, 5, 0.0, "轻量化设计"))
    unit.add_supply(Supply("能量电池", 2.0, 0, 30))

    return unit

def create_alpha_unit(x: int, y: int) -> EnhancedCombatUnit:
    """创建Alpha-1指挥型战舰"""
    unit = EnhancedCombatUnit("Alpha-1", x, y, "commander")
    unit.max_health = 200
    unit.health = 200
    unit.max_energy = 150
    unit.energy = 150

    # 装备
    unit.equip_weapon(Weapon("指挥火炮", 50.0, 50, 70, 5, 1, "范围攻击"))
    unit.equip_armor(Armor("重型护甲", 80.0, 40, 0.3, "舰载护甲"))

    return unit

def create_heavy_unit(x: int, y: int, name: str = "重装") -> EnhancedCombatUnit:
    """创建重装单位"""
    unit = EnhancedCombatUnit(name, x, y, "heavy")
    unit.max_health = 200
    unit.health = 200
    unit.max_energy = 50
    unit.energy = 50

    unit.equip_weapon(Weapon("重型机枪", 30.0, 45, 60, 3, 3, "持续火力"))
    unit.equip_armor(Armor("重甲", 100.0, 50, 0.4, "移动缓慢"))

    return unit

def create_enemy_unit(x: int, y: int, num: int = 1) -> EnhancedCombatUnit:
    """创建敌方单位"""
    unit = EnhancedCombatUnit(f"敌{num}", x, y, "assault")
    unit.max_health = 80
    unit.health = 80

    unit.equip_weapon(Weapon("敌军步枪", 6.0, 22, 75, 3, 1))
    unit.equip_armor(Armor("敌军护甲", 15.0, 10, 0.1))

    return unit


# ==================== 演示 ====================

def demo_enhanced_combat():
    """演示增强战斗系统"""
    print("\n" + "=" * 70)
    print("[宇宙之影] 增强地图战斗系统")
    print("=" * 70)
    print("\n[新增功能]")
    print("  - 移动系统: 行动点/负重惩罚/地形影响")
    print("  - 装备系统: 武器/护甲/补给")
    print("  - 属性系统: 力量/敏捷/耐力/感知/智力")
    print("  - 战斗计算: 命中率/暴击/闪避/护甲减伤")

    # 创建战场
    battlefield = EnhancedBattlefield(width=50, height=18, seed=2026)

    # 创建单位
    gamma = create_gamma_unit(5, 9)
    sigma = create_sigma_unit(8, 11)
    alpha = create_alpha_unit(3, 7)
    enemy1 = create_enemy_unit(40, 9, 1)
    enemy2 = create_enemy_unit(42, 11, 2)
    enemy3 = create_enemy_unit(38, 7, 3)

    # 添加到战场
    battlefield.add_unit(gamma)
    battlefield.add_unit(sigma)
    battlefield.add_unit(alpha)
    battlefield.add_unit(enemy1)
    battlefield.add_unit(enemy2)
    battlefield.add_unit(enemy3)

    print(f"\n[战场初始化]")
    print(f"  地图大小: {battlefield.map.width}x{battlefield.map.height}")
    print(f"  单位数量: {len(battlefield.units)}")

    # 显示单位详情
    print("\n[单位详情]")
    print("-" * 70)
    for unit in battlefield.units.values():
        print(unit.get_status_summary())
        print()

    print(battlefield.render())

    # 创建战斗系统
    combat = EnhancedCombat(battlefield)

    print("\n[战斗开始]")
    print("=" * 70)

    # 运行若干回合
    for i in range(8):
        result = combat.run_turn()
        for log in result["log"]:
            print(log)

        print(battlefield.render())

        # 检查结束
        end_result = combat.check_end()
        if end_result:
            print(f"\n[战斗结束] {end_result}")
            break

        import time
        time.sleep(0.3)

    # 最终统计
    print("\n" + "=" * 70)
    print("[战斗统计]")
    print("=" * 70)

    survivors = [u for u in battlefield.units.values() if u.is_alive()]
    print(f"  存活单位: {len(survivors)}")
    for unit in survivors:
        print(f"    {unit.name}: HP {unit.health}/{unit.max_health} 能量{unit.energy}/{unit.max_energy}")


def demo_unit_load_system():
    """演示负重系统"""
    print("\n" + "=" * 70)
    print("[负重系统演示]")
    print("=" * 70)

    # 创建单位
    unit = EnhancedCombatUnit("测试单位", 0, 0, "assault")
    print(f"\n[单位属性]")
    print(f"  类型: {unit.UNIT_TYPES[unit.unit_type]['name']}")
    print(f"  最大负重: {unit.max_load}kg")
    print(f"  基础移动: {unit.base_move_range}")

    # 测试不同负重
    print("\n[负重影响测试]")
    test_weights = [0, 20, 40, 60, 80, 100]

    for w in test_weights:
        # 模拟负重
        unit.weapons = [Weapon(f"物品{i}", 10.0, 10) for i in range(w // 10)]
        actual = unit.get_total_weight()
        ratio = unit.get_load_ratio()
        move_range = unit.get_actual_move_range()
        penalty = unit.get_move_penalty_from_load()

        load_status = "正常" if ratio < 0.8 else "过载"
        print(f"  负重{actual:.0f}kg ({ratio*100:.0f}%): 移动{unit.base_move_range}->{move_range} ({penalty*100:.0f}%惩罚) [{load_status}]")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--load":
        demo_unit_load_system()
    else:
        demo_enhanced_combat()
