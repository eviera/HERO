# H.E.R.O. Remake - Player Class

import pygame
from constants import *

class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vel_x = 0
        self.vel_y = 0
        self.width = 32
        self.height = 32
        self.facing_right = True
        self.using_propulsor = False
        self.is_grounded = False
        self.image = None
        self.image_fly = None
        self.image_shooting = None
        self.shooting_timer = 0  # Tiempo restante mostrando sprite de disparo
        self.walk_frames = []    # [walk1, walk2] sprites de caminata
        self.walk_sounds = []    # [walk1, walk2] sonidos alternados
        self.walk_distance = 0   # Distancia acumulada para alternar pasos
        self.walk_frame_index = 0  # Frame actual (0 o 1)
        self.is_walking = False  # Caminando sobre superficie
        self.propulsor_active_time = 0  # Tiempo acumulado usando propulsor (para warmup)
        # Animación de hélice
        self.propeller_timer = 0.0
        self.propeller_frame = 0
        self._prop_bodies = {}       # sprite_key -> Surface (cuerpo sin palas)
        self._prop_bodies_flip = {}  # sprite_key -> Surface (cuerpo flippeado)
        self._prop_frames = {}       # sprite_key -> [frame0, frame1, frame2, frame3]
        self._prop_frames_flip = {}  # sprite_key -> [frame0_flip, ...]

    def init(self, level_map):
        """Initialize player position from map"""
        for row_index, row in enumerate(level_map):
            for col_index, tile in enumerate(row):
                if tile == "S":
                    self.x = col_index * TILE_SIZE
                    self.y = row_index * TILE_SIZE
                    self.vel_x = 0
                    self.vel_y = 0
                    return
        # Default
        self.x = TILE_SIZE * 2
        self.y = TILE_SIZE * 2

    def update(self, dt, keys, joy_axis_x, joy_axis_y, level_map, game):
        """Update player with CORRECT HERO physics"""
        level_h = len(level_map) if level_map else DEFAULT_LEVEL_HEIGHT

        # Actualizar timer de disparo
        if self.shooting_timer > 0:
            self.shooting_timer -= dt

        # Horizontal movement - gradual con joystick, fijo con teclado
        move_x = 0
        if keys[pygame.K_LEFT]:
            move_x = -1
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            move_x = 1
            self.facing_right = True

        # Joystick horizontal: intensidad gradual
        if joy_axis_x < -DEAD_ZONE:
            move_x = joy_axis_x  # Valor entre -1.0 y -DEAD_ZONE
            self.facing_right = False
        elif joy_axis_x > DEAD_ZONE:
            move_x = joy_axis_x  # Valor entre DEAD_ZONE y 1.0
            self.facing_right = True

        self.vel_x = move_x * PLAYER_SPEED_X

        # Check if grounded (standing on something)
        self.is_grounded = self.check_collision(self.x, self.y + 2, level_map)

        # GRAVITY - only apply if not grounded or using propulsor
        if not self.is_grounded or self.vel_y < 0:
            self.vel_y += GRAVITY * dt
        else:
            # Grounded and not jumping - zero velocity to prevent accumulation
            self.vel_y = 0

        # Propulsor - con warmup: arranca en hover y sube a potencia completa
        # Solo funciona si hay energia
        self.using_propulsor = False
        if game.energy > 0:
            propulsor_input = 0  # 0 = no input, >0 = intensidad (0..1)
            if keys[pygame.K_UP]:
                propulsor_input = 1.0
            elif joy_axis_y < -DEAD_ZONE:
                propulsor_input = abs(joy_axis_y)  # 0.15 a 1.0

            if propulsor_input > 0:
                self.using_propulsor = True
                self.propulsor_active_time += dt
                # Propulsor siempre empuja a potencia completa
                self.vel_y -= PROPULSOR_POWER * propulsor_input * dt
                # Pero limitamos cuanto puede subir segun el warmup
                warmup_t = min(self.propulsor_active_time / PROPULSOR_WARMUP_TIME, 1.0)
                max_ascent = PROPULSOR_MAX_ASCENT_INITIAL + (PROPULSOR_MAX_ASCENT_FULL - PROPULSOR_MAX_ASCENT_INITIAL) * warmup_t
                # Clampar velocidad de ascenso (vel_y negativo = subiendo)
                if self.vel_y < -max_ascent:
                    self.vel_y = -max_ascent
            else:
                # Reset warmup cuando suelta el propulsor
                self.propulsor_active_time = 0

        # Descenso activo - helice invertida para bajar mas rapido
        if keys[pygame.K_DOWN]:
            self.vel_y += DIVE_POWER * dt
        elif joy_axis_y > DEAD_ZONE:
            intensity = abs(joy_axis_y)
            self.vel_y += DIVE_POWER * intensity * dt

        # Limit fall speed
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        # Apply velocities
        new_x = self.x + self.vel_x * dt
        new_y = self.y + self.vel_y * dt

        # Check horizontal collision
        if not self.check_collision(new_x, self.y, level_map):
            self.x = new_x
        else:
            self.vel_x = 0

        # Check vertical collision
        if not self.check_collision(self.x, new_y, level_map):
            self.y = new_y
        else:
            self.vel_y = 0

        # Keep in level bounds (ancho por banda, alto total)
        current_band_w = band_width(level_map, int(self.y / TILE_SIZE))
        self.x = max(0, min(self.x, current_band_w * TILE_SIZE - self.width))
        self.y = max(0, min(self.y, level_h * TILE_SIZE - self.height))

        # Energia: se consume siempre, ritmo segun estado
        if self.using_propulsor:
            game.energy -= ENERGY_DRAIN_FLYING * dt
        elif self.is_walking:
            game.energy -= ENERGY_DRAIN_WALKING * dt
        else:
            game.energy -= ENERGY_DRAIN_IDLE * dt
        game.energy = max(game.energy, 0)

        # Animacion de caminata: solo si esta en el suelo y se mueve horizontalmente
        if self.is_grounded and abs(self.vel_x) > 10 and not self.using_propulsor:
            self.is_walking = True
            self.walk_distance += abs(self.vel_x) * dt
            if self.walk_distance >= WALK_STEP_DISTANCE:
                self.walk_distance -= WALK_STEP_DISTANCE
                self.walk_frame_index = 1 - self.walk_frame_index
                # Reproducir sonido de paso alternado
                if self.walk_sounds:
                    self.walk_sounds[self.walk_frame_index].play()
        else:
            self.is_walking = False
            self.walk_distance = 0
            self.walk_frame_index = 0

        # Animación de hélice: gira lento en tierra, rápido en el aire
        prop_speed = PROPELLER_FAST_SPEED if (self.using_propulsor or not self.is_grounded) else PROPELLER_SLOW_SPEED
        self.propeller_timer += prop_speed * dt
        while self.propeller_timer >= 1.0:
            self.propeller_timer -= 1.0
            self.propeller_frame = (self.propeller_frame + 1) % PROPELLER_NUM_FRAMES

    def check_collision(self, x, y, level_map):
        """Check collision with tiles (hitbox estrecho centrado en el cuerpo)"""
        level_h = len(level_map) if level_map else 0
        corners = [
            (x + PLAYER_FOOT_INSET, y + 2),
            (x + self.width - PLAYER_FOOT_INSET - 1, y + 2),
            (x + PLAYER_FOOT_INSET, y + self.height - 3),
            (x + self.width - PLAYER_FOOT_INSET - 1, y + self.height - 3)
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

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_mask(self, masks):
        """Retorna la mask del sprite actual según prioridad de dibujo"""
        if self.shooting_timer > 0 and self.image_shooting:
            key = 'player_shooting'
        elif not self.is_grounded and self.image_fly:
            key = 'player_fly'
        elif self.is_walking and self.walk_frames:
            key = 'player_walk' + str(self.walk_frame_index + 1)
        else:
            key = 'player'
        # Versión flipped si mira a la derecha (sprite base mira a la izquierda)
        if self.facing_right:
            return masks.get(key + '_flip')
        return masks.get(key)

    def draw(self, screen, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        if self.image:
            # Determinar sprite_key según prioridad: disparo > vuelo > caminata > idle
            if self.shooting_timer > 0 and self.image_shooting:
                sprite_key = 'player_shooting'
            elif not self.is_grounded and self.image_fly:
                sprite_key = 'player_fly'
            elif self.is_walking and self.walk_frames:
                sprite_key = 'player_walk' + str(self.walk_frame_index + 1)
            else:
                sprite_key = 'player'

            pos = (int(screen_x), int(screen_y))

            # Composición cuerpo + hélice animada (2 blits, sin transforms en runtime)
            if sprite_key in self._prop_bodies:
                if self.facing_right:
                    screen.blit(self._prop_bodies_flip[sprite_key], pos)
                    screen.blit(self._prop_frames_flip[sprite_key][self.propeller_frame], pos)
                else:
                    screen.blit(self._prop_bodies[sprite_key], pos)
                    screen.blit(self._prop_frames[sprite_key][self.propeller_frame], pos)
            else:
                # Fallback: sprite original sin animación de hélice
                if sprite_key == 'player_shooting':
                    base_img = self.image_shooting
                elif sprite_key == 'player_fly':
                    base_img = self.image_fly
                elif sprite_key.startswith('player_walk'):
                    base_img = self.walk_frames[self.walk_frame_index]
                else:
                    base_img = self.image
                if self.facing_right:
                    base_img = pygame.transform.flip(base_img, True, False)
                screen.blit(base_img, pos)
        else:
            # Draw simple helicopter
            pygame.draw.rect(screen, COLOR_BLUE,
                           (int(screen_x + 8), int(screen_y + 12), 16, 12))
            # Rotor
            rotor_y = int(screen_y + 8)
            if self.using_propulsor:
                # Rotor spinning
                offset = (pygame.time.get_ticks() % 100) / 100 * 32
                pygame.draw.line(screen, COLOR_WHITE,
                               (int(screen_x + offset), rotor_y),
                               (int(screen_x + offset), rotor_y), 3)
            else:
                pygame.draw.line(screen, COLOR_WHITE,
                               (int(screen_x), rotor_y),
                               (int(screen_x + 32), rotor_y), 2)
            # Cockpit
            pygame.draw.circle(screen, (100, 150, 255),
                             (int(screen_x + 16), int(screen_y + 16)), 6)
