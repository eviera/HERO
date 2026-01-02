# H.E.R.O. Remake - Dynamite Class

import pygame
from constants import *

class Dynamite:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_y = 0
        self.fuse_time = DYNAMITE_FUSE_TIME
        self.exploded = False
        self.explosion_time = 0.5
        self.active = True
        self.width = 8
        self.height = 16
        self.on_ground = False

    def check_collision(self, x, y, level_map):
        """Check collision with tiles"""
        # Check bottom corners
        corners = [
            (x + 2, y + self.height - 1),
            (x + self.width - 3, y + self.height - 1)
        ]

        for corner_x, corner_y in corners:
            tile_x = int(corner_x / TILE_SIZE)
            tile_y = int(corner_y / TILE_SIZE)

            if tile_y < 0 or tile_y >= LEVEL_HEIGHT:
                return True
            if tile_x < 0 or tile_x >= LEVEL_WIDTH:
                return True

            if 0 <= tile_y < len(level_map) and 0 <= tile_x < len(level_map[0]):
                tile = level_map[tile_y][tile_x]
                if tile == '#' or tile == 'B' or tile == '.':
                    return True

        return False

    def update(self, dt, level_map):
        if not self.exploded:
            # Apply gravity if not on ground
            if not self.on_ground:
                self.vel_y += GRAVITY * 0.3 * dt  # Cae más lento
                new_y = self.y + self.vel_y * dt

                # Check if would collide
                if self.check_collision(self.x, new_y, level_map):
                    # Stop falling
                    self.vel_y = 0
                    self.on_ground = True
                else:
                    self.y = new_y

            # Countdown fuse
            self.fuse_time -= dt
            if self.fuse_time <= 0:
                self.exploded = True
        else:
            self.explosion_time -= dt
            if self.explosion_time <= 0:
                self.active = False

    def get_explosion_rect(self):
        if self.exploded:
            return pygame.Rect(
                self.x - DYNAMITE_EXPLOSION_RADIUS/2,
                self.y - DYNAMITE_EXPLOSION_RADIUS/2,
                DYNAMITE_EXPLOSION_RADIUS,
                DYNAMITE_EXPLOSION_RADIUS
            )
        return None

    def draw(self, screen, camera_y):
        screen_y = self.y - camera_y
        if -100 < screen_y < VIEWPORT_HEIGHT + 100:
            if not self.exploded:
                # Draw dynamite
                pygame.draw.rect(screen, COLOR_RED,
                               (int(self.x), int(screen_y), self.width, self.height))
                # Fuse blinking
                if self.fuse_time % 0.3 < 0.15:
                    pygame.draw.circle(screen, COLOR_YELLOW,
                                     (int(self.x + (self.width) / 2), int(screen_y)), 3)
            else:
                # Draw explosion
                radius = int(DYNAMITE_EXPLOSION_RADIUS * (self.explosion_time / 0.5))
                pygame.draw.circle(screen, COLOR_ORANGE,
                                 (int(self.x), int(screen_y)), radius)
                pygame.draw.circle(screen, COLOR_YELLOW,
                                 (int(self.x), int(screen_y)), int(radius * 0.6))
