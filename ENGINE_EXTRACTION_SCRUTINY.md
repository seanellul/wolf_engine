# Engine Extraction Scrutiny Document

## Vision

Extract the reusable rendering, input, audio, and game loop infrastructure from this Wolfenstein 3D clone into a **standalone engine template** for building Wolfenstein-esque first-person games. The goal: swap out assets, game data, and entity logic to produce different games on the same proven architecture — fast.

---

## Current Architecture Summary

| Layer | Files | Lines | Verdict |
|-------|-------|-------|---------|
| App Shell / Loop | `main.py` | ~90 | Mixed engine + game. Needs split. |
| Engine Orchestrator | `engine.py` | ~60 | Mostly game-specific. Needs rewrite. |
| Settings | `settings.py` | ~270 | Flat constants. Needs split into engine config + game data files. |
| Camera | `camera.py` | ~60 | **Clean. Reusable as-is.** |
| Player | `player.py` | ~230 | God object. Combat/pickup/door logic must be extracted. |
| Rendering | `scene.py`, `shader_program.py`, `meshes/*`, `shaders/*` | ~500 | Good bones. Needs render queue, VAO fix. |
| Textures | `textures.py`, `texture_builder.py`, `texture_id.py` | ~130 | Reusable pipeline. ID enum is game-specific. |
| Level Loading | `level_map.py` | ~90 | TMX parsing reusable. Entity spawning is game-specific. |
| Raycasting | `ray_casting.py` | ~60 | **Reusable as-is.** DDA algorithm is generic. |
| Pathfinding | `path_finding.py` | ~50 | BFS is reusable. Direct `npc_map` access needs abstraction. |
| Audio | `sound.py` | ~70 | Entirely game-specific catalogue. Pattern is reusable. |
| Entities | `game_objects/*` | ~400 | All game-specific. Base class pattern is reusable. |

**Total: ~1,950 lines.** Roughly 40% is reusable engine code, 60% is game-specific.

---

## System-by-System Scrutiny

### 1. Game Loop (`main.py`)

**Current state:** `Game` class owns OpenGL context creation, the main loop, timer events, and `Engine` instantiation. Mouse capture is hardcoded. Delta time is computed *after* the update step (off by one frame).

**What to keep:**
- OpenGL context setup pattern (version, depth, blend, auto GC)
- The update → render loop structure
- Timer-based animation/sound pulse system (`anim_trigger`, `sound_trigger`)

**What to fix:**
- Move `delta_time = clock.tick()` to the *start* of the frame, before `update()`
- Extract mouse capture into an input manager (games may want cursor for menus)
- Add a **game state stack** (menu → playing → paused → game-over) so the loop dispatches to the active state
- Make window resolution configurable at runtime, not just a constant

**Proposed engine API:**
```python
class App:
    def __init__(self, config: EngineConfig):
        # GL context, window, clock, input manager
    def push_state(self, state: GameState): ...
    def pop_state(self): ...
    def run(self): ...  # loop dispatches to active state
```

---

### 2. Engine Orchestrator (`engine.py`)

**Current state:** `Engine` owns all subsystems and has a `new_game()` that hard-resets everything. `update_npc_map()` contains NPC lifecycle logic (removing dead NPCs, rebuilding spatial map). Music playback starts in `new_game()`.

**Problems:**
- `new_game()` is both "load level" and "restart game" with no distinction
- NPC map cleanup is engine-level code doing game-specific work
- No concept of loading/unloading — just full reconstruction
- `PlayerAttribs` is the only persistence mechanism and it's ad-hoc

**What to extract into engine:**
- System initialization ordering (textures → shaders → level → entities → scene)
- The update dispatch pattern (player → shaders → scene)
- Level transition lifecycle (unload old → load new → init entities)

**What belongs in game code:**
- `update_npc_map()` — this is entity lifecycle management, belongs in a game-specific world manager
- Music playback decisions
- `PlayerAttribs` persistence logic

**Proposed engine API:**
```python
class Engine:
    def __init__(self, app: App):
        self.textures = TextureManager(app)
        self.shaders = ShaderManager(app)
        self.audio = AudioManager()
        self.input = InputManager()
        self.world = None  # set by game state

    def load_level(self, tmx_path: str) -> World:
        # Returns a World with parsed geometry + spawn points
        # Game code registers its own entities

    def unload_level(self): ...
```

---

