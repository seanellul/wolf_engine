# Architecture

## Directory Structure

```
wolf_engine/                        Reusable engine (copy to start a new game)
├── __init__.py                       Public API: Entity, World, CollisionResolver, RayCaster, GridPathfinder
├── config.py                         Engine constants (resolution, FOV, GL params, input keys, timers)
├── camera.py                         Camera math (position, orientation, view/projection matrices)
├── entity.py                         Base Entity class (pos, rot, scale, model matrix, lifecycle hooks)
├── world.py                          Entity registry with spatial indexing and group management
├── collision.py                      Axis-separated AABB collision with pluggable blockers
├── raycasting.py                     DDA voxel raycaster with callback-based blocking/targets
├── pathfinding.py                    BFS grid pathfinder with dynamic blockers and cache
└── rendering/
    ├── __init__.py
    ├── shader_program.py             GLSL shader loader and uniform management
    ├── texture_manager.py            Texture array GPU upload
    ├── texture_builder.py            Texture atlas builder from numbered PNGs
    ├── meshes/
    │   ├── base_mesh.py              Abstract VAO/VBO base
    │   ├── quad_mesh.py              Billboard quad geometry
    │   ├── instanced_quad_mesh.py    Instanced rendering (persistent VBOs)
    │   ├── level_mesh.py             Level geometry VAO
    │   ├── level_mesh_builder.py     Level geometry generator with AO
    │   └── weapon_mesh.py            First-person weapon quad
    └── shaders/
        ├── level.vert / .frag              Level geometry (AO, face shading, fog)
        ├── instanced_billboard.vert / .frag  Camera-facing sprites (NPCs, items)
        ├── instanced_door.vert / .frag       Door rendering with rotation
        ├── instanced_hud.vert / .frag        Screen-space HUD elements
        └── weapon.vert / .frag               First-person weapon overlay

game/                               Game-specific code (swap this for a different game)
├── __init__.py
├── engine.py                         Game orchestrator (system init, level lifecycle, NPC management)
├── player.py                         Player controller (combat, inventory, interaction)
├── scene.py                          Render order manager
├── level_map.py                      TMX level loader and entity spawning
├── ray_casting.py                    Game-specific raycasting rules (what blocks, what's a target)
├── path_finding.py                   Game-specific pathfinding rules (walkability, NPC avoidance)
├── sound.py                          Audio catalogue and channel management
├── data.py                           Game definitions (weapons, NPCs, items, HUD layout)
├── texture_id.py                     Texture ID registry (IntEnum mapping names to atlas indices)
└── entities/
    ├── game_object.py                Game entity base (adds engine/app refs to Entity)
    ├── npc.py                        Enemy AI (patrol, pursue, attack, death, drops)
    ├── door.py                       Door mechanics (open/close animation, key locks)
    ├── item.py                       Pickupable items (health, ammo, weapons, keys)
    ├── weapon.py                     First-person weapon (animation state machine)
    └── hud.py                        HUD rendering (health, ammo, FPS digits)

main.py                             Entry point (GL context, game loop, event dispatch)
settings.py                         Re-export shim (backward compat for `from settings import *`)
assets/                             Game assets (textures, sounds, music)
resources/                          Level data (Tiled .tmx files)
```

## The Engine/Game Boundary

The split follows one rule: **if it defines behavior, it's game code. If it provides capability, it's engine code.**

### What the engine provides

| Module | Capability |
|--------|-----------|
| `camera.py` | First-person camera with position, orientation, and projection matrices |
| `entity.py` | Base object with position, rotation, scale, model matrix, and lifecycle hooks |
| `world.py` | Entity storage with named groups, spatial indexing by tile, and deferred destruction |
| `collision.py` | Movement resolution against arbitrary blocking rules (plug in your own blockers) |
| `raycasting.py` | Line-of-sight and hit detection (plug in your own blocking and target rules) |
| `pathfinding.py` | Grid navigation (plug in your own walkability rules and dynamic obstacles) |
| `rendering/` | OpenGL 3.3 pipeline: texture arrays, instanced billboards, level mesh with AO, shaders |

### What the game defines

| Module | Behavior |
|--------|----------|
| `data.py` | Weapon stats, NPC stats, item values, HUD layout |
| `texture_id.py` | Which texture index means what (wall, enemy frame, item sprite) |
| `player.py` | What happens when you shoot, pick up items, open doors, die |
| `entities/npc.py` | How enemies spot you, chase you, attack, die, drop loot |
| `entities/door.py` | How doors animate, which ones need keys |
| `ray_casting.py` | "Walls and closed doors block rays. NPCs are targets." |
| `path_finding.py` | "Walls aren't walkable. Avoid other NPCs." |
| `sound.py` | Which sounds play for which events |

### How to make a different game

1. Copy `wolf_engine/` as-is
2. Replace `game/` with your own:
   - Write your own `data.py` with your entity stats
   - Write your own `texture_id.py` mapping your texture atlas
   - Write your own entity classes inheriting from `wolf_engine.Entity`
   - Write your own `ray_casting.py` / `path_finding.py` wrappers with your game's rules
   - Write your own `player.py` with your game's controls and mechanics
3. Replace `assets/` and `resources/` with your own art and levels
4. Update `main.py` and `settings.py` if needed

## Key Design Patterns

### Callback-based systems

The engine never hardcodes game rules. Instead, game code passes callbacks:

```python
# Collision: game defines what blocks movement
collision = CollisionResolver(radius=0.15)
collision.add_blocker(lambda pos: pos in wall_map)
collision.add_blocker(lambda pos: pos in door_map and door_map[pos].is_closed)

# Raycasting: game defines what blocks rays and what counts as a target
result = RayCaster.cast(start, direction,
    is_blocked=lambda pos: pos in wall_map,
    targets={player.tile_pos})

# Pathfinding: game defines walkability
pathfinder = GridPathfinder(width, depth,
    is_walkable=lambda x, z: (x, z) not in wall_map)
```

### Entity lifecycle

```python
entity = MyNPC(tex_id=45, x=5, z=3)  # inherits wolf_engine.Entity
world.spawn(entity, group='npcs')      # registers + calls on_spawn()
# ... game loop ...
world.destroy(entity, group='npcs')    # marks for removal
world.flush()                          # actually removes + calls on_destroy()
```

### Settings shim

During the transition, `from settings import *` still works everywhere. It re-exports
both `wolf_engine.config` (engine constants) and `game.data` (game definitions).
This will be removed once all files use direct imports.
