"""
宇宙之影 - 战争机器战斗系统
Shadow of the Universe - Warfare Machine Combat System

基于原文设定：武器是航母、堡垒等战争机器，超能力辅助增强这些装备
"""

import random
import time
from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

class BloodlineTier(Enum):
    LOW = "低级血统"
    MEDIUM = "中级血统"
    HIGH = "高级血统"

class MachineType(Enum):
    """战争机器类型"""
    AIRCRAFT_CARRIER = "航空母舰"
    FORTRESS = "要塞堡垒"
    BATTLESHIP = "战列舰"
    MECHA = "机甲战士"
    ARTILLERY = "重炮阵地"
    COMMAND_CENTER = "指挥中心"

@dataclass
class WarfareMachineStats:
    """战争机器属性"""
    name: str
    machine_type: MachineType
    max_health: int
    base_damage: int
    attack_range: int
    accuracy: int
    special_systems: List[str]  # 特殊系统
    crew_requirement: int  # 需要船员数量
    energy_capacity: int  # 能量容量
    current_energy: int = 100

@dataclass
class AbilityEffect:
    """超能力效果 - 增强战争机器"""
    name: str
    description: str
    success_rate: int
    reality_debt: int
    duration: int  # 持续时间（回合）

    # 战争机器增强效果
    damage_boost: int = 0  # 伤害增强
    accuracy_boost: int = 0  # 精度增强
    range_boost: int = 0  # 射程增强
    defense_boost: int = 0  # 防御增强
    detection_boost: int = 0  # 探测增强
    energy_efficiency: int = 0  # 能量效率
    repair_boost: int = 0  # 维修增强
    system_unlock: str = ""  # 解锁特殊系统

class MachineOperator:
    """战争机器操作员"""
    def __init__(self, name: str, tier: BloodlineTier):
        self.name = name
        self.tier = tier
        self.command_skill = random.randint(60, 90)  # 指挥技能
        self.technical_skill = random.randint(50, 85)  # 技术技能
        self.reality_debt = 0
        self.fatigue = 0
        self.abilities: List['Ability'] = []

    def add_ability(self, ability: 'Ability'):
        """添加超能力"""
        self.abilities.append(ability)

class Ability:
    """超能力 - 增强战争机器性能"""
    def __init__(self, name: str, tier: BloodlineTier, effect: AbilityEffect, description: str):
        self.name = name
        self.tier = tier
        self.effect = effect
        self.description = description
        self.consecutive_uses = 0
        self.active_duration = 0

    def get_modified_success_rate(self, operator: MachineOperator) -> int:
        """获取修正后的成功率"""
        rate = self.effect.success_rate
        rate -= self.consecutive_uses * 5
        if operator.reality_debt > 500:
            rate -= 10
        if operator.fatigue > 70:
            rate -= 15
        # 操作员技能影响
        rate += (operator.technical_skill - 70) // 2
        return max(10, min(95, rate))

    def get_risk_level(self, operator: MachineOperator) -> str:
        """获取风险等级"""
        success_rate = self.get_modified_success_rate(operator)
        if success_rate >= 85:
            return "安全"
        elif success_rate >= 70:
            return "低风险"
        elif success_rate >= 50:
            return "中等风险"
        elif success_rate >= 30:
            return "高风险"
        else:
            return "极高风险"

