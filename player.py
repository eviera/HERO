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

        # Horizontal movement
        move_x = 0
        if keys[pygame.K_LEFT] or joy_axis_x < -DEAD_ZONE:
            move_x = -1
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or joy_axis_x > DEAD_ZONE:
            move_x = 1
            self.facing_right = True

        self.vel_x = move_x * PLAYER_SPEED_X

        # Check if grounded (standing on something)
        # Test a position slightly below current position
        # Need to check far enough that collision points (y+29) would detect ground
        self.is_grounded = self.check_collision(self.x, self.y + 2, level_map)

        # GRAVITY - only apply if not grounded or using propulsor
        if not self.is_grounded or self.vel_y < 0:
            self.vel_y += GRAVITY * dt
        else:
            # Grounded and not jumping - zero velocity to prevent accumulation
            self.vel_y = 0

        # Propulsor - MANTENER PRESIONADO para volar
        self.using_propulsor = False
        if keys[pygame.K_UP] or joy_axis_y < -DEAD_ZONE:
            self.using_propulsor = True
            self.vel_y -= PROPULSOR_POWER * dt
            game.energy -= ENERGY_DRAIN_PROPULSOR * dt

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
            # Hit floor or ceiling - stop at last valid position
            self.vel_y = 0

        # Keep in level bounds
        self.x = max(0, min(self.x, LEVEL_WIDTH * TILE_SIZE - self.width))
        self.y = max(0, min(self.y, LEVEL_HEIGHT * TILE_SIZE - self.height))

        # Passive energy drain
        game.energy -= ENERGY_DRAIN_PASSIVE * dt

    def check_collision(self, x, y, level_map):
        """Check collision with tiles"""
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
                if tile == '#' or tile == 'B' or tile == '.':
                    return True

        return False

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen, camera_y):
        screen_y = self.y - camera_y
        if self.image:
            # Voltear sprite según orientación (invertido)
            img = self.image
            if self.facing_right:
                img = pygame.transform.flip(self.image, True, False)
            screen.blit(img, (int(self.x), int(screen_y)))
        else:
            # Draw simple helicopter
            pygame.draw.rect(screen, COLOR_BLUE,
                           (int(self.x + 8), int(screen_y + 12), 16, 12))
            # Rotor
            rotor_y = int(screen_y + 8)
            if self.using_propulsor:
                # Rotor spinning
                offset = (pygame.time.get_ticks() % 100) / 100 * 32
                pygame.draw.line(screen, COLOR_WHITE,
                               (int(self.x + offset), rotor_y),
                               (int(self.x + offset), rotor_y), 3)
            else:
                pygame.draw.line(screen, COLOR_WHITE,
                               (int(self.x), rotor_y),
                               (int(self.x + 32), rotor_y), 2)
            # Cockpit
            pygame.draw.circle(screen, (100, 150, 255),
                             (int(self.x + 16), int(screen_y + 16)), 6)
