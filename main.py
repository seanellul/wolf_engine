import pygame as pg
from wolf_engine.app import App, GameState
from game.engine import Engine


class PlayingState(GameState):
    """Main gameplay state — wraps the game Engine."""

    def enter(self):
        self.engine = Engine(self.app)

    def handle_event(self, event):
        # Quit on Escape
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.app.is_running = False
            return

        # Toggle mouse capture with Tab
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


if __name__ == '__main__':
    app = App(title='Wolfenstein 3D')
    app.push_state(PlayingState())
    app.run()
