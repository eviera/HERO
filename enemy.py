# H.E.R.O. Remake - Enemy Class

import pygame
import random
from constants import *
from evgamelib.entity import AnimatedEntity

class Enemy(AnimatedEntity):
    def __init__(self, x, y, enemy_type="bat"):
        super().__init__(x, y, 32, 32)
        self.start_x = x
        self.start_y = y
        self.enemy_type = enemy_type
        speed_table = {"bat": BAT_SPEED, "spider": SPIDER_SPEED, "bug": BUG_SPEED,
                       "snake_left": SNAKE_EMERGE_SPEED, "snake_right": SNAKE_EMERGE_SPEED}
        self.speed = speed_table.get(enemy_type, BAT_SPEED)
        self.direction = random.choice([-1, 1])
        self.active = True
        if enemy_type == "bat":
            self.width = 22
            self.height = 22
            # Centrar el murciélago dentro del tile
            self.x = x + (TILE_SIZE - 22) // 2
            self.y = y + (TILE_SIZE - 22) // 2
        elif enemy_type == "spider":
            self.width = 22
            self.height = 22
            # Centrar la araña dentro del tile
            self.x = x + (TILE_SIZE - 22) // 2
            self.y = y + (TILE_SIZE - 22) // 2
            self.start_x = self.x
            self.start_y = self.y
        else:
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

        # Víbora: sale y entra de una pared
        if enemy_type in ("snake_left", "snake_right"):
            self.snake_facing = -1 if enemy_type == "snake_left" else 1  # dirección de salida
            self.snake_state = "hidden"  # hidden, emerging, extended, retracting
            self.snake_timer = random.uniform(0.5, SNAKE_HIDDEN_TIME)  # tiempo inicial aleatorio
            self.snake_extend = 0.0  # 0.0 = escondida, TILE_SIZE = totalmente fuera
            self.wall_row = int(y / TILE_SIZE)
            self.wall_col = int(x / TILE_SIZE)
            # Sprites asignados desde Game: snake_head, snake_neck
            self.snake_head_sprite = None
            self.snake_neck_sprite = None

        # Bicho: se mueve en zona 3x3 tiles alrededor del spawn
        if enemy_type == "bug":
            spawn_col = int(x / TILE_SIZE)
            spawn_row = int(y / TILE_SIZE)
            self.bug_zone_min_x = (spawn_col - 1) * TILE_SIZE
            self.bug_zone_max_x = (spawn_col + 2) * TILE_SIZE - self.width
            self.bug_zone_min_y = (spawn_row - 1) * TILE_SIZE
            self.bug_zone_max_y = (spawn_row + 2) * TILE_SIZE - self.height
            # Dirección inicial aleatoria (incluye diagonales)
            angle = random.uniform(0, 2 * 3.14159)
            import math
            self.bug_dx = math.cos(angle)
            self.bug_dy = math.sin(angle)
            self.bug_change_timer = 0.0  # temporizador para cambios erráticos

    def check_collision(self, x, y, level_map):
        """Check collision with tiles using all 4 corners (margen de 1px)"""
        level_h = len(level_map) if level_map else 0
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
            if tile_x < 0 or tile_x >= len(level_map[tile_y]):
                return True

            tile = level_map[tile_y][tile_x]
            if tile in SOLID_TILES:
                return True

        return False

    def _find_ceiling_y(self, level_map):
        """Busca el techo más cercano arriba de la posición de spawn de la araña"""
        tile_x = int((self.start_x + self.width // 2) / TILE_SIZE)
        start_tile_y = int(self.start_y / TILE_SIZE)

        for tile_y in range(start_tile_y - 1, -1, -1):
            if 0 <= tile_y < len(level_map) and 0 <= tile_x < len(level_map[tile_y]):
                tile = level_map[tile_y][tile_x]
                if tile in SOLID_TILES:
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

        if self.enemy_type in ("snake_left", "snake_right"):
            # Víbora: ciclo hidden → emerging → extended → retracting
            if self.snake_state == "hidden":
                self.snake_timer -= dt
                if self.snake_timer <= 0:
                    self.snake_state = "emerging"
                    self.snake_extend = 0.0
            elif self.snake_state == "emerging":
                self.snake_extend += self.speed * dt
                if self.snake_extend >= TILE_SIZE:
                    self.snake_extend = TILE_SIZE
                    self.snake_state = "extended"
                    self.snake_timer = SNAKE_EXTENDED_TIME
            elif self.snake_state == "extended":
                self.snake_timer -= dt
                if self.snake_timer <= 0:
                    self.snake_state = "retracting"
            elif self.snake_state == "retracting":
                self.snake_extend -= self.speed * dt
                if self.snake_extend <= 0:
                    self.snake_extend = 0.0
                    self.snake_state = "hidden"
                    self.snake_timer = SNAKE_HIDDEN_TIME
            return

        elif self.enemy_type == "bug":
            import math
            # Movimiento errático: cambiar dirección aleatoriamente cada cierto tiempo
            self.bug_change_timer -= dt
            if self.bug_change_timer <= 0:
                # Nueva dirección aleatoria (cualquier ángulo, incluye diagonales)
                angle = random.uniform(0, 2 * math.pi)
                self.bug_dx = math.cos(angle)
                self.bug_dy = math.sin(angle)
                self.bug_change_timer = random.uniform(0.3, 1.0)

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
            elif self.check_collision(new_x, self.y, level_map):
                new_x = self.x
                bounced = True

            # Clamp vertical a zona y verificar colisión
            if new_y < self.bug_zone_min_y:
                new_y = self.bug_zone_min_y
                bounced = True
            elif new_y > self.bug_zone_max_y:
                new_y = self.bug_zone_max_y
                bounced = True
            elif self.check_collision(self.x, new_y, level_map):
                new_y = self.y
                bounced = True

            self.x = new_x
            self.y = new_y

            if bounced:
                # Rebotar: nueva dirección aleatoria
                angle = random.uniform(0, 2 * math.pi)
                self.bug_dx = math.cos(angle)
                self.bug_dy = math.sin(angle)
                self.bug_change_timer = random.uniform(0.3, 1.0)

            # Animación de alas (cicla entre 4 frames)
            if self.images:
                self.distance_traveled += self.speed * dt
                if self.distance_traveled >= BUG_ANIM_DISTANCE:
                    self.distance_traveled -= BUG_ANIM_DISTANCE
                    self.anim_frame = (self.anim_frame + 1) % len(self.images)
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

    def get_mask(self, masks):
        """Retorna la mask del sprite actual"""
        if self.enemy_type == "bat":
            key = 'bat' + str(self.anim_frame + 1)
            # El sprite del bat no se flipea en draw(), usar mask directa
            return masks.get(key)
        elif self.enemy_type == "spider":
            return masks.get('spider')
        elif self.enemy_type == "bug":
            key = 'bug' + str(self.anim_frame + 1)
            # Bicho volante no rota, usa mask directa
            return masks.get(key)
        # snake y otros: no usan mask (colisión por rect)
        return None

    def get_rect(self):
        if self.enemy_type in ("snake_left", "snake_right") and hasattr(self, 'snake_extend'):
            # Hitbox = solo la parte visible fuera de la pared (cuello + cabeza)
            ext = int(self.snake_extend)
            if ext <= 0:
                return pygame.Rect(0, 0, 0, 0)  # No hay hitbox cuando está escondida
            wall_x = self.wall_col * TILE_SIZE
            wall_y = self.wall_row * TILE_SIZE
            # Alto ajustado al cuerpo real de la víbora (~10px centrado en el tile)
            body_h = 10
            body_y = wall_y + (TILE_SIZE - body_h) // 2
            if self.snake_facing < 0:  # sale a la izquierda
                return pygame.Rect(wall_x - ext, body_y, ext, body_h)
            else:  # sale a la derecha
                return pygame.Rect(wall_x + TILE_SIZE, body_y, ext, body_h)
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def _draw_snake(self, screen, camera_x, camera_y, wall_tile=None):
        """Dibuja la víbora saliendo por detrás de la pared (estilo C64).
        La víbora se dibuja completa desplazándose, luego el tile de tierra
        se redibuja encima para taparla parcialmente.
        """
        ext = int(self.snake_extend)
        if ext <= 0:
            return

        wall_x = self.wall_col * TILE_SIZE
        wall_y = self.wall_row * TILE_SIZE
        # Usar int(camera) para coincidir con render_level() y evitar offset de 1px
        wall_sx = wall_x - int(camera_x)
        wall_sy = wall_y - int(camera_y)

        if not (-50 < wall_sy < GAME_VIEWPORT_HEIGHT + 50 and
                -80 < wall_sx < GAME_WIDTH + 80):
            return

        facing_left = (self.snake_facing < 0)

        # Dibujar cuello desde el borde de la pared hasta la cabeza
        # El cuello cubre todo el largo de extensión, la cabeza se dibuja encima
        if ext > 0 and self.snake_neck_sprite:
            neck_scaled = pygame.transform.scale(self.snake_neck_sprite, (ext, TILE_SIZE))
            if facing_left:
                screen.blit(neck_scaled, (int(wall_sx - ext), wall_sy))
            else:
                screen.blit(neck_scaled, (int(wall_sx + TILE_SIZE), wall_sy))

        # Cabeza en la punta (encima del cuello)
        if self.snake_head_sprite:
            if facing_left:
                head_x = wall_sx - ext
            else:
                head_x = wall_sx + TILE_SIZE + ext - TILE_SIZE
            screen.blit(self.snake_head_sprite, (int(head_x), wall_sy))

        # Redibujar el tile de tierra ENCIMA para tapar la parte que aún está adentro
        if wall_tile:
            screen.blit(wall_tile, (wall_sx, wall_sy))

    def draw(self, screen, camera_x, camera_y, level_map=None, wall_tile=None):
        # Víbora se dibuja con método propio
        if self.enemy_type in ("snake_left", "snake_right"):
            if self.exploding:
                wall_x = self.wall_col * TILE_SIZE
                wall_y = self.wall_row * TILE_SIZE
                sx = int(wall_x - camera_x)
                sy = int(wall_y - camera_y)
                if -50 < sy < GAME_VIEWPORT_HEIGHT + 50 and -50 < sx < GAME_WIDTH + 50:
                    progress = self.explosion_timer / self.explosion_duration
                    radius = int(8 + progress * 10)
                    for i in range(2):
                        r = radius - i * 5
                        if r > 0:
                            color = (139, 69, 19) if i == 0 else (101, 67, 33)
                            pygame.draw.circle(screen, color,
                                             (sx + 16, sy + 16), r)
            else:
                self._draw_snake(screen, camera_x, camera_y, wall_tile)
            return

        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        if -50 < screen_y < GAME_VIEWPORT_HEIGHT + 50 and -50 < screen_x < GAME_WIDTH + 50:
            if self.exploding:
                # Draw explosion animation - más pequeña y marrón
                progress = self.explosion_timer / self.explosion_duration
                radius = int(8 + progress * 10)

                cx = int(screen_x + self.width // 2)
                cy = int(screen_y + self.height // 2)
                for i in range(2):
                    r = radius - i * 5
                    if r > 0:
                        if i == 0:
                            color = (139, 69, 19)  # Marrón medio
                        else:
                            color = (101, 67, 33)  # Marrón oscuro
                        pygame.draw.circle(screen, color, (cx, cy), r)
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
                    screen.blit(self.image, (int(screen_x), int(screen_y)))
                else:
                    pygame.draw.circle(screen, COLOR_RED,
                                     (int(screen_x + self.width // 2), int(screen_y + self.height // 2)),
                                     self.width // 2 - 4)
