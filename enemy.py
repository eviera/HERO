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
        speed_table = {"bat": BAT_SPEED, "spider": SPIDER_SPEED, "bug": BUG_SPEED}
        self.speed = speed_table.get(enemy_type, BAT_SPEED)
        self.direction = random.choice([-1, 1])
        self.active = True
        self.width = 32
        self.height = 32
        self.image = None
        self.images = None  # Lista de sprites para animación [bat1, bat2]
        self.distance_traveled = 0  # Distancia recorrida para alternar sprites
        self.anim_frame = 0  # Frame actual de animación
        self.exploding = False
        self.explosion_timer = 0
        self.explosion_duration = 0.2  # Más corto para que desaparezca rápido

        # Araña: desciende máximo 2 tiles desde el spawn y vuelve
        if enemy_type == "spider":
            self.spider_max_y = y + 2 * TILE_SIZE  # límite inferior
            self.direction = 1  # empieza bajando

        # Bicho: se mueve en zona 3x3 tiles alrededor del spawn
        if enemy_type == "bug":
            spawn_col = int(x / TILE_SIZE)
            spawn_row = int(y / TILE_SIZE)
            self.bug_zone_min_x = (spawn_col - 1) * TILE_SIZE
            self.bug_zone_max_x = (spawn_col + 2) * TILE_SIZE - self.width
            self.bug_zone_min_y = (spawn_row - 1) * TILE_SIZE
            self.bug_zone_max_y = (spawn_row + 2) * TILE_SIZE - self.height
            # Dirección inicial aleatoria (cardinal)
            dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            self.bug_dx, self.bug_dy = random.choice(dirs)

    def check_collision(self, x, y, level_map):
        """Check collision with tiles using all 4 corners (margen de 1px)"""
        level_h = len(level_map) if level_map else 0
        level_w = len(level_map[0]) if level_map and level_map[0] else 0
        corners = [
            (x + 1, y + 1),
            (x + self.width - 2, y + 1),
            (x + 1, y + self.height - 2),
            (x + self.width - 2, y + self.height - 2)
        ]

        for corner_x, corner_y in corners:
            tile_x = int(corner_x / TILE_SIZE)
            tile_y = int(corner_y / TILE_SIZE)

            if tile_y < 0 or tile_y >= level_h:
                return True
            if tile_x < 0 or tile_x >= level_w:
                return True

            tile = level_map[tile_y][tile_x]
            if tile in ('#', 'G', '.', 'R'):
                return True

        return False

    def _find_ceiling_y(self, level_map):
        """Busca el techo más cercano arriba de la posición de spawn de la araña"""
        tile_x = int((self.start_x + self.width // 2) / TILE_SIZE)
        start_tile_y = int(self.start_y / TILE_SIZE)

        for tile_y in range(start_tile_y - 1, -1, -1):
            if 0 <= tile_y < len(level_map) and 0 <= tile_x < len(level_map[0]):
                tile = level_map[tile_y][tile_x]
                if tile in ('#', 'G', '.', 'R'):
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

        if self.enemy_type == "bug":
            # Bicho se mueve en zona 3x3 tiles, rebota contra límites y paredes
            new_x = self.x + self.bug_dx * self.speed * dt
            new_y = self.y + self.bug_dy * self.speed * dt

            # Verificar límites de zona y colisión con paredes
            bounced = False

            # Clamp horizontal a zona y verificar colisión
            if new_x < self.bug_zone_min_x:
                new_x = self.bug_zone_min_x
                bounced = True
            elif new_x > self.bug_zone_max_x:
                new_x = self.bug_zone_max_x
                bounced = True
            elif self.bug_dx != 0 and self.check_collision(new_x, self.y, level_map):
                new_x = self.x
                bounced = True

            # Clamp vertical a zona y verificar colisión
            if new_y < self.bug_zone_min_y:
                new_y = self.bug_zone_min_y
                bounced = True
            elif new_y > self.bug_zone_max_y:
                new_y = self.bug_zone_max_y
                bounced = True
            elif self.bug_dy != 0 and self.check_collision(self.x, new_y, level_map):
                new_y = self.y
                bounced = True

            self.x = new_x
            self.y = new_y

            if bounced:
                # Elegir nueva dirección aleatoria (distinta a la actual)
                dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                current = (self.bug_dx, self.bug_dy)
                options = [d for d in dirs if d != current]
                self.bug_dx, self.bug_dy = random.choice(options)

            # Animación de patas
            if self.images:
                self.distance_traveled += self.speed * dt
                if self.distance_traveled >= BUG_ANIM_DISTANCE:
                    self.distance_traveled -= BUG_ANIM_DISTANCE
                    self.anim_frame = 1 - self.anim_frame
                    self.image = self.images[self.anim_frame]

        elif self.enemy_type == "spider":
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

            # Alternar sprite cada 16 píxeles recorridos
            if self.images:
                self.distance_traveled += abs(self.speed * dt)
                if self.distance_traveled >= BAT_ANIM_DISTANCE:
                    self.distance_traveled -= BAT_ANIM_DISTANCE
                    self.anim_frame = 1 - self.anim_frame
                    self.image = self.images[self.anim_frame]

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen, camera_x, camera_y, level_map=None):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        if -50 < screen_y < GAME_VIEWPORT_HEIGHT + 50 and -50 < screen_x < GAME_WIDTH + 50:
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
                                         (int(screen_x + 16), int(screen_y + 16)), r)
            else:
                # Dibujar hilo de araña antes del sprite
                if self.enemy_type == "spider" and level_map is not None:
                    ceiling_y = self._find_ceiling_y(level_map)
                    if ceiling_y is not None:
                        thread_top = ceiling_y - camera_y
                        thread_bottom = screen_y + self.height // 2
                        center_x = int(screen_x + self.width // 2)
                        pygame.draw.line(screen, COLOR_WHITE,
                                       (center_x, int(thread_top)),
                                       (center_x, int(thread_bottom)), 1)

                if self.image:
                    if self.enemy_type == "bug":
                        # Rotar sprite según dirección de movimiento
                        # Sprite base mira arriba (0, -1)
                        angle = 0
                        if self.bug_dx == 1:    # derecha
                            angle = -90
                        elif self.bug_dx == -1:  # izquierda
                            angle = 90
                        elif self.bug_dy == 1:   # abajo
                            angle = 180
                        rotated = pygame.transform.rotate(self.image, angle)
                        screen.blit(rotated, (int(screen_x), int(screen_y)))
                    else:
                        screen.blit(self.image, (int(screen_x), int(screen_y)))
                else:
                    pygame.draw.circle(screen, COLOR_RED,
                                     (int(screen_x + 16), int(screen_y + 16)), 12)
