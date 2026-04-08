"""
宇宙之影 - 游戏主入口
Shadow of the Universe - Main Game Entry
"""

import pygame
import sys
from core.game import Game
from core.state_manager import GameState
from config import *

def main():
    """主函数"""
    # 初始化pygame
    pygame.init()

    # 创建游戏实例
    game = Game(
        screen_width=SCREEN_WIDTH,
        screen_height=SCREEN_HEIGHT,
        window_title=WINDOW_TITLE,
        fps=FPS
    )

    # 注册菜单状态
    from states.menu_state import MenuState
    from states.strategy_map_state import StrategyMapState
    game.state_manager.register_state(GameState.MENU.value, MenuState)
    game.state_manager.register_state(GameState.STRATEGY_MAP.value, StrategyMapState)

    # 初始化进入菜单状态（在所有状态注册完成之后）
    game.state_manager.change_state(GameState.MENU)

    # 运行游戏
    try:
        game.run()
    except KeyboardInterrupt:
        print("\n游戏被用户中断")
    except Exception as e:
        print(f"\n游戏运行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
