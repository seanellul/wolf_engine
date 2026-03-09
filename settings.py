"""
Settings shim — re-exports everything from engine_config and game_data
so existing `from settings import *` imports continue to work.

Engine constants live in engine_config.py (resolution, FOV, GL params, etc.)
Game-specific data lives in game_data.py (weapons, NPCs, items, HUD, etc.)
"""
from engine_config import *  # noqa: F401,F403
from game_data import *      # noqa: F401,F403
