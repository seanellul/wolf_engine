# Architecture

## Directory Structure

```
wolf_engine/                        Reusable engine (copy to start a new game)
├── __init__.py                       Public API: App, GameState, Entity, World, CollisionResolver, RayCaster, GridPathfinder, AudioManager, InputManager, TMXLoader, RenderScene, ShaderManager
├── app.py                            App shell with GL context, main loop, and game state stack
├── config.py                         Engine constants (resolution, FOV, GL params, input keys, timers)
├── camera.py                         Camera math (position, orientation, view/projection matrices)
├── entity.py                         Base Entity class (pos, rot, scale, model matrix, lifecycle hooks)
├── world.py                          Entity registry with spatial indexing and group management
├── collision.py                      Axis-separated AABB collision with pluggable blockers
├── raycasting.py                     DDA voxel raycaster with callback-based blocking/targets
├── pathfinding.py                    BFS grid pathfinder with dynamic blockers and cache
├── audio.py                          Manifest-driven sound loading, positional audio, music playback
├── input.py                          Action-based input mapping (decouples game logic from key codes)
├── tmx_loader.py                     TMX parsing → LevelData (no entity spawning)
├── ui.py                             MenuRenderer (GL text/quads) + MenuState (navigable menu screens)
└── rendering/
    ├── __init__.py
    ├── render_scene.py               Named render layers (RenderScene, RenderLayer)
    ├── shader_manager.py             Data-driven shader loading with #include resolution
    ├── shader_program.py             Game-facing shader setup (uses ShaderManager)
    ├── texture_manager.py            Texture array GPU upload with cache-aware building
    ├── texture_builder.py            Texture atlas builder with mtime-based caching
    ├── meshes/
    │   ├── base_mesh.py              Abstract VAO/VBO base
    │   ├── quad_mesh.py              Billboard quad geometry
    │   ├── instanced_quad_mesh.py    Instanced rendering (persistent VBOs)
    │   ├── level_mesh.py             Level geometry VAO
    │   ├── level_mesh_builder.py     Level geometry generator with AO
    │   └── weapon_mesh.py            First-person weapon quad
    └── shaders/
        ├── include/
        │   ├── fog.glsl                    Shared exponential fog (apply_fog)
        │   └── gamma.glsl                  Shared sRGB gamma (gamma_decode/gamma_encode)
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
| `app.py` | Game loop shell with GL context, timing, and game state stack (push/pop/replace) |
| `camera.py` | First-person camera with position, orientation, and projection matrices |
| `entity.py` | Base object with position, rotation, scale, model matrix, and lifecycle hooks |
| `world.py` | Entity storage with named groups, spatial indexing by tile, and deferred destruction |
| `collision.py` | Movement resolution against arbitrary blocking rules (plug in your own blockers) |
| `raycasting.py` | Line-of-sight and hit detection (plug in your own blocking and target rules) |
| `pathfinding.py` | Grid navigation (plug in your own walkability rules and dynamic obstacles) |
| `audio.py` | Manifest-driven sound loading, round-robin channels, positional audio, music |
| `input.py` | Action-based key bindings, decoupling game logic from specific key constants |
| `tmx_loader.py` | TMX parsing into raw `LevelData` (tile grids + object spawn points, no entities) |
| `ui.py` | `MenuRenderer` for GL text/quad rendering + `MenuState` for navigable menu screens |
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

### Render layers

The engine provides `RenderScene` — an ordered collection of named render layers.
Games register layers in the order they should render, then add meshes to each:

```python
from wolf_engine.rendering.render_scene import RenderScene

scene = RenderScene()
scene.add_layer('level').add(level_mesh)
scene.add_layer('doors').add(door_mesh)
scene.add_layer('items').add(item_mesh)
scene.add_layer('hud').add(hud_mesh)
scene.add_layer('npcs').add(npc_mesh)
scene.add_layer('weapon').add(weapon_mesh)

# Each frame:
scene.render_all()  # renders in registration order
```

### Shader management

`ShaderManager` loads GLSL programs from files, with `#include` directive support:

