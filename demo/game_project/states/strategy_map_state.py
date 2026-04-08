"""
战略地图状态
Strategy Map State - 对应 Unity 的 MainMapScene
"""

import pygame
import math
from core.state_manager import BaseState, GameState
from data import (
    create_test_star_map, create_player_fleet, create_enemy_fleet,
    get_node_by_id, StarNode, Fleet, DebtLevel, NodeType,
)
from config import Colors, get_font


class StrategyMapState(BaseState):
    """战略地图状态"""

    def initialize(self, **kwargs):
        """初始化地图"""
        self.setup_map()
        self.setup_hud()

    def setup_map(self):
        """设置星图数据"""
        self.nodes = create_test_star_map()
        self.player_fleet = create_player_fleet("node_0")
        self.enemy_fleet = create_enemy_fleet("node_3")

        # 将舰队位置映射到节点坐标
        self.fleets = [self.player_fleet, self.enemy_fleet]

        # 地图缩放/偏移（适配屏幕）
        self.map_offset_x = 100
        self.map_offset_y = 80
        self.map_scale = 1.0

        # 交互状态
        self.selected_node: StarNode | None = None
        self.hovered_node: StarNode | None = None
        self.hovered_fleet: Fleet | None = None

        # 路径预览
        self.path_preview: list[StarNode] = []

        # 连接节点坐标
        self._update_node_screen_positions()

    def _update_node_screen_positions(self):
        """更新节点的屏幕坐标"""
        for node in self.nodes:
            node.screen_x = int(node.x * self.map_scale + self.map_offset_x)
            node.screen_y = int(node.y * self.map_scale + self.map_offset_y)

    def setup_hud(self):
        """设置 HUD 信息"""
        self.player_debt = 0
        self.max_debt = 1000
        self.normal_resource = 500
        self.compromise_points = 50

    def on_exit(self):
        """退出状态时清理"""
        print(f"退出状态: {self.__class__.__name__}")

    # ==================== 交互 ====================

    def _get_node_at(self, x: int, y: int) -> StarNode | None:
        """获取指定像素坐标下的节点"""
        radius = 20
        for node in self.nodes:
            sx, sy = node.screen_x, node.screen_y
            if (x - sx) ** 2 + (y - sy) ** 2 <= radius ** 2:
                return node
        return None

    def _get_fleet_at(self, x: int, y: int) -> Fleet | None:
        """获取指定像素坐标下的舰队"""
        radius = 15
        for fleet in self.fleets:
            if fleet.current_node_id is None:
                continue
            node = get_node_by_id(self.nodes, fleet.current_node_id)
            if node is None:
                continue
            sx, sy = node.screen_x, node.screen_y
            if (x - sx) ** 2 + (y - sy) ** 2 <= radius ** 2:
                return fleet
        return None

    def _get_connected_nodes(self, node: StarNode) -> list[StarNode]:
        """获取与节点相连的所有节点"""
        result = []
        for conn_id in node.connections:
            conn = get_node_by_id(self.nodes, conn_id)
            if conn:
                result.append(conn)
        return result

    def _move_fleet_to(self, fleet: Fleet, target_node: StarNode):
        """将舰队移动到目标节点"""
        if not target_node.is_passable():
            print(f"[移动失败] {target_node.name} 为死区，无法进入")
            return
        if fleet.has_acted:
            print(f"[移动失败] {fleet.name} 本回合已行动")
            return

        # 简单路径：直线移动（简化版 A*）
        path_ids = [target_node.id]
        fleet.move_to(target_node.id, path_ids)
        print(f"[移动] {fleet.name} -> {target_node.name}")

        # 如果目标有敌军，进入战斗
        enemy_in_node = (
            fleet.team == "player"
            and target_node.owner == "enemy"
            and target_node.garrison_strength > 0
        )
        if enemy_in_node:
            print(f"[战斗触发] {fleet.name} 在 {target_node.name} 遭遇敌军！")
            # TODO: 切换到 BattleState

    # ==================== 回合逻辑 ====================

    def start_player_turn(self):
        """开始玩家回合"""
        self.player_fleet.has_acted = False
        self.player_debt = max(0, self.player_debt - 5)  # 每回合减少5点债务
        print("[回合开始] 玩家回合")

    def end_player_turn(self):
        """结束玩家回合"""
        print("[回合结束] 玩家回合")
        self._run_enemy_turn()

    def _run_enemy_turn(self):
        """运行敌方回合（简单AI）"""
        print("[敌方回合]")
        # 简单AI：向玩家方向移动
        enemy = self.enemy_fleet
        if enemy.has_acted:
            return

        current = get_node_by_id(self.nodes, enemy.current_node_id)
        if current is None:
            return

        # 找到连接节点中距离玩家舰队最近的
        best_target = None
        best_dist = float("inf")
        player_node = get_node_by_id(self.nodes, self.player_fleet.current_node_id)
        if player_node is None:
            return

        for conn_id in current.connections:
            conn = get_node_by_id(self.nodes, conn_id)
            if conn and conn.is_passable():
                dist = math.hypot(conn.x - player_node.x, conn.y - player_node.y)
                if dist < best_dist:
                    best_dist = dist
                    best_target = conn

        if best_target:
            enemy.move_to(best_target.id, [best_target.id])
            print(f"[敌方移动] {enemy.name} -> {best_target.name}")

    # ==================== 更新 ====================

    def update(self, delta_time):
        """更新地图"""
        # 更新所有节点债务等级
        for node in self.nodes:
            node.update_debt_level()

    # ==================== 渲染 ====================

    def render(self, screen):
        """渲染战略地图"""
        screen.fill((10, 10, 20))

        # 渲染连接线
        self._render_connections(screen)
        # 渲染路径预览
        self._render_path_preview(screen)
        # 渲染节点
        self._render_nodes(screen)
        # 渲染舰队
        self._render_fleets(screen)
        # 渲染HUD
        self._render_hud(screen)
        # 渲染选中信息
        if self.selected_node:
            self._render_node_info(screen, self.selected_node)

    def _render_connections(self, screen):
        """渲染节点连接线"""
        drawn = set()
        for node in self.nodes:
            sx1, sy1 = node.screen_x, node.screen_y
            for conn_id in node.connections:
                edge_key = tuple(sorted([node.id, conn_id]))
                if edge_key in drawn:
                    continue
                drawn.add(edge_key)
                conn = get_node_by_id(self.nodes, conn_id)
                if conn:
                    sx2, sy2 = conn.screen_x, conn.screen_y
                    color = (50, 50, 80) if node.owner == conn.owner else (80, 40, 40)
                    pygame.draw.line(screen, color, (sx1, sy1), (sx2, sy2), 2)

    def _render_path_preview(self, screen):
        """渲染路径预览"""
        if len(self.path_preview) < 2:
            return
        for i in range(len(self.path_preview) - 1):
            n1, n2 = self.path_preview[i], self.path_preview[i + 1]
            pygame.draw.line(screen, (100, 150, 255), (n1.screen_x, n1.screen_y), (n2.screen_x, n2.screen_y), 3)

    def _render_nodes(self, screen):
        """渲染所有节点"""
        font_small = get_font(18)
        for node in self.nodes:
            sx, sy = node.screen_x, node.screen_y
            color = node.get_color()
            is_selected = node is self.selected_node
            is_hovered = node is self.hovered_node

            # 节点外圈
            base_radius = 18
            if is_selected:
                pygame.draw.circle(screen, Colors.HIGHLIGHT, (sx, sy), base_radius + 6, 2)
            elif is_hovered:
                pygame.draw.circle(screen, (150, 150, 180), (sx, sy), base_radius + 3, 1)

            # 节点主体
            pygame.draw.circle(screen, color, (sx, sy), base_radius)
            pygame.draw.circle(screen, (20, 20, 30), (sx, sy), base_radius, 2)

            # 节点类型图标
            icons = {
                NodeType.HOME_BASE: "H",
                NodeType.STRATEGIC: "S",
                NodeType.RESOURCE: "R",
                NodeType.DANGER: "X",
                NodeType.JUMP_GATE: "J",
                NodeType.NORMAL: "N",
            }
            icon_text = font_small.render(icons.get(node.node_type, "?"), True, (255, 255, 255))
            screen.blit(icon_text, icon_text.get_rect(center=(sx, sy - 3)))

            # 已探索标记
            if node.is_explored:
                debt_text = font_small.render(str(node.reality_debt), True, (200, 200, 200))
                screen.blit(debt_text, debt_text.get_rect(center=(sx, sy + base_radius + 10)))

    def _render_fleets(self, screen):
        """渲染舰队标记"""
        font_small = get_font(16)
        for fleet in self.fleets:
            if fleet.current_node_id is None:
                continue
            node = get_node_by_id(self.nodes, fleet.current_node_id)
            if node is None:
                continue
            sx, sy = node.screen_x, node.screen_y

            color = (100, 180, 255) if fleet.team == "player" else (255, 80, 80)
            label = "P" if fleet.team == "player" else "E"

            # 舰队标记（三角形）
            points = [
                (sx, sy - 12),
                (sx - 8, sy + 6),
                (sx + 8, sy + 6),
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, (255, 255, 255), points, 1)

            # 舰队名
            name_text = font_small.render(label, True, (255, 255, 255))
            screen.blit(name_text, name_text.get_rect(center=(sx, sy - 22)))

            # 已行动标记
            if fleet.has_acted:
                pygame.draw.circle(screen, (100, 100, 100), (sx + 10, sy - 10), 4)

    def _render_hud(self, screen):
        """渲染顶部 HUD"""
        w, h = self.screen_size
        hud_height = 50

        # HUD 背景
        hud_rect = pygame.Rect(0, 0, w, hud_height)
        pygame.draw.rect(screen, (20, 20, 35), hud_rect)
        pygame.draw.line(screen, (60, 60, 80), (0, hud_height), (w, hud_height), 1)

        font = get_font(24)

        # 现实债务
        debt_color = Colors.RISK_LOW
        if self.player_debt > 400:
            debt_color = Colors.RISK_HIGH
        if self.player_debt > 700:
            debt_color = Colors.RISK_CRITICAL

        debt_text = font.render(f"现实债务: {self.player_debt}/{self.max_debt}", True, debt_color)
        screen.blit(debt_text, (20, 15))

        # 妥协点数
        compromise_text = font.render(f"妥协点数: {self.compromise_points}", True, Colors.HIGHLIGHT)
        screen.blit(compromise_text, (250, 15))

        # 常规资源
        resource_text = font.render(f"资源: {self.normal_resource}", True, Colors.TEXT)
        screen.blit(resource_text, (480, 15))

        # 返回菜单按钮
        btn_w, btn_h = 100, 32
        btn_x, btn_y = w - btn_w - 15, (hud_height - btn_h) // 2
        self._menu_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        pygame.draw.rect(screen, (60, 60, 90), self._menu_btn_rect, border_radius=4)
        menu_text = font.render("返回菜单", True, Colors.TEXT)
        screen.blit(menu_text, menu_text.get_rect(center=self._menu_btn_rect.center))

    def _render_node_info(self, screen, node: StarNode):
        """渲染选中节点信息面板"""
        font = get_font(22)
        w, h = self.screen_size

        panel_w, panel_h = 280, 200
        panel_x, panel_y = w - panel_w - 15, 70

        pygame.draw.rect(screen, (30, 30, 50), (panel_x, panel_y, panel_w, panel_h), border_radius=6)
        pygame.draw.rect(screen, Colors.BORDER, (panel_x, panel_y, panel_w, panel_h), 2, border_radius=6)

        lines = [
            f"节点: {node.name}",
            f"类型: {node.node_type.value}",
            f"现实债务: {node.reality_debt}",
            f"债务等级: {node.debt_level.label}",
            f"占领: {node.owner}",
            f"驻军: {node.garrison_strength}",
            "",
            f"连接节点: {len(node.connections)}",
        ]

        y = panel_y + 15
        for line in lines:
            text = font.render(line, True, Colors.TEXT)
            screen.blit(text, (panel_x + 15, y))
            y += 22

        # 可连接节点列表
        connected = self._get_connected_nodes(node)
        hint_y = y + 5
        if connected:
            hint = font.render("相邻: " + ", ".join(n.name for n in connected[:4]), True, (150, 150, 180))
            screen.blit(hint, (panel_x + 15, hint_y))

    # ==================== 事件处理 ====================

    def handle_event(self, event):
        """处理 pygame 事件"""
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self.hovered_node = self._get_node_at(mx, my)
            self.hovered_fleet = self._get_fleet_at(mx, my)

            # 更新路径预览
            if self.selected_node and self.hovered_node:
                if self.hovered_node.id in self.selected_node.connections:
                    self.path_preview = [self.selected_node, self.hovered_node]
                else:
                    self.path_preview = []
            else:
                self.path_preview = []

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # 返回菜单按钮
            if hasattr(self, '_menu_btn_rect') and self._menu_btn_rect.collidepoint(mx, my):
                self.game.state_manager.change_state(GameState.MENU)
                return

            # 点击节点
            clicked_node = self._get_node_at(mx, my)
            if clicked_node:
                if self.selected_node == clicked_node:
                    # 双击节点：移动玩家舰队到该节点
                    self._move_fleet_to(self.player_fleet, clicked_node)
                else:
                    self.selected_node = clicked_node
                    print(f"[选中] {clicked_node.name}")
                return

            # 点击舰队
            clicked_fleet = self._get_fleet_at(mx, my)
            if clicked_fleet:
                if clicked_fleet.current_node_id:
                    sel = get_node_by_id(self.nodes, clicked_fleet.current_node_id)
                    if sel:
                        self.selected_node = sel
                        print(f"[选中舰队] {clicked_fleet.name} @ {sel.name}")

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.state_manager.change_state(GameState.MENU)
            elif event.key == pygame.K_SPACE:
                self.end_player_turn()
            elif event.key == pygame.K_1:
                # 快捷键：触发战斗演示
                print("[演示] 启动战斗演示...")
                self._run_battle_demo()

    def _run_battle_demo(self):
        """运行战斗演示（使用 map_combat 系统）"""
        try:
            from map_combat import demo_enhanced_combat
            print("[战斗演示] 切换到文本模式演示...")
            # 切换到文本模式（pygame 窗口无法直接显示）
            print("=" * 60)
            print("[战斗演示] 使用增强战斗系统")
            print("=" * 60)
            # 在新线程中运行（实际项目应切换到 BattleState）
            import threading
            t = threading.Thread(target=self._run_text_battle_demo, daemon=True)
            t.start()
        except Exception as e:
            print(f"[错误] 无法启动战斗演示: {e}")

    def _run_text_battle_demo(self):
        """文本模式战斗演示"""
        try:
            from map_combat import demo_enhanced_combat
            demo_enhanced_combat()
        except Exception as e:
            print(f"[战斗演示错误] {e}")
