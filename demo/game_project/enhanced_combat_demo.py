"""
宇宙之影 - 增强战斗系统演示
Enhanced Combat System Demo

演示新增的四个核心系统：
1. 预测能力机制
2. 空间操控能力系统
3. 阶段进化系统
4. 增强现实债务后果系统
"""

import random
import time
from modern_warfare_system import EnemyForce, MachineScale

class EnhancedCombatDemo:
    def __init__(self):
        print("=" * 80)
        print("[宇宙之影] 增强战斗系统演示")
        print("=" * 80)
        print("\n[新增系统]")
        print("- 预测能力系统：战斗/战术/资源预测")
        print("- 空间操控能力：空间折叠/时间减缓/物理修改")
        print("- 阶段进化系统：基础→魔→神")
        print("- 增强现实债务后果系统")

    def create_enhanced_operator(self):
        """创建增强型操作员"""
        operator = Operator("预测者零号", AbilityTier.ELITE, is_commander=True)

        # 添加预测能力
        combat_prediction = PredictionAbility(
            name="战斗直觉",
            prediction_type=PredictionType.COMBAT,
            accuracy=85,
            prediction_range="5-10秒",
            reality_debt_cost=15,
            cooldown=2
        )

        tactical_prediction = PredictionAbility(
            name="战术洞察",
            prediction_type=PredictionType.TACTICAL,
            accuracy=75,
            prediction_range="1-2小时",
            reality_debt_cost=25,
            cooldown=3
        )

        resource_prediction = PredictionAbility(
            name="资源感知",
            prediction_type=PredictionType.RESOURCE,
            accuracy=70,
            prediction_range="1-3天",
            reality_debt_cost=20,
            cooldown=4
        )

        # 添加空间能力
        spatial_fold = SpatialAbility(
            name="空间折叠",
            ability_type=SpatialAbilityType.SPATIAL_FOLD,
            power_level=5,
            range_m=1000,
            duration=1,
            reality_debt_cost=80,
            backlash_risk=20
        )

        time_slow = SpatialAbility(
            name="时间减缓",
            ability_type=SpatialAbilityType.TIME_SLOW,
            power_level=4,
            range_m=500,
            duration=3,
            reality_debt_cost=60,
            backlash_risk=15
        )

        physics_modify = SpatialAbility(
            name="物理重构",
            ability_type=SpatialAbilityType.PHYSICS_MODIFY,
            power_level=6,
            range_m=200,
            duration=2,
            reality_debt_cost=100,
            backlash_risk=25
        )

        operator.add_prediction_ability(combat_prediction)
        operator.add_prediction_ability(tactical_prediction)
        operator.add_prediction_ability(resource_prediction)
        operator.add_spatial_ability(spatial_fold)
        operator.add_spatial_ability(time_slow)
        operator.add_spatial_ability(physics_modify)

        return operator

    def create_enemy_force(self):
        """创建敌方力量"""
        # 修复参数错位：EnemyForce(name, scale, combat_power, evasion)
        # combat_power=600 → max_health=3000，与原来期望一致
        enemy = EnemyForce("敌军精锐部队", MachineScale.LEGION, 600, 80)
        return enemy

    def demonstrate_prediction_system(self, operator, user_unit, enemy):
        """演示预测能力系统"""
        print("\n" + "=" * 80)
        print("[系统演示] 预测能力系统")
        print("=" * 80)

        for pred_ability in operator.prediction_abilities:
            print(f"\n[预测能力] {pred_ability.name}")
            print(f"[类型] {pred_ability.prediction_type.value}")
            print(f"[精确度] {pred_ability.accuracy}%")
            print(f"[范围] {pred_ability.prediction_range}")
            print(f"[代价] {pred_ability.reality_debt_cost}点现实债务")

            if pred_ability.can_use_prediction(operator):
                result = pred_ability.execute_prediction(user_unit, enemy)
                if result["success"]:
                    print(f"[预测成功] {result['prediction']}")
                    print(f"[精确度] 实际使用: {result['accuracy_used']}%")
                    operator.reality_debt += result['debt_cost']
                    print(f"[债务增加] +{result['debt_cost']}点")
                else:
                    print(f"[预测失败] {result['reason']}")
            else:
                print("[无法使用] 现实债务或疲劳过高")

            time.sleep(1)

    def demonstrate_spatial_system(self, operator, user_unit, enemy):
        """演示空间操控系统"""
        print("\n" + "=" * 80)
        print("[系统演示] 空间操控能力系统")
        print("=" * 80)

        for spatial_ability in operator.spatial_abilities[:2]:  # 演示前两个能力
            print(f"\n[空间能力] {spatial_ability.name}")
            print(f"[类型] {spatial_ability.ability_type.value}")
            print(f"[强度] Lv.{spatial_ability.power_level}")
            print(f"[范围] {spatial_ability.range_m}米")
            print(f"[反噬风险] {spatial_ability.backlash_risk}%")
            print(f"[代价] {spatial_ability.reality_debt_cost}点现实债务")

            if spatial_ability.can_use_spatial(operator):
                result = spatial_ability.execute_spatial_ability(user_unit, [enemy])
                if result["success"]:
                    print(f"[能力生效] {result['effect']['description']}")
                    if 'damage' in result['effect']:
                        print(f"[造成伤害] {result['effect']['damage']}点")
                    operator.reality_debt += result['debt_cost']
                    print(f"[债务增加] +{result['debt_cost']}点")
                else:
                    print(f"[能力反噬] 受到{result['backlash_damage']}点反噬伤害")
                    operator.reality_debt += result['debt_cost'] // 2
            else:
                print("[无法使用] 现实债务或疲劳过高")

            time.sleep(1)

    def demonstrate_evolution_system(self, operator):
        """演示阶段进化系统"""
        print("\n" + "=" * 80)
        print("[系统演示] 阶段进化系统")
        print("=" * 80)

        print(f"\n[当前阶段] {operator.evolution_progress.current_stage.value}")
        print(f"[进化进度] {operator.evolution_progress.progress_to_next * 100:.1f}%")
        print("[阶段修正]")
        for key, value in operator.evolution_progress.stage_modifiers.items():
            print(f"  {key}: {value}")

        # 模拟添加进化进度
        print("\n[模拟进化] 添加进度...")
        operator.evolution_progress.add_progress(0.3)
        print(f"[当前进度] {operator.evolution_progress.progress_to_next * 100:.1f}%")

        operator.evolution_progress.add_progress(0.4)
        print(f"[当前进度] {operator.evolution_progress.progress_to_next * 100:.1f}%")

        operator.evolution_progress.add_progress(0.3)
        print(f"[当前进度] {operator.evolution_progress.progress_to_next * 100:.1f}%")

        if operator.can_evolve():
            print("\n[进化条件满足] 可以尝试进化！")
            choice = input("是否尝试进化？(y/n): ")

            if choice.lower() == 'y':
                result = operator.attempt_evolution()
                if result["success"]:
                    print(f"[进化成功] {result['message']}")
                    print(f"[新阶段] {operator.evolution_progress.current_stage.value}")
                    print("[新阶段修正]")
                    for key, value in operator.evolution_progress.stage_modifiers.items():
                        print(f"  {key}: {value}")
                else:
                    print(f"[进化失败] {result['message']}")
                    print(f"[成功率] {result['success_chance']}%")

    def demonstrate_debt_system(self, operator):
        """演示现实债务系统"""
        print("\n" + "=" * 80)
        print("[系统演示] 增强现实债务后果系统")
        print("=" * 80)

        # 模拟高债务状态
        operator.reality_debt = 750

        print(f"\n[现实债务] {operator.reality_debt}/1000")
        print("[债务后果]")
        consequences = operator.get_debt_consequences()
        for consequence in consequences:
            print(f"  ⚠ {consequence}")

        print("\n[现实扭曲检测]")
        distortion = operator.check_reality_distortion()
        if distortion["distortion"]:
            print(f"[扭曲等级] {distortion['level']}/5")
            print("[扭曲效应]")
            for effect in distortion['effects']:
                print(f"  ▲ {effect}")

        # 演示债务减少方法
        print("\n[债务减少方法]")
        print("1. 休息 (减少50点，需1回合)")
        print("2. 冥想 (减少100点，需2回合，85%成功率)")
        print("3. 现实锚定 (减少200点，需3回合，60%成功率)")
        print("4. 生命牺牲 (减少400点，50点生命值，95%成功率)")

        # 尝试减少债务
        print("\n[尝试减少债务]")
        result = operator.debt_system.attempt_debt_reduction(operator, "meditation")
        if result["success"]:
            print(f"[减少成功] 减少{result['potential_reduction']}点现实债务")
            print(f"[当前债务] {operator.reality_debt}/1000")
        else:
            print("[减少失败] 冥想失败，未能减少现实债务")

    def run_full_demo(self):
        """运行完整演示"""
        try:
            # 创建角色
            operator = self.create_enhanced_operator()
            user_unit = WarfareUnit("第一军团", MachineScale.LEGION, operator)
            enemy = self.create_enemy_force()

            # 演示各个系统
            self.demonstrate_prediction_system(operator, user_unit, enemy)
            self.demonstrate_spatial_system(operator, user_unit, enemy)
            self.demonstrate_evolution_system(operator)
            self.demonstrate_debt_system(operator)

            print("\n" + "=" * 80)
            print("[演示完成] 所有新系统演示完毕")
            print("=" * 80)

            print("\n[系统总结]")
            print("✅ 预测能力：提供战术信息和未来洞察")
            print("✅ 空间能力：强大的战场控制手段")
            print("✅ 阶段进化：角色成长和力量提升")
            print("✅ 债务系统：使用能力的代价和风险")

            print(f"\n[操作员状态]")
            print(f"[现实债务] {operator.reality_debt}/1000")
            print(f"[疲劳度] {operator.fatigue}/100")
            print(f"[进化阶段] {operator.evolution_progress.current_stage.value}")
            print(f"[能力倍率] {operator.get_total_ability_multiplier()}x")
            print(f"[债务倍率] {operator.get_debt_multiplier()}x")

        except KeyboardInterrupt:
            print("\n[演示中断]")
        except Exception as e:
            print(f"\n[错误] {e}")

if __name__ == "__main__":
    demo = EnhancedCombatDemo()
    demo.run_full_demo()
