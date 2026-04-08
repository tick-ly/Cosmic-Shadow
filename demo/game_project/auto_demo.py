"""
宇宙之影 - 自动演示版本
Shadow of the Universe - Auto Demo

物理妥协能力系统自动演示
"""

import random
import time
from dataclasses import dataclass
from typing import List, Optional
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

@dataclass
class SkillEffect:
    success_description: str
    failure_description: str
    success_damage: int
    failure_damage: int
    reality_debt: int

class Skill:
    def __init__(self, name, tier, base_success_rate, effect, description):
        self.name = name
        self.tier = tier
        self.base_success_rate = base_success_rate
        self.effect = effect
        self.description = description
        self.consecutive_uses = 0

    def get_modified_success_rate(self, user):
        rate = self.base_success_rate
        rate -= self.consecutive_uses * 5
        if user.reality_debt > 500:
            rate -= 10
        if user.fatigue > 70:
            rate -= 15
        return max(10, min(95, rate))

    def get_risk_level(self, user):
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
    def __init__(self, name, tier, max_health=100):
        self.name = name
        self.tier = tier
        self.max_health = max_health
        self.current_health = max_health
        self.reality_debt = 0
        self.fatigue = 0
        self.skills = []

    def add_skill(self, skill):
        self.skills.append(skill)

    def can_use_skill(self, skill):
        if self.reality_debt > 800 and skill.tier != BloodlineTier.LOW:
            return False
        if self.fatigue >= 100:
            return False
        return True

    def take_damage(self, damage):
        self.current_health = max(0, self.current_health - damage)

    def is_alive(self):
        return self.current_health > 0

class Enemy:
    def __init__(self, name, health, attack_power):
        self.name = name
        self.max_health = health
        self.current_health = health
        self.attack_power = attack_power

    def take_damage(self, damage):
        self.current_health = max(0, self.current_health - damage)

    def is_alive(self):
        return self.current_health > 0

class BattleManager:
    def __init__(self):
        self.turn = 0
        self.combat_log = []

    def use_skill(self, user, skill, target):
        if not user.can_use_skill(skill):
            print(f"[无法使用] {user.name}无法使用{skill.name}！")
            return False

        success_rate = skill.get_modified_success_rate(user)
        risk_level = skill.get_risk_level(user)
        roll = random.randint(1, 100)

        print(f"\n[技能使用] {user.name}使用{skill.name}！")
        print(f"[风险评估] 成功率: {success_rate}% | 风险: {risk_level.value}")
        print(f"[判定] 投掷: {roll} vs 需求: {success_rate}")

        if roll <= success_rate:
            return self._skill_success(user, skill, target)
        else:
            return self._skill_failure(user, skill, target)

    def _skill_success(self, user, skill, target):
        print(f"[成功] {skill.effect.success_description}")
        target.take_damage(skill.effect.success_damage)
        user.reality_debt += skill.effect.reality_debt
        user.fatigue += 10
        skill.consecutive_uses += 1
        return True

    def _skill_failure(self, user, skill, target):
        print(f"[失败] {skill.effect.failure_description}")
        user.take_damage(skill.effect.failure_damage)
        user.reality_debt += int(skill.effect.reality_debt * 1.5)
        user.fatigue += 20
        return False

    def enemy_attack(self, enemy, target):
        damage = enemy.attack_power + random.randint(-2, 2)
        target.take_damage(damage)
        print(f"\n[敌人攻击] {enemy.name}对{target.name}造成{damage}点伤害")

    def show_battle_status(self, hero, enemy):
        print("\n" + "="*60)
        print(f"[战斗状态] 第{self.turn}回合")
        print("="*60)
        print(f"\n[英雄] {hero.name} ({hero.tier.value})")
        print(f"[生命] {hero.current_health}/{hero.max_health}")
        print(f"[现实债务] {hero.reality_debt}/1000 {self._get_debt_status(hero.reality_debt)}")
        print(f"[疲劳] {hero.fatigue}/100")
        print(f"\n[敌人] {enemy.name}")
        print(f"[生命] {enemy.current_health}/{enemy.max_health}")

    def _get_debt_status(self, debt):
        if debt >= 900:
            return "[极危]"
        elif debt >= 700:
            return "[危险]"
        elif debt >= 500:
            return "[警告]"
        elif debt >= 300:
            return "[注意]"
        else:
            return "[安全]"

def create_hero():
    hero = CombatUnit("零号实验体", BloodlineTier.LOW, 100)

    heat_skill = Skill(
        "热量转移", BloodlineTier.LOW, 90,
        SkillEffect(
            "成功转移热量，敌人皮肤灼伤！",
            "热量转移失控！你自己也被灼伤了！",
            25, 10, 8
        ),
        "轻微违反热力学第二定律"
    )

    charge_skill = Skill(
        "静电聚集", BloodlineTier.LOW, 85,
        SkillEffect(
            "电荷成功聚集！敌人被电击！",
            "电荷失控！你自己也被电到了！",
            20, 8, 10
        ),
        "轻微违反库伦定律"
    )

    reaction_skill = Skill(
        "反应增强", BloodlineTier.LOW, 95,
        SkillEffect(
            "反应速度大幅提升！攻击精准命中！",
            "神经负担过重！反应混乱！",
            30, 5, 5
        ),
        "轻微提升神经传导速度"
    )

    hero.add_skill(heat_skill)
    hero.add_skill(charge_skill)
    hero.add_skill(reaction_skill)

    return hero

