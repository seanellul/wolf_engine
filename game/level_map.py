from settings import *
from wolf_engine.tmx_loader import TMXLoader
from game.entities.door import Door
from game.entities.item import Item
from game.entities.npc import NPC


class LevelMap:
    def __init__(self, eng, tmx_file='test.tmx'):
        self.eng = eng

        # Use engine TMXLoader for raw parsing
        loader = TMXLoader(base_path='resources/levels/')
        level_data = loader.load(tmx_file)

        self.width = level_data.width
        self.depth = level_data.depth

        # Tile maps from TMXLoader
        self.wall_map = level_data.tile_maps.get('walls', {})
        self.floor_map = level_data.tile_maps.get('floors', {})
        self.ceil_map = level_data.tile_maps.get('ceilings', {})

        # Entity maps (populated by spawn_entities)
        self.door_map, self.item_map = {}, {}
        self.npc_map, self.npc_list = {}, []

        # Spawn entities from parsed data
        self.spawn_entities(level_data)

    def spawn_entities(self, level_data):
        # Set player position
        px, py, pz = level_data.player_spawn
        self.eng.player.position = glm.vec3(px, PLAYER_HEIGHT, pz)

        # Spawn doors
        for obj in level_data.objects.get('doors', []):
            door = Door(self, tex_id=obj.tex_id, x=obj.pos[0], z=obj.pos[1])
            self.door_map[obj.pos] = door

        # Spawn items
        for obj in level_data.objects.get('items', []):
            item = Item(self, tex_id=obj.tex_id, x=obj.pos[0], z=obj.pos[1])
            self.item_map[obj.pos] = item

        # Spawn NPCs
        for obj in level_data.objects.get('npc', []):
            npc = NPC(self, tex_id=obj.tex_id, x=obj.pos[0], z=obj.pos[1])
            self.npc_map[obj.pos] = npc
            self.npc_list.append(npc)

        # Update player data
        self.eng.player.wall_map = self.wall_map
        self.eng.player.door_map = self.door_map
        self.eng.player.item_map = self.item_map
        self.eng.player.setup_collision()
