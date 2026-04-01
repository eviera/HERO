# H.E.R.O. Remake - Sistema de paleta por profundidad
# Módulo compartido entre hero.py y editor.py
# Tintea tiles según la fila dentro de cada viewport (profundidad en la mina)
# La paleta se repite idéntica en cada viewport del nivel

import pygame
import random
from constants import (
    VIEWPORT_ROWS, TILE_SIZE, SOLID_TILES,
    # Textura C64 (suelo/lava)
    OVERLAY_CHEVRON_PERIOD, OVERLAY_CHEVRON_W, OVERLAY_CHEVRON_H, OVERLAY_CHEVRON_THICKNESS,
    OVERLAY_CHEVRON_SPACING, OVERLAY_CHEVRON_IRREGULARITY, OVERLAY_NOISE_DENSITY,
    OVERLAY_CLUSTER_COUNT, OVERLAY_CLUSTER_SIZE, OVERLAY_CLUSTER_FILL,
    OVERLAY_BIG_HOLE_COUNT, OVERLAY_BIG_HOLE_W, OVERLAY_BIG_HOLE_H, OVERLAY_BIG_HOLE_EDGE_SKIP,
    OVERLAY_TEETH_COUNT, OVERLAY_TEETH_W, OVERLAY_TEETH_DEPTH, OVERLAY_TEETH_BASE_GAP,
    OVERLAY_TEETH_BASE_EXTRA,
    # Musgo/raíces
    MOSS_BASE_H, MOSS_BASE_W, MOSS_MAX_DOWN, MOSS_MAX_UP, MOSS_MAX_SIDE,
    MOSS_BASE_GAP_CHANCE, MOSS_COLOR_VARIATION, MOSS_ALPHA_TIP, MOSS_ALPHA_BASE,
    MOSS_TENDRIL_COUNT, MOSS_TENDRIL_LENGTH,
    MOSS_JAG_GAP_CHANCE, MOSS_JAG_CLUSTER_LEN, MOSS_JAG_PEAK_CHANCE,
    MOSS_JAG_PEAK_EXTRA,
)

# Grosor del borde decorativo en píxeles (legacy, usado por draw_tile_edges)
EDGE_THICKNESS = 3

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
                cluster_len = rng.randint(*MOSS_JAG_CLUSTER_LEN)
                h = rng.randint(min_h, max(min_h + 1, max_h))
            else:
                if rng.random() < MOSS_JAG_GAP_CHANCE:
                    in_gap = True
                    cluster_len = rng.randint(*MOSS_JAG_CLUSTER_LEN)
                else:
                    cluster_len = rng.randint(*MOSS_JAG_CLUSTER_LEN)
                    h = rng.randint(min_h, max_h)
        cluster_len -= 1
        if in_gap:
            heights.append(max(0, rng.randint(0, min_h)))
        else:
            h += rng.randint(-1, 1)
            h = max(min_h, min(max_h, h))
            # Picos largos ocasionales
            if rng.random() < MOSS_JAG_PEAK_CHANCE:
                heights.append(min(max_h + 5, h + rng.randint(*MOSS_JAG_PEAK_EXTRA)))
            else:
                heights.append(h)
    return heights


