# H.E.R.O. Remake - Sistema de paleta por profundidad
# Módulo compartido entre hero.py y editor.py
# Tintea tiles según la fila dentro de cada viewport (profundidad en la mina)
# La paleta se repite idéntica en cada viewport del nivel

import pygame
import random
from constants import VIEWPORT_ROWS, TILE_SIZE, SOLID_TILES

# Grosor del borde decorativo en píxeles (legacy, usado por draw_tile_edges)
EDGE_THICKNESS = 3

# Parámetros del overlay de musgo/raices
MOSS_BASE_H = 2        # Grosor base del borde sólido (horizontal)
MOSS_MAX_DOWN = 14     # Largo máximo de stalactitas (cuelgan del techo)
MOSS_MAX_UP = 12       # Largo máximo de stalagmitas (crecen del suelo)

# Parámetros de textura porosa del suelo
FLOOR_STREAKS = (5, 9)       # Rango de franjas por tile
FLOOR_STREAK_W = (6, 18)     # Ancho de franjas en px
FLOOR_STREAK_H = (1, 3)      # Alto de franjas en px
FLOOR_BLOBS = (3, 7)         # Rango de manchas por tile
FLOOR_BLOB_W = (3, 10)       # Ancho de manchas en px
FLOOR_BLOB_H = (2, 5)        # Alto de manchas en px
FLOOR_DOTS = (15, 25)        # Rango de poros por tile

# Tinte neutro (sin cambio de color)
NEUTRAL_TINT = [255, 255, 255]

# Color de borde por defecto (verde musgo, como en el C64 original)
DEFAULT_EDGE_COLOR = [80, 180, 60]


def get_depth_palette(screen_data):
    """Extraer depth_palette de un dict de nivel en screens.json.
    Retorna lista de {"wall": [r,g,b]} (2 entradas máximo)."""
    return screen_data.get("depth_palette", [])


def get_edge_color(screen_data):
    """Extraer edge_color de un dict de nivel en screens.json."""
    return screen_data.get("edge_color", list(DEFAULT_EDGE_COLOR))


def get_row_wall_color(depth_palette, row_index):
    """Obtener color de wall para una fila dada.
    Distribución fija dentro de cada viewport (se repite en cada uno):
      filas 0-4 (5 filas) -> entrada 0 (color principal)
      filas 5-7 (3 filas) -> entrada 1 (color secundario)"""
    if not depth_palette:
        return NEUTRAL_TINT

    # Fila relativa dentro del viewport actual (0 a VIEWPORT_ROWS-1)
    local_row = row_index % VIEWPORT_ROWS

    # Filas 0-4 -> entrada 0, filas 5-7 -> entrada 1
    entry_index = 0 if local_row < 5 else 1

    if entry_index >= len(depth_palette):
        return NEUTRAL_TINT

    return depth_palette[entry_index].get("wall", NEUTRAL_TINT)


def tint_surface(base_surface, color):
    """Crear una copia tintada de una superficie usando BLEND_RGB_MULT.
    color es [r, g, b] donde 255 = sin cambio en ese canal."""
    tinted = base_surface.copy()
    tinted.fill((color[0], color[1], color[2], 255), special_flags=pygame.BLEND_RGB_MULT)
    return tinted


def build_tinted_floors(base_tile, depth_palette):
    """Construir lista de tiles de suelo tintados (uno por fila del viewport).
    Filas 0-4 usan entrada 0, filas 5-7 usan entrada 1.
    Retorna lista de pygame.Surface indexada por fila local (0 a VIEWPORT_ROWS-1)."""
    # Pre-tintear solo los 2 colores distintos
    surfaces = [None, None]
    for i in range(2):
        if i < len(depth_palette):
            wall_color = depth_palette[i].get("wall", NEUTRAL_TINT)
            if wall_color == NEUTRAL_TINT:
                surfaces[i] = base_tile
            else:
                surfaces[i] = tint_surface(base_tile, wall_color)
        else:
            surfaces[i] = base_tile

    # Mapear cada fila del viewport a su superficie
    tinted = []
    for local_row in range(VIEWPORT_ROWS):
        entry_index = 0 if local_row < 5 else 1
        tinted.append(surfaces[entry_index])
    return tinted


