"""
UI基础系统
UI Base System
"""

import pygame
from config import Colors, get_font


class UI:
    """UI管理器"""

    def __init__(self, screen):
        """初始化UI管理器"""
        self.screen = screen
        self.widgets = []
        self.fonts = {
            "small": get_font(20),
            "medium": get_font(28),
            "large": get_font(36),
            "title": get_font(48)
        }

    def render(self):
        """渲染所有UI组件"""
        for widget in self.widgets:
            widget.render(self.screen)
            # 递归渲染子组件（Panel 的 children）
            if hasattr(widget, 'children'):
                for child in widget.children:
                    child.render(self.screen)

    def add_widget(self, widget):
        """添加UI组件"""
        self.widgets.append(widget)

    def remove_widget(self, widget):
        """移除UI组件"""
        if widget in self.widgets:
            self.widgets.remove(widget)

    def clear(self):
        """清空所有UI组件"""
        self.widgets.clear()

    def get_font(self, size="medium"):
        """获取字体"""
        return self.fonts.get(size, self.fonts["medium"])


class Widget:
    """UI组件基类"""

    def __init__(self, x, y, width, height):
        """初始化组件"""
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
        self.enabled = True
        self.hovered = False

    def render(self, screen):
        """渲染组件"""
        pass

    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)


class Button(Widget):
    """按钮组件"""

    def __init__(self, x, y, width, height, text, callback, color=Colors.PANEL):
        """初始化按钮"""
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = tuple(min(c + 30, 255) for c in color)
        self.text_color = Colors.TEXT
        self.font = get_font(24)

    def render(self, screen):
        """渲染按钮"""
        if not self.visible:
            return

        # 绘制按钮背景
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, Colors.BORDER, self.rect, 2, border_radius=5)

        # 绘制文字
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        """处理事件"""
        super().handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.enabled:
                if self.callback:
                    self.callback()


class Panel(Widget):
    """面板组件"""

    def __init__(self, x, y, width, height, title=""):
        """初始化面板"""
        super().__init__(x, y, width, height)
        self.title = title
        self.background_color = Colors.PANEL
        self.border_color = Colors.BORDER
        self.children = []
        self.title_font = get_font(22)

    def render(self, screen):
        """渲染面板"""
        if not self.visible:
            return

        # 绘制面板背景
        pygame.draw.rect(screen, self.background_color, self.rect, border_radius=5)
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=5)

        # 绘制标题
        if self.title:
            title_surface = self.title_font.render(self.title, True, Colors.TEXT)
            title_rect = title_surface.get_rect(midtop=(self.rect.centerx, self.rect.top + 10))
            screen.blit(title_surface, title_rect)

        # 渲染子组件
        for child in self.children:
            child.render(screen)

    def add_child(self, widget):
        """添加子组件"""
        self.children.append(widget)

    def handle_event(self, event):
        """处理事件"""
        super().handle_event(event)
        for child in self.children:
            child.handle_event(event)


class ProgressBar(Widget):
    """进度条组件"""

    def __init__(self, x, y, width, height, value=0, max_value=100, color=Colors.HIGHLIGHT):
        """初始化进度条"""
        super().__init__(x, y, width, height)
        self.value = value
        self.max_value = max_value
        self.color = color
        self.background_color = (40, 40, 50)
        self.border_color = Colors.BORDER

    def render(self, screen):
        """渲染进度条"""
        if not self.visible:
            return

        # 绘制背景
        pygame.draw.rect(screen, self.background_color, self.rect, border_radius=3)
        pygame.draw.rect(screen, self.border_color, self.rect, 1, border_radius=3)

        # 计算进度
        progress = min(self.value / self.max_value, 1.0)
        fill_rect = pygame.Rect(
            self.rect.x + 2,
            self.rect.y + 2,
            (self.rect.width - 4) * progress,
            self.rect.height - 4
        )

        # 绘制进度
        if progress > 0:
            pygame.draw.rect(screen, self.color, fill_rect, border_radius=2)

    def set_value(self, value):
        """设置进度值"""
        self.value = max(0, min(value, self.max_value))

    def get_color_by_value(self):
        """根据数值返回颜色"""
        ratio = self.value / self.max_value
        if ratio < 0.5:
            return Colors.RISK_LOW
        elif ratio < 0.8:
            return Colors.RISK_MEDIUM
        else:
            return Colors.RISK_CRITICAL


class TextDisplay(Widget):
    """文本显示组件"""

    def __init__(self, x, y, text, color=Colors.TEXT, size="medium"):
        """初始化文本显示"""
        super().__init__(x, y, 0, 0)
        self.text = text
        self.color = color
        self.size = size
        self.font = None
        self.update_surface()

    def update_surface(self):
        """更新文本表面"""
        if isinstance(self.size, str):
            size_map = {"small": 20, "medium": 28, "large": 36, "title": 48}
            s = size_map.get(self.size, 28)
        else:
            s = self.size
        self.font = get_font(s)
        self.surface = self.font.render(self.text, True, self.color)
        self.rect = self.surface.get_rect(topleft=(self.rect.x, self.rect.y))

    def render(self, screen):
        """渲染文本"""
        if self.visible and self.surface:
            screen.blit(self.surface, self.rect)

    def set_text(self, text):
        """设置文本"""
        self.text = text
        self.update_surface()
