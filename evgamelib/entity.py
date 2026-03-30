# evgamelib - Clases base de entidades

import pygame


class Entity:
    """Entidad base con posicion, tamaño y estado activo."""

    def __init__(self, x=0, y=0, width=32, height=32):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.active = True
        self.image = None

    def get_rect(self):
        """Retorna el rectangulo de colision."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def is_on_screen(self, camera_x, camera_y, viewport_w, viewport_h, margin=50):
        """Verifica si la entidad esta visible en el viewport."""
        sx = self.x - camera_x
        sy = self.y - camera_y
        return (-margin < sx < viewport_w + margin and
                -margin < sy < viewport_h + margin)

    def draw(self, surface, camera_x, camera_y):
        """Renderiza la entidad. Override en subclases."""
        if self.image and self.is_on_screen(camera_x, camera_y,
                                             surface.get_width(), surface.get_height()):
            screen_x = int(self.x - camera_x)
            screen_y = int(self.y - camera_y)
            surface.blit(self.image, (screen_x, screen_y))


class PhysicsEntity(Entity):
    """Entidad con velocidad y gravedad."""

    def __init__(self, x=0, y=0, width=32, height=32):
        super().__init__(x, y, width, height)
        self.vel_x = 0
        self.vel_y = 0

    def apply_gravity(self, dt, gravity, max_fall_speed=None):
        """Aplica gravedad a vel_y."""
        self.vel_y += gravity * dt
        if max_fall_speed is not None and self.vel_y > max_fall_speed:
            self.vel_y = max_fall_speed

    def check_collision_corners(self, x, y, level_map, solid_tiles, corners=None):
        """Colision por esquinas contra tiles solidos.
        corners: lista de (dx, dy) offsets desde (x, y).
        Default: 4 esquinas con 1px de margen."""
        level_h = len(level_map) if level_map else 0
        if corners is None:
            corners = [
                (x + 1, y + 1),
                (x + self.width - 2, y + 1),
                (x + 1, y + self.height - 2),
                (x + self.width - 2, y + self.height - 2),
            ]
        tile_size = 32  # default
        for cx, cy in corners:
            tx = int(cx / tile_size)
            ty = int(cy / tile_size)
            if ty < 0 or ty >= level_h:
                return True
            if tx < 0 or tx >= len(level_map[ty]):
                return True
            if level_map[ty][tx] in solid_tiles:
                return True
        return False

    def move_with_binary_search(self, new_x, new_y, level_map, collision_fn, steps=10):
        """Mueve la entidad resolviendo colisiones con busqueda binaria.
        collision_fn(x, y, level_map) -> bool"""
        # Horizontal
        if not collision_fn(new_x, self.y, level_map):
            self.x = new_x
        else:
            valid = self.x
            invalid = new_x
            for _ in range(steps):
                mid = (valid + invalid) * 0.5
                if collision_fn(mid, self.y, level_map):
                    invalid = mid
                else:
                    valid = mid
            self.x = valid
            self.vel_x = 0

        # Vertical
        if not collision_fn(self.x, new_y, level_map):
            self.y = new_y
        else:
            valid = self.y
            invalid = new_y
            for _ in range(steps):
                mid = (valid + invalid) * 0.5
                if collision_fn(self.x, mid, level_map):
                    invalid = mid
                else:
                    valid = mid
            self.y = valid
            self.vel_y = 0


class AnimatedEntity(Entity):
    """Entidad con animacion de frames basada en distancia recorrida."""

    def __init__(self, x=0, y=0, width=32, height=32):
        super().__init__(x, y, width, height)
        self.images = None        # lista de frames de animacion
        self.anim_frame = 0
        self.distance_traveled = 0
        self.anim_distance = 8    # pixels entre cambios de frame

    def advance_animation(self, distance_delta):
        """Avanza el frame de animacion segun distancia recorrida."""
        if not self.images or len(self.images) <= 1:
            return
        self.distance_traveled += abs(distance_delta)
        if self.distance_traveled >= self.anim_distance:
            self.distance_traveled -= self.anim_distance
            self.anim_frame = (self.anim_frame + 1) % len(self.images)
            self.image = self.images[self.anim_frame]