```python
from wolf_engine.rendering.shader_manager import ShaderManager

mgr = ShaderManager(ctx)
mgr.load_manifest({
    'level': 'level',
    'billboard': 'instanced_billboard',
})
program = mgr['level']
```

Shared shader code lives in `wolf_engine/rendering/shaders/include/`:
- `fog.glsl` — `apply_fog(color)` for exponential squared fog
- `gamma.glsl` — `gamma_decode(color)` and `gamma_encode(color)` for sRGB

Use `#include "include/fog.glsl"` in any shader to inline them.

### Texture caching

`TextureArrayBuilder` compares source file mtimes against the cached atlas.
It only rebuilds when textures have changed, skipping the build on subsequent launches.

### Game state stack

`App` manages a stack of `GameState` objects. The top state receives all events, updates, and renders. Games push/pop states for flow control:

```python
from wolf_engine.app import App, GameState

class PlayingState(GameState):
    def enter(self):
        # set up level, player, etc.
    def handle_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.app.push_state(PausedState())
    def update(self):
        # game logic
    def render(self):
        # draw scene

app = App()
app.push_state(PlayingState())
app.run()
```

### Menu system

`MenuState` + `MenuRenderer` provide keyboard-navigable menu screens rendered via OpenGL. The reference game uses three states:

```
MainMenuState ──[New Game]──> PlayingState ──[ESC]──> PauseMenuState
                                   ^                       │
                                   └───────[Resume]────────┘
                                                           │
                              MainMenuState <──[Main Menu]─┘
```

```python
from wolf_engine.ui import MenuState

class PauseMenu(MenuState):
    def __init__(self, engine):
        super().__init__('PAUSED', [
            ('Resume', self.resume),
            ('Quit', self.quit),
        ])
        self.engine = engine

    def resume(self):
        self.app.pop_state()

    def quit(self):
        self.app.is_running = False

    def render(self):
        self.engine.render()           # game scene behind
        self.ui.begin()
        self.ui.draw_overlay(alpha=0.6) # darken
        self.render_menu()              # title + items
        self.ui.end()
```

### Audio management

`AudioManager` loads sounds from a manifest and plays them with round-robin channel assignment. Supports positional audio with distance-based volume falloff:

```python
from wolf_engine.audio import AudioManager

audio = AudioManager(num_channels=10)
audio.load_manifest({
    'gunshot': {'path': 'gunshot.wav', 'volume': 0.8},
    'footstep': 'footstep.ogg',  # shorthand, volume defaults to 0.5
}, base_path='assets/sounds/')

audio.play('gunshot')
audio.play_positional('footstep', source_pos, listener_pos, max_dist=15.0)
audio.play_music('assets/music/theme.ogg')
```

### Input mapping

`InputManager` decouples game logic from specific key codes. Games define actions and bind them to keys:

```python
from wolf_engine.input import InputManager

input_mgr = InputManager(bindings={
    'move_forward': pg.K_w,
    'shoot': pg.K_SPACE,
})

# In update:
if input_mgr.is_pressed('move_forward'):
    player.move_forward()

# In event handling:
if input_mgr.is_action_event(event, 'shoot'):
    player.shoot()
```

### Level loading

`TMXLoader` parses Tiled maps into raw `LevelData` without spawning entities. Games use the data to create their own entities:

```python
from wolf_engine.tmx_loader import TMXLoader

loader = TMXLoader(base_path='resources/levels/')
level_data = loader.load('level_0.tmx')

# level_data.tile_maps['walls']  -> {(x, z): tex_id, ...}
# level_data.objects['npc']      -> [ObjectData(pos, tex_id, properties), ...]
# level_data.player_spawn        -> (x, y, z)

# Game spawns its own entities from the raw data:
for obj in level_data.objects['npc']:
    world.spawn(MyNPC(obj.pos, obj.tex_id), group='npcs')
```

### Settings shim

During the transition, `from settings import *` still works everywhere. It re-exports
both `wolf_engine.config` (engine constants) and `game.data` (game definitions).
This will be removed once all files use direct imports.