def _is_solid(level_map, row, col):
    """Verificar si un tile es sólido (para detección de bordes)."""
    if row < 0 or row >= len(level_map):
        return True  # Fuera de límites = sólido
    row_data = level_map[row]
    if col < 0 or col >= len(row_data):
        return True  # Fuera de límites = sólido
    return row_data[col] in SOLID_TILES


def draw_tile_edges(surface, x, y, row, col, level_map, edge_color):
    """Dibujar bordes decorativos en las caras superior e inferior de un tile
    sólido que están expuestas al vacío (adyacente a tile no-sólido).
    x, y son las coordenadas en píxeles en la superficie destino.
    Usado por el editor. El juego usa generate_edge_overlay()."""
    t = EDGE_THICKNESS
    color = tuple(edge_color)

    # Cara superior: si el vecino de arriba no es sólido
    if not _is_solid(level_map, row - 1, col):
        pygame.draw.rect(surface, color, (x, y, TILE_SIZE, t))

    # Cara inferior: si el vecino de abajo no es sólido
    if not _is_solid(level_map, row + 1, col):
        pygame.draw.rect(surface, color, (x, y + TILE_SIZE - t, TILE_SIZE, t))


# ---------------------------------------------------------------------------
# Overlay de musgo/raíces (reemplaza draw_tile_edges en el juego principal)
# Se pre-genera una vez al cargar el nivel y se blitea por viewport
# ---------------------------------------------------------------------------

def _clamp_color(val):
    """Clampa un valor de color a 0-255"""
    return max(0, min(255, val))


def _jagged_heights(rng, count, min_h, max_h):
    """Genera alturas irregulares con clusters y gaps para borde dentado."""
    heights = []
    h = rng.randint(min_h, max(min_h + 1, max_h - 1))
    cluster_len = 0
    in_gap = False
    for i in range(count):
        if cluster_len <= 0:
            if in_gap:
                in_gap = False
                cluster_len = rng.randint(2, 6)
                h = rng.randint(min_h, max(min_h + 1, max_h))
            else:
                if rng.random() < 0.25:
                    in_gap = True
                    cluster_len = rng.randint(2, 6)
                else:
                    cluster_len = rng.randint(2, 5)
                    h = rng.randint(min_h, max_h)
        cluster_len -= 1
        if in_gap:
            heights.append(max(0, rng.randint(0, min_h)))
        else:
            h += rng.randint(-1, 1)
            h = max(min_h, min(max_h, h))
            # Picos largos ocasionales
            if rng.random() < 0.06:
                heights.append(min(max_h + 5, h + rng.randint(4, 10)))
            else:
                heights.append(h)
    return heights


def generate_edge_overlay(level_map, edge_color, seed=42):
    """Genera superficie SRCALPHA con musgo/raíces en bordes expuestos.
    Se llama una vez al inicio del nivel. El resultado se blitea por viewport."""
    level_h = len(level_map)
    level_w = max(len(row) for row in level_map)
    width = level_w * TILE_SIZE
    height = level_h * TILE_SIZE
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    rng = random.Random(seed)
    cr, cg, cb = edge_color[0], edge_color[1], edge_color[2]

    for row in range(level_h):
        for col in range(len(level_map[row])):
            tile = level_map[row][col]
            if tile != '.':
                continue
            px = col * TILE_SIZE
            py = row * TILE_SIZE

            # Cara inferior expuesta (techo -> stalactitas cuelgan)
            if not _is_solid(level_map, row + 1, col):
                _draw_moss_down(overlay, px, py + TILE_SIZE,
                                width, height, cr, cg, cb, rng)

            # Cara superior expuesta (suelo -> stalagmitas crecen)
            if not _is_solid(level_map, row - 1, col):
                _draw_moss_up(overlay, px, py,
                              width, height, cr, cg, cb, rng)

    return overlay


