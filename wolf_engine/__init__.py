"""
wolf_engine — A reusable engine for Wolfenstein-esque first-person games.

Built on Pygame + ModernGL. Provides camera, entity management, collision,
raycasting, pathfinding, rendering pipeline, and a tile-based world system.
Game-specific logic (combat, AI, items) lives outside the engine.
"""
from wolf_engine.entity import Entity
from wolf_engine.world import World
from wolf_engine.collision import CollisionResolver
from wolf_engine.raycasting import RayCaster, RayResult
from wolf_engine.pathfinding import GridPathfinder
from wolf_engine.rendering.render_scene import RenderScene, RenderLayer
from wolf_engine.rendering.shader_manager import ShaderManager
