"""
宇宙之影 - 基于武器的战斗系统
Shadow of the Universe - Weapon-Based Combat System

根据原文设定重新设计：武器为主，超能力为辅
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

class RiskLevel(Enum):
    SAFE = "安全"
    LOW = "低风险"
    MEDIUM = "中等风险"
    HIGH = "高风险"
    CRITICAL = "极高风险"

class WeaponType(Enum):
    PISTOL = "手枪"
    RIFLE = "步枪"
    SMG = "冲锋枪"
    SNIPER = "狙击枪"
    MELEE = "近战武器"

@dataclass
class WeaponStats:
    """武器属性"""
    name: str
    weapon_type: WeaponType
    base_damage: int
    accuracy: int  # 命中率 0-100
    fire_rate: int  # 射速（每回合攻击次数）
    range: int  # 射程
    magazine_size: int  # 弹匣容量
    reload_time: int  # 换弹时间（回合）
    weight: float  # 重量(kg)
    current_ammo: int = 0  # 当前弹药

@dataclass
class AbilityEffect:
    """能力效果 - 主要用于辅助"""
    name: str
    description: str
    success_rate: int
    reality_debt: int
    duration: int  # 持续时间（回合）
    # 辅助效果类型
    accuracy_boost: int = 0  # 命中加成
    damage_boost: int = 0  # 伤害加成
    dodge_boost: int = 0  # 闪避加成
    detection_range: int = 0  # 感知范围
    prediction_level: int = 0  # 预判等级
    defense_boost: int = 0  # 防御加成

class Ability:
    """
    超能力 - 辅助性质

    注意：此 Ability 类为数据层定义，用于 hero_units_v2.py 中的英雄数据。
    如需在现代战争系统中使用，请通过 hero_integration.py 的转换函数
    (convert_ability_to_combat_ability) 转换为 modern_warfare_system.Ability。
    """
    def __init__(self, name: str, tier: BloodlineTier, effect: AbilityEffect, description: str):
        self.name = name
        self.tier = tier
        self.effect = effect
        self.description = description
        self.consecutive_uses = 0
        self.active_duration = 0  # 激活状态剩余回合

    def get_modified_success_rate(self, user: 'CombatUnit') -> int:
        """获取修正后的成功率"""
        rate = self.effect.success_rate
        rate -= self.consecutive_uses * 5
        if user.reality_debt > 500:
            rate -= 10
        if user.fatigue > 70:
            rate -= 15
        return max(10, min(95, rate))

    def get_risk_level(self, user: 'CombatUnit') -> RiskLevel:
        """获取风险等级"""
        success_rate = self.get_modified_success_rate(user)
        if success_rate >= 85:
            return RiskLevel.SAFE
        elif success_rate >= 70:
            return RiskLevel.LOW
        elif success_rate >= 50:
            return RiskLevel.MEDIUM
        elif success_rate >= 30:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

class CombatUnit:
    """战斗单位"""
    def __init__(self, name: str, tier: BloodlineTier, max_health: int = 100):
        self.name = name
        self.tier = tier
        self.max_health = max_health
        self.current_health = max_health

        # 武器系统
        self.weapon: Optional[WeaponStats] = None
        self.base_accuracy = 70  # 基础命中
        self.base_dodge = 20  # 基础闪避

        # 核心资源
        self.reality_debt = 0
        self.fatigue = 0

        # 能力系统
        self.abilities: List[Ability] = []
        self.active_buffs: Dict[str, int] = {}  # 激活的增益效果

        # 战斗状态
        self.consecutive_uses = 0
        self.is_reloading = False
        self.reload_turns_remaining = 0

    def equip_weapon(self, weapon: WeaponStats):
        """装备武器"""
        self.weapon = weapon
        self.weapon.current_ammo = weapon.magazine_size

    def add_ability(self, ability: Ability):
        """添加能力"""
        self.abilities.append(ability)

    def can_use_ability(self, ability: Ability) -> bool:
        """检查是否能使用能力"""
        if self.reality_debt > 800 and ability.tier != BloodlineTier.LOW:
            return False
        if self.fatigue >= 100:
            return False
        return True

    def get_total_accuracy(self) -> int:
        """获取总命中率"""
        accuracy = self.base_accuracy
        # 武器影响
        if self.weapon:
            accuracy += (self.weapon.accuracy - 70) // 2
            # 负重影响精度：每超重 5kg 精度-1
            weight_penalty = int(self.weapon.weight // 5)
            accuracy -= weight_penalty
        # 增益影响
        accuracy += self.active_buffs.get('accuracy_boost', 0)
        # 疲劳影响
        accuracy -= self.fatigue // 10
        return max(10, min(95, accuracy))

    def get_total_dodge(self) -> int:
        """获取总闪避率"""
        dodge = self.base_dodge
        dodge += self.active_buffs.get('dodge_boost', 0)
        dodge -= self.fatigue // 15
        return max(5, min(80, dodge))

    def attack_with_weapon(self, target: 'Enemy') -> Dict:
        """使用武器攻击"""
        if not self.weapon or self.weapon.current_ammo <= 0:
            return {"success": False, "reason": "弹药耗尽"}

        # 计算命中
        accuracy = self.get_total_accuracy()
        dodge = target.get_dodge() if hasattr(target, 'get_dodge') else 0
        hit_chance = accuracy - dodge

        roll = random.randint(1, 100)
        hit = roll <= hit_chance

        result = {
            "hit": hit,
            "damage": 0,
            "ammo_used": 1,
            "accuracy": accuracy,
            "dodge": dodge,
            "roll": roll
        }

        if hit:
            # 计算伤害
            base_damage = self.weapon.base_damage
            damage_boost = self.active_buffs.get('damage_boost', 0)
            total_damage = base_damage + damage_boost + random.randint(-5, 5)
            result["damage"] = max(1, total_damage)
            target.take_damage(result["damage"])

        self.weapon.current_ammo -= 1
        return result

    def activate_ability(self, ability: Ability) -> Dict:
        """激活超能力"""
        if not self.can_use_ability(ability):
            return {"success": False, "reason": "无法使用能力"}

        success_rate = ability.get_modified_success_rate(self)
        roll = random.randint(1, 100)
        success = roll <= success_rate

        result = {
            "success": success,
            "ability": ability.name,
            "roll": roll,
            "success_rate": success_rate
        }

        if success:
            # 应用增益效果
            if ability.effect.accuracy_boost > 0:
                self.active_buffs['accuracy_boost'] = \
                    self.active_buffs.get('accuracy_boost', 0) + ability.effect.accuracy_boost
            if ability.effect.damage_boost > 0:
                self.active_buffs['damage_boost'] = \
                    self.active_buffs.get('damage_boost', 0) + ability.effect.damage_boost
            if ability.effect.dodge_boost > 0:
                self.active_buffs['dodge_boost'] = \
                    self.active_buffs.get('dodge_boost', 0) + ability.effect.dodge_boost
            if ability.effect.defense_boost > 0:
                self.active_buffs['defense_boost'] = \
                    self.active_buffs.get('defense_boost', 0) + ability.effect.defense_boost

            ability.active_duration = ability.effect.duration
            ability.consecutive_uses += 1
            self.reality_debt += ability.effect.reality_debt
            self.fatigue += 10

            result["effects"] = self.active_buffs.copy()
            result["duration"] = ability.effect.duration
        else:
            # 失败后果
            self.take_damage(5)
            self.reality_debt += int(ability.effect.reality_debt * 1.5)
            self.fatigue += 20

        return result

    def take_damage(self, damage: int):
        """受到伤害"""
        defense = self.active_buffs.get('defense_boost', 0)
        actual_damage = max(1, damage - defense)
        self.current_health = max(0, self.current_health - actual_damage)

    def is_alive(self) -> bool:
        """是否存活"""
        return self.current_health > 0

    def update_buffs(self):
        """更新增益状态"""
        # 减少所有能力持续时间
        for ability in self.abilities:
            if ability.active_duration > 0:
                ability.active_duration -= 1
                if ability.active_duration <= 0:
                    # 移除增益
                    if ability.effect.accuracy_boost > 0:
                        self.active_buffs['accuracy_boost'] = \
                            max(0, self.active_buffs.get('accuracy_boost', 0) - ability.effect.accuracy_boost)
                    if ability.effect.damage_boost > 0:
                        self.active_buffs['damage_boost'] = \
                            max(0, self.active_buffs.get('damage_boost', 0) - ability.effect.damage_boost)
                    if ability.effect.dodge_boost > 0:
                        self.active_buffs['dodge_boost'] = \
                            max(0, self.active_buffs.get('dodge_boost', 0) - ability.effect.dodge_boost)
                    if ability.effect.defense_boost > 0:
                        self.active_buffs['defense_boost'] = \
                            max(0, self.active_buffs.get('defense_boost', 0) - ability.effect.defense_boost)

class Enemy:
    """敌人"""
    def __init__(self, name: str, health: int, attack_power: int, dodge: int = 10):
        self.name = name
        self.max_health = health
        self.current_health = health
        self.attack_power = attack_power
        self.dodge = dodge

    def take_damage(self, damage: int):
        """受到伤害"""
        self.current_health = max(0, self.current_health - damage)

    def get_dodge(self) -> int:
        """获取闪避率"""
        return self.dodge

    def is_alive(self) -> bool:
        """是否存活"""
        return self.current_health > 0

class WeaponBasedBattle:
    """基于武器的战斗系统"""

    def __init__(self):
        self.turn = 0
        self.combat_log = []

    def show_battle_status(self, hero: CombatUnit, enemy: Enemy):
        """显示战斗状态"""
        print("\n" + "="*70)
        print(f"[战斗状态] 第{self.turn}回合")
        print("="*70)

        # 英雄状态
        print(f"\n[英雄] {hero.name} ({hero.tier.value})")
        health_bar = self._create_bar(hero.current_health, hero.max_health)
        print(f"[生命] {hero.current_health}/{hero.max_health} {health_bar}")

        debt_bar = self._create_bar(hero.reality_debt, 1000, reverse=True)
        debt_status = self._get_debt_status(hero.reality_debt)
        print(f"[现实债务] {hero.reality_debt}/1000 {debt_bar} [{debt_status}]")

        fatigue_bar = self._create_bar(hero.fatigue, 100, reverse=True)
        print(f"[疲劳] {hero.fatigue}/100 {fatigue_bar}")

        # 武器状态
        if hero.weapon:
            print(f"[武器] {hero.weapon.name}")
            print(f"  命中率: {hero.get_total_accuracy()}% | 闪避率: {hero.get_total_dodge()}%")
            print(f"  弹药: {hero.weapon.current_ammo}/{hero.weapon.magazine_size}")

        # 增益状态
        if hero.active_buffs:
            print(f"[增益效果]")
            for buff_name, buff_value in hero.active_buffs.items():
                print(f"  {buff_name}: +{buff_value}")

        # 敌人状态
        print(f"\n[敌人] {enemy.name}")
        enemy_health_bar = self._create_bar(enemy.current_health, enemy.max_health)
        print(f"[生命] {enemy.current_health}/{enemy.max_health} {enemy_health_bar}")
        print(f"[闪避] {enemy.get_dodge()}%")

    def _create_bar(self, current, maximum, length=20, reverse=False):
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

    def weapon_attack(self, user: CombatUnit, target: Enemy) -> str:
        """武器攻击"""
        result = user.attack_with_weapon(target)

        status = f"\n[武器攻击] {user.name}使用{user.weapon.name}射击！"
        status += f"\n[命中判定] 命中率:{result['accuracy']}% 闪避:{result['dodge']}%"
        status += f"\n[投掷] {result['roll']} vs {result['accuracy'] - result['dodge']}"

        if result['hit']:
            status += f"\n[命中!] 造成{result['damage']}点伤害！"
            self.combat_log.append(f"[攻击] {user.name}命中目标，造成{result['damage']}伤害")
        else:
            status += f"\n[未命中] 攻击被闪避！"
            self.combat_log.append(f"[攻击] {user.name}攻击未命中")

        return status

    def ability_activate(self, user: CombatUnit, ability: Ability) -> str:
        """激活能力"""
        risk_level = ability.get_risk_level(user)
        status = f"\n[能力激活] {user.name}使用{ability.name}！"
        status += f"\n[风险评估] 成功率:{ability.get_modified_success_rate(user)}% 风险:{risk_level.value}"

        result = user.activate_ability(ability)
        status += f"\n[判定] 投掷:{result['roll']} vs 需求:{result['success_rate']}"

        if result['success']:
            status += f"\n[成功!] {ability.effect.description}"
            status += f"\n[增益效果]"
            if result.get('effects'):
                for buff_name, buff_value in result['effects'].items():
                    status += f"\n  {buff_name}:+{buff_value}"
            status += f"\n[持续时间] {result['duration']}回合"
            self.combat_log.append(f"[能力] {user.name}成功激活{ability.name}")
        else:
            status += f"\n[失败] 能力失控！受到反噬伤害！"
            self.combat_log.append(f"[能力] {user.name}使用{ability.name}失败")

        return status

    def enemy_attack(self, enemy: Enemy, target: CombatUnit):
        """敌人攻击"""
        damage = enemy.attack_power + random.randint(-3, 3)
        target.take_damage(damage)
        print(f"\n[敌人攻击] {enemy.name}对{target.name}造成{damage}点伤害")

    def check_battle_end(self, hero: CombatUnit, enemy: Enemy) -> Optional[str]:
        """检查战斗结束"""
        if not hero.is_alive():
            return "hero_defeated"
        elif not enemy.is_alive():
            return "enemy_defeated"
        elif hero.reality_debt >= 1000:
            return "debt_crisis"
        return None

    def ai_decide_action(self, hero: CombatUnit, enemy: Enemy) -> str:
        """AI决策逻辑"""
        # 弹药检查
        if hero.weapon.current_ammo <= 0:
            return "换弹"

        # 疲劳/债务检查
        if hero.fatigue > 70 or hero.reality_debt > 600:
            return "休息"

        # 检查是否有激活的高价值增益
        active_high_value_buffs = [a for a in hero.abilities
                                  if a.active_duration > 0 and
                                  (a.effect.damage_boost >= 15 or a.effect.accuracy_boost >= 15)]
        if active_high_value_buffs:
            return "武器射击"

        # 检查安全能力可以激活
        safe_abilities = [a for a in hero.abilities
                          if a.get_risk_level(hero) == RiskLevel.SAFE and a.active_duration == 0]
        if safe_abilities:
            ability_index = hero.abilities.index(safe_abilities[0]) + 1
            return f"能力 {ability_index}"

        # 默认武器攻击
        return "武器射击"

    def print_battle_result(self, result: str, hero: CombatUnit, enemy: Enemy, battle: 'WeaponBasedBattle'):
        """打印战斗结果"""
        print("\n" + "="*70)
        print("[战斗结束]")
        print("="*70)

        if result == "enemy_defeated":
            print("\n[胜利]")
            print(f"敌人被击败！剩余生命: {hero.current_health} 累积债务: {hero.reality_debt}")
            print(f"剩余弹药: {hero.weapon.current_ammo}/{hero.weapon.magazine_size}")

            if hero.reality_debt < 300:
                print("[完美] 债务控制优秀，战术运用得当！")
            elif hero.reality_debt < 600:
                print("[良好] 能力使用合理，注意节奏控制")
            else:
                print("[险胜] 债务较高，需要更谨慎的能力使用")

        elif result == "hero_defeated":
            print("\n[失败]")
            print(f"{hero.name}被击败... 剩余敌人生命: {enemy.current_health}")

        elif result == "debt_crisis":
            print("\n[债务危机]")
            print("现实债务达到临界值，现实开始排斥...")

        print(f"\n[战斗统计]")
        print(f"回合数: {battle.turn}")
        print(f"武器攻击次数: {len([log for log in battle.combat_log if '攻击' in log])}")
        print(f"能力使用次数: {len([log for log in battle.combat_log if '能力' in log])}")

        print(f"\n[系统特点]")
        print(f"- 武器是主要伤害来源（稳定可靠）")
        print(f"- 超能力提供战术增益（有风险有代价）")
        print(f"- 能力有持续时间，需要时机把握")
        print(f"- 弹药管理增加战术深度")


def create_hero_with_weapon() -> CombatUnit:
    """创建装备武器的英雄"""
    hero = CombatUnit("特工零号", BloodlineTier.LOW, 100)

    # 装备武器
    pistol = WeaponStats(
        name="战术手枪",
        weapon_type=WeaponType.PISTOL,
        base_damage=25,
        accuracy=80,
        fire_rate=1,
        range=50,
        magazine_size=12,
        reload_time=1,
        weight=0.8
    )
    hero.equip_weapon(pistol)

    # 添加辅助能力
    accuracy_boost = Ability(
        "反应增强",
        BloodlineTier.LOW,
        AbilityEffect(
            name="反应增强",
            description="神经传导速度提升，大幅提高命中率",
            success_rate=95,
            reality_debt=5,
            duration=3,
            accuracy_boost=15,
            detection_range=10
        ),
        "轻微提升神经传导速度"
    )

    dodge_boost = Ability(
        "感知增强",
        BloodlineTier.LOW,
        AbilityEffect(
            name="感知增强",
            description="感知能力提升，提高闪避和预判",
            success_rate=90,
            reality_debt=8,
            duration=2,
            dodge_boost=20,
            prediction_level=1
        ),
        "提升感知和预判能力"
    )

    damage_boost = Ability(
        "力量激发",
        BloodlineTier.LOW,
        AbilityEffect(
            name="力量激发",
            description="临时激发潜能，提高武器伤害",
            success_rate=85,
            reality_debt=10,
            duration=2,
            damage_boost=15
        ),
        "临时提升身体能力"
    )

    hero.add_ability(accuracy_boost)
    hero.add_ability(dodge_boost)
    hero.add_ability(damage_boost)

    return hero

def create_armed_enemy() -> Enemy:
    """创建装备武器的敌人"""
    return Enemy("武装暴徒", health=120, attack_power=15, dodge=15)

def auto_battle_demo():
    """自动战斗演示"""
    print("="*70)
    print("[宇宙之影] 基于武器的战斗系统演示")
    print("="*70)
    print("\n[核心设计理念]")
    print("- 武器是主要攻击手段")
    print("- 超能力是辅助增强（命中/闪避/伤害）")
    print("- 能力有持续时间，需要战术使用时机")
    print("- 现实债务累积限制过度使用能力\n")

    hero = create_hero_with_weapon()
    enemy = create_armed_enemy()
    battle = WeaponBasedBattle()

    print(f"[战斗开始] {hero.name} vs {enemy.name}")
    print(f"英雄装备: {hero.weapon.name}（弹匣{hero.weapon.magazine_size}发）")
    print(f"英雄能力: {len(hero.abilities)}个辅助能力")

    time.sleep(2)

    # 战斗循环
    while True:
        battle.turn += 1
        battle.show_battle_status(hero, enemy)

        # 显示可用能力
        print(f"\n[可用能力]")
        for i, ability in enumerate(hero.abilities, 1):
            success_rate = ability.get_modified_success_rate(hero)
            risk_level = ability.get_risk_level(hero)
            can_use = "[可用]" if hero.can_use_ability(ability) else "[不可用]"
            active_mark = " [激活中]" if ability.active_duration > 0 else ""
            print(f"{can_use} {i}. {ability.name}{active_mark}")
            print(f"   成功率:{success_rate}% 风险:{risk_level.value}")
            print(f"   效果:{ability.effect.description}")
            print(f"   代价:债务+{ability.effect.reality_debt} 疲劳+10")

        # AI决策
        print(f"\n[AI决策]")
        action = battle.ai_decide_action(hero, enemy)
        print(f"选择: {action}")

        time.sleep(1)

        # 执行行动
        if action == "武器射击":
            result = battle.weapon_attack(hero, enemy)
            print(result)

        elif "能力" in action:
            ability_index = int(action.split()[1]) - 1
            ability = hero.abilities[ability_index]
            result = battle.ability_activate(hero, ability)
            print(result)

        elif action == "换弹":
            hero.weapon.current_ammo = hero.weapon.magazine_size
            print(f"[换弹] 弹药已补充至{hero.weapon.current_ammo}发")

        elif action == "休息":
            hero.fatigue = max(0, hero.fatigue - 30)
            debt_reduction = min(hero.reality_debt, 20)
            hero.reality_debt -= debt_reduction
            print(f"[休息] 疲劳-30 债务-{debt_reduction}")

        # 更新增益状态
        hero.update_buffs()

        # 敌人反击
        if enemy.is_alive():
            battle.enemy_attack(enemy, hero)

        time.sleep(1)

        # 检查战斗结束
        result = battle.check_battle_end(hero, enemy)
        if result:
            battle.show_battle_status(hero, enemy)
            battle.print_battle_result(result, hero, enemy, battle)
            break

if __name__ == "__main__":
    try:
        auto_battle_demo()
    except KeyboardInterrupt:
        print("\n[演示中断]")
    except Exception as e:
        print(f"\n[错误] {e}")
