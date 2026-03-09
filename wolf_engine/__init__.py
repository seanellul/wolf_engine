"""
wolf_engine — A reusable engine for Wolfenstein-esque first-person games.

Built on Pygame + ModernGL. Provides app shell with game state stack,
camera, entity management, collision, raycasting, pathfinding, audio,
input, TMX level loading, and a rendering pipeline. Game-specific logic
(combat, AI, items) lives outside the engine.
"""
from wolf_engine.app import App, GameState
from wolf_engine.entity import Entity
from wolf_engine.world import World
from wolf_engine.collision import CollisionResolver
from wolf_engine.raycasting import RayCaster, RayResult
from wolf_engine.pathfinding import GridPathfinder
from wolf_engine.audio import AudioManager
from wolf_engine.input import InputManager
from wolf_engine.tmx_loader import TMXLoader, LevelData, ObjectData
from wolf_engine.rendering.render_scene import RenderScene, RenderLayer
from wolf_engine.rendering.shader_manager import ShaderManager
