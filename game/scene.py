from wolf_engine.rendering.render_scene import RenderScene
from wolf_engine.rendering.meshes.level_mesh import LevelMesh
from wolf_engine.rendering.meshes.instanced_quad_mesh import InstancedQuadMesh
from game.entities.hud import HUD
from game.entities.weapon import Weapon
from wolf_engine.rendering.meshes.weapon_mesh import WeaponMesh


class Scene:
    def __init__(self, eng):
        self.eng = eng

        # entity collections
        self.hud = HUD(eng)
        self.doors = self.eng.level_map.door_map.values()
        self.items = self.eng.level_map.item_map.values()
        self.npc = self.eng.level_map.npc_map.values()
        self.weapon = Weapon(eng)

        # build meshes
        level_mesh = LevelMesh(eng)
        door_mesh = InstancedQuadMesh(
            eng, self.doors, eng.shader_program.instanced_door
        )
        item_mesh = InstancedQuadMesh(
            eng, self.items, eng.shader_program.instanced_billboard
        )
        hud_mesh = InstancedQuadMesh(
            eng, self.hud.objects, eng.shader_program.instanced_hud
        )
        npc_mesh = InstancedQuadMesh(
            eng, self.npc, eng.shader_program.instanced_billboard
        )
        weapon_mesh = WeaponMesh(eng, eng.shader_program.weapon, self.weapon)

        # register render layers in order
        self.render_scene = RenderScene()
        self.render_scene.add_layer('level').add(level_mesh)
        self.render_scene.add_layer('doors').add(door_mesh)
        self.render_scene.add_layer('items').add(item_mesh)
        self.render_scene.add_layer('hud').add(hud_mesh)
        self.render_scene.add_layer('npcs').add(npc_mesh)
        self.render_scene.add_layer('weapon').add(weapon_mesh)

    def update(self):
        for door in self.doors:
            door.update()
        for npc in self.npc:
            npc.update()
        self.hud.update()
        self.weapon.update()

    def render(self):
        self.render_scene.render_all()
