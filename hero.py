# H.E.R.O. Remake - CORRECTO basado en Atari 2600
# Helicopter Emergency Rescue Operation

import pygame
import json
import os
import math
import array
import random

# Import constants
from constants import *

# Import game classes
from laser import Laser
from dynamite import Dynamite
from enemy import Enemy
from miner import Miner
from player import Player
from audio_effects import apply_sid_to_sound

##################################################################################################
# Utility Functions
##################################################################################################

def load_scores():
    """Load high scores from JSON file"""
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, 'r') as f:
                scores = json.load(f)
                if isinstance(scores, list):
                    return scores
        except:
            pass
    return []

def save_scores(scores):
    """Save high scores to JSON file"""
    try:
        with open(SCORES_FILE, 'w') as f:
            json.dump(scores, f, indent=2)
    except Exception as e:
        print(f"Error saving scores: {e}")

def add_score(name, score):
    """Add a new score and keep only top 10"""
    scores = load_scores()
    scores.append({"name": name, "score": score})
    scores.sort(key=lambda x: x["score"], reverse=True)
    scores = scores[:10]
    save_scores(scores)
    return scores

##################################################################################################
# Level Generator
##################################################################################################
# Niveles cargados desde screens.json
# Leyenda:
#   S = Start (jugador)
#   M = Miner (persona a rescatar)
#   E = Enemy bat (murciélago)
#   A = Spider (araña)
#   B = Bloque destructible (solo se rompe con dinamita)
#   # = Pared sólida
#   . = Suelo/plataforma
#   (espacio) = Aire

def load_levels_from_file():
    """Cargar niveles desde screens.json"""
    if os.path.exists(SCREENS_FILE):
        try:
            with open(SCREENS_FILE, 'r', encoding='utf-8') as f:
                screens = json.load(f)
                levels = []
                for s in screens:
                    level_map = s["map"]
                    # Normalizar dimensiones
                    normalized = []
                    for row in level_map:
                        if len(row) < LEVEL_WIDTH:
                            row = row + '#' * (LEVEL_WIDTH - len(row))
                        normalized.append(row[:LEVEL_WIDTH])
                    while len(normalized) < LEVEL_HEIGHT:
                        normalized.append('#' * LEVEL_WIDTH)
                    levels.append(normalized[:LEVEL_HEIGHT])
                return levels
        except Exception as e:
            print(f"Error cargando niveles: {e}")
    return []

LEVELS = load_levels_from_file()

