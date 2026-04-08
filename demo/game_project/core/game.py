"""
游戏核心类
Core Game Engine
"""

import pygame
import sys
from core.state_manager import StateManager
from core.event_system import EventSystem
from ui.base import UI
from config import get_font

class Game:
    """游戏主类"""

    def __init__(self, screen_width, screen_height, window_title, fps=60):
        """初始化游戏"""
        # 屏幕设置
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.window_title = window_title
        self.fps = fps

        # 创建屏幕
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption(window_title)

        # 时钟
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False

        # 核心系统
        self.state_manager = StateManager(self)
        self.event_system = EventSystem(self)
        self.ui = UI(self.screen)

        # 游戏数据
        self.game_data = {
            "current_state": "MENU",
            "fps": 0,
            "delta_time": 0
        }

        print(f"游戏初始化完成 - {window_title}")

    def run(self):
        """运行游戏主循环"""
        while self.running:
            # 计算delta time
            delta_time = self.clock.tick(self.fps) / 1000.0
            self.game_data["delta_time"] = delta_time
            self.game_data["fps"] = self.clock.get_fps()

            # 处理事件
            self.handle_events()

            # 更新游戏状态
            if not self.paused:
                self.update(delta_time)

            # 渲染
            self.render()

            # 更新显示
            pygame.display.flip()

        print("游戏主循环结束")

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # 将事件传递给当前状态
            self.state_manager.handle_event(event)

            # 将事件传递给事件系统
            self.event_system.handle_event(event)

    def update(self, delta_time):
        """更新游戏逻辑"""
        # 更新当前状态
        self.state_manager.update(delta_time)

        # 更新事件系统
        self.event_system.update(delta_time)

    def render(self):
        """渲染游戏画面"""
        # 清空屏幕
        self.screen.fill((30, 30, 40))

        # 渲染当前状态
        self.state_manager.render(self.screen)

        # 渲染UI
        self.ui.render()

        # 显示FPS（调试模式）
        from config import DEBUG_MODE, SHOW_FPS
        if DEBUG_MODE and SHOW_FPS:
            self.show_fps()

    def show_fps(self):
        """显示FPS"""
        font = get_font(24)
        fps_text = f"FPS: {int(self.game_data['fps'])}"
        text_surface = font.render(fps_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (10, 10))

    def pause(self):
        """暂停游戏"""
        self.paused = True

    def resume(self):
        """恢复游戏"""
        self.paused = False

    def quit(self):
        """退出游戏"""
        self.running = False

    def get_screen(self):
        """获取屏幕对象"""
        return self.screen

    def get_screen_size(self):
        """获取屏幕尺寸"""
        return (self.screen_width, self.screen_height)
