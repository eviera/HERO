# H.E.R.O. Remake - Enemy Class

import pygame
import random
import math
from constants import *

class Enemy:
    def __init__(self, x, y, enemy_type="bat"):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.speed = 40 if enemy_type == "bat" else 30
        self.direction = random.choice([-1, 1])
        self.active = True
        self.width = 32
        self.height = 32
        self.image = None
        self.move_timer = 0
        self.vertical_offset = 0
        self.vertical_speed = 20
        self.exploding = False
        self.explosion_timer = 0
        self.explosion_duration = 0.3

    def update(self, dt, level_map):
        if not self.active:
            return

        # Handle explosion animation
        if self.exploding:
            self.explosion_timer += dt
            if self.explosion_timer >= self.explosion_duration:
                self.active = False
            return

        if self.enemy_type == "spider":
            # Spiders move on the ground horizontally
            self.x += self.direction * self.speed * dt

            # Check walls and change direction
            tile_x = int(self.x / TILE_SIZE)
            tile_y = int(self.y / TILE_SIZE)

            if tile_x < 0 or tile_x >= LEVEL_WIDTH or \
               (0 <= tile_y < len(level_map) and 0 <= tile_x < len(level_map[0]) and
                (level_map[tile_y][tile_x] == '#' or level_map[tile_y][tile_x] == 'B' or level_map[tile_y][tile_x] == '.')):
                self.direction *= -1
        else:
            # Bats fly horizontally with oscillation
            self.x += self.direction * self.speed * dt

            # Check walls and change direction
            tile_x = int(self.x / TILE_SIZE)
            tile_y = int(self.y / TILE_SIZE)

            if tile_x < 0 or tile_x >= LEVEL_WIDTH or \
               (0 <= tile_y < len(level_map) and 0 <= tile_x < len(level_map[0]) and (level_map[tile_y][tile_x] == '#' or level_map[tile_y][tile_x] == '.')):
                self.direction *= -1

            # Vertical oscillation for bats
            self.move_timer += dt
            self.vertical_offset = math.sin(self.move_timer * 3) * 15

    def get_rect(self):
        return pygame.Rect(self.x, self.y + self.vertical_offset, self.width, self.height)

    def draw(self, screen, camera_y):
        screen_y = self.y + self.vertical_offset - camera_y
        if -50 < screen_y < VIEWPORT_HEIGHT + 50:
            if self.exploding:
                # Draw explosion animation
                progress = self.explosion_timer / self.explosion_duration
                radius = int(16 + progress * 20)
                alpha = int(255 * (1 - progress))

                # Draw expanding circles for explosion
                for i in range(3):
                    r = radius - i * 8
                    if r > 0:
                        color = (255, 200 - i * 50, 0)  # Orange to yellow
                        pygame.draw.circle(screen, color,
                                         (int(self.x + 16), int(screen_y + 16)), r)
            elif self.image:
                screen.blit(self.image, (int(self.x), int(screen_y)))
            else:
                # Draw simple enemy
                pygame.draw.circle(screen, COLOR_RED,
                                 (int(self.x + 16), int(screen_y + 16)), 12)