def generate_level(level_num):
    """Return a level loaded from screens.json"""
    if len(LEVELS) == 0:
        print("ERROR: No se encontraron niveles en screens.json")
        # Nivel de emergencia
        empty = ['#' * LEVEL_WIDTH] * LEVEL_HEIGHT
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
        self.xbox_controller = None
        self.tiles = {}
        self.sprites = {}
        self.sounds = {}
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
        self.lives = 5
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

        # Camera
        self.camera_y = 0

        # Input
        self.keys = []
        self.joy_axis_x = 0
        self.joy_axis_y = 0

        # Timers
        self.shoot_cooldown = 0
        self.level_complete_timer = 0

        # Sound state
        self.helicopter_playing = False
        self.splash_theme_playing = False

        # Quit confirmation
        self.show_quit_confirm = False

        # Fullscreen
        self.fullscreen = False
        self.display_surface = None
        self.render_scale = 1.0
        self.render_w = SCREEN_WIDTH
        self.render_h = SCREEN_HEIGHT
        self.render_x = 0
        self.render_y = 0

        # Name entry
        self.player_name = ""

        # Score tracking
        self.last_life_score = 0

        # Explosion flash effect
        self.explosion_flash = False
        self.explosion_flash_timer = 0

        # Floating score texts
        self.floating_scores = []

        # Level complete animation (ColecoVision style)
        self.level_complete_phase = 0     # 0=energy drain, 1=bombs, 2=display
        self.bomb_explosion_effects = []  # Efectos activos de explosion en HUD
        self.score_beep_timer = 0         # Timer entre beeps
        self.score_beep_index = 0         # Indice del beep actual (para pitch ascendente)
        self.bomb_explode_timer = 0       # Timer entre explosiones de bombas
        self.score_beeps = []             # Beep sounds pre-generados

    def init(self):
        """Initialize pygame and resources"""
        pygame.init()
        pygame.mixer.init()

        # Initialize joysticks
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()

        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            if "Xbox" in joystick.get_name() or "Controller" in joystick.get_name():
                self.xbox_controller = joystick
                self.xbox_controller.init()
                print(f"Controller found: {joystick.get_name()}")
                break

        self.display_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.fullscreen = True
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._update_scaling()
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("H.E.R.O. - Atari 2600 Remake")

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

        # Destructible block tile (B)
        self.tiles['block'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.tiles['block'].fill(COLOR_MAGENTA)
        pygame.draw.rect(self.tiles['block'], (200, 0, 200), (2, 2, 28, 28))

        # Breakable wall tile (W)
        try:
            self.tiles['breakable'] = pygame.image.load("tiles/breakable_wall.png").convert_alpha()
        except:
            self.tiles['breakable'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['breakable'].fill((180, 170, 160))

        # Load sprites
        try:
            self.sprites['player'] = pygame.image.load("sprites/player.png").convert_alpha()
            self.sprites['player_shooting'] = pygame.image.load("sprites/player_shooting.png").convert_alpha()
            self.sprites['player_walk1'] = pygame.image.load("sprites/player_walk1.png").convert_alpha()
            self.sprites['player_walk2'] = pygame.image.load("sprites/player_walk2.png").convert_alpha()
            self.sprites['enemy'] = pygame.image.load("sprites/enemy.png").convert_alpha()
            self.sprites['spider'] = pygame.image.load("sprites/spider.png").convert_alpha()
            self.sprites['bomb1'] = pygame.image.load("sprites/bomb1.png").convert_alpha()
            self.sprites['bomb2'] = pygame.image.load("sprites/bomb2.png").convert_alpha()
            self.sprites['bomb3'] = pygame.image.load("sprites/bomb3.png").convert_alpha()
            self.sprites['miner'] = pygame.image.load("sprites/miner.png").convert_alpha()
            print("Sprites loaded successfully")
        except Exception as e:
            print(f"Error loading sprites: {e}")

        # Crear mini-iconos para el HUD (ColecoVision style)
        if 'player' in self.sprites:
            self.hud_player_icon = pygame.transform.scale(self.sprites['player'], (16, 16))
        if 'bomb1' in self.sprites:
            self.hud_bomb_icon = pygame.transform.scale(self.sprites['bomb1'], (16, 16))

        # Load sounds
        try:
            self.sounds['shoot'] = pygame.mixer.Sound("sounds/shoot.wav")
            self.sounds['explosion'] = pygame.mixer.Sound("sounds/explosion.wav")
            self.sounds['death'] = pygame.mixer.Sound("sounds/death.wav")
            self.sounds['splatter'] = pygame.mixer.Sound("sounds/splatter.wav")
            self.sounds['helicopter'] = pygame.mixer.Sound("sounds/helicopter.wav")
            self.sounds['walk'] = pygame.mixer.Sound("sounds/walk.wav")
            self.sounds['win_screen'] = pygame.mixer.Sound("sounds/win_screen.wav")

            # Load splash theme original
            splash_original = pygame.mixer.Sound("sounds/splash_screen_theme.wav")

            # Apply SID emulation effects
            # print("Applying SID effects to splash theme...")
            # self.sounds['splash_theme'] = apply_sid_to_sound(
            #     splash_original,
            #     intensity=SID_INTENSITY
            # )
            # print(f"SID effects applied (intensity: {SID_INTENSITY})")
            self.sounds['splash_theme'] = splash_original

            print("Sounds loaded successfully")
        except Exception as e:
            print(f"Error loading sounds: {e}")
            
        # Load background image
        try:
            self.background_image = pygame.image.load("images/hero_background.png").convert_alpha()
            self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            self.gray_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.gray_overlay.set_alpha(140)      
            self.gray_overlay.fill((128, 128, 128))
            
            print("Background image loaded successfully")
        except Exception as e:
            print(f"Error loading background image: {e}")

        # Generar beep sounds ascendentes para animacion de score
        self.score_beeps = []
        for i in range(10):
            freq = 400 + i * 80  # 400Hz → 1120Hz
            beep = self._generate_beep(freq, duration_ms=50, volume=0.3)
            self.score_beeps.append(beep)

    def _generate_beep(self, frequency, duration_ms=50, volume=0.3):
        """Genera un sonido corto sine wave sin dependencia de numpy"""
        mixer_info = pygame.mixer.get_init()
        sample_rate, bit_size, channels = mixer_info
        n_samples = int(sample_rate * duration_ms / 1000)
        samples = []
        max_val = int(32767 * volume)
        for i in range(n_samples):
            val = int(max_val * math.sin(2 * math.pi * frequency * i / sample_rate))
            samples.append(val)
            if channels == 2:
                samples.append(val)  # duplicar para stereo
        return pygame.mixer.Sound(buffer=array.array('h', samples))

    def toggle_fullscreen(self):
        """Alternar entre ventana y pantalla completa"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.display_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._update_scaling()

    def _update_scaling(self):
        """Calcular escala y offset para mantener aspect ratio"""
        display_w, display_h = self.display_surface.get_size()
        scale_x = display_w / SCREEN_WIDTH
        scale_y = display_h / SCREEN_HEIGHT
        self.render_scale = min(scale_x, scale_y)
        self.render_w = int(SCREEN_WIDTH * self.render_scale)
        self.render_h = int(SCREEN_HEIGHT * self.render_scale)
        self.render_x = (display_w - self.render_w) // 2
        self.render_y = (display_h - self.render_h) // 2

    def _generate_cave_background(self):
        """Genera superficie de fondo con pintitas simulando textura de caverna"""
        width = LEVEL_WIDTH * TILE_SIZE
        height = LEVEL_HEIGHT * TILE_SIZE
        self.cave_bg = pygame.Surface((width, height))
        self.cave_bg.fill(COLOR_BLACK)

        # Colores en escalas de marron (textura de roca/caverna)
        dot_colors = [
            (45, 30, 15),
            (55, 35, 18),
            (40, 25, 12),
            (50, 32, 20),
            (35, 22, 10),
            (60, 40, 22),
        ]

        # Densidad baja: ~0.1% del area total
        num_dots = int(width * height * 0.001)

        for _ in range(num_dots):
            dx = random.randint(0, width - CAVE_DOT_SIZE)
            dy = random.randint(0, height - CAVE_DOT_SIZE)
            color = random.choice(dot_colors)
            if CAVE_DOT_SIZE <= 1:
                self.cave_bg.set_at((dx, dy), color)
            else:
                pygame.draw.rect(self.cave_bg, color,
                                 (dx, dy, CAVE_DOT_SIZE, CAVE_DOT_SIZE))

    def start_level(self):
        """Start a new level"""
        self.state = STATE_PLAYING
        self.energy = MAX_ENERGY
        self.dynamite_count = DYNAMITE_QUANTITY  # Restore bombs for new level

        # Stop helicopter sound when starting new level
        if hasattr(self, 'helicopter_playing') and self.helicopter_playing:
            self.sounds['helicopter'].stop()
            self.helicopter_playing = False

        # Generate level
        self.level_map = generate_level(self.level_num)

        # Generar fondo de caverna con pintitas
        self._generate_cave_background()

        # Clear entities
        self.enemies = []
        self.lasers = []
        self.dynamites = []
        self.miner = None
        self.floating_scores = []

        # Create player
        self.player = Player()
        self.player.init(self.level_map)
        if 'player' in self.sprites:
            self.player.image = self.sprites['player']
        if 'player_shooting' in self.sprites:
            self.player.image_shooting = self.sprites['player_shooting']
        if 'player_walk1' in self.sprites and 'player_walk2' in self.sprites:
            self.player.walk_frames = [self.sprites['player_walk1'], self.sprites['player_walk2']]
        if 'walk' in self.sounds:
            self.player.walk_sound = self.sounds['walk']

        # Parse level and create entities
        for row_index, row in enumerate(self.level_map):
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE

                if tile == "E":
                    enemy = Enemy(x, y, "bat")
                    if 'enemy' in self.sprites:
                        enemy.image = self.sprites['enemy']
                    self.enemies.append(enemy)
                elif tile == "A":
                    enemy = Enemy(x, y, "spider")
                    if 'spider' in self.sprites:
                        enemy.image = self.sprites['spider']
                    self.enemies.append(enemy)
                elif tile == "M":
                    self.miner = Miner(x, y)
                    if 'miner' in self.sprites:
                        self.miner.image = self.sprites['miner']

        # Reset camera to player
        self.camera_y = self.player.y - VIEWPORT_HEIGHT / 2

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
            self.shoot_cooldown = 0.2

            # Activar sprite de disparo
            self.player.shooting_timer = 0.15

            if 'shoot' in self.sounds:
                self.sounds['shoot'].play()

    def drop_dynamite(self):
        """Player drops dynamite"""
        if self.dynamite_count > 0:
            # Coloca la bomba enfrente del héroe según su dirección
            offset_x = 24 if self.player.facing_right else -8
            dynamite = Dynamite(self.player.x + offset_x, self.player.y + 16)
            if 'bomb1' in self.sprites:
                dynamite.explosion_sprites = [
                    self.sprites['bomb1'],
                    self.sprites['bomb2'],
                    self.sprites['bomb3'],
                ]
            self.dynamites.append(dynamite)
            self.dynamite_count -= 1

    def update_camera(self):
        """Update camera to follow player"""
        target_y = self.player.y - VIEWPORT_HEIGHT / 2

        # Smooth camera
        self.camera_y += (target_y - self.camera_y) * 0.1

        # Keep camera in bounds
        self.camera_y = max(0, min(self.camera_y,
                                   LEVEL_HEIGHT * TILE_SIZE - VIEWPORT_HEIGHT))

    def check_collisions(self):
        """Check all collisions"""
        if not self.player:
            return

        player_rect = self.player.get_rect()

        # Player vs enemies
        for enemy in self.enemies:
            if enemy.active and player_rect.colliderect(enemy.get_rect()):
                self.player_hit()
                return

        # Player vs miner
        if self.miner and not self.miner.rescued:
            if player_rect.colliderect(self.miner.get_rect()):
                self.rescue_miner()
                return

        # Lasers vs enemies
        for laser in self.lasers[:]:
            if not laser.active:
                continue
            laser_rect = laser.get_rect()
            for enemy in self.enemies:
                if enemy.active and not enemy.exploding and laser_rect.colliderect(enemy.get_rect()):
                    enemy.exploding = True
                    laser.active = False
                    self.score += 50
                    self.add_floating_score(enemy.x + 16, enemy.y, 50)

                    # Play splatter sound
                    if 'splatter' in self.sounds:
                        self.sounds['splatter'].play()

                    break

        # Dynamite explosions
        for dynamite in self.dynamites[:]:
            if dynamite.exploded:
                explosion_rect = dynamite.get_explosion_rect()
                if explosion_rect:
                    # Check if player is in blast radius
                    if player_rect.colliderect(explosion_rect):
                        self.player_hit()
                        return

                    # Destroy enemies
                    for enemy in self.enemies:
                        if enemy.active and not enemy.exploding and explosion_rect.colliderect(enemy.get_rect()):
                            enemy.exploding = True
                            self.score += 75
                            self.add_floating_score(enemy.x + 16, enemy.y, 75)

                            # Play splatter sound
                            if 'splatter' in self.sounds:
                                self.sounds['splatter'].play()

                    # Destroy blocks and walls
                    for row_index in range(len(self.level_map)):
                        for col_index in range(len(self.level_map[row_index])):
                            tile = self.level_map[row_index][col_index]
                            if tile in ('B', '#', 'W'):  # Destruye bloques, paredes y rompibles
                                tile_x = col_index * TILE_SIZE
                                tile_y = row_index * TILE_SIZE
                                tile_rect = pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE)

                                if explosion_rect.colliderect(tile_rect):
                                    row = list(self.level_map[row_index])
                                    row[col_index] = ' '
                                    self.level_map[row_index] = "".join(row)
                                    # Más puntos por destruir paredes que bloques
                                    pts = 20 if tile == '#' else 10
                                    self.score += pts
                                    self.add_floating_score(tile_x + 16, tile_y, pts)

                    # Play sound once
                    if 'explosion' in self.sounds and dynamite.explosion_time > 0.4:
                        self.sounds['explosion'].play()

    def player_hit(self):
        """Player takes damage"""
        self.lives -= 1

        # Stop helicopter sound
        if hasattr(self, 'helicopter_playing') and self.helicopter_playing:
            self.sounds['helicopter'].stop()
            self.helicopter_playing = False

        # Play death sound
        if 'death' in self.sounds:
            self.sounds['death'].play()

        if self.lives <= 0:
            self.state = STATE_ENTERING_NAME
        else:
            self.start_level()

    def rescue_miner(self):
        """Rescue miner and complete level - inicia animacion ColecoVision"""
        self.miner.rescued = True
        self.score += 1000  # Solo puntos base por rescate

        # Stop helicopter sound
        if hasattr(self, 'helicopter_playing') and self.helicopter_playing:
            self.sounds['helicopter'].stop()
            self.helicopter_playing = False

        # Inicializar animacion de level complete
        self.state = STATE_LEVEL_COMPLETE
        self.score_beep_timer = 0
        self.score_beep_index = 0
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
        self.floating_scores.append({
            'x': x,
            'y': y,
            'text': str(points),
            'timer': 1.0,
            'max_timer': 1.0,
        })

    def render_floating_scores(self):
        """Renderiza los textos flotantes de puntuacion"""
        cv_yellow = (212, 193, 84)
        for fs in self.floating_scores:
            alpha = int(255 * (fs['timer'] / fs['max_timer']))
            text_surf = self.hud_font.render(fs['text'], True, cv_yellow)

            # Posicion en coordenadas de pantalla
            screen_x = int(fs['x']) - text_surf.get_width() // 2
            screen_y = int(fs['y']) - int(self.camera_y)

            # Clampar dentro de los margenes de las paredes externas
            screen_x = max(TILE_SIZE, min(screen_x, (LEVEL_WIDTH - 1) * TILE_SIZE - text_surf.get_width()))
            screen_y = max(0, min(screen_y, VIEWPORT_HEIGHT - text_surf.get_height()))

            # Aplicar alpha con surface transparente
            alpha_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
            text_surf_alpha = self.hud_font.render(fs['text'], True, (*cv_yellow, alpha))
            alpha_surf.blit(text_surf_alpha, (0, 0))

            self.screen.blit(alpha_surf, (screen_x, screen_y))

    def next_level(self):
        """Advance to next level"""
        self.level_num += 1
        if self.level_num >= len(LEVELS):
            # Won game!
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

        # Helicopter sound when flying (in the air, not on ground)
        if 'helicopter' in self.sounds:
            # Play sound when player is in the air (not grounded)
            if not self.player.is_grounded:
                # Start playing if not already
                if not hasattr(self, 'helicopter_playing') or not self.helicopter_playing:
                    self.sounds['helicopter'].play(loops=-1)  # Loop indefinitely
                    self.helicopter_playing = True
            else:
                # Stop playing if it's playing (player is on ground)
                if hasattr(self, 'helicopter_playing') and self.helicopter_playing:
                    self.sounds['helicopter'].stop()
                    self.helicopter_playing = False

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
            if not laser.active:
                self.lasers.remove(laser)

        # Update dynamites
        for dynamite in self.dynamites[:]:
            dynamite.update(dt, self.level_map)
            if not dynamite.active:
                self.dynamites.remove(dynamite)

        # Update floating scores
        for fs in self.floating_scores[:]:
            fs['timer'] -= dt
            fs['y'] -= 30 * dt  # flota hacia arriba
            if fs['timer'] <= 0:
                self.floating_scores.remove(fs)

        # Check collisions
        self.check_collisions()

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

            # Beeps ascendentes cada ~80ms
            self.score_beep_timer += dt
            if self.score_beep_timer >= 0.08 and self.score_beeps:
                self.score_beep_timer -= 0.08
                beep_idx = min(self.score_beep_index, len(self.score_beeps) - 1)
                self.score_beeps[beep_idx].play()
                self.score_beep_index = (self.score_beep_index + 1) % len(self.score_beeps)

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
                # Posicion de la bomba mas a la izquierda (la que va a explotar)
                bx = ce - bomb_count * (16 + icon_gap) + icon_gap
                by = icons_y

                # Crear efecto de explosion en esa posicion
                self.bomb_explosion_effects.append({
                    'x': bx + 8,  # Centro del icono
                    'y': by + 8,
                    'timer': 0.4,
                    'max_timer': 0.4
                })

                self.dynamite_count -= 1
                self.score += 50

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

    def render_level(self):
        """Render visible part of level"""
        # Usar offset entero consistente para fondo y tiles
        cam_y = int(self.camera_y)

        # Dibujar fondo de caverna (o flash blanco si hay explosion)
        if self.explosion_flash:
            self.screen.fill(COLOR_WHITE, (0, 0, LEVEL_WIDTH * TILE_SIZE, VIEWPORT_HEIGHT))
        elif self.cave_bg:
            src_rect = pygame.Rect(0, cam_y, LEVEL_WIDTH * TILE_SIZE, VIEWPORT_HEIGHT)
            self.screen.blit(self.cave_bg, (0, 0), src_rect)

        # Calculate visible tiles
        start_row = max(0, cam_y // TILE_SIZE - 1)
        end_row = min(LEVEL_HEIGHT, (cam_y + VIEWPORT_HEIGHT) // TILE_SIZE + 2)

        for row_index in range(start_row, end_row):
            if row_index >= len(self.level_map):
                break

            row = self.level_map[row_index]
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE - cam_y

                if tile == '#':
                    self.screen.blit(self.tiles['wall'], (x, y))
                elif tile == '.':
                    self.screen.blit(self.tiles['floor'], (x, y))
                elif tile == 'B':
                    self.screen.blit(self.tiles['block'], (x, y))
                elif tile == 'W':
                    self.screen.blit(self.tiles['breakable'], (x, y))
                # Espacios vacios: no dibujar nada, el cave_bg ya se ve

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

        # Iconos de bombas (alineados a la derecha)
        bomb_count = max(0, min(self.dynamite_count, 10))
        for i in range(bomb_count):
            bx = ce - (bomb_count - i) * (16 + icon_gap)
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

    def draw_text_with_outline(self, font, text, color, outline_color, center, outline=1):
        # Texto base
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=center)

        # Outline (dibujos alrededor)
        for dx in (-outline, 0, outline):
            for dy in (-outline, 0, outline):
                if dx != 0 or dy != 0:
                    outline_surf = font.render(text, True, outline_color)
                    outline_rect = outline_surf.get_rect(center=(center[0] + dx, center[1] + dy))
                    self.screen.blit(outline_surf, outline_rect)

        # Texto principal arriba
        self.screen.blit(text_surf, text_rect)


    def render_splash(self):
        """Render splash screen"""
        self.screen.blit(self.background_image, (0, 0))
        self.screen.blit(self.gray_overlay, (0, 0))


        """
        title = self.font.render("H.E.R.O.", True, COLOR_WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 80))
        self.screen.blit(title, title_rect)

        subtitle = self.small_font.render("Helicopter Emergency", True, COLOR_GRAY)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 120))
        self.screen.blit(subtitle, subtitle_rect)

        subtitle2 = self.small_font.render("Rescue Operation", True, COLOR_GRAY)
        subtitle2_rect = subtitle2.get_rect(center=(SCREEN_WIDTH//2, 140))
        self.screen.blit(subtitle2, subtitle2_rect)
        """

        self.draw_text_with_outline(self.small_font, "Press SPACE to Play", COLOR_WHITE, COLOR_BLACK, (SCREEN_WIDTH//2, 200))
        self.draw_text_with_outline(self.small_font, "Press ESC to Quit", COLOR_WHITE, COLOR_BLACK, (SCREEN_WIDTH//2, 230))
        self.draw_text_with_outline(self.small_font, "CONTROLS", COLOR_WHITE, COLOR_BLACK, (SCREEN_WIDTH//2, 270))
        self.draw_text_with_outline(self.small_font, "Arrows: Move/Fly", COLOR_WHITE, COLOR_BLACK, (SCREEN_WIDTH//2, 295))
        self.draw_text_with_outline(self.small_font, "SPACE: Shoot", COLOR_WHITE, COLOR_BLACK, (SCREEN_WIDTH//2, 315))
        self.draw_text_with_outline(self.small_font, "Z: Drop Bomb", COLOR_WHITE, COLOR_BLACK, (SCREEN_WIDTH//2, 335))
        self.draw_text_with_outline(self.small_font, "Xbox: Stick/X/B", COLOR_WHITE, COLOR_BLACK, (SCREEN_WIDTH//2, 355))
        self.draw_text_with_outline(self.small_font, "HIGH SCORES", COLOR_WHITE, COLOR_BLACK, (SCREEN_WIDTH//2, 390))

        scores = load_scores()[:3]
        for i, score in enumerate(scores):
            self.draw_text_with_outline(self.small_font, f"{i+1}. {score['name']}: {score['score']}", COLOR_WHITE, COLOR_BLACK, (SCREEN_WIDTH//2, 420 + i*20))

    def render_entering_name(self):
        """Render name entry screen"""
        self.screen.fill(COLOR_BLACK)

        game_over = self.font.render("GAME OVER", True, COLOR_RED)
        go_rect = game_over.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(game_over, go_rect)

        score_text = self.small_font.render(f"Final Score: {self.score}", True, COLOR_WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(score_text, score_rect)

        prompt = self.small_font.render("Enter Your Name:", True, COLOR_WHITE)
        prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(prompt, prompt_rect)

        name = self.font.render(self.player_name + "_", True, COLOR_GREEN)
        name_rect = name.get_rect(center=(SCREEN_WIDTH//2, 240))
        self.screen.blit(name, name_rect)

        instr = self.small_font.render("Press ENTER when done", True, COLOR_GRAY)
        instr_rect = instr.get_rect(center=(SCREEN_WIDTH//2, 300))
        self.screen.blit(instr, instr_rect)

    def render_level_complete(self):
        """Render level complete - fases 0 y 1 muestran juego + HUD, fase 2 agrega overlay"""
        self.render_level()

        if self.miner:
            self.miner.draw(self.screen, self.camera_y)

        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera_y)

        for laser in self.lasers:
            laser.draw(self.screen, self.camera_y)

        for dynamite in self.dynamites:
            dynamite.draw(self.screen, self.camera_y)

        if self.player:
            self.player.draw(self.screen, self.camera_y)

        self.render_floating_scores()
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

            # Get input
            self.keys = pygame.key.get_pressed()

            if self.xbox_controller:
                self.joy_axis_x = self.xbox_controller.get_axis(0)
                self.joy_axis_y = self.xbox_controller.get_axis(1)

                if abs(self.joy_axis_x) < DEAD_ZONE:
                    self.joy_axis_x = 0
                if abs(self.joy_axis_y) < DEAD_ZONE:
                    self.joy_axis_y = 0
            else:
                self.joy_axis_x = 0
                self.joy_axis_y = 0

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    # Fullscreen toggle (Alt+Enter)
                    if event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT):
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
                            self.lives = 5
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
                            if hasattr(self, 'helicopter_playing') and self.helicopter_playing:
                                self.sounds['helicopter'].stop()
                                self.helicopter_playing = False
                            # Return to splash screen
                            self.state = STATE_SPLASH

                    elif self.state == STATE_ENTERING_NAME:
                        if event.key == pygame.K_RETURN:
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
                            self.lives = 5
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
            elif self.state == STATE_LEVEL_COMPLETE:
                self.update_level_complete(dt)

            # Splash theme music management
            if 'splash_theme' in self.sounds:
                if self.state == STATE_SPLASH:
                    # Start playing if not already
                    if not self.splash_theme_playing:
                        self.sounds['splash_theme'].play(loops=-1)  # Loop indefinitely
                        self.splash_theme_playing = True
                else:
                    # Stop playing if we're not in splash screen
                    if self.splash_theme_playing:
                        self.sounds['splash_theme'].stop()
                        self.splash_theme_playing = False

            # Render
            self.screen.fill(COLOR_BLACK)

            if self.state == STATE_SPLASH:
                self.render_splash()

            elif self.state == STATE_PLAYING:
                self.render_level()

                # Draw entities
                if self.miner:
                    self.miner.draw(self.screen, self.camera_y)

                for enemy in self.enemies:
                    enemy.draw(self.screen, self.camera_y)

                for laser in self.lasers:
                    laser.draw(self.screen, self.camera_y)

                for dynamite in self.dynamites:
                    dynamite.draw(self.screen, self.camera_y)

                if self.player:
                    self.player.draw(self.screen, self.camera_y)

                self.render_floating_scores()
                self.render_hud()

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
    game = Game()
    game.init()

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
