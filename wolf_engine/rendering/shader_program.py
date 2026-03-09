"""
ShaderProgram — game-facing shader setup.

Uses ShaderManager for loading, but provides the same interface the
game code expects (named program attributes, set_uniforms_on_init, update).
"""
from wolf_engine.config import TEXTURE_UNIT_0
from wolf_engine.rendering.shader_manager import ShaderManager


SHADER_MANIFEST = {
    'level': 'level',
    'instanced_door': 'instanced_door',
    'instanced_billboard': 'instanced_billboard',
    'instanced_hud': 'instanced_hud',
    'weapon': 'weapon',
}


class ShaderProgram:
    def __init__(self, eng):
        self.eng = eng
        self.ctx = eng.ctx
        self.player = eng.player

        self.manager = ShaderManager(eng.ctx)
        self.manager.load_manifest(SHADER_MANIFEST)

        # expose programs as attributes for backward compat
        self.level = self.manager['level']
        self.instanced_door = self.manager['instanced_door']
        self.instanced_billboard = self.manager['instanced_billboard']
        self.instanced_hud = self.manager['instanced_hud']
        self.weapon = self.manager['weapon']

        self.set_uniforms_on_init()

    def set_uniforms_on_init(self):
        # level
        self.level['m_proj'].write(self.player.m_proj)
        self.level['u_texture_array_0'] = TEXTURE_UNIT_0

        # instanced door
        self.instanced_door['m_proj'].write(self.player.m_proj)
        self.instanced_door['u_texture_array_0'] = TEXTURE_UNIT_0

        # billboard
        self.instanced_billboard['m_proj'].write(self.player.m_proj)
        self.instanced_billboard['u_texture_array_0'] = TEXTURE_UNIT_0

        # hud
        self.instanced_hud['u_texture_array_0'] = TEXTURE_UNIT_0

        # weapon
        self.weapon['u_texture_array_0'] = TEXTURE_UNIT_0

    def update(self):
        self.level['m_view'].write(self.player.m_view)
        self.instanced_door['m_view'].write(self.player.m_view)
        self.instanced_billboard['m_view'].write(self.player.m_view)
