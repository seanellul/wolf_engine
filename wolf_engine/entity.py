"""
Base entity class for all world-space objects.

Game-specific entities (NPCs, doors, items, weapons) inherit from this
and override update() / on_spawn() / on_destroy() as needed.
"""
import glm
from engine_config import H_WALL_SIZE


class Entity:
    def __init__(self, tex_id, x, z):
        self.tex_id = tex_id
        self.pos = glm.vec3(x + H_WALL_SIZE, 0, z + H_WALL_SIZE)
        self.rot = 0
        self.scale = glm.vec3(1)
        self.m_model = self.get_model_matrix()
        self.active = True

    def get_model_matrix(self):
        m_model = glm.translate(glm.mat4(), self.pos)
        m_model = glm.rotate(m_model, self.rot, glm.vec3(0, 1, 0))
        m_model = glm.scale(m_model, self.scale)
        return m_model

    def update(self, dt):
        """Override in subclasses. Called each frame with delta time in ms."""
        pass

    def on_spawn(self):
        """Called when the entity is added to a World."""
        pass

    def on_destroy(self):
        """Called when the entity is removed from a World."""
        pass

    @property
    def tile_pos(self):
        return int(self.pos.x), int(self.pos.z)