def create_enemy():
    return Enemy("失控实验体", 80, 12)

def auto_battle_demo():
    """自动战斗演示"""
    print("="*60)
    print("[宇宙之影] 物理妥协能力系统演示")
    print("="*60)
    print("\n[核心概念]")
    print("- 超能力是物理法则对某一方向的妥协")
    print("- 每次使用能力都有代价和风险")
    print("- 现实债务累积会带来严重后果\n")

    hero = create_hero()
    enemy = create_enemy()
    battle = BattleManager()

    print(f"[战斗开始] {hero.name} vs {enemy.name}")
    print(f"英雄拥有{len(hero.skills)}个低级血统能力")
    time.sleep(1)

    # 自动战斗循环
    while True:
        battle.turn += 1
        battle.show_battle_status(hero, enemy)

        # 显示可用技能
        print(f"\n[可用技能]")
        for i, skill in enumerate(hero.skills, 1):
            success_rate = skill.get_modified_success_rate(hero)
            risk_level = skill.get_risk_level(hero)
            status = "[可用]" if hero.can_use_skill(skill) else "[不可用]"
            print(f"{status} {i}. {skill.name} - 成功率:{success_rate}% 风险:{risk_level.value}")

        # AI决策
        print(f"\n[AI决策]")
        action = battle.ai_decide_action(hero, enemy)
        print(f"选择: {action}")

        time.sleep(1)

        # 执行行动
        if action == "基础攻击":
            damage = 15 + random.randint(-3, 3)
            enemy.take_damage(damage)
            print(f"[执行] 基础攻击造成{damage}点伤害")
        elif action == "休息":
            hero.fatigue = max(0, hero.fatigue - 30)
            debt_reduction = min(hero.reality_debt, 20)
            hero.reality_debt -= debt_reduction
            print(f"[执行] 休息 - 疲劳-30 债务-{debt_reduction}")
        elif "技能" in action:
            skill_index = int(action.split()[1]) - 1
            skill = hero.skills[skill_index]
            battle.use_skill(hero, skill, enemy)

        # 敌人反击
        if enemy.is_alive():
            battle.enemy_attack(enemy, hero)

        time.sleep(1)

        # 检查战斗结束
        result = battle.check_battle_end(hero, enemy)
        if result:
            battle.show_battle_status(hero, enemy)
            battle.print_battle_result(result, hero, enemy)
            break

# 为BattleManager添加AI决策和检查方法
def ai_decide_action(self, hero, enemy):
    """AI决策行动"""
    # 简单的AI逻辑
    if hero.fatigue > 70 or hero.reality_debt > 600:
        return "休息"

    # 检查是否有安全技能
    safe_skills = [s for s in hero.skills if s.get_risk_level(hero) == RiskLevel.SAFE]
    if safe_skills and hero.can_use_skill(safe_skills[0]):
        skill_index = hero.skills.index(safe_skills[0]) + 1
        return f"技能 {skill_index}"

    # 检查是否有低风险技能
    low_risk_skills = [s for s in hero.skills if s.get_risk_level(hero) == RiskLevel.LOW]
    if low_risk_skills and hero.can_use_skill(low_risk_skills[0]):
        skill_index = hero.skills.index(low_risk_skills[0]) + 1
        return f"技能 {skill_index}"

    return "基础攻击"

def check_battle_end(self, hero, enemy):
    if not hero.is_alive():
        return "hero_defeated"
    elif not enemy.is_alive():
        return "enemy_defeated"
    elif hero.reality_debt >= 1000:
        return "debt_crisis"
    return None

def print_battle_result(self, result, hero, enemy):
    print("\n" + "="*60)
    print("[战斗结束]")
    print("="*60)

    if result == "enemy_defeated":
        print("\n[胜利]")
        print(f"敌人被击败！剩余生命: {hero.current_health} 累积债务: {hero.reality_debt}")
        if hero.reality_debt < 300:
            print("[完美] 债务控制优秀！")
        elif hero.reality_debt < 600:
            print("[良好] 注意债务累积")
        else:
            print("[险胜] 债务已达危险水平")
    elif result == "hero_defeated":
        print("\n[失败]")
        print(f"{hero.name}被击败... 剩余敌人生命: {enemy.current_health}")
    elif result == "debt_crisis":
        print("\n[债务危机]")
        print("现实债务达到临界值，现实开始排斥...")

    print(f"\n[统计] 回合数: {self.turn}")
    print("[教学] 低级能力成功率高，连续使用降低成功率，")
    print("       现实债务需时间消散，风险管理是核心")

# 绑定方法
BattleManager.ai_decide_action = ai_decide_action
BattleManager.check_battle_end = check_battle_end
BattleManager.print_battle_result = print_battle_result

if __name__ == "__main__":
    try:
        auto_battle_demo()
    except KeyboardInterrupt:
        print("\n[演示中断]")
    except Exception as e:
        print(f"\n[错误] {e}")
