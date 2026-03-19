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
        self.explosion_sprites = []  # bomb1, bomb2, bomb3 sprites

    def check_collision(self, x, y, level_map):
        """Check collision with tiles"""
        level_h = len(level_map) if level_map else 0
        # Check bottom corners
        corners = [
            (x + 2, y + self.height - 1),
            (x + self.width - 3, y + self.height - 1)
        ]

        for corner_x, corner_y in corners:
            tile_x = int(corner_x / TILE_SIZE)
            tile_y = int(corner_y / TILE_SIZE)

            if tile_y < 0 or tile_y >= level_h:
                return True
            if tile_x < 0 or tile_x >= len(level_map[tile_y]):
                return True

            tile = level_map[tile_y][tile_x]
            if tile in SOLID_TILES:
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

    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        if -100 < screen_y < GAME_VIEWPORT_HEIGHT + 100 and -100 < screen_x < GAME_WIDTH + 100:
            if not self.exploded:
                if self.explosion_sprites:
                    # Alternar bomb1/bomb2/bomb3 desde que se suelta
                    elapsed = DYNAMITE_FUSE_TIME - self.fuse_time
                    frame_duration = 0.1
                    frame_index = int(elapsed / frame_duration) % len(self.explosion_sprites)
                    sprite = self.explosion_sprites[frame_index]
                    sx = int(screen_x - sprite.get_width() / 2)
                    sy = int(screen_y - sprite.get_height() / 2)
                    screen.blit(sprite, (sx, sy))
                else:
                    # Fallback: rectangulo rojo
                    pygame.draw.rect(screen, COLOR_RED,
                                   (int(screen_x), int(screen_y), self.width, self.height))
            else:
                # No dibujar nada durante la explosión;
                # el flash de pantalla en hero.py da el efecto visual
                pass
