"""
UI — OpenGL text and quad rendering for menu screens.

Uses pygame.font for text, uploads as GL textures, and draws
screen-space quads. Provides MenuState for keyboard-navigable menus.
"""
import pygame as pg
import moderngl as mgl
import numpy as np
from wolf_engine.app import GameState


class MenuRenderer:
    """Renders text and colored rectangles as OpenGL screen-space quads."""

    def __init__(self, ctx, win_res):
        self.ctx = ctx
        self.win_res = win_res
        self._tex_cache = {}
        self._font_cache = {}
        self._prog = self._build_program()
        self._vao = self._build_quad()

    def _build_program(self):
        return self.ctx.program(
            vertex_shader='''
                #version 330 core
                in vec2 in_pos;
                in vec2 in_uv;
                out vec2 uv;
                uniform vec2 u_pos;
                uniform vec2 u_size;
                uniform vec2 u_screen;
                void main() {
                    vec2 pixel = u_pos + in_pos * u_size;
                    vec2 ndc = (pixel / u_screen) * 2.0 - 1.0;
                    ndc.y = -ndc.y;
                    gl_Position = vec4(ndc, 0.0, 1.0);
                    uv = in_uv;
                }
            ''',
            fragment_shader='''
                #version 330 core
                in vec2 uv;
                out vec4 frag;
                uniform sampler2D u_tex;
                uniform float u_alpha;
                void main() {
                    vec4 c = texture(u_tex, uv);
                    frag = vec4(c.rgb, c.a * u_alpha);
                }
            ''',
        )

    def _build_quad(self):
        verts = np.array([
            # pos    uv (v=1 at top for flipped texture data)
            0, 0, 0, 1,
            1, 0, 1, 1,
            1, 1, 1, 0,
            0, 0, 0, 1,
            1, 1, 1, 0,
            0, 1, 0, 0,
        ], dtype='f4')
        vbo = self.ctx.buffer(verts)
        return self.ctx.vertex_array(
            self._prog, [(vbo, '2f 2f', 'in_pos', 'in_uv')]
        )

    def _get_font(self, size, name=None):
        key = (name, size)
        if key not in self._font_cache:
            self._font_cache[key] = pg.font.SysFont(name, size)
        return self._font_cache[key]

    def _text_tex(self, text, size, color):
        key = (text, size, color)
        if key not in self._tex_cache:
            font = self._get_font(size)
            surf = font.render(text, True, color).convert_alpha()
            w, h = surf.get_size()
            data = pg.image.tostring(surf, 'RGBA', True)
            tex = self.ctx.texture((w, h), 4, data)
            tex.filter = (mgl.LINEAR, mgl.LINEAR)
            self._tex_cache[key] = (tex, w, h)
        return self._tex_cache[key]

    def _rect_tex(self, r, g, b):
        key = ('__rect__', r, g, b)
        if key not in self._tex_cache:
            data = bytes([r, g, b, 255])
            tex = self.ctx.texture((1, 1), 4, data)
            self._tex_cache[key] = (tex, 1, 1)
        return self._tex_cache[key][0]

    def begin(self):
        """Call before a batch of draw operations."""
        self.ctx.disable(mgl.DEPTH_TEST)
        self.ctx.blend_func = mgl.SRC_ALPHA, mgl.ONE_MINUS_SRC_ALPHA

    def end(self):
        """Call after a batch of draw operations."""
        self.ctx.enable(mgl.DEPTH_TEST)

    def draw_text(self, text, x, y, size=36, color=(255, 255, 255),
                  alpha=1.0, center=False):
        """Draw text at pixel position. Call between begin()/end()."""
        if not text:
            return
        tex, w, h = self._text_tex(text, size, color)
        if center:
            x -= w / 2
            y -= h / 2
        self._draw_quad(tex, x, y, w, h, alpha)

    def draw_rect(self, x, y, w, h, color=(0, 0, 0), alpha=0.7):
        """Draw a colored rectangle. Call between begin()/end()."""
        tex = self._rect_tex(*color)
        self._draw_quad(tex, x, y, w, h, alpha)

    def draw_overlay(self, color=(0, 0, 0), alpha=0.7):
        """Draw a fullscreen overlay. Call between begin()/end()."""
        self.draw_rect(
            0, 0, float(self.win_res.x), float(self.win_res.y), color, alpha
        )

    def _draw_quad(self, tex, x, y, w, h, alpha):
        self._prog['u_pos'].value = (float(x), float(y))
        self._prog['u_size'].value = (float(w), float(h))
        self._prog['u_screen'].value = (
            float(self.win_res.x), float(self.win_res.y)
        )
        self._prog['u_alpha'].value = alpha
        tex.use(0)
        self._prog['u_tex'].value = 0
        self._vao.render()


class MenuState(GameState):
    """
    Base class for keyboard-navigable menu screens.

    Subclass and set title + items:

        class MainMenu(MenuState):
            def __init__(self):
                super().__init__('My Game', [
                    ('Play', self.play),
                    ('Quit', self.quit),
                ])
    """

    def __init__(self, title='', items=None):
        self.title = title
        self.items = items or []
        self.selected = 0
        self.ui: MenuRenderer | None = None

    def enter(self):
        # Lazy-create shared MenuRenderer
        if not hasattr(self.app, '_menu_renderer') or self.app._menu_renderer is None:
            self.app._menu_renderer = MenuRenderer(self.app.ctx, self.app.win_res)
        self.ui = self.app._menu_renderer
        # Show cursor in menus
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)

    def handle_event(self, event):
        if event.type != pg.KEYDOWN or not self.items:
            return
        if event.key in (pg.K_UP, pg.K_w):
            self.selected = (self.selected - 1) % len(self.items)
        elif event.key in (pg.K_DOWN, pg.K_s):
            self.selected = (self.selected + 1) % len(self.items)
        elif event.key in (pg.K_RETURN, pg.K_SPACE):
            _, callback = self.items[self.selected]
            callback()

    def render_menu(self):
        """Render the title and items. Call between ui.begin()/ui.end()."""
        cx = float(self.app.win_res.x) / 2
        cy = float(self.app.win_res.y) / 2

        if self.title:
            self.ui.draw_text(
                self.title, cx, cy - 100,
                size=64, color=(200, 180, 100), center=True,
            )

        for i, (label, _) in enumerate(self.items):
            y = cy + 20 + i * 55
            if i == self.selected:
                color = (255, 220, 80)
                display = '> ' + label
            else:
                color = (180, 180, 180)
                display = '  ' + label
            self.ui.draw_text(display, cx, y, size=40, color=color, center=True)

    def render(self):
        self.ui.begin()
        self.render_menu()
        self.ui.end()
