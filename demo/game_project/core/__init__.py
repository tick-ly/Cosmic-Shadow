"""
Core package initialization
"""

from core.game import Game
from core.state_manager import StateManager, BaseState, GameState
from core.event_system import EventSystem, EventType, Event

__all__ = ['Game', 'StateManager', 'BaseState', 'GameState', 'EventSystem', 'EventType', 'Event']
