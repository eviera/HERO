# H.E.R.O. Remake - Constants
# Game constants shared across all modules

import pygame

# Importar constantes genéricas desde evgamelib (colores, estados)
from evgamelib.constants import (
    COLOR_BLACK, COLOR_WHITE, COLOR_RED, COLOR_GREEN, COLOR_BLUE,
    COLOR_YELLOW, COLOR_ORANGE, COLOR_GRAY, COLOR_MAGENTA,
    STATE_SPLASH, STATE_PLAYING, STATE_GAME_OVER, STATE_ENTERING_NAME,
    STATE_LEVEL_COMPLETE, STATE_DYING,
    DEFAULT_FPS, DEFAULT_DEAD_ZONE,
)

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
SNAKE_BODY_H = 8               # Alto del cuerpo de la víbora en píxeles
SNAKE_HEAD_W = 12              # Ancho de la cabeza de la víbora en píxeles
SNAKE_HEAD_H = 10              # Alto de la cabeza de la víbora en píxeles

# Agua tóxica
TOXIC_WATER_SCROLL_SPEED = 10  # Píxeles por segundo de scroll horizontal

# =====================================================================
# TEXTURAS - Fine tuning de overlays sobre suelo (.) y lava (X)
# Todas las texturas se pre-generan al cargar el nivel.
# Modificar estos valores cambia la apariencia de la caverna.
# =====================================================================

# --- Fondo de caverna (pintitas en el vacío) ---
CAVE_DOT_SIZE = 2             # Tamaño en pixels de cada pintita
CAVE_DOT_DENSITY = 0.002     # Proporción del área total cubierta (0.0005 = sparse, 0.003 = denso)
CAVE_DOT_BRIGHTNESS = [13, 15, 18, 20, 22, 25]  # % del color base para cada variante de punto

# --- Overlay de textura del suelo/lava (negro sobre tiles . y X) ---
# Chevrones (formas de V invertida que dan textura rugosa)
OVERLAY_CHEVRON_PERIOD = 14       # Separación vertical entre filas de chevrones (px)
OVERLAY_CHEVRON_W = (10, 18)     # Ancho de cada chevrón (min, max px)
OVERLAY_CHEVRON_H = (5, 9)       # Altura de cada chevrón (min, max px)
OVERLAY_CHEVRON_THICKNESS = (2, 4)  # Grosor de las líneas del chevrón (min, max px)
OVERLAY_CHEVRON_SPACING = (2, 8) # Espacio horizontal entre chevrones (min, max px)
OVERLAY_CHEVRON_IRREGULARITY = 0.3  # Probabilidad de píxeles extra para irregularidad (0-1)

# Ruido disperso (píxeles negros sueltos sobre el tile)
OVERLAY_NOISE_DENSITY = 0.08     # Probabilidad de pixel negro por posición (0.01=limpio, 0.1=sucio)

# Clusters (grupos de píxeles negros = cavidades pequeñas)
OVERLAY_CLUSTER_COUNT = (2, 5)   # Cantidad de clusters por tile (min, max)
OVERLAY_CLUSTER_SIZE = (2, 5)    # Tamaño de cada cluster en px (min, max)
OVERLAY_CLUSTER_FILL = 0.65      # Probabilidad de llenar cada pixel del cluster (0-1)

# Agujeros grandes (huecos irregulares en el tile)
OVERLAY_BIG_HOLE_COUNT = (1, 3)  # Cantidad por tile (min, max)
OVERLAY_BIG_HOLE_W = (5, 12)     # Ancho del agujero (min, max px)
OVERLAY_BIG_HOLE_H = (4, 8)      # Alto del agujero (min, max px)
OVERLAY_BIG_HOLE_EDGE_SKIP = 0.4 # Probabilidad de omitir pixel en bordes (irregularidad)

# Dientes en bordes expuestos al vacío (dan aspecto irregular a las aristas)
OVERLAY_TEETH_COUNT = (8, 14)    # Cantidad de dientes por borde (min, max)
OVERLAY_TEETH_W = (1, 5)         # Ancho de cada diente (min, max px)
OVERLAY_TEETH_DEPTH = (3, 10)    # Profundidad hacia adentro del tile (min, max px)
OVERLAY_TEETH_BASE_GAP = 0.15    # Probabilidad de hueco en la línea base del borde
OVERLAY_TEETH_BASE_EXTRA = 0.6   # Probabilidad de segunda línea base (más grosor)

