"""
InputManager — action-based input mapping.

Decouples game logic from specific key codes. Games define actions
(e.g., 'move_forward') and bind them to keys. Input queries use
action names, not key constants.
"""
import pygame as pg


class InputManager:
    def __init__(self, bindings=None, mouse_sensitivity=0.0015):
        self._bindings = bindings or {}
        self.mouse_sensitivity = mouse_sensitivity

    def bind(self, action, key):
        """Bind an action name to a pygame key constant."""
        self._bindings[action] = key

    def bind_all(self, bindings):
        """Bind multiple actions from a dict of {action: key}."""
        self._bindings.update(bindings)

    def get_key(self, action):
        """Get the key constant bound to an action."""
        return self._bindings.get(action)

    def is_pressed(self, action, key_state=None):
        """Check if the key for an action is currently held down."""
        key = self._bindings.get(action)
        if key is None:
            return False
        if key_state is None:
            key_state = pg.key.get_pressed()
        return key_state[key]

    def is_action_event(self, event, action):
        """Check if a KEYDOWN event matches an action."""
        if event.type != pg.KEYDOWN:
            return False
        return event.key == self._bindings.get(action)

    def get_mouse_delta(self):
        """Get mouse movement delta, scaled by sensitivity."""
        dx, dy = pg.mouse.get_rel()
        return dx * self.mouse_sensitivity, dy * self.mouse_sensitivity

    @property
    def bindings(self):
        return dict(self._bindings)
