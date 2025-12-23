# H.E.R.O. Remake - Complete Game
# Helicopter Emergency Rescue Operation

import pygame
import json
import os
import math

# Window dimensions
SCREEN_WIDTH = 512
SCREEN_HEIGHT = 480
FPS = 60
TILE_SIZE = 32
PLAYER_SPEED = 150
BULLET_SPEED = 300
ENEMY_SPEED = 50
DEAD_ZONE = 0.1
GRAVITY = 600
HOVER_POWER = 500
ENERGY_DRAIN_RATE = 5  # Energy per second
MAX_ENERGY = 100

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

# Level maps (16x13 for game area, plus 2 rows for HUD)
MAPS = [
    # Level 1 - Tutorial level
    [
        "################",
        "S              #",
        "#              #",
        "#    ###       #",
        "#    #E#       #",
        "#    ###       #",
        "#              #",
        "#       B      #",
        "#              #",
        "#     E        #",
        "#          R  ##",
        "#............###",
        "################",
    ],
    # Level 2 - Vertical descent
    [
        "####S###########",
        "####E###########",
        "####.###########",
        "####.######E####",
        "###...##########",
        "####.###########",
        "####.###########",
        "#....E#######E##",
        "##....##########",
        "###..###########",
        "####.R##########",
        "####..##########",
        "################",
    ],
    # Level 3 - Horizontal maze
    [
        "################",
        "S....E....E....#",
        "#..............#",
        "#BBB...BBB...BB#",
        "#..............#",
        "#....E.....E...#",
        "#..............#",
        "#.BBB....BBB.BB#",
        "#..............#",
        "#.....E........#",
        "#..............R",
        "#..............#",
        "################",
    ],
    # Level 4 - Complex structure
    [
        "###S############",
        "###.###E########",
        "##...###########",
        "##.#...##E######",
        "#...###.########",
        "#.###...#####E##",
        "#.#BBB#.########",
        "#....E..########",
        "###.....########",
        "####.#..########",
        "#####.#.##R#####",
        "######...#######",
        "################",
    ],
    # Level 5 - Magma level
    [
        "####S###########",
        "####.###########",
        "###...MMMMMM####",
        "##.....MMMMM####",
        "##.###MMMM######",
        "#...##MMMM###E##",
        "#.E.##MMM#######",
        "#...BBMMM####E##",
        "##...EMMM#######",
        "###...MMM#######",
        "####...MM####R##",
        "#####.......####",
        "################",
    ],
]

# Scores file
SCORES_FILE = "scores.json"

##################################################################################################
# Utility Functions
##################################################################################################

def load_scores():
    """Load high scores from JSON file"""
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, 'r') as f:
                scores = json.load(f)
                # Ensure it's a list
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
    scores = scores[:10]  # Keep only top 10
    save_scores(scores)
    return scores

##################################################################################################
# Bullet Class
##################################################################################################
class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction  # 1 = right, -1 = left
        self.width = 8
        self.height = 4
        self.active = True

    def update(self, dt):
        self.x += self.direction * BULLET_SPEED * dt

        # Check if out of bounds
        if self.x < 0 or self.x > SCREEN_WIDTH:
            self.active = False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_YELLOW, (int(self.x), int(self.y), self.width, self.height))

##################################################################################################
# Bomb/Dynamite Class
##################################################################################################
class Dynamite:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 2.0  # 2 seconds to explode
        self.exploded = False
        self.explosion_timer = 0.3  # Explosion lasts 0.3 seconds
        self.active = True
        self.explosion_radius = 64

    def update(self, dt):
        if not self.exploded:
            self.timer -= dt
            if self.timer <= 0:
                self.exploded = True
        else:
            self.explosion_timer -= dt
            if self.explosion_timer <= 0:
                self.active = False

    def draw(self, screen):
        if not self.exploded:
            # Draw dynamite (red square)
            pygame.draw.rect(screen, COLOR_RED, (int(self.x), int(self.y), 16, 16))
        else:
            # Draw explosion (yellow/orange circle)
            pygame.draw.circle(screen, COLOR_ORANGE, (int(self.x + 8), int(self.y + 8)),
                             int(self.explosion_radius))
            pygame.draw.circle(screen, COLOR_YELLOW, (int(self.x + 8), int(self.y + 8)),
                             int(self.explosion_radius * 0.6))

    def get_explosion_rect(self):
        if self.exploded:
            return pygame.Rect(self.x - self.explosion_radius/2,
                             self.y - self.explosion_radius/2,
                             self.explosion_radius,
                             self.explosion_radius)
        return None

