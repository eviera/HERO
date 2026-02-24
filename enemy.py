# H.E.R.O. Remake - Enemy Class

import pygame
import random
from constants import *

class Enemy:
    def __init__(self, x, y, enemy_type="bat"):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.enemy_type = enemy_type
        self.speed = BAT_SPEED if enemy_type == "bat" else SPIDER_SPEED
        self.direction = random.choice([-1, 1])
        self.active = True
        self.width = 32
        self.height = 32
        self.image = None
        self.exploding = False
        self.explosion_timer = 0
        self.explosion_duration = 0.2  # Más corto para que desaparezca rápido

        # Araña: desciende máximo 2 tiles desde el spawn y vuelve
        if enemy_type == "spider":
            self.spider_max_y = y + 2 * TILE_SIZE  # límite inferior
            self.direction = 1  # empieza bajando

    def check_collision(self, x, y, level_map):
        """Check collision with tiles using all 4 corners (margen de 1px)"""
        corners = [
            (x + 1, y + 1),
            (x + self.width - 2, y + 1),
            (x + 1, y + self.height - 2),
            (x + self.width - 2, y + self.height - 2)
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
                if tile in ('#', 'B', '.', 'W'):
                    return True

        return False

    def _find_ceiling_y(self, level_map):
        """Busca el techo más cercano arriba de la posición de spawn de la araña"""
        tile_x = int((self.start_x + self.width // 2) / TILE_SIZE)
        start_tile_y = int(self.start_y / TILE_SIZE)

        for tile_y in range(start_tile_y - 1, -1, -1):
            if 0 <= tile_y < len(level_map) and 0 <= tile_x < len(level_map[0]):
                tile = level_map[tile_y][tile_x]
                if tile in ('#', 'B', '.', 'W'):
                    # El fondo del tile sólido
                    return (tile_y + 1) * TILE_SIZE
        return None

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
            # Arañas bajan desde el spawn hasta 2 tiles y vuelven al techo
            new_y = self.y + self.direction * self.speed * dt

            # Colisión con tiles: rebotar contra pared/piso
            if self.check_collision(self.x, new_y, level_map):
                if self.direction > 0:  # bajando
                    tile_y = int((new_y + self.height) / TILE_SIZE)
                    self.y = tile_y * TILE_SIZE - self.height
                else:  # subiendo
                    tile_y = int(new_y / TILE_SIZE)
                    self.y = (tile_y + 1) * TILE_SIZE
                self.direction *= -1
            else:
                # Límite inferior: máximo 2 tiles abajo del spawn
                if new_y > self.spider_max_y:
                    new_y = self.spider_max_y
                    self.direction = -1  # volver arriba
                # Límite superior: no pasar del spawn
                elif new_y < self.start_y:
                    new_y = self.start_y
                    self.direction = 1  # volver abajo
                self.y = new_y
        else:
            # Murciélagos se mueven horizontalmente, rebotan contra bloques
            new_x = self.x + self.direction * self.speed * dt

            if self.check_collision(new_x, self.y, level_map):
                # Snap al borde del tile
                if self.direction > 0:  # derecha
                    tile_x = int((new_x + self.width) / TILE_SIZE)
                    self.x = tile_x * TILE_SIZE - self.width
                else:  # izquierda
                    tile_x = int(new_x / TILE_SIZE)
                    self.x = (tile_x + 1) * TILE_SIZE
                self.direction *= -1
            else:
                self.x = new_x

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen, camera_y, level_map=None):
        screen_y = self.y - camera_y
        if -50 < screen_y < VIEWPORT_HEIGHT + 50:
            if self.exploding:
                # Draw explosion animation - más pequeña y marrón
                progress = self.explosion_timer / self.explosion_duration
                radius = int(8 + progress * 10)

                for i in range(2):
                    r = radius - i * 5
                    if r > 0:
                        if i == 0:
                            color = (139, 69, 19)  # Marrón medio
                        else:
                            color = (101, 67, 33)  # Marrón oscuro
                        pygame.draw.circle(screen, color,
                                         (int(self.x + 16), int(screen_y + 16)), r)
            else:
                # Dibujar hilo de araña antes del sprite
                if self.enemy_type == "spider" and level_map is not None:
                    ceiling_y = self._find_ceiling_y(level_map)
                    if ceiling_y is not None:
                        thread_top = ceiling_y - camera_y
                        thread_bottom = screen_y + self.height // 2
                        center_x = int(self.x + self.width // 2)
                        pygame.draw.line(screen, COLOR_WHITE,
                                       (center_x, int(thread_top)),
                                       (center_x, int(thread_bottom)), 1)

                if self.image:
                    screen.blit(self.image, (int(self.x), int(screen_y)))
                else:
                    pygame.draw.circle(screen, COLOR_RED,
                                     (int(self.x + 16), int(screen_y + 16)), 12)