def generate_edge_overlay(level_map, edge_color, seed=42, skip_tiles=None):
    """Genera superficie SRCALPHA con musgo/raíces en bordes expuestos.
    Se llama una vez al inicio del nivel. El resultado se blitea por viewport.
    skip_tiles: set de (row, col) a excluir del musgo (ej: tiles de víbora)."""
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
            if skip_tiles and (row, col) in skip_tiles:
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
    v = MOSS_COLOR_VARIATION
    # Banda base (sparse - no todos los píxeles)
    for i in range(TILE_SIZE):
        bx = x + i
        if bx >= sw:
            break
        if rng.random() < MOSS_BASE_GAP_CHANCE:
            continue  # huecos en la base
        for dy in range(base_h):
            by = y0 + dy
            if by >= sh:
                break
            overlay.set_at((bx, by), (cr, cg, cb, MOSS_ALPHA_BASE))
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
            a = MOSS_ALPHA_BASE if dy < h - 3 else max(MOSS_ALPHA_TIP, MOSS_ALPHA_BASE - (dy - (h - 3)) * 50)
            overlay.set_at((bx, by), (
                _clamp_color(cr + rng.randint(-v, v)),
                _clamp_color(cg + rng.randint(-v, v)),
                _clamp_color(cb + rng.randint(-v, v)), a))
    # Tendriles finos extra
    for _ in range(rng.randint(*MOSS_TENDRIL_COUNT)):
        tx_off = rng.randint(0, TILE_SIZE - 1)
        tx = x + tx_off
        base = heights[tx_off] if tx_off < len(heights) else 3
        tlen = rng.randint(*MOSS_TENDRIL_LENGTH)
        for dy in range(tlen):
            by = y0 + base_h + base + dy
            if by >= sh:
                break
            tx2 = tx + rng.randint(-1, 1)
            if 0 <= tx2 < sw:
                a = max(MOSS_ALPHA_TIP // 2, 180 - dy * 12)
                overlay.set_at((tx2, by), (cr, cg, cb, a))


def _draw_moss_up(overlay, x, y0, sw, sh, cr, cg, cb, rng):
    """Stalagmitas creciendo del suelo hacia arriba."""
    base_h = MOSS_BASE_H
    v = MOSS_COLOR_VARIATION
    for i in range(TILE_SIZE):
        bx = x + i
        if bx >= sw:
            break
        if rng.random() < MOSS_BASE_GAP_CHANCE:
            continue  # huecos en la base
        for dy in range(base_h):
            by = y0 - 1 - dy
            if by < 0:
                break
            overlay.set_at((bx, by), (cr, cg, cb, MOSS_ALPHA_BASE))
    heights = _jagged_heights(rng, TILE_SIZE, 1, MOSS_MAX_UP)
    for i, h in enumerate(heights):
        bx = x + i
        if bx >= sw:
            break
        for dy in range(h):
            by = y0 - base_h - 1 - dy
            if by < 0:
                break
            a = MOSS_ALPHA_BASE if dy < h - 3 else max(MOSS_ALPHA_TIP, MOSS_ALPHA_BASE - (dy - (h - 3)) * 50)
            overlay.set_at((bx, by), (
                _clamp_color(cr + rng.randint(-v, v)),
                _clamp_color(cg + rng.randint(-v, v)),
                _clamp_color(cb + rng.randint(-v, v)), a))
    for _ in range(rng.randint(*MOSS_TENDRIL_COUNT)):
        tx_off = rng.randint(0, TILE_SIZE - 1)
        tx = x + tx_off
        base = heights[tx_off] if tx_off < len(heights) else 3
        tlen = rng.randint(*MOSS_TENDRIL_LENGTH)
        for dy in range(tlen):
            by = y0 - base_h - 1 - base - dy
            if by < 0:
                break
            tx2 = tx + rng.randint(-1, 1)
            if 0 <= tx2 < sw:
                a = max(MOSS_ALPHA_TIP // 2, 180 - dy * 14)
                overlay.set_at((tx2, by), (cr, cg, cb, a))


def _draw_moss_left(overlay, x0, y, sw, sh, cr, cg, cb, rng):
    """Musgo creciendo hacia la izquierda."""
    base_w = MOSS_BASE_W
    v = MOSS_COLOR_VARIATION
    for i in range(TILE_SIZE):
        by = y + i
        if by >= sh:
            break
        bw = base_w + (1 if rng.random() < MOSS_BASE_GAP_CHANCE else 0)
        for dx in range(bw):
            bx = x0 - 1 - dx
            if bx < 0:
                break
            overlay.set_at((bx, by), (cr, cg, cb, MOSS_ALPHA_BASE))
    heights = _jagged_heights(rng, TILE_SIZE, 1, MOSS_MAX_SIDE)
    for i, h in enumerate(heights):
        by = y + i
        if by >= sh:
            break
        for dx in range(h):
            bx = x0 - base_w - 1 - dx
            if bx < 0:
                break
            a = MOSS_ALPHA_BASE if dx < h - 2 else max(MOSS_ALPHA_TIP, MOSS_ALPHA_BASE - (dx - (h - 2)) * 60)
            overlay.set_at((bx, by), (
                _clamp_color(cr + rng.randint(-v, v)),
                _clamp_color(cg + rng.randint(-v, v)),
                _clamp_color(cb + rng.randint(-v, v)), a))


def _draw_moss_right(overlay, x0, y, sw, sh, cr, cg, cb, rng):
    """Musgo creciendo hacia la derecha."""
    base_w = MOSS_BASE_W
    v = MOSS_COLOR_VARIATION
    for i in range(TILE_SIZE):
        by = y + i
        if by >= sh:
            break
        bw = base_w + (1 if rng.random() < MOSS_BASE_GAP_CHANCE else 0)
        for dx in range(bw):
            bx = x0 + dx
            if bx >= sw:
                break
            overlay.set_at((bx, by), (cr, cg, cb, MOSS_ALPHA_BASE))
    heights = _jagged_heights(rng, TILE_SIZE, 1, MOSS_MAX_SIDE)
    for i, h in enumerate(heights):
        by = y + i
        if by >= sh:
            break
        for dx in range(h):
            bx = x0 + base_w + dx
            if bx >= sw:
                break
            a = MOSS_ALPHA_BASE if dx < h - 2 else max(MOSS_ALPHA_TIP, MOSS_ALPHA_BASE - (dx - (h - 2)) * 60)
            overlay.set_at((bx, by), (
                _clamp_color(cr + rng.randint(-v, v)),
                _clamp_color(cg + rng.randint(-v, v)),
                _clamp_color(cb + rng.randint(-v, v)), a))


# ---------------------------------------------------------------------------
# Overlay de textura para tiles de suelo (.) y lava (X)
# Solo negro puro (0,0,0,255) o nada. Sin degradados ni alpha parcial.
# Patrón: bandas zigzag horizontales + ruido + dientes en bordes expuestos
# ---------------------------------------------------------------------------

_BLACK = (0, 0, 0, 255)


def _is_empty(level_map, row, col):
    """Verificar si un tile es vacío (aire, o fuera de límites)."""
    if row < 0 or row >= len(level_map):
        return False
    row_data = level_map[row]
    if col < 0 or col >= len(row_data):
        return False
    return row_data[col] not in SOLID_TILES


def generate_floor_texture(level_map, seed=42):
    """Genera overlay SRCALPHA estilo C64: solo negro puro sobre tiles de suelo/lava.
    Patrón de bandas zigzag horizontales + ruido disperso + dientes en bordes.
    Se llama una vez al inicio del nivel."""
    level_h = len(level_map)
    level_w = max(len(row) for row in level_map)
    width = level_w * TILE_SIZE
    height = level_h * TILE_SIZE
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    rng = random.Random(seed)

    _TEXTURED_TILES = {'.', 'X'}

    for row in range(level_h):
        for col in range(len(level_map[row])):
            tile = level_map[row][col]
            if tile not in _TEXTURED_TILES:
                continue
            px = col * TILE_SIZE
            py = row * TILE_SIZE

            # --- Filas de chevrones grandes (estilo C64) ---
            period = OVERLAY_CHEVRON_PERIOD
            y_offset = rng.randint(0, period - 1)

            for band_y in range(y_offset, TILE_SIZE + period, period):
                # Llenar la fila con chevrones uno al lado del otro
                cx = rng.randint(-4, 2)  # offset inicial aleatorio
                while cx < TILE_SIZE:
                    cw = rng.randint(*OVERLAY_CHEVRON_W)
                    ch = rng.randint(*OVERLAY_CHEVRON_H)
                    thick = rng.randint(*OVERLAY_CHEVRON_THICKNESS)
                    # Dibujar chevrón: forma de V invertida (∧)
                    half = cw // 2
                    for lx in range(cw):
                        # Altura del trazo en esta columna (forma de V)
                        dist_center = abs(lx - half)
                        # La V baja desde los extremos hacia el centro
                        stripe_y = ch * dist_center // max(1, half)
                        for t in range(thick):
                            bx = px + cx + lx
                            by = py + band_y + stripe_y + t
                            if px <= bx < px + TILE_SIZE and py <= by < py + TILE_SIZE:
                                overlay.set_at((bx, by), _BLACK)
                            # Píxeles extras para irregularidad
                            if rng.random() < OVERLAY_CHEVRON_IRREGULARITY:
                                by2 = by + rng.choice([-1, 1])
                                if py <= by2 < py + TILE_SIZE and px <= bx < px + TILE_SIZE:
                                    overlay.set_at((bx, by2), _BLACK)

                    cx += cw + rng.randint(*OVERLAY_CHEVRON_SPACING)

            # --- Clusters de píxeles negros (cavidades pequeñas) ---
            num_clusters = rng.randint(*OVERLAY_CLUSTER_COUNT)
            for _ in range(num_clusters):
                cx = rng.randint(0, TILE_SIZE - 1)
                cy = rng.randint(0, TILE_SIZE - 1)
                size = rng.randint(*OVERLAY_CLUSTER_SIZE)
                for dx in range(size):
                    for dy in range(size):
                        if rng.random() > OVERLAY_CLUSTER_FILL:
                            continue
                        bx = px + cx + dx
                        by = py + cy + dy
                        if px <= bx < px + TILE_SIZE and py <= by < py + TILE_SIZE:
                            overlay.set_at((bx, by), _BLACK)

            # --- Agujeros grandes aleatorios ---
            num_holes = rng.randint(*OVERLAY_BIG_HOLE_COUNT)
            for _ in range(num_holes):
                hx = rng.randint(1, TILE_SIZE - 4)
                hy = rng.randint(1, TILE_SIZE - 4)
                hw = rng.randint(*OVERLAY_BIG_HOLE_W)
                hh = rng.randint(*OVERLAY_BIG_HOLE_H)
                for dx in range(hw):
                    for dy in range(hh):
                        # Forma irregular: bordes con huecos aleatorios
                        edge = (dx == 0 or dx == hw - 1 or dy == 0 or dy == hh - 1)
                        if edge and rng.random() < OVERLAY_BIG_HOLE_EDGE_SKIP:
                            continue
                        bx = px + hx + dx
                        by = py + hy + dy
                        if px <= bx < px + TILE_SIZE and py <= by < py + TILE_SIZE:
                            overlay.set_at((bx, by), _BLACK)

            # --- Ruido disperso (píxeles sueltos) ---
            for ly in range(TILE_SIZE):
                for lx in range(TILE_SIZE):
                    if rng.random() < OVERLAY_NOISE_DENSITY:
                        overlay.set_at((px + lx, py + ly), _BLACK)

            # --- Dientes irregulares en bordes expuestos al vacío ---
            # Cara superior expuesta (dientes crecen hacia arriba = dentro del tile)
            if _is_empty(level_map, row - 1, col):
                _draw_c64_teeth_top(overlay, px, py, rng)
            # Cara inferior expuesta (dientes cuelgan hacia abajo = dentro del tile)
            if _is_empty(level_map, row + 1, col):
                _draw_c64_teeth_bottom(overlay, px, py, rng)
            # Cara izquierda expuesta
            if _is_empty(level_map, row, col - 1):
                _draw_c64_teeth_left(overlay, px, py, rng)
            # Cara derecha expuesta
            if _is_empty(level_map, row, col + 1):
                _draw_c64_teeth_right(overlay, px, py, rng)

    return overlay


def _draw_c64_teeth_top(overlay, px, py, rng):
    """Dientes negros irregulares en el borde superior del tile."""
    ts = TILE_SIZE
    # Línea base negra en el borde (1-2px)
    for lx in range(ts):
        if rng.random() < OVERLAY_TEETH_BASE_GAP:
            continue
        overlay.set_at((px + lx, py), _BLACK)
        if rng.random() < OVERLAY_TEETH_BASE_EXTRA:
            overlay.set_at((px + lx, py + 1), _BLACK)
    # Dientes triangulares que se meten en el tile
    num = rng.randint(*OVERLAY_TEETH_COUNT)
    for _ in range(num):
        tx = rng.randint(0, ts - 1)
        tw = rng.randint(*OVERLAY_TEETH_W)
        td = rng.randint(*OVERLAY_TEETH_DEPTH)
        for dy in range(td):
            # Se angosta con la profundidad (forma triangular)
            shrink = dy * tw // (td + 1)
            for dx in range(max(1, tw - shrink)):
                bx = px + tx + dx
                by = py + dy
                if px <= bx < px + ts and py <= by < py + ts:
                    overlay.set_at((bx, by), _BLACK)


def _draw_c64_teeth_bottom(overlay, px, py, rng):
    """Dientes negros irregulares en el borde inferior del tile."""
    ts = TILE_SIZE
    for lx in range(ts):
        if rng.random() < OVERLAY_TEETH_BASE_GAP:
            continue
        overlay.set_at((px + lx, py + ts - 1), _BLACK)
        if rng.random() < OVERLAY_TEETH_BASE_EXTRA:
            overlay.set_at((px + lx, py + ts - 2), _BLACK)
    num = rng.randint(*OVERLAY_TEETH_COUNT)
    for _ in range(num):
        tx = rng.randint(0, ts - 1)
        tw = rng.randint(*OVERLAY_TEETH_W)
        td = rng.randint(*OVERLAY_TEETH_DEPTH)
        for dy in range(td):
            shrink = dy * tw // (td + 1)
            for dx in range(max(1, tw - shrink)):
                bx = px + tx + dx
                by = py + ts - 1 - dy
                if px <= bx < px + ts and py <= by < py + ts:
                    overlay.set_at((bx, by), _BLACK)


def _draw_c64_teeth_left(overlay, px, py, rng):
    """Dientes negros irregulares en el borde izquierdo del tile."""
    ts = TILE_SIZE
    for ly in range(ts):
        if rng.random() < OVERLAY_TEETH_BASE_GAP:
            continue
        overlay.set_at((px, py + ly), _BLACK)
        if rng.random() < OVERLAY_TEETH_BASE_EXTRA:
            overlay.set_at((px + 1, py + ly), _BLACK)
    num = rng.randint(*OVERLAY_TEETH_COUNT)
    for _ in range(num):
        ty = rng.randint(0, ts - 1)
        th = rng.randint(*OVERLAY_TEETH_W)
        td = rng.randint(*OVERLAY_TEETH_DEPTH)
        for dx in range(td):
            shrink = dx * th // (td + 1)
            for dy in range(max(1, th - shrink)):
                bx = px + dx
                by = py + ty + dy
                if px <= bx < px + ts and py <= by < py + ts:
                    overlay.set_at((bx, by), _BLACK)


def _draw_c64_teeth_right(overlay, px, py, rng):
    """Dientes negros irregulares en el borde derecho del tile."""
    ts = TILE_SIZE
    for ly in range(ts):
        if rng.random() < OVERLAY_TEETH_BASE_GAP:
            continue
        overlay.set_at((px + ts - 1, py + ly), _BLACK)
        if rng.random() < OVERLAY_TEETH_BASE_EXTRA:
            overlay.set_at((px + ts - 2, py + ly), _BLACK)
    num = rng.randint(*OVERLAY_TEETH_COUNT)
    for _ in range(num):
        ty = rng.randint(0, ts - 1)
        th = rng.randint(*OVERLAY_TEETH_W)
        td = rng.randint(*OVERLAY_TEETH_DEPTH)
        for dx in range(td):
            shrink = dx * th // (td + 1)
            for dy in range(max(1, th - shrink)):
                bx = px + ts - 1 - dx
                by = py + ty + dy
                if px <= bx < px + ts and py <= by < py + ts:
                    overlay.set_at((bx, by), _BLACK)