##################################################################################################
# Enemy Class
##################################################################################################
class Enemy:
    def __init__(self, x, y, enemy_type="bat"):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.speed = ENEMY_SPEED
        self.direction = 1  # 1 = right, -1 = left
        self.active = True
        self.width = 32
        self.height = 32

        # AI behavior
        self.move_timer = 0
        self.move_duration = 2.0  # Change direction every 2 seconds

    def update(self, dt, level_map):
        if not self.active:
            return

        # Simple patrol AI
        self.move_timer += dt
        if self.move_timer >= self.move_duration:
            self.direction *= -1
            self.move_timer = 0

        # Move horizontally
        new_x = self.x + self.direction * self.speed * dt

        # Check collision with walls
        if not self.check_wall_collision(new_x, self.y, level_map):
            self.x = new_x
        else:
            self.direction *= -1

    def check_wall_collision(self, x, y, level_map):
        """Check if position collides with walls"""
        tile_x = int(x / TILE_SIZE)
        tile_y = int(y / TILE_SIZE)

        if tile_y < 0 or tile_y >= len(level_map):
            return True
        if tile_x < 0 or tile_x >= len(level_map[0]):
            return True

        tile = level_map[tile_y][tile_x]
        return tile == "#" or tile == "B"

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if self.active:
            # Draw enemy as red circle with wings
            pygame.draw.circle(screen, COLOR_RED, (int(self.x + 16), int(self.y + 16)), 12)
            # Simple wings
            pygame.draw.circle(screen, COLOR_RED, (int(self.x + 8), int(self.y + 16)), 6)
            pygame.draw.circle(screen, COLOR_RED, (int(self.x + 24), int(self.y + 16)), 6)

##################################################################################################
# Miner Class (objective to rescue)
##################################################################################################
class Miner:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rescued = False
        self.width = 32
        self.height = 32

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        if not self.rescued:
            # Draw miner as green person
            pygame.draw.circle(screen, COLOR_GREEN, (int(self.x + 16), int(self.y + 10)), 8)  # Head
            pygame.draw.rect(screen, COLOR_GREEN, (int(self.x + 12), int(self.y + 18), 8, 12))  # Body
            pygame.draw.line(screen, COLOR_GREEN, (int(self.x + 16), int(self.y + 20)),
                           (int(self.x + 10), int(self.y + 26)), 2)  # Arm
            pygame.draw.line(screen, COLOR_GREEN, (int(self.x + 16), int(self.y + 20)),
                           (int(self.x + 22), int(self.y + 26)), 2)  # Arm

