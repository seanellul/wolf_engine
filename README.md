# wolf_engine

A reusable engine template for building Wolfenstein-esque first-person games, built on Pygame + ModernGL.

Forked from [StanislavPetrovV's Wolfenstein 3D clone](https://github.com/StanislavPetrovV/Wolfenstein-3D-Clone) (MIT license). The original project is a complete, playable Wolfenstein 3D tribute. We're extracting its proven rendering and game loop architecture into a composable engine so we can rapidly build different games on the same foundation.

![wolfenstein](/screenshot/0.jpg)

## What's Here

The codebase is mid-extraction. The reference game (the original Wolfenstein clone) is fully playable while we refactor the internals into clean engine vs game layers.

### Current Architecture

```
engine_config.py        Engine constants (resolution, FOV, GL params, input, timers)
game_data.py            Game-specific data (weapons, NPCs, items, HUD layout)
settings.py             Re-export shim (so existing code keeps working during refactor)
texture_id.py           Texture ID registry

main.py                 App shell, GL context, game loop
engine.py               System orchestrator, level lifecycle
camera.py               Camera math (position, orientation, view/projection matrices)
player.py               Player controller + combat + interaction
level_map.py            TMX level loader + entity spawning
ray_casting.py          DDA raycaster (line-of-sight, shooting)
path_finding.py         BFS grid pathfinder with LRU cache
scene.py                Render order manager
shader_program.py       GLSL shader loader + uniform management
textures.py             Texture array GPU upload
texture_builder.py      Texture atlas builder from PNGs
sound.py                Audio system (channel-based)

wolf_engine/            Engine core package:
  entity.py               Base Entity class (pos, rot, scale, model matrix, lifecycle)
  world.py                Entity registry with spatial indexing and group management
  collision.py            Axis-separated AABB collision with pluggable blockers
  raycasting.py           DDA voxel raycaster with callback-based blocking/targets
  pathfinding.py          BFS grid pathfinder with cache invalidation

meshes/                 Mesh builders (level geometry, instanced quads, weapon)
shaders/                GLSL 330 shaders (level, billboard, door, HUD, weapon)
game_objects/           Game entity classes (NPC, Door, Item, Weapon, HUD)
resources/levels/       Tiled TMX map files
assets/                 Textures, sounds, music
```

### Extraction Progress

See [ENGINE_EXTRACTION_SCRUTINY.md](ENGINE_EXTRACTION_SCRUTINY.md) for the full plan.

- **Phase 1: Critical bug fixes** -- Done
  - Fixed VAO-per-frame rebuild in instanced rendering (pre-allocated persistent VBOs)
  - Fixed delta_time ordering (measured before update, not after)
  - Fixed NPC list mutation during iteration + dict reassignment breaking views
- **Phase 2: Settings split** -- Done
  - `engine_config.py` -- engine constants (swap these to change engine behavior)
  - `game_data.py` -- game definitions (swap these to make a different game)
  - `settings.py` -- backward-compatible shim
- **Phase 3: Engine core extraction** -- Done
  - `wolf_engine/entity.py` -- Base Entity with pos, rot, scale, model matrix, lifecycle hooks
  - `wolf_engine/world.py` -- Unified entity registry with spatial indexing and group management
  - `wolf_engine/collision.py` -- Axis-separated AABB with pluggable blocker callbacks
  - `wolf_engine/raycasting.py` -- DDA raycaster with callback-based blocking and target detection
  - `wolf_engine/pathfinding.py` -- BFS grid pathfinder with dynamic blockers and cache invalidation
  - Game objects (`GameObject`, `NPC`, `Player`) now use engine systems
- **Phase 4: Rendering pipeline** -- Next
- **Phase 5: Infrastructure** -- Planned
- **Phase 6: Reference game rebuild** -- Planned

## Tech Stack

| Dependency | Role |
|---|---|
| [Pygame](https://www.pygame.org/) | Window, input, audio, image loading |
| [ModernGL](https://github.com/moderngl/moderngl) | OpenGL 3.3 abstraction |
| [PyGLM](https://github.com/Zuzu-Typ/PyGLM) | Vector/matrix math |
| [NumPy](https://numpy.org/) | Vertex data arrays |
| [PyTMX](https://github.com/bitcraft/PyTMX) | Tiled map format parsing |

## Getting Started

```bash
pip install -r requirements.txt
python main.py
```

### Controls

| Key | Action |
|---|---|
| WASD | Move |
| Mouse | Look |
| Left click | Shoot |
| 1 / 2 / 3 | Switch weapon (knife / pistol / rifle) |
| Mouse wheel | Cycle weapons |
| F | Interact (open doors) |
| Q / E | Move up / down |
| Tab | Toggle mouse capture |
| Esc | Quit |

### Level Editing

Levels are [Tiled](https://www.mapeditor.org/) maps (`.tmx`). See `resources/levels/` for examples. Layers:

- `walls`, `floors`, `ceilings` -- tile layers with texture IDs
- `player` -- object layer, single spawn point
- `doors`, `items`, `npc` -- object layers with positioned entities

## Credits

- Original game by [StanislavPetrovV](https://github.com/StanislavPetrovV) ([YouTube tutorial](https://youtu.be/yJXuvK_eLrQ))
- Engine extraction and architecture work by [@seanellul](https://github.com/seanellul)

## License

MIT -- see [LICENSE](LICENSE).
