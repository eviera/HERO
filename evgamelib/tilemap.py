# evgamelib - Sistema de tile maps

import json
import os


class TileMap:
    """Mapa de tiles basado en grid de caracteres con bandas de viewport de ancho variable."""

    def __init__(self, grid, tile_size=32, viewport_cols=16, viewport_rows=8):
        self.grid = grid  # lista de strings
        self.tile_size = tile_size
        self.viewport_cols = viewport_cols
        self.viewport_rows = viewport_rows

    @property
    def height(self):
        """Alto del mapa en tiles."""
        return len(self.grid)

    @property
    def width(self):
        """Ancho maximo del mapa en tiles."""
        return self.max_width()

    def row_width(self, tile_row):
        """Ancho en tiles de una fila especifica."""
        if not self.grid or tile_row < 0 or tile_row >= len(self.grid):
            return 0
        return len(self.grid[tile_row])

    def band_width(self, tile_row):
        """Ancho en tiles de la banda de viewport que contiene tile_row."""
        if not self.grid:
            return self.viewport_cols
        if tile_row < 0:
            return len(self.grid[0])
        band_start = (tile_row // self.viewport_rows) * self.viewport_rows
        if band_start < len(self.grid):
            return len(self.grid[band_start])
        return self.viewport_cols

    def max_width(self):
        """Ancho maximo entre todas las filas del mapa."""
        return max(len(row) for row in self.grid) if self.grid else 0

    def tile_at(self, row, col):
        """Retorna el caracter en (row, col), o ' ' si fuera de rango."""
        if 0 <= row < len(self.grid) and 0 <= col < len(self.grid[row]):
            return self.grid[row][col]
        return ' '

    def set_tile(self, row, col, char):
        """Establece el caracter en (row, col). Convierte la fila a lista mutable si es necesario."""
        if 0 <= row < len(self.grid) and 0 <= col < len(self.grid[row]):
            row_list = list(self.grid[row])
            row_list[col] = char
            self.grid[row] = ''.join(row_list)

    def is_solid(self, row, col, solid_tiles):
        """Verifica si el tile en (row, col) es solido."""
        return self.tile_at(row, col) in solid_tiles

    def find_tile(self, char):
        """Encuentra la primera ocurrencia de un caracter. Retorna (row, col) o None."""
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                if tile == char:
                    return (row_idx, col_idx)
        return None

    def find_all_tiles(self, char):
        """Genera todas las ocurrencias de un caracter como (row, col)."""
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                if tile == char:
                    yield (row_idx, col_idx)

    @staticmethod
    def load_maps_from_json(filepath, viewport_cols=16, viewport_rows=8, tile_size=32):
        """Carga lista de TileMaps desde un archivo screens.json."""
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                screens = json.load(f)
        except Exception:
            return []

        tilemaps = []
        for s in screens:
            level_map = s.get("map", [])
            # Normalizar altura a multiplo de viewport_rows
            map_height = len(level_map)
            target_h = max(viewport_rows, ((map_height + viewport_rows - 1) // viewport_rows) * viewport_rows)
            while len(level_map) < target_h:
                level_map.append('#' * viewport_cols)

            # Normalizar ancho por banda
            for band_start in range(0, len(level_map), viewport_rows):
                band_rows = level_map[band_start:band_start + viewport_rows]
                if band_rows:
                    max_w = max(len(r) for r in band_rows)
                    target_w = max(viewport_cols, ((max_w + viewport_cols - 1) // viewport_cols) * viewport_cols)
                    for i in range(band_start, min(band_start + viewport_rows, len(level_map))):
                        if len(level_map[i]) < target_w:
                            level_map[i] = level_map[i] + '#' * (target_w - len(level_map[i]))

            tilemaps.append(TileMap(level_map, tile_size, viewport_cols, viewport_rows))
        return tilemaps


# Funciones standalone de compatibilidad (para codigo que usa funciones sueltas)

def band_width(level_map, tile_row, viewport_cols=16, viewport_rows=8):
    """Ancho en tiles de la banda de viewport que contiene tile_row."""
    if not level_map:
        return viewport_cols
    if tile_row < 0:
        return len(level_map[0])
    band_start = (tile_row // viewport_rows) * viewport_rows
    if band_start < len(level_map):
        return len(level_map[band_start])
    return viewport_cols

def row_width(level_map, tile_row):
    """Ancho en tiles de una fila especifica."""
    if not level_map or tile_row < 0 or tile_row >= len(level_map):
        return 0
    return len(level_map[tile_row])

def max_level_width(level_map):
    """Ancho maximo entre todas las filas del mapa."""
    return max(len(row) for row in level_map) if level_map else 0