# --- Musgo/raíces (overlay verde en bordes de suelo expuestos) ---
MOSS_BASE_H = 2              # Grosor base horizontal (stalactitas/stalagmitas) en px
MOSS_BASE_W = 2              # Grosor base vertical (musgo lateral) en px
MOSS_MAX_DOWN = 14           # Largo máximo de stalactitas (cuelgan del techo) en px
MOSS_MAX_UP = 12             # Largo máximo de stalagmitas (crecen del suelo) en px
MOSS_MAX_SIDE = 10           # Largo máximo de musgo lateral en px
MOSS_BASE_GAP_CHANCE = 0.15  # Probabilidad de hueco en la banda base (0=sólida, 0.3=muy rota)
MOSS_COLOR_VARIATION = 8     # ±variación RGB por pixel (0=uniforme, 15=muy variado)
MOSS_ALPHA_TIP = 80          # Alpha mínimo en la punta (0=invisible, 255=sólido)
MOSS_ALPHA_BASE = 240        # Alpha de la base (cerca del tile)
MOSS_TENDRIL_COUNT = (1, 3)  # Hilos extra que se extienden más allá del dentado (min, max)
MOSS_TENDRIL_LENGTH = (3, 12)  # Largo de cada tendril (min, max px)

# Parámetros del dentado irregular (_jagged_heights)
MOSS_JAG_GAP_CHANCE = 0.25   # Probabilidad de iniciar un gap (zona baja) en el dentado
MOSS_JAG_CLUSTER_LEN = (2, 6)  # Largo de cada cluster de alturas similares (min, max)
MOSS_JAG_PEAK_CHANCE = 0.06  # Probabilidad de pico largo ocasional
MOSS_JAG_PEAK_EXTRA = (4, 10)  # Altura extra del pico sobre la base (min, max px)

# Archivo JSON de parámetros de textura (editables desde el editor)
TEXTURE_PARAMS_FILE = "texture_params.json"

# Constantes que son tuplas (min, max) - se convierten desde listas JSON
TEXTURE_TUPLE_KEYS = {
    'OVERLAY_CHEVRON_W', 'OVERLAY_CHEVRON_H', 'OVERLAY_CHEVRON_THICKNESS',
    'OVERLAY_CHEVRON_SPACING', 'OVERLAY_CLUSTER_COUNT', 'OVERLAY_CLUSTER_SIZE',
    'OVERLAY_BIG_HOLE_COUNT', 'OVERLAY_BIG_HOLE_W', 'OVERLAY_BIG_HOLE_H',
    'OVERLAY_TEETH_COUNT', 'OVERLAY_TEETH_W', 'OVERLAY_TEETH_DEPTH',
    'MOSS_TENDRIL_COUNT', 'MOSS_TENDRIL_LENGTH',
    'MOSS_JAG_CLUSTER_LEN', 'MOSS_JAG_PEAK_EXTRA',
}

def _load_texture_params():
    """Cargar parámetros de textura desde JSON, con fallback a defaults hardcodeados"""
    import json as _json
    import os as _os
    if not _os.path.exists(TEXTURE_PARAMS_FILE):
        return
    try:
        with open(TEXTURE_PARAMS_FILE, 'r', encoding='utf-8') as f:
            data = _json.load(f)
    except Exception:
        return
    g = globals()
    for key, value in data.items():
        if key in g:
            if key in TEXTURE_TUPLE_KEYS and isinstance(value, list):
                g[key] = tuple(value)
            else:
                g[key] = value

_load_texture_params()

# Dimensiones por defecto de nivel (para compatibilidad y editor)
DEFAULT_LEVEL_WIDTH = 16   # tiles
DEFAULT_LEVEL_HEIGHT = 24  # tiles
LEVEL_WIDTH = DEFAULT_LEVEL_WIDTH    # Alias para editor (legacy)
LEVEL_HEIGHT = DEFAULT_LEVEL_HEIGHT  # Alias para editor (legacy)

# Game States (importados desde evgamelib.constants)

# Animación de muerte
DEATH_FLASH_TIME = 0.35       # Segundos de flash blanco inicial (más dramático)
DEATH_SKELETON_TIME = 1.0     # Segundos mostrando el esqueleto
DEATH_ANIM_TIME = DEATH_FLASH_TIME + DEATH_SKELETON_TIME  # Total

# Animación de hélice del helicóptero
PROPELLER_SLOW_SPEED = 5.0    # Ciclos por segundo (idle/caminando)
PROPELLER_FAST_SPEED = 20.0   # Ciclos por segundo (volando)
PROPELLER_NUM_FRAMES = 4      # Frames de rotación
PROPELLER_WIDTH_FACTORS = [1.0, 0.65, 0.15, 0.65]  # Factor de ancho por frame

# Colors (importados desde evgamelib.constants)

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
    ('X', 'Lava',       (200, 80, 30),     0,    True),   # indestructible, mata al contacto
    ('W', 'RocaLava',   (180, 100, 40),    30,   True),   # destructible con dinamita/láser
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

# Helpers para mapas jagged (re-exportados desde evgamelib.tilemap)
from evgamelib.tilemap import band_width, row_width, max_level_width