class CombatUnit:
    """战斗单位 - 战争机器+操作员"""
    def __init__(self, machine: WarfareMachineStats, operator: MachineOperator):
        self.machine = machine
        self.operator = operator
        self.current_health = machine.max_health
        self.active_buffs: Dict[str, int] = {}

        # 战斗状态
        self.is_repairing = False
        self.systems_active = True

    def get_total_damage(self) -> int:
        """获取总伤害"""
        damage = self.machine.base_damage
        damage += self.active_buffs.get('damage_boost', 0)
        damage += self.operator.command_skill // 10
        return damage

    def get_total_accuracy(self) -> int:
        """获取总精度"""
        accuracy = self.machine.accuracy
        accuracy += self.active_buffs.get('accuracy_boost', 0)
        accuracy += self.operator.technical_skill // 15
        accuracy -= self.operator.fatigue // 20
        return max(20, min(95, accuracy))

    def get_total_range(self) -> int:
        """获取总射程"""
        range_val = self.machine.attack_range
        range_val += self.active_buffs.get('range_boost', 0)
        return range_val

    def get_defense(self) -> int:
        """获取防御力"""
        defense = self.active_buffs.get('defense_boost', 0)
        defense += self.machine.current_energy // 10
        return defense

    def machine_attack(self, target: 'EnemyForce') -> Dict:
        """战争机器攻击"""
        damage = self.get_total_damage()
        accuracy = self.get_total_accuracy()

        # 计算命中
        dodge = getattr(target, 'evasion', 10)
        hit_chance = accuracy - dodge
        roll = random.randint(1, 100)
        hit = roll <= hit_chance

        result = {
            "hit": hit,
            "damage": 0 if not hit else damage + random.randint(-10, 10),
            "accuracy": accuracy,
            "roll": roll,
            "hit_chance": hit_chance
        }

        if hit:
            result["damage"] = max(10, result["damage"])
            target.take_damage(result["damage"])

        return result

    def activate_ability(self, ability: Ability) -> Dict:
        """激活超能力增强"""
        if not self.can_use_ability(ability):
            return {"success": False, "reason": "无法使用能力"}

        success_rate = ability.get_modified_success_rate(self.operator)
        roll = random.randint(1, 100)
        success = roll <= success_rate

        result = {
            "success": success,
            "ability": ability.name,
            "roll": roll,
            "success_rate": success_rate
        }

        if success:
            # 应用增强效果
            if ability.effect.damage_boost > 0:
                self.active_buffs['damage_boost'] = \
                    self.active_buffs.get('damage_boost', 0) + ability.effect.damage_boost
            if ability.effect.accuracy_boost > 0:
                self.active_buffs['accuracy_boost'] = \
                    self.active_buffs.get('accuracy_boost', 0) + ability.effect.accuracy_boost
            if ability.effect.range_boost > 0:
                self.active_buffs['range_boost'] = \
                    self.active_buffs.get('range_boost', 0) + ability.effect.range_boost
            if ability.effect.defense_boost > 0:
                self.active_buffs['defense_boost'] = \
                    self.active_buffs.get('defense_boost', 0) + ability.effect.defense_boost
            if ability.effect.repair_boost > 0:
                repair_amount = ability.effect.repair_boost + self.operator.technical_skill // 5
                self.current_health = min(self.machine.max_health, self.current_health + repair_amount)

            ability.active_duration = ability.effect.duration
            ability.consecutive_uses += 1
            self.operator.reality_debt += ability.effect.reality_debt
            self.operator.fatigue += 15

            result["effects"] = self.active_buffs.copy()
            result["duration"] = ability.effect.duration
        else:
            # 失败后果 - 机器受损
            self.current_health -= 20
            self.operator.reality_debt += int(ability.effect.reality_debt * 2)
            self.operator.fatigue += 25

        return result

    def can_use_ability(self, ability: Ability) -> bool:
        """检查是否能使用能力"""
        if self.operator.reality_debt > 800 and ability.tier != BloodlineTier.LOW:
            return False
        if self.operator.fatigue >= 100:
            return False
        if self.machine.current_energy < 20:
            return False
        return True

    def take_damage(self, damage: int):
        """受到伤害"""
        defense = self.get_defense()
        actual_damage = max(5, damage - defense)
        self.current_health = max(0, self.current_health - actual_damage)

    def repair_machine(self):
        """维修机器"""
        if not self.is_repairing:
            repair_amount = 30 + self.operator.technical_skill // 3
            self.current_health = min(self.machine.max_health, self.current_health + repair_amount)
            self.operator.fatigue = max(0, self.operator.fatigue - 20)
            return True
        return False

    def is_alive(self) -> bool:
        """是否还能战斗"""
        return self.current_health > 0

    def update_buffs(self):
        """更新增益状态"""
        for ability in self.operator.abilities:
            if ability.active_duration > 0:
                ability.active_duration -= 1
                if ability.active_duration <= 0:
                    # 移除增益
                    if ability.effect.damage_boost > 0:
                        self.active_buffs['damage_boost'] = \
                            max(0, self.active_buffs.get('damage_boost', 0) - ability.effect.damage_boost)
                    if ability.effect.accuracy_boost > 0:
                        self.active_buffs['accuracy_boost'] = \
                            max(0, self.active_buffs.get('accuracy_boost', 0) - ability.effect.accuracy_boost)
                    if ability.effect.range_boost > 0:
                        self.active_buffs['range_boost'] = \
                            max(0, self.active_buffs.get('range_boost', 0) - ability.effect.range_boost)
                    if ability.effect.defense_boost > 0:
                        self.active_buffs['defense_boost'] = \
                            max(0, self.active_buffs.get('defense_boost', 0) - ability.effect.defense_boost)

