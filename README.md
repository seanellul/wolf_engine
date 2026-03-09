# wolf_engine

A reusable engine template for building Wolfenstein-esque first-person games, built on Pygame + ModernGL.

Forked from [StanislavPetrovV's Wolfenstein 3D clone](https://github.com/StanislavPetrovV/Wolfenstein-3D-Clone) (MIT license). The original project is a complete, playable Wolfenstein 3D tribute. We're extracting its proven rendering and game loop architecture into a composable engine so we can rapidly build different games on the same foundation.

![wolfenstein](/screenshot/0.jpg)

## Project Structure

The codebase is split into two packages with a clear boundary:

```
wolf_engine/        Engine (reusable across games)
  config.py           Engine constants (resolution, FOV, GL, input, timers)
  camera.py           First-person camera math
  entity.py           Base Entity (pos, rot, scale, model matrix, lifecycle)
  world.py            Entity registry with spatial indexing
  collision.py        AABB collision with pluggable blockers
  raycasting.py       DDA raycaster with callback-based blocking/targets
  pathfinding.py      BFS grid pathfinder with dynamic blockers
  rendering/          OpenGL pipeline (shaders, meshes, textures)

game/               Game code (swap this to make a different game)
  engine.py           Game orchestrator and level lifecycle
  player.py           Player combat, inventory, interaction
  scene.py            Render order manager
  level_map.py        TMX level loader and entity spawning
  ray_casting.py      Game-specific raycasting rules
  path_finding.py     Game-specific pathfinding rules
  sound.py            Audio catalogue
  data.py             Weapon, NPC, item, HUD definitions
  texture_id.py       Texture ID registry
  entities/           NPC, Door, Item, Weapon, HUD

main.py             Entry point
settings.py         Re-export shim (backward compat)
assets/             Textures, sounds, music
resources/          Tiled .tmx level files
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full breakdown of the engine/game boundary, design patterns, and how to build a new game on the engine.

See [ENGINE_EXTRACTION_SCRUTINY.md](ENGINE_EXTRACTION_SCRUTINY.md) for the original analysis and extraction plan.

### Extraction Progress

- **Phase 1: Critical bug fixes** -- Done
- **Phase 2: Settings split** -- Done
- **Phase 3: Engine core extraction** -- Done
- **Phase 3.5: Repo reorganization** -- Done
- **Phase 4: Rendering pipeline** -- Done
  - `RenderScene` with named layers replacing hardcoded render order
  - `ShaderManager` with data-driven loading and `#include` resolution
  - Shared shader snippets (`fog.glsl`, `gamma.glsl`) eliminating duplication
  - `TextureArrayBuilder` with mtime-based caching (skips rebuild when unchanged)
- **Phase 5: Infrastructure** -- Next
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
