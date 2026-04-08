"""
宇宙之影 - 文本版演示
Shadow of the Universe - Text-based Demo

物理妥协能力系统原型演示
"""

import random
import time
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class BloodlineTier(Enum):
    """血统等级"""
    LOW = "低级血统"
    MEDIUM = "中级血统"
    HIGH = "高级血统"

class RiskLevel(Enum):
    """风险等级"""
    SAFE = "安全"
    LOW = "低风险"
    MEDIUM = "中等风险"
    HIGH = "高风险"
    CRITICAL = "极高风险"

@dataclass
class SkillEffect:
    """技能效果"""
    success_description: str
    failure_description: str
    success_damage: int
    failure_damage: int
    reality_debt: int

class Skill:
    """技能类"""

    def __init__(self, name: str, tier: BloodlineTier, base_success_rate: int,
                 effect: SkillEffect, description: str):
        self.name = name
        self.tier = tier
        self.base_success_rate = base_success_rate
        self.effect = effect
        self.description = description
        self.consecutive_uses = 0

    def get_modified_success_rate(self, user: 'CombatUnit') -> int:
        """获取修正后的成功率"""
        rate = self.base_success_rate

        # 连续使用惩罚
        rate -= self.consecutive_uses * 5

        # 债务过高惩罚
        if user.reality_debt > 500:
            rate -= 10

        # 疲劳惩罚
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

        # 核心资源
        self.reality_debt = 0  # 现实债务
        self.fatigue = 0       # 疲劳度

        # 能力
        self.skills: List[Skill] = []

        # 状态
        self.consecutive_uses = 0

    def add_skill(self, skill: Skill):
        """添加技能"""
        self.skills.append(skill)

    def can_use_skill(self, skill: Skill) -> bool:
        """检查是否能使用技能"""
        # 债务过高时禁止使用高级技能
        if self.reality_debt > 800 and skill.tier != BloodlineTier.LOW:
            return False

        # 疲劳过高时禁止使用任何技能
        if self.fatigue >= 100:
            return False

        return True

    def take_damage(self, damage: int):
        """受到伤害"""
        self.current_health = max(0, self.current_health - damage)

    def is_alive(self) -> bool:
        """是否存活"""
        return self.current_health > 0

class Enemy:
    """敌人"""

    def __init__(self, name: str, health: int, attack_power: int):
        self.name = name
        self.max_health = health
        self.current_health = health
        self.attack_power = attack_power

    def take_damage(self, damage: int):
        """受到伤害"""
        self.current_health = max(0, self.current_health - damage)

    def is_alive(self) -> bool:
        """是否存活"""
        return self.current_health > 0

