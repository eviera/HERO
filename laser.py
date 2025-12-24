# H.E.R.O. Remake - Laser Class

import pygame
from constants import *

class Laser:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction  # 1 = right, -1 = left
        self.width = 16
        self.height = 4
        self.active = True
        self.color = COLOR_YELLOW

    def update(self, dt, level_map):
        self.x += self.direction * LASER_SPEED * dt

        # Check bounds
        if self.x < 0 or self.x > LEVEL_WIDTH * TILE_SIZE:
            self.active = False
            return

        # Check collision with walls
        tile_x = int(self.x / TILE_SIZE)
        tile_y = int(self.y / TILE_SIZE)

        if 0 <= tile_y < len(level_map) and 0 <= tile_x < len(level_map[0]):
            tile = level_map[tile_y][tile_x]
            if tile == '#' or tile == '.':  # Wall and floor indestructible
                self.active = False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen, camera_y):
        screen_y = self.y - camera_y
        if -50 < screen_y < VIEWPORT_HEIGHT + 50:
            pygame.draw.rect(screen, self.color,
                           (int(self.x), int(screen_y), self.width, self.height))
