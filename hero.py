# H.E.R.O. Remake - CORRECTO basado en Atari 2600
# Helicopter Emergency Rescue Operation

import pygame
import json
import os
import math
import array
import random
import argparse

# Import constants
from constants import *

# Import game classes
from laser import Laser
from dynamite import Dynamite
from enemy import Enemy
from miner import Miner
from player import Player
try:
    from evgamelib.audio_effects import apply_sid_to_sound
except ImportError:
    apply_sid_to_sound = None
from palette import (get_depth_palette, get_edge_color, build_tinted_floors,
                      draw_tile_edges, generate_edge_overlay,
                      generate_floor_texture)
from evgamelib.scores import HighScoreManager
from evgamelib.text import draw_text_with_outline as _draw_text_with_outline, FloatingTextManager
from evgamelib.sound_manager import SoundManager
from evgamelib.input_manager import InputManager
from evgamelib.collision import mask_overlap
from evgamelib.camera import SnapCamera
from evgamelib.rendering import RenderPipeline

##################################################################################################
# Utility Functions
##################################################################################################

# High score manager (evgamelib)
_score_manager = HighScoreManager(SCORES_FILE)

def load_scores():
    """Load high scores from JSON file"""
    return _score_manager.load()

def save_scores(scores):
    """Save high scores to JSON file"""
    _score_manager.save(scores)

def add_score(name, score):
    """Add a new score and keep only top 10"""
    return _score_manager.add(name, score)

##################################################################################################
# Level Generator
##################################################################################################
# Niveles cargados desde screens.json
# Leyenda:
#   S = Start (jugador)
#   M = Miner (persona a rescatar)
#   V = Enemy bat (murciélago)
#   A = Spider (araña)
#   B = Bug (bicho)
#   < = Snake left (víbora que sale a la izquierda)
#   > = Snake right (víbora que sale a la derecha)
#   # = Pared sólida
#   . = Suelo/plataforma
#   (espacio) = Aire

