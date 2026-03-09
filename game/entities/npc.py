from settings import *
import random
from game.entities.game_object import GameObject
from game.entities.item import Item
from wolf_engine.collision import CollisionResolver


class NPC(GameObject):
    def __init__(self, level_map, tex_id, x, z):
        super().__init__(level_map, tex_id, x, z)
        self.level_map = level_map
        self.player = self.eng.player
        self.npc_id = tex_id
        #
        self.scale = NPC_SETTINGS[self.npc_id]['scale']
        self.speed = NPC_SETTINGS[self.npc_id]['speed']
        self.size = NPC_SETTINGS[self.npc_id]['size']
        self.attack_dist = NPC_SETTINGS[self.npc_id]['attack_dist']
        self.health = NPC_SETTINGS[self.npc_id]['health']
        self.damage = NPC_SETTINGS[self.npc_id]['damage']
        self.hit_probability = NPC_SETTINGS[self.npc_id]['hit_probability']
        self.drop_item = NPC_SETTINGS[self.npc_id]['drop_item']
        #
        self.anim_periods = NPC_SETTINGS[self.npc_id]['anim_periods']
        self.anim_counter = 0
        self.frame = 0
        self.is_animate = True

        # current state: walk, attack, hurt, death
        self.num_frames, self.state_tex_id = None, None
        self.set_state(state='walk')
        #
        self.is_player_spotted: bool = False
        self.path_to_player: Tuple[int, int] = None
        #
        self.is_alive = True
        self.is_hurt = False
        #
        self.collision = CollisionResolver(radius=self.size)
        self.collision.add_blocker(lambda pos: pos in self.level_map.wall_map)
        self.collision.add_blocker(
            lambda pos: pos in (self.level_map.npc_map.keys() - {self.tile_pos})
        )
        #
        self.play = self.eng.sound.play
        self.sound = self.eng.sound
        #
        self.m_model = self.get_model_matrix()

    def update(self):
        if self.is_hurt:
            self.set_state(state='hurt')
        #
        elif self.health > 0:
            self.ray_to_player()
            self.get_path_to_player()
            #
            if not self.attack():
                self.move_to_player()
        else:
            self.is_alive = False
            self.set_state('death')
        #
        self.animate()
        # set current texture
        self.tex_id = self.state_tex_id + self.frame

    def get_damage(self):
        self.health -= WEAPON_SETTINGS[self.player.weapon_id]['damage']
        self.is_hurt = True
        #
        if not self.is_player_spotted:
            self.is_player_spotted = True

    def attack(self):
        if not self.is_player_spotted:
            return False

        if glm.length(self.player.position.xz - self.pos.xz) > self.attack_dist:
            return False

        dir_to_player = glm.normalize(self.player.position - self.pos)
        #
        if self.eng.ray_casting.run(start_pos=self.pos, direction=dir_to_player):
            self.set_state(state='attack')

            if self.app.sound_trigger:
                self.play(self.sound.enemy_attack[self.npc_id])

            if random.random() < self.hit_probability:
                self.player.health -= self.damage
                #
                self.play(self.sound.player_hurt)
            return True

    def get_path_to_player(self):
        if not self.is_player_spotted:
            return None

        self.path_to_player = self.eng.path_finder.find(
            start_pos=self.tile_pos,
            end_pos=self.player.tile_pos
        )

    def move_to_player(self):
        if not self.path_to_player:
            return None

        # set state
        self.set_state(state='walk')

        # step to player
        dir_vec = glm.normalize(glm.vec2(self.path_to_player) + H_WALL_SIZE - self.pos.xz)
        delta_vec = dir_vec * self.speed * self.app.delta_time

        # collisions
        new_x, new_z = self.collision.resolve(self.pos, delta_vec[0], delta_vec[1])
        self.pos.x = new_x
        self.pos.z = new_z

        # open door
        door_map = self.level_map.door_map
        if self.tile_pos in door_map:
            door = door_map[self.tile_pos]
            if door.is_closed and not door.is_moving:
                door.is_moving = True
                #
                self.play(self.sound.open_door)

        # translate
        self.m_model = self.get_model_matrix()


    def ray_to_player(self):
        if self.is_player_spotted:
            return None

        dir_to_player = glm.normalize(self.player.position - self.pos)
        #
        if self.eng.ray_casting.run(start_pos=self.pos, direction=dir_to_player):
            self.is_player_spotted = True
            #
            self.play(self.sound.spotted[self.npc_id])

    def set_state(self, state):
        self.num_frames = NPC_SETTINGS[self.npc_id]['num_frames'][state]
        self.state_tex_id = NPC_SETTINGS[self.npc_id]['state_tex_id'][state]
        self.frame %= self.num_frames

    def animate(self):
        if not (self.is_animate and self.app.anim_trigger):
            return None

        self.anim_counter += 1
        #
        if self.anim_counter == self.anim_periods:
            self.anim_counter = 0
            self.frame = (self.frame + 1) % self.num_frames
            #
            if self.is_hurt:
                self.is_hurt = False
            #
            elif not self.is_alive and self.frame == self.num_frames - 1:
                self.is_animate = False
                #
                self.to_drop_item()
                #
                self.play(self.eng.sound.death[self.npc_id])

    def to_drop_item(self):
        if self.drop_item is not None:
            self.level_map.item_map[self.tile_pos] = Item(
                self.level_map, self.drop_item, x=self.tile_pos[0], z=self.tile_pos[1]
            )
