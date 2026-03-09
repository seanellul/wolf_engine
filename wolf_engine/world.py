"""
World — unified entity registry with spatial indexing.

Replaces the scattered npc_map, item_map, door_map dictionaries with a
single system that manages entity groups, spatial queries, and lifecycle.
"""


class World:
    def __init__(self):
        self._groups = {}       # group_name -> list[Entity]
        self._spatial = {}      # (x, z) -> list[Entity]
        self._pending_destroy = []

    def register_group(self, name):
        """Register an entity group (e.g., 'npcs', 'doors', 'items')."""
        if name not in self._groups:
            self._groups[name] = []

    def spawn(self, entity, group):
        """Add an entity to the world in the given group."""
        if group not in self._groups:
            self.register_group(group)
        self._groups[group].append(entity)
        self._add_to_spatial(entity)
        entity.on_spawn()

    def destroy(self, entity, group):
        """Mark an entity for removal. Actual removal happens in flush()."""
        self._pending_destroy.append((entity, group))

    def flush(self):
        """Remove all entities marked for destruction."""
        for entity, group in self._pending_destroy:
            if group in self._groups and entity in self._groups[group]:
                self._groups[group].remove(entity)
            self._remove_from_spatial(entity)
            entity.on_destroy()
        self._pending_destroy.clear()

    def get_group(self, name):
        """Get all entities in a group."""
        return self._groups.get(name, [])

    def get_at(self, tile_pos):
        """Get all entities at a tile position."""
        return self._spatial.get(tile_pos, [])

    def get_one_at(self, tile_pos, group=None):
        """Get a single entity at a tile position, optionally filtered by group."""
        entities = self.get_at(tile_pos)
        if group is None:
            return entities[0] if entities else None
        group_set = set(self._groups.get(group, []))
        for e in entities:
            if e in group_set:
                return e
        return None

    def rebuild_spatial(self, group=None):
        """Rebuild the spatial index. Call after entities move."""
        if group is None:
            self._spatial.clear()
            for grp in self._groups.values():
                for entity in grp:
                    self._add_to_spatial(entity)
        else:
            # Remove all entities of this group from spatial, then re-add
            group_entities = set(self._groups.get(group, []))
            to_remove = []
            for pos, entities in self._spatial.items():
                self._spatial[pos] = [e for e in entities if e not in group_entities]
                if not self._spatial[pos]:
                    to_remove.append(pos)
            for pos in to_remove:
                del self._spatial[pos]
            for entity in group_entities:
                self._add_to_spatial(entity)

    def update_all(self, dt, group=None):
        """Update all entities, or just one group."""
        if group:
            for entity in self._groups.get(group, []):
                entity.update(dt)
        else:
            for grp in self._groups.values():
                for entity in grp:
                    entity.update(dt)

    def clear(self):
        """Remove all entities from all groups."""
        for grp in self._groups.values():
            for entity in grp:
                entity.on_destroy()
        self._groups.clear()
        self._spatial.clear()
        self._pending_destroy.clear()

    def _add_to_spatial(self, entity):
        pos = entity.tile_pos
        if pos not in self._spatial:
            self._spatial[pos] = []
        self._spatial[pos].append(entity)

    def _remove_from_spatial(self, entity):
        pos = entity.tile_pos
        if pos in self._spatial:
            self._spatial[pos] = [e for e in self._spatial[pos] if e is not entity]
            if not self._spatial[pos]:
                del self._spatial[pos]
