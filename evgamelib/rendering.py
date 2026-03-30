# evgamelib - Pipeline de renderizado

import pygame


class RenderPipeline:
    """Pipeline de renderizado de dos superficies con HUD y fullscreen."""

    def __init__(self, game_w, game_h, render_scale, hud_height, screen_w=None, screen_h=None):
        """
        game_w, game_h: dimensiones de la superficie de juego (sin escalar)
        render_scale: factor de escala para la superficie de juego
        hud_height: altura del HUD en pixels
        """
        self.game_w = game_w
        self.game_h = game_h
        self.render_scale_factor = render_scale
        self.hud_height = hud_height

        # Dimensiones de screen
        self.screen_w = screen_w or int(game_w * render_scale)
        self.screen_h = screen_h or (int(game_h * render_scale) + hud_height)
        self.viewport_h = int(game_h * render_scale)

        # Superficies
        self.game_surface = pygame.Surface((game_w, game_h))
        self.screen = pygame.Surface((self.screen_w, self.screen_h))
        self._scaled_game = pygame.Surface((self.screen_w, self.viewport_h))

        # Display
        self.display_surface = None
        self.fullscreen = False

        # Scaling para display
        self.render_scale = 1.0
        self.render_w = self.screen_w
        self.render_h = self.screen_h
        self.render_x = 0
        self.render_y = 0

    def init_display(self, fullscreen=True):
        """Crea la superficie de display."""
        self.fullscreen = fullscreen
        if fullscreen:
            self.display_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.display_surface = pygame.display.set_mode((self.screen_w, self.screen_h))
        self._update_scaling()

    def toggle_fullscreen(self):
        """Alterna entre ventana y pantalla completa."""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.display_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.display_surface = pygame.display.set_mode((self.screen_w, self.screen_h))
        self._update_scaling()

    def _update_scaling(self):
        """Calcula escala y offset para mantener aspect ratio."""
        display_w, display_h = self.display_surface.get_size()
        scale_x = display_w / self.screen_w
        scale_y = display_h / self.screen_h
        self.render_scale = min(scale_x, scale_y)
        self.render_w = int(self.screen_w * self.render_scale)
        self.render_h = int(self.screen_h * self.render_scale)
        self.render_x = (display_w - self.render_w) // 2
        self.render_y = (display_h - self.render_h) // 2

    def scale_game_to_screen(self):
        """Escala game_surface a la zona de juego del screen."""
        pygame.transform.scale(self.game_surface, (self.screen_w, self.viewport_h), self._scaled_game)
        self.screen.blit(self._scaled_game, (0, 0))

    def present(self):
        """Escala screen a display_surface y flip."""
        self.display_surface.fill((0, 0, 0))
        if self.render_w != self.screen_w or self.render_h != self.screen_h:
            scaled = pygame.transform.scale(self.screen, (self.render_w, self.render_h))
            self.display_surface.blit(scaled, (self.render_x, self.render_y))
        else:
            self.display_surface.blit(self.screen, (self.render_x, self.render_y))
        pygame.display.flip()