class BattleManager:
    """战斗管理器"""

    def __init__(self):
        self.turn = 0
        self.combat_log: List[str] = []

    def use_skill(self, user: CombatUnit, skill: Skill, target: Enemy) -> bool:
        """使用技能"""
        if not user.can_use_skill(skill):
            self.combat_log.append(f"[X] {user.name}无法使用{skill.name}！")
            return False

        # 计算成功率
        success_rate = skill.get_modified_success_rate(user)
        risk_level = skill.get_risk_level(user)
        roll = random.randint(1, 100)

        print(f"\n[*] {user.name}使用{skill.name}！")
        print(f"[成功率: {success_rate}%] [风险等级: {risk_level.value}]")
        print(f"[投掷: {roll} vs 需求: {success_rate}]")

        # 判定成功/失败
        if roll <= success_rate:
            return self._skill_success(user, skill, target)
        else:
            return self._skill_failure(user, skill, target)

    def _skill_success(self, user: CombatUnit, skill: Skill, target: Enemy) -> bool:
        """技能成功"""
        print(f"[SUCCESS] {skill.effect.success_description}")
        target.take_damage(skill.effect.success_damage)
        user.reality_debt += skill.effect.reality_debt
        user.fatigue += 10
        skill.consecutive_uses += 1

        self.combat_log.append(
            f"[OK] {user.name}成功使用{skill.name}！"
            f"敌人受到{skill.effect.success_damage}点伤害。"
            f"现实债务+{skill.effect.reality_debt}"
        )

        return True

    def _skill_failure(self, user: CombatUnit, skill: Skill, target: Enemy) -> bool:
        """技能失败"""
        print(f"[FAIL] {skill.effect.failure_description}")
        user.take_damage(skill.effect.failure_damage)
        user.reality_debt += int(skill.effect.reality_debt * 1.5)  # 失败时债务增加
        user.fatigue += 20

        self.combat_log.append(
            f"[X] {user.name}使用{skill.name}失败！"
            f"自身受到{skill.effect.failure_damage}点伤害。"
            f"现实债务+{int(skill.effect.reality_debt * 1.5)}"
        )

        return False

    def enemy_attack(self, enemy: Enemy, target: CombatUnit):
        """敌人攻击"""
        damage = enemy.attack_power + random.randint(-2, 2)
        target.take_damage(damage)

        print(f"\n[!] {enemy.name}攻击{target.name}！")
        print(f"[DAMAGE] 造成{damage}点伤害！")

        self.combat_log.append(f"[!] {enemy.name}对{target.name}造成{damage}点伤害")

    def check_battle_end(self, hero: CombatUnit, enemy: Enemy) -> Optional[str]:
        """检查战斗是否结束"""
        if not hero.is_alive():
            return "hero_defeated"
        elif not enemy.is_alive():
            return "enemy_defeated"
        elif hero.reality_debt >= 1000:
            return "debt_crisis"
        return None

    def show_battle_status(self, hero: CombatUnit, enemy: Enemy):
        """显示战斗状态"""
        print("\n" + "="*50)
        print(f"[BATTLE STATUS] Turn {self.turn}")
        print("="*50)

        # 英雄状态
        print(f"\n[HERO] {hero.name} ({hero.tier.value})")
        health_bar = self._create_bar(hero.current_health, hero.max_health)
        print(f"[HP] {hero.current_health}/{hero.max_health} {health_bar}")

        debt_bar = self._create_bar(hero.reality_debt, 1000, reverse=True)
        debt_status = self._get_debt_status(hero.reality_debt)
        print(f"[DEBT] {hero.reality_debt}/1000 {debt_bar} [{debt_status}]")

        fatigue_bar = self._create_bar(hero.fatigue, 100, reverse=True)
        print(f"[FATIGUE] {hero.fatigue}/100 {fatigue_bar}")

        # 敌人状态
        print(f"\n[ENEMY] {enemy.name}")
        enemy_health_bar = self._create_bar(enemy.current_health, enemy.max_health)
        print(f"[HP] {enemy.current_health}/{enemy.max_health} {enemy_health_bar}")

    def _create_bar(self, current, maximum, length=20, reverse=False):
        """创建状态条"""
        ratio = current / maximum
        filled = int(ratio * length)

        if reverse:
            # 疲劳和债务使用反向字符（越高越坏）
            if ratio < 0.3:
                char = "+"
            elif ratio < 0.6:
                char = "="
            elif ratio < 0.8:
                char = "#"
            else:
                char = "!"
        else:
            # 生命值使用正向字符（越高越好）
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
            return "CRITICAL"
        elif debt >= 700:
            return "DANGER"
        elif debt >= 500:
            return "WARNING"
        elif debt >= 300:
            return "CAUTION"
        else:
            return "SAFE"

def create_hero() -> CombatUnit:
    """创建英雄"""
    hero = CombatUnit("零号实验体", BloodlineTier.LOW, max_health=100)

    # 创建低级技能
    heat_skill = Skill(
        name="热量转移",
        tier=BloodlineTier.LOW,
        base_success_rate=90,
        effect=SkillEffect(
            success_description="你成功转移热量，敌人皮肤灼伤！",
            failure_description="热量转移失控！你自己也被灼伤了！",
            success_damage=25,
            failure_damage=10,
            reality_debt=8
        ),
        description="轻微违反热力学第二定律，转移局部热量"
    )

    charge_skill = Skill(
        name="静电聚集",
        tier=BloodlineTier.LOW,
        base_success_rate=85,
        effect=SkillEffect(
            success_description="电荷成功聚集！敌人被电击！",
            failure_description="电荷失控！你自己也被电到了！",
            success_damage=20,
            failure_damage=8,
            reality_debt=10
        ),
        description="轻微违反库伦定律，聚集静电电荷"
    )

    reaction_skill = Skill(
        name="反应增强",
        tier=BloodlineTier.LOW,
        base_success_rate=95,
        effect=SkillEffect(
            success_description="反应速度大幅提升！攻击精准命中！",
            failure_description="神经负担过重！反应混乱！",
            success_damage=30,
            failure_damage=5,
            reality_debt=5
        ),
        description="轻微提升神经传导速度"
    )

    hero.add_skill(heat_skill)
    hero.add_skill(charge_skill)
    hero.add_skill(reaction_skill)

    return hero

def create_enemy() -> Enemy:
    """创建敌人"""
    return Enemy("失控实验体", health=80, attack_power=12)

