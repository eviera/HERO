# evgamelib - Utilidades de colision

import pygame


def mask_overlap(x1, y1, mask1, x2, y2, mask2):
    """Colision pixel-perfect entre dos masks.
    Retorna punto de overlap o None."""
    if mask1 is None or mask2 is None:
        return None
    offset = (int(x2 - x1), int(y2 - y1))
    return mask1.overlap(mask2, offset)


def rect_overlap(rect1, rect2):
    """Colision simple AABB (rectangulos alineados)."""
    return rect1.colliderect(rect2)


def check_corners_vs_tiles(x, y, width, height, level_map, solid_tiles,
                            tile_size=32, corners=None):
    """Colision por esquinas contra tiles solidos.
    corners: lista de (cx, cy) absolutos. Si None, usa las 4 esquinas con 1px de margen."""
    level_h = len(level_map) if level_map else 0
    if corners is None:
        corners = [
            (x + 1, y + 1),
            (x + width - 2, y + 1),
            (x + 1, y + height - 2),
            (x + width - 2, y + height - 2),
        ]
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


def mask_vs_tiles(x, y, entity_mask, level_map, tile_mask, solid_tiles,
                  width, height, tile_size=32):
    """Colision pixel-perfect de una entidad contra tiles solidos del mapa.
    Retorna True si hay colision, junto con info del tile tocado."""
    level_h = len(level_map) if level_map else 0
    if level_h == 0 or entity_mask is None:
        return False

    left_tile = int(x / tile_size)
    right_tile = int((x + width - 1) / tile_size)
    top_tile = int(y / tile_size)
    bottom_tile = int((y + height - 1) / tile_size)

    for ty in range(top_tile, bottom_tile + 1):
        if ty < 0 or ty >= level_h:
            return True
        for tx in range(left_tile, right_tile + 1):
            if tx < 0 or tx >= len(level_map[ty]):
                return True
            tile_char = level_map[ty][tx]
            if tile_char in solid_tiles:
                tile_px = tx * tile_size
                tile_py = ty * tile_size
                ox = int(x - tile_px)
                oy = int(y - tile_py)
                if entity_mask.overlap(tile_mask, (-ox, -oy)):
                    return True

    return False


def binary_search_position(valid_pos, invalid_pos, collision_fn, steps=10):
    """Busqueda binaria para encontrar la posicion mas cercana sin colision.
    collision_fn(pos) -> bool. Retorna la posicion valida mas cercana."""
    valid = valid_pos
    invalid = invalid_pos
    for _ in range(steps):
        mid = (valid + invalid) * 0.5
        if collision_fn(mid):
            invalid = mid
        else:
            valid = mid
    return valid
