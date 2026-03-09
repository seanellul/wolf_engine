from wolf_engine.raycasting import RayCaster
from wolf_engine.config import MAX_RAY_DIST


class RayCasting:
    """Game-specific raycasting that wraps the engine's RayCaster."""

    def __init__(self, eng):
        self.eng = eng
        self.level_map = eng.level_map
        self.wall_map = eng.level_map.wall_map
        self.door_map = eng.level_map.door_map
        self.player = eng.player

    def _is_blocked(self, tile_pos):
        if tile_pos in self.wall_map:
            return True
        if tile_pos in self.door_map:
            return self.door_map[tile_pos].is_closed
        return False

    def run(self, start_pos, direction, max_dist=MAX_RAY_DIST, npc_to_player_flag=True):
        if npc_to_player_flag:
            # NPC checking if it can see the player
            targets = {self.player.tile_pos}
            result = RayCaster.cast(
                start_pos, direction, self._is_blocked,
                targets=targets, max_dist=max_dist
            )
            return result.hit_target
        else:
            # Player shooting at NPCs
            targets = set(self.level_map.npc_map.keys())
            result = RayCaster.cast(
                start_pos, direction, self._is_blocked,
                targets=targets, max_dist=max_dist
            )
            return result.hit_pos if result.hit_target else None
