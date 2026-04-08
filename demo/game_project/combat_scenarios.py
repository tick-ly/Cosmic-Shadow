# -*- coding: utf-8 -*-
"""
宇宙之影 - 三种战斗情景
Shadow of the Universe - Three Combat Scenarios

三种战斗情景：
1. 大战场（军团级正面战）
2. 潜入（单兵渗透侦察）
3. 小队作战（3-5人协同战术）
"""

import random
import time
import math
from typing import List, Dict, Optional, Tuple, Any

# 复用现有系统
from modern_warfare_system import (
    ModernCombatSystem, WarfareUnit, Operator, EnemyForce,
    MachineScale, Ability, AbilityEffect, AbilityTier, UnitType
)
from battlefield_map import BattlefieldMap, HistoricBattlefieldGenerator, TerrainTile, TerrainTile
from terrain_system import (
    TerrainSystem, TerrainType, WeatherCondition,
    BattlefieldZone, TERRAIN_REGISTRY
)


# ============================================================
# 基础情景类
# ============================================================

class BaseScenario:
    """战斗情景基类"""

    name: str = "未命名情景"
    description: str = ""
    map_size: Tuple[int, int] = (60, 30)

    def __init__(self):
        self.turn = 0
        self.max_turns = 10
        self.friendly_units: List[WarfareUnit] = []
        self.enemies: List[EnemyForce] = []
        self.combat_log: List[str] = []
        self.result: Optional[str] = None
        self._init_units()

    def _init_units(self):
        """初始化单位 — 子类实现"""
        raise NotImplementedError

    def setup_map(self) -> BattlefieldMap:
        """初始化战场地图"""
        return BattlefieldMap(width=self.map_size[0], height=self.map_size[1])

    def render(self) -> str:
        """渲染场景状态"""
        raise NotImplementedError

    def run_phase(self):
        """执行单个回合"""
        self.turn += 1
        self._log(f"\n{'='*60}")
        self._log(f"[第{self.turn}回合]")
        self._log('=' * 60)
        self._execute_phase()

    def _execute_phase(self):
        """执行回合逻辑 — 子类实现"""
        raise NotImplementedError

    def check_end(self) -> Optional[str]:
        """检查结束条件"""
        if all(u.current_health <= 0 for u in self.friendly_units):
            return "defeat"
        if all(e.current_health <= 0 for e in self.enemies):
            return "victory"
        if self.turn >= self.max_turns:
            return "timeout"
        return None

    def run(self):
        """运行完整情景"""
        self._print_intro()
        self._print_briefing()

        while True:
            self.run_phase()
            result = self.check_end()
            if result:
                self.result = result
                self._print_result()
                break

            response = input("\n[按回车继续，输入 q 退出] > ")
            if response.strip().lower() == 'q':
                self.result = "aborted"
                break

            time.sleep(0.5)

    def _log(self, msg: str):
        """添加日志"""
        self.combat_log.append(msg)
        print(msg)

    def _print_intro(self):
        """打印开场"""
        print("\n" + "=" * 70)
        print(f"[{self.name}]")
        print("=" * 70)
        print(self.description)

    def _print_briefing(self):
        """打印任务简报"""
        self._log("\n[任务简报]")
        self._log(f"  我方单位: {len(self.friendly_units)}")
        self._log(f"  敌方单位: {len(self.enemies)}")
        self._log(f"  最大回合: {self.max_turns}")
        self._log(f"  地图尺寸: {self.map_size[0]}x{self.map_size[1]}")

    def _print_result(self):
        """打印结果"""
        print("\n" + "=" * 70)
        print("[战斗结果]")
        print("=" * 70)
        if self.result == "victory":
            print("\n[胜利] 任务完成！")
        elif self.result == "defeat":
            print("\n[失败] 我方全灭...")
        elif self.result == "timeout":
            print("\n[超时] 任务未能在规定时间内完成")
        else:
            print(f"\n[中断] 任务被手动中止")

        alive = sum(1 for u in self.friendly_units if u.current_health > 0)
        self._log(f"\n  存活单位: {alive}/{len(self.friendly_units)}")
        self._log(f"  战斗回合: {self.turn}")


# ============================================================
# 情景1：大战场（军团级正面战）
# ============================================================

