from wolf_engine.pathfinding import GridPathfinder


class PathFinder:
    """Game-specific pathfinder that wraps the engine's GridPathfinder."""

    def __init__(self, eng):
        self.eng = eng
        self.level_map = eng.level_map

        self._pathfinder = GridPathfinder(
            width=self.level_map.width,
            depth=self.level_map.depth,
            is_walkable=self._is_walkable,
        )

    def _is_walkable(self, x, z):
        return (x, z) not in self.level_map.wall_map

    def find(self, start_pos, end_pos):
        # Pass current NPC positions as dynamic blockers
        dynamic_blocked = set(self.eng.level_map.npc_map.keys())
        return self._pathfinder.find(start_pos, end_pos, dynamic_blocked=dynamic_blocked)
