# Tests para evgamelib.tilemap

import pytest
from evgamelib.tilemap import TileMap, band_width, row_width, max_level_width


class TestTileMap:
    def setup_method(self):
        self.grid = [
            "################",
            "#S             #",
            "#  ...  ...    #",
            "#              #",
            "#   V     A    #",
            "#  ...  ...    #",
            "#        M     #",
            "################",
        ]
        self.tm = TileMap(self.grid, tile_size=32, viewport_cols=16, viewport_rows=8)

    def test_height(self):
        assert self.tm.height == 8

    def test_width(self):
        assert self.tm.width == 16

    def test_row_width(self):
        assert self.tm.row_width(0) == 16
        assert self.tm.row_width(-1) == 0
        assert self.tm.row_width(100) == 0

    def test_band_width(self):
        assert self.tm.band_width(0) == 16
        assert self.tm.band_width(7) == 16

    def test_tile_at(self):
        assert self.tm.tile_at(0, 0) == '#'
        assert self.tm.tile_at(1, 1) == 'S'
        assert self.tm.tile_at(6, 9) == 'M'
        assert self.tm.tile_at(-1, 0) == ' '  # fuera de rango
        assert self.tm.tile_at(100, 0) == ' '

    def test_set_tile(self):
        self.tm.set_tile(1, 1, 'X')
        assert self.tm.tile_at(1, 1) == 'X'

    def test_is_solid(self):
        solid = {'#', '.', 'G', 'R', 'X', 'W'}
        assert self.tm.is_solid(0, 0, solid) == True
        assert self.tm.is_solid(1, 2, solid) == False

    def test_find_tile(self):
        result = self.tm.find_tile('S')
        assert result == (1, 1)

        result = self.tm.find_tile('M')
        assert result == (6, 9)

        result = self.tm.find_tile('Z')
        assert result is None

    def test_find_all_tiles(self):
        dots = list(self.tm.find_all_tiles('.'))
        assert len(dots) == 12  # 6 dots per row * 2 rows

    def test_max_width(self):
        assert self.tm.max_width() == 16


class TestStandaloneFunctions:
    def test_band_width_empty(self):
        assert band_width([], 0) == 16

    def test_band_width_normal(self):
        grid = ["################"] * 8
        assert band_width(grid, 0) == 16
        assert band_width(grid, 7) == 16

    def test_row_width_empty(self):
        assert row_width([], 0) == 0

    def test_row_width_normal(self):
        grid = ["################"]
        assert row_width(grid, 0) == 16

    def test_max_level_width_empty(self):
        assert max_level_width([]) == 0

    def test_max_level_width_variable(self):
        grid = ["########", "################"]
        assert max_level_width(grid) == 16
