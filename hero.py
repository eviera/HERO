# H.E.R.O. Remake - CORRECTO basado en Atari 2600
# Helicopter Emergency Rescue Operation

import pygame
import json
import os

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
# NIVELES FIJOS - No procedurales
# Leyenda:
#   S = Start (jugador)
#   M = Miner (persona a rescatar)
#   E = Enemy bat (murciélago)
#   A = Spider (araña)
#   B = Bloque destructible (solo se rompe con dinamita)
#   # = Pared sólida
#   . = Suelo/plataforma
#   (espacio) = Aire

LEVELS = [
    # Nivel 1 - Tutorial: Rescate con dinamita
    [
        "################",
        "#  S           #",
        "#              #",
        "#              #",
        "#      E       #",
        "#              #",
        "#  BBB         #",
        "#  ###.......  #",
        "#              #",
        "#              #",
        "#   E          #",
        "#              #",
        "#     BBB      #",
        "#     ###....  #",
        "#              #",
        "#              #",
        "#        A     #",
        "#              #",
        "#              #",
        "#              #",
        "#              #",
        "#      ###     #",
        "#      #M#     #",
        "#..............#",
        "################",
        "################",
        "################",
        "################",
        "################"
    ],
    # Nivel 2 - Más enemigos
    [
        "################",
        "#       S      #",
        "#              #",
        "#              #",
        "#   E      E   #",
        "#              #",
        "#    BBBBB     #",
        "#    #####...  #",
        "#              #",
        "#              #",
        "#     A        #",
        "#              #",
        "#   BBB   BBB  #",
        "#   ###   ###  #",
        "#              #",
        "#              #",
        "#  E       A   #",
        "#              #",
        "#     BBBBB    #",
        "#     #####..  #",
        "#              #",
        "#              #",
        "#       M      #",
        "#..............#",
        "################",
        "################",
        "################",
        "################",
        "################",
        "################"
    ],
    # Nivel 3 - Laberinto estrecho
    [
        "################",
        "#      S       #",
        "#              #",
        "#              #",
        "#  E           #",
        "#              #",
        "#  BBB    #####",
        "#  ###    #####",
        "#         #####",
        "#      A       #",
        "#              #",
        "#####          #",
        "#####     #####",
        "#####     #####",
        "#   BBB   #####",
        "#   ###   #####",
        "#     E        #",
        "#              #",
        "#####     #####",
        "#####     #####",
        "#    BBBBB     #",
        "#    #####...  #",
        "#              #",
        "#       M      #",
        "#..............#",
        "################",
        "################",
        "################",
        "################",
        "################"
    ],
    # Nivel 4 - Muchos bloques
    [
        "################",
        "#       S      #",
        "#              #",
        "#              #",
        "#        E     #",
        "# BBBBBBBBBBB  #",
        "# ############ #",
        "#              #",
        "#    A         #",
        "# BBBBBBBBBBB  #",
        "# ############ #",
        "#              #",
        "#        E     #",
        "# BBBBBBBBBBB  #",
        "# ############ #",
        "#              #",
        "#    A         #",
        "# BBBBBBBBBBB  #",
        "# ############ #",
        "#              #",
        "#              #",
        "#       M      #",
        "#..............#",
        "################",
        "################",
        "################",
        "################",
        "################",
        "################",
        "################"
    ],
    # Nivel 5 - Difícil
    [
        "################",
        "#      S       #",
        "#              #",
        "#              #",
        "#   E          #",
        "#   BBB        #",
        "#   ###   #####",
        "#         #####",
        "#####     #####",
        "#####          #",
        "#####  A       #",
        "#####          #",
        "#####     #####",
        "#####     #####",
        "#    E    #####",
        "#  BBB    #####",
        "#  ###    #####",
        "#         #####",
        "#####     #####",
        "#####          #",
        "#####  A       #",
        "#    BBBBB     #",
        "#    #####...  #",
        "#              #",
        "#       M      #",
        "#..............#",
        "################",
        "################",
        "################",
        "################"
    ]
]