class EnemyForce:
    """敌方部队"""
    def __init__(self, name: str, health: int, attack_power: int, evasion: int = 10):
        self.name = name
        self.max_health = health
        self.current_health = health
        self.attack_power = attack_power
        self.evasion = evasion

    def take_damage(self, damage: int):
        """受到伤害"""
        self.current_health = max(0, self.current_health - damage)

    def is_alive(self) -> bool:
        """是否存活"""
        return self.current_health > 0

class WarfareBattle:
    """战争机器战斗系统"""

    def __init__(self):
        self.turn = 0
        self.combat_log = []

    def show_battle_status(self, unit: CombatUnit, enemy: EnemyForce):
        """显示战斗状态"""
        print("\n" + "="*80)
        print(f"[战役状态] 第{self.turn}回合")
        print("="*80)

        # 我方单位状态
        print(f"\n[我方] {unit.machine.name}")
        print(f"[操作员] {unit.operator.name} ({unit.operator.tier.value})")
        machine_health_bar = self._create_bar(unit.current_health, unit.machine.max_health)
        print(f"[机体完整度] {unit.current_health}/{unit.machine.max_health} {machine_health_bar}")

        operator_debt_bar = self._create_bar(unit.operator.reality_debt, 1000, reverse=True)
        debt_status = self._get_debt_status(unit.operator.reality_debt)
        print(f"[操作员债务] {unit.operator.reality_debt}/1000 {operator_debt_bar} [{debt_status}]")

        operator_fatigue_bar = self._create_bar(unit.operator.fatigue, 100, reverse=True)
        print(f"[操作员疲劳] {unit.operator.fatigue}/100 {operator_fatigue_bar}")

        # 战斗性能
        print(f"\n[战斗性能]")
        print(f"[伤害输出] {unit.get_total_damage()} | [命中精度] {unit.get_total_accuracy()}%")
        print(f"[攻击射程] {unit.get_total_range()}km | [防御等级] {unit.get_defense()}")

        # 增益状态
        if unit.active_buffs:
            print(f"[超能增强]")
            for buff_name, buff_value in unit.active_buffs.items():
                print(f"  {buff_name}:+{buff_value}")

        # 敌方状态
        print(f"\n[敌方] {enemy.name}")
        enemy_health_bar = self._create_bar(enemy.current_health, enemy.max_health)
        print(f"[战斗力] {enemy.current_health}/{enemy.max_health} {enemy_health_bar}")
        print(f"[闪避能力] {enemy.evasion}%")

    def _create_bar(self, current, maximum, length=25, reverse=False):
        """创建状态条"""
        ratio = current / maximum
        filled = int(ratio * length)
        if reverse:
            if ratio < 0.3:
                char = "+"
            elif ratio < 0.6:
                char = "="
            elif ratio < 0.8:
                char = "#"
            else:
                char = "!"
        else:
            if ratio > 0.7:
                char = "+"
            elif ratio > 0.4:
                char = "="
            elif ratio > 0.2:
                char = "#"
            else:
                char = "!"
        bar = char * filled + "-" * (length - filled)
        return f"[{bar}]"

    def _get_debt_status(self, debt: int) -> str:
        """获取债务状态"""
        if debt >= 900:
            return "极危"
        elif debt >= 700:
            return "危险"
        elif debt >= 500:
            return "警告"
        elif debt >= 300:
            return "注意"
        else:
            return "安全"

    def machine_attack(self, unit: CombatUnit, enemy: EnemyForce) -> str:
        """战争机器攻击"""
        result = unit.machine_attack(enemy)

        status = f"\n[主炮齐射] {unit.machine.name}对{enemy.name}发起攻击！"
        status += f"\n[弹道计算] 命中率:{result['accuracy']}% 闪避:{enemy.evasion}%"
        status += f"\n[命中判定] {result['roll']} vs {result['hit_chance']}"

        if result['hit']:
            status += f"\n[直接命中!] 造成{result['damage']}点伤害！"
            self.combat_log.append(f"[攻击] {unit.machine.name}命中目标，造成{result['damage']}伤害")
        else:
            status += f"\n[攻击未命中] 目标成功闪避！"
            self.combat_log.append(f"[攻击] {unit.machine.name}攻击未命中")

        return status

    def ability_enhance(self, unit: CombatUnit, ability: Ability) -> str:
        """超能力增强机器"""
        risk_level = ability.get_risk_level(unit.operator)
        status = f"\n[超能增强] {unit.operator.name}使用{ability.name}增强{unit.machine.name}！"
        status += f"\n[风险评估] 成功率:{ability.get_modified_success_rate(unit.operator)}% 风险:{risk_level}"

        result = unit.activate_ability(ability)
        status += f"\n[强化判定] 投掷:{result['roll']} vs 需求:{result['success_rate']}"

        if result['success']:
            status += f"\n[强化成功!] {ability.effect.description}"
            if result.get('effects'):
                status += f"\n[性能提升]"
                for buff_name, buff_value in result['effects'].items():
                    if buff_value > 0:
                        status += f"\n  {buff_name}:+{buff_value}"
            if result.get('duration'):
                status += f"\n[持续时间] {result['duration']}回合"
            self.combat_log.append(f"[强化] {unit.operator.name}成功使用{ability.name}")
        else:
            status += f"\n[强化失败] 能力失控！机体受到反噬损伤！"
            self.combat_log.append(f"[强化] {unit.operator.name}使用{ability.name}失败")

        return status

    def enemy_counterattack(self, enemy: EnemyForce, unit: CombatUnit):
        """敌方反击"""
        damage = enemy.attack_power + random.randint(-10, 10)
        unit.take_damage(damage)
        print(f"\n[敌方反击] {enemy.name}对{unit.machine.name}造成{damage}点伤害")

    def check_battle_end(self, unit: CombatUnit, enemy: EnemyForce) -> Optional[str]:
        """检查战役结束"""
        if not unit.is_alive():
            return "unit_destroyed"
        elif not enemy.is_alive():
            return "enemy_defeated"
        elif unit.operator.reality_debt >= 1000:
            return "debt_crisis"
        return None

