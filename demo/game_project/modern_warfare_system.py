"""
宇宙之影 - 现代战争战斗系统
Shadow of the Universe - Modern Warfare Combat System

核心改进：
1. 超能分类：基础/进阶/精英（平等称呼）
2. 战争机器分级：单兵/小队/军团
3. 指挥官光环buff系统
4. 现代武器火力参考
5. 信息传递速度差异

新增功能：
6. 预测能力系统：战斗/战术/资源预测
7. 空间操控能力：空间折叠/时间减缓/物理修改
8. 阶段进化系统：基础→魔→神
9. 增强现实债务后果系统
"""

import random
import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Set
from enum import Enum

class AbilityTier(Enum):
    """超能等级（平等称呼）"""
    BASIC = "基础超能"
    ADVANCED = "进阶超能"
    ELITE = "精英超能"

class MachineScale(Enum):
    """战争机器规模"""
    INDIVIDUAL = "单兵装备"
    SQUAD = "小队单位"
    LEGION = "军团编制"

class UnitType(Enum):
    """单位类型"""
    INFANTRY = "步兵"
    ARMORED = "装甲"
    ARTILLERY = "炮兵"
    AIR_SUPPORT = "空中支援"
    COMMAND = "指挥"
    SPECIAL_FORCES = "特种"


# ==================== 武器分类体系 ====================

class WeaponCategory(Enum):
    """
    武器投射方式分类

    - BALLISTIC（弹道）：子弹、炮弹等物理抛射物，有飞行时间、距离衰减
    - CRUISE（巡航）：导弹等有制导系统，发射后仍可追踪目标
    - ENERGY（能量）：激光、等离子等定向能武器，即时命中，有过热机制
    """
    BALLISTIC = "弹道"
    CRUISE = "巡航"
    ENERGY = "能量"


class WeaponClass(Enum):
    """武器类别（按用途/规格细分）"""
    # --- 弹道类 ---
    PISTOL = "手枪"
    RIFLE = "步枪"
    SMG = "冲锋枪"
    SNIPER = "狙击步枪"
    MG = "机枪"
    SHOTGUN = "霰弹枪"
    CANNON = "加农炮"
    HOWITZER = "榴弹炮"
    MORTAR = "迫击炮"

    # --- 巡航类 ---
    ATGM = "反坦克导弹"       # 反装甲
    AAM = "防空导弹"           # 防空
    CRUISE_MISSILE = "巡航导弹"  # 对地

    # --- 能量类 ---
    LASER = "激光武器"
    PLASMA = "等离子武器"
    PARTICLE = "粒子束武器"
    MICROWAVE = "微波武器"


@dataclass
class BallisticProperties:
    """弹道类专属属性"""
    projectile_speed: int = 800   # m/s，飞行速度（影响远距离延迟）
    falloff_start: int = 300     # 米，此距离后精度开始衰减
    falloff_rate: float = 0.002  # 每超过falloff_start 1米，命中-衰减率


@dataclass
class CruiseProperties:
    """巡航类专属属性"""
    lock_on_time: int = 1       # 锁定目标所需回合数
    tracking: int = 75           # 追踪能力（被规避的概率降低）
    countermeasure_vuln: int = 30 # 对抗干扰的脆弱性（被拦截概率%）
    flight_speed: int = 300      # m/s，巡航速度
    terminal_guidance: bool = True # 末制导（是否在末端主动追踪）


@dataclass
class EnergyProperties:
    """能量类专属属性"""
    sustained_multiplier: float = 1.5  # 持续命中时的伤害倍率
    heat_per_shot: int = 15      # 每发产生的热量
    heat_capacity: int = 60       # 最大热量上限
    heat_dissipation: int = 8     # 每回合散热量
    armor_ignores_pct: int = 40   # 无视护甲的百分比（能量束穿甲）
    beam_width: int = 0           # 光束宽度，0=点对点，>0=范围伤害


class ModernWeapon:
    """
    现代武器系统

    武器分类：
    - 弹道（BALLISTIC）：子弹/炮弹，有飞行时间、距离衰减、穿甲率
    - 巡航（CRUISE）：导弹，有锁定时间、追踪能力、拦截风险
    - 能量（ENERGY）：激光/等离子，瞬时命中、有过热、可穿甲
    """
    def __init__(
        self,
        name: str,
        weapon_class: WeaponClass,
        category: WeaponCategory,
        damage: int,
        rate_of_fire: int,
        accuracy: int,
        range_m: int,
        magazine_size: int,
        weight: float,
        special_features: List[str],
        anti_air: bool = False,
        suppression: bool = False,
        # 通用进阶
        armor_penetration: int = 0,   # 穿甲值（直接减甲）
        armor_shred: int = 0,          # 护甲削弱（每次命中永久削甲）
        # 弹道专属
        ballistic: BallisticProperties = None,
        # 巡航专属
        cruise: CruiseProperties = None,
        # 能量专属
        energy: EnergyProperties = None,
    ):
        self.name = name
        self.weapon_class = weapon_class
        self.category = category
        self.damage = damage
        self.rate_of_fire = rate_of_fire
        self.accuracy = accuracy          # 基准精度（近距离完全发挥）
        self.range_m = range_m            # 最大射程
        self.magazine_size = magazine_size
        self.current_ammo = magazine_size
        self.weight = weight
        self.special_features = special_features
        self.anti_air = anti_air
        self.suppression = suppression
        self.armor_penetration = armor_penetration
        self.armor_shred = armor_shred

        # 弹药状态
        self._is_reloading = False
        self._reload_turns = 0

        # 弹道属性
        self.ballistic = ballistic or (
            BallisticProperties()
            if category == WeaponCategory.BALLISTIC else None
        )
        # 巡航属性
        self.cruise = cruise or (
            CruiseProperties()
            if category == WeaponCategory.CRUISE else None
        )
        # 能量属性
        self.energy = energy or (
            EnergyProperties()
            if category == WeaponCategory.ENERGY else None
        )

        # 能量武器过热状态（外部持有）
        self._heat = 0

    def __repr__(self):
        return f"ModernWeapon({self.name}, {self.category.value}, dmg={self.damage})"

    def can_fire(self) -> bool:
        """武器是否可以开火"""
        if self._is_reloading:
            return False
        if self.current_ammo <= 0:
            return False
        return True

    def fire(self, shots: int = 1) -> int:
        """消耗弹药，返回实际射击数"""
        if self._is_reloading:
            return 0
        actual = min(shots, self.current_ammo)
        self.current_ammo -= actual
        return actual

    def needs_reload(self) -> bool:
        """是否需要换弹"""
        return self.current_ammo <= 0 and not self._is_reloading

    def start_reload(self, turns: int = 1):
        """开始换弹"""
        self._is_reloading = True
        self._reload_turns = turns

    def update_reload(self) -> bool:
        """更新换弹状态，返回是否完成"""
        if not self._is_reloading:
            return False
        self._reload_turns -= 1
        if self._reload_turns <= 0:
            self._is_reloading = False
            self.current_ammo = self.magazine_size
            return True
        return False

    def get_hit_chance_at_range(self, distance: int, target_mobility: int = 0) -> float:
        """
        计算在给定距离上的命中概率（考虑类别特性）

        Args:
            distance: 目标距离（米）
            target_mobility: 目标机动性（影响巡航类追踪）
        """
        if distance > self.range_m:
            return 0.0

        # 弹道类：距离越远精度越低
        if self.category == WeaponCategory.BALLISTIC and self.ballistic:
            acc = self.accuracy
            if distance > self.ballistic.falloff_start:
                over = distance - self.ballistic.falloff_start
                acc -= int(over * self.ballistic.falloff_rate)
            return max(0.05, acc / 100)

        # 巡航类：锁定后才能发射，追踪决定最终命中率
        if self.category == WeaponCategory.CRUISE and self.cruise:
            base = self.accuracy
            # 目标机动性越高，追踪效果越差，命中率越低
            tracking_penalty = max(0, target_mobility - self.cruise.tracking) // 5
            return max(0.05, (base - tracking_penalty) / 100)

        # 能量类：即时命中，距离不影响精度
        if self.category == WeaponCategory.ENERGY:
            return self.accuracy / 100

        return self.accuracy / 100

    def get_effective_damage(self, distance: int = 0, is_sustained: bool = False) -> int:
        """
        获取有效伤害（考虑距离衰减和类别特性）

        Args:
            distance: 射击距离（米）
            is_sustained: 是否为持续命中（能量武器持续照射增伤）
        """
        dmg = self.damage

        # 弹道类：距离不影响弹道伤害（终末速度补偿）
        # 巡航类：引信触发，有轻微距离惩罚
        if self.category == WeaponCategory.CRUISE:
            dist_penalty = int(distance / 500)  # 每500米-1伤害
            dmg = max(1, dmg - dist_penalty)

        # 能量类：持续照射（激光枪持续命中）额外伤害
        if self.category == WeaponCategory.ENERGY and self.energy and is_sustained:
            dmg = int(dmg * self.energy.sustained_multiplier)

        return dmg

    def get_heat(self) -> int:
        return getattr(self, '_heat', 0)

    def add_heat(self, amount: int):
        """热量增加（能量武器）"""
        if self.category != WeaponCategory.ENERGY or not self.energy:
            return
        self._heat = min(self.energy.heat_capacity, self._heat + amount)

    def dissipate_heat(self) -> int:
        """散热，返回剩余热量"""
        if self.category != WeaponCategory.ENERGY or not self.energy:
            return 0
        self._heat = max(0, self._heat - self.energy.heat_dissipation)
        return self._heat

    def is_overheated(self) -> bool:
        """是否过热（能量武器）"""
        if self.category != WeaponCategory.ENERGY or not self.energy:
            return False
        return self._heat >= self.energy.heat_capacity

