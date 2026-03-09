"""
App — game loop shell with a state stack.

Handles GL context creation, the main loop, and dispatching to the
active game state. Games push/pop states (menu, playing, paused,
game-over) and the App routes update/render/events to the top state.
"""
import sys
import pygame as pg
import moderngl as mgl
from wolf_engine.config import (
    MAJOR_VERSION, MINOR_VERSION, DEPTH_SIZE,
    WIN_RES, BG_COLOR, SYNC_PULSE,
)


class GameState:
    """
    Base class for game states.

    Subclass and override the methods your state needs.
    The `app` attribute is set automatically when pushed.
    """
    app = None

    def enter(self):
        """Called when this state becomes active (pushed or uncovered)."""
        pass

    def exit(self):
        """Called when this state is removed (popped or covered)."""
        pass

    def handle_event(self, event):
        """Handle a single pygame event."""
        pass

    def update(self):
        """Per-frame update logic."""
        pass

    def render(self):
        """Per-frame rendering."""
        pass


class App:
    """
    Game loop shell with OpenGL context and state stack.

    Usage:
        app = App()
        app.push_state(MyPlayingState())
        app.run()
    """
    def __init__(self, win_res=None, title='wolf_engine',
                 grab_mouse=True, sync_pulse=SYNC_PULSE):
        pg.init()

        win_res = win_res or WIN_RES

        # OpenGL context
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, MAJOR_VERSION)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, MINOR_VERSION)
        pg.display.gl_set_attribute(
            pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE
        )
        pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, DEPTH_SIZE)

        self.win_res = win_res
        pg.display.set_mode(
            (int(win_res.x), int(win_res.y)),
            flags=pg.OPENGL | pg.DOUBLEBUF,
        )
        pg.display.set_caption(title)

        self.ctx = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.BLEND)
        self.ctx.gc_mode = 'auto'

        # Timing
        self.clock = pg.time.Clock()
        self.delta_time = 0
        self.time = 0
        self.fps_value = 0

        # Mouse
        if grab_mouse:
            pg.event.set_grab(True)
            pg.mouse.set_visible(False)

        # Timer events
        self.anim_trigger = False
        self.anim_event = pg.USEREVENT + 0
        pg.time.set_timer(self.anim_event, sync_pulse)

        self.sound_trigger = False
        self.sound_event = pg.USEREVENT + 1
        pg.time.set_timer(self.sound_event, 750)

        # State stack
        self._states: list[GameState] = []
        self.is_running = True

    @property
    def active_state(self) -> GameState | None:
        return self._states[-1] if self._states else None

    def push_state(self, state: GameState):
        """Push a state onto the stack, making it active."""
        if self._states:
            self._states[-1].exit()
        state.app = self
        self._states.append(state)
        state.enter()

    def pop_state(self) -> GameState | None:
        """Pop the active state. The state below (if any) becomes active."""
        if not self._states:
            return None
        old = self._states.pop()
        old.exit()
        if self._states:
            self._states[-1].enter()
        return old

    def replace_state(self, state: GameState):
        """Replace the active state (pop + push without activating the one below)."""
        if self._states:
            self._states[-1].exit()
            self._states.pop()
        state.app = self
        self._states.append(state)
        state.enter()

    def handle_events(self):
        self.anim_trigger = False
        self.sound_trigger = False

        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False
                return

            if event.type == self.anim_event:
                self.anim_trigger = True
            elif event.type == self.sound_event:
                self.sound_trigger = True

            # Dispatch to active state
            if self.active_state:
                self.active_state.handle_event(event)

    def update(self):
        self.delta_time = self.clock.tick()
        self.time = pg.time.get_ticks() * 0.001

        if self.active_state:
            self.active_state.update()

        self.fps_value = int(self.clock.get_fps())

    def render(self):
        self.ctx.clear(color=BG_COLOR)
        if self.active_state:
            self.active_state.render()
        pg.display.flip()

    def run(self):
        """Main loop. Runs until is_running is False or all states are popped."""
        while self.is_running and self._states:
            self.handle_events()
            self.update()
            self.render()
        pg.quit()
        sys.exit()
