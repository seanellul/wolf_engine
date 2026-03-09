"""
TextureManager — texture array loading with caching support.

Builds a texture atlas from numbered PNGs, uploads as an OpenGL
texture array. Supports cache-aware rebuilding (skips build if the
atlas is newer than all source textures).
"""
import os
import moderngl as mgl
import pygame as pg
from wolf_engine.config import TEXTURE_UNIT_0, TEX_SIZE
from wolf_engine.rendering.texture_builder import TextureArrayBuilder


class Textures:
    def __init__(self, eng, source_dir='assets/textures',
                 array_path='assets/texture_array/texture_array.png',
                 sheet_path='assets/sprite_sheet/sprite_sheet.png'):
        self.eng = eng
        self.ctx = eng.ctx

        # build texture arrays (cached — skips if up to date)
        TextureArrayBuilder.build_if_needed(
            source_dir, array_path, sheet_path, tex_size=TEX_SIZE
        )

        # load textures
        self.texture_array = self.load(array_path)

        # assign texture unit
        self.texture_array.use(location=TEXTURE_UNIT_0)

    def load(self, file_path):
        texture = pg.image.load(file_path)
        texture = pg.transform.flip(texture, flip_x=True, flip_y=False)

        num_layers = texture.get_height() // texture.get_width()
        texture = self.ctx.texture_array(
            size=(texture.get_width(), texture.get_height() // num_layers, num_layers),
            components=4,
            data=pg.image.tostring(texture, 'RGBA', False)
        )

        texture.anisotropy = 32.0
        texture.build_mipmaps()
        texture.filter = (mgl.NEAREST, mgl.NEAREST)
        return texture