@dataclass
class AbilityEffect:
    """超能效果"""
    name: str
    tier: AbilityTier
    description: str
    success_rate: int
    reality_debt: int
    duration: int

    # 增强效果
    damage_boost: int = 0
    accuracy_boost: int = 0
    dodge_boost: int = 0
    range_boost: int = 0
    defense_boost: int = 0
    speed_boost: int = 0
    detection_boost: int = 0
    communication_boost: int = 0  # 信息传递速度
    morale_boost: int = 0
    repair_rate: int = 0

    # 光环效果（指挥官专用）
    aura_range: int = 0  # 光环影响范围
    aura_effects: List[str] = None  # 光环提供的效果

class Ability:
    """超能力"""
    def __init__(self, name: str, tier: AbilityTier, effect: AbilityEffect):
        self.name = name
        self.tier = tier
        self.effect = effect
        self.consecutive_uses = 0
        self.active_duration = 0

    def get_modified_success_rate(self, operator) -> int:
        """计算修正成功率"""
        rate = self.effect.success_rate
        rate -= self.consecutive_uses * 5
        if operator.reality_debt > 500:
            rate -= 10
        if operator.fatigue > 70:
            rate -= 15
        return max(10, min(95, rate))

    def get_risk_level(self, operator) -> str:
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

# ==================== 新增系统类 ====================

class PredictionType(Enum):
    """预测能力类型"""
    COMBAT = "战斗预测"      # 短期：几秒到几分钟
    TACTICAL = "战术预测"    # 中期：几小时到几天
    RESOURCE = "资源预测"    # 长期：几个月到几年