def main():
    """主函数"""
    print("[宇宙之影] 物理妥协能力系统演示")
    print("=" * 50)
    print("\n核心概念：")
    print("   超能力是物理法则对某一方向的妥协")
    print("   每次使用能力都有代价和风险")
    print("   现实债务累积会带来严重后果\n")

    input("按回车键开始...")

    # 初始化战斗
    hero = create_hero()
    enemy = create_enemy()
    battle = BattleManager()

    print(f"\n[战斗开始]")
    print(f"   {hero.name} vs {enemy.name}")
    print(f"   英雄拥有{len(hero.skills)}个低级血统能力")

    time.sleep(2)

    # 战斗循环
    while True:
        battle.turn += 1

        # 显示状态
        battle.show_battle_status(hero, enemy)

        # 显示可用技能
        print(f"\n[可用技能]")
        for i, skill in enumerate(hero.skills, 1):
            success_rate = skill.get_modified_success_rate(hero)
            risk_level = skill.get_risk_level(hero)
            can_use = "[OK]" if hero.can_use_skill(skill) else "[XX]"
            print(f"   {can_use} {i}. {skill.name}")
            print(f"      成功率: {success_rate}% | 风险: {risk_level.value}")
            print(f"      效果: {skill.effect.success_description}")
            print(f"      代价: 债务+{skill.effect.reality_debt}, 疲劳+10")

        # 玩家选择
        print(f"\n[选择行动]")
        print(f"   1-{len(hero.skills)}. 使用技能")
        print(f"   0. 基础攻击 (无风险，伤害15)")
        print(f"   -1. 休息 (恢复疲劳，减少债务)")

        try:
            choice = input(f"\n请选择: ").strip()

            if choice == "-1":
                # 休息
                print(f"\n[REST] {hero.name}选择休息...")
                hero.fatigue = max(0, hero.fatigue - 30)
                debt_reduction = min(hero.reality_debt, 20)
                hero.reality_debt -= debt_reduction
                print(f"   疲劳-30，债务-{debt_reduction}")

                # 敌人攻击
                battle.enemy_attack(enemy, hero)

            elif choice == "0":
                # 基础攻击
                print(f"\n[ATTACK] {hero.name}进行基础攻击...")
                damage = 15 + random.randint(-3, 3)
                enemy.take_damage(damage)
                print(f"   造成{damage}点伤害！")
                battle.combat_log.append(f"[ATTACK] {hero.name}基础攻击造成{damage}伤害")

                # 敌人攻击
                battle.enemy_attack(enemy, hero)

            elif choice.isdigit() and 1 <= int(choice) <= len(hero.skills):
                # 使用技能
                skill_index = int(choice) - 1
                skill = hero.skills[skill_index]

                if hero.can_use_skill(skill):
                    battle.use_skill(hero, skill, enemy)

                    # 敌人攻击（如果还活着）
                    if enemy.is_alive():
                        battle.enemy_attack(enemy, hero)
                else:
                    print(f"\n[X] 无法使用{skill.name}！")
                    continue

            else:
                print("[X] 无效选择！")
                continue

        except KeyboardInterrupt:
            print("\n\n游戏被中断")
            return
        except Exception as e:
            print(f"[ERROR] 发生错误: {e}")
            continue

        # 检查战斗结束
        result = battle.check_battle_end(hero, enemy)
        if result:
            battle.show_battle_status(hero, enemy)
            print_battle_result(result, hero, enemy, battle)
            break

        time.sleep(1)

def print_battle_result(result: str, hero: CombatUnit, enemy: Enemy, battle: BattleManager):
    """打印战斗结果"""
    print("\n" + "="*50)
    print("[战斗结束]")
    print("="*50)

    if result == "enemy_defeated":
        print("\n[VICTORY]")
        print(f"   敌人被击败！")
        print(f"   剩余生命: {hero.current_health}")
        print(f"   累积债务: {hero.reality_debt}")

        if hero.reality_debt < 300:
            print("\n[PERFECT] 完美胜利！债务控制良好！")
        elif hero.reality_debt < 600:
            print("\n[GOOD] 胜利！需要注意债务累积。")
        else:
            print("\n[WARNING] 险胜！债务已达危险水平！")

    elif result == "hero_defeated":
        print("\n[DEFEAT]")
        print(f"   {hero.name}被击败...")
        print(f"   剩余敌人生命: {enemy.current_health}")

    elif result == "debt_crisis":
        print("\n[CRISIS]")
        print(f"   债务达到临界值，现实开始排斥...")
        print(f"   游戏结束")

    # 战斗统计
    print(f"\n[战斗统计]")
    print(f"   回合数: {battle.turn}")
    print(f"   战斗日志: {len(battle.combat_log)}条")

    print(f"\n[教学总结]")
    print(f"   - 低级能力成功率较高(85-95%)")
    print(f"   - 连续使用会降低成功率")
    print(f"   - 现实债务累积需要时间消散")
    print(f"   - 休息可以降低疲劳和债务")
    print(f"   - 风险管理是核心玩法")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n游戏结束")
