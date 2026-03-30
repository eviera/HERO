# Tests para evgamelib.collision

import pytest
import pygame
from evgamelib.collision import (
    mask_overlap, rect_overlap, check_corners_vs_tiles,
    binary_search_position
)


# Inicializar pygame para poder crear masks
pygame.init()


class TestMaskOverlap:
    def test_overlap_detected(self):
        mask1 = pygame.mask.Mask((10, 10), fill=True)
        mask2 = pygame.mask.Mask((10, 10), fill=True)
        result = mask_overlap(0, 0, mask1, 5, 5, mask2)
        assert result is not None

    def test_no_overlap(self):
        mask1 = pygame.mask.Mask((10, 10), fill=True)
        mask2 = pygame.mask.Mask((10, 10), fill=True)
        result = mask_overlap(0, 0, mask1, 20, 20, mask2)
        assert result is None

    def test_none_masks(self):
        mask1 = pygame.mask.Mask((10, 10), fill=True)
        assert mask_overlap(0, 0, None, 0, 0, mask1) is None
        assert mask_overlap(0, 0, mask1, 0, 0, None) is None


class TestRectOverlap:
    def test_overlapping(self):
        r1 = pygame.Rect(0, 0, 10, 10)
        r2 = pygame.Rect(5, 5, 10, 10)
        assert rect_overlap(r1, r2) == True

    def test_not_overlapping(self):
        r1 = pygame.Rect(0, 0, 10, 10)
        r2 = pygame.Rect(20, 20, 10, 10)
        assert rect_overlap(r1, r2) == False


class TestCheckCornersVsTiles:
    def test_collision_with_wall(self):
        level_map = ["####", "#  #", "####"]
        solid = {'#'}
        # Punto dentro de la pared (tile 0,0)
        assert check_corners_vs_tiles(0, 0, 10, 10, level_map, solid,
                                       tile_size=32, corners=[(1, 1)]) == True

    def test_no_collision_in_air(self):
        level_map = ["####", "#  #", "####"]
        solid = {'#'}
        # Punto en espacio abierto (tile 1, col 1)
        assert check_corners_vs_tiles(32, 32, 10, 10, level_map, solid,
                                       tile_size=32, corners=[(34, 34)]) == False

    def test_out_of_bounds(self):
        level_map = ["####"]
        solid = {'#'}
        # Fuera del mapa
        assert check_corners_vs_tiles(0, 0, 10, 10, level_map, solid,
                                       tile_size=32, corners=[(0, -1)]) == True


class TestBinarySearchPosition:
    def test_finds_boundary(self):
        # Colision a partir de x=100
        def collision_fn(x):
            return x >= 100

        result = binary_search_position(50, 150, collision_fn, steps=20)
        assert 99.99 < result < 100.01

    def test_no_collision(self):
        def collision_fn(x):
            return False

        result = binary_search_position(0, 100, collision_fn, steps=10)
        # Si no hay colision, devuelve un punto cercano al invalido
        assert result > 90  # Se acerca a 100
