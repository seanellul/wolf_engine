import pygame as pg
from wolf_engine.app import App, GameState
from wolf_engine.ui import MenuState
from game.engine import Engine


class MainMenuState(MenuState):
    """Title screen — New Game or Quit."""

    def __init__(self):
        super().__init__(
            title='WOLFENSTEIN 3D',
            items=[
                ('New Game', self.start_game),
                ('Quit', self.quit_game),
            ],
        )

    def start_game(self):
        self.app.replace_state(PlayingState())

    def quit_game(self):
        self.app.is_running = False


class PlayingState(GameState):
    """Main gameplay state — wraps the game Engine."""

    def __init__(self):
        self.engine = None

    def enter(self):
        if self.engine is None:
            self.engine = Engine(self.app)
        pg.event.set_grab(True)
        pg.mouse.set_visible(False)

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.app.push_state(PauseMenuState(self.engine))
            return

        if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
            grabbed = pg.event.get_grab()
            pg.event.set_grab(not grabbed)
            pg.mouse.set_visible(grabbed)

        self.engine.handle_events(event=event)

    def update(self):
        self.engine.update()
        pg.display.set_caption(f'{self.app.fps_value}')

    def render(self):
        self.engine.render()


class PauseMenuState(MenuState):
    """Pause overlay — Resume, Main Menu, or Quit."""

    def __init__(self, engine):
        super().__init__(
            title='PAUSED',
            items=[
                ('Resume', self.resume),
                ('Main Menu', self.main_menu),
                ('Quit', self.quit_game),
            ],
        )
        self.engine = engine

    def resume(self):
        self.app.pop_state()

    def main_menu(self):
        pg.mixer.music.stop()
        self.app.pop_state()  # pop PauseMenuState
        self.app.replace_state(MainMenuState())  # replace PlayingState

    def quit_game(self):
        self.app.is_running = False

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.resume()
            return
        super().handle_event(event)

    def render(self):
        # Game scene behind the overlay
        self.engine.render()
        self.ui.begin()
        self.ui.draw_overlay(alpha=0.6)
        self.render_menu()
        self.ui.end()


if __name__ == '__main__':
    app = App(title='Wolfenstein 3D', grab_mouse=False)
    app.push_state(MainMenuState())
    app.run()
