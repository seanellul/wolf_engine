"""
GridPathfinder — BFS pathfinding on a tile grid.

Abstracted from path_finding.py. Uses callback-based walkability checks
instead of direct map references. Supports cache invalidation.
"""
from collections import deque
from functools import lru_cache


class GridPathfinder:
    """
    BFS-based grid pathfinder.

    Args:
        width: grid width in tiles
        depth: grid depth in tiles
        is_walkable: callback (x, z) -> bool, returns True if tile is walkable
        allow_diagonal: whether to allow diagonal movement (default True)
        cache_size: LRU cache max entries (default 256, None for unlimited)
    """

    CARDINAL = [(-1, 0), (0, -1), (1, 0), (0, 1)]
    DIAGONAL = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

    def __init__(self, width, depth, is_walkable, allow_diagonal=True, cache_size=256):
        self.width = width
        self.depth = depth
        self._is_walkable = is_walkable
        self._ways = self.CARDINAL + (self.DIAGONAL if allow_diagonal else [])

        self._graph = {}
        self._build_graph()

        # Create a cached version of _find_impl
        self._find_cached = lru_cache(maxsize=cache_size)(self._find_impl)

    def _build_graph(self):
        """Build the static adjacency graph from walkability checks."""
        for y in range(self.depth):
            for x in range(self.width):
                neighbors = []
                for dx, dy in self._ways:
                    nx, ny = x + dx, y + dy
                    if self._is_walkable(nx, ny):
                        neighbors.append((nx, ny))
                self._graph[(x, y)] = neighbors

    def find(self, start_pos, end_pos, dynamic_blocked=None):
        """
        Find the next step from start_pos toward end_pos.

        Args:
            start_pos: (x, z) starting tile
            end_pos: (x, z) goal tile
            dynamic_blocked: optional set of tile positions to treat as
                             blocked (e.g., other NPC positions). When
                             provided, bypasses the cache since results
                             depend on dynamic state.

        Returns:
            The next tile position to move toward, or start_pos if no path.
        """
        if dynamic_blocked:
            return self._find_impl(start_pos, end_pos, frozenset(dynamic_blocked))
        return self._find_cached(start_pos, end_pos, frozenset())

    def _find_impl(self, start_pos, end_pos, dynamic_blocked):
        visited = self._bfs(start_pos, end_pos, dynamic_blocked)
        path = [end_pos]
        step = visited.get(end_pos, start_pos)

        while step and step != start_pos:
            path.append(step)
            step = visited[step]
        return path[-1]

    def _bfs(self, start, goal, dynamic_blocked):
        queue = deque([start])
        visited = {start: None}

        while queue:
            cur_node = queue.popleft()
            if cur_node == goal:
                break
            next_nodes = self._graph.get(cur_node, [])

            for next_node in next_nodes:
                if next_node not in visited and next_node not in dynamic_blocked:
                    queue.append(next_node)
                    visited[next_node] = cur_node
        return visited

    def invalidate_cache(self):
        """Clear the pathfinding cache. Call on level load or major map changes."""
        self._find_cached.cache_clear()

    @property
    def cache_info(self):
        """Return cache statistics."""
        return self._find_cached.cache_info()