##################################################################################################
# Player Class
##################################################################################################
class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 32
        self.height = 32
        self.vel_y = 0
        self.facing_right = True
        self.hovering = False

    def init(self, level_map):
        """Initialize player position from map"""
        for row_index, row in enumerate(level_map):
            for col_index, tile in enumerate(row):
                if tile == "S":
                    self.x = col_index * TILE_SIZE
                    self.y = row_index * TILE_SIZE
                    self.vel_y = 0
                    return

        # Default position if "S" not found
        self.x = TILE_SIZE
        self.y = TILE_SIZE
        self.vel_y = 0

    def update(self, dt, keys, joy_axis_x, joy_axis_y, level_map, game):
        """Update player physics and movement"""

        # Horizontal movement
        move_x = 0
        if keys[pygame.K_LEFT] or joy_axis_x < -DEAD_ZONE:
            move_x = -1
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or joy_axis_x > DEAD_ZONE:
            move_x = 1
            self.facing_right = True

        # Apply horizontal movement
        new_x = self.x + move_x * PLAYER_SPEED * dt
        if not self.check_collision(new_x, self.y, level_map):
            self.x = new_x

        # Hovering (flying up)
        self.hovering = False
        if keys[pygame.K_UP] or joy_axis_y < -DEAD_ZONE:
            self.hovering = True
            self.vel_y = -HOVER_POWER * dt
            # Drain energy while hovering
            game.energy -= ENERGY_DRAIN_RATE * 2 * dt
        else:
            # Apply gravity
            self.vel_y += GRAVITY * dt

        # Apply vertical velocity
        new_y = self.y + self.vel_y

        # Check vertical collision
        if self.check_collision(self.x, new_y, level_map):
            # Hit something, stop vertical movement
            self.vel_y = 0
            # Snap to tile boundary
            if self.vel_y > 0:  # Was falling
                self.y = int(self.y / TILE_SIZE) * TILE_SIZE
        else:
            self.y = new_y

        # Keep in bounds
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height - 64))  # Account for HUD

        # Drain energy over time
        game.energy -= ENERGY_DRAIN_RATE * dt

    def check_collision(self, x, y, level_map):
        """Check if position collides with solid tiles"""
        # Check all four corners of the player
        corners = [
            (x, y),
            (x + self.width - 1, y),
            (x, y + self.height - 1),
            (x + self.width - 1, y + self.height - 1)
        ]

        for corner_x, corner_y in corners:
            tile_x = int(corner_x / TILE_SIZE)
            tile_y = int(corner_y / TILE_SIZE)

            if tile_y < 0 or tile_y >= len(level_map):
                return True
            if tile_x < 0 or tile_x >= len(level_map[0]):
                return True

            tile = level_map[tile_y][tile_x]
            if tile == "#" or tile == "B":
                return True

        return False

    def check_magma_collision(self, level_map):
        """Check if touching magma tiles"""
        corners = [
            (self.x, self.y),
            (self.x + self.width - 1, self.y),
            (self.x, self.y + self.height - 1),
            (self.x + self.width - 1, self.y + self.height - 1)
        ]

        for corner_x, corner_y in corners:
            tile_x = int(corner_x / TILE_SIZE)
            tile_y = int(corner_y / TILE_SIZE)

            if 0 <= tile_y < len(level_map) and 0 <= tile_x < len(level_map[0]):
                if level_map[tile_y][tile_x] == "M":
                    return True
        return False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        # Draw player as blue helicopter
        # Body
        pygame.draw.rect(screen, COLOR_BLUE, (int(self.x + 8), int(self.y + 12), 16, 12))
        # Rotor
        rotor_y = int(self.y + 8)
        pygame.draw.line(screen, COLOR_WHITE, (int(self.x), rotor_y), (int(self.x + 32), rotor_y), 2)
        # Cockpit
        pygame.draw.circle(screen, (100, 150, 255), (int(self.x + 16), int(self.y + 16)), 6)
        # Landing skids
        pygame.draw.line(screen, COLOR_GRAY, (int(self.x + 8), int(self.y + 24)),
                        (int(self.x + 8), int(self.y + 28)), 2)
        pygame.draw.line(screen, COLOR_GRAY, (int(self.x + 24), int(self.y + 24)),
                        (int(self.x + 24), int(self.y + 28)), 2)