def create_warfare_unit() -> CombatUnit:
    """创建战争机器单位"""
    # 航空母舰
    carrier = WarfareMachineStats(
        name="海洋之星号航母",
        machine_type=MachineType.AIRCRAFT_CARRIER,
        max_health=500,
        base_damage=80,
        attack_range=200,
        accuracy=75,
        special_systems=["舰载机群", "防空系统", "雷达系统"],
        crew_requirement=300,
        energy_capacity=1000
    )

    # 低级血统操作员
    operator = MachineOperator("指挥官零号", BloodlineTier.LOW)

    unit = CombatUnit(carrier, operator)

    # 添加辅助能力
    damage_boost = Ability(
        "火力增强",
        BloodlineTier.LOW,
        AbilityEffect(
            name="火力增强",
            description="通过操控电磁场大幅提升舰炮威力",
            success_rate=90,
            reality_debt=15,
            duration=3,
            damage_boost=30
        ),
        "电磁操控增强武器系统"
    )

    accuracy_boost = Ability(
        "雷达增强",
        BloodlineTier.LOW,
        AbilityEffect(
            name="雷达增强",
            description="感知能力增强雷达系统，大幅提高精度",
            success_rate=95,
            reality_debt=10,
            duration=4,
            accuracy_boost=20,
            detection_boost=50
        ),
        "感知能力增强探测系统"
    )

    repair_ability = Ability(
        "紧急修复",
        BloodlineTier.LOW,
        AbilityEffect(
            name="紧急修复",
            description="通过物质操控快速修复受损机体",
            success_rate=85,
            reality_debt=25,
            duration=1,
            repair_boost=50
        ),
        "物质操控修复受损系统"
    )

    operator.add_ability(damage_boost)
    operator.add_ability(accuracy_boost)
    operator.add_ability(repair_ability)

    return unit

