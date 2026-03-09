"""
TMXLoader — raw level data extraction from Tiled TMX files.

Parses TMX maps into engine-neutral data structures (LevelData).
No entity spawning — that's the game's job. Games receive tile grids
and object spawn points, then create their own entities from them.
"""
import pytmx
from dataclasses import dataclass, field
from wolf_engine.config import TEX_SIZE


@dataclass
class ObjectData:
    """A spawnable object parsed from a TMX object layer."""
    pos: tuple[int, int]
    tex_id: int
    properties: dict = field(default_factory=dict)


@dataclass
class LevelData:
    """Raw level data extracted from a TMX file."""
    width: int
    depth: int
    tile_maps: dict[str, dict[tuple[int, int], int]] = field(default_factory=dict)
    objects: dict[str, list[ObjectData]] = field(default_factory=dict)
    player_spawn: tuple[float, float, float] = (0, 0, 0)


class TMXLoader:
    """Loads TMX files into engine-neutral LevelData."""

    # Standard tile layer names
    TILE_LAYERS = ('walls', 'floors', 'ceilings')

    # Standard object layer names
    OBJECT_LAYERS = ('doors', 'items', 'npc')

    def __init__(self, base_path='resources/levels/'):
        self.base_path = base_path

    def load(self, tmx_file, tile_layers=None, object_layers=None,
             player_layer='player') -> LevelData:
        """
        Parse a TMX file into a LevelData structure.

        Args:
            tmx_file: filename (relative to base_path) or absolute path
            tile_layers: names of tile layers to parse (default: walls, floors, ceilings)
            object_layers: names of object layers to parse (default: doors, items, npc)
            player_layer: name of the player spawn layer

        Returns:
            LevelData with tile grids, object spawn points, and player spawn.
        """
        path = tmx_file if '/' in tmx_file else self.base_path + tmx_file
        tiled_map = pytmx.TiledMap(path)
        gid_map = tiled_map.tiledgidmap

        tile_layers = tile_layers or self.TILE_LAYERS
        object_layers = object_layers or self.OBJECT_LAYERS

        data = LevelData(
            width=tiled_map.width,
            depth=tiled_map.height,
        )

        # Parse player spawn
        if player_layer:
            try:
                player_obj = tiled_map.get_layer_by_name(player_layer).pop()
                data.player_spawn = (
                    player_obj.x / TEX_SIZE,
                    0,
                    player_obj.y / TEX_SIZE,
                )
            except (ValueError, IndexError):
                pass

        # Parse tile layers
        for layer_name in tile_layers:
            try:
                layer = tiled_map.get_layer_by_name(layer_name)
            except ValueError:
                continue

            tile_map = {}
            for ix in range(data.width):
                for iz in range(data.depth):
                    if gid := layer.data[iz][ix]:
                        tile_map[(ix, iz)] = gid_map[gid] - 1
            data.tile_maps[layer_name] = tile_map

        # Parse object layers
        for layer_name in object_layers:
            try:
                layer = tiled_map.get_layer_by_name(layer_name)
            except ValueError:
                continue

            objects = []
            for obj in layer:
                pos = (int(obj.x / TEX_SIZE), int(obj.y / TEX_SIZE))
                tex_id = gid_map[obj.gid] - 1
                props = dict(obj.properties) if obj.properties else {}
                objects.append(ObjectData(pos=pos, tex_id=tex_id, properties=props))
            data.objects[layer_name] = objects

        return data