### 3. Settings (`settings.py`)

**Current state:** Single flat module with `from settings import *` used everywhere. Mixes engine constants (resolution, FOV, near/far planes) with game data (weapon stats, NPC stats, item definitions). Dynamically mutates an `IntEnum` at module load time.

**This is the highest-leverage refactor.** Splitting settings enables the entire "swap game data to make a new game" workflow.

**Split into:**

| File | Contents | Format |
|------|----------|--------|
| `engine/config.py` | `WIN_RES`, `FOV`, `NEAR`, `FAR`, `MOUSE_SENSITIVITY`, `DEPTH_SIZE`, `GL_VERSION`, `SYNC_PULSE` | Python dataclass or dict loaded from TOML/JSON |
| `game/data/player.toml` | `speed`, `size`, `height`, `init_health`, `init_ammo`, `start_pos` | Data file |
| `game/data/weapons.toml` | Per-weapon: `damage`, `range`, `accuracy`, `ammo_cost`, `anim_frames`, `sound` | Data file |
| `game/data/npcs.toml` | Per-NPC-type: `health`, `damage`, `speed`, `accuracy`, `size`, `anim_frames`, `sounds`, `drops` | Data file |
| `game/data/items.toml` | Per-item: `type` (health/ammo/weapon/key), `value`, `sound` | Data file |
| `game/data/hud.toml` | HUD element positions, scales, texture IDs | Data file |

**The `IntEnum` mutation hack** (`ID.HEALTH_DIGIT_0 = 0 + NUM_TEXTURES`) should be replaced with a proper texture registry that games populate from their asset manifests.

---

### 4. Rendering Pipeline (`scene.py`, `meshes/*`, `shaders/*`)

**Current state:** `Scene` hardcodes render order: level → doors → items → HUD → NPCs → weapon. Each instanced mesh type rebuilds its VAO every frame. Shaders have duplicated fog/gamma code.

**Critical bug: VAO rebuild per frame.** `InstancedQuadMesh.render()` calls `get_vao()` which creates new GPU buffers and a new VAO every single frame. This is the single biggest performance issue. Fix:
- Allocate VBOs once at creation
- Use `vbo.write(data)` to update instance data each frame
- Only recreate VAO when instance count changes

**Rendering improvements for engine:**
1. **Render queue with layers.** Replace hardcoded render order with named layers (`LEVEL`, `WORLD_SPRITES`, `HUD`, `WEAPON`) that games can populate.
2. **Shared shader includes.** Extract fog, gamma correction, and billboard math into includable snippets (or use string concatenation since GLSL has no `#include`).
3. **Depth sorting for transparent sprites.** NPCs and items are alpha-tested billboards. When they overlap, the render order matters. Sort back-to-front within the sprite layer.
4. **Frustum culling.** Currently all entities render regardless of visibility. For larger levels, cull objects outside the view frustum before building instance buffers.

**What's already good:**
- Instanced rendering pattern (just fix the buffer management)
- Texture array approach (single bind, layer index per object)
- The billboard shader math (cylindrical billboarding via model-view matrix manipulation)
- Level mesh builder with AO (ambient occlusion adds visual quality cheaply)
- Per-face shading in the level shader

---

### 5. Entity System (`game_objects/*`)

**Current state:** `GameObject` base class provides position/rotation/scale and a model matrix. `NPC`, `Door`, `Item` inherit from it. `Weapon` and `HUD` use `GameObject.get_model_matrix` as an unbound function (not inheriting). No enforced interface — no base `update()` or `render()`.

**For the engine, provide:**
```python
class Entity:
    """Base for all world-space objects."""
    pos: glm.vec3
    rot: float  # Y-axis rotation
    scale: glm.vec3
    tex_id: int
    m_model: glm.mat4
    active: bool = True

    def update(self, dt: float): ...  # override in game code
    def on_spawn(self): ...
    def on_destroy(self): ...
    def get_model_matrix(self) -> glm.mat4: ...
```

**Entity management:**
```python
class World:
    """Manages all entities and spatial queries."""
    entities: dict[str, list[Entity]]  # keyed by type/group
    spatial_map: dict[tuple[int,int], list[Entity]]

    def spawn(self, entity: Entity, group: str): ...
    def destroy(self, entity: Entity): ...
    def get_at(self, tile_pos: tuple) -> list[Entity]: ...
    def get_in_radius(self, pos, radius) -> list[Entity]: ...
    def update_all(self, dt: float): ...
```