def create_enemy_force() -> EnemyForce:
    """创建敌方部队"""
    return EnemyForce("敌军舰队", health=600, attack_power=50, evasion=15)

def auto_warfare_demo():
    """自动战争机器演示"""
    print("="*80)
    print("[宇宙之影] 战争机器战斗系统演示")
    print("="*80)
    print("\n[核心设计理念]")
    print("- 武器：航母、堡垒等战争机器（主要战斗力）")
    print("- 超能力：增强机器性能（伤害、精度、射程、修复等）")
    print("- 操作员：低级血统者控制战争机器")
    print("- 风险：能力失败会导致机体受损，操作员承担现实债务")
    print("- 战术：合理使用能力增强，时机把握是关键\n")

    unit = create_warfare_unit()
    enemy = create_enemy_force()
    battle = WarfareBattle()

    print(f"[战役开始] {unit.machine.name} vs {enemy.name}")
    print(f"[作战单位] {unit.operator.name}指挥{unit.machine.name}")
    print(f"[特殊系统] {', '.join(unit.machine.special_systems)}")
    print(f"[操作员能力] {len(unit.operator.abilities)}个增强能力")

    time.sleep(2)

    # 战斗循环
    while True:
        battle.turn += 1
        battle.show_battle_status(unit, enemy)

        # 显示可用能力
        print(f"\n[可用增强能力]")
        for i, ability in enumerate(unit.operator.abilities, 1):
            success_rate = ability.get_modified_success_rate(unit.operator)
            risk_level = ability.get_risk_level(unit.operator)
            can_use = "[可用]" if unit.can_use_ability(ability) else "[不可用]"
            active_mark = f" [激活中{ability.active_duration}回]" if ability.active_duration > 0 else ""
            print(f"{can_use} {i}. {ability.name}{active_mark}")
            print(f"   成功率:{success_rate}% 风险:{risk_level}")
            print(f"   效果:{ability.effect.description}")
            print(f"   增益:伤害+{ability.effect.damage_boost} 精度+{ability.effect.accuracy_boost} 修复+{ability.effect.repair_boost}")
            print(f"   代价:债务+{ability.effect.reality_debt} 疲劳+15")

        # AI决策
        print(f"\n[指挥决策]")
        action = battle.ai_command_decision(unit, enemy)
        print(f"选择: {action}")

        time.sleep(1)

        # 执行行动
        if action == "主炮攻击":
            result = battle.machine_attack(unit, enemy)
            print(result)

        elif "增强" in action:
            ability_index = int(action.split()[1]) - 1
            ability = unit.operator.abilities[ability_index]
            result = battle.ability_enhance(unit, ability)
            print(result)

        elif action == "系统维修":
            if unit.repair_machine():
                print(f"\n[系统维修] 机体得到修复，当前完整度: {unit.current_health}/{unit.machine.max_health}")
            else:
                print(f"\n[维修失败] 正在维修中")

        elif action == "战术休整":
            unit.operator.fatigue = max(0, unit.operator.fatigue - 40)
            debt_reduction = min(unit.operator.reality_debt, 30)
            unit.operator.reality_debt -= debt_reduction
            print(f"\n[战术休整] 操作员疲劳-40 债务-{debt_reduction}")

        # 更新增益状态
        unit.update_buffs()

        # 敌方反击
        if enemy.is_alive():
            battle.enemy_counterattack(enemy, unit)

        time.sleep(1)

        # 检查战斗结束
        result = battle.check_battle_end(unit, enemy)
        if result:
            battle.show_battle_status(unit, enemy)
            battle.print_battle_result(result, unit, enemy, battle)
            break

