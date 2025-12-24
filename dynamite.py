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
        self.width = 16
        self.height = 16

    def update(self, dt):
        if not self.exploded:
            # Dynamite falls
            self.vel_y += GRAVITY * 0.3 * dt  # Cae más lento
            self.y += self.vel_y

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
                                     (int(self.x + 8), int(screen_y)), 3)
            else:
                # Draw explosion
                radius = int(DYNAMITE_EXPLOSION_RADIUS * (self.explosion_time / 0.5))
                pygame.draw.circle(screen, COLOR_ORANGE,
                                 (int(self.x), int(screen_y)), radius)
                pygame.draw.circle(screen, COLOR_YELLOW,
                                 (int(self.x), int(screen_y)), int(radius * 0.6))