def _draw_moss_down(overlay, x, y0, sw, sh, cr, cg, cb, rng):
    """Stalactitas colgando del techo hacia abajo."""
    base_h = MOSS_BASE_H
    # Banda base (sparse - no todos los píxeles)
    for i in range(TILE_SIZE):
        bx = x + i
        if bx >= sw:
            break
        if rng.random() < 0.15:
            continue  # huecos en la base
        for dy in range(base_h):
            by = y0 + dy
            if by >= sh:
                break
            overlay.set_at((bx, by), (cr, cg, cb, 220))
    # Dentado irregular
    heights = _jagged_heights(rng, TILE_SIZE, 1, MOSS_MAX_DOWN)
    for i, h in enumerate(heights):
        bx = x + i
        if bx >= sw:
            break
        for dy in range(h):
            by = y0 + base_h + dy
            if by >= sh:
                break
            a = 240 if dy < h - 3 else max(80, 240 - (dy - (h - 3)) * 50)
            overlay.set_at((bx, by), (
                _clamp_color(cr + rng.randint(-8, 8)),
                _clamp_color(cg + rng.randint(-8, 8)),
                _clamp_color(cb + rng.randint(-8, 8)), a))
    # Tendriles finos extra
    for _ in range(rng.randint(1, 3)):
        tx_off = rng.randint(0, TILE_SIZE - 1)
        tx = x + tx_off
        base = heights[tx_off] if tx_off < len(heights) else 3
        tlen = rng.randint(3, 12)
        for dy in range(tlen):
            by = y0 + base_h + base + dy
            if by >= sh:
                break
            tx2 = tx + rng.randint(-1, 1)
            if 0 <= tx2 < sw:
                a = max(40, 180 - dy * 12)
                overlay.set_at((tx2, by), (cr, cg, cb, a))


def _draw_moss_up(overlay, x, y0, sw, sh, cr, cg, cb, rng):
    """Stalagmitas creciendo del suelo hacia arriba."""
    base_h = MOSS_BASE_H
    for i in range(TILE_SIZE):
        bx = x + i
        if bx >= sw:
            break
        if rng.random() < 0.15:
            continue  # huecos en la base
        for dy in range(base_h):
            by = y0 - 1 - dy
            if by < 0:
                break
            overlay.set_at((bx, by), (cr, cg, cb, 220))
    heights = _jagged_heights(rng, TILE_SIZE, 1, MOSS_MAX_UP)
    for i, h in enumerate(heights):
        bx = x + i
        if bx >= sw:
            break
        for dy in range(h):
            by = y0 - base_h - 1 - dy
            if by < 0:
                break
            a = 240 if dy < h - 3 else max(80, 240 - (dy - (h - 3)) * 50)
            overlay.set_at((bx, by), (
                _clamp_color(cr + rng.randint(-8, 8)),
                _clamp_color(cg + rng.randint(-8, 8)),
                _clamp_color(cb + rng.randint(-8, 8)), a))
    for _ in range(rng.randint(1, 3)):
        tx_off = rng.randint(0, TILE_SIZE - 1)
        tx = x + tx_off
        base = heights[tx_off] if tx_off < len(heights) else 3
        tlen = rng.randint(3, 10)
        for dy in range(tlen):
            by = y0 - base_h - 1 - base - dy
            if by < 0:
                break
            tx2 = tx + rng.randint(-1, 1)
            if 0 <= tx2 < sw:
                a = max(40, 180 - dy * 14)
                overlay.set_at((tx2, by), (cr, cg, cb, a))


def _draw_moss_left(overlay, x0, y, sw, sh, cr, cg, cb, rng):
    """Musgo creciendo hacia la izquierda."""
    base_w = MOSS_BASE_W
    for i in range(TILE_SIZE):
        by = y + i
        if by >= sh:
            break
        bw = base_w + (1 if rng.random() < 0.15 else 0)
        for dx in range(bw):
            bx = x0 - 1 - dx
            if bx < 0:
                break
            overlay.set_at((bx, by), (cr, cg, cb, 220))
    heights = _jagged_heights(rng, TILE_SIZE, 1, MOSS_MAX_SIDE)
    for i, h in enumerate(heights):
        by = y + i
        if by >= sh:
            break
        for dx in range(h):
            bx = x0 - base_w - 1 - dx
            if bx < 0:
                break
            a = 220 if dx < h - 2 else max(80, 220 - (dx - (h - 2)) * 60)
            overlay.set_at((bx, by), (
                _clamp_color(cr + rng.randint(-8, 8)),
                _clamp_color(cg + rng.randint(-8, 8)),
                _clamp_color(cb + rng.randint(-8, 8)), a))


