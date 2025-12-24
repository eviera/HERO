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
MAX_FALL_SPEED = 400  # Velocidad máxima de caída
LASER_SPEED = 400
ENERGY_DRAIN_PASSIVE = 7  # Energía por segundo (pasivo)
ENERGY_DRAIN_PROPULSOR = 40  # Energía por segundo al volar
MAX_ENERGY = 2550  # Suficiente para jugar un nivel
DYNAMITE_FUSE_TIME = 3.0  # Tiempo antes de explotar
DYNAMITE_EXPLOSION_RADIUS = 80
DEAD_ZONE = 0.15

# Level dimensions - NIVELES VERTICALES
LEVEL_WIDTH = 16  # tiles
LEVEL_HEIGHT = 30  # tiles - 2-3 pantallas de largo

# Viewport (lo que se ve en pantalla)
VIEWPORT_WIDTH = SCREEN_WIDTH
VIEWPORT_HEIGHT = SCREEN_HEIGHT - 64  # Menos el HUD

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

# Scores file
SCORES_FILE = "scores.json"
