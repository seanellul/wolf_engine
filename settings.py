"""
Settings shim — re-exports everything from wolf_engine.config and game.data
so existing `from settings import *` imports continue to work.

Engine constants live in wolf_engine/config.py
Game-specific data lives in game/data.py
"""
from wolf_engine.config import *  # noqa: F401,F403
from game.data import *           # noqa: F401,F403
