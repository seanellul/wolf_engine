import glm
from wolf_engine.entity import Entity


class GameObject(Entity):
    """Game-specific entity base. Adds engine/app references to Entity."""

    def __init__(self, level_map, tex_id, x, z):
        self.eng = level_map.eng
        self.app = self.eng.app
        super().__init__(tex_id, x, z)