class BattlefieldScenario(BaseScenario):
    """
    大战场 — 军团级正面战

    特点：
    - 军团级单位正面冲突
    - 多区域控制点占领
    - 动态天气系统
    - 指挥官光环效果
    - AI指挥决策（进攻/防守/撤退）
    """

    name = "大战场"
    description = (
        "【军团级正面战】\n"
        "       大规模军团在复杂地形上展开正面冲突。\n"
        "       占领关键控制点获得战术优势，\n"
        "       利用天气变化调整战术。"
    )
    map_size = (80, 40)

    def __init__(self):
        self.control_zones: Dict[str, dict] = {}  # 控制点状态
        self.weather = WeatherCondition.CLEAR
        self.commander_aura_active = False
        self.ai_tactic = "attack"  # attack / defend / retreat
        super().__init__()

    def _init_units(self):
        """初始化大战场单位"""
        from modern_warfare_system import ModernWeapon, WeaponCategory, WeaponClass, BallisticProperties, CruiseProperties

        # 我方军团
        commander_op = Operator("张铁山", AbilityTier.ELITE, is_commander=True)
        commander_op.command_skill = 90
        commander_op.combat_skill = 80

        # 指挥官光环
        aura = Ability(
            "战场统御",
            AbilityTier.ELITE,
            AbilityEffect(
                name="战场统御光环",
                tier=AbilityTier.ELITE,
                description="提升全军火力与士气",
                success_rate=90,
                reality_debt=20,
                duration=3,
                damage_boost=15,
                morale_boost=20,
                aura_range=5000,
                aura_effects=["全军火力+15", "士气+20"]
            )
        )
        commander_op.add_ability(aura)

        self.commander = WarfareUnit("第一合成军团", MachineScale.LEGION, commander_op)
        self.commander.max_health = 2000
        self.commander.current_health = 2000
        self.commander.base_armor = 60
        self.commander.mobility = 30

        # 添加火炮
        for i in range(6):
            artillery = ModernWeapon(
                name=f"155mm火炮#{i+1}",
                weapon_class=WeaponClass.HOWITZER,
                category=WeaponCategory.BALLISTIC,
                damage=120,
                rate_of_fire=1,
                accuracy=50,
                range_m=30000,
                magazine_size=40,
                weight=55000.0,
                special_features=["计算机火控", "自动装填"],
                suppression=True,
                armor_penetration=50,
                ballistic=BallisticProperties(
                    projectile_speed=600,
                    falloff_start=15000,
                    falloff_rate=0.0001,
                ),
            )
            self.commander.add_weapon(artillery)

        # 添加防空（巡航导弹）
        for i in range(4):
            aa = ModernWeapon(
                name=f"防空系统#{i+1}",
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
            self.commander.add_weapon(aa)

        self.friendly_units.append(self.commander)

        # 敌方军团
        self.enemy = EnemyForce("敌军东部集群", MachineScale.LEGION, 1000, evasion=10)
        self.enemies.append(self.enemy)

        # 初始化控制点
        self._init_control_zones()

    def _init_control_zones(self):
        """初始化控制点"""
        self.control_zones = {
            "A区": {"controller": "neutral", "value": 0, "importance": 3},
            "B区": {"controller": "neutral", "value": 0, "importance": 5},
            "C区": {"controller": "neutral", "value": 0, "importance": 4},
            "D区": {"controller": "neutral", "value": 0, "importance": 2},
        }

    def setup_map(self) -> BattlefieldMap:
        """使用斯大林格勒风格地图"""
        return HistoricBattlefieldGenerator.generate_stalingrad(
            width=80, height=40
        )

    def render(self) -> str:
        """渲染大战场状态"""
        lines = [
            f"\n[大战场] 第{self.turn}回合 | 天气: {self.weather.value}",
            "=" * 60,
        ]

        # 控制点状态
        lines.append("\n[控制点]")
        for zone, state in self.control_zones.items():
            ctrl = state["controller"]
            val = state["value"]
            imp = "★" * state["importance"]
            if ctrl == "friendly":
                lines.append(f"  {zone} ★{imp} → 我方控制 (+{val})")
            elif ctrl == "enemy":
                lines.append(f"  {zone} ★{imp} → 敌方控制 (-{val})")
            else:
                lines.append(f"  {zone} ★{imp} → 争夺中")

        # 单位状态
        lines.append(f"\n[我方] {self.commander.name}")
        hp_pct = self.commander.current_health / self.commander.max_health
        hp_bar = "+" * int(hp_pct * 20) + "-" * (20 - int(hp_pct * 20))
        lines.append(f"  生命: {self.commander.current_health}/{self.commander.max_health} [{hp_bar}]")
        lines.append(f"  火力: {self.commander.get_total_damage_output()}/回合")
        lines.append(f"  机动: {self.commander.get_mobility()}")

        lines.append(f"\n[敌方] {self.enemy.name}")
        hp_pct = self.enemy.current_health / self.enemy.max_health
        hp_bar = "+" * int(hp_pct * 20) + "-" * (20 - int(hp_pct * 20))
        lines.append(f"  战力: {self.enemy.current_health}/{self.enemy.max_health} [{hp_bar}]")

        return "\n".join(lines)

    def _execute_phase(self):
        """大战场回合逻辑"""
        # 1. 侦查阶段
        self._reconnaissance_phase()

        # 2. AI指挥决策
        self._ai_tactical_decision()

        # 3. 指挥官光环激活
        self._activate_commander_aura()

        # 4. 火力覆盖阶段
        self._fire_support_phase()

        # 5. 突击阶段
        self._assault_phase()

        # 6. 控制点争夺
        self._control_zone_phase()

        # 7. 天气更新（每2回合）
        if self.turn % 2 == 0:
            self._update_weather()

        # 8. 敌方行动
        self._enemy_action()

        self._log(self.render())

    def _reconnaissance_phase(self):
        """侦查阶段"""
        self._log("\n[侦查阶段]")
        detection_range = self.commander.get_communication_efficiency()
        self._log(f"  侦查范围: {detection_range}m")
        self._log(f"  敌方位置: 已锁定")
        self._log(f"  敌方战力: {self.enemy.current_health}/{self.enemy.max_health}")

    def _ai_tactical_decision(self):
        """AI指挥决策"""
        self._log("\n[指挥决策]")

        health_ratio = self.enemy.current_health / self.enemy.max_health

        if health_ratio > 0.7:
            tactic = "全面进攻"
            self.ai_tactic = "attack"
        elif health_ratio > 0.3:
            tactic = "稳步推进"
            self.ai_tactic = "defend"
        else:
            tactic = "围歼残敌"
            self.ai_tactic = "attack"

        self._log(f"  战术指令: {tactic}")
        self._log(f"  AI决策: {self.ai_tactic}")

    def _activate_commander_aura(self):
        """激活指挥官光环"""
        self._log("\n[指挥官光环]")
        if self.commander.operator.abilities:
            aura = self.commander.operator.abilities[0]
            if aura.active_duration == 0:
                result = self.commander.activate_ability(aura)
                if result['success']:
                    self.commander_aura_active = True
                    self._log(f"  ✓ {aura.name} 已激活")
                    self._log(f"    效果: 全军火力+15, 士气+20")
                    aura.active_duration = aura.effect.duration
                else:
                    self._log(f"  ✗ {aura.name} 激活失败")
            else:
                self._log(f"  ○ {aura.name} 持续中 (剩余{aura.active_duration}回合)")
                self.commander_aura_active = True
        self.commander.update_buffs()

    def _fire_support_phase(self):
        """火力覆盖阶段"""
        self._log("\n[火力覆盖阶段]")

        if self.ai_tactic in ("attack", "defend"):
            damage = self.commander.get_total_damage_output()
            weather_mod = self._get_weather_accuracy_mod()
            effective_damage = int(damage * weather_mod)
            self.enemy.take_damage(effective_damage)
            self._log(f"  155mm火炮群齐射!")
            self._log(f"  气象修正: ×{weather_mod:.2f}")
            self._log(f"  造成 {effective_damage} 点伤害")

            # 压制效果
            self.enemy.suppression_level += 20
            self._log(f"  敌方压制等级: +20 (当前: {self.enemy.suppression_level})")

    def _assault_phase(self):
        """突击阶段"""
        self._log("\n[突击阶段]")

        if self.ai_tactic == "attack":
            assault_damage = int(self.commander.get_total_damage_output() * 0.5)
            self.enemy.take_damage(assault_damage)
            self._log(f"  装甲突击群发起进攻!")
            self._log(f"  追加伤害: {assault_damage}")
        else:
            self._log("  部队转入防御态势")

    def _control_zone_phase(self):
        """控制点争夺阶段"""
        self._log("\n[控制点争夺]")

        for zone, state in self.control_zones.items():
            if self.ai_tactic == "attack":
                state["value"] += 1
                if state["value"] >= 3:
                    state["controller"] = "friendly"
                    self._log(f"  ✓ {zone} 已被我方控制!")
            elif self.ai_tactic == "defend":
                if state["controller"] == "enemy":
                    state["value"] -= 1
                    if state["value"] <= 0:
                        state["controller"] = "neutral"
                        self._log(f"  ○ {zone} 争夺中 (我方反攻)")
                else:
                    state["value"] = max(0, state["value"] - 1)
                    if state["value"] == 0 and state["controller"] == "friendly":
                        state["controller"] = "neutral"

            # 控制增益
            if state["controller"] == "friendly":
                heal = state["importance"] * 2
                self.commander.current_health = min(
                    self.commander.max_health,
                    self.commander.current_health + heal
                )
                self._log(f"  {zone} 补给: 我方回复{heal}生命")

    def _update_weather(self):
        """更新天气"""
        old = self.weather
        weathers = [
            WeatherCondition.CLEAR,
            WeatherCondition.RAINY,
            WeatherCondition.STORMY,
            WeatherCondition.FOGGY,
        ]
        # 随机转移天气
        if random.random() < 0.4:
            self.weather = random.choice(weathers)
            if self.weather != old:
                self._log(f"\n[天气变化] {old.value} → {self.weather.value}")
                # 天气效果
                if self.weather == WeatherCondition.STORMY:
                    self._log("  暴风雨: 所有单位移动-30%, 精度-25%")
                elif self.weather == WeatherCondition.FOGGY:
                    self._log("  大雾: 侦查范围-50%, 精度-15%")
                elif self.weather == WeatherCondition.RAINY:
                    self._log("  下雨: 移动-10%, 精度-10%")

    def _get_weather_accuracy_mod(self) -> float:
        """获取天气精度修正"""
        mods = {
            WeatherCondition.CLEAR: 1.0,
            WeatherCondition.RAINY: 0.9,
            WeatherCondition.STORMY: 0.75,
            WeatherCondition.FOGGY: 0.85,
        }
        return mods.get(self.weather, 1.0)

    def _enemy_action(self):
        """敌方行动"""
        if self.enemy.current_health <= 0:
            return

        self._log("\n[敌方行动]")
        counter = self.enemy.attack_power + random.randint(-50, 50)
        self.commander.take_damage(counter)
        self._log(f"  敌军反击! 造成 {counter} 点伤害")

        # 压制我方
        self.commander.suppression_level += 5
        self._log(f"  我方压制等级: +5 (当前: {self.commander.suppression_level})")


# ============================================================
# 情景2：潜入（单兵渗透侦察）
# ============================================================

class InfiltrationScenario(BaseScenario):
    """
    潜入 — 单兵渗透侦察

    特点：
    - 单兵级渗透行动
    - 预演系统可视化（3种路径选择）
    - 隐蔽值系统
    - 侦察道具布置
    - 发现状态机：隐蔽 → 可疑 → 发现 → 交战
    """

    name = "潜入"
    description = (
        "【单兵渗透侦察】\n"
        "       渗透至敌方防线深处，执行侦察或破坏任务。\n"
        "       利用预演能力分析路径风险，\n"
        "       保持隐蔽，避免被发现。"
    )
    map_size = (60, 30)

    def __init__(self):
        self.stealth = 100           # 当前隐蔽值
        self.detection_level = 0      # 敌方探测等级
        self.sensors_placed = []     # 已放置传感器
        self.objectives_reached = 0  # 已达成目标
        self.max_objectives = 3      # 目标数量
        self.discovered = False       # 是否被发现
        self.in_combat = False       # 是否进入战斗
        self.preview_paths = []       # 预演路径
        self.map_grid = None         # 地图网格
        super().__init__()

    def _init_units(self):
        """初始化单兵单位"""
        from modern_warfare_system import ModernWeapon, WeaponCategory, WeaponClass, BallisticProperties, CruiseProperties

        # 操作员
        operator = Operator("代号：影", AbilityTier.ADVANCED, is_commander=False)
        operator.combat_skill = 85
        operator.technical_skill = 95

        # 侦察能力
        recon_ability = Ability(
            "战术预演",
            AbilityTier.ADVANCED,
            AbilityEffect(
                name="战术预演",
                tier=AbilityTier.ADVANCED,
                description="预演3种行动路径，分析风险与成功率",
                success_rate=95,
                reality_debt=10,
                duration=1,
                accuracy_boost=20,
                detection_boost=30
            )
        )
        operator.add_ability(recon_ability)

        self.agent = WarfareUnit("渗透者", MachineScale.INDIVIDUAL, operator)
        self.agent.max_health = 120
        self.agent.current_health = 120
        self.agent.base_armor = 10
        self.agent.mobility = 90

        # 隐蔽装备
        smg = ModernWeapon(
            name="消音冲锋枪",
            weapon_class=WeaponClass.SMG,
            category=WeaponCategory.BALLISTIC,
            damage=25,
            rate_of_fire=3,
            accuracy=70,
            range_m=100,
            magazine_size=30,
            weight=2.5,
            special_features=["消音器", "红外瞄准"],
            suppression=False,
            ballistic=BallisticProperties(
                projectile_speed=400,
                falloff_start=50,
                falloff_rate=0.004,
            ),
        )
        self.agent.add_weapon(smg)

        self.friendly_units.append(self.agent)

        # 巡逻敌人
        for i in range(5):
            enemy = EnemyForce(
                f"巡逻哨兵#{i+1}",
                MachineScale.INDIVIDUAL,
                30,
                evasion=20
            )
            self.enemies.append(enemy)

        # 初始化地图网格
        self._init_grid()

    def _init_grid(self):
        """初始化渗透地图网格"""
        w, h = self.map_size
        # 0=空地, 1=掩体, 2=敌人感知范围, 3=目标点, 4=危险区
        self.map_grid = [[0] * w for _ in range(h)]

        # 放置掩体
        for _ in range(15):
            x, y = random.randint(5, w-5), random.randint(3, h-3)
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < w and 0 <= ny < h:
                        if (dx, dy) == (0, 0):
                            self.map_grid[ny][nx] = 1
                        else:
                            self.map_grid[ny][nx] = max(self.map_grid[ny][nx], 1)

        # 放置敌人感知范围（敌人巡逻点周围5格）
        enemy_x = [w//3, w//2, 2*w//3]
        enemy_y = [h//4, h//2, 3*h//4]
        for ex, ey in zip(enemy_x, enemy_y):
            for dy in range(-5, 6):
                for dx in range(-5, 6):
                    nx, ny = ex+dx, ey+dy
                    if 0 <= nx < w and 0 <= ny < h:
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist <= 5 and self.map_grid[ny][nx] == 0:
                            self.map_grid[ny][nx] = 2

        # 放置目标点
        self.objective_positions = [(w-5, h//2), (w-3, h//4), (w-3, 3*h//4)]
        for ox, oy in self.objective_positions:
            if 0 <= ox < w and 0 <= oy < h:
                self.map_grid[oy][ox] = 3

        # 放置危险区
        for _ in range(3):
            rx, ry = random.randint(10, w-10), random.randint(3, h-3)
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    nx, ny = rx+dx, ry+dy
                    if 0 <= nx < w and 0 <= ny < h:
                        if self.map_grid[ny][nx] == 0:
                            self.map_grid[ny][nx] = 4

    def setup_map(self) -> BattlefieldMap:
        """使用诺曼底风格地图（登陆+渗透）"""
        return HistoricBattlefieldGenerator.generate_normandy(
            width=60, height=30
        )

    def render(self) -> str:
        """渲染渗透状态"""
        w, h = self.map_size

        # 构建显示网格
        display = []
        for y in range(h):
            row = ""
            for x in range(w):
                # 检查单位
                if self.agent.current_health > 0 and not self.discovered:
                    if x == 3 and y == h//2:
                        row += "\033[92m我\033[0m"  # 绿色我方
                        continue

                # 检查目标
                if (x, y) in self.objective_positions:
                    if self.map_grid[y][x] == 3:
                        row += "\033[93m◎\033[0m"  # 黄色目标
                        continue

                # 检查敌人
                enemy_here = any(
                    e.current_health > 0 and
                    abs(x - (i+1) * w//6) < 2 and
                    abs(y - [h//4, h//2, 3*h//4][i % 3]) < 2
                    for i, e in enumerate(self.enemies)
                )
                if enemy_here and self.map_grid[y][x] == 2:
                    row += "\033[91m敌\033[0m"  # 红色敌人
                    continue

                # 地形
                tile = self.map_grid[y][x]
                symbols = {0: "·", 1: "▓", 2: "◐", 3: "◎", 4: "✖"}
                colors = {0: "", 1: "\033[90m", 2: "\033[33m", 3: "\033[93m", 4: "\033[91m"}
                row += f"{colors.get(tile, '')}{symbols.get(tile, '·')}\033[0m"

            display.append(row)

        lines = [
            f"\n[潜入] 第{self.turn}回合 | 隐蔽值: {self.stealth} | 探测等级: {self.detection_level}",
            "=" * 60,
            "  " + "".join(f"{i%10}" for i in range(w)),  # 坐标刻度
        ]
        for i, row in enumerate(display):
            lines.append(f"{i:2d}{row}")
        lines.append("  " + "·空地 ▓掩体 ◐巡逻区 ◎目标 ✖危险区")

        # 状态栏
        lines.append(f"\n[状态] 生命:{self.agent.current_health}/{self.agent.max_health} "
                     f"| 目标:{self.objectives_reached}/{self.max_objectives} "
                     f"| 传感器:{len(self.sensors_placed)}")

        if self.discovered:
            if self.in_combat:
                lines.append("  ⚠ [战斗中] 敌人已发现你!")
            else:
                lines.append("  ⚠ [可疑] 你可能已被发现，敌人正在搜索")
        else:
            lines.append("  ✓ [隐蔽] 未被发现")

        return "\n".join(lines)

    def _preview_paths(self) -> List[dict]:
        """预演：生成3种行动路径"""
        self._log("\n[战术预演] 使用能力分析路径...")

        ability = self.agent.operator.abilities[0]
        result = self.agent.activate_ability(ability)

        paths = []

        # 路径1：安全路线（绕远但隐蔽）
        paths.append({
            "name": "安全路线",
            "route": "左翼迂回 → 利用掩体 → 抵达目标",
            "stealth_risk": 15,
            "time_cost": 3,
            "success_rate": 88,
            "description": "绕远路，利用所有掩体，敌人感知范围边缘通过"
        })

        # 路径2：平衡路线
        paths.append({
            "name": "平衡路线",
            "route": "中央推进 → 穿越巡逻区 → 抵达目标",
            "stealth_risk": 45,
            "time_cost": 2,
            "success_rate": 65,
            "description": "直接路线，需穿越部分巡逻区，必要时可布置传感器"
        })

        # 路径3：激进路线
        paths.append({
            "name": "激进路线",
            "route": "正面突击 → 快速通过 → 立即撤离",
            "stealth_risk": 80,
            "time_cost": 1,
            "success_rate": 40,
            "description": "最快路线，但几乎必定被发现，需要准备交火"
        })

        self.preview_paths = paths

        self._log(f"\n  预演结果 ({len(paths)}种可能):")
        for i, p in enumerate(paths, 1):
            risk_icon = "🟢" if p["stealth_risk"] < 30 else "🟡" if p["stealth_risk"] < 60 else "🔴"
            self._log(f"  [{i}] {p['name']} {risk_icon}")
            self._log(f"      路线: {p['route']}")
            self._log(f"      隐蔽风险: {p['stealth_risk']}% | 成功率: {p['success_rate']}%")
            self._log(f"      描述: {p['description']}")

        return paths

    def _select_path(self) -> int:
        """让玩家选择路径"""
        self._preview_paths()

        while True:
            try:
                choice = input("\n[选择路径 1/2/3] > ").strip()
                if choice in ("1", "2", "3"):
                    return int(choice) - 1
                self._log("  无效输入，请输入 1、2 或 3")
            except (ValueError, EOFError):
                return 1  # 默认平衡路线

    def _execute_phase(self):
        """潜入回合逻辑"""
        self._log(self.render())

        # 检查是否被发现
        if self.discovered and not self.in_combat:
            self._log("\n[敌方搜索] 敌人正在搜索你的位置...")
            if random.random() < 0.3:
                self.in_combat = True
                self._log("  ⚠ 你被发现了! 进入战斗!")
            else:
                self._log("  ✓ 敌人暂时没有发现你")

        if self.in_combat:
            self._combat_phase()
            return

        if self.agent.current_health <= 0:
            return

        # 路径选择
        path_idx = self._select_path()
        path = self.preview_paths[path_idx]

        self._log(f"\n[执行] 选择: {path['name']}")

        # 隐蔽判定
        stealth_roll = random.randint(1, 100)
        risk = path["stealth_risk"]

        if stealth_roll > risk:
            # 成功隐蔽
            self._log(f"  ✓ 隐蔽判定: {stealth_roll} vs {risk} → 成功!")
            self.detection_level = max(0, self.detection_level - 5)

            # 检查是否到达目标
            if random.random() < 0.4:
                self.objectives_reached += 1
                self._log(f"  ★ 达成目标! ({self.objectives_reached}/{self.max_objectives})")
                # 标记目标为已完成
                if self.objectives_reached >= self.max_objectives:
                    self.result = "victory"
                    return

        else:
            # 被发现
            self._log(f"  ✗ 隐蔽判定: {stealth_roll} vs {risk} → 失败!")
            self.detection_level += risk // 2
            self._log(f"  探测等级: +{risk//2} → {self.detection_level}")

            if self.detection_level >= 50:
                self.discovered = True
                self._log("  ⚠ 你已被发现!")
                self.in_combat = True
                # 敌人开始追击
                for enemy in self.enemies:
                    if enemy.current_health > 0:
                        enemy.attack_power += 20

        # 放置传感器（消耗行动）
        if len(self.sensors_placed) < 5 and not self.in_combat:
            place = input("  [放置传感器? y/n] > ").strip().lower()
            if place == 'y':
                self.sensors_placed.append((3 + len(self.sensors_placed), self.map_size[1]//2))
                self._log(f"  ✓ 传感器#{len(self.sensors_placed)} 已布置")
                self.stealth = min(100, self.stealth + 10)

        # 敌人巡逻移动
        self._enemy_patrol()

        # 消耗体力
        fatigue = path["time_cost"] * 5
        self.agent.operator.fatigue = min(100, self.agent.operator.fatigue + fatigue)
        self._log(f"  疲劳: +{fatigue} (当前: {self.agent.operator.fatigue})")

    def _combat_phase(self):
        """潜入中的遭遇战"""
        self._log("\n[遭遇战]")

        if not self.enemies:
            self._log("  没有敌人")
            return

        # 选择最近的敌人
        enemy = self.enemies[0]
        if enemy.current_health <= 0:
            enemy = self.enemies[1] if len(self.enemies) > 1 else None

        if not enemy:
            self.in_combat = False
            self.discovered = False
            self._log("  敌人已被消灭")
            return

        self._log(f"  目标: {enemy.name} (战力:{enemy.current_health})")

        # 我方攻击（先手）
        damage = self.agent.get_total_damage_output()
        hit_chance = 70 - self.detection_level // 5
        if random.randint(1, 100) <= hit_chance:
            enemy.take_damage(damage)
            self._log(f"  消音冲锋枪命中! 造成 {damage} 点伤害")
        else:
            self._log("  射击未命中!")

        # 敌人在隐蔽状态下的低效攻击
        if enemy.current_health > 0:
            enemy_damage = enemy.attack_power + random.randint(-5, 15)
            self.agent.take_damage(enemy_damage)
            self._log(f"  {enemy.name} 反击! 造成 {enemy_damage} 点伤害")

            # 追击风险
            if random.random() < 0.3:
                self._log("  ⚠ 附近敌人正在赶来支援!")

        # 脱离判定
        if enemy.current_health <= 0 or random.random() < 0.4:
            self.in_combat = False
            self.discovered = random.random() < 0.5  # 30%概率继续被发现
            if not self.discovered:
                self._log("  ✓ 成功脱离战斗")
                self.stealth = min(100, self.stealth + 20)
            else:
                self._log("  ⚠ 脱离战斗但仍在被追击中")

    def _enemy_patrol(self):
        """敌人巡逻"""
        self._log("\n[巡逻情报]")
        active = sum(1 for e in self.enemies if e.current_health > 0)

        # 传感器提供情报
        if self.sensors_placed:
            detected = random.randint(0, len(self.sensors_placed))
            if detected > 0:
                self._log(f"  传感器探测: 发现{active}个敌人在巡逻")
                self.stealth = min(100, self.stealth + detected * 5)
                self._log(f"  隐蔽值: +{detected*5} (传感器补偿)")
        else:
            self._log(f"  无传感器，敌人在{active}个区域巡逻")
            self.detection_level += 2
            self._log(f"  探测等级: +2 (无情报支持)")

    def check_end(self) -> Optional[str]:
        """检查结束条件"""
        if self.objectives_reached >= self.max_objectives:
            return "victory"
        if self.agent.current_health <= 0:
            return "defeat"
        if self.turn >= self.max_turns:
            return "timeout"
        return None


# ============================================================
# 情景3：小队作战（3-5人协同战术）
# ============================================================

class SquadScenario(BaseScenario):
    """
    小队作战 — 3-5人协同战术

    特点：
    - 小队级协同战斗
    - 角色定位（侦察/突击/支援/指挥）
    - 协同技能系统（组合触发）
    - 战术指令广播
    - 物资点管理（弹药/医疗包）
    """

    name = "小队作战"
    description = (
        "【小队协同战术】\n"
        "       3-5人小队执行战术任务。\n"
        "       合理利用角色定位和协同技能，\n"
        "       指令统一，全队协调行动。"
    )
    map_size = (50, 25)

    # 角色定义
    ROLE_SCOUT = "scout"
    ROLE_ASSAULT = "assault"
    ROLE_SUPPORT = "support"
    ROLE_COMMAND = "command"

    # 协同技能表
    COORDINATION_SKILLS = {
        (ROLE_SCOUT, ROLE_ASSAULT): {
            "name": "侦察-突击连锁",
            "effect": "侦察指引突击命中率+25%，伤害+15",
            "bonus": {"accuracy": 25, "damage": 15}
        },
        (ROLE_ASSAULT, ROLE_SUPPORT): {
            "name": "突击-支援协同",
            "effect": "突击手获得支援掩护，受伤-20%",
            "bonus": {"damage_reduction": 20}
        },
        (ROLE_SCOUT, ROLE_SUPPORT): {
            "name": "侦察-支援配合",
            "effect": "侦察范围+50%，支援效率+30%",
            "bonus": {"detection": 50, "heal": 30}
        },
        (ROLE_COMMAND, ROLE_ASSAULT): {
            "name": "指挥-突击协同",
            "effect": "突击伤害+30%，士气高涨",
            "bonus": {"damage": 30, "morale": 20}
        },
        (ROLE_COMMAND, ROLE_SCOUT): {
            "name": "指挥-侦察联动",
            "effect": "侦察精度+40%，情报共享",
            "bonus": {"detection": 40, "stealth": 20}
        },
    }

    def __init__(self):
        self.tactical_orders = "hold"  # hold / advance / flank / retreat
        self.supply_points = 10       # 物资点
        self.squad_coordination = 0   # 默契度
        self.active_synergy = None    # 当前激活的协同技能
        super().__init__()

    def _init_units(self):
        """初始化小队成员"""
        from modern_warfare_system import ModernWeapon, WeaponCategory, WeaponClass, BallisticProperties, CruiseProperties

        # 角色1：侦察员
        scout_op = Operator("林锐", AbilityTier.BASIC, is_commander=False)
        scout_op.combat_skill = 70
        scout_op.technical_skill = 90
        scout = WarfareUnit("侦察员-林锐", MachineScale.SQUAD, scout_op)
        scout.max_health = 150
        scout.current_health = 150
        scout.base_armor = 10
        scout.mobility = 95
        scout.role = self.ROLE_SCOUT

        rifle = ModernWeapon(
            name="侦察步枪",
            weapon_class=WeaponClass.SNIPER,
            category=WeaponCategory.BALLISTIC,
            damage=35,
            rate_of_fire=2,
            accuracy=85,
            range_m=400,
            magazine_size=20,
            weight=3.2,
            special_features=["瞄准镜", "消音器"],
            suppression=False,
            ballistic=BallisticProperties(
                projectile_speed=800,
                falloff_start=200,
                falloff_rate=0.002,
            ),
        )
        scout.add_weapon(rifle)

        # 角色2：突击手
        assault_op = Operator("王铁", AbilityTier.BASIC, is_commander=False)
        assault_op.combat_skill = 95
        assault_op.technical_skill = 60
        assault = WarfareUnit("突击手-王铁", MachineScale.SQUAD, assault_op)
        assault.max_health = 200
        assault.current_health = 200
        assault.base_armor = 20
        assault.mobility = 75
        assault.role = self.ROLE_ASSAULT

        smg = ModernWeapon(
            name="突击步枪",
            weapon_class=WeaponClass.RIFLE,
            category=WeaponCategory.BALLISTIC,
            damage=45,
            rate_of_fire=3,
            accuracy=75,
            range_m=300,
            magazine_size=30,
            weight=3.8,
            special_features=["前握把", "光学瞄准"],
            suppression=True,
            ballistic=BallisticProperties(
                projectile_speed=800,
                falloff_start=200,
                falloff_rate=0.003,
            ),
        )
        assault.add_weapon(smg)

        # 角色3：支援手
        support_op = Operator("赵芸", AbilityTier.BASIC, is_commander=False)
        support_op.combat_skill = 60
        support_op.technical_skill = 80
        support = WarfareUnit("支援手-赵芸", MachineScale.SQUAD, support_op)
        support.max_health = 120
        support.current_health = 120
        support.base_armor = 15
        support.mobility = 60
        support.role = self.ROLE_SUPPORT

        lmg = ModernWeapon(
            name="轻机枪",
            weapon_class=WeaponClass.MG,
            category=WeaponCategory.BALLISTIC,
            damage=55,
            rate_of_fire=2,
            accuracy=60,
            range_m=600,
            magazine_size=200,
            weight=8.0,
            special_features=["两脚架"],
            suppression=True,
            ballistic=BallisticProperties(
                projectile_speed=800,
                falloff_start=350,
                falloff_rate=0.001,
            ),
        )
        support.add_weapon(lmg)

        self.friendly_units = [scout, assault, support]

        # 敌人群
        for i in range(3):
            enemy = EnemyForce(
                f"敌方步兵班#{i+1}",
                MachineScale.SQUAD,
                150,
                evasion=15
            )
            self.enemies.append(enemy)

    def render(self) -> str:
        """渲染小队状态"""
        lines = [
            f"\n[小队作战] 第{self.turn}回合 | 物资:{self.supply_points} | 默契:{self.squad_coordination}%",
            "=" * 60,
            f"\n[战术指令] {self._get_order_name()}",
        ]

        # 小队成员状态
        lines.append("\n[小队成员]")
        for unit in self.friendly_units:
            role_icon = {"scout": "🔍", "assault": "⚔", "support": "🛡", "command": "🎖"}
            icon = role_icon.get(getattr(unit, 'role', ''), "○")
            hp_pct = unit.current_health / unit.max_health
            hp_bar = "+" * int(hp_pct * 15) + "-" * (15 - int(hp_pct * 15))
            mobility = unit.get_mobility()

            lines.append(f"  {icon} {unit.name} HP:[{hp_bar}] {unit.current_health}/{unit.max_health} 机动:{mobility}")

            # 负重状态
            total_weight = sum(w.weight for w in unit.weapons)
            base = 100
            ratio = total_weight / base
            if ratio > 1.0:
                lines.append(f"      ⚠ 负重超载({total_weight:.1f}kg) 机动-{int((ratio-1)*60)}%")

        # 敌人状态
        lines.append("\n[敌方目标]")
        for enemy in self.enemies:
            if enemy.current_health > 0:
                hp_pct = enemy.current_health / enemy.max_health
                hp_bar = "+" * int(hp_pct * 15) + "-" * (15 - int(hp_pct * 15))
                lines.append(f"  ■ {enemy.name} HP:[{hp_bar}] {enemy.current_health}/{enemy.max_health}")

        # 协同技能状态
        if self.active_synergy:
            lines.append(f"\n[协同技能] ★ {self.active_synergy['name']} — {self.active_synergy['effect']}")
        else:
            lines.append(f"\n[协同技能] ○ 无激活 (需要2名成员相邻)")
            synergy = self._detect_synergy()
            if synergy:
                lines.append(f"  → 可触发: {synergy['name']}")

        return "\n".join(lines)

    def _get_order_name(self) -> str:
        names = {"hold": "原地防守", "advance": "全面进攻",
                 "flank": "两翼包围", "retreat": "战术撤退"}
        return names.get(self.tactical_orders, "待命")

    def _select_orders(self):
        """选择战术指令"""
        self._log("\n[战术指令]")
        self._log("  1. 原地防守 (hold)")
        self._log("  2. 全面进攻 (advance)")
        self._log("  3. 两翼包围 (flank)")
        self._log("  4. 战术撤退 (retreat)")

        orders = {"1": "hold", "2": "advance", "3": "flank", "4": "retreat"}
        while True:
            try:
                choice = input("\n[选择指令 1/2/3/4] > ").strip()
                if choice in orders:
                    self.tactical_orders = orders[choice]
                    break
                self._log("  无效输入")
            except (ValueError, EOFError):
                break

        order_names = {"hold": "原地防守", "advance": "全面进攻",
                       "flank": "两翼包围", "retreat": "战术撤退"}
        self._log(f"  指令已下达: {order_names[self.tactical_orders]}")

    def _detect_synergy(self) -> Optional[dict]:
        """检测协同技能"""
        roles = [getattr(u, 'role', None) for u in self.friendly_units
                 if u.current_health > 0]

        for (role1, role2), synergy in self.COORDINATION_SKILLS.items():
            if role1 in roles and role2 in roles:
                return synergy
        return None

    def _activate_synergy(self):
        """激活协同技能"""
        synergy = self._detect_synergy()
        if synergy:
            self.active_synergy = synergy
            self.squad_coordination = min(100, self.squad_coordination + 10)
            self._log(f"\n[协同技能激活] ★ {synergy['name']}")
            self._log(f"  效果: {synergy['effect']}")
            self._log(f"  默契度: {self.squad_coordination}%")

    def _execute_phase(self):
        """小队回合逻辑"""
        self._log(self.render())

        # 选择战术指令
        if self.turn == 1:
            self._select_orders()

        # 协同技能检测
        synergy = self._detect_synergy()
        if synergy and not self.active_synergy:
            self._activate_synergy()
        elif self.active_synergy:
            self._log(f"\n[协同技能] ○ {self.active_synergy['name']} 持续中")

        # 战术执行
        if self.tactical_orders == "advance":
            self._tactical_assault()
        elif self.tactical_orders == "hold":
            self._tactical_defend()
        elif self.tactical_orders == "flank":
            self._tactical_flank()
        elif self.tactical_orders == "retreat":
            self._tactical_retreat()

        # 物资管理
        self._supply_phase()

        # 敌方行动
        self._enemy_response()

        # 回合结束：更新buff
        for unit in self.friendly_units:
            if unit.current_health > 0:
                unit.update_buffs()

        # 默契度衰减
        if self.turn % 3 == 0:
            self.squad_coordination = max(0, self.squad_coordination - 5)

    def _tactical_assault(self):
        """全面进攻"""
        self._log("\n[全面进攻]")

        synergy_bonus = {}
        if self.active_synergy:
            synergy_bonus = self.active_synergy.get("bonus", {})

        for unit in self.friendly_units:
            if unit.current_health <= 0:
                continue

            if getattr(unit, 'role', '') == self.ROLE_ASSAULT:
                damage = unit.get_total_damage_output()
                damage_bonus = synergy_bonus.get("damage", 0)
                effective = int(damage * (1 + damage_bonus/100))

                for enemy in self.enemies:
                    if enemy.current_health > 0:
                        enemy.take_damage(effective)
                        self._log(f"  ⚔ {unit.name} 突击! 伤害+{damage_bonus}% → {effective}")
                        break

            elif getattr(unit, 'role', '') == self.ROLE_SCOUT:
                detection = unit.get_communication_efficiency()
                detect_bonus = synergy_bonus.get("detection", 0)
                self._log(f"  🔍 {unit.name} 前沿侦察 探测范围+{detect_bonus}m")

            elif getattr(unit, 'role', '') == self.ROLE_SUPPORT:
                heal_bonus = synergy_bonus.get("heal", 0)
                target = min(self.friendly_units, key=lambda u: u.current_health / u.max_health
                             if u.current_health > 0 else 999)
                heal = 15 + heal_bonus
                target.current_health = min(target.max_health, target.current_health + heal)
                self._log(f"  🛡 {unit.name} 战场支援 回复{heal}HP → {target.name}")

    def _tactical_defend(self):
        """原地防守"""
        self._log("\n[原地防守]")

        for unit in self.friendly_units:
            if unit.current_health <= 0:
                continue

            # 防守姿态：精准射击
            if unit.weapons:
                weapon = unit.weapons[0]
                accuracy_mod = 15  # 防守时精度提升
                damage = unit.get_total_damage_output()

                for enemy in self.enemies:
                    if enemy.current_health > 0:
                        hit = random.randint(1, 100) <= (weapon.accuracy + accuracy_mod)
                        if hit:
                            enemy.take_damage(damage)
                            self._log(f"  🛡 {unit.name} 精准射击 命中 {enemy.name} -{damage}")
                        else:
                            self._log(f"  🛡 {unit.name} 射击未命中")
                        break

    def _tactical_flank(self):
        """两翼包围"""
        self._log("\n[两翼包围]")

        # 协同加成
        synergy_bonus = {}
        if self.active_synergy:
            synergy_bonus = self.active_synergy.get("bonus", {})

        hit_count = 0
        for enemy in self.enemies:
            if enemy.current_health > 0:
                total_damage = sum(
                    int(u.get_total_damage_output() * (1 + synergy_bonus.get("damage", 0)/100))
                    for u in self.friendly_units
                    if u.current_health > 0
                )
                enemy.take_damage(total_damage)
                hit_count += 1
                self._log(f"  ⚔ 包围射击! 集中{len([u for u in self.friendly_units if u.current_health>0])}把枪 → {enemy.name} -{total_damage}")
                break

        if hit_count == 0:
            self._log("  无有效目标")

    def _tactical_retreat(self):
        """战术撤退"""
        self._log("\n[战术撤退]")

        # 边打边撤
        for unit in self.friendly_units:
            if unit.current_health > 0 and unit.weapons:
                enemy = self.enemies[0] if self.enemies else None
                if enemy and enemy.current_health > 0:
                    damage = int(unit.get_total_damage_output() * 0.5)
                    enemy.take_damage(damage)
                    self._log(f"  ← {unit.name} 边撤边打 -{damage}")
                    break

        # 所有单位回复少量生命
        for unit in self.friendly_units:
            if unit.current_health > 0:
                heal = 5
                unit.current_health = min(unit.max_health, unit.current_health + heal)
        self._log("  全队边撤边回复: +5HP")

    def _supply_phase(self):
        """物资管理阶段"""
        self._log("\n[物资管理]")

        self._log(f"  物资点: {self.supply_points}")

        # 消耗弹药
        ammo_used = sum(
            len(unit.weapons) for unit in self.friendly_units
            if unit.current_health > 0
        )
        self.supply_points = max(0, self.supply_points - ammo_used // 2)
        self._log(f"  弹药消耗: -{ammo_used//2} (剩余: {self.supply_points})")

        if self.supply_points < 3:
            self._log("  ⚠ 物资告急! 需要补充!")

    def _enemy_response(self):
        """敌方反应"""
        self._log("\n[敌方行动]")

        for enemy in self.enemies:
            if enemy.current_health <= 0:
                continue

            # 战术影响
            if self.tactical_orders == "hold":
                # 敌人进攻困难
                damage = enemy.attack_power // 2
                self._log(f"  ■ {enemy.name} 进攻困难 造成{damage}")
            elif self.tactical_orders == "retreat":
                # 敌人追击
                damage = enemy.attack_power
                self._log(f"  ■ {enemy.name} 追击 造成{damage}")
            else:
                damage = enemy.attack_power
                self._log(f"  ■ {enemy.name} 火力压制 造成{damage}")

            # 应用伤害到最前线的单位
            alive = [u for u in self.friendly_units if u.current_health > 0]
            if alive:
                target = alive[0]  # 最前线的成员
                reduction = self.active_synergy.get("bonus", {}).get("damage_reduction", 0) if self.active_synergy else 0
                actual = int(damage * (1 - reduction/100))
                target.take_damage(actual)
                self._log(f"    → {target.name} 受伤{actual}")


# ============================================================
# 演示入口
# ============================================================

def demo_menu():
    """情景选择菜单"""
    print("\n" + "=" * 70)
    print("  宇宙之影 — 战斗情景选择")
    print("=" * 70)
    print()
    print("  [1] 大战场      — 军团级正面战，多区域控制")
    print("  [2] 潜入        — 单兵渗透侦察，预演路径分析")
    print("  [3] 小队作战    — 3-5人协同战术，角色配合")
    print()
    print("  [0] 退出")
    print()

    while True:
        try:
            choice = input("  选择情景 [1/2/3/0] > ").strip()
            if choice == "1":
                BattlefieldScenario().run()
                break
            elif choice == "2":
                InfiltrationScenario().run()
                break
            elif choice == "3":
                SquadScenario().run()
                break
            elif choice == "0":
                print("\n[退出]")
                break
            else:
                print("  无效输入")
        except (ValueError, EOFError, KeyboardInterrupt):
            print("\n[退出]")
            break


if __name__ == "__main__":
    demo_menu()
