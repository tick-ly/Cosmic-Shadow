"""
事件系统
Event System
"""

from enum import Enum
import pygame

class EventType(Enum):
    """事件类型枚举"""
    # 游戏事件
    GAME_START = "game_start"
    GAME_PAUSE = "game_pause"
    GAME_RESUME = "game_resume"
    GAME_OVER = "game_over"

    # 战斗事件
    BATTLE_START = "battle_start"
    BATTLE_END = "battle_end"
    TURN_START = "turn_start"
    TURN_END = "turn_end"

    # 技能事件
    SKILL_USE = "skill_use"
    SKILL_SUCCESS = "skill_success"
    SKILL_FAILURE = "skill_failure"
    SKILL_BACKLASH = "skill_backlash"

    # 单位事件
    UNIT_DAMAGED = "unit_damaged"
    UNIT_HEALED = "unit_healed"
    UNIT_DIED = "unit_died"
    UNIT_DEBT_WARNING = "unit_debt_warning"

    # UI事件
    BUTTON_CLICKED = "button_clicked"
    PANEL_CLOSED = "panel_closed"

class Event:
    """事件类"""

    def __init__(self, event_type, data=None):
        """初始化事件"""
        self.type = event_type
        self.data = data or {}
        self.handled = False
        self.timestamp = pygame.time.get_ticks()

    def __repr__(self):
        return f"Event({self.type}, {self.data})"

class EventListener:
    """事件监听器"""

    def __init__(self, event_type, callback, priority=0):
        """初始化监听器"""
        self.event_type = event_type
        self.callback = callback
        self.priority = priority  # 优先级，数值越大优先级越高

    def __lt__(self, other):
        """用于排序"""
        return self.priority < other.priority

class EventSystem:
    """事件系统"""

    def __init__(self, game):
        """初始化事件系统"""
        self.game = game
        self.listeners = {}
        self.event_queue = []
        self.event_log = []
        self.max_log_size = 100

    def subscribe(self, event_type, callback, priority=0):
        """订阅事件"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []

        listener = EventListener(event_type, callback, priority)
        self.listeners[event_type].append(listener)
        self.listeners[event_type].sort(reverse=True)

        print(f"事件订阅: {event_type} -> {callback.__name__}")

    def unsubscribe(self, event_type, callback):
        """取消订阅"""
        if event_type in self.listeners:
            self.listeners[event_type] = [
                listener for listener in self.listeners[event_type]
                if listener.callback != callback
            ]

    def emit(self, event_type, data=None):
        """触发事件"""
        event = Event(event_type, data)
        self.event_queue.append(event)

        # 记录事件
        self.event_log.append(event)
        if len(self.event_log) > self.max_log_size:
            self.event_log.pop(0)

    def update(self, delta_time):
        """更新事件系统"""
        # 处理队列中的事件
        while self.event_queue:
            event = self.event_queue.pop(0)
            self.process_event(event)

    def process_event(self, event):
        """处理事件"""
        if event.type in self.listeners:
            for listener in self.listeners[event.type]:
                try:
                    listener.callback(event)
                except Exception as e:
                    print(f"事件处理错误: {e}")

        event.handled = True

    def handle_event(self, pygame_event):
        """处理pygame事件"""
        # 这里可以添加对特定pygame事件的监听
        pass

    def get_recent_events(self, event_type=None, count=10):
        """获取最近的事件"""
        if event_type:
            events = [e for e in self.event_log if e.type == event_type]
        else:
            events = self.event_log

        return events[-count:]

    def clear_log(self):
        """清空事件日志"""
        self.event_log.clear()
