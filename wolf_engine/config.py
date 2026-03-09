import math
import glm
import pygame as pg

# opengl
MAJOR_VERSION = 3
MINOR_VERSION = 3
DEPTH_SIZE = 24

# resolution
WIN_RES = glm.vec2(1280, 720)

# camera
ASPECT_RATIO = WIN_RES.x / WIN_RES.y
FOV_DEG = 50
V_FOV = glm.radians(FOV_DEG)  # vertical FOV
H_FOV = 2 * math.atan(math.tan(V_FOV * 0.5) * ASPECT_RATIO)  # horizontal FOV
NEAR = 0.01
FAR = 2000.0
PITCH_MAX = glm.radians(89)

# input
MOUSE_SENSITIVITY = 0.0015
KEYS = {
    'FORWARD': pg.K_w,
    'BACK': pg.K_s,
    'UP': pg.K_q,
    'DOWN': pg.K_e,
    'STRAFE_L': pg.K_a,
    'STRAFE_R': pg.K_d,
    'INTERACT': pg.K_f,
    'WEAPON_1': pg.K_1,
    'WEAPON_2': pg.K_2,
    'WEAPON_3': pg.K_3,
}

# textures
TEX_SIZE = 256
TEXTURE_UNIT_0 = 0

# walls
WALL_SIZE = 1
H_WALL_SIZE = WALL_SIZE / 2

# timer
SYNC_PULSE = 10  # ms

# ray casting
MAX_RAY_DIST = 20

# sound
MAX_SOUND_CHANNELS = 10

# colors
BG_COLOR = glm.vec3(0.1, 0.16, 0.25)
