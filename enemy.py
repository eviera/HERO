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
        self.explosion_duration = 0.2  # Más corto para que desaparezca rápido

    def check_collision(self, x, y, level_map):
        """Check collision with tiles using all 4 corners"""
        corners = [
            (x + 2, y + 2),
            (x + self.width - 3, y + 2),
            (x + 2, y + self.height - 3),
            (x + self.width - 3, y + self.height - 3)
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
                # Colisiona con paredes, bloques, pisos
                if tile == '#' or tile == 'B' or tile == '.':
                    return True

        return False

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
            # Calculate new position
            new_x = self.x + self.direction * self.speed * dt

            # Check collision at new position
            if self.check_collision(new_x, self.y, level_map):
                # Hit wall - change direction but don't move
                self.direction *= -1
            else:
                # No collision - safe to move
                self.x = new_x
        else:
            # Bats fly horizontally with oscillation
            # Calculate new position
            new_x = self.x + self.direction * self.speed * dt

            # Check collision at new position
            if self.check_collision(new_x, self.y, level_map):
                # Hit wall - change direction but don't move
                self.direction *= -1
            else:
                # No collision - safe to move
                self.x = new_x

            # Vertical oscillation for bats
            self.move_timer += dt
            self.vertical_offset = math.sin(self.move_timer * 3) * 15

    def get_rect(self):
        return pygame.Rect(self.x, self.y + self.vertical_offset, self.width, self.height)

    def draw(self, screen, camera_y):
        screen_y = self.y + self.vertical_offset - camera_y
        if -50 < screen_y < VIEWPORT_HEIGHT + 50:
            if self.exploding:
                # Draw explosion animation - más pequeña y marrón
                progress = self.explosion_timer / self.explosion_duration
                radius = int(8 + progress * 10)  # Radio más pequeño (máx ~18)

                # Draw expanding circles for explosion with brown colors
                for i in range(2):  # Solo 2 círculos en lugar de 3
                    r = radius - i * 5
                    if r > 0:
                        # Colores marrones: marrón oscuro -> marrón claro
                        if i == 0:
                            color = (139, 69, 19)  # Marrón medio
                        else:
                            color = (101, 67, 33)  # Marrón oscuro
                        pygame.draw.circle(screen, color,
                                         (int(self.x + 16), int(screen_y + 16)), r)
            elif self.image:
                screen.blit(self.image, (int(self.x), int(screen_y)))
            else:
                # Draw simple enemy
                pygame.draw.circle(screen, COLOR_RED,
                                 (int(self.x + 16), int(screen_y + 16)), 12)
