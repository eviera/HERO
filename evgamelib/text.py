# evgamelib - Utilidades de texto

import pygame


def draw_text_with_outline(surface, font, text, color, outline_color, center, outline=1):
    """Dibuja texto con contorno (outline) en una superficie."""
    # Texto base
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=center)

    # Outline (dibujos alrededor)
    for dx in (-outline, 0, outline):
        for dy in (-outline, 0, outline):
            if dx != 0 or dy != 0:
                outline_surf = font.render(text, True, outline_color)
                outline_rect = outline_surf.get_rect(center=(center[0] + dx, center[1] + dy))
                surface.blit(outline_surf, outline_rect)

    # Texto principal arriba
    surface.blit(text_surf, text_rect)


class FloatingText:
    """Texto flotante que sube y se desvanece."""

    def __init__(self, x, y, text, duration=1.0):
        self.x = x
        self.y = y
        self.text = text
        self.timer = duration
        self.max_timer = duration


class FloatingTextManager:
    """Maneja una lista de textos flotantes."""

    def __init__(self):
        self.items = []

    def add(self, x, y, text, duration=1.0):
        """Agrega un texto flotante en coordenadas de mundo."""
        self.items.append(FloatingText(x, y, str(text), duration))

    def update(self, dt, rise_speed=30):
        """Actualiza posiciones y remueve los expirados."""
        for ft in self.items[:]:
            ft.timer -= dt
            ft.y -= rise_speed * dt
            if ft.timer <= 0:
                self.items.remove(ft)

    def render(self, surface, font, camera_x, camera_y, color, viewport_w, viewport_h):
        """Renderiza textos flotantes en la superficie dada."""
        for ft in self.items:
            alpha = int(255 * (ft.timer / ft.max_timer))
            text_surf = font.render(ft.text, True, color)

            screen_x = int(ft.x) - int(camera_x) - text_surf.get_width() // 2
            screen_y = int(ft.y) - int(camera_y)

            # Clampar dentro del viewport
            screen_x = max(0, min(screen_x, viewport_w - text_surf.get_width()))
            screen_y = max(0, min(screen_y, viewport_h - text_surf.get_height()))

            # Aplicar alpha
            alpha_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
            text_surf_alpha = font.render(ft.text, True, (*color, alpha))
            alpha_surf.blit(text_surf_alpha, (0, 0))

            surface.blit(alpha_surf, (screen_x, screen_y))
