"""
TextureArrayBuilder — builds a texture atlas from numbered PNG files.

Compiles individual textures into a vertical strip (texture array) and
a debug sprite sheet. Supports cache-aware building — skips rebuild
if the output atlas is newer than all source textures.
"""
import math
import os
import pathlib
import re
import pygame as pg
from wolf_engine.config import TEX_SIZE


class TextureArrayBuilder:

    @staticmethod
    def build_if_needed(source_dir, array_path, sheet_path, tex_size=TEX_SIZE):
        """Build only if source textures are newer than the cached atlas."""
        texture_paths = TextureArrayBuilder._get_sorted_paths(source_dir)
        if not texture_paths:
            return

        # Check if rebuild is needed
        if os.path.exists(array_path):
            atlas_mtime = os.path.getmtime(array_path)
            source_mtime = max(os.path.getmtime(p) for p in texture_paths)
            if atlas_mtime >= source_mtime:
                return  # cache is up to date

        TextureArrayBuilder._build(texture_paths, array_path, sheet_path, tex_size)

    @staticmethod
    def build(source_dir, array_path, sheet_path, tex_size=TEX_SIZE):
        """Force rebuild regardless of cache."""
        texture_paths = TextureArrayBuilder._get_sorted_paths(source_dir)
        if texture_paths:
            TextureArrayBuilder._build(texture_paths, array_path, sheet_path, tex_size)

    @staticmethod
    def _get_sorted_paths(source_dir):
        texture_paths = [
            item for item in pathlib.Path(source_dir).rglob('*.png') if item.is_file()
        ]
        return sorted(
            texture_paths,
            key=lambda p: int(re.search(r'\d+', str(p)).group(0))
        )

    @staticmethod
    def _build(texture_paths, array_path, sheet_path, tex_size):
        # texture array (vertical strip)
        texture_array = pg.Surface(
            [tex_size, tex_size * len(texture_paths)], pg.SRCALPHA, 32
        )

        # sprite sheet (square grid, for debugging)
        size = int(math.sqrt(len(texture_paths))) + 1
        sheet_size = tex_size * size
        sprite_sheet = pg.Surface([sheet_size, sheet_size], pg.SRCALPHA, 32)

        for i, path in enumerate(texture_paths):
            texture = pg.image.load(path)
            texture_array.blit(texture, (0, i * tex_size))
            sprite_sheet.blit(texture, ((i % size) * tex_size, (i // size) * tex_size))

        # ensure output directories exist
        os.makedirs(os.path.dirname(array_path), exist_ok=True)
        os.makedirs(os.path.dirname(sheet_path), exist_ok=True)

        pg.image.save(sprite_sheet, sheet_path)
        pg.image.save(texture_array, array_path)
