"""
RenderScene — ordered render layer system.

Replaces hardcoded render order with named layers that games can
populate. Layers render in registration order.
"""
from collections import OrderedDict


class RenderLayer:
    """A single render layer containing renderable objects."""

    def __init__(self, name):
        self.name = name
        self._renderables = []

    def add(self, renderable):
        """Add a renderable (anything with a .render() method)."""
        self._renderables.append(renderable)

    def remove(self, renderable):
        self._renderables.remove(renderable)

    def clear(self):
        self._renderables.clear()

    def render(self):
        for r in self._renderables:
            r.render()

    def __len__(self):
        return len(self._renderables)


class RenderScene:
    """
    Manages named render layers in a fixed order.

    Usage:
        scene = RenderScene()
        scene.add_layer('level')
        scene.add_layer('world_sprites')
        scene.add_layer('hud')
        scene.add_layer('weapon')

        scene['level'].add(level_mesh)
        scene['world_sprites'].add(door_mesh)
        scene['world_sprites'].add(npc_mesh)

        scene.render_all()  # renders layers in registration order
    """

    def __init__(self):
        self._layers = OrderedDict()

    def add_layer(self, name):
        """Register a new render layer. Layers render in registration order."""
        if name not in self._layers:
            self._layers[name] = RenderLayer(name)
        return self._layers[name]

    def __getitem__(self, name):
        return self._layers[name]

    def __contains__(self, name):
        return name in self._layers

    def render_all(self):
        """Render all layers in order."""
        for layer in self._layers.values():
            layer.render()

    def clear_all(self):
        """Clear all renderables from all layers."""
        for layer in self._layers.values():
            layer.clear()

    @property
    def layer_names(self):
        return list(self._layers.keys())
