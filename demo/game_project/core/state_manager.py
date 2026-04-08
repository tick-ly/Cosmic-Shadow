"""
状态管理系统
State Management System
"""

from enum import Enum

class GameState(Enum):
    """游戏状态枚举"""
    MENU = "menu"
    STRATEGY_MAP = "strategy_map"
    BATTLE = "battle"
    CAMPAIGN_RESULT = "campaign_result"
    GAME_OVER = "game_over"

class StateManager:
    """状态管理器"""

    def __init__(self, game):
        """初始化状态管理器"""
        self.game = game
        self.current_state = None
        self.states = {}
        self.state_history = []
        self._initialized = False

    def register_state(self, state_name, state_class):
        """注册状态"""
        if state_name not in self.states:
            self.states[state_name] = state_class
            print(f"状态已注册: {state_name}")

    def change_state(self, new_state, **kwargs):
        """切换状态"""
        # 保存当前状态到历史
        if self.current_state:
            self.state_history.append(self.current_state)
            self.current_state.on_exit()

        # 创建新状态
        if isinstance(new_state, GameState):
            state_name = new_state.value
        else:
            state_name = new_state

        if state_name in self.states:
            self.current_state = self.states[state_name](self.game, **kwargs)
            self.current_state.on_enter(**kwargs)
            print(f"状态切换: {state_name}")
        else:
            print(f"状态不存在: {state_name}")
            print(f"可用状态: {list(self.states.keys())}")

    def update(self, delta_time):
        """更新当前状态"""
        if self.current_state:
            self.current_state.update(delta_time)

    def render(self, screen):
        """渲染当前状态"""
        if self.current_state:
            self.current_state.render(screen)

    def handle_event(self, event):
        """处理事件"""
        if self.current_state:
            self.current_state.handle_event(event)

    def get_current_state_name(self):
        """获取当前状态名称"""
        if self.current_state:
            return self.current_state.__class__.__name__
        return None

    def push_state(self, new_state, **kwargs):
        """压入新状态（用于暂停等场景）"""
        if self.current_state:
            self.state_history.append(self.current_state)

        if isinstance(new_state, GameState):
            state_name = new_state.value
        else:
            state_name = new_state

        if state_name in self.states:
            self.current_state = self.states[state_name](self.game, **kwargs)
            self.current_state.on_enter(**kwargs)

    def pop_state(self):
        """弹出状态"""
        if self.state_history:
            if self.current_state:
                self.current_state.on_exit()

            self.current_state = self.state_history.pop()
            if self.current_state:
                self.current_state.on_resume()
        else:
            print("状态历史为空，无法弹出")

class BaseState:
    """状态基类"""

    def __init__(self, game, **kwargs):
        """初始化状态"""
        self.game = game
        self.screen = game.get_screen()
        self.screen_size = game.get_screen_size()
        self.initialized = False

    def on_enter(self, **kwargs):
        """进入状态时调用"""
        if not self.initialized:
            self.initialize(**kwargs)
            self.initialized = True
        print(f"进入状态: {self.__class__.__name__}")

    def on_exit(self):
        """退出状态时调用"""
        print(f"退出状态: {self.__class__.__name__}")

    def on_resume(self):
        """从其他状态返回时调用"""
        print(f"恢复状态: {self.__class__.__name__}")

    def initialize(self, **kwargs):
        """初始化状态（子类重写）"""
        pass

    def update(self, delta_time):
        """更新状态（子类重写）"""
        pass

    def render(self, screen):
        """渲染状态（子类重写）"""
        pass

    def handle_event(self, event):
        """处理事件（子类重写）"""
        pass