This replaces the current scattered `npc_map`, `item_map`, `door_map` dictionaries with a unified spatial index. Games register their entity types and the engine handles lifecycle.

---

### 6. Player / Camera (`camera.py`, `player.py`)

**Current state:** `Player` inherits from `Camera`. `Camera` is clean math (position, orientation, matrices). `Player` adds combat, inventory, collision, item pickup, door interaction, weapon switching, health checks, and level transitions — all in one 230-line class.

**Camera: keep as-is.** It's the cleanest module in the codebase.

**Player: split into layers:**

| Layer | Responsibility | Lives in |
|-------|---------------|----------|
| `Camera` | Position, orientation, view/projection matrices | Engine |
| `PlayerController` | Movement, collision resolution, mouse look | Engine |
| `PlayerCombat` | Health, damage, weapons, shooting | Game code |
| `PlayerInteraction` | Door interaction, item pickup, inventory | Game code |

The engine provides `Camera` + `PlayerController` (movement with collision against a spatial map). Games compose their player from these plus their own combat/interaction systems.

**Collision system to extract:** The axis-separated AABB collision resolution (`is_collide(dx, dz)` → try x, try z independently) is a clean reusable pattern. Generalize it:
```python
class CollisionResolver:
    def __init__(self, blocked_check: Callable[[int, int], bool], radius: float):
        ...
    def resolve_movement(self, pos: vec3, dx: float, dz: float) -> vec3:
        # Returns new position after collision resolution
```

---

### 7. Level Loading (`level_map.py`)

**Current state:** Parses TMX with pytmx. Builds `wall_map`, `floor_map`, `ceil_map` as `dict[(int,int) -> int]`. Spawns game entities (Door, Item, NPC, Player) directly from object layers.

**Split into:**

| Component | Engine or Game | What it does |
|-----------|---------------|--------------|
| `TMXLoader` | Engine | Parses TMX, returns raw tile grids + object positions |
| `LevelGeometry` | Engine | Holds wall/floor/ceil maps, generates level mesh |
| `EntitySpawner` | Game | Takes object positions, creates game-specific entities |

**The engine's `TMXLoader` returns:**
```python
@dataclass
class LevelData:
    tile_maps: dict[str, dict[tuple[int,int], int]]  # layer_name -> tile grid
    objects: dict[str, list[ObjectData]]  # layer_name -> list of objects
    player_spawn: vec3
    map_size: tuple[int, int]

@dataclass
class ObjectData:
    pos: tuple[int, int]
    tex_id: int
    properties: dict  # custom Tiled properties
```

Games provide a spawner callback:
```python
def spawn_entities(level_data: LevelData, world: World):
    for obj in level_data.objects['npc']:
        world.spawn(MyNPC(obj.pos, NPC_STATS[obj.tex_id]), group='npcs')
    for obj in level_data.objects['doors']:
        world.spawn(MyDoor(obj.pos, obj.tex_id), group='doors')
```

---

### 8. Raycasting (`ray_casting.py`)

**Current state:** 3D DDA voxel traversal. Dual-purpose: NPC line-of-sight and player shooting. Checks against `wall_map` and `door_map` for obstruction.

**Reusable as-is with minor abstraction.** The DDA algorithm just needs a generic "is blocked" callback instead of direct map references:

```python
class RayCaster:
    def cast(self, start: vec3, end: vec3, is_blocked: Callable[[int,int], bool],
             targets: set[tuple[int,int]] = None, max_dist: float = 20) -> RayResult:
        ...

@dataclass
class RayResult:
    hit: bool
    hit_pos: tuple[int, int] | None
    distance: float
```

---

### 9. Pathfinding (`path_finding.py`)

**Current state:** BFS on a grid graph. Nodes are all non-wall tiles minus NPC-occupied tiles. `@lru_cache` on `bfs()` (unbounded cache, never cleared).

**Issues:**
- Cache never invalidates — if doors open/close or NPCs move, cached paths may be stale
- Reads `npc_map` directly for obstacle avoidance
- BFS is unweighted — no cost differentiation (e.g., prefer open areas)

**For the engine:**
```python
class GridPathfinder:
    def __init__(self, walkable: Callable[[int,int], bool]):
        ...
    def find_path(self, start: tuple, goal: tuple,
                  dynamic_blocked: set[tuple] = None) -> list[tuple]:
        ...
    def invalidate_cache(self): ...
```