def load_levels_from_file():
    """Cargar niveles desde screens.json (tamaño dinámico, múltiplos del viewport)"""
    global LEVEL_PALETTES, LEVEL_EDGE_COLORS
    if os.path.exists(SCREENS_FILE):
        try:
            with open(SCREENS_FILE, 'r', encoding='utf-8') as f:
                screens = json.load(f)
                levels = []
                LEVEL_PALETTES = []
                LEVEL_EDGE_COLORS = []
                for s in screens:
                    LEVEL_PALETTES.append(get_depth_palette(s))
                    LEVEL_EDGE_COLORS.append(get_edge_color(s))
                    level_map = s["map"]
                    # Determinar altura del mapa
                    map_height = len(level_map)

                    # Redondear hacia arriba al múltiplo del viewport más cercano
                    target_h = max(VIEWPORT_ROWS, ((map_height + VIEWPORT_ROWS - 1) // VIEWPORT_ROWS) * VIEWPORT_ROWS)

                    # Normalizar altura total a múltiplo de VIEWPORT_ROWS
                    while len(level_map) < target_h:
                        level_map.append('#' * VIEWPORT_COLS)

                    # Normalizar por banda: cada grupo de VIEWPORT_ROWS filas
                    # tiene su propio ancho (múltiplo de VIEWPORT_COLS)
                    normalized = []
                    for band_start in range(0, target_h, VIEWPORT_ROWS):
                        band_end = min(band_start + VIEWPORT_ROWS, len(level_map))
                        band_rows = level_map[band_start:band_end]
                        band_w = max(len(r) for r in band_rows) if band_rows else VIEWPORT_COLS
                        target_band_w = max(VIEWPORT_COLS, ((band_w + VIEWPORT_COLS - 1) // VIEWPORT_COLS) * VIEWPORT_COLS)
                        for row in band_rows:
                            if len(row) < target_band_w:
                                row = row + '#' * (target_band_w - len(row))
                            normalized.append(row[:target_band_w])
                        # Completar filas faltantes de la banda
                        while len(normalized) < band_start + VIEWPORT_ROWS:
                            normalized.append('#' * target_band_w)
                    levels.append(normalized[:target_h])
                return levels
        except Exception as e:
            print(f"Error cargando niveles: {e}")
    return []

LEVEL_PALETTES = []  # Paletas de profundidad por nivel
LEVEL_EDGE_COLORS = []  # Color de borde por nivel
LEVELS = load_levels_from_file()

def get_level_palette(level_num):
    """Obtener paleta de profundidad para un nivel"""
    if level_num < 0 or level_num >= len(LEVEL_PALETTES):
        return []
    return LEVEL_PALETTES[level_num]

def get_level_edge_color(level_num):
    """Obtener color de borde para un nivel"""
    from palette import DEFAULT_EDGE_COLOR
    if level_num < 0 or level_num >= len(LEVEL_EDGE_COLORS):
        return list(DEFAULT_EDGE_COLOR)
    return LEVEL_EDGE_COLORS[level_num]

def generate_level(level_num):
    """Return a level loaded from screens.json"""
    if len(LEVELS) == 0:
        print("ERROR: No se encontraron niveles en screens.json")
        # Nivel de emergencia
        empty = ['#' * DEFAULT_LEVEL_WIDTH] * DEFAULT_LEVEL_HEIGHT
        return list(empty)
    if level_num < 0 or level_num >= len(LEVELS):
        level_num = 0
    # Devolver copia para no modificar el nivel original
    return list(LEVELS[level_num])

##################################################################################################
# Game Class
##################################################################################################
class Game:
    def __init__(self):
        self.screen = None
        self.clock = None
        self.input_manager = InputManager(dead_zone=DEAD_ZONE)
        self.xbox_controller = None  # alias legacy
        self.tiles = {}
        self.sprites = {}
        self.sound_manager = SoundManager()
        self.sounds = self.sound_manager.sounds  # acceso directo al dict
        self.background_image = None
        self.gray_overlay = None
        self.font = None
        self.small_font = None
        self.hud_font = None
        self.hud_player_icon = None
        self.hud_bomb_icon = None

        # Game state
        self.state = STATE_SPLASH
        self.score = 0
        self.level_num = 0
        self.lives = INITIAL_LIVES
        self.dynamite_count = DYNAMITE_QUANTITY
        self.energy = MAX_ENERGY

        # Level data
        self.level_map = []

        # Entities
        self.player = None
        self.enemies = []
        self.lasers = []
        self.dynamites = []
        self.miner = None

        # Cave background
        self.cave_bg = None
        self.edge_overlay = None
        self.floor_texture = None

        # Camera (evgamelib)
        self._camera = SnapCamera(GAME_WIDTH, GAME_VIEWPORT_HEIGHT, TILE_SIZE)
        self.camera_x = 0
        self.camera_y = 0

        # Input (accesos directos al input_manager)
        self.keys = self.input_manager.keys
        self.joy_axis_x = 0
        self.joy_axis_y = 0

        # Timers
        self.shoot_cooldown = 0
        self.level_complete_timer = 0

        # Sound state (gestionado por sound_manager)

        # Quit confirmation
        self.show_quit_confirm = False

        # Rendering pipeline (evgamelib)
        self._render_pipeline = RenderPipeline(GAME_WIDTH, GAME_VIEWPORT_HEIGHT, RENDER_SCALE, HUD_HEIGHT)
        self.fullscreen = False
        self.display_surface = None
        self.render_scale = 1.0
        self.render_w = SCREEN_WIDTH
        self.render_h = SCREEN_HEIGHT
        self.render_x = 0
        self.render_y = 0

        # Name entry
        self.player_name = ""
        self.is_victory = False
        self.victory_palette_offset = 0  # Para ciclar colores en VICTORY!

        # Paleta de 256 colores estilo VGA (6-8-5 levels RGB para retro feel)
        self._victory_palette = []
        for i in range(256):
            if i < 64:
                # Rojo a amarillo
                r = 255
                g = i * 4
                b = 0
            elif i < 128:
                # Amarillo a verde
                r = 255 - (i - 64) * 4
                g = 255
                b = 0
            elif i < 192:
                # Verde a cyan a azul
                r = 0
                g = 255 - (i - 128) * 4
                b = (i - 128) * 4
            else:
                # Azul a magenta a rojo
                r = (i - 192) * 4
                g = 0
                b = 255 - (i - 192) * 4
            # Clampar a 0-255
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            self._victory_palette.append((r, g, b))

        # Score tracking
        self.last_life_score = 0

        # Explosion flash effect
        self.explosion_flash = False
        self.explosion_flash_timer = 0

        # Floating score texts (evgamelib)
        self.floating_scores_mgr = FloatingTextManager()

        # Level complete animation (ColecoVision style)
        self.level_complete_phase = 0     # 0=energy drain, 1=bombs, 2=display
        self.bomb_explosion_effects = []  # Efectos activos de explosion en HUD
        self.score_beep_timer = 0         # Timer entre beeps
        self.score_beep_initial_energy = 0  # Energia inicial para calcular proporcion de beeps
        self.bomb_explode_timer = 0       # Timer entre explosiones de bombas
        self.score_beeps = []             # Beep sounds pre-generados

        # Lampara / modo oscuridad
        self.dark_mode = False
        self.lamps = []                   # Lista de posiciones {x, y} de lamparas
        self._grayscale_cache = {}        # Cache de sprites en escala de gris

    def init(self):
        """Initialize pygame and resources"""
        pygame.init()
        pygame.mixer.init()

        # Initialize joysticks (via InputManager)
        self.input_manager.init_controllers()
        self.xbox_controller = self.input_manager.controller  # alias legacy

        # Inicializar rendering pipeline
        self._render_pipeline.init_display(fullscreen=True)
        self.fullscreen = self._render_pipeline.fullscreen
        self.display_surface = self._render_pipeline.display_surface
        self.screen = self._render_pipeline.screen
        self.game_surface = self._render_pipeline.game_surface
        self._scaled_game = self._render_pipeline._scaled_game
        self.render_scale = self._render_pipeline.render_scale
        self.render_w = self._render_pipeline.render_w
        self.render_h = self._render_pipeline.render_h
        self.render_x = self._render_pipeline.render_x
        self.render_y = self._render_pipeline.render_y
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("H.E.R.O. - Atari 2600 Remake")
        try:
            icon = pygame.image.load("sprites/player_fly.png").convert_alpha()
            icon = pygame.transform.flip(icon, True, False)  # Mirar a la derecha
            pygame.display.set_icon(icon)
        except:
            pass

        # Load fonts
        try:
            self.font = pygame.font.Font("fonts/PressStart2P-vaV7.ttf", 16)
            self.small_font = pygame.font.Font("fonts/PressStart2P-vaV7.ttf", 13)
        except:
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 16)

        # HUD font (ColecoVision style, smaller)
        try:
            self.hud_font = pygame.font.Font("fonts/PressStart2P-vaV7.ttf", 12)
        except:
            self.hud_font = pygame.font.Font(None, 16)

        # Load tiles
        try:
            self.tiles['wall'] = pygame.image.load("tiles/wall.png").convert_alpha()
            self.tiles['floor'] = pygame.image.load("tiles/floor.png").convert_alpha()
            self.tiles['blank'] = pygame.image.load("tiles/blank.png").convert_alpha()
        except Exception as e:
            print(f"Error loading tiles: {e}")
            # Create fallback tiles
            self.tiles['wall'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['wall'].fill(COLOR_GRAY)
            self.tiles['floor'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['floor'].fill((100, 70, 50))
            self.tiles['blank'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['blank'].fill(COLOR_BLACK)

        # Granite tile (G) - indestructible
        try:
            self.tiles['granite'] = pygame.image.load("tiles/granite.png").convert_alpha()
        except:
            self.tiles['granite'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['granite'].fill((60, 60, 65))

        # Breakable wall tile (W)
        try:
            self.tiles['rock'] = pygame.image.load("tiles/breakable_wall.png").convert_alpha()
        except:
            self.tiles['rock'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['rock'].fill((180, 170, 160))

        # Roca dañada (estado intermedio por impactos de láser)
        try:
            self.tiles['rock_damaged'] = pygame.image.load("tiles/broken_wall.png").convert_alpha()
        except:
            self.tiles['rock_damaged'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['rock_damaged'].fill((140, 130, 120))

        # Toxic water tile (~) - agua tóxica verde animada (strip de frames)
        try:
            strip = pygame.image.load("tiles/toxic_water_strip.png").convert_alpha()
            self.toxic_water_frames = []
            num_frames = strip.get_width() // TILE_SIZE
            for i in range(num_frames):
                frame = strip.subsurface(pygame.Rect(i * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))
                self.toxic_water_frames.append(frame)
        except:
            # Fallback: un solo frame sólido
            fallback = pygame.Surface((TILE_SIZE, TILE_SIZE))
            fallback.fill((30, 120, 40))
            self.toxic_water_frames = [fallback]
        self.tiles['toxic_water'] = self.toxic_water_frames[0]
        self.toxic_water_scroll = 0.0

        # Lava tile (X) - indestructible, mata al contacto
        try:
            self.tiles['lava'] = pygame.image.load("tiles/lava.png").convert_alpha()
        except:
            self.tiles['lava'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['lava'].fill((200, 80, 30))

        # Lava rock tiles (W) - destructibles, tintados color lava
        try:
            self.tiles['lava_rock'] = pygame.image.load("tiles/lava_breakable_wall.png").convert_alpha()
        except:
            self.tiles['lava_rock'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['lava_rock'].fill((180, 100, 40))
        try:
            self.tiles['lava_rock_damaged'] = pygame.image.load("tiles/lava_broken_wall.png").convert_alpha()
        except:
            self.tiles['lava_rock_damaged'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['lava_rock_damaged'].fill((140, 70, 30))

        # Lamp tile (L) - lampara dorada
        try:
            self.tiles['lamp'] = pygame.image.load("tiles/lamp.png").convert_alpha()
        except:
            # Fallback: circulo amarillo dorado
            self.tiles['lamp'] = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(self.tiles['lamp'], (255, 200, 50),
                             (TILE_SIZE // 2, TILE_SIZE // 2), TILE_SIZE // 3)
            pygame.draw.circle(self.tiles['lamp'], (255, 240, 100),
                             (TILE_SIZE // 2, TILE_SIZE // 2 - 2), TILE_SIZE // 5)
        # Calcular bounding box de pixeles no transparentes para colision precisa
        lamp_mask = pygame.mask.from_surface(self.tiles['lamp'])
        bounding = lamp_mask.get_bounding_rects()
        if bounding:
            # Unir todos los rects del mask en uno solo
            self.lamp_hit_rect = bounding[0].unionall(bounding[1:]) if len(bounding) > 1 else bounding[0]
        else:
            self.lamp_hit_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)

        # Load sprites
        try:
            self.sprites['player'] = pygame.image.load("sprites/player.png").convert_alpha()
            self.sprites['player_shooting'] = pygame.image.load("sprites/player_shooting.png").convert_alpha()
            self.sprites['player_walk1'] = pygame.image.load("sprites/player_walk1.png").convert_alpha()
            self.sprites['player_walk2'] = pygame.image.load("sprites/player_walk2.png").convert_alpha()
            self.sprites['player_fly'] = pygame.image.load("sprites/player_fly.png").convert_alpha()
            self.sprites['bat1'] = pygame.image.load("sprites/bat1.png").convert_alpha()
            self.sprites['bat2'] = pygame.image.load("sprites/bat2.png").convert_alpha()
            self.sprites['spider'] = pygame.image.load("sprites/spider.png").convert_alpha()
            self.sprites['bug1'] = pygame.image.load("sprites/bug1.png").convert_alpha()
            self.sprites['bug2'] = pygame.image.load("sprites/bug2.png").convert_alpha()
            self.sprites['bug3'] = pygame.image.load("sprites/bug3.png").convert_alpha()
            self.sprites['bug4'] = pygame.image.load("sprites/bug4.png").convert_alpha()
            self.sprites['bomb1'] = pygame.image.load("sprites/bomb1.png").convert_alpha()
            self.sprites['bomb2'] = pygame.image.load("sprites/bomb2.png").convert_alpha()
            self.sprites['bomb3'] = pygame.image.load("sprites/bomb3.png").convert_alpha()
            self.sprites['miner'] = pygame.image.load("sprites/miner.png").convert_alpha()
            self.sprites['snake_head'] = pygame.image.load("sprites/snake_head.png").convert_alpha()
            self.sprites['snake_neck'] = pygame.image.load("sprites/snake_neck.png").convert_alpha()
            # Generar sprite de esqueleto a partir del sprite del player
            self.sprites['skeleton'] = self._generate_skeleton_sprite(self.sprites['player'])
            # Preparar animación de hélice (separar palas del cuerpo)
            self._prepare_propeller_sprites()
            print("Sprites loaded successfully")
        except Exception as e:
            print(f"Error loading sprites: {e}")

        # Precomputar masks de sprites para colisiones pixel-perfect
        self.masks = {}
        # Sprites que necesitan versión flipped (solo player, sprite base mira a la izquierda)
        player_mask_keys = ['player', 'player_fly', 'player_shooting', 'player_walk1', 'player_walk2']
        for key in player_mask_keys:
            if key in self.sprites:
                self.masks[key] = pygame.mask.from_surface(self.sprites[key])
                self.masks[key + '_flip'] = pygame.mask.from_surface(
                    pygame.transform.flip(self.sprites[key], True, False))
        # Sprites sin flip
        for key in ['bat1', 'bat2', 'spider', 'miner']:
            if key in self.sprites:
                self.masks[key] = pygame.mask.from_surface(self.sprites[key])
        # Bug: mask directa (bicho volante no rota, hitbox = parte coloreada)
        for bug_key in ['bug1', 'bug2', 'bug3', 'bug4']:
            if bug_key in self.sprites:
                self.masks[bug_key] = pygame.mask.from_surface(self.sprites[bug_key])

        # Mask del láser (rect sólido pequeño, precomputado)
        laser_surf = pygame.Surface((LASER_WIDTH, LASER_HEIGHT), pygame.SRCALPHA)
        laser_surf.fill((255, 255, 255))
        self.laser_mask = pygame.mask.from_surface(laser_surf)

        # Precomputar hit rect de agua tóxica (bounding box de píxeles visibles)
        if self.toxic_water_frames:
            tw_mask = pygame.mask.from_surface(self.toxic_water_frames[0])
            tw_bounding = tw_mask.get_bounding_rects()
            if tw_bounding:
                self.toxic_water_hit_rect = tw_bounding[0].unionall(tw_bounding[1:]) if len(tw_bounding) > 1 else tw_bounding[0]
            else:
                self.toxic_water_hit_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        else:
            self.toxic_water_hit_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)

        # Crear mini-iconos para el HUD (ColecoVision style)
        if 'player_fly' in self.sprites:
            self.hud_player_icon = pygame.transform.scale(self.sprites['player_fly'], (16, 16))
        if 'bomb1' in self.sprites:
            self.hud_bomb_icon = pygame.transform.scale(self.sprites['bomb1'], (16, 16))

        # Load sounds (via SoundManager)
        try:
            sm = self.sound_manager
            sm.load('shoot', "sounds/shoot.wav")
            sm.load('explosion', "sounds/explosion.wav")
            sm.load('death', "sounds/death.wav")
            sm.load('splatter', "sounds/splatter.wav")
            sm.load('helicopter', "sounds/helicopter.wav")
            sm.load('walk1', "sounds/walk1.wav")
            sm.load('walk2', "sounds/walk2.wav")
            sm.load('win_screen', "sounds/win_screen.wav")
            sm.load('rock_break', "sounds/rock_break.wav")
            sm.load('rock_crack', "sounds/rock_crack.wav")
            sm.load('death_song', "sounds/death_song.wav")
            sm.load('splash_theme', "sounds/splash_screen_theme.wav")

            print("Sounds loaded successfully")
        except Exception as e:
            print(f"Error loading sounds: {e}")
            
        # Splash: se renderiza a 512x480 (tamaño original) y se pega centrado en screen
        self._splash_w, self._splash_h = 512, 480
        self.splash_surface = pygame.Surface((self._splash_w, self._splash_h))

        # Load background image (al tamaño original del splash)
        try:
            self.background_image = pygame.image.load("images/hero_background.png").convert_alpha()
            self.background_image = pygame.transform.scale(self.background_image, (self._splash_w, self._splash_h))

            self.gray_overlay = pygame.Surface((self._splash_w, self._splash_h))
            self.gray_overlay.set_alpha(140)
            self.gray_overlay.fill((128, 128, 128))
            
            print("Background image loaded successfully")
        except Exception as e:
            print(f"Error loading background image: {e}")

        # Generar beep sounds ascendentes para animacion de score
        self.score_beeps = []
        for i in range(10):
            freq = 400 + i * 80  # 400Hz → 1120Hz
            beep = self.sound_manager.generate_beep(freq, duration_ms=50, volume=0.3)
            self.score_beeps.append(beep)

    def toggle_fullscreen(self):
        """Alternar entre ventana y pantalla completa"""
        self._render_pipeline.toggle_fullscreen()
        self._sync_render_pipeline()

    def _update_scaling(self):
        """Calcular escala y offset para mantener aspect ratio"""
        self._render_pipeline._update_scaling()
        self._sync_render_pipeline()

    def _sync_render_pipeline(self):
        """Sincronizar atributos locales con el render pipeline"""
        rp = self._render_pipeline
        self.fullscreen = rp.fullscreen
        self.display_surface = rp.display_surface
        self.render_scale = rp.render_scale
        self.render_w = rp.render_w
        self.render_h = rp.render_h
        self.render_x = rp.render_x
        self.render_y = rp.render_y

    def _prepare_propeller_sprites(self):
        """Separa las palas de la hélice del cuerpo de cada sprite y genera frames de rotación.
        Las palas están en filas 2-3 para idle/walk/shoot y filas 0-1 para fly."""
        # Filas que contienen las palas para cada sprite
        blade_rows = {
            'player': (2, 3),
            'player_shooting': (2, 3),
            'player_walk1': (2, 3),
            'player_walk2': (2, 3),
            'player_fly': (0, 1),
        }

        self.propeller_bodies = {}
        self.propeller_bodies_flip = {}
        self.propeller_frames = {}
        self.propeller_frames_flip = {}

        for sprite_key, (row_start, row_end) in blade_rows.items():
            if sprite_key not in self.sprites:
                continue

            original = self.sprites[sprite_key]

            # Recopilar píxeles de las palas (no transparentes en las filas de blade)
            blade_pixels = []
            for y in range(row_start, row_end + 1):
                for x in range(original.get_width()):
                    color = original.get_at((x, y))
                    if color.a > 0:
                        blade_pixels.append((x, y, color))

            if not blade_pixels:
                continue

            # Centro y medio-ancho de las palas
            min_x = min(p[0] for p in blade_pixels)
            max_x = max(p[0] for p in blade_pixels)
            center_x = (min_x + max_x) / 2.0
            half_width = (max_x - min_x) / 2.0

            # Sprite del cuerpo: original con píxeles de palas borrados
            body = original.copy()
            for bx, by, _ in blade_pixels:
                body.set_at((bx, by), pygame.Color(0, 0, 0, 0))
            self.propeller_bodies[sprite_key] = body
            self.propeller_bodies_flip[sprite_key] = pygame.transform.flip(body, True, False)

            # Generar frames de rotación variando el ancho visible
            frames = []
            frames_flip = []
            for factor in PROPELLER_WIDTH_FACTORS:
                frame = pygame.Surface((32, 32), pygame.SRCALPHA)
                scaled_half = half_width * factor
                for bx, by, color in blade_pixels:
                    if abs(bx - center_x) <= scaled_half:
                        frame.set_at((bx, by), color)
                frames.append(frame)
                frames_flip.append(pygame.transform.flip(frame, True, False))

            self.propeller_frames[sprite_key] = frames
            self.propeller_frames_flip[sprite_key] = frames_flip

        print(f"Propeller sprites prepared: {len(self.propeller_bodies)} body sprites, "
              f"{sum(len(f) for f in self.propeller_frames.values())} overlay frames")

    def _generate_skeleton_sprite(self, player_sprite):
        """Genera sprite de esqueleto a partir del sprite del jugador.
        Toma la silueta y la recolorea con tonos hueso/blanco."""
        w, h = player_sprite.get_size()
        skeleton = pygame.Surface((w, h), pygame.SRCALPHA)

        # Colores hueso para el esqueleto
        bone_light = (230, 220, 200)   # Hueso claro
        bone_dark = (180, 170, 150)    # Hueso oscuro
        bone_shadow = (120, 110, 95)   # Sombra

        for x in range(w):
            for y in range(h):
                r, g, b, a = player_sprite.get_at((x, y))
                if a < 30:
                    continue
                # Calcular luminosidad del pixel original
                lum = (r * 0.299 + g * 0.587 + b * 0.114) / 255.0
                # Mapear a tonos hueso según luminosidad
                if lum > 0.6:
                    color = bone_light
                elif lum > 0.3:
                    color = bone_dark
                else:
                    color = bone_shadow
                skeleton.set_at((x, y), (*color, a))

        return skeleton

    def _generate_cave_background(self):
        """Genera superficie de fondo con pintitas simulando textura de caverna"""
        level_w = max_level_width(self.level_map) if self.level_map else DEFAULT_LEVEL_WIDTH
        level_h = len(self.level_map) if self.level_map else DEFAULT_LEVEL_HEIGHT
        width = level_w * TILE_SIZE
        height = level_h * TILE_SIZE
        self.cave_bg = pygame.Surface((width, height))
        self.cave_bg.fill(COLOR_BLACK)

        # Derivar colores de puntitos del color 1 del nivel (depth_palette entrada 0)
        # Se usan variantes oscuras (~15-25% del color original)
        if self.depth_palette and len(self.depth_palette) > 0:
            wc = self.depth_palette[0].get("wall", [255, 255, 255])
            base_r, base_g, base_b = wc[0], wc[1], wc[2]
        else:
            base_r, base_g, base_b = 180, 120, 60  # Fallback marron
        dot_colors = [
            (max(0, base_r * pct // 100), max(0, base_g * pct // 100), max(0, base_b * pct // 100))
            for pct in CAVE_DOT_BRIGHTNESS
        ]

        num_dots = int(width * height * CAVE_DOT_DENSITY)

        for _ in range(num_dots):
            dx = random.randint(0, width - CAVE_DOT_SIZE)
            dy = random.randint(0, height - CAVE_DOT_SIZE)
            color = random.choice(dot_colors)
            if CAVE_DOT_SIZE <= 1:
                self.cave_bg.set_at((dx, dy), color)
            else:
                pygame.draw.rect(self.cave_bg, color,
                                 (dx, dy, CAVE_DOT_SIZE, CAVE_DOT_SIZE))

    def _generate_edge_overlay(self):
        """Genera overlay pre-computado con musgo/raíces en bordes expuestos"""
        self.edge_overlay = generate_edge_overlay(
            self.level_map, self.edge_color, seed=self.level_num)

    def _generate_floor_texture(self):
        """Genera overlay pre-computado con textura porosa en tiles de suelo"""
        self.floor_texture = generate_floor_texture(
            self.level_map, seed=self.level_num + 1000)

    def start_level(self):
        """Start a new level"""
        self.state = STATE_PLAYING
        self.energy = MAX_ENERGY
        self.dynamite_count = DYNAMITE_QUANTITY  # Restore bombs for new level

        # Stop helicopter sound when starting new level
        self.sound_manager.stop_loop('helicopter')

        # Generate level
        self.level_map = generate_level(self.level_num)

        # Construir tiles de suelo tintados por fila del viewport (se repiten en cada viewport)
        self.depth_palette = get_level_palette(self.level_num)
        self.edge_color = get_level_edge_color(self.level_num)
        self.tinted_floors = build_tinted_floors(self.tiles['floor'], self.depth_palette)

        # Generar fondo de caverna con pintitas
        self._generate_cave_background()

        # Generar overlays pre-computados (se blitean por viewport)
        self._generate_edge_overlay()
        self._generate_floor_texture()

        # Clear entities
        self.enemies = []
        self.lasers = []
        self.dynamites = []
        self.miner = None
        self.floating_scores_mgr.items.clear()
        self.rock_health = {}  # {(row, col): hits_restantes} para rocas dañadas por láser

        # Reset lampara/oscuridad
        self.dark_mode = False
        self.lamps = []

        # Reset scroll de agua tóxica
        self.toxic_water_scroll = 0.0

        # Create player
        self.player = Player()
        self.player.init(self.level_map)
        if 'player' in self.sprites:
            self.player.image = self.sprites['player']
        if 'player_shooting' in self.sprites:
            self.player.image_shooting = self.sprites['player_shooting']
        if 'player_walk1' in self.sprites and 'player_walk2' in self.sprites:
            self.player.walk_frames = [self.sprites['player_walk1'], self.sprites['player_walk2']]
        if 'player_fly' in self.sprites:
            self.player.image_fly = self.sprites['player_fly']
        # Asignar datos de animación de hélice
        if hasattr(self, 'propeller_bodies'):
            self.player._prop_bodies = self.propeller_bodies
            self.player._prop_bodies_flip = self.propeller_bodies_flip
            self.player._prop_frames = self.propeller_frames
            self.player._prop_frames_flip = self.propeller_frames_flip
        if 'walk1' in self.sounds and 'walk2' in self.sounds:
            self.player.walk_sounds = [self.sounds['walk1'], self.sounds['walk2']]
        # Referencia a masks para colisión pixel-perfect con tiles
        self.player._masks_ref = self.masks

        # Parse level and create entities
        for row_index, row in enumerate(self.level_map):
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE

                if tile == "V":
                    enemy = Enemy(x, y, "bat")
                    # Velocidad base con escalado por nivel y variación aleatoria ±5%
                    speed_variation = random.uniform(1 - ENEMY_SPEED_VARIATION, 1 + ENEMY_SPEED_VARIATION)
                    enemy.speed = BAT_SPEED * (1 + BAT_SPEED_SCALE * self.level_num) * speed_variation
                    if 'bat1' in self.sprites:
                        enemy.images = [self.sprites['bat1'], self.sprites['bat2']]
                        enemy.image = enemy.images[0]
                    self.enemies.append(enemy)
                elif tile == "A":
                    enemy = Enemy(x, y, "spider")
                    # Variación aleatoria ±5% en velocidad de araña
                    speed_variation = random.uniform(1 - ENEMY_SPEED_VARIATION, 1 + ENEMY_SPEED_VARIATION)
                    enemy.speed = SPIDER_SPEED * speed_variation
                    if 'spider' in self.sprites:
                        enemy.image = self.sprites['spider']
                    self.enemies.append(enemy)
                elif tile == "B":
                    enemy = Enemy(x, y, "bug")
                    # Variación aleatoria ±5% en velocidad de bicho
                    speed_variation = random.uniform(1 - ENEMY_SPEED_VARIATION, 1 + ENEMY_SPEED_VARIATION)
                    enemy.speed = BUG_SPEED * speed_variation
                    if 'bug1' in self.sprites:
                        enemy.images = [self.sprites['bug1'], self.sprites['bug2'],
                                        self.sprites['bug3'], self.sprites['bug4']]
                        enemy.image = enemy.images[0]
                    self.enemies.append(enemy)
                elif tile in ("<", ">"):
                    # Víbora: reemplazar tile por tierra (#) y crear enemigo
                    etype = "snake_left" if tile == "<" else "snake_right"
                    enemy = Enemy(x, y, etype)
                    speed_variation = random.uniform(1 - ENEMY_SPEED_VARIATION, 1 + ENEMY_SPEED_VARIATION)
                    enemy.speed = SNAKE_EMERGE_SPEED * speed_variation
                    # Asignar sprites de víbora
                    if tile == "<":
                        # Mira a la izquierda: cabeza tal cual
                        if 'snake_head' in self.sprites:
                            enemy.snake_head_sprite = self.sprites['snake_head']
                        if 'snake_neck' in self.sprites:
                            enemy.snake_neck_sprite = self.sprites['snake_neck']
                    else:
                        # Mira a la derecha: flipear cabeza
                        if 'snake_head' in self.sprites:
                            enemy.snake_head_sprite = pygame.transform.flip(self.sprites['snake_head'], True, False)
                        if 'snake_neck' in self.sprites:
                            enemy.snake_neck_sprite = self.sprites['snake_neck']
                    self.enemies.append(enemy)
                    # El tile se convierte en tierra (la pared de donde sale)
                    self.level_map[row_index] = (
                        self.level_map[row_index][:col_index] + '#' +
                        self.level_map[row_index][col_index + 1:]
                    )
                elif tile == "M":
                    self.miner = Miner(x, y)
                    if 'miner' in self.sprites:
                        self.miner.image = self.sprites['miner']
                elif tile == "L":
                    # Guardar posicion de lampara y limpiar del mapa (no es solido)
                    self.lamps.append({'x': x, 'y': y})
                    self.level_map[row_index] = (
                        self.level_map[row_index][:col_index] + ' ' +
                        self.level_map[row_index][col_index + 1:]
                    )

        # Reset camera al viewport del jugador (snap instantáneo, usando centro del sprite)
        player_cx = int(self.player.x + self.player.width / 2)
        player_cy = int(self.player.y + self.player.height / 2)
        viewport_col = player_cx // GAME_WIDTH
        viewport_row = player_cy // GAME_VIEWPORT_HEIGHT
        player_tile_y = int(self.player.y / TILE_SIZE)
        current_band_w = band_width(self.level_map, player_tile_y)
        level_h = len(self.level_map) if self.level_map else DEFAULT_LEVEL_HEIGHT
        max_cam_x = max(0, current_band_w * TILE_SIZE - GAME_WIDTH)
        max_cam_y = max(0, level_h * TILE_SIZE - GAME_VIEWPORT_HEIGHT)
        self.camera_x = max(0, min(viewport_col * GAME_WIDTH, max_cam_x))
        self.camera_y = max(0, min(viewport_row * GAME_VIEWPORT_HEIGHT, max_cam_y))

    def shoot_laser(self):
        """Player shoots laser"""
        if self.shoot_cooldown <= 0:
            direction = 1 if self.player.facing_right else -1
            # El laser sale de la punta del arma a nivel de cadera (y+16)
            # Sprite mira izquierda por defecto, arma en x=3
            # Facing left: laser sale de x+3, facing right: laser sale de x+29 (flip)
            if self.player.facing_right:
                laser_x = self.player.x + 29
            else:
                laser_x = self.player.x + 3 - LASER_WIDTH
            laser = Laser(laser_x, self.player.y + 16, direction)
            self.lasers.append(laser)
            self.shoot_cooldown = LASER_COOLDOWN

            # Activar sprite de disparo
            self.player.shooting_timer = 0.15

            if 'shoot' in self.sounds:
                self.sounds['shoot'].play()

    def drop_dynamite(self):
        """Player drops dynamite"""
        if self.dynamite_count > 0:
            # Coloca la bomba centrada horizontalmente sobre el héroe, a la altura del suelo
            dyn_x = self.player.x + self.player.width / 2 - 4  # centrar dinamita (width=8) en el héroe (width=32)
            dyn_y = self.player.y + self.player.height - 16  # base de dinamita alineada con pies del héroe
            dynamite = Dynamite(dyn_x, dyn_y)
            if 'bomb1' in self.sprites:
                dynamite.explosion_sprites = [
                    self.sprites['bomb1'],
                    self.sprites['bomb2'],
                    self.sprites['bomb3'],
                ]
            self.dynamites.append(dynamite)
            self.dynamite_count -= 1

    def update_camera(self):
        """Update camera - snap instantáneo a viewport (estilo juego original)"""
        level_h = len(self.level_map) if self.level_map else DEFAULT_LEVEL_HEIGHT
        self._camera.update(
            self.player.x, self.player.y,
            self.player.width, self.player.height,
            level_h,
            band_width_fn=lambda tile_row: band_width(self.level_map, tile_row)
        )
        self.camera_x = self._camera.x
        self.camera_y = self._camera.y

    def mask_collide(self, x1, y1, mask1, x2, y2, mask2):
        """Colision pixel-perfect entre dos masks. Retorna punto de overlap o None."""
        return mask_overlap(x1, y1, mask1, x2, y2, mask2)

    def check_collisions(self):
        """Check all collisions"""
        if not self.player:
            return

        player_rect = self.player.get_rect()
        player_mask = self.player.get_mask(self.masks)

        # Player vs enemies (pixel-perfect con masks, fallback a rect para snake)
        for enemy in self.enemies:
            if not enemy.active or enemy.exploding:
                continue
            enemy_mask = enemy.get_mask(self.masks)
            if enemy_mask and player_mask:
                # Colisión pixel-perfect
                if self.mask_collide(enemy.x, enemy.y, enemy_mask,
                                     self.player.x, self.player.y, player_mask):
                    self.player_hit()
                    return
            else:
                # Snake y otros sin mask: verificar overlap del rect del enemigo
                # contra la mask del player (respeta transparencia del player)
                enemy_rect = enemy.get_rect()
                if enemy_rect.width > 0 and enemy_rect.height > 0 and player_mask:
                    # Offset del player relativo al rect del enemigo
                    ox = int(self.player.x - enemy_rect.x)
                    oy = int(self.player.y - enemy_rect.y)
                    # Verificar si algún pixel visible del player cae dentro del rect
                    if player_mask.overlap_area(
                            pygame.mask.Mask((enemy_rect.width, enemy_rect.height), fill=True),
                            (-ox, -oy)) > 0:
                        self.player_hit()
                        return
                elif player_rect.colliderect(enemy_rect):
                    self.player_hit()
                    return

        # Player vs miner (pixel-perfect)
        if self.miner and not self.miner.rescued:
            miner_mask = self.miner.get_mask(self.masks)
            if miner_mask and player_mask:
                if self.mask_collide(self.miner.x, self.miner.y, miner_mask,
                                     self.player.x, self.player.y, player_mask):
                    self.rescue_miner()
                    return
            elif player_rect.colliderect(self.miner.get_rect()):
                self.rescue_miner()
                return

        # Lasers vs enemies (pixel-perfect con mask del enemigo, fallback rect para snake)
        for laser in self.lasers[:]:
            if not laser.active:
                continue
            laser_rect = laser.get_rect()
            for enemy in self.enemies:
                if not enemy.active or enemy.exploding:
                    continue
                enemy_mask = enemy.get_mask(self.masks)
                hit = False
                if enemy_mask:
                    # Colisión pixel-perfect
                    if self.mask_collide(enemy.x, enemy.y, enemy_mask,
                                         laser.x, laser.y, self.laser_mask):
                        hit = True
                else:
                    # Fallback a rect (snake y otros sin mask)
                    if laser_rect.colliderect(enemy.get_rect()):
                        hit = True
                if not hit:
                    continue

                enemy.exploding = True
                laser.active = False
                pts = TILE_SCORES[ENEMY_TILE_CHARS[enemy.enemy_type]]
                self.score += pts
                self.add_floating_score(enemy.x + 16, enemy.y, pts)

                # Víbora: al morir, el tile de pared original queda vacío
                if enemy.enemy_type in ("snake_left", "snake_right"):
                    r, c = enemy.wall_row, enemy.wall_col
                    if 0 <= r < len(self.level_map) and 0 <= c < len(self.level_map[r]):
                        self.level_map[r] = (
                            self.level_map[r][:c] + ' ' + self.level_map[r][c + 1:]
                        )

                # Play splatter sound
                if 'splatter' in self.sounds:
                    self.sounds['splatter'].play()

                break

        # Dynamite explosions
        for dynamite in self.dynamites[:]:
            if dynamite.exploded:
                explosion_rect = dynamite.get_explosion_rect()
                if explosion_rect:
                    # Destroy enemies (antes de check player para que siempre se procesen)
                    for enemy in self.enemies:
                        if enemy.active and not enemy.exploding and explosion_rect.colliderect(enemy.get_rect()):
                            enemy.exploding = True
                            self.score += EXPLOSION_KILL_SCORE
                            self.add_floating_score(enemy.x + 16, enemy.y, EXPLOSION_KILL_SCORE)

                            # Víbora: al morir, el tile de pared original queda vacío
                            if enemy.enemy_type in ("snake_left", "snake_right"):
                                r, c = enemy.wall_row, enemy.wall_col
                                if 0 <= r < len(self.level_map) and 0 <= c < len(self.level_map[r]):
                                    self.level_map[r] = (
                                        self.level_map[r][:c] + ' ' + self.level_map[r][c + 1:]
                                    )

                            # Play splatter sound
                            if 'splatter' in self.sounds:
                                self.sounds['splatter'].play()

                    # Destroy blocks and walls
                    tiles_changed = False
                    for row_index in range(len(self.level_map)):
                        for col_index in range(len(self.level_map[row_index])):
                            tile = self.level_map[row_index][col_index]
                            if tile in ('#', 'R', 'W'):  # Destruye tierra, rocas y roca lava (G, X indestructibles)
                                tile_x = col_index * TILE_SIZE
                                tile_y = row_index * TILE_SIZE
                                tile_rect = pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE)

                                if explosion_rect.colliderect(tile_rect):
                                    row = list(self.level_map[row_index])
                                    row[col_index] = ' '
                                    self.level_map[row_index] = "".join(row)
                                    # Limpiar health de roca si tenía daño por láser
                                    self.rock_health.pop((row_index, col_index), None)
                                    pts = TILE_SCORES.get(tile, 0)
                                    self.score += pts
                                    self.add_floating_score(tile_x + 16, tile_y, pts)
                                    tiles_changed = True

                    # Matar víboras cuya pared fue destruida
                    for enemy in self.enemies:
                        if (enemy.active and not enemy.exploding and
                                enemy.enemy_type in ("snake_left", "snake_right")):
                            r, c = enemy.wall_row, enemy.wall_col
                            if (0 <= r < len(self.level_map) and
                                    0 <= c < len(self.level_map[r]) and
                                    self.level_map[r][c] == ' '):
                                enemy.exploding = True
                                pts = TILE_SCORES.get(ENEMY_TILE_CHARS[enemy.enemy_type], 0)
                                self.score += pts
                                self.add_floating_score(
                                    enemy.wall_col * TILE_SIZE + 16,
                                    enemy.wall_row * TILE_SIZE, pts)
                                if 'splatter' in self.sounds:
                                    self.sounds['splatter'].play()
                                tiles_changed = True

                    # El overlay de musgo NO se regenera; el moss original
                    # queda intacto y los nuevos bordes expuestos quedan sin moss

                    # Play sound once
                    if 'explosion' in self.sounds and dynamite.explosion_time > 0.4:
                        self.sounds['explosion'].play()

                    # Check if player is in blast radius (al final para no saltear enemigos/bloques)
                    if player_rect.colliderect(explosion_rect):
                        self.player_hit()
                        return

    def player_hit(self):
        """Player takes damage - inicia animación de muerte"""
        self.lives -= 1

        # Stop helicopter sound
        self.sound_manager.stop_loop('helicopter')

        # Play death sound
        if 'death' in self.sounds:
            self.sounds['death'].play()

        # Iniciar animación de muerte
        self.state = STATE_DYING
        self.death_timer = 0
        self.death_flash_done = False
        # Guardar posición, orientación y sprite actual del player para la animación
        self.death_x = self.player.x
        self.death_y = self.player.y
        self.death_facing_right = self.player.facing_right
        # Capturar el sprite que tenía al morir para usar como silueta del flash
        p = self.player
        if p.shooting_timer > 0 and p.image_shooting:
            death_sprite = p.image_shooting
        elif not p.is_grounded and p.image_fly:
            death_sprite = p.image_fly
        elif p.is_walking and p.walk_frames:
            death_sprite = p.walk_frames[p.walk_frame_index]
        else:
            death_sprite = p.image
        if self.death_facing_right and death_sprite:
            death_sprite = pygame.transform.flip(death_sprite, True, False)
        self.death_sprite = death_sprite

    def rescue_miner(self):
        """Rescue miner and complete level - inicia animacion ColecoVision"""
        self.miner.rescued = True
        self.score += TILE_SCORES['M']

        # Stop helicopter sound
        self.sound_manager.stop_loop('helicopter')

        # Inicializar animacion de level complete
        self.state = STATE_LEVEL_COMPLETE
        self.score_beep_timer = 0
        self.score_beep_initial_energy = self.energy  # Energia inicial para calcular proporcion de beeps
        self.bomb_explosion_effects = []
        self.bomb_explode_timer = 0

        # Determinar fase inicial
        if self.energy > 0:
            self.level_complete_phase = 0  # Energy drain
        elif self.dynamite_count > 0:
            self.level_complete_phase = 1  # Bomb explosions
        else:
            self.level_complete_phase = 2  # Display directo
            self.level_complete_timer = 2.0
            if 'win_screen' in self.sounds:
                self.sounds['win_screen'].play()

    def add_floating_score(self, x, y, points):
        """Agrega un texto flotante de puntuacion en coordenadas de mundo"""
        self.floating_scores_mgr.add(x, y, points)

    def render_floating_scores(self):
        """Renderiza los textos flotantes de puntuacion (en game_surface)"""
        cv_yellow = (212, 193, 84)
        self.floating_scores_mgr.render(
            self.game_surface, self.hud_font, self.camera_x, self.camera_y,
            cv_yellow, GAME_WIDTH, GAME_VIEWPORT_HEIGHT
        )

    def next_level(self):
        """Advance to next level"""
        # Vida extra al pasar de nivel (sin superar el máximo)
        if self.lives < MAX_LIVES:
            self.lives += 1
        self.level_num += 1
        if self.level_num >= len(LEVELS):
            # Won game! - pantalla de victoria
            self.is_victory = True
            self.victory_palette_offset = 0
            self.state = STATE_ENTERING_NAME
        else:
            self.start_level()

    def update_dying(self, dt):
        """Actualiza animación de muerte del jugador"""
        self.death_timer += dt

        # Fase 1: flash blanco breve
        if self.death_timer >= DEATH_FLASH_TIME and not self.death_flash_done:
            self.death_flash_done = True

        # Fase 2: después del tiempo total, reiniciar o game over
        if self.death_timer >= DEATH_ANIM_TIME:
            if self.lives <= 0:
                self.is_victory = False
                self.state = STATE_ENTERING_NAME
            else:
                self.start_level()

    def update_playing(self, dt):
        """Update game during play"""
        if self.energy < 0:
            self.energy = 0

        # Update player
        self.player.update(dt, self.keys, self.joy_axis_x, self.joy_axis_y,
                          self.level_map, self)

        # Contacto con lava detectado por check_collision pixel-perfect
        if self.player._touched_lava:
            self.player._touched_lava = False
            self.player_hit()
            return

        # Helicopter sound when flying (in the air, not on ground)
        if 'helicopter' in self.sounds:
            # Play sound when player is in the air (not grounded)
            if not self.player.is_grounded:
                self.sound_manager.start_loop('helicopter')
            else:
                self.sound_manager.stop_loop('helicopter')

        # Update camera
        self.update_camera()

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(dt, self.level_map)
            if not enemy.active:
                self.enemies.remove(enemy)

        # Update lasers
        for laser in self.lasers[:]:
            laser.update(dt, self.level_map)
            # Procesar impacto en roca antes de eliminar el láser
            if laser.hit_rock_pos:
                row, col = laser.hit_rock_pos
                tile_char = self.level_map[row][col] if (0 <= row < len(self.level_map) and 0 <= col < len(self.level_map[row])) else ' '
                if tile_char in ('R', 'W'):
                    key = (row, col)
                    if key not in self.rock_health:
                        self.rock_health[key] = ROCK_LASER_HITS
                    self.rock_health[key] -= 1
                    if self.rock_health[key] == ROCK_DAMAGE_MIDPOINT:
                        # Sonido de agrietamiento al llegar al estado intermedio
                        if 'rock_crack' in self.sounds:
                            self.sounds['rock_crack'].play()
                    if self.rock_health[key] <= 0:
                        # Destruir la roca
                        row_list = list(self.level_map[row])
                        row_list[col] = ' '
                        self.level_map[row] = "".join(row_list)
                        del self.rock_health[key]
                        tile_x = col * TILE_SIZE
                        tile_y = row * TILE_SIZE
                        pts = TILE_SCORES.get(tile_char, 0)
                        self.score += pts
                        self.add_floating_score(tile_x + 16, tile_y, pts)
                        if 'rock_break' in self.sounds:
                            self.sounds['rock_break'].play()
                laser.hit_rock_pos = None
            if not laser.active:
                self.lasers.remove(laser)

        # Update dynamites
        for dynamite in self.dynamites[:]:
            dynamite.update(dt, self.level_map)
            if not dynamite.active:
                self.dynamites.remove(dynamite)

        # Update floating scores
        self.floating_scores_mgr.update(dt, rise_speed=30)

        # Actualizar animación de agua tóxica (avanza en frames)
        self.toxic_water_scroll += TOXIC_WATER_SCROLL_SPEED * dt

        # Colisión jugador vs agua tóxica (usa bounding box de píxeles visibles)
        player_rect = self.player.get_rect()
        player_mask = self.player.get_mask(self.masks)
        # Verificar tiles de agua cercanos al jugador
        p_tile_left = max(0, int(self.player.x / TILE_SIZE))
        p_tile_right = int((self.player.x + self.player.width) / TILE_SIZE)
        p_tile_top = max(0, int(self.player.y / TILE_SIZE))
        p_tile_bottom = min(int((self.player.y + self.player.height) / TILE_SIZE),
                            len(self.level_map) - 1 if self.level_map else 0)
        for tile_row in range(p_tile_top, p_tile_bottom + 1):
            for tile_col in range(p_tile_left, p_tile_right + 1):
                if (0 <= tile_row < len(self.level_map) and
                        0 <= tile_col < len(self.level_map[tile_row]) and
                        self.level_map[tile_row][tile_col] == '~'):
                    # Usar hit rect del agua (bounding box de píxeles visibles del tile)
                    water_rect = self.toxic_water_hit_rect.move(
                        tile_col * TILE_SIZE, tile_row * TILE_SIZE)
                    if player_rect.colliderect(water_rect):
                        self.player_hit()
                        return

        # Check collisions
        self.check_collisions()

        # Colision jugador-lampara (toggle oscuridad, deteccion por flanco)
        # Usa bounding box de pixeles visibles del sprite, no el tile completo
        player_rect = self.player.get_rect()
        for lamp in self.lamps:
            lamp_rect = self.lamp_hit_rect.move(lamp['x'], lamp['y'])
            currently_inside = player_rect.colliderect(lamp_rect)
            if currently_inside and not lamp.get('player_inside', False):
                self.dark_mode = not self.dark_mode
            lamp['player_inside'] = currently_inside

        # Explosion flash effect (fondo parpadea blanco/negro)
        any_exploding = any(d.exploded for d in self.dynamites)
        if any_exploding:
            self.explosion_flash_timer += dt
            if self.explosion_flash_timer >= 0.05:  # Alternar cada 50ms
                self.explosion_flash_timer -= 0.05
                self.explosion_flash = not self.explosion_flash
        else:
            self.explosion_flash = False
            self.explosion_flash_timer = 0

        # Update timers
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

        # Check for extra life
        if self.score >= self.last_life_score + 20000:
            if self.lives < MAX_LIVES:
                self.lives += 1
            self.last_life_score = self.score

    def update_level_complete(self, dt):
        """Update level complete state - animacion ColecoVision de 3 fases"""

        if self.level_complete_phase == 0:
            # Fase 0: Drenar energia, sumar puntos, beeps ascendentes
            drain_rate = MAX_ENERGY / 1.5  # Drenar toda la energia en ~1.5 seg
            drain_amount = drain_rate * dt
            actual_drain = min(drain_amount, self.energy)
            self.energy -= actual_drain
            self.score += int(actual_drain)

            # Beeps ascendentes cada ~80ms, tono proporcional a energia drenada
            self.score_beep_timer += dt
            if self.score_beep_timer >= 0.08 and self.score_beeps:
                self.score_beep_timer -= 0.08
                # Calcular indice del beep segun proporcion de energia drenada
                if self.score_beep_initial_energy > 0:
                    drained_ratio = 1.0 - (self.energy / self.score_beep_initial_energy)
                    beep_idx = int(drained_ratio * (len(self.score_beeps) - 1))
                    beep_idx = max(0, min(beep_idx, len(self.score_beeps) - 1))
                else:
                    beep_idx = len(self.score_beeps) - 1
                self.score_beeps[beep_idx].play()

            # Pasar a fase 1 cuando se acaba la energia
            if self.energy <= 0:
                self.energy = 0
                if self.dynamite_count > 0:
                    self.level_complete_phase = 1
                    self.bomb_explode_timer = 0.3  # Pequeña pausa antes de la primera bomba
                else:
                    self.level_complete_phase = 2
                    self.level_complete_timer = 2.0
                    if 'win_screen' in self.sounds:
                        self.sounds['win_screen'].play()

        elif self.level_complete_phase == 1:
            # Fase 1: Explotar bombas una por una
            # Actualizar efectos de explosion existentes
            for effect in self.bomb_explosion_effects[:]:
                effect['timer'] -= dt
                if effect['timer'] <= 0:
                    self.bomb_explosion_effects.remove(effect)

            self.bomb_explode_timer -= dt
            if self.bomb_explode_timer <= 0 and self.dynamite_count > 0:
                # Calcular posicion del icono de bomba en HUD
                panel_w = 70
                ce = SCREEN_WIDTH - panel_w - 10
                icon_gap = 2
                hud_y = VIEWPORT_HEIGHT
                icons_y = hud_y + 28
                bomb_count = self.dynamite_count
                bomb_spacing = 10  # Mismo espaciado que en render_hud
                # Posicion de la bomba mas a la izquierda (la que va a explotar)
                bx = ce - bomb_count * bomb_spacing
                by = icons_y

                # Crear efecto de explosion en esa posicion
                self.bomb_explosion_effects.append({
                    'x': bx + 8,  # Centro del icono
                    'y': by + 8,
                    'timer': 0.4,
                    'max_timer': 0.4
                })

                self.dynamite_count -= 1
                self.score += BOMB_REMAINING_SCORE

                if 'explosion' in self.sounds:
                    self.sounds['explosion'].play()

                self.bomb_explode_timer = 0.5  # Intervalo entre bombas

            # Pasar a fase 2 cuando no quedan bombas y terminan los efectos
            if self.dynamite_count <= 0 and len(self.bomb_explosion_effects) == 0:
                self.level_complete_phase = 2
                self.level_complete_timer = 2.0
                if 'win_screen' in self.sounds:
                    self.sounds['win_screen'].play()

        elif self.level_complete_phase == 2:
            # Fase 2: Mostrar "LEVEL COMPLETE!" por 2 segundos
            self.level_complete_timer -= dt
            if self.level_complete_timer <= 0:
                self.next_level()

    def _to_grayscale(self, surface):
        """Convierte una surface a escala de gris (con cache)"""
        key = id(surface)
        if key not in self._grayscale_cache:
            self._grayscale_cache[key] = pygame.transform.grayscale(surface)
        return self._grayscale_cache[key]

    def render_lamps(self):
        """Dibuja las lamparas en sus posiciones (en game_surface)"""
        cam_x = int(self.camera_x)
        cam_y = int(self.camera_y)
        for lamp in self.lamps:
            sx = lamp['x'] - cam_x
            sy = lamp['y'] - cam_y
            if -TILE_SIZE < sy < GAME_VIEWPORT_HEIGHT and -TILE_SIZE < sx < GAME_WIDTH:
                self.game_surface.blit(self.tiles['lamp'], (sx, sy))

    def _render_dark_mode_overlay(self):
        """Modo oscuridad estilo C64: fondo negro, sprites en gris, lasers/dinamitas en color"""
        if not self.dark_mode or self.explosion_flash:
            return

        cam_x = int(self.camera_x)
        cam_y = int(self.camera_y)

        # Cubrir viewport con negro (oculta tiles/fondo) - en game_surface
        pygame.draw.rect(self.game_surface, COLOR_BLACK, (0, 0, GAME_WIDTH, GAME_VIEWPORT_HEIGHT))

        # Lamparas en gris
        gray_lamp = self._to_grayscale(self.tiles['lamp'])
        for lamp in self.lamps:
            sx = lamp['x'] - cam_x
            sy = lamp['y'] - cam_y
            if -TILE_SIZE < sy < GAME_VIEWPORT_HEIGHT and -TILE_SIZE < sx < GAME_WIDTH:
                self.game_surface.blit(gray_lamp, (sx, sy))

        # Minero en gris
        if self.miner and not self.miner.rescued:
            sx = self.miner.x - cam_x
            sy = self.miner.y - cam_y
            if -50 < sy < GAME_VIEWPORT_HEIGHT + 50 and -50 < sx < GAME_WIDTH + 50:
                if self.miner.image:
                    gray_img = self._to_grayscale(self.miner.image)
                    self.game_surface.blit(gray_img, (int(sx), int(sy)))

        # Enemigos en gris
        for enemy in self.enemies:
            if not enemy.active:
                continue
            sx = enemy.x - cam_x
            sy = enemy.y - cam_y
            if -50 < sy < GAME_VIEWPORT_HEIGHT + 50 and -50 < sx < GAME_WIDTH + 50:
                if enemy.exploding:
                    # Explosion en gris
                    progress = enemy.explosion_timer / enemy.explosion_duration
                    radius = int(8 + progress * 10)
                    for i in range(2):
                        r = radius - i * 5
                        if r > 0:
                            gray_val = 100 if i == 0 else 70
                            pygame.draw.circle(self.game_surface, (gray_val, gray_val, gray_val),
                                             (int(sx + 16), int(sy + 16)), r)
                else:
                    # Hilo de araña en gris
                    if enemy.enemy_type == "spider":
                        ceiling_y = enemy._find_ceiling_y(self.level_map)
                        if ceiling_y is not None:
                            thread_top = ceiling_y - cam_y
                            thread_bottom = sy + enemy.height // 2
                            center_x = int(sx + enemy.width // 2)
                            pygame.draw.line(self.game_surface, COLOR_GRAY,
                                           (center_x, int(thread_top)),
                                           (center_x, int(thread_bottom)), 1)
                    if enemy.image:
                        gray_img = self._to_grayscale(enemy.image)
                        self.game_surface.blit(gray_img, (int(sx), int(sy)))

        # Jugador en gris
        if self.player:
            sx = self.player.x - cam_x
            sy = self.player.y - cam_y
            if -50 < sy < GAME_VIEWPORT_HEIGHT + 50 and -50 < sx < GAME_WIDTH + 50:
                # Seleccionar sprite (misma logica que player.draw)
                base_img = self.player.image
                if self.player.shooting_timer > 0 and self.player.image_shooting:
                    base_img = self.player.image_shooting
                elif not self.player.is_grounded and self.player.image_fly:
                    base_img = self.player.image_fly
                elif self.player.is_walking and self.player.walk_frames:
                    base_img = self.player.walk_frames[self.player.walk_frame_index]
                if base_img:
                    gray_img = self._to_grayscale(base_img)
                    if self.player.facing_right:
                        gray_img = pygame.transform.flip(gray_img, True, False)
                    self.game_surface.blit(gray_img, (int(sx), int(sy)))

        # Lasers y dinamitas en color (visibles)
        for laser in self.lasers:
            laser.draw(self.game_surface, cam_x, cam_y)
        for dynamite in self.dynamites:
            dynamite.draw(self.game_surface, cam_x, cam_y)

    def render_level(self):
        """Render visible part of level (en game_surface, sin escalar)"""
        level_w = max_level_width(self.level_map) if self.level_map else DEFAULT_LEVEL_WIDTH
        level_h = len(self.level_map) if self.level_map else DEFAULT_LEVEL_HEIGHT
        # Usar offset entero consistente para fondo y tiles
        cam_x = int(self.camera_x)
        cam_y = int(self.camera_y)

        # Dibujar fondo de caverna (o flash blanco si hay explosion)
        if self.explosion_flash:
            self.game_surface.fill(COLOR_WHITE, (0, 0, GAME_WIDTH, GAME_VIEWPORT_HEIGHT))
        elif self.cave_bg:
            src_rect = pygame.Rect(cam_x, cam_y, GAME_WIDTH, GAME_VIEWPORT_HEIGHT)
            self.game_surface.blit(self.cave_bg, (0, 0), src_rect)

        # Calculate visible tiles (ambos ejes)
        start_col = max(0, cam_x // TILE_SIZE - 1)
        end_col = min(level_w, (cam_x + GAME_WIDTH) // TILE_SIZE + 2)
        start_row = max(0, cam_y // TILE_SIZE - 1)
        end_row = min(level_h, (cam_y + GAME_VIEWPORT_HEIGHT) // TILE_SIZE + 2)

        for row_index in range(start_row, end_row):
            if row_index >= len(self.level_map):
                break

            row = self.level_map[row_index]
            for col_index in range(start_col, end_col):
                if col_index >= len(row):
                    # Espacio fuera de la banda: renderizar como pared sólida
                    x = col_index * TILE_SIZE - cam_x
                    y = row_index * TILE_SIZE - cam_y
                    self.game_surface.blit(self.tiles['wall'], (x, y))
                    continue
                tile = row[col_index]
                x = col_index * TILE_SIZE - cam_x
                y = row_index * TILE_SIZE - cam_y

                if tile == '#':
                    self.game_surface.blit(self.tiles['wall'], (x, y))
                elif tile == '.':
                    local_row = row_index % VIEWPORT_ROWS
                    self.game_surface.blit(self.tinted_floors[local_row], (x, y))
                elif tile == 'G':
                    self.game_surface.blit(self.tiles['granite'], (x, y))
                elif tile == 'R':
                    # Mostrar sprite dañado si la roca fue impactada lo suficiente
                    key = (row_index, col_index)
                    if key in self.rock_health and self.rock_health[key] <= ROCK_DAMAGE_MIDPOINT:
                        self.game_surface.blit(self.tiles['rock_damaged'], (x, y))
                    else:
                        self.game_surface.blit(self.tiles['rock'], (x, y))
                elif tile == 'X':
                    self.game_surface.blit(self.tiles['lava'], (x, y))
                elif tile == 'W':
                    # Roca lava: sprite dañado si fue impactada lo suficiente
                    key = (row_index, col_index)
                    if key in self.rock_health and self.rock_health[key] <= ROCK_DAMAGE_MIDPOINT:
                        self.game_surface.blit(self.tiles['lava_rock_damaged'], (x, y))
                    else:
                        self.game_surface.blit(self.tiles['lava_rock'], (x, y))
                elif tile == '~':
                    # Agua tóxica con onda animada por frames
                    frame_idx = int(self.toxic_water_scroll) % len(self.toxic_water_frames)
                    self.game_surface.blit(self.toxic_water_frames[frame_idx], (x, y))
                # Espacios vacios: no dibujar nada, el cave_bg ya se ve

        # Overlay de textura porosa del suelo
        if self.floor_texture:
            src_rect = pygame.Rect(cam_x, cam_y, GAME_WIDTH, GAME_VIEWPORT_HEIGHT)
            self.game_surface.blit(self.floor_texture, (0, 0), src_rect)

        # Overlay de musgo/raíces
        if self.edge_overlay:
            src_rect = pygame.Rect(cam_x, cam_y, GAME_WIDTH, GAME_VIEWPORT_HEIGHT)
            self.game_surface.blit(self.edge_overlay, (0, 0), src_rect)

    def _render_game_to_screen(self):
        """Escala game_surface (512x256) a la zona de juego del screen (768x384)"""
        self._render_pipeline.scale_game_to_screen()

    def render_dying(self):
        """Renderiza la animación de muerte: nivel + esqueleto en lugar del player"""
        self.game_surface.fill(COLOR_BLACK)
        self.render_level()
        self.render_lamps()

        # Dibujar entidades (sin el player)
        if self.miner and not self.miner.rescued:
            self.miner.draw(self.game_surface, self.camera_x, self.camera_y)

        for enemy in self.enemies:
            enemy.draw(self.game_surface, self.camera_x, self.camera_y, self.level_map,
                       wall_tile=self.tiles.get('wall'))

        for dynamite in self.dynamites:
            dynamite.draw(self.game_surface, self.camera_x, self.camera_y)

        # Dibujar esqueleto o flash en la posición del player
        screen_x = self.death_x - self.camera_x
        screen_y = self.death_y - self.camera_y

        if not self.death_flash_done:
            # Flash blanco: silueta del sprite original en blanco (respeta transparencia)
            if self.death_sprite:
                flash_surf = self.death_sprite.copy()
                # Poner RGB a blanco sin tocar el canal alpha
                flash_surf.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_MAX)
                flash_alpha = int(255 * (1.0 - self.death_timer / DEATH_FLASH_TIME))
                flash_surf.set_alpha(flash_alpha)
                self.game_surface.blit(flash_surf, (int(screen_x), int(screen_y)))
            # Flash de pantalla: overlay blanco que se desvanece
            screen_flash_alpha = int(180 * max(0, 1.0 - self.death_timer / (DEATH_FLASH_TIME * 0.6)))
            if screen_flash_alpha > 0:
                flash_overlay = pygame.Surface(self.game_surface.get_size(), pygame.SRCALPHA)
                flash_overlay.fill((255, 255, 255, screen_flash_alpha))
                self.game_surface.blit(flash_overlay, (0, 0))
        else:
            # Mostrar esqueleto
            skeleton = self.sprites.get('skeleton')
            if skeleton:
                img = skeleton
                if self.death_facing_right:
                    img = pygame.transform.flip(skeleton, True, False)
                self.game_surface.blit(img, (int(screen_x), int(screen_y)))

        # Oscuridad estilo C64
        self._render_dark_mode_overlay()

        self.render_floating_scores()
        self._render_game_to_screen()
        self.render_hud()

    def render_hud(self):
        """Render HUD - ColecoVision style"""
        hud_y = VIEWPORT_HEIGHT
        hud_h = HUD_HEIGHT

        # Colores paleta ColecoVision TMS9918A
        cv_yellow = (212, 193, 84)
        cv_red = (212, 82, 77)
        cv_gray = (192, 192, 192)
        cv_highlight = (224, 224, 224)
        cv_shadow = (140, 140, 140)

        # Fondo negro para toda el area del HUD
        pygame.draw.rect(self.screen, COLOR_BLACK, (0, hud_y, SCREEN_WIDTH, hud_h))

        # --- Paneles grises laterales con bisel 3D ---
        panel_w = 70

        # Panel izquierdo
        pygame.draw.rect(self.screen, cv_gray, (0, hud_y, panel_w, hud_h))
        pygame.draw.rect(self.screen, cv_highlight, (0, hud_y, panel_w, 2))
        pygame.draw.rect(self.screen, cv_highlight, (0, hud_y, 2, hud_h))
        pygame.draw.rect(self.screen, cv_shadow, (0, hud_y + hud_h - 2, panel_w, 2))
        pygame.draw.rect(self.screen, cv_shadow, (panel_w - 2, hud_y, 2, hud_h))

        # Panel derecho
        rx = SCREEN_WIDTH - panel_w
        pygame.draw.rect(self.screen, cv_gray, (rx, hud_y, panel_w, hud_h))
        pygame.draw.rect(self.screen, cv_highlight, (rx, hud_y, panel_w, 2))
        pygame.draw.rect(self.screen, cv_highlight, (rx, hud_y, 2, hud_h))
        pygame.draw.rect(self.screen, cv_shadow, (rx, hud_y + hud_h - 2, panel_w, 2))
        pygame.draw.rect(self.screen, cv_shadow, (SCREEN_WIDTH - 2, hud_y, 2, hud_h))

        # --- Area central ---
        cx = panel_w + 10
        ce = SCREEN_WIDTH - panel_w - 10

        # Fila 1: POWER label + barra de energia
        power_label = self.hud_font.render("POWER", True, cv_yellow)
        self.screen.blit(power_label, (cx, hud_y + 8))

        bar_x = cx + power_label.get_width() + 8
        bar_y = hud_y + 8
        bar_w = ce - bar_x
        bar_h = 12

        # Barra: fondo rojo (energia gastada), relleno amarillo (energia restante)
        pygame.draw.rect(self.screen, cv_red, (bar_x, bar_y, bar_w, bar_h))
        energy_pct = max(0, min(1, self.energy / MAX_ENERGY))
        fill_w = int(energy_pct * bar_w)
        if fill_w > 0:
            pygame.draw.rect(self.screen, cv_yellow, (bar_x, bar_y, fill_w, bar_h))

        # Fila 2: Vidas (iconos player) izquierda, Bombas (iconos bomb) derecha
        icons_y = hud_y + 28
        icon_gap = 2

        # Iconos de vidas
        for i in range(min(self.lives, 10)):
            ix = cx + i * (16 + icon_gap)
            if self.hud_player_icon:
                self.screen.blit(self.hud_player_icon, (ix, icons_y))
            else:
                pygame.draw.rect(self.screen, COLOR_BLUE, (ix + 2, icons_y, 12, 16))

        # Iconos de bombas (alineados a la derecha, juntas)
        bomb_count = max(0, min(self.dynamite_count, 10))
        bomb_spacing = 10  # Espaciado reducido para que se vean juntas
        for i in range(bomb_count):
            bx = ce - (bomb_count - i) * bomb_spacing
            if self.hud_bomb_icon:
                self.screen.blit(self.hud_bomb_icon, (bx, icons_y))
            else:
                pygame.draw.rect(self.screen, cv_red, (bx + 3, icons_y, 10, 16))

        # Efectos de explosion de bombas (animacion level complete)
        for effect in self.bomb_explosion_effects:
            progress = 1.0 - (effect['timer'] / effect['max_timer'])
            radius = int(6 + progress * 10)
            alpha = int(255 * (1.0 - progress))
            # Circulo naranja que se expande
            explosion_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surf, (255, 165, 0, alpha), (radius, radius), radius)
            # Circulo amarillo interior
            inner_r = max(1, int(radius * 0.5))
            pygame.draw.circle(explosion_surf, (255, 255, 0, alpha), (radius, radius), inner_r)
            self.screen.blit(explosion_surf, (effect['x'] - radius, effect['y'] - radius))

        # Fila 3: LEVEL + numero (izquierda), Score (derecha)
        bottom_y = hud_y + 54
        level_text = self.hud_font.render(f"LEVEL: {self.level_num + 1}", True, cv_yellow)
        self.screen.blit(level_text, (cx, bottom_y))

        score_text = self.hud_font.render(f"{self.score}", True, cv_yellow)
        self.screen.blit(score_text, (ce - score_text.get_width(), bottom_y))

    def draw_text_with_outline(self, font, text, color, outline_color, center, outline=1, surface=None):
        target = surface or self.screen
        _draw_text_with_outline(target, font, text, color, outline_color, center, outline)


    def render_splash(self):
        """Render splash screen - dibuja a 512x480 (original) y pega centrado sin estirar"""
        s = self.splash_surface
        cx = self._splash_w // 2

        s.blit(self.background_image, (0, 0))
        s.blit(self.gray_overlay, (0, 0))

        """
        title = self.font.render("H.E.R.O.", True, COLOR_WHITE)
        title_rect = title.get_rect(center=(cx, 80))
        s.blit(title, title_rect)

        subtitle = self.small_font.render("Helicopter Emergency", True, COLOR_GRAY)
        subtitle_rect = subtitle.get_rect(center=(cx, 120))
        s.blit(subtitle, subtitle_rect)

        subtitle2 = self.small_font.render("Rescue Operation", True, COLOR_GRAY)
        subtitle2_rect = subtitle2.get_rect(center=(cx, 140))
        s.blit(subtitle2, subtitle2_rect)
        """

        self.draw_text_with_outline(self.small_font, "Press SPACE to Play", COLOR_WHITE, COLOR_BLACK, (cx, 200), surface=s)
        self.draw_text_with_outline(self.small_font, "Press ESC to Quit", COLOR_WHITE, COLOR_BLACK, (cx, 230), surface=s)
        self.draw_text_with_outline(self.small_font, "CONTROLS", COLOR_WHITE, COLOR_BLACK, (cx, 270), surface=s)
        self.draw_text_with_outline(self.small_font, "Arrows: Move/Fly", COLOR_WHITE, COLOR_BLACK, (cx, 295), surface=s)
        self.draw_text_with_outline(self.small_font, "SPACE: Shoot", COLOR_WHITE, COLOR_BLACK, (cx, 315), surface=s)
        self.draw_text_with_outline(self.small_font, "Z: Drop Bomb", COLOR_WHITE, COLOR_BLACK, (cx, 335), surface=s)
        self.draw_text_with_outline(self.small_font, "Controller: Stick/X/B", COLOR_WHITE, COLOR_BLACK, (cx, 355), surface=s)
        self.draw_text_with_outline(self.small_font, "HIGH SCORES", COLOR_WHITE, COLOR_BLACK, (cx, 390), surface=s)

        scores = load_scores()[:3]
        for i, score in enumerate(scores):
            self.draw_text_with_outline(self.small_font, f"{i+1}. {score['name']}: {score['score']}", COLOR_WHITE, COLOR_BLACK, (cx, 420 + i*20), surface=s)

        # Escalar splash manteniendo aspect ratio y centrar en screen
        scale = min(SCREEN_WIDTH / self._splash_w, SCREEN_HEIGHT / self._splash_h)
        sw = int(self._splash_w * scale)
        sh = int(self._splash_h * scale)
        scaled = pygame.transform.scale(s, (sw, sh))
        self.screen.blit(scaled, ((SCREEN_WIDTH - sw) // 2, (SCREEN_HEIGHT - sh) // 2))

    def render_entering_name(self):
        """Render name entry screen (victoria o game over)"""
        self.screen.fill(COLOR_BLACK)

        if self.is_victory:
            # "VICTORY!" con cada letra de un color distinto, ciclando la paleta
            self.victory_palette_offset = (self.victory_palette_offset + 1) % 256
            victory_text = "VICTORY!"
            # Renderizar cada letra por separado con color distinto
            letter_surfaces = []
            total_w = 0
            spacing = 256 // len(victory_text)  # Distribuir colores uniformemente
            for i, ch in enumerate(victory_text):
                color_idx = (self.victory_palette_offset + i * spacing) % 256
                color = self._victory_palette[color_idx]
                surf = self.font.render(ch, True, color)
                letter_surfaces.append(surf)
                total_w += surf.get_width()
            # Centrar y dibujar
            x = (SCREEN_WIDTH - total_w) // 2
            y = 100
            for surf in letter_surfaces:
                h = surf.get_height()
                self.screen.blit(surf, (x, y - h // 2))
                x += surf.get_width()
        else:
            game_over = self.font.render("GAME OVER", True, COLOR_RED)
            go_rect = game_over.get_rect(center=(SCREEN_WIDTH//2, 100))
            self.screen.blit(game_over, go_rect)

        score_text = self.small_font.render(f"Final Score: {self.score}", True, COLOR_WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(score_text, score_rect)

        # Solo permitir entrada de nombre si el score es mayor a 0
        if self.score > 0 or self.is_victory:
            prompt = self.small_font.render("Enter Your Name:", True, COLOR_WHITE)
            prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH//2, 200))
            self.screen.blit(prompt, prompt_rect)

            name = self.font.render(self.player_name + "_", True, COLOR_GREEN)
            name_rect = name.get_rect(center=(SCREEN_WIDTH//2, 240))
            self.screen.blit(name, name_rect)

            instr = self.small_font.render("Press ENTER when done", True, COLOR_GRAY)
            instr_rect = instr.get_rect(center=(SCREEN_WIDTH//2, 300))
            self.screen.blit(instr, instr_rect)
        else:
            instr = self.small_font.render("Press ENTER to continue", True, COLOR_GRAY)
            instr_rect = instr.get_rect(center=(SCREEN_WIDTH//2, 250))
            self.screen.blit(instr, instr_rect)

    def render_level_complete(self):
        """Render level complete - fases 0 y 1 muestran juego + HUD, fase 2 agrega overlay"""
        self.game_surface.fill(COLOR_BLACK)
        self.render_level()
        self.render_lamps()

        if self.miner:
            self.miner.draw(self.game_surface, self.camera_x, self.camera_y)

        for enemy in self.enemies:
            enemy.draw(self.game_surface, self.camera_x, self.camera_y, self.level_map,
                       wall_tile=self.tiles.get('wall'))

        for laser in self.lasers:
            laser.draw(self.game_surface, self.camera_x, self.camera_y)

        if self.player:
            self.player.draw(self.game_surface, self.camera_x, self.camera_y)

        for dynamite in self.dynamites:
            dynamite.draw(self.game_surface, self.camera_x, self.camera_y)

        # Oscuridad con spotlight
        self._render_dark_mode_overlay()

        self.render_floating_scores()
        self._render_game_to_screen()
        self.render_hud()

        # Solo en fase 2: overlay oscuro + texto "LEVEL COMPLETE!"
        if self.level_complete_phase == 2:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(COLOR_BLACK)
            self.screen.blit(overlay, (0, 0))

            complete = self.font.render("LEVEL COMPLETE!", True, COLOR_GREEN)
            complete_rect = complete.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(complete, complete_rect)

    def loop(self):
        """Main game loop"""
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000.0

            # Get input (via InputManager)
            self.input_manager.poll()
            self.keys = self.input_manager.keys
            self.joy_axis_x = self.input_manager.joy_axis_x
            self.joy_axis_y = self.input_manager.joy_axis_y

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    # Fullscreen toggle (F11)
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                        continue

                    # Quit confirmation dialog
                    if self.show_quit_confirm:
                        if event.key in (pygame.K_y, pygame.K_ESCAPE):
                            running = False
                        else:
                            self.show_quit_confirm = False
                        continue

                    if self.state == STATE_SPLASH:
                        if event.key == pygame.K_SPACE:
                            self.level_num = 0
                            self.score = 0
                            self.lives = INITIAL_LIVES
                            self.dynamite_count = 6
                            self.last_life_score = 0
                            self.start_level()
                        elif event.key == pygame.K_ESCAPE:
                            self.show_quit_confirm = True

                    elif self.state == STATE_PLAYING:
                        if event.key == pygame.K_SPACE:
                            self.shoot_laser()
                        elif event.key == pygame.K_z:
                            self.drop_dynamite()
                        elif event.key == pygame.K_ESCAPE:
                            # Stop helicopter sound
                            self.sound_manager.stop_loop('helicopter')
                            # Return to splash screen
                            self.state = STATE_SPLASH

                    elif self.state == STATE_ENTERING_NAME:
                        # Sin score, solo ENTER para volver al splash
                        if self.score <= 0 and not self.is_victory:
                            if event.key == pygame.K_RETURN:
                                self.state = STATE_SPLASH
                        elif event.key == pygame.K_RETURN:
                            if len(self.player_name) > 0:
                                add_score(self.player_name, self.score)
                                self.player_name = ""
                                self.state = STATE_SPLASH
                        elif event.key == pygame.K_BACKSPACE:
                            self.player_name = self.player_name[:-1]
                        elif event.unicode.isalnum() and len(self.player_name) < 10:
                            self.player_name += event.unicode.upper()

                elif event.type == pygame.JOYBUTTONDOWN:
                    if self.state == STATE_SPLASH:
                        if event.button == 0:  # A
                            self.level_num = 0
                            self.score = 0
                            self.lives = INITIAL_LIVES
                            self.dynamite_count = 6
                            self.last_life_score = 0
                            self.start_level()

                    elif self.state == STATE_PLAYING:
                        if event.button == 2:  # X
                            self.shoot_laser()
                        elif event.button == 1:  # B
                            self.drop_dynamite()

            # Update
            if self.state == STATE_PLAYING:
                self.update_playing(dt)
            elif self.state == STATE_DYING:
                self.update_dying(dt)
            elif self.state == STATE_LEVEL_COMPLETE:
                self.update_level_complete(dt)

            # Splash theme music management
            if 'splash_theme' in self.sounds:
                if self.state == STATE_SPLASH:
                    self.sound_manager.start_loop('splash_theme')
                else:
                    self.sound_manager.stop_loop('splash_theme')

            # Death song music management (game over screen)
            if 'death_song' in self.sounds:
                if self.state == STATE_ENTERING_NAME and not self.is_victory:
                    if not self.sound_manager.is_looping('death_song'):
                        self.sounds['death_song'].play()
                        self.sound_manager._loops['death_song'] = True
                else:
                    if self.sound_manager.is_looping('death_song'):
                        self.sounds['death_song'].stop()
                        self.sound_manager._loops['death_song'] = False

            # Render
            self.screen.fill(COLOR_BLACK)

            if self.state == STATE_SPLASH:
                self.render_splash()

            elif self.state == STATE_PLAYING:
                self.game_surface.fill(COLOR_BLACK)
                self.render_level()
                self.render_lamps()

                # Draw entities en game_surface
                if self.miner:
                    self.miner.draw(self.game_surface, self.camera_x, self.camera_y)

                for enemy in self.enemies:
                    enemy.draw(self.game_surface, self.camera_x, self.camera_y, self.level_map,
                               wall_tile=self.tiles.get('wall'))

                for laser in self.lasers:
                    laser.draw(self.game_surface, self.camera_x, self.camera_y)

                if self.player:
                    self.player.draw(self.game_surface, self.camera_x, self.camera_y)

                for dynamite in self.dynamites:
                    dynamite.draw(self.game_surface, self.camera_x, self.camera_y)

                # Oscuridad estilo C64
                self._render_dark_mode_overlay()

                self.render_floating_scores()
                self._render_game_to_screen()
                self.render_hud()

            elif self.state == STATE_DYING:
                self.render_dying()

            elif self.state == STATE_LEVEL_COMPLETE:
                self.render_level_complete()

            elif self.state == STATE_ENTERING_NAME:
                self.render_entering_name()

            # Quit confirmation overlay
            if self.show_quit_confirm:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(220)
                overlay.fill(COLOR_BLACK)
                self.screen.blit(overlay, (0, 0))

                quit_text = self.font.render("Do you want to quit (Y/N)?", True, COLOR_WHITE)
                quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
                self.screen.blit(quit_text, quit_rect)

            # Escalar game surface al display manteniendo aspect ratio
            self.display_surface.fill(COLOR_BLACK)
            scaled = pygame.transform.scale(self.screen, (self.render_w, self.render_h))
            self.display_surface.blit(scaled, (self.render_x, self.render_y))
            pygame.display.flip()

        pygame.quit()

##################################################################################################
# Main
##################################################################################################
def main():
    parser = argparse.ArgumentParser(description="H.E.R.O. Remake")
    parser.add_argument("--level", type=int, default=None,
                        help="Nivel inicial (1-N) para testing")
    args = parser.parse_args()

    game = Game()
    game.init()

    # Si se especificó --level, arrancar directo en ese nivel
    if args.level is not None:
        level_idx = args.level - 1  # El usuario pasa 1-based
        if level_idx < 0 or level_idx >= len(LEVELS):
            print(f"Nivel inválido. Disponibles: 1-{len(LEVELS)}")
            pygame.quit()
            return
        game.level_num = level_idx
        game.score = 0
        game.lives = INITIAL_LIVES
        game.dynamite_count = 6
        game.last_life_score = 0
        game.start_level()

    try:
        game.loop()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
