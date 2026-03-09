"""
RayCaster — DDA voxel traversal for line-of-sight and hit detection.

Abstracted from ray_casting.py. Uses callback-based blocking and target
checks instead of direct map references, so games can define their own
blocking/target logic.
"""
import glm
from dataclasses import dataclass
from typing import Callable, Optional, Set, Tuple
from wolf_engine.config import MAX_RAY_DIST


@dataclass
class RayResult:
    """Result of a ray cast."""
    hit_blocked: bool = False      # Ray hit a blocking tile
    hit_target: bool = False       # Ray reached a target tile
    hit_pos: Optional[Tuple[int, int]] = None  # Tile position of the hit
    distance: float = 0.0         # Distance traveled


class RayCaster:
    """
    Generic DDA raycaster. Configure with callbacks:
    - is_blocked(tile_pos) -> bool: does this tile stop the ray?
    - targets: set of tile positions to detect hits on
    """

    @staticmethod
    def _get_init_data(pos1, pos2):
        d_ = glm.sign(pos2 - pos1)
        delta_ = min(d_ / (pos2 - pos1), 10000000.0) if d_ != 0 else 10000000.0
        max_ = delta_ * (1.0 - glm.fract(pos1)) if d_ > 0 else delta_ * glm.fract(pos1)
        return d_, delta_, max_

    @staticmethod
    def cast(start_pos, direction,
             is_blocked: Callable[[Tuple[int, int]], bool],
             targets: Optional[Set[Tuple[int, int]]] = None,
             max_dist: float = MAX_RAY_DIST) -> RayResult:
        """
        Cast a ray through the voxel grid.

        Args:
            start_pos: origin point (vec3)
            direction: ray direction (vec3, will be scaled by max_dist)
            is_blocked: callback that returns True for blocking tiles
            targets: optional set of tile positions to detect
            max_dist: maximum ray distance

        Returns:
            RayResult with hit information.
        """
        x1, y1, z1 = start_pos
        x2, y2, z2 = start_pos + direction * max_dist
        cur_voxel_pos = glm.ivec3(x1, y1, z1)

        dx, delta_x, max_x = RayCaster._get_init_data(x1, x2)
        dy, delta_y, max_y = RayCaster._get_init_data(y1, y2)
        dz, delta_z, max_z = RayCaster._get_init_data(z1, z2)

        while not (max_x > 1.0 and max_y > 1.0 and max_z > 1.0):
            cur_tile_pos = (cur_voxel_pos.x, cur_voxel_pos.z)

            if is_blocked(cur_tile_pos):
                return RayResult(hit_blocked=True, hit_pos=cur_tile_pos)

            if targets is not None and cur_tile_pos in targets:
                return RayResult(hit_target=True, hit_pos=cur_tile_pos)

            if max_x < max_y:
                if max_x < max_z:
                    cur_voxel_pos.x += dx
                    max_x += delta_x
                else:
                    cur_voxel_pos.z += dz
                    max_z += delta_z
            else:
                if max_y < max_z:
                    cur_voxel_pos.y += dy
                    max_y += delta_y
                else:
                    cur_voxel_pos.z += dz
                    max_z += delta_z

        return RayResult()