@dataclass
class PredictionAbility:
    """预测能力系统"""
    name: str
    prediction_type: PredictionType
    accuracy: int  # 预测精确度 0-100
    prediction_range: str  # 预测时间范围
    reality_debt_cost: int  # 现实债务代价
    cooldown: int  # 冷却回合数
    active_duration: int = 0  # 持续时间

    def can_use_prediction(self, operator) -> bool:
        """判断是否可以使用预测"""
        debt_penalty = max(0, (operator.reality_debt - 700) // 10)
        fatigue_penalty = max(0, (operator.fatigue - 50) // 5)
        modified_accuracy = self.accuracy - debt_penalty - fatigue_penalty
        return modified_accuracy > 30

    def execute_prediction(self, unit, target) -> Dict:
        """执行预测能力"""
        if not self.can_use_prediction(unit.operator):
            return {"success": False, "reason": "现实债务或疲劳过高", "prediction_type": self.prediction_type, "accuracy_used": 0, "debt_cost": 0}

        # 计算实际精确度
        debt_penalty = max(0, (unit.operator.reality_debt - 700) // 10)
        fatigue_penalty = max(0, (unit.operator.fatigue - 50) // 5)
        actual_accuracy = self.accuracy - debt_penalty - fatigue_penalty

        # 执行预测
        success = random.randint(1, 100) <= actual_accuracy

        result = {
            "success": success,
            "prediction_type": self.prediction_type,
            "accuracy_used": actual_accuracy,
            "debt_cost": self.reality_debt_cost
        }

        if success:
            if self.prediction_type == PredictionType.COMBAT:
                result["prediction"] = self._combat_prediction(target)
            elif self.prediction_type == PredictionType.TACTICAL:
                result["prediction"] = self._tactical_prediction(target)
            elif self.prediction_type == PredictionType.RESOURCE:
                result["prediction"] = self._resource_prediction()

        return result

    def _combat_prediction(self, target) -> str:
        """战斗预测：预判敌方攻击轨迹"""
        predictions = [
            f"敌方{target.name}准备发起猛攻！",
            f"检测到{target.name}的弱点暴露",
            f"预判{target.name}将使用特殊战术",
            f"{target.name}的攻击模式已分析完毕"
        ]
        return random.choice(predictions)

    def _tactical_prediction(self, target) -> str:
        """战术预测：预测敌方战略意图"""
        predictions = [
            f"敌方{target.name}意图包围我方",
            f"分析显示{target.name}将采取守势",
            f"预判{target.name}将在2回合内发动总攻",
            f"敌方{target.name}正在寻求撤退路线"
        ]
        return random.choice(predictions)

    def _resource_prediction(self) -> str:
        """资源预测：预知资源分布和变化"""
        predictions = [
            "东北方向发现重要资源点",
            "预计3回合后将有补给到达",
            "检测到敌方资源运输线",
            "预测该区域资源将在短时间内枯竭"
        ]
        return random.choice(predictions)

class SpatialAbilityType(Enum):
    """空间能力类型"""
    SPATIAL_FOLD = "空间折叠"    # 瞬移打击
    TIME_SLOW = "时间减缓"       # 提高反应速度
    PHYSICS_MODIFY = "物理修改"  # 修改物理常数

@dataclass
class SpatialAbility:
    """空间操控能力系统"""
    name: str
    ability_type: SpatialAbilityType
    power_level: int  # 能力强度 1-10
    range_m: int  # 影响范围（米）
    duration: int  # 持续时间（回合）
    reality_debt_cost: int  # 现实债务代价
    backlash_risk: int  # 反噬风险百分比

    def can_use_spatial(self, operator) -> bool:
        """判断是否可以使用空间能力"""
        if operator.reality_debt + self.reality_debt_cost > 1000:
            return False
        if operator.fatigue > 80:
            return False
        return True

    def execute_spatial_ability(self, user_unit, target_units) -> Dict:
        """执行空间能力"""
        if not self.can_use_spatial(user_unit.operator):
            return {"success": False, "reason": "现实债务或疲劳过高"}

        # 计算成功率和风险
        base_success = 80 - (user_unit.operator.reality_debt // 10)
        actual_success = max(20, min(95, base_success))

        # 检查是否发生反噬
        backlash = random.randint(1, 100) <= self.backlash_risk

        result = {
            "success": not backlash,
            "ability_type": self.ability_type,
            "power_level": self.power_level,
            "backlash": backlash,
            "debt_cost": self.reality_debt_cost
        }

        if not backlash:
            if self.ability_type == SpatialAbilityType.SPATIAL_FOLD:
                result["effect"] = self._spatial_fold_attack(user_unit, target_units)
            elif self.ability_type == SpatialAbilityType.TIME_SLOW:
                result["effect"] = self._time_slow(user_unit, target_units)
            elif self.ability_type == SpatialAbilityType.PHYSICS_MODIFY:
                result["effect"] = self._physics_modify(user_unit)
        else:
            result["backlash_damage"] = self._calculate_backlash_damage(user_unit)

        return result

    def _spatial_fold_attack(self, user_unit, target_units) -> Dict:
        """空间折叠攻击：瞬移打击"""
        target = random.choice(target_units)
        base_damage = 150 * self.power_level
        actual_damage = base_damage + random.randint(-30, 30)

        damage_dealt = target.take_damage(actual_damage)

        return {
            "description": f"空间折叠攻击！直接命中{target.name}",
            "damage": damage_dealt,
            "target": target.name,
            "special": "无视防御和距离"
        }

    def _time_slow(self, user_unit, target_units) -> Dict:
        """时间减缓：提高我方反应速度"""
        speed_boost = 25 * self.power_level
        user_unit.active_buffs['speed_boost'] = speed_boost
        user_unit.active_buffs['reaction_boost'] = speed_boost // 2

        return {
            "description": f"时间减缓！我方反应速度提升{speed_boost}%",
            "speed_boost": speed_boost,
            "duration": self.duration,
            "affected_units": len(target_units)
        }

    def _physics_modify(self, user_unit) -> Dict:
        """物理常数修改"""
        modifications = []

        if self.power_level >= 3:
            gravity_reduction = 10 * self.power_level
            user_unit.active_buffs['mobility_boost'] = gravity_reduction
            modifications.append(f"重力降低{gravity_reduction}%")

        if self.power_level >= 5:
            defense_boost = 15 * self.power_level
            user_unit.active_buffs['defense_boost'] = defense_boost
            modifications.append(f"防御提升{defense_boost}")

        if self.power_level >= 7:
            damage_boost = 20 * self.power_level
            user_unit.active_buffs['damage_boost'] = damage_boost
            modifications.append(f"伤害提升{damage_boost}")

        return {
            "description": "物理常数修改完成",
            "modifications": modifications,
            "power_level": self.power_level
        }

    def _calculate_backlash_damage(self, user_unit) -> int:
        """计算反噬伤害"""
        backlash_damage = 100 * self.power_level
        user_unit.take_damage(backlash_damage)
        return backlash_damage

class EvolutionStage(Enum):
    """阶段进化系统"""
    BASIC = "基础阶段"  # 普通能力使用
    MAGIC = "魔阶段"   # 能力大幅增强，代价增加
    DIVINE = "神阶段"  # 接近全能，极大代价

@dataclass
class EvolutionProgress:
    """进化进度系统"""
    current_stage: EvolutionStage
    progress_to_next: float  # 0.0-1.0
    unlocked_abilities: List[str]
    stage_modifiers: Dict[str, float]

    def __post_init__(self):
        if not self.stage_modifiers:
            self._init_stage_modifiers()

    def _init_stage_modifiers(self):
        """初始化阶段修正值"""
        if self.current_stage == EvolutionStage.BASIC:
            self.stage_modifiers = {
                "ability_multiplier": 1.0,
                "debt_multiplier": 1.0,
                "success_rate_modifier": 0.0
            }
        elif self.current_stage == EvolutionStage.MAGIC:
            self.stage_modifiers = {
                "ability_multiplier": 1.8,
                "debt_multiplier": 1.5,
                "success_rate_modifier": 10.0
            }
        elif self.current_stage == EvolutionStage.DIVINE:
            self.stage_modifiers = {
                "ability_multiplier": 3.0,
                "debt_multiplier": 2.5,
                "success_rate_modifier": 20.0
            }

    def can_evolve(self) -> bool:
        """判断是否可以进化"""
        return self.progress_to_next >= 1.0

    def attempt_evolution(self, operator) -> Dict:
        """尝试进化到下一阶段"""
        if not self.can_evolve():
            return {"success": False, "reason": "进度不足"}

        stages = [EvolutionStage.BASIC, EvolutionStage.MAGIC, EvolutionStage.DIVINE]
        current_index = stages.index(self.current_stage)

        if current_index >= len(stages) - 1:
            return {"success": False, "reason": "已达最高阶段"}

        next_stage = stages[current_index + 1]

        # 计算进化成功率
        base_success = 70
        debt_penalty = max(0, (operator.reality_debt - 500) // 5)
        fatigue_penalty = max(0, (operator.fatigue - 60) // 3)
        actual_success = max(20, min(90, base_success - debt_penalty - fatigue_penalty))

        success = random.randint(1, 100) <= actual_success

        result = {
            "success": success,
            "current_stage": self.current_stage,
            "target_stage": next_stage,
            "success_chance": actual_success
        }

        if success:
            self.current_stage = next_stage
            self.progress_to_next = 0.0
            self._init_stage_modifiers()
            result["message"] = f"进化成功！进入{next_stage.value}"
        else:
            # 进化失败惩罚
            operator.reality_debt += 100
            operator.fatigue += 30
            result["message"] = "进化失败！受到现实反噬"
            result["penalty"] = {"debt": 100, "fatigue": 30}

        return result

    def add_progress(self, amount: float):
        """添加进化进度"""
        self.progress_to_next = min(1.0, self.progress_to_next + amount)

class EnhancedRealityDebtSystem:
    """增强现实债务后果系统"""
    def __init__(self):
        self.debt_levels = {
            500: "能力成功率降低10%",
            600: "能力成功率降低20%",
            700: "开始出现现实扭曲，能力成功率降低30%",
            800: "现实扭曲加剧，所有成功率降低40%",
            900: "严重反噬效应，使用能力可能直接失败",
            950: "极度危险，现实边界模糊",
            1000: "现实崩溃临界点"
        }

    def get_debt_consequences(self, debt_level: int) -> List[str]:
        """获取当前债务后果"""
        consequences = []
        for threshold, consequence in self.debt_levels.items():
            if debt_level >= threshold:
                consequences.append(consequence)
        return consequences

    def apply_debt_penalties(self, operator, base_success_rate: int) -> int:
        """应用债务惩罚到成功率"""
        penalty = 0
        if operator.reality_debt >= 500:
            penalty += 10
        if operator.reality_debt >= 600:
            penalty += 10
        if operator.reality_debt >= 700:
            penalty += 10
        if operator.reality_debt >= 800:
            penalty += 10
        if operator.reality_debt >= 900:
            penalty += 15

        return max(5, base_success_rate - penalty)

    def check_reality_distortion(self, operator) -> Dict:
        """检查现实扭曲程度"""
        if operator.reality_debt < 700:
            return {"distortion": False, "level": 0}

        distortion_level = min(5, (operator.reality_debt - 700) // 50)

        effects = {
            1: ["轻微视觉干扰", "空间感轻微异常"],
            2: ["中等现实扭曲", "时间感知异常", "物体边缘模糊"],
            3: ["严重现实扭曲", "重力异常", "声音扭曲"],
            4: ["极度现实扭曲", "空间裂缝", "存在感知模糊"],
            5: ["现实边界崩溃", "存在稳定性丧失", "认知崩溃风险"]
        }

        return {
            "distortion": True,
            "level": distortion_level,
            "effects": effects.get(distortion_level, [])
        }

    def attempt_debt_reduction(self, operator, reduction_method: str) -> Dict:
        """尝试减少现实债务"""
        base_reduction = 0
        cost = 0
        success_rate = 100

        if reduction_method == "rest":
            base_reduction = 50
            cost = 1  # 休息1回合
            success_rate = 100
        elif reduction_method == "meditation":
            base_reduction = 100
            cost = 2  # 冥想2回合
            success_rate = 85
        elif reduction_method == "reality_anchor":
            base_reduction = 200
            cost = 3  # 锚定现实3回合
            success_rate = 60
        elif reduction_method == "sacrifice":
            base_reduction = 400
            cost = 50  # 牺牲生命值
            success_rate = 95

        actual_reduction = int(base_reduction * (1 - operator.fatigue / 200))

        success = random.randint(1, 100) <= success_rate

        result = {
            "success": success,
            "method": reduction_method,
            "potential_reduction": actual_reduction if success else 0,
            "cost": cost
        }

        if success:
            operator.reality_debt = max(0, operator.reality_debt - actual_reduction)
            if reduction_method == "sacrifice":
                operator.current_health -= cost
            elif reduction_method in ["rest", "meditation", "reality_anchor"]:
                # 这些方法需要消耗回合，由战斗系统处理
                pass

        return result

# TODO: 组织管理系统 - 未来实现
# 设计思路：
# 1. BloodlineOrganization 类：血统能力组织
#    - 招募成员：recruit_member(operator)
#    - 任务分配：assign_mission(member, mission)
#    - 资源支持：provide_support(member, support_type)
#    - 组织影响力：influence_level
#    - 组织资源：resources
#
# 2. OrganizationMission 类：组织任务
#    - 任务类型：战斗、侦查、资源收集
#    - 任务奖励：现实债务减免、资源获取、能力解锁
#    - 任务难度：根据成员能力动态调整
#
# 3. 集成点：
#    - Operator 类添加 organization 属性
#    - 战斗系统添加组织支援调用
#    - 战役循环添加组织任务
#
# 4. 技术考虑：
#    - 组织管理需要独立的UI界面
#    - 组织任务需要单独的任务系统
#    - 组织影响力需要全局状态管理
#    - 优先级：P2（中期功能）
#    - 预计工作量：2-3周

# ==================== 继续原有类定义 ====================

class Operator:
    """操作员/指挥官"""
    def __init__(self, name: str, ability_tier: AbilityTier, is_commander: bool = False):
        self.name = name
        self.ability_tier = ability_tier
        self.is_commander = is_commander

        # 基础属性
        self.command_skill = random.randint(60, 95) if is_commander else random.randint(40, 80)
        self.combat_skill = random.randint(50, 85)
        self.technical_skill = random.randint(50, 80)

        # 状态
        self.reality_debt = 0
        self.fatigue = 0
        self.morale = 100

        # 能力
        self.abilities: List[Ability] = []

        # 新增系统支持
        self.prediction_abilities: List[PredictionAbility] = []
        self.spatial_abilities: List[SpatialAbility] = []
        self.evolution_progress = EvolutionProgress(
            current_stage=EvolutionStage.BASIC,
            progress_to_next=0.0,
            unlocked_abilities=[],
            stage_modifiers={}
        )
        self.debt_system = EnhancedRealityDebtSystem()

    def add_ability(self, ability: Ability):
        """添加超能力"""
        self.abilities.append(ability)

    def add_prediction_ability(self, ability: PredictionAbility):
        """添加预测能力"""
        self.prediction_abilities.append(ability)

    def add_spatial_ability(self, ability: SpatialAbility):
        """添加空间能力"""
        self.spatial_abilities.append(ability)

    def get_total_ability_multiplier(self) -> float:
        """获取总能力倍率（考虑进化阶段）"""
        return self.evolution_progress.stage_modifiers.get("ability_multiplier", 1.0)

    def get_debt_multiplier(self) -> float:
        """获取债务倍率（考虑进化阶段）"""
        return self.evolution_progress.stage_modifiers.get("debt_multiplier", 1.0)

    def can_evolve(self) -> bool:
        """判断是否可以进化"""
        return self.evolution_progress.can_evolve()

    def attempt_evolution(self) -> Dict:
        """尝试进化"""
        return self.evolution_progress.attempt_evolution(self)

    def get_debt_consequences(self) -> List[str]:
        """获取当前债务后果"""
        return self.debt_system.get_debt_consequences(self.reality_debt)

    def check_reality_distortion(self) -> Dict:
        """检查现实扭曲程度"""
        return self.debt_system.check_reality_distortion(self)

class WarfareUnit:
    """战争单位"""
    def __init__(self, name: str, scale: MachineScale, operator: Operator):
        self.name = name
        self.scale = scale
        self.operator = operator

        # 根据规模设置基础属性
        if scale == MachineScale.INDIVIDUAL:
            self.max_health = 100
            self.base_armor = 20
            self.mobility = 80
            self.evasion = 25   # 闪避率（%）
            self.communication_range = 100
        elif scale == MachineScale.SQUAD:
            self.max_health = 500
            self.base_armor = 40
            self.mobility = 60
            self.evasion = 15
            self.communication_range = 500
        elif scale == MachineScale.LEGION:
            self.max_health = 2000
            self.base_armor = 60
            self.mobility = 30
            self.evasion = 5
            self.communication_range = 2000

        self.current_health = self.max_health
        self.weapons: List[ModernWeapon] = []
        self.active_buffs: Dict[str, int] = {}
        self._buff_stacks: Dict[str, int] = {}  # buff堆叠计数
        self.active_auras: Dict[str, Dict] = {}  # 光环效果

        # 战斗状态
        self.suppression_level = 0  # 被压制程度
        self.morale = 100
        self.combat_readiness = 100

    def add_weapon(self, weapon: ModernWeapon):
        """添加武器"""
        self.weapons.append(weapon)

    def get_total_damage_output(self) -> int:
        """计算总火力输出"""
        total_damage = 0
        for weapon in self.weapons:
            base_damage = weapon.damage
            damage_boost = self.active_buffs.get('damage_boost', 0)
            morale_modifier = 1.0 if self.morale > 50 else 0.7
            weapon_damage = (base_damage + damage_boost) * morale_modifier
            total_damage += int(weapon_damage * weapon.rate_of_fire)

        # 指挥官光环加成
        if self.active_auras:
            for aura_name, aura_data in self.active_auras.items():
                if 'damage' in aura_data['effects']:
                    total_damage += aura_data['effects']['damage']

        return total_damage

    def get_mobility(self) -> int:
        """
        计算实际机动性（考虑负重影响）

        负重惩罚规则：
        - 总重量 < 基准×60%：无惩罚
        - 总重量 60-80%：速度-10%
        - 总重量 80-100%：速度-25%
        - 总重量 > 100%：速度-60%

        基准：单兵15kg / 小队100kg / 军团500kg
        """
        # 基准负重（按规模）
        weight_base = {MachineScale.INDIVIDUAL: 15, MachineScale.SQUAD: 100, MachineScale.LEGION: 500}
        base = weight_base.get(self.scale, 15)

        # 计算总负重
        total_weight = sum(w.weight for w in self.weapons)
        load_ratio = total_weight / base

        # 负重惩罚
        if load_ratio > 1.0:
            penalty = 0.40
        elif load_ratio > 0.8:
            penalty = 0.25
        elif load_ratio > 0.6:
            penalty = 0.10
        else:
            penalty = 0.0

        # buff 加成
        speed_buff = self.active_buffs.get('speed_boost', 0) + self.active_buffs.get('mobility_boost', 0)

        mobility = int(self.mobility * (1.0 - penalty))
        mobility = int(mobility * (1.0 + speed_buff / 100))

        return max(1, mobility)

    def get_communication_efficiency(self) -> int:
        """计算通讯效率"""
        base_efficiency = 100

        # 基础通讯范围
        if self.scale == MachineScale.INDIVIDUAL:
            base_efficiency = 100
        elif self.scale == MachineScale.SQUAD:
            base_efficiency = 80
        elif self.scale == MachineScale.LEGION:
            base_efficiency = 50

        # 超能增强
        base_efficiency += self.active_buffs.get('communication_boost', 0)

        # 指挥官光环
        if self.active_auras:
            for aura_name, aura_data in self.active_auras.items():
                if 'communication' in aura_data['effects']:
                    base_efficiency += aura_data['effects']['communication']

        # 压制影响
        base_efficiency -= self.suppression_level

        return max(20, min(100, base_efficiency))

    def get_detection_range(self) -> int:
        """获取侦查范围"""
        base_range = 0

        if self.scale == MachineScale.INDIVIDUAL:
            base_range = 200
        elif self.scale == MachineScale.SQUAD:
            base_range = 800
        elif self.scale == MachineScale.LEGION:
            base_range = 3000

        # 超能增强
        base_range += self.active_buffs.get('detection_boost', 0)

        # 指挥官光环
        if self.active_auras:
            for aura_name, aura_data in self.active_auras.items():
                if 'detection' in aura_data['effects']:
                    base_range += aura_data['effects']['detection']

        return base_range

    def activate_ability(self, ability: Ability) -> Dict:
        """激活超能力"""
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
            # 初始化堆叠跟踪
            if not hasattr(self, '_buff_stacks'):
                self._buff_stacks: Dict[str, int] = {}

            # 应用增强效果（可叠加）
            if ability.effect.damage_boost > 0:
                self.active_buffs['damage_boost'] = \
                    self.active_buffs.get('damage_boost', 0) + ability.effect.damage_boost
                self._buff_stacks['damage_boost'] = self._buff_stacks.get('damage_boost', 0) + 1
            if ability.effect.accuracy_boost > 0:
                self.active_buffs['accuracy_boost'] = \
                    self.active_buffs.get('accuracy_boost', 0) + ability.effect.accuracy_boost
                self._buff_stacks['accuracy_boost'] = self._buff_stacks.get('accuracy_boost', 0) + 1
            if ability.effect.communication_boost > 0:
                self.active_buffs['communication_boost'] = \
                    self.active_buffs.get('communication_boost', 0) + ability.effect.communication_boost
                self._buff_stacks['communication_boost'] = self._buff_stacks.get('communication_boost', 0) + 1
            if ability.effect.detection_boost > 0:
                self.active_buffs['detection_boost'] = \
                    self.active_buffs.get('detection_boost', 0) + ability.effect.detection_boost
                self._buff_stacks['detection_boost'] = self._buff_stacks.get('detection_boost', 0) + 1

            # 指挥官光环
            if ability.effect.aura_range > 0:
                self.active_auras[ability.name] = {
                    "range": ability.effect.aura_range,
                    "duration": ability.effect.duration,
                    "effects": {}
                }
                if ability.effect.damage_boost > 0:
                    self.active_auras[ability.name]["effects"]["damage"] = ability.effect.damage_boost
                if ability.effect.communication_boost > 0:
                    self.active_auras[ability.name]["effects"]["communication"] = ability.effect.communication_boost
                if ability.effect.detection_boost > 0:
                    self.active_auras[ability.name]["effects"]["detection"] = ability.effect.detection_boost

            ability.active_duration = ability.effect.duration
            ability.consecutive_uses += 1
            self.operator.reality_debt += ability.effect.reality_debt
            self.operator.fatigue += 15

            result["effects"] = self.active_buffs.copy()
            if self.active_auras:
                result["auras"] = self.active_auras.copy()
        else:
            # 失败后果
            self.current_health -= 30
            self.operator.reality_debt += int(ability.effect.reality_debt * 1.5)
            self.operator.fatigue += 25
            self.morale -= 10

        return result

    def can_use_ability(self, ability: Ability) -> bool:
        """检查是否能使用能力"""
        if self.operator.reality_debt > 800 and ability.tier != AbilityTier.BASIC:
            return False
        if self.operator.fatigue >= 100:
            return False
        if self.morale < 30:
            return False
        return True

    def attack_with_weapons(self, target: 'EnemyForce', distance: int = 200) -> Dict:
        """
        使用武器攻击目标（按武器分类处理）

        Args:
            target: 敌方目标
            distance: 距离（米），影响弹道精度衰减和命中判定

        武器分类处理：
        - BALLISTIC: 弹道衰减、穿甲值、直接伤害
        - CRUISE: 锁定状态、追踪规避、穿甲
        - ENERGY: 即时命中、穿甲比例、可能过热
        """
        total_damage = 0
        attacks = []
        hit_count = 0
        miss_count = 0

        for weapon in self.weapons:
            if not weapon.can_fire():
                continue

            shots = weapon.fire(weapon.rate_of_fire)
            if shots == 0:
                continue

            for _ in range(shots):
                hit, dmg, detail = self._resolve_shot(weapon, target, distance)
                if hit:
                    total_damage += dmg
                    hit_count += 1
                else:
                    miss_count += 1
                attacks.append(detail)

        # 压制效果：所有压制武器对目标施加压制
        if any(w.suppression for w in self.weapons):
            suppression_power = sum(15 for w in self.weapons if w.suppression)
            target.suppression_level += suppression_power

        # 弹药状态报告
        ammo_status = {}
        for w in self.weapons:
            if not w.can_fire() and not w._is_reloading:
                ammo_status[w.name] = "empty"
            elif w._is_reloading:
                ammo_status[w.name] = "reloading"
            elif w.is_overheated():
                ammo_status[w.name] = "overheated"
            elif w.current_ammo < w.magazine_size:
                ammo_status[w.name] = f"{w.current_ammo}/{w.magazine_size}"

        return {
            "total_damage": total_damage,
            "hit_count": hit_count,
            "miss_count": miss_count,
            "shots_fired": hit_count + miss_count,
            "attacks": attacks,
            "suppression_applied": any(w.suppression for w in self.weapons),
            "ammo_status": ammo_status,
        }

    def _resolve_shot(self, weapon: ModernWeapon, target: 'EnemyForce', distance: int) -> tuple:
        """
        解析单发射击

        Returns:
            (hit: bool, damage: int, detail: dict)
        """
        detail = {
            "weapon": weapon.name,
            "category": weapon.category.value,
            "distance": distance,
            "hit": False,
            "damage": 0,
            "critical": False,
            "armor_pierced": False,
            "suppression": 0,
        }

        # --- 命中判定 ---
        target_mobility = getattr(target, 'mobility', target.evasion)
        base_hit = weapon.get_hit_chance_at_range(distance, target_mobility)

        # Buff 加成/惩罚
        acc_boost = self.active_buffs.get('accuracy_boost', 0)
        final_hit_chance = min(0.99, base_hit + acc_boost / 100)

        # 攻击方自身压制惩罚（被压制的单位命中率下降）
        attacker_penalty = self.get_suppression_penalty()
        final_hit_chance = max(0.05, final_hit_chance - attacker_penalty)

        # 目标压制惩罚（被压制的目标更易命中，因为无法有效机动）
        sup_penalty = min(0.25, target.suppression_level / 200)
        final_hit_chance = min(0.99, final_hit_chance + sup_penalty)

        # 高压制状态：射击有概率被打断（无法行动）
        if self.suppression_level > 60 and random.random() < 0.4:
            detail["result"] = "射击被打断"
            detail["hit"] = False
            return False, 0, detail

        roll = random.random()  # 0.0 ~ 1.0
        hit = roll <= final_hit_chance
        detail["hit_chance"] = round(final_hit_chance, 3)
        detail["roll"] = round(roll, 3)

        if not hit:
            detail["result"] = "未命中"
            return False, 0, detail

        # --- 伤害计算 ---
        # 暴击判定（狙击/精英武器更高暴击率）
        crit_chance = 0.05
        if weapon.weapon_class in (WeaponClass.SNIPER, WeaponClass.CANNON, WeaponClass.AAM):
            crit_chance = 0.15
        elif weapon.category == WeaponCategory.ENERGY:
            crit_chance = 0.10

        is_crit = random.random() < crit_chance
        detail["critical"] = is_crit

        # 基础伤害
        base_dmg = weapon.get_effective_damage(distance)
        detail["base_damage"] = base_dmg

        # 弹药波动
        dmg = base_dmg + random.randint(-5, 5)

        # Buff 加成
        dmg += self.active_buffs.get('damage_boost', 0)

        # 暴击增伤
        if is_crit:
            dmg = int(dmg * 1.5)
            detail["result"] = "暴击"
        else:
            detail["result"] = "命中"

        # --- 穿甲处理 ---
        target_armor = getattr(target, 'armor', 0)
        if target_armor > 0:
            ap = weapon.armor_penetration
            # 能量武器按百分比无视护甲
            if weapon.category == WeaponCategory.ENERGY and weapon.energy:
                ignore = int(target_armor * weapon.energy.armor_ignores_pct / 100)
                effective_armor = max(0, target_armor - ap - ignore)
            else:
                effective_armor = max(0, target_armor - ap)

            if effective_armor < target_armor:
                dmg -= effective_armor
                detail["armor_pierced"] = True
                detail["armor_before"] = target_armor
                detail["armor_after"] = effective_armor
            else:
                dmg -= target_armor

        dmg = max(1, dmg)
        detail["damage"] = dmg

        # --- 特殊效果 ---
        # 能量武器过热
        if weapon.category == WeaponCategory.ENERGY:
            weapon.add_heat(weapon.energy.heat_per_shot)
            if weapon.is_overheated():
                detail["overheated"] = True
            detail["heat"] = weapon.get_heat()

        # 护甲削弱（每次命中）
        if weapon.armor_shred > 0 and hasattr(target, 'armor'):
            target.armor = max(0, target.armor - weapon.armor_shred)

        # 压制效果
        if weapon.suppression:
            detail["suppression"] = 15

        return True, dmg, detail

    def take_damage(self, damage: int):
        """受到伤害"""
        defense = self.base_armor + self.active_buffs.get('defense_boost', 0)
        actual_damage = max(10, damage - defense // 2)
        self.current_health = max(0, self.current_health - actual_damage)

        # 压制影响
        self.suppression_level = min(100, self.suppression_level + 10)
        self.combat_readiness -= 5

    def update_suppression(self):
        """
        回合结束减少压制状态

        压制消散：每回合 -10
        压制效果：
        - 压制 > 60：无法执行进攻行动（被迫防守）
        - 压制 > 30：命中率和闪避率 -20%
        - 压制 > 0：所有行动有概率中断
        """
        self.suppression_level = max(0, self.suppression_level - 10)

    def is_suppressed(self) -> bool:
        """是否处于压制状态（无法正常行动）"""
        return self.suppression_level > 60

    def reload_all(self) -> Dict[str, bool]:
        """
        为所有需要换弹的武器执行换弹
        返回每把武器是否成功完成换弹

        注意：换弹会消耗一回合的行动
        """
        results = {}
        for weapon in self.weapons:
            if weapon.needs_reload():
                weapon.start_reload(turns=1)
                # 换弹开始，下回合update_reload完成
                results[weapon.name] = "reloading"
            elif weapon._is_reloading:
                done = weapon.update_reload()
                results[weapon.name] = "done" if done else "reloading"
            else:
                results[weapon.name] = "ready"
        return results

    def get_ammo_status(self) -> Dict[str, dict]:
        """获取所有武器的弹药状态"""
        return {
            w.name: {
                "current": w.current_ammo,
                "max": w.magazine_size,
                "reloading": w._is_reloading,
                "overheated": w.is_overheated(),
                "heat": w.get_heat() if w.category == WeaponCategory.ENERGY else 0,
            }
            for w in self.weapons
        }

    def update_energy_weapons(self):
        """回合结束：能量武器散热 + 换弹"""
        for weapon in self.weapons:
            if weapon.category == WeaponCategory.ENERGY:
                weapon.dissipate_heat()
            elif weapon._is_reloading:
                weapon.update_reload()

    def get_suppression_penalty(self) -> float:
        """
        获取压制惩罚倍率（用于命中率和闪避率计算）

        压制 > 30: -20%
        压制 > 60: -40%
        """
        if self.suppression_level > 60:
            return 0.40
        elif self.suppression_level > 30:
            return 0.20
        return 0.0

    def repair(self):
        """维修"""
        repair_rate = 10 + self.operator.technical_skill // 5
        repair_rate += self.active_buffs.get('repair_rate', 0)
        self.current_health = min(self.max_health, self.current_health + repair_rate)

    def update_buffs(self):
        """
        回合结束更新增益状态

        使用堆叠系统：每个buff类型有独立计数
        同一buff被多次激活时，计数累加；消退时逐层移除
        """
        # 初始化堆叠跟踪（如尚无）
        if not hasattr(self, '_buff_stacks'):
            self._buff_stacks: Dict[str, int] = {}

        # 追踪哪些buff类型已到期
        expired_keys = set()

        # 逐个处理 operator.abilities 的持续时间
        for ability in self.operator.abilities:
            if ability.active_duration > 0:
                ability.active_duration -= 1
                if ability.active_duration <= 0:
                    # 该能力到期，从堆叠中减少
                    for buff_key, buff_field in [
                        ('damage_boost', 'damage_boost'),
                        ('accuracy_boost', 'accuracy_boost'),
                        ('communication_boost', 'communication_boost'),
                        ('detection_boost', 'detection_boost'),
                        ('speed_boost', 'speed_boost'),
                        ('mobility_boost', 'mobility_boost'),
                        ('defense_boost', 'defense_boost'),
                    ]:
                        if getattr(ability.effect, buff_field, 0) > 0:
                            self._buff_stacks[buff_key] = self._buff_stacks.get(buff_key, 1) - 1
                            if self._buff_stacks[buff_key] <= 0:
                                # 该buff所有层均已到期，彻底移除
                                self.active_buffs.pop(buff_key, None)
                                self._buff_stacks.pop(buff_key, None)
                                expired_keys.add(buff_key)

        # 减少光环持续时间
        expired_auras = []
        for aura_name, aura_data in list(self.active_auras.items()):
            aura_data["duration"] -= 1
            if aura_data["duration"] <= 0:
                expired_auras.append(aura_name)
                self._buff_stacks.pop(f"aura_{aura_name}", None)

        for aura_name in expired_auras:
            del self.active_auras[aura_name]

        # 减少光环持续时间
        expired_auras = []
        for aura_name, aura_data in self.active_auras.items():
            aura_data["duration"] -= 1
            if aura_data["duration"] <= 0:
                expired_auras.append(aura_name)

        for aura_name in expired_auras:
            del self.active_auras[aura_name]

    def is_active(self) -> bool:
        """是否还能战斗"""
        return self.current_health > 0 and self.morale > 0

class EnemyForce:
    """
    敌方部队

    与 WarfareUnit 对称设计：拥有武器、护甲、士气等属性。
    """
    def __init__(
        self,
        name: str,
        scale: MachineScale,
        combat_power: int,
        evasion: int = 10,
        armor: int = 0,
        mobility: int = None,
        morale: int = 100,
        weapons: List[ModernWeapon] = None,
    ):
        self.name = name
        self.scale = scale
        self.max_health = combat_power * 5
        self.current_health = self.max_health
        self.attack_power = combat_power
        self.evasion = evasion          # 闪避（影响弹道武器命中）
        self.armor = armor              # 护甲值（被穿甲伤害减免）
        self.mobility = mobility if mobility is not None else self._default_mobility()
        self.morale = morale           # 士气（影响攻击力）
        self.suppression_level = 0
        self.weapons = weapons or []

    def _default_mobility(self) -> int:
        if self.scale == MachineScale.INDIVIDUAL:
            return 70
        elif self.scale == MachineScale.SQUAD:
            return 50
        else:
            return 25

    def add_weapon(self, weapon: ModernWeapon):
        self.weapons.append(weapon)

    def attack_with_weapons(self, target: 'WarfareUnit', distance: int = 200) -> Dict:
        """
        敌方使用武器攻击我方单位

        Returns:
            {"total_damage": int, "hit_count": int, "attacks": list}
        """
        total_damage = 0
        attacks = []
        hit_count = 0

        for weapon in self.weapons:
            if not weapon.can_fire():
                continue
            shots = weapon.fire(weapon.rate_of_fire)
            if shots == 0:
                continue

            for _ in range(shots):
                detail = self._enemy_resolve_shot(weapon, target, distance)
                if detail["hit"]:
                    total_damage += detail["damage"]
                    hit_count += 1
                attacks.append(detail)

        return {
            "total_damage": total_damage,
            "hit_count": hit_count,
            "attacks": attacks,
        }

    def _enemy_resolve_shot(self, weapon: ModernWeapon, target: 'WarfareUnit', distance: int) -> Dict:
        """敌方射击解析"""
        detail = {"weapon": weapon.name, "distance": distance, "hit": False, "damage": 0}

        # 高压制状态：射击有概率被打断
        if self.suppression_level > 60 and random.random() < 0.4:
            detail["result"] = "射击被打断"
            return detail

        # 命中判定（敌方用 evasion，我方用命中-闪避）
        target_dodge = target.evasion if hasattr(target, 'evasion') else 20
        hit_chance = weapon.get_hit_chance_at_range(distance, target_dodge)

        # 敌方自身压制惩罚
        hit_chance = max(0.05, hit_chance - self.get_suppression_penalty())

        roll = random.random()
        if roll > hit_chance:
            detail["result"] = "未命中"
            return detail

        detail["hit"] = True

        # 伤害计算
        dmg = weapon.get_effective_damage(distance)
        dmg += random.randint(-5, 5)
        morale_factor = 1.0 if self.morale > 50 else 0.7
        dmg = int(dmg * morale_factor)

        # 护甲减免
        if hasattr(target, 'base_armor'):
            def_val = target.base_armor + target.active_buffs.get('defense_boost', 0)
            dmg = max(1, dmg - def_val // 2)

        detail["damage"] = dmg
        detail["result"] = "命中"
        return detail

    def take_damage(self, damage: int):
        """受到伤害"""
        self.current_health = max(0, self.current_health - damage)
        # 受伤降低士气
        self.morale = max(0, self.morale - 3)
        # 被压制加深（累积）
        self.suppression_level = min(100, self.suppression_level + 10)

    def update_suppression(self):
        """回合结束减少压制"""
        self.suppression_level = max(0, self.suppression_level - 10)

    def get_suppression_penalty(self) -> float:
        if self.suppression_level > 60:
            return 0.40
        elif self.suppression_level > 30:
            return 0.20
        return 0.0

    def is_active(self) -> bool:
        """是否存活"""
        return self.current_health > 0 and self.morale > 0

    def reload_all(self) -> Dict[str, str]:
        """敌方换弹"""
        results = {}
        for weapon in self.weapons:
            if weapon.needs_reload():
                weapon.start_reload(turns=1)
                results[weapon.name] = "reloading"
            elif weapon._is_reloading:
                done = weapon.update_reload()
                results[weapon.name] = "done" if done else "reloading"
            else:
                results[weapon.name] = "ready"
        return results

    def update_energy_weapons(self):
        """回合结束：能量武器散热"""
        for weapon in self.weapons:
            if weapon.category == WeaponCategory.ENERGY:
                weapon.dissipate_heat()
            elif weapon._is_reloading:
                weapon.update_reload()

class ModernCombatSystem:
    """现代战争战斗系统"""

    def __init__(self, enable_terrain: bool = False, battlefield_name: str = None):
        self.turn = 0
        self.combat_log = []
        self.detection_levels = {}  # 各单位的侦查等级
        self.active_units: Dict[str, 'WarfareUnit'] = {}  # 已部署的单位

        # 可选：地形/天气系统插件
        self.terrain = None
        if enable_terrain:
            from terrain_combat_demo import TerrainCombatPlugin
            self.terrain = TerrainCombatPlugin(battlefield_name or "默认战场")

    def create_individual_unit(self) -> WarfareUnit:
        """创建单兵单位"""
        operator = Operator("特种兵零号", AbilityTier.BASIC, is_commander=False)
        operator.add_ability(Ability(
            "反应增强",
            AbilityTier.BASIC,
            AbilityEffect(
                name="反应增强",
                tier=AbilityTier.BASIC,
                description="提升神经反应速度，提高闪避和命中率",
                success_rate=90,
                reality_debt=8,
                duration=3,
                accuracy_boost=15,
                dodge_boost=10,
                detection_boost=50
            )
        ))

        unit = WarfareUnit("单兵突击手", MachineScale.INDIVIDUAL, operator)

        # 现代单兵武器
        assault_rifle = ModernWeapon(
            name="突击步枪",
            weapon_class=WeaponClass.RIFLE,
            category=WeaponCategory.BALLISTIC,
            damage=35,
            rate_of_fire=1,
            accuracy=75,
            range_m=300,
            magazine_size=30,
            weight=3.5,
            special_features=["光学瞄准镜", "榴弹发射器"],
            suppression=False,
            ballistic=BallisticProperties(
                projectile_speed=800,
                falloff_start=200,
                falloff_rate=0.003,
            ),
        )

        pistol = ModernWeapon(
            name="战术手枪",
            weapon_class=WeaponClass.PISTOL,
            category=WeaponCategory.BALLISTIC,
            damage=20,
            rate_of_fire=1,
            accuracy=80,
            range_m=50,
            magazine_size=15,
            weight=0.8,
            special_features=["消音器"],
            suppression=False,
            ballistic=BallisticProperties(
                projectile_speed=350,
                falloff_start=30,
                falloff_rate=0.005,
            ),
        )

        unit.add_weapon(assault_rifle)
        unit.add_weapon(pistol)

        return unit

    def create_squad_unit(self) -> WarfareUnit:
        """创建小队单位"""
        operator = Operator("队长阿尔法", AbilityTier.ADVANCED, is_commander=False)
        operator.add_ability(Ability(
            "战场感知",
            AbilityTier.ADVANCED,
            AbilityEffect(
                name="战场感知",
                tier=AbilityTier.ADVANCED,
                description="增强全队的侦查和协调能力",
                success_rate=85,
                reality_debt=15,
                duration=4,
                detection_boost=200,
                communication_boost=25,
                morale_boost=15
            )
        ))

        unit = WarfareUnit("阿尔法小队", MachineScale.SQUAD, operator)

        # 小队武器配置
        rifleman_weapons = [
            ModernWeapon(
                name="突击步枪",
                weapon_class=WeaponClass.RIFLE,
                category=WeaponCategory.BALLISTIC,
                damage=40,
                rate_of_fire=1,
                accuracy=70,
                range_m=400,
                magazine_size=30,
                weight=3.8,
                special_features=["光学瞄准镜", "前握把"],
                suppression=False,
                ballistic=BallisticProperties(
                    projectile_speed=800,
                    falloff_start=250,
                    falloff_rate=0.002,
                ),
            )
            for _ in range(4)
        ]

        machine_gunner = ModernWeapon(
            name="通用机枪",
            weapon_class=WeaponClass.MG,
            category=WeaponCategory.BALLISTIC,
            damage=60,
            rate_of_fire=3,
            accuracy=60,
            range_m=800,
            magazine_size=200,
            weight=12.0,
            special_features=["两脚架", "快速更换枪管"],
            suppression=True,
            ballistic=BallisticProperties(
                projectile_speed=800,
                falloff_start=400,
                falloff_rate=0.001,
            ),
        )

        marksman_rifle = ModernWeapon(
            name="狙击步枪",
            weapon_class=WeaponClass.SNIPER,
            category=WeaponCategory.BALLISTIC,
            damage=80,
            rate_of_fire=1,
            accuracy=95,
            range_m=1500,
            magazine_size=10,
            weight=6.5,
            special_features=["高倍瞄准镜", "消音器"],
            suppression=False,
            armor_penetration=30,
            ballistic=BallisticProperties(
                projectile_speed=900,
                falloff_start=800,
                falloff_rate=0.001,
            ),
        )

        unit.add_weapon(machine_gunner)
        unit.add_weapon(marksman_rifle)
        for rifle in rifleman_weapons:
            unit.add_weapon(rifle)

        return unit

    def create_legion_commander(self) -> WarfareUnit:
        """创建军团指挥官"""
        operator = Operator("总指挥官", AbilityTier.ELITE, is_commander=True)
        operator.command_skill = 95
        operator.combat_skill = 90

        # 指挥官光环能力
        commander_aura = Ability(
            "战场统御",
            AbilityTier.ELITE,
            AbilityEffect(
                name="战场统御光环",
                tier=AbilityTier.ELITE,
                description="强大的战场指挥能力，大幅提升全军性能",
                success_rate=80,
                reality_debt=30,
                duration=5,
                damage_boost=20,
                accuracy_boost=15,
                communication_boost=40,
                detection_boost=300,
                morale_boost=25,
                aura_range=5000,
                aura_effects=["火力增强", "指挥协调", "士气提升"]
            )
        )

        operator.add_ability(commander_aura)

        unit = WarfareUnit("第一军团", MachineScale.LEGION, operator)

        # 军团级武器配置
        artillery_battery = [
            ModernWeapon(
                name="155mm自行火炮",
                weapon_class=WeaponClass.HOWITZER,
                category=WeaponCategory.BALLISTIC,
                damage=120,
                rate_of_fire=1,
                accuracy=50,
                range_m=30000,
                magazine_size=40,
                weight=55000.0,
                special_features=["自行底盘", "计算机火控系统"],
                suppression=True,
                armor_penetration=50,
                ballistic=BallisticProperties(
                    projectile_speed=600,
                    falloff_start=15000,
                    falloff_rate=0.0001,
                ),
            )
            for _ in range(6)
        ]

        aa_systems = [
            ModernWeapon(
                name="防空导弹系统",
                weapon_class=WeaponClass.AAM,
                category=WeaponCategory.CRUISE,
                damage=80,
                rate_of_fire=2,
                accuracy=85,
                range_m=15000,
                magazine_size=8,
                weight=15000.0,
                special_features=["雷达制导", "垂直发射"],
                suppression=False,
                anti_air=True,
                armor_penetration=40,
                cruise=CruiseProperties(
                    lock_on_time=1,
                    tracking=75,
                    countermeasure_vuln=30,
                    flight_speed=800,
                    terminal_guidance=True,
                ),
            )
            for _ in range(4)
        ]

        for weapon in artillery_battery:
            unit.add_weapon(weapon)
        for weapon in aa_systems:
            unit.add_weapon(weapon)

        return unit

    def create_enemy_force(self, scale: MachineScale) -> EnemyForce:
        """创建对应规模的敌方部队"""
        if scale == MachineScale.INDIVIDUAL:
            return EnemyForce("敌军单兵", scale, 40, 20)
        elif scale == MachineScale.SQUAD:
            return EnemyForce("敌军小队", scale, 200, 15)
        elif scale == MachineScale.LEGION:
            return EnemyForce("敌军军团", scale, 1000, 10)

    def show_battle_status(self, friendly_units: List[WarfareUnit], enemy: EnemyForce):
        """显示战斗状态"""
        print("\n" + "="*80)
        print(f"[战役状态] 第{self.turn}回合")
        print("="*80)

        # 我方单位
        for unit in friendly_units:
            print(f"\n[{unit.scale.value}] {unit.name}")
            print(f"[操作员] {unit.operator.name} ({unit.operator.ability_tier.value})")
            health_bar = self._create_bar(unit.current_health, unit.max_health)
            print(f"[完整度] {unit.current_health}/{unit.max_health} {health_bar}")

            debt_bar = self._create_bar(unit.operator.reality_debt, 1000, reverse=True)
            debt_status = self._get_debt_status(unit.operator.reality_debt)
            print(f"[现实债务] {unit.operator.reality_debt}/1000 {debt_bar} [{debt_status}]")

            fatigue_bar = self._create_bar(unit.operator.fatigue, 100, reverse=True)
            print(f"[疲劳度] {unit.operator.fatigue}/100 {fatigue_bar}")

            print(f"[火力输出] {unit.get_total_damage_output()}/回合")
            print(f"[通讯效率] {unit.get_communication_efficiency()}%")
            print(f"[侦查范围] {unit.get_detection_range()}m")

            # 武器信息
            weapon_info = ", ".join([f"{w.name}({w.damage}伤)" for w in unit.weapons[:3]])
            if len(unit.weapons) > 3:
                weapon_info += f" 等{len(unit.weapons)}件"
            print(f"[武器] {weapon_info}")

            # 增益状态
            if unit.active_buffs:
                print(f"[增强效果]")
                for buff_name, buff_value in unit.active_buffs.items():
                    if buff_value > 0:
                        print(f"  {buff_name}:+{buff_value}")

            # 光环状态
            if unit.active_auras:
                print(f"[指挥光环]")
                for aura_name, aura_data in unit.active_auras.items():
                    print(f"  {aura_name} (范围{aura_data['range']}m, 剩余{aura_data['duration']}回合)")
                    if aura_data['effects']:
                        for effect_name, effect_value in aura_data['effects'].items():
                            print(f"    {effect_name}:+{effect_value}")

        # 敌方状态
        print(f"\n[{enemy.scale.value}] {enemy.name}")
        enemy_health_bar = self._create_bar(enemy.current_health, enemy.max_health)
        print(f"[战斗力] {enemy.current_health}/{enemy.max_health} {enemy_health_bar}")

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

    def combat_phase(self, friendly_units: List[WarfareUnit], enemy: EnemyForce):
        """战斗阶段"""
        total_damage = 0

        # 我方攻击
        for unit in friendly_units:
            if unit.is_active():
                result = unit.attack_with_weapons(enemy)
                total_damage += result['total_damage']
                self.combat_log.append(f"[攻击] {unit.name}造成{result['total_damage']}伤害")

        enemy.take_damage(total_damage)

        # 敌方反击
        if enemy.is_active():
            counter_damage = enemy.attack_power + random.randint(-10, 10)
            for unit in friendly_units:
                if unit.is_active():
                    unit.take_damage(counter_damage // len(friendly_units))

    def ability_phase(self, friendly_units: List[WarfareUnit], enemy: EnemyForce):
        """超能使用阶段"""
        print(f"\n[超能增强阶段]")

        # 指挥官优先使用光环
        for unit in friendly_units:
            if unit.operator.is_commander and unit.is_active():
                commander_auras = [a for a in unit.operator.abilities if a.effect.aura_range > 0]
                for aura in commander_auras:
                    if unit.can_use_ability(aura) and aura.active_duration == 0:
                        print(f"[指挥官光环] {unit.operator.name}激活{aura.name}")
                        result = unit.activate_ability(aura)
                        if result['success']:
                            print(f"[光环生效] 范围{aura.effect.aura_range}m")
                            for effect_name, effect_value in result.get('auras', {}).get(aura.name, {}).get('effects', {}).items():
                                print(f"  全军{effect_name}:+{effect_value}")
                        else:
                            print(f"[光环失败] 能力失控！")

        # 其他单位使用个人能力
        for unit in friendly_units:
            if unit.is_active() and not unit.operator.is_commander:
                personal_abilities = [a for a in unit.operator.abilities if not a.effect.aura_range > 0]
                safe_abilities = [a for a in personal_abilities if a.get_risk_level(unit.operator) == "安全"]

                if safe_abilities and unit.can_use_ability(safe_abilities[0]):
                    ability = safe_abilities[0]
                    if ability.active_duration == 0:
                        print(f"[能力使用] {unit.name}的{unit.operator.name}使用{ability.name}")
                        result = unit.activate_ability(ability)
                        if result['success']:
                            print(f"[成功] {ability.effect.description}")
                        else:
                            print(f"[失败] 能力失控！单位受损")

    def check_battle_end(self, friendly_units: List[WarfareUnit], enemy: EnemyForce) -> Optional[str]:
        """检查战斗结束"""
        if not any(unit.is_active() for unit in friendly_units):
            return "friendly_defeated"
        elif not enemy.is_active():
            return "enemy_defeated"
        elif any(unit.operator.reality_debt >= 1000 for unit in friendly_units):
            return "debt_crisis"
        return None

    def print_battle_result(self, result, friendly_units: List[WarfareUnit], enemy: EnemyForce):
        """打印战斗结果"""
        print("\n" + "="*80)
        print("[战役结束]")
        print("="*80)

        active_units = [u for u in friendly_units if u.is_active()]

        if result == "enemy_defeated":
            print("\n[战役胜利]")
            print(f"敌方部队被击败！")
            total_debt = sum(u.operator.reality_debt for u in friendly_units)
            print(f"[总现实债务] {total_debt}/1000")

            if total_debt < 300:
                print("[完美] 卓作出色，代价控制优秀！")
            elif total_debt < 600:
                print("[良好] 战术合理，损失可控")
            else:
                print("[惨胜] 代价较高，需要改进战术")

        elif result == "friendly_defeated":
            print("\n[战役失败]")
            print(f"我方部队被击败...")
            print(f"[敌方残存] {enemy.current_health}/{enemy.max_health}")

        elif result == "debt_crisis":
            print("\n[现实危机]")
            print("操作员现实债务达到临界值，被现实排斥...")

        print(f"\n[战役统计]")
        print(f"战斗回合: {self.turn}")
        print(f"存活单位: {len(active_units)}/{len(friendly_units)}")

    def deploy_hero(self, hero_key: str) -> Optional['WarfareUnit']:
        """
        部署英雄单位（通过官方桥接层 hero_integration.py）

        Args:
            hero_key: hero_units_v2.HERO_REGISTRY 中的英雄键名
                      例如: "gamma_7", "sigma_3", "omega_12", "alpha_1"

        Returns:
            WarfareUnit 实例，部署失败返回 None
        """
        from hero_integration import (
            create_warfare_unit_from_hero,
            add_hero_abilities_to_operator
        )
        from hero_units_v2 import HERO_REGISTRY

        hero = HERO_REGISTRY.get(hero_key)
        if not hero:
            return None

        unit = create_warfare_unit_from_hero(hero)
        add_hero_abilities_to_operator(unit.operator, hero)
        return unit

    def deploy_heroes(self, hero_keys: List[str]) -> List['WarfareUnit']:
        """批量部署英雄单位"""
        return [self.deploy_hero(key) for key in hero_keys if self.deploy_hero(key)]


def auto_modern_combat_demo():
    """自动现代战争演示"""
    print("="*80)
    print("[宇宙之影] 现代战争战斗系统演示")
    print("="*80)
    print("\n[核心改进]")
    print("- 超能分类: 基础/进阶/精英（平等称呼）")
    print("- 战争机器: 单兵/小队/军团三个级别")
    print("- 指挥官光环: 军团级buff，最全面的辅助")
    print("- 现代武器: 参考真实战争火力配置")
    print("- 信息传递: 不同规模有不同的通讯效率\n")

    # 创建三个级别的单位
    individual_unit = combat_system.create_individual_unit()
    squad_unit = combat_system.create_squad_unit()
    legion_commander = combat_system.create_legion_commander()

    # 选择战斗规模
    print("[规模选择]")
    print("1. 单兵对决（基础超能）")
    print("2. 小队对抗（进阶超能）")
    print("3. 军团战役（精英超能+指挥光环）")

    # 自动选择：军团战役
    selected_scale = 3
    print(f"\n[演示规模] 军团战役（最完整体验）")

    friendly_units = [legion_commander]
    enemy = combat_system.create_enemy_force(MachineScale.LEGION)

    print(f"[我方] {legion_commander.name}")
    print(f"[敌方] {enemy.name}")
    print(f"[武器配置] 6门155mm火炮 + 4套防空系统")

    time.sleep(2)

    # 战斗循环
    while True:
        combat_system.turn += 1

        # 状态阶段
        combat_system.show_battle_status(friendly_units, enemy)

        # 信息侦查阶段
        detection_info = combat_system.detection_phase(friendly_units, enemy)

        # 指挥决策阶段
        command_decisions = combat_system.ai_command_decisions(friendly_units, enemy, detection_info)

        # 超能增强阶段
        combat_system.ability_phase(friendly_units, enemy)

        # 更新增益
        for unit in friendly_units:
            unit.update_buffs()

        # 战斗阶段
        combat_system.combat_phase(friendly_units, enemy)

        time.sleep(1)

        # 检查战斗结束
        result = combat_system.check_battle_end(friendly_units, enemy)
        if result:
            combat_system.show_battle_status(friendly_units, enemy)
            combat_system.print_battle_result(result, friendly_units, enemy)
            break

# 添加缺失的方法
def detection_phase(self, friendly_units: List[WarfareUnit], enemy: EnemyForce) -> Dict:
    """侦查阶段"""
    detection_info = {}

    for unit in friendly_units:
        if unit.is_active():
            detection_range = unit.get_detection_range()
            detection_level = "unknown"

            if detection_range >= 3000:
                detection_level = "精确"
            elif detection_range >= 1000:
                detection_level = "良好"
            elif detection_range >= 300:
                detection_level = "基本"
            else:
                detection_level = "有限"

            detection_info[unit.name] = {
                "level": detection_level,
                "range": detection_range,
                "enemy_info": f"{enemy.scale.value}级部队" if detection_level != "有限" else "未知"
            }

    return detection_info

def ai_command_decisions(self, friendly_units: List[WarfareUnit], enemy: EnemyForce, detection_info: Dict) -> List[str]:
    """AI指挥决策"""
    decisions = []

    for unit in friendly_units:
        if not unit.is_active():
            decisions.append(f"{unit.name}:已退出战斗")
            continue

        # 检查是否需要维修
        if unit.current_health < unit.max_health * 0.3:
            repair_ability = next((a for a in unit.operator.abilities if a.effect.repair_rate > 0), None)
            if repair_ability and unit.can_use_ability(repair_ability):
                decisions.append(f"{unit.name}:紧急维修")

        # 检查是否需要休整
        if unit.operator.fatigue > 70 or unit.operator.reality_debt > 600:
            decisions.append(f"{unit.name}:战术休整")

        # 默认攻击
        decisions.append(f"{unit.name}:全力攻击")

    return decisions

# 绑定方法
ModernCombatSystem.detection_phase = detection_phase
ModernCombatSystem.ai_command_decisions = ai_command_decisions

# 创建全局实例
combat_system = ModernCombatSystem()

if __name__ == "__main__":
    try:
        auto_modern_combat_demo()
    except KeyboardInterrupt:
        print("\n[演示中断]")
    except Exception as e:
        print(f"\n[错误] {e}")