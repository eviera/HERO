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
GRAVITY = 200  # Gravedad constante (reducida para caída más suave)
PROPULSOR_POWER = 600  # Poder del propulsor (potencia máxima)
PROPULSOR_WARMUP_TIME = 0.5  # Segundos hasta poder ascender a velocidad completa
PROPULSOR_MAX_ASCENT_INITIAL = 0  # Velocidad máxima de ascenso al arrancar (casi nada)
PROPULSOR_MAX_ASCENT_FULL = 400  # Velocidad máxima de ascenso a potencia completa
PLAYER_SPEED_X = 150  # Velocidad horizontal
WALK_STEP_DISTANCE = 16  # Pixeles entre pasos
PLAYER_FOOT_INSET = 8    # Margen interior del hitbox de colision (hitbox = 16px centrado)
MAX_FALL_SPEED = 400  # Velocidad máxima de caída
DIVE_POWER = 400      # Poder de descenso activo (helice invertida)
LASER_SPEED = 600
LASER_COOLDOWN = 0.12         # Segundos entre disparos (~8 disparos/seg)
LASER_WIDTH = 10  # Ancho del láser en pixels
LASER_HEIGHT = 2  # Alto del láser en pixels
ENERGY_DRAIN_IDLE = 15        # Energía por segundo estando quieto
ENERGY_DRAIN_WALKING = 40     # Energía por segundo caminando
ENERGY_DRAIN_FLYING = 150     # Energía por segundo volando
MAX_ENERGY = 3000  # Suficiente para jugar un nivel
DYNAMITE_FUSE_TIME = 1.5  # Tiempo antes de explotar (desde que se suelta)
DYNAMITE_EXPLOSION_RADIUS = 64
DYNAMITE_QUANTITY = 5
INITIAL_LIVES = 3
MAX_LIVES = 3
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

# Agua tóxica
TOXIC_WATER_SCROLL_SPEED = 10  # Píxeles por segundo de scroll horizontal

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
STATE_DYING = "dying"

# Animación de muerte
DEATH_FLASH_TIME = 0.35       # Segundos de flash blanco inicial (más dramático)
DEATH_SKELETON_TIME = 1.0     # Segundos mostrando el esqueleto
DEATH_ANIM_TIME = DEATH_FLASH_TIME + DEATH_SKELETON_TIME  # Total

# Animación de hélice del helicóptero
PROPELLER_SLOW_SPEED = 5.0    # Ciclos por segundo (idle/caminando)
PROPELLER_FAST_SPEED = 20.0   # Ciclos por segundo (volando)
PROPELLER_NUM_FRAMES = 4      # Frames de rotación
PROPELLER_WIDTH_FACTORS = [1.0, 0.65, 0.15, 0.65]  # Factor de ancho por frame

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

# Tile types (caracter, nombre, color_fallback, puntos, sólido)
TILE_TYPES = [
    (' ', 'Aire',       COLOR_BLACK,       0,    False),
    ('#', 'Tierra',     COLOR_GRAY,        20,   True),   # destructible con dinamita
    ('.', 'Suelo',      (100, 70, 50),     0,    True),   # indestructible
    ('G', 'Granito',    (60, 60, 65),      0,    True),   # indestructible
    ('R', 'Rocas',      (180, 170, 160),   25,   True),   # destructible con dinamita/láser
    ('S', 'Start',      COLOR_BLUE,        0,    False),
    ('M', 'Minero',     COLOR_GREEN,       1000, False),  # puntos al rescatar
    ('V', 'Murcielago', COLOR_RED,         70,   False),  # puntos al matar con láser
    ('A', 'Arana',      COLOR_ORANGE,      50,   False),  # puntos al matar con láser
    ('B', 'Bicho',      COLOR_GREEN,       50,   False),  # puntos al matar con láser
    ('<', 'ViboraIzq',  (0, 180, 0),       60,   False),  # víbora que sale hacia la izquierda
    ('>', 'VibDer',     (0, 180, 0),       60,   False),  # víbora que sale hacia la derecha
    ('L', 'Lampara',    (255, 200, 50),    0,    False),
    ('~', 'AguaToxica', (30, 120, 40),     0,    False),  # mata al jugador al contacto
]

# Lookup rápido: caracter → puntos
TILE_SCORES = {t[0]: t[3] for t in TILE_TYPES}

# Tiles sólidos (para colisiones y detección de bordes)
SOLID_TILES = {t[0] for t in TILE_TYPES if t[4]}

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

# Helpers para mapas jagged (bandas de viewport con ancho independiente)

def band_width(level_map, tile_row):
    """Ancho en tiles de la banda de viewport que contiene tile_row"""
    if not level_map:
        return DEFAULT_LEVEL_WIDTH
    if tile_row < 0:
        return len(level_map[0])
    band_start = (tile_row // VIEWPORT_ROWS) * VIEWPORT_ROWS
    if band_start < len(level_map):
        return len(level_map[band_start])
    return VIEWPORT_COLS

def row_width(level_map, tile_row):
    """Ancho en tiles de una fila específica"""
    if not level_map or tile_row < 0 or tile_row >= len(level_map):
        return 0
    return len(level_map[tile_row])

def max_level_width(level_map):
    """Ancho máximo entre todas las filas del mapa"""
    return max(len(row) for row in level_map) if level_map else 0
