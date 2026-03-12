# H.E.R.O. Remake - Constants
# Game constants shared across all modules

import pygame

# Window dimensions
TILE_SIZE = 32
FPS = 60
RENDER_SCALE = 1.5  # Escala de la superficie de juego al screen final

# Viewport (tamaño visible en tiles)
VIEWPORT_COLS = 16   # tiles visibles horizontalmente
VIEWPORT_ROWS = 8    # tiles visibles verticalmente

# Superficie de juego (lógica interna, sin escalar) - derivada del viewport
GAME_WIDTH = VIEWPORT_COLS * TILE_SIZE             # 512 - ancho del viewport en pixels
GAME_VIEWPORT_HEIGHT = VIEWPORT_ROWS * TILE_SIZE   # 256 - alto del viewport en pixels

# Pantalla final (escalada)
SCREEN_WIDTH = int(GAME_WIDTH * RENDER_SCALE)              # 768
VIEWPORT_HEIGHT = int(GAME_VIEWPORT_HEIGHT * RENDER_SCALE)  # 384
HUD_HEIGHT = 80  # ColecoVision-style HUD height
SCREEN_HEIGHT = VIEWPORT_HEIGHT + HUD_HEIGHT                # 464

# Game constants - FÍSICAS CORRECTAS
GRAVITY = 400  # Gravedad constante (reducida para caída más suave)
PROPULSOR_POWER = 800  # Poder del propulsor (aumentado para facilitar el ascenso)
PLAYER_SPEED_X = 150  # Velocidad horizontal
WALK_STEP_DISTANCE = 16  # Pixeles entre pasos
PLAYER_FOOT_INSET = 8    # Margen interior del hitbox de colision (hitbox = 16px centrado)
MAX_FALL_SPEED = 400  # Velocidad máxima de caída
DIVE_POWER = 600      # Poder de descenso activo (helice invertida)
LASER_SPEED = 500
LASER_COOLDOWN = 0.12         # Segundos entre disparos (~8 disparos/seg)
LASER_WIDTH = 10  # Ancho del láser en pixels
LASER_HEIGHT = 2  # Alto del láser en pixels
ENERGY_DRAIN_IDLE = 15        # Energía por segundo estando quieto
ENERGY_DRAIN_WALKING = 40     # Energía por segundo caminando
ENERGY_DRAIN_FLYING = 200     # Energía por segundo volando
MAX_ENERGY = 2550  # Suficiente para jugar un nivel
DYNAMITE_FUSE_TIME = 1.5  # Tiempo antes de explotar (desde que se suelta)
DYNAMITE_EXPLOSION_RADIUS = 80
DYNAMITE_QUANTITY = 5
DEAD_ZONE = 0.15

# Rocas - destrucción con láser
ROCK_LASER_HITS = 10          # Disparos para destruir una roca
ROCK_DAMAGE_MIDPOINT = 5     # Disparos para estado intermedio (agrietada)

# Enemigos
BAT_SPEED = 60             # Velocidad horizontal del murciélago
BAT_SPEED_SCALE = 0.05     # +5% por nivel
BAT_ANIM_DISTANCE = 8     # Píxeles entre cambios de sprite
SPIDER_SPEED = 30          # Velocidad vertical de la araña
BUG_SPEED = 120            # Velocidad del bicho (se mueve en zona 3x3)
BUG_ANIM_DISTANCE = 8     # Píxeles entre cambios de sprite del bicho
ENEMY_SPEED_VARIATION = 0.05  # ±5% variación aleatoria de velocidad por enemigo

# Víbora (snake)
SNAKE_HIDDEN_TIME = 2.0        # Segundos escondida antes de salir
SNAKE_EMERGE_SPEED = 64        # Píxeles por segundo al salir/entrar
SNAKE_EXTENDED_TIME = 1.5      # Segundos que permanece extendida
SNAKE_KILL_SCORE = 60          # Puntos al matar la víbora

# Cave background dots (pintitas del fondo de caverna)
CAVE_DOT_SIZE = 2  # Tamaño en pixels de las pintitas

# Dimensiones por defecto de nivel (para compatibilidad y editor)
DEFAULT_LEVEL_WIDTH = 16   # tiles
DEFAULT_LEVEL_HEIGHT = 24  # tiles
LEVEL_WIDTH = DEFAULT_LEVEL_WIDTH    # Alias para editor (legacy)
LEVEL_HEIGHT = DEFAULT_LEVEL_HEIGHT  # Alias para editor (legacy)

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

# Tile types (caracter, nombre, color_fallback, puntos al destruir/matar/rescatar)
TILE_TYPES = [
    (' ', 'Aire',       COLOR_BLACK,       0),
    ('#', 'Tierra',     COLOR_GRAY,        20),   # destructible con dinamita
    ('.', 'Suelo',      (100, 70, 50),     0),    # indestructible
    ('G', 'Granito',    (60, 60, 65),      0),    # indestructible
    ('R', 'Rocas',      (180, 170, 160),   25),   # destructible con dinamita/láser
    ('S', 'Start',      COLOR_BLUE,        0),
    ('M', 'Minero',     COLOR_GREEN,       1000), # puntos al rescatar
    ('V', 'Murcielago', COLOR_RED,         70),   # puntos al matar con láser
    ('A', 'Arana',      COLOR_ORANGE,      50),   # puntos al matar con láser
    ('B', 'Bicho',      COLOR_GREEN,       50),   # puntos al matar con láser
    ('<', 'ViboraIzq',  (0, 180, 0),       60),   # víbora que sale hacia la izquierda
    ('>', 'VibDer',     (0, 180, 0),       60),   # víbora que sale hacia la derecha
    ('L', 'Lampara',    (255, 200, 50),    0),
]

# Lookup rápido: caracter → puntos
TILE_SCORES = {t[0]: t[3] for t in TILE_TYPES}

# Puntuación por matar enemigos con explosión (mayor que con láser)
EXPLOSION_KILL_SCORE = 75

# Puntuación por bomba restante al completar nivel
BOMB_REMAINING_SCORE = 50

# Mapeo de tipo de enemigo a caracter de tile
ENEMY_TILE_CHARS = {'bat': 'V', 'spider': 'A', 'bug': 'B', 'snake_left': '<', 'snake_right': '>'}

# Scores file
SCORES_FILE = "scores.json"

# Screens file (niveles del juego)
SCREENS_FILE = "screens.json"

# SID Audio Effects (Commodore 64 emulation)
SID_INTENSITY = 'light'  # 'light', 'medium', o 'heavy'
SID_BITDEPTH = 8         # bits (1-8)
SID_LOWPASS_CUTOFF = 3500  # Hz
SID_DISTORTION = 0.2     # 0.0 - 1.0
