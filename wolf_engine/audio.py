"""
AudioManager — manifest-driven sound loading and playback.

Games provide a sound manifest mapping names to file paths and volumes.
Supports round-robin channel assignment, music playback, and positional
audio with distance-based volume falloff.
"""
import pygame as pg
import glm
from wolf_engine.config import MAX_SOUND_CHANNELS


class AudioManager:
    def __init__(self, num_channels=MAX_SOUND_CHANNELS):
        pg.mixer.init()
        pg.mixer.set_num_channels(num_channels)
        self._num_channels = num_channels
        self._channel = 0
        self._sounds = {}

    def load(self, name, file_path, volume=0.5):
        """Load a single sound by name."""
        sound = pg.mixer.Sound(file_path)
        sound.set_volume(volume)
        self._sounds[name] = sound
        return sound

    def load_manifest(self, manifest, base_path=''):
        """
        Load sounds from a manifest dict.

        manifest format: {name: {path: str, volume: float (optional)}}
        """
        for name, info in manifest.items():
            if isinstance(info, str):
                path = info
                volume = 0.5
            else:
                path = info['path']
                volume = info.get('volume', 0.5)
            self.load(name, base_path + path, volume)

    def get(self, name):
        """Get a loaded sound by name."""
        return self._sounds.get(name)

    def play(self, sound_or_name, volume=None):
        """
        Play a sound. Accepts a Sound object or a string name.
        Uses round-robin channel assignment.
        """
        if isinstance(sound_or_name, str):
            sound = self._sounds.get(sound_or_name)
            if sound is None:
                return
        else:
            sound = sound_or_name

        channel = pg.mixer.Channel(self._channel)
        if volume is not None:
            channel.set_volume(volume)
        channel.play(sound)
        self._channel = (self._channel + 1) % self._num_channels

    def play_positional(self, sound_or_name, source_pos, listener_pos,
                        max_dist=20.0, min_volume=0.0):
        """
        Play a sound with volume based on distance from listener.
        """
        if isinstance(source_pos, glm.vec3):
            dist = glm.length(source_pos - listener_pos)
        else:
            dist = glm.length(glm.vec3(source_pos) - glm.vec3(listener_pos))

        if dist >= max_dist:
            return

        volume = max(min_volume, 1.0 - (dist / max_dist))
        self.play(sound_or_name, volume=volume)

    def play_music(self, path, volume=0.1, loop=True):
        """Start background music."""
        pg.mixer.music.load(path)
        pg.mixer.music.set_volume(volume)
        pg.mixer.music.play(-1 if loop else 0)

    def stop_music(self):
        pg.mixer.music.stop()

    def pause_music(self):
        pg.mixer.music.pause()

    def resume_music(self):
        pg.mixer.music.unpause()
