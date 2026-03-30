# evgamelib - Sistema de camara


class SnapCamera:
    """Camara que hace snap a boundaries de viewport.
    Soporta niveles con bandas de ancho variable."""

    def __init__(self, viewport_w, viewport_h, tile_size=32):
        self.x = 0
        self.y = 0
        self.viewport_w = viewport_w
        self.viewport_h = viewport_h
        self.tile_size = tile_size

    def update(self, player_x, player_y, player_w, player_h,
               level_h_tiles, band_width_fn=None):
        """Actualiza la camara con snap instantaneo al viewport del jugador.
        band_width_fn(tile_row) -> int: retorna ancho en tiles de la banda."""
        # Centro del jugador
        player_cx = int(player_x + player_w / 2)
        player_cy = int(player_y + player_h / 2)

        # Viewport actual del jugador
        viewport_col = player_cx // self.viewport_w
        viewport_row = player_cy // self.viewport_h

        # Eje horizontal
        if band_width_fn:
            player_tile_y = int(player_y / self.tile_size)
            current_band_w = band_width_fn(player_tile_y)
        else:
            current_band_w = self.viewport_w // self.tile_size

        max_cam_x = current_band_w * self.tile_size - self.viewport_w
        if max_cam_x > 0:
            self.x = max(0, min(viewport_col * self.viewport_w, max_cam_x))
        else:
            self.x = 0

        # Eje vertical
        max_cam_y = level_h_tiles * self.tile_size - self.viewport_h
        if max_cam_y > 0:
            self.y = max(0, min(viewport_row * self.viewport_h, max_cam_y))
        else:
            self.y = 0

    def get_visible_tile_range(self, level_w_tiles, level_h_tiles):
        """Retorna (start_col, end_col, start_row, end_row) de tiles visibles."""
        start_col = max(0, int(self.x / self.tile_size))
        end_col = min(level_w_tiles, int((self.x + self.viewport_w) / self.tile_size) + 1)
        start_row = max(0, int(self.y / self.tile_size))
        end_row = min(level_h_tiles, int((self.y + self.viewport_h) / self.tile_size) + 1)
        return start_col, end_col, start_row, end_row
