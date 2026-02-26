# H.E.R.O. Remake - Constants
# Game constants shared across all modules

import pygame

# Window dimensions
SCREEN_WIDTH = 512
SCREEN_HEIGHT = 480
FPS = 60
TILE_SIZE = 32

# Game constants - FÍSICAS CORRECTAS
GRAVITY = 400  # Gravedad constante (reducida para caída más suave)
PROPULSOR_POWER = 800  # Poder del propulsor (aumentado para facilitar el ascenso)
PLAYER_SPEED_X = 150  # Velocidad horizontal
WALK_STEP_DISTANCE = 16  # Pixeles entre pasos
MAX_FALL_SPEED = 400  # Velocidad máxima de caída
DIVE_POWER = 600      # Poder de descenso activo (helice invertida)
LASER_SPEED = 400
LASER_WIDTH = 10  # Ancho del láser en pixels
LASER_HEIGHT = 2  # Alto del láser en pixels
ENERGY_DRAIN_PROPULSOR = 400  # Energía por segundo al volar 
ENERGY_RECOVERY = 300         # Energía recuperada por segundo en el suelo
MAX_ENERGY = 2550  # Suficiente para jugar un nivel
DYNAMITE_FUSE_TIME = 1.5  # Tiempo antes de explotar (desde que se suelta)
DYNAMITE_EXPLOSION_RADIUS = 80
DYNAMITE_QUANTITY = 5
DEAD_ZONE = 0.15

# Enemigos
BAT_SPEED = 60             # Velocidad horizontal del murciélago
BAT_SPEED_SCALE = 0.05     # +5% por nivel
BAT_ANIM_DISTANCE = 8     # Píxeles entre cambios de sprite
SPIDER_SPEED = 30          # Velocidad vertical de la araña
ENEMY_SPEED_VARIATION = 0.05  # ±5% variación aleatoria de velocidad por enemigo

# Cave background dots (pintitas del fondo de caverna)
CAVE_DOT_SIZE = 2  # Tamaño en pixels de las pintitas

# Level dimensions - NIVELES VERTICALES
LEVEL_WIDTH = 16  # tiles
LEVEL_HEIGHT = 30  # tiles - 2-3 pantallas de largo

# Viewport (lo que se ve en pantalla)
VIEWPORT_WIDTH = SCREEN_WIDTH
HUD_HEIGHT = 80  # ColecoVision-style HUD height
VIEWPORT_HEIGHT = SCREEN_HEIGHT - HUD_HEIGHT  # Menos el HUD

# Game States
STATE_SPLASH = "splash"
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_ENTERING_NAME = "entering_name"
STATE_LEVEL_COMPLETE = "level_complete"

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 100, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_ORANGE = (255, 165, 0)
COLOR_GRAY = (128, 128, 128)
COLOR_MAGENTA = (255, 0, 255)

# Tile types (caracter, nombre, color_fallback)
TILE_TYPES = [
    (' ', 'Aire',       COLOR_BLACK),
    ('#', 'Pared',      COLOR_GRAY),
    ('.', 'Suelo',      (100, 70, 50)),
    ('B', 'Bloque',     COLOR_MAGENTA),
    ('W', 'Rompible',   (180, 170, 160)),
    ('S', 'Start',      COLOR_BLUE),
    ('M', 'Minero',     COLOR_GREEN),
    ('V', 'Murcielago', COLOR_RED),
    ('A', 'Arana',      COLOR_ORANGE),
]

# Scores file
SCORES_FILE = "scores.json"

# Screens file (niveles del juego)
SCREENS_FILE = "screens.json"

# SID Audio Effects (Commodore 64 emulation)
SID_INTENSITY = 'light'  # 'light', 'medium', o 'heavy'
SID_BITDEPTH = 8         # bits (1-8)
SID_LOWPASS_CUTOFF = 3500  # Hz
SID_DISTORTION = 0.2     # 0.0 - 1.0