Consider A* as an option for larger maps where BFS is too expensive. For the current 16x9 maps, BFS is fine.

---

### 10. Audio (`sound.py`)

**Current state:** All sounds hardcoded by name. Round-robin channel assignment. No spatial audio, no priority, no distance-based volume.

**Engine audio manager:**
```python
class AudioManager:
    def __init__(self, num_channels: int = 10):
        ...
    def load_bank(self, manifest: dict[str, str]):
        # manifest maps sound_name -> file_path
    def play(self, name: str, volume: float = 1.0, priority: int = 0): ...
    def play_positional(self, name: str, source_pos: vec3, listener_pos: vec3,
                        falloff: float = 1.0): ...
    def play_music(self, path: str, loop: bool = True): ...
    def stop_music(self): ...
```

Games provide a sound manifest (loaded from data file) instead of hardcoding paths.

---

### 11. Texture System (`textures.py`, `texture_builder.py`, `texture_id.py`)

**Current state:** `TextureArrayBuilder` globs PNGs sorted by filename integer, builds a vertical strip atlas. `Textures` uploads it as a `texture_array`. `texture_id.py` is a game-specific `IntEnum`.

**What to generalize:**
- Builder should accept a manifest (list of paths + IDs) rather than globbing and sorting by filename
- Builder should cache and only rebuild when source files change (compare mtimes)
- The ID enum should be generated from the manifest, not maintained by hand
- Support multiple texture arrays (e.g., separate arrays for level textures vs sprite textures)

**Engine texture API:**
```python
class TextureManager:
    def load_array(self, name: str, manifest: list[str], tile_size: int) -> int:
        # Returns texture unit index
    def get_id(self, name: str, texture_name: str) -> int:
        # Returns layer index within the array
    def bind(self, name: str, unit: int): ...
```

---

## Proposed Engine Directory Structure

```
wolf_engine/
├── __init__.py
├── app.py                  # App shell, GL context, main loop, game state stack
├── config.py               # EngineConfig dataclass, loads from TOML/JSON
├── camera.py               # Camera (as-is, it's clean)
├── input.py                # InputManager, action mapping, key rebinding
├── collision.py            # CollisionResolver (axis-separated AABB)
├── raycasting.py           # RayCaster (DDA with callback)
├── pathfinding.py          # GridPathfinder (BFS/A* with cache invalidation)
├── world.py                # World (entity registry, spatial map, lifecycle)
├── entity.py               # Entity base class
├── audio.py                # AudioManager (manifest-driven, positional)
├── rendering/
│   ├── __init__.py
│   ├── scene.py            # RenderScene with named layers
│   ├── shader_manager.py   # Shader loading, uniform management
│   ├── texture_manager.py  # Texture array loading, manifest-driven
│   ├── texture_builder.py  # Atlas builder (cached)
│   ├── meshes/
│   │   ├── base_mesh.py
│   │   ├── quad_mesh.py
│   │   ├── instanced_mesh.py  # Fixed: persistent VBOs, write() per frame
│   │   ├── level_mesh.py
│   │   └── level_mesh_builder.py
│   └── shaders/
│       ├── level.vert / .frag
│       ├── billboard.vert / .frag
│       ├── door.vert / .frag
│       ├── hud.vert / .frag
│       └── weapon.vert / .frag
├── level/
│   ├── tmx_loader.py       # TMX parsing → LevelData
│   └── level_geometry.py   # Wall/floor/ceil maps, mesh generation
└── utils/
    ├── math.py              # Shared GLM helpers
    └── timer.py             # Pulse timer system (anim_trigger, etc.)

# Game code lives OUTSIDE the engine:
my_game/
├── main.py                 # App + EngineConfig, push initial state
├── states/
│   ├── playing.py          # GameState: playing
│   ├── menu.py             # GameState: main menu
│   └── game_over.py        # GameState: death/victory
├── entities/
│   ├── player.py           # PlayerCombat, PlayerInteraction
│   ├── npc.py              # Game-specific NPC AI
│   ├── door.py             # Door behavior
│   ├── item.py             # Pickupable items
│   ├── weapon.py           # Weapon state machine
│   └── hud.py              # HUD layout
├── data/
│   ├── game.toml           # Player stats, game rules
│   ├── weapons.toml        # Weapon definitions
│   ├── npcs.toml           # NPC type definitions
│   ├── items.toml          # Item definitions
│   ├── sounds.toml         # Sound manifest
│   └── textures.toml       # Texture manifest + IDs
├── assets/
│   ├── textures/
│   ├── sounds/
│   └── music/
└── resources/
    └── levels/             # TMX files
```