##################################################################################################
# Game Class
##################################################################################################
class Game:
    def __init__(self):
        self.screen = None
        self.clock = None
        self.xbox_controller = None
        self.tiles = {}
        self.font = None
        self.small_font = None

        # Game state
        self.state = STATE_SPLASH
        self.score = 0
        self.level = 0
        self.lives = 3
        self.bombs = 5
        self.energy = MAX_ENERGY

        # Entities
        self.player = None
        self.enemies = []
        self.bullets = []
        self.dynamites = []
        self.miner = None

        # Input
        self.keys = []
        self.joy_axis_x = 0
        self.joy_axis_y = 0

        # Name entry
        self.player_name = ""

        # Score tracking for extra lives
        self.last_life_score = 0

        # Level complete tracking
        self.level_complete_timer = 0

        # Shooting cooldown
        self.shoot_cooldown = 0

    def init(self):
        """Initialize pygame and game resources"""
        pygame.init()
        pygame.mixer.init()

        # Initialize joysticks
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()

        # Find Xbox controller
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            if "Xbox" in joystick.get_name() or "Controller" in joystick.get_name():
                self.xbox_controller = joystick
                self.xbox_controller.init()
                print(f"Found controller: {joystick.get_name()}")
                break

        if self.xbox_controller is None:
            print("No controller found. Using keyboard controls.")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("H.E.R.O. Remake")

        # Load fonts
        try:
            self.font = pygame.font.Font("fonts/PressStart2P-vaV7.ttf", 16)
            self.small_font = pygame.font.Font("fonts/PressStart2P-vaV7.ttf", 10)
        except:
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 16)

        # Load sounds
        try:
            self.shoot_sound = pygame.mixer.Sound("sounds/shoot.wav")
            self.explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")
        except:
            print("Could not load sound files")
            self.shoot_sound = None
            self.explosion_sound = None

        # Load tile images or create colored surfaces
        try:
            self.tiles['wall'] = pygame.image.load("tiles/wall.png").convert_alpha()
            self.tiles['floor'] = pygame.image.load("tiles/floor.png").convert_alpha()
            self.tiles['blank'] = pygame.image.load("tiles/blank.png").convert_alpha()
        except:
            # Create simple colored tiles
            self.tiles['wall'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['wall'].fill(COLOR_GRAY)
            self.tiles['floor'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['floor'].fill((100, 70, 50))
            self.tiles['blank'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['blank'].fill(COLOR_BLACK)

        # Create magma tile
        self.tiles['magma'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.tiles['magma'].fill(COLOR_ORANGE)
        pygame.draw.rect(self.tiles['magma'], COLOR_RED, (4, 4, 24, 24))

        # Create destructible block tile
        self.tiles['block'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.tiles['block'].fill((139, 90, 43))
        pygame.draw.rect(self.tiles['block'], (160, 100, 50), (2, 2, 28, 28))

    def start_level(self):
        """Initialize a level"""
        self.state = STATE_PLAYING
        self.energy = MAX_ENERGY

        # Clear entities
        self.enemies = []
        self.bullets = []
        self.dynamites = []
        self.miner = None

        # Create player
        self.player = Player()
        self.player.init(MAPS[self.level])

        # Parse level and create entities
        level_map = MAPS[self.level]
        for row_index, row in enumerate(level_map):
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE

                if tile == "E":
                    self.enemies.append(Enemy(x, y))
                elif tile == "R":
                    # Create miner at the R position (Rescue)
                    if not self.miner:
                        self.miner = Miner(x, y)

    def shoot(self):
        """Player shoots a laser"""
        if self.shoot_cooldown <= 0:
            direction = 1 if self.player.facing_right else -1
            bullet = Bullet(self.player.x + 16, self.player.y + 16, direction)
            self.bullets.append(bullet)
            self.shoot_cooldown = 0.3  # 0.3 second cooldown

            if self.shoot_sound:
                self.shoot_sound.play()

    def place_dynamite(self):
        """Player places dynamite"""
        if self.bombs > 0:
            dynamite = Dynamite(self.player.x, self.player.y + 32)
            self.dynamites.append(dynamite)
            self.bombs -= 1

    def check_collisions(self):
        """Check all collision interactions"""
        if not self.player:
            return

        player_rect = self.player.get_rect()

        # Check player vs enemies
        for enemy in self.enemies:
            if enemy.active and player_rect.colliderect(enemy.get_rect()):
                self.player_hit()
                return

        # Check player vs miner (rescue)
        if self.miner and not self.miner.rescued:
            if player_rect.colliderect(self.miner.get_rect()):
                self.rescue_miner()
                return

        # Check bullets vs enemies
        for bullet in self.bullets[:]:
            if not bullet.active:
                continue
            bullet_rect = bullet.get_rect()

            for enemy in self.enemies:
                if enemy.active and bullet_rect.colliderect(enemy.get_rect()):
                    enemy.active = False
                    bullet.active = False
                    self.score += 100
                    break

            # Check bullet vs blocks
            tile_x = int(bullet.x / TILE_SIZE)
            tile_y = int(bullet.y / TILE_SIZE)
            level_map = MAPS[self.level]

            if 0 <= tile_y < len(level_map) and 0 <= tile_x < len(level_map[0]):
                if level_map[tile_y][tile_x] == "B":
                    # Destroy block
                    row = list(level_map[tile_y])
                    row[tile_x] = " "
                    MAPS[self.level][tile_y] = "".join(row)
                    bullet.active = False
                    self.score += 50

        # Check dynamite explosions
        for dynamite in self.dynamites[:]:
            if dynamite.exploded:
                explosion_rect = dynamite.get_explosion_rect()
                if explosion_rect:
                    # Destroy enemies in explosion
                    for enemy in self.enemies:
                        if enemy.active and explosion_rect.colliderect(enemy.get_rect()):
                            enemy.active = False
                            self.score += 150

                    # Destroy blocks in explosion
                    level_map = MAPS[self.level]
                    for row_index in range(len(level_map)):
                        for col_index in range(len(level_map[0])):
                            tile_x = col_index * TILE_SIZE
                            tile_y = row_index * TILE_SIZE
                            tile_rect = pygame.Rect(tile_x, tile_y, TILE_SIZE, TILE_SIZE)

                            if explosion_rect.colliderect(tile_rect) and level_map[row_index][col_index] == "B":
                                row = list(level_map[row_index])
                                row[col_index] = " "
                                MAPS[self.level][row_index] = "".join(row)
                                self.score += 25

                if self.explosion_sound and dynamite.explosion_timer > 0.25:
                    self.explosion_sound.play()

        # Check magma collision
        if self.player.check_magma_collision(MAPS[self.level]):
            self.player_hit()

    def player_hit(self):
        """Player takes damage"""
        self.lives -= 1
        if self.lives <= 0:
            self.state = STATE_ENTERING_NAME
        else:
            # Restart level
            self.start_level()

    def rescue_miner(self):
        """Player rescues the miner"""
        if not self.miner.rescued:
            self.miner.rescued = True

            # Award points
            bonus_points = int(self.energy * 10)  # Bonus for remaining energy
            bonus_points += self.bombs * 100  # Bonus for remaining bombs
            self.score += 1000 + bonus_points

            self.state = STATE_LEVEL_COMPLETE
            self.level_complete_timer = 2.0

    def next_level(self):
        """Advance to next level"""
        self.level += 1
        if self.level >= len(MAPS):
            # Game complete!
            self.state = STATE_ENTERING_NAME
        else:
            self.start_level()

    def check_extra_life(self):
        """Check if player earned an extra life"""
        if self.score >= self.last_life_score + 20000:
            self.lives += 1
            self.last_life_score = self.score

    def update_playing(self, dt):
        """Update game state during play"""
        if self.energy <= 0:
            self.player_hit()
            return

        # Update player
        self.player.update(dt, self.keys, self.joy_axis_x, self.joy_axis_y, MAPS[self.level], self)

        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt, MAPS[self.level])

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update(dt)
            if not bullet.active:
                self.bullets.remove(bullet)

        # Update dynamites
        for dynamite in self.dynamites[:]:
            dynamite.update(dt)
            if not dynamite.active:
                self.dynamites.remove(dynamite)

        # Check collisions
        self.check_collisions()

        # Check for extra life
        self.check_extra_life()

        # Update shooting cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt

    def update_level_complete(self, dt):
        """Update level complete state"""
        self.level_complete_timer -= dt
        if self.level_complete_timer <= 0:
            self.next_level()

    def render_level(self):
        """Render the current level"""
        level_map = MAPS[self.level]

        for row_index, row in enumerate(level_map):
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE

                if tile == "#":
                    self.screen.blit(self.tiles['wall'], (x, y))
                elif tile == ".":
                    self.screen.blit(self.tiles['floor'], (x, y))
                elif tile == "B":
                    self.screen.blit(self.tiles['block'], (x, y))
                elif tile == "M":
                    # Draw magma
                    self.screen.blit(self.tiles['magma'], (x, y))
                else:
                    # For blank spaces, S (start), E (enemy), and R (rescue/miner)
                    self.screen.blit(self.tiles['blank'], (x, y))

    def render_hud(self):
        """Render heads-up display"""
        hud_y = SCREEN_HEIGHT - 64
        hud_background = pygame.Surface((SCREEN_WIDTH, 64))
        hud_background.set_alpha(200)
        hud_background.fill(COLOR_BLACK)
        self.screen.blit(hud_background, (0, hud_y))

        # Score
        score_text = self.small_font.render(f"SCORE: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (10, hud_y + 5))

        # Level
        level_text = self.small_font.render(f"LVL: {self.level + 1}", True, COLOR_WHITE)
        self.screen.blit(level_text, (10, hud_y + 25))

        # Lives
        lives_text = self.small_font.render(f"LIVES: {self.lives}", True, COLOR_WHITE)
        self.screen.blit(lives_text, (150, hud_y + 5))

        # Bombs
        bombs_text = self.small_font.render(f"BOMBS: {self.bombs}", True, COLOR_WHITE)
        self.screen.blit(bombs_text, (150, hud_y + 25))

        # Energy bar
        energy_text = self.small_font.render("ENERGY", True, COLOR_WHITE)
        self.screen.blit(energy_text, (300, hud_y + 5))

        # Energy bar background
        pygame.draw.rect(self.screen, COLOR_RED, (300, hud_y + 25, 200, 20))
        # Energy bar fill
        energy_width = int((self.energy / MAX_ENERGY) * 200)
        if energy_width > 0:
            energy_color = COLOR_GREEN if self.energy > 30 else COLOR_YELLOW if self.energy > 15 else COLOR_RED
            pygame.draw.rect(self.screen, energy_color, (300, hud_y + 25, energy_width, 20))
        # Energy bar border
        pygame.draw.rect(self.screen, COLOR_WHITE, (300, hud_y + 25, 200, 20), 2)

    def render_splash(self):
        """Render splash screen / main menu"""
        self.screen.fill(COLOR_BLACK)

        # Title
        title_text = self.font.render("H.E.R.O.", True, COLOR_WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)

        subtitle_text = self.small_font.render("Helicopter Emergency", True, COLOR_GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(subtitle_text, subtitle_rect)

        subtitle2_text = self.small_font.render("Rescue Operation", True, COLOR_GRAY)
        subtitle2_rect = subtitle2_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(subtitle2_text, subtitle2_rect)

        # Menu options
        play_text = self.small_font.render("Press SPACE or A to Play", True, COLOR_GREEN)
        play_rect = play_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(play_text, play_rect)

        quit_text = self.small_font.render("Press ESC to Quit", True, COLOR_RED)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, 230))
        self.screen.blit(quit_text, quit_rect)

        # High scores
        scores_title = self.small_font.render("HIGH SCORES", True, COLOR_YELLOW)
        scores_rect = scores_title.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(scores_title, scores_rect)

        scores = load_scores()[:3]  # Top 3
        for i, score_entry in enumerate(scores):
            score_text = self.small_font.render(
                f"{i + 1}. {score_entry['name']}: {score_entry['score']}",
                True, COLOR_WHITE
            )
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 310 + i * 25))
            self.screen.blit(score_text, score_rect)

        # Controls
        controls_text = self.small_font.render("Controls:", True, COLOR_GRAY)
        self.screen.blit(controls_text, (20, 400))

        controls1 = self.small_font.render("ARROWS/STICK: Move", True, COLOR_GRAY)
        self.screen.blit(controls1, (20, 420))

        controls2 = self.small_font.render("SPACE/X: Shoot", True, COLOR_GRAY)
        self.screen.blit(controls2, (20, 440))

        controls3 = self.small_font.render("DOWN+CTRL/B: Dynamite", True, COLOR_GRAY)
        self.screen.blit(controls3, (20, 460))

    def render_entering_name(self):
        """Render name entry screen"""
        self.screen.fill(COLOR_BLACK)

        # Game Over
        game_over_text = self.font.render("GAME OVER", True, COLOR_RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(game_over_text, game_over_rect)

        # Final score
        score_text = self.small_font.render(f"Final Score: {self.score}", True, COLOR_WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(score_text, score_rect)

        # Name entry
        name_prompt = self.small_font.render("Enter Your Name:", True, COLOR_WHITE)
        name_rect = name_prompt.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(name_prompt, name_rect)

        # Current name
        name_text = self.font.render(self.player_name + "_", True, COLOR_GREEN)
        name_text_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, 240))
        self.screen.blit(name_text, name_text_rect)

        # Instructions
        instr_text = self.small_font.render("Press ENTER when done", True, COLOR_GRAY)
        instr_rect = instr_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(instr_text, instr_rect)

    def render_level_complete(self):
        """Render level complete overlay"""
        # Draw normal game
        self.render_level()

        if self.miner:
            self.miner.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        if self.player:
            self.player.draw(self.screen)

        self.render_hud()

        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(COLOR_BLACK)
        self.screen.blit(overlay, (0, 0))

        # Level complete text
        complete_text = self.font.render("LEVEL COMPLETE!", True, COLOR_GREEN)
        complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(complete_text, complete_rect)

    def loop(self):
        """Main game loop"""
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000.0

            # Get input state
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
                            self.level = 0
                            self.score = 0
                            self.lives = 3
                            self.bombs = 5
                            self.last_life_score = 0
                            self.start_level()
                        elif event.key == pygame.K_ESCAPE:
                            running = False

                    elif self.state == STATE_PLAYING:
                        if event.key == pygame.K_SPACE:
                            self.shoot()
                        elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                            if self.keys[pygame.K_DOWN]:
                                self.place_dynamite()

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
                        if event.button == 0:  # A button
                            self.level = 0
                            self.score = 0
                            self.lives = 3
                            self.bombs = 5
                            self.last_life_score = 0
                            self.start_level()

                    elif self.state == STATE_PLAYING:
                        if event.button == 2:  # X button
                            self.shoot()
                        elif event.button == 1:  # B button
                            self.place_dynamite()

            # Update game state
            if self.state == STATE_PLAYING:
                self.update_playing(dt)
            elif self.state == STATE_LEVEL_COMPLETE:
                self.update_level_complete(dt)

            # Render
            self.screen.fill(COLOR_BLACK)

            if self.state == STATE_SPLASH:
                self.render_splash()
            elif self.state == STATE_PLAYING:
                self.render_level()

                # Draw entities
                if self.miner:
                    self.miner.draw(self.screen)

                for enemy in self.enemies:
                    enemy.draw(self.screen)

                for bullet in self.bullets:
                    bullet.draw(self.screen)

                for dynamite in self.dynamites:
                    dynamite.draw(self.screen)

                if self.player:
                    self.player.draw(self.screen)

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
