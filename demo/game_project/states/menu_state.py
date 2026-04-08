"""
菜单状态
Menu State
"""

import pygame
from core.state_manager import BaseState, GameState
from ui.base import Button, Panel, TextDisplay
from config import Colors, get_font


class MenuState(BaseState):
    """菜单状态"""

    def initialize(self, **kwargs):
        """初始化菜单"""
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        # 创建标题
        title = TextDisplay(
            self.screen_size[0] // 2 - 200,
            100,
            "宇宙之影",
            Colors.HIGHLIGHT,
            "title"
        )

        subtitle = TextDisplay(
            self.screen_size[0] // 2 - 150,
            160,
            "Shadow of the Universe",
            Colors.TEXT,
            "medium"
        )

        # 创建按钮
        button_width = 200
        button_height = 50
        center_x = self.screen_size[0] // 2 - button_width // 2

        self.start_button = Button(
            center_x,
            300,
            button_width,
            button_height,
            "开始游戏",
            self.on_start_click
        )

        self.quit_button = Button(
            center_x,
            400,
            button_width,
            button_height,
            "退出游戏",
            self.on_quit_click
        )

        # 创建信息面板
        self.info_panel = Panel(
            50,
            500,
            self.screen_size[0] - 100,
            180,
            "游戏信息"
        )

        # 收集所有 UI 元素
        self.ui_elements = [title, subtitle, self.start_button, self.quit_button, self.info_panel]

        # 注册到游戏 UI 系统（game.ui.render() 会渲染 self.widgets）
        for widget in self.ui_elements:
            self.game.ui.add_widget(widget)

    def on_exit(self):
        """退出状态时调用"""
        # 注销所有 UI 元素，防止切换状态后仍然响应事件
        for widget in self.ui_elements:
            self.game.ui.remove_widget(widget)
        print(f"退出状态: {self.__class__.__name__}")

    def on_start_click(self):
        """开始游戏按钮点击"""
        print("开始游戏...")
        self.game.state_manager.change_state(GameState.STRATEGY_MAP)

    def on_quit_click(self):
        """退出游戏按钮点击"""
        print("退出游戏...")
        self.game.quit()

    def update(self, delta_time):
        """更新菜单状态"""
        pass

    def render(self, screen):
        """渲染菜单"""
        # 仅渲染背景和面板内文字（按钮等已由 game.ui.render() 渲染）
        screen.fill((30, 30, 40))
        self.render_info_text(screen)

    def render_info_text(self, screen):
        """渲染信息面板内的文字"""
        font = get_font(24)
        info_lines = [
            "物理妥协能力系统演示",
            "核心概念：超能力是物理法则对某一方向的妥协",
            "核心玩法：风险管理决策",
            "",
            "Demo版本 v0.1.0"
        ]

        y_offset = 540
        for line in info_lines:
            if line:
                text_surface = font.render(line, True, Colors.TEXT)
                text_rect = text_surface.get_rect(midleft=(70, y_offset))
                screen.blit(text_surface, text_rect)
            y_offset += 25

    def handle_event(self, event):
        """处理事件（转发给 UI 系统）"""
        for widget in self.ui_elements:
            widget.handle_event(event)
