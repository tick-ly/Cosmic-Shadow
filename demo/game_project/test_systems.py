"""
简单测试脚本 - 验证新系统功能
"""
import sys
sys.path.insert(0, 'D:\\program\\univers\\demo\\game_project')

from modern_warfare_system import *

def test_prediction_system():
    """测试预测系统"""
    print("=" * 60)
    print("测试预测能力系统")
    print("=" * 60)

    operator = Operator("测试操作员", AbilityTier.ELITE, is_commander=True)

    # 添加预测能力
    prediction = PredictionAbility(
        name="战斗直觉",
        prediction_type=PredictionType.COMBAT,
        accuracy=85,
        prediction_range="5-10秒",
        reality_debt_cost=15,
        cooldown=2
    )

    operator.add_prediction_ability(prediction)

    # 创建测试单位
    test_unit = WarfareUnit("测试单位", MachineScale.LEGION, operator)
    enemy = type('Enemy', (), {'name': '测试敌军'})()

    # 测试预测能力
    result = prediction.execute_prediction(test_unit, enemy)
    print(f"预测结果: {result}")

    if result['success']:
        print(f"[SUCCESS] 预测成功: {result['prediction']}")
        print(f"[SUCCESS] 精确度: {result['accuracy_used']}%")
    else:
        print(f"[FAILED] 预测失败: {result.get('reason', '未知原因')}")

    print()

def test_spatial_system():
    """测试空间系统"""
    print("=" * 60)
    print("测试空间操控能力系统")
    print("=" * 60)

    operator = Operator("测试操作员", AbilityTier.ELITE, is_commander=True)

    # 添加空间能力
    spatial = SpatialAbility(
        name="空间折叠",
        ability_type=SpatialAbilityType.SPATIAL_FOLD,
        power_level=5,
        range_m=1000,
        duration=1,
        reality_debt_cost=80,
        backlash_risk=20
    )

    operator.add_spatial_ability(spatial)

    # 创建测试单位
    test_unit = WarfareUnit("测试单位", MachineScale.LEGION, operator)

    # 创建有效的敌方目标
    class MockEnemy:
        def __init__(self, name):
            self.name = name
            self.health = 1000

        def take_damage(self, damage):
            self.health -= damage
            return max(0, damage)

    enemy = MockEnemy("测试敌军")

    # 检查是否可以使用
    can_use = spatial.can_use_spatial(operator)
    print(f"可以使用空间能力: {can_use}")

    if can_use:
        result = spatial.execute_spatial_ability(test_unit, [enemy])
        print(f"空间能力结果: {result}")

        if result['success']:
            print(f"[SUCCESS] 能力生效: {result['effect']['description']}")
        else:
            print(f"[FAILED] 能力反噬: 受到{result['backlash_damage']}点伤害")

    print()

def test_evolution_system():
    """测试进化系统"""
    print("=" * 60)
    print("测试阶段进化系统")
    print("=" * 60)

    operator = Operator("测试操作员", AbilityTier.ELITE, is_commander=True)

    print(f"当前阶段: {operator.evolution_progress.current_stage.value}")
    print(f"进化进度: {operator.evolution_progress.progress_to_next * 100:.1f}%")

    # 添加进度
    operator.evolution_progress.add_progress(0.5)
    print(f"添加进度后: {operator.evolution_progress.progress_to_next * 100:.1f}%")

    operator.evolution_progress.add_progress(0.6)
    print(f"再次添加后: {operator.evolution_progress.progress_to_next * 100:.1f}%")

    # 检查是否可以进化
    if operator.can_evolve():
        print("[CAN EVOLVE] 可以尝试进化")
        result = operator.attempt_evolution()
        print(f"进化结果: {result}")

        if result['success']:
            print(f"[SUCCESS] {result['message']}")
        else:
            print(f"[FAILED] {result['message']}")
    else:
        print("[FAILED] 进度不足，无法进化")

    print()

def test_debt_system():
    """测试债务系统"""
    print("=" * 60)
    print("测试增强现实债务后果系统")
    print("=" * 60)

    operator = Operator("测试操作员", AbilityTier.ELITE, is_commander=True)

    # 设置高债务
    operator.reality_debt = 750

    print(f"现实债务: {operator.reality_debt}/1000")

    consequences = operator.get_debt_consequences()
    print("债务后果:")
    for consequence in consequences:
        print(f"  [WARNING] {consequence}")

    # 检查现实扭曲
    distortion = operator.check_reality_distortion()
    if distortion['distortion']:
        print(f"\n现实扭曲等级: {distortion['level']}/5")
        print("扭曲效应:")
        for effect in distortion['effects']:
            print(f"  [DISTORTION] {effect}")

    # 尝试减少债务
    print(f"\n尝试减少债务...")
    result = operator.debt_system.attempt_debt_reduction(operator, "meditation")
    print(f"减少结果: {result}")

    if result['success']:
        print(f"[SUCCESS] 成功减少{result['potential_reduction']}点债务")
        print(f"当前债务: {operator.reality_debt}/1000")
    else:
        print("[FAILED] 债务减少失败")

    print()

if __name__ == "__main__":
    try:
        test_prediction_system()
        test_spatial_system()
        test_evolution_system()
        test_debt_system()

        print("=" * 60)
        print("[COMPLETE] 所有系统测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