def _draw_moss_right(overlay, x0, y, sw, sh, cr, cg, cb, rng):
    """Musgo creciendo hacia la derecha."""
    base_w = MOSS_BASE_W
    for i in range(TILE_SIZE):
        by = y + i
        if by >= sh:
            break
        bw = base_w + (1 if rng.random() < 0.15 else 0)
        for dx in range(bw):
            bx = x0 + dx
            if bx >= sw:
                break
            overlay.set_at((bx, by), (cr, cg, cb, 220))
    heights = _jagged_heights(rng, TILE_SIZE, 1, MOSS_MAX_SIDE)
    for i, h in enumerate(heights):
        by = y + i
        if by >= sh:
            break
        for dx in range(h):
            bx = x0 + base_w + dx
            if bx >= sw:
                break
            a = 220 if dx < h - 2 else max(80, 220 - (dx - (h - 2)) * 60)
            overlay.set_at((bx, by), (
                _clamp_color(cr + rng.randint(-8, 8)),
                _clamp_color(cg + rng.randint(-8, 8)),
                _clamp_color(cb + rng.randint(-8, 8)), a))


# ---------------------------------------------------------------------------
# Textura porosa del suelo (hoyos oscuros sobre tiles de suelo '.')
# Se pre-genera una vez al cargar el nivel y se blitea por viewport
# ---------------------------------------------------------------------------

# Colores oscuros para los hoyos/poros
_HOLE_COLORS = [
    (0, 0, 0),
    (10, 8, 3),
    (20, 15, 8),
    (5, 3, 1),
]


def generate_floor_texture(level_map, seed=42):
    """Genera overlay SRCALPHA con hoyos oscuros sobre tiles de suelo (.).
    Se llama una vez al inicio del nivel."""
    level_h = len(level_map)
    level_w = max(len(row) for row in level_map)
    width = level_w * TILE_SIZE
    height = level_h * TILE_SIZE
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    rng = random.Random(seed)

    # Tiles que reciben textura porosa (suelo y lava)
    _TEXTURED_TILES = {'.', 'X'}

    for row in range(level_h):
        for col in range(len(level_map[row])):
            if level_map[row][col] not in _TEXTURED_TILES:
                continue
            px = col * TILE_SIZE
            py = row * TILE_SIZE

            # Franjas horizontales oscuras
            num_streaks = rng.randint(*FLOOR_STREAKS)
            for _ in range(num_streaks):
                sy = py + rng.randint(0, TILE_SIZE - 1)
                sx = px + rng.randint(-6, TILE_SIZE - 1)
                streak_w = rng.randint(*FLOOR_STREAK_W)
                streak_h = rng.randint(*FLOOR_STREAK_H)
                color = rng.choice(_HOLE_COLORS)
                for dx in range(streak_w):
                    for dy in range(streak_h):
                        if rng.random() < 0.15:
                            continue
                        bx = sx + dx
                        by = sy + dy
                        # Clampar al tile actual para no escapar
                        if px <= bx < px + TILE_SIZE and py <= by < py + TILE_SIZE:
                            overlay.set_at((bx, by), (*color, 230))

            # Manchas irregulares
            num_blobs = rng.randint(*FLOOR_BLOBS)
            for _ in range(num_blobs):
                bx = px + rng.randint(0, TILE_SIZE - 1)
                by = py + rng.randint(0, TILE_SIZE - 1)
                blob_w = rng.randint(*FLOOR_BLOB_W)
                blob_h = rng.randint(*FLOOR_BLOB_H)
                color = rng.choice(_HOLE_COLORS)
                for dx in range(blob_w):
                    for dy in range(blob_h):
                        if rng.random() < 0.25:
                            continue
                        px2 = bx + dx
                        py2 = by + dy
                        # Clampar al tile actual para no escapar
                        if px <= px2 < px + TILE_SIZE and py <= py2 < py + TILE_SIZE:
                            overlay.set_at((px2, py2), (*color, 220))

            # Poros pequeños
            num_dots = rng.randint(*FLOOR_DOTS)
            for _ in range(num_dots):
                dx = px + rng.randint(0, TILE_SIZE - 1)
                dy = py + rng.randint(0, TILE_SIZE - 1)
                if 0 <= dx < width and 0 <= dy < height:
                    color = rng.choice(_HOLE_COLORS)
                    overlay.set_at((dx, dy), (*color, 200))
                    if rng.random() < 0.5:
                        dx2 = dx + rng.choice([-1, 0, 1])
                        if 0 <= dx2 < width:
                            overlay.set_at((dx2, dy), (*color, 180))

    return overlay
