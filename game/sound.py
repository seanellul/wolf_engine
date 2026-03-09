from wolf_engine.audio import AudioManager
from game.texture_id import *


class Sound(AudioManager):
    """Game-specific sound catalogue built on the engine's AudioManager."""

    def __init__(self):
        super().__init__()
        self.path = 'assets/sounds/'
        #
        self.player_attack = {
            ID.KNIFE_0: self.load('player_attack_knife', self.path + 'w_knife.ogg', volume=0.2),
            ID.PISTOL_0: self.load('player_attack_pistol', self.path + 'w_pistol.wav', volume=0.2),
            ID.RIFLE_0: self.load('player_attack_rifle', self.path + 'w_rifle.ogg', volume=0.2),
        }
        #
        self.player_hurt = self.load('player_hurt', self.path + 'p_hurt.ogg')
        #
        self.player_death = self.load('player_death', self.path + 'p_death.ogg')
        #
        self.player_missed = self.load('player_missed', self.path + 'p_missed.wav')
        #
        self.open_door = self.load('open_door', self.path + 'p_open_door.wav', volume=1.0)
        #
        self.pick_up = {
            ID.AMMO: self.load('pick_up_ammo', self.path + 'p_ammo.ogg'),
            ID.MED_KIT: self.load('pick_up_med_kit', self.path + 'p_med_kit.mp3'),
            ID.KEY: self.load('pick_up_key', self.path + 'p_key.wav'),
        }
        self.pick_up[ID.PISTOL_ICON] = self.pick_up[ID.AMMO]
        self.pick_up[ID.RIFLE_ICON] = self.pick_up[ID.AMMO]
        #
        self.enemy_attack = {
            ID.SOLDIER_BLUE_0: self.load('enemy_attack_soldier', self.path + 'n_soldier_attack.mp3', volume=0.8),
            ID.SOLDIER_BROWN_0: self.load('enemy_attack_brown', self.path + 'n_soldier_attack.mp3', volume=0.8),
            ID.RAT_0: self.load('enemy_attack_rat', self.path + 'n_rat_attack.ogg', volume=0.2),
        }
        #
        self.spotted = {
            ID.SOLDIER_BLUE_0: self.load('spotted_blue', self.path + 'n_soldier_spotted.ogg', volume=1.0),
            ID.SOLDIER_BROWN_0: self.load('spotted_brown', self.path + 'n_brown_spotted.ogg', volume=0.8),
            ID.RAT_0: self.load('spotted_rat', self.path + 'n_rat_spotted.ogg', volume=0.5),
        }
        #
        self.death = {
            ID.SOLDIER_BLUE_0: self.load('death_blue', self.path + 'n_blue_death.ogg', volume=0.8),
            ID.SOLDIER_BROWN_0: self.load('death_brown', self.path + 'n_brown_death.ogg', volume=0.8),
            ID.RAT_0: self.load('death_rat', self.path + 'no_sound.mp3', volume=0.0),
        }
        #
        self.play_music(self.path + 'theme.ogg')
