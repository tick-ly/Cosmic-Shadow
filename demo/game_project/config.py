"""
游戏配置文件
Game Configuration
"""

# 屏幕设置
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
WINDOW_TITLE = "宇宙之影 - Shadow of the Universe"
FPS = 60

# 颜色定义
class Colors:
    """颜色常量"""
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)

    # 风险等级颜色
    RISK_LOW = (76, 175, 80)       # 绿色
    RISK_MEDIUM = (255, 193, 7)    # 黄色
    RISK_HIGH = (255, 152, 0)      # 橙色
    RISK_CRITICAL = (244, 67, 54)  # 红色

    # UI颜色
    BACKGROUND = (30, 30, 40)
    PANEL = (50, 50, 70)
    BORDER = (100, 100, 120)
    TEXT = (220, 220, 220)
    HIGHLIGHT = (100, 150, 255)

# 战斗设置
BATTLE_TURN_TIME = 30  # 每回合秒数
MAX_REALITY_DEBT = 1000  # 最大现实债务
DEBT_WARNING_THRESHOLD = 500  # 债务警告阈值
DEBT_CRITICAL_THRESHOLD = 800  # 债务危险阈值

# 血统等级
BLOODLINE_TIERS = {
    "LOW": (0, 999),
    "MEDIUM": (1000, 9999),
    "HIGH": (10000, 99999)
}

# 能力设置
SKILL_BASE_SUCCESS_RATE = {
    "LOW": 90,
    "MEDIUM": 70,
    "HIGH": 50
}

# 现实债务设置
REALITY_DEBT_COST = {
    "LOW": (5, 15),
    "MEDIUM": (20, 50),
    "HIGH": (100, 300)
}

# 调试模式
DEBUG_MODE = True
SHOW_FPS = True
LOG_COMBAT = True

# 字体配置（优先使用支持中文的系统字体）
import pygame as _pg
_pg.init()
_CJK_FONTS = [
    "microsoftyaheiui",
    "microsoftyahei",
    "simsun",
    "mingliu",
]
FONT_NAME = None
for _f in _CJK_FONTS:
    if _f in _pg.font.get_fonts():
        FONT_NAME = _f
        break
del _CJK_FONTS, _f


def get_font(size: int):
    """获取支持中文的字体"""
    if FONT_NAME:
        return _pg.font.SysFont(FONT_NAME, size)
    return _pg.font.Font(None, size)
