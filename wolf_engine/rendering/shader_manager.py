"""
ShaderManager — data-driven shader loading and uniform management.

Loads shaders from a manifest (dict of name -> shader_name pairs) instead
of hardcoding shader names. Manages per-frame uniform updates.
"""
import os
import re
import moderngl as mgl


class ShaderManager:
    """
    Loads and manages GLSL shader programs.

    Usage:
        mgr = ShaderManager(ctx)

        # Load from the engine's built-in shaders directory
        mgr.load('level', 'level')
        mgr.load('billboard', 'instanced_billboard')

        # Or load all from a manifest
        mgr.load_manifest({
            'level': 'level',
            'door': 'instanced_door',
            'billboard': 'instanced_billboard',
            'hud': 'instanced_hud',
            'weapon': 'weapon',
        })

        # Access programs
        program = mgr['level']
        program['m_proj'].write(proj_matrix)
    """

    def __init__(self, ctx, shader_dir=None):
        self.ctx = ctx
        self._programs = {}
        self._shader_dir = shader_dir or os.path.join(
            os.path.dirname(__file__), 'shaders'
        )
        self._per_frame_updates = []

    def load(self, name, shader_name, shader_dir=None):
        """Load a shader program from .vert/.frag files."""
        search_dir = shader_dir or self._shader_dir
        vert_path = os.path.join(search_dir, f'{shader_name}.vert')
        frag_path = os.path.join(search_dir, f'{shader_name}.frag')

        with open(vert_path) as f:
            vertex_shader = self._resolve_includes(f.read(), search_dir)
        with open(frag_path) as f:
            fragment_shader = self._resolve_includes(f.read(), search_dir)

        self._programs[name] = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )
        return self._programs[name]

    def _resolve_includes(self, source, shader_dir):
        """
        Resolve #include "path" directives by inlining file contents.
        Supports includes relative to the shader directory.
        """
        def replace_include(match):
            include_path = os.path.join(shader_dir, match.group(1))
            with open(include_path) as f:
                return f.read()

        return re.sub(r'#include\s+"([^"]+)"', replace_include, source)

    def load_manifest(self, manifest, shader_dir=None):
        """Load multiple shaders from a dict of {name: shader_filename}."""
        for name, shader_name in manifest.items():
            self.load(name, shader_name, shader_dir)

    def __getitem__(self, name):
        return self._programs[name]

    def __contains__(self, name):
        return name in self._programs

    def get(self, name, default=None):
        return self._programs.get(name, default)

    def set_uniform(self, shader_name, uniform_name, value):
        """Set a uniform on a specific shader."""
        program = self._programs[shader_name]
        if hasattr(value, 'write'):
            # glm matrix — use write()
            program[uniform_name].write(value)
        else:
            program[uniform_name] = value

    def set_uniform_all(self, uniform_name, value, shader_names=None):
        """Set a uniform across multiple shaders."""
        targets = shader_names or self._programs.keys()
        for name in targets:
            program = self._programs.get(name)
            if program and uniform_name in program:
                if hasattr(value, 'to_bytes'):
                    program[uniform_name].write(value)
                else:
                    program[uniform_name] = value

    def register_per_frame(self, callback):
        """Register a callback to run each frame during update()."""
        self._per_frame_updates.append(callback)

    def update(self):
        """Run all per-frame uniform updates."""
        for callback in self._per_frame_updates:
            callback()

    @property
    def program_names(self):
        return list(self._programs.keys())