---

## Priority-Ordered Extraction Plan

### Phase 1: Fix Critical Bugs (do first, even before extraction)

1. **Fix VAO-per-frame rebuild** in `instanced_quad_mesh.py`. Allocate persistent VBOs, use `vbo.write()`. This is a real performance bug.
2. **Fix delta_time ordering** in `main.py`. Call `clock.tick()` at the start of the frame.
3. **Fix NPC list mutation during iteration** in `engine.py`. Build a removal list, then remove after iteration.

### Phase 2: Split Settings (enables everything else)

4. **Split `settings.py`** into engine config (resolution, FOV, GL params) and game data (weapon stats, NPC stats, items).
5. **Create data loading** from TOML/JSON files for game-specific settings.
6. **Replace `texture_id.py` IntEnum** with a manifest-driven texture registry.

### Phase 3: Extract Engine Core

7. **Extract `Camera`** as-is into `wolf_engine/camera.py`.
8. **Create `Entity` base class** with `update()`, `on_spawn()`, `on_destroy()` interface.
9. **Create `World`** class with unified spatial map, entity groups, and lifecycle management.
10. **Create `CollisionResolver`** from the `is_collide` pattern in `player.py` and `npc.py`.
11. **Abstract `RayCaster`** with callback-based blocking check.
12. **Abstract `GridPathfinder`** with callback-based walkability and cache invalidation.

### Phase 4: Extract Rendering

13. **Fix `InstancedQuadMesh`** with persistent buffer management.
14. **Create `RenderScene`** with named layers replacing hardcoded render order.
15. **Create `ShaderManager`** that loads shaders from a manifest instead of hardcoded names.
16. **Create `TextureManager`** with manifest-driven loading and caching.
17. **Extract shared shader code** (fog, gamma) into concatenable snippets.

### Phase 5: Extract Infrastructure

18. **Create `AudioManager`** with manifest-driven sound loading and positional audio.
19. **Create `InputManager`** with action mapping (decouple key constants from game logic).
20. **Create `App`** with game state stack (menu → playing → paused → game-over).
21. **Create `TMXLoader`** that returns raw `LevelData` without spawning entities.
22. **Add error handling** around all file I/O and GPU resource creation.

### Phase 6: First Game on Engine

23. **Rebuild the original Wolfenstein clone** on top of `wolf_engine` as the reference game.
24. **Verify feature parity** — same gameplay, same visuals, same performance (or better).
25. **Build a second game** (different theme/assets) to validate the engine is truly reusable.

---

## Known Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Over-engineering the engine before building a second game | Waste time on abstractions nobody uses | Build the minimum engine that supports the reference game, then generalize only when the second game needs it |
| ModernGL auto-GC not releasing resources on level transition | GPU memory leak across many level loads | Add explicit `release()` calls in `World.unload()` |
| `@lru_cache` on pathfinding growing unbounded | Memory leak in long sessions | Add `maxsize` parameter and call `cache_clear()` on level load |
| Tiled TMX format is limiting for non-grid levels | Can't do irregular geometry | Accept this constraint — Wolfenstein-esque games are grid-based by definition |
| Python performance ceiling for large levels | FPS drops with many NPCs or large maps | Profile before optimizing. Instanced rendering handles draw calls. Pathfinding is the likely bottleneck — cap NPC count or use spatial partitioning |

---

## What Makes This Worth Doing

The current codebase already solves the hard problems:
- **OpenGL 3.3 instanced rendering** with texture arrays — this is the right GPU architecture
- **Billboard shaders** that handle sprite-based enemies correctly
- **Level mesh generation** with AO from Tiled maps — this workflow is proven
- **DDA raycasting** for line-of-sight and shooting — clean algorithm
- **Axis-separated collision** that allows wall sliding — feels right in play

These aren't trivial to implement from scratch. The extraction preserves all of this working code while making it composable. The result: a template where you define your game in data files and entity scripts, and the engine handles rendering, physics, audio, and the game loop.

**Time to first new game after extraction: hours, not weeks.**