def generate_level(level_num):
    """Return a fixed level from LEVELS array"""
    if level_num < 0 or level_num >= len(LEVELS):
        level_num = 0
    return LEVELS[level_num]

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

        # Name entry
        self.player_name = ""

        # Score tracking
        self.last_life_score = 0

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

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("H.E.R.O. - Atari 2600 Remake")

        # Load fonts
        try:
            self.font = pygame.font.Font("fonts/PressStart2P-vaV7.ttf", 16)
            self.small_font = pygame.font.Font("fonts/PressStart2P-vaV7.ttf", 13)
        except:
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 16)

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

        # Destructible block tile
        self.tiles['block'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.tiles['block'].fill(COLOR_MAGENTA)
        pygame.draw.rect(self.tiles['block'], (200, 0, 200), (2, 2, 28, 28))

        # Load sprites
        try:
            self.sprites['player'] = pygame.image.load("sprites/player.png").convert_alpha()
            self.sprites['enemy'] = pygame.image.load("sprites/enemy.png").convert_alpha()
            self.sprites['spider'] = pygame.image.load("sprites/spider.png").convert_alpha()
            self.sprites['bomb'] = pygame.image.load("sprites/bomb.png").convert_alpha()
            self.sprites['miner'] = pygame.image.load("sprites/miner.png").convert_alpha()
            print("Sprites loaded successfully")
        except Exception as e:
            print(f"Error loading sprites: {e}")

        # Load sounds
        try:
            self.sounds['shoot'] = pygame.mixer.Sound("sounds/shoot.wav")
            self.sounds['explosion'] = pygame.mixer.Sound("sounds/explosion.wav")
            self.sounds['death'] = pygame.mixer.Sound("sounds/death.wav")
            self.sounds['splatter'] = pygame.mixer.Sound("sounds/splatter.wav")
            self.sounds['helicopter'] = pygame.mixer.Sound("sounds/helicopter.wav")

            # Load splash theme original
            splash_original = pygame.mixer.Sound("sounds/splash_screen_theme.wav")

            # Apply SID emulation effects
            print("Applying SID effects to splash theme...")
            self.sounds['splash_theme'] = apply_sid_to_sound(
                splash_original,
                intensity=SID_INTENSITY
            )
            print(f"SID effects applied (intensity: {SID_INTENSITY})")

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

        # Clear entities
        self.enemies = []
        self.lasers = []
        self.dynamites = []
        self.miner = None

        # Create player
        self.player = Player()
        self.player.init(self.level_map)
        if 'player' in self.sprites:
            self.player.image = self.sprites['player']

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
            laser = Laser(self.player.x + 16, self.player.y + 16, direction)
            self.lasers.append(laser)
            self.shoot_cooldown = 0.2

            if 'shoot' in self.sounds:
                self.sounds['shoot'].play()

    def drop_dynamite(self):
        """Player drops dynamite"""
        if self.dynamite_count > 0:
            # Coloca la bomba enfrente del héroe según su dirección
            offset_x = 24 if self.player.facing_right else -8
            dynamite = Dynamite(self.player.x + offset_x, self.player.y + 16)
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

                            # Play splatter sound
                            if 'splatter' in self.sounds:
                                self.sounds['splatter'].play()

                    # Destroy blocks and walls
                    for row_index in range(len(self.level_map)):
                        for col_index in range(len(self.level_map[row_index])):
                            tile = self.level_map[row_index][col_index]
                            if tile == 'B' or tile == '#':  # Destruye bloques Y paredes
                                tile_x = col_index * TILE_SIZE
                                tile_y = row_index * TILE_SIZE
                                tile_rect = pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE)

                                if explosion_rect.colliderect(tile_rect):
                                    row = list(self.level_map[row_index])
                                    row[col_index] = ' '
                                    self.level_map[row_index] = "".join(row)
                                    # Más puntos por destruir paredes que bloques
                                    self.score += 20 if tile == '#' else 10

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
        """Rescue miner and complete level"""
        self.miner.rescued = True
        bonus = int(self.energy) + (self.dynamite_count * 50)
        self.score += 1000 + bonus

        # Stop helicopter sound
        if hasattr(self, 'helicopter_playing') and self.helicopter_playing:
            self.sounds['helicopter'].stop()
            self.helicopter_playing = False

        self.state = STATE_LEVEL_COMPLETE
        self.level_complete_timer = 2.0

    def next_level(self):
        """Advance to next level"""
        self.level_num += 1
        if self.level_num >= 5:
            # Won game!
            self.state = STATE_ENTERING_NAME
        else:
            self.start_level()

    def update_playing(self, dt):
        """Update game during play"""
        if self.energy <= 0:
            self.player_hit()
            return

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

        # Check collisions
        self.check_collisions()

        # Update timers
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

        # Check for extra life
        if self.score >= self.last_life_score + 20000:
            self.lives += 1
            self.last_life_score = self.score

    def update_level_complete(self, dt):
        """Update level complete state"""
        self.level_complete_timer -= dt
        if self.level_complete_timer <= 0:
            self.next_level()

    def render_level(self):
        """Render visible part of level"""
        # Calculate visible tiles
        start_row = max(0, int(self.camera_y / TILE_SIZE) - 1)
        end_row = min(LEVEL_HEIGHT, int((self.camera_y + VIEWPORT_HEIGHT) / TILE_SIZE) + 2)

        for row_index in range(start_row, end_row):
            if row_index >= len(self.level_map):
                break

            row = self.level_map[row_index]
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE - self.camera_y

                if tile == '#':
                    self.screen.blit(self.tiles['wall'], (x, int(y)))
                elif tile == '.':
                    self.screen.blit(self.tiles['floor'], (x, int(y)))
                elif tile == 'B':
                    self.screen.blit(self.tiles['block'], (x, int(y)))
                else:
                    self.screen.blit(self.tiles['blank'], (x, int(y)))

    def render_hud(self):
        """Render HUD"""
        hud_y = VIEWPORT_HEIGHT
        hud_bg = pygame.Surface((SCREEN_WIDTH, 64))
        hud_bg.fill(COLOR_BLACK)
        self.screen.blit(hud_bg, (0, hud_y))

        # Score
        score_text = self.small_font.render(f"SCORE:{self.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (10, hud_y + 5))

        # Level
        level_text = self.small_font.render(f"LVL:{self.level_num+1}", True, COLOR_WHITE)
        self.screen.blit(level_text, (10, hud_y + 25))

        # Lives
        lives_text = self.small_font.render(f"LIVES:{self.lives}", True, COLOR_WHITE)
        self.screen.blit(lives_text, (150, hud_y + 5))

        # Dynamite
        dyn_text = self.small_font.render(f"BOMBS:{self.dynamite_count}", True, COLOR_WHITE)
        self.screen.blit(dyn_text, (150, hud_y + 25))

        # Energy bar
        energy_text = self.small_font.render("ENERGY", True, COLOR_WHITE)
        self.screen.blit(energy_text, (300, hud_y + 5))

        bar_width = 200
        bar_height = 20
        bar_x = 300
        bar_y = hud_y + 25

        # Background
        pygame.draw.rect(self.screen, COLOR_RED, (bar_x, bar_y, bar_width, bar_height))

        # Energy fill
        energy_width = int((self.energy / MAX_ENERGY) * bar_width)
        if energy_width > 0:
            color = COLOR_GREEN if self.energy > MAX_ENERGY * 0.3 else COLOR_YELLOW if self.energy > MAX_ENERGY * 0.15 else COLOR_RED
            pygame.draw.rect(self.screen, color, (bar_x, bar_y, energy_width, bar_height))

        # Border
        pygame.draw.rect(self.screen, COLOR_WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

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
        """Render level complete overlay"""
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

        self.render_hud()

        # Overlay
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
                    if self.state == STATE_SPLASH:
                        if event.key == pygame.K_SPACE:
                            self.level_num = 0
                            self.score = 0
                            self.lives = 5
                            self.dynamite_count = 6
                            self.last_life_score = 0
                            self.start_level()
                        elif event.key == pygame.K_ESCAPE:
                            running = False

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

                self.render_hud()

            elif self.state == STATE_LEVEL_COMPLETE:
                self.render_level_complete()

            elif self.state == STATE_ENTERING_NAME:
                self.render_entering_name()

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
