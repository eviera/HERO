# H.E.R.O. Remake - Sistema de paleta por profundidad
# Módulo compartido entre hero.py y editor.py
# Tintea tiles según la fila dentro de cada viewport (profundidad en la mina)
# La paleta se repite idéntica en cada viewport del nivel

import pygame
from constants import VIEWPORT_ROWS, TILE_SIZE

# Tiles sólidos (para detección de bordes)
SOLID_TILES = {'#', '.', 'G', 'R'}

# Grosor del borde decorativo en píxeles
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
    """Dibujar bordes decorativos en las caras de un tile sólido
    que están expuestas al vacío (adyacente a tile no-sólido).
    x, y son las coordenadas en píxeles en la superficie destino."""
    t = EDGE_THICKNESS
    color = tuple(edge_color)

    # Cara superior: si el vecino de arriba no es sólido
    if not _is_solid(level_map, row - 1, col):
        pygame.draw.rect(surface, color, (x, y, TILE_SIZE, t))

    # Cara inferior: si el vecino de abajo no es sólido
    if not _is_solid(level_map, row + 1, col):
        pygame.draw.rect(surface, color, (x, y + TILE_SIZE - t, TILE_SIZE, t))

    # Cara izquierda: si el vecino izquierdo no es sólido
    if not _is_solid(level_map, row, col - 1):
        pygame.draw.rect(surface, color, (x, y, t, TILE_SIZE))

    # Cara derecha: si el vecino derecho no es sólido
    if not _is_solid(level_map, row, col + 1):
        pygame.draw.rect(surface, color, (x + TILE_SIZE - t, y, t, TILE_SIZE))
