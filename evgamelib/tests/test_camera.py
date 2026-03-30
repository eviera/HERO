# Tests para evgamelib.camera

import pytest
from evgamelib.camera import SnapCamera


class TestSnapCamera:
    def setup_method(self):
        self.cam = SnapCamera(viewport_w=512, viewport_h=256, tile_size=32)

    def test_initial_position(self):
        assert self.cam.x == 0
        assert self.cam.y == 0

    def test_snap_to_first_viewport(self):
        # Jugador en primera pantalla
        self.cam.update(100, 100, 32, 32, level_h_tiles=24)
        assert self.cam.x == 0
        assert self.cam.y == 0

    def test_snap_to_second_row(self):
        # Jugador en la segunda fila de viewports (y > 256)
        self.cam.update(100, 300, 32, 32, level_h_tiles=24)
        assert self.cam.y == 256

    def test_snap_to_second_col(self):
        # Jugador a la derecha del primer viewport (x > 512)
        def band_fn(tile_row):
            return 32  # 32 tiles de ancho
        self.cam.update(600, 100, 32, 32, level_h_tiles=24, band_width_fn=band_fn)
        assert self.cam.x == 512

    def test_clamp_at_bottom(self):
        # Jugador en la ultima fila, camara no baja mas del limite
        self.cam.update(100, 700, 32, 32, level_h_tiles=24)
        max_y = 24 * 32 - 256
        assert self.cam.y <= max_y

    def test_single_viewport_level(self):
        # Nivel de 1 viewport (16x8), camara siempre en 0,0
        self.cam.update(100, 100, 32, 32, level_h_tiles=8)
        assert self.cam.x == 0
        assert self.cam.y == 0

    def test_get_visible_tile_range(self):
        self.cam.x = 0
        self.cam.y = 0
        start_col, end_col, start_row, end_row = self.cam.get_visible_tile_range(16, 24)
        assert start_col == 0
        assert end_col == 16  # min(512/32 + 1, 16) = 16
        assert start_row == 0
        assert end_row == 9   # min(256/32 + 1, 24) = 9