def ai_command_decision(self, unit: CombatUnit, enemy: EnemyForce) -> str:
    """AI指挥决策"""
    # 机体损伤严重时优先维修
    if unit.current_health < unit.machine.max_health * 0.3:
        repair_ability = next((a for a in unit.operator.abilities if a.effect.repair_boost > 0), None)
        if repair_ability and unit.can_use_ability(repair_ability):
            ability_index = unit.operator.abilities.index(repair_ability) + 1
            return f"增强 {ability_index}"

    # 疲劳/债务检查
    if unit.operator.fatigue > 70 or unit.operator.reality_debt > 600:
        return "战术休整"

    # 检查是否有高价值增益激活
    active_high_buffs = [a for a in unit.operator.abilities
                         if a.active_duration > 0 and
                         (a.effect.damage_boost >= 30 or a.effect.accuracy_boost >= 20)]
    if active_high_buffs:
        return "主炮攻击"

    # 检查安全能力
    safe_abilities = [a for a in unit.operator.abilities
                      if a.get_risk_level(unit.operator) == "安全" and a.active_duration == 0]
    if safe_abilities:
        ability_index = unit.operator.abilities.index(safe_abilities[0]) + 1
        return f"增强 {ability_index}"

    # 默认攻击
    return "主炮攻击"

def print_battle_result(self, result, unit: CombatUnit, enemy: EnemyForce, battle):
    """打印战役结果"""
    print("\n" + "="*80)
    print("[战役结束]")
    print("="*80)

    if result == "enemy_defeated":
        print("\n[战役胜利]")
        print(f"敌方部队被击败！")
        print(f"[我方损耗] 机体完整度: {unit.current_health}/{unit.machine.max_health}")
        print(f"[操作员状态] 现实债务: {unit.operator.reality_debt}/1000")

        if unit.operator.reality_debt < 300:
            print("[完美战役] 能力运用出色，代价控制优秀！")
        elif unit.operator.reality_debt < 600:
            print("[良好胜利] 战术运用合理，损失可控")
        else:
            print("[惨胜] 代价较高，需要更谨慎的战术决策")

    elif result == "unit_destroyed":
        print("\n[战役失败]")
        print(f"{unit.machine.name}被摧毁...")
        print(f"[敌方残存] {enemy.name}剩余战斗力: {enemy.current_health}")

    elif result == "debt_crisis":
        print("\n[现实危机]")
        print("操作员现实债务达到临界值，被现实排斥...")

    print(f"\n[战役统计]")
    print(f"战斗回合: {battle.turn}")
    print(f"主炮射击: {len([log for log in battle.combat_log if '攻击' in log])}次")
    print(f"能力强化: {len([log for log in battle.combat_log if '强化' in log])}次")

    print(f"\n[系统特点]")
    print(f"- 战争机器提供稳定强大的火力输出")
    print(f"- 超能力增强机器性能，改变战局平衡")
    print(f"- 能力有持续时间，需要战术时机把握")
    print(f"- 失败会导致机体受损，风险与收益并存")
    print(f"- 操作员的现实债务限制过度依赖超能力")

# 绑定方法
WarfareBattle.ai_command_decision = ai_command_decision
WarfareBattle.print_battle_result = print_battle_result

if __name__ == "__main__":
    try:
        auto_warfare_demo()
    except KeyboardInterrupt:
        print("\n[演示中断]")
    except Exception as e:
        print(f"\n[错误] {e}")