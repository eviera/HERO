# H.E.R.O. Remake - Miner Class

import pygame
import math
from constants import *

class Miner:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rescued = False
        self.width = 32
        self.height = 32
        self.image = None

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen, camera_y):
        screen_y = self.y - camera_y
        if -50 < screen_y < VIEWPORT_HEIGHT + 50:
            if self.image:
                # Draw sprite
                screen.blit(self.image, (int(self.x), int(screen_y)))
            else:
                # Fallback: Draw miner
                pygame.draw.circle(screen, COLOR_GREEN, (int(self.x + 16), int(screen_y + 10)), 8)
                pygame.draw.rect(screen, COLOR_GREEN, (int(self.x + 12), int(screen_y + 18), 8, 12))
                # Arms waving
                wave = math.sin(pygame.time.get_ticks() / 200) * 5
                pygame.draw.line(screen, COLOR_GREEN,
                               (int(self.x + 16), int(screen_y + 20)),
                               (int(self.x + 10 + wave), int(screen_y + 26)), 2)
                pygame.draw.line(screen, COLOR_GREEN,
                               (int(self.x + 16), int(screen_y + 20)),
                               (int(self.x + 22 - wave), int(screen_y + 26)), 2)
