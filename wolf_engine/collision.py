"""
CollisionResolver — axis-separated AABB collision against a tile grid.

Extracted from the identical collision patterns in player.py and npc.py.
Resolves movement per-axis so entities slide along walls naturally.
"""
import glm


class CollisionResolver:
    def __init__(self, radius):
        self.radius = radius
        self._blockers = []  # list of callables: (int, int) -> bool

    def add_blocker(self, check):
        """
        Register a blocking check function.

        check(tile_x, tile_z) -> bool: returns True if the tile blocks movement.
        Multiple blockers are OR'd together (any blocker = blocked).
        """
        self._blockers.append(check)

    def clear_blockers(self):
        self._blockers.clear()

    def is_blocked(self, tile_pos):
        """Check if a tile position is blocked by any registered blocker."""
        for check in self._blockers:
            if check(tile_pos):
                return True
        return False

    def resolve(self, pos, dx, dz):
        """
        Resolve movement with axis-separated collision.

        Args:
            pos: current position (glm.vec3 or anything with .x, .z)
            dx: proposed x movement delta
            dz: proposed z movement delta

        Returns:
            (new_x, new_z) after collision resolution.
        """
        new_x, new_z = pos.x, pos.z

        # Try X axis
        probe_x = int(pos.x + dx + (self.radius if dx > 0 else -self.radius if dx < 0 else 0))
        probe_z_for_x = int(pos.z)
        if not self.is_blocked((probe_x, probe_z_for_x)):
            new_x = pos.x + dx

        # Try Z axis
        probe_x_for_z = int(new_x)
        probe_z = int(pos.z + dz + (self.radius if dz > 0 else -self.radius if dz < 0 else 0))
        if not self.is_blocked((probe_x_for_z, probe_z)):
            new_z = pos.z + dz

        return new_x, new_z
