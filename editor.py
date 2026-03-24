# H.E.R.O. Level Editor
# Editor de pantallas para el juego H.E.R.O.
# Soporta niveles de tamaño dinámico (múltiplos del viewport 8x16)

import pygame
import json
import os
import random
from constants import *
import palette as palette_module
from palette import (get_depth_palette, get_edge_color, build_tinted_floors,
                     draw_tile_edges, DEFAULT_EDGE_COLOR, NEUTRAL_TINT,
                     generate_floor_texture, generate_edge_overlay)

# TILE_TYPES importado desde constants.py

def load_screens():
    """Cargar pantallas desde archivo JSON"""
    if os.path.exists(SCREENS_FILE):
        try:
            with open(SCREENS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando screens: {e}")
    return []

def save_screens(screens):
    """Guardar pantallas a archivo JSON"""
    try:
        with open(SCREENS_FILE, 'w', encoding='utf-8') as f:
            json.dump(screens, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error guardando screens: {e}")
        return False

def normalize_map(level_map):
    """Normalizar mapa por banda de viewport (cada banda tiene su propio ancho)"""
    if not level_map:
        return ['#' * VIEWPORT_COLS] * VIEWPORT_ROWS

    map_height = len(level_map)

    # Normalizar altura total a múltiplo de VIEWPORT_ROWS
    target_h = max(VIEWPORT_ROWS, ((map_height + VIEWPORT_ROWS - 1) // VIEWPORT_ROWS) * VIEWPORT_ROWS)
    while len(level_map) < target_h:
        level_map.append('#' * VIEWPORT_COLS)

    # Normalizar por banda: cada grupo de VIEWPORT_ROWS filas tiene su propio ancho
    result = []
    for band_start in range(0, target_h, VIEWPORT_ROWS):
        band_end = min(band_start + VIEWPORT_ROWS, len(level_map))
        band_rows = level_map[band_start:band_end]
        band_w = max(len(r) for r in band_rows) if band_rows else VIEWPORT_COLS
        target_band_w = max(VIEWPORT_COLS, ((band_w + VIEWPORT_COLS - 1) // VIEWPORT_COLS) * VIEWPORT_COLS)
        for row in band_rows:
            if len(row) < target_band_w:
                row = row + '#' * (target_band_w - len(row))
            result.append(row[:target_band_w])
        # Completar filas faltantes de la banda
        while len(result) < band_start + VIEWPORT_ROWS:
            result.append('#' * target_band_w)
    return result[:target_h]

def get_map_dims(level_map):
    """Obtener dimensiones del mapa en tiles (ancho = máximo entre filas)"""
    h = len(level_map) if level_map else VIEWPORT_ROWS
    w = max(len(row) for row in level_map) if level_map else VIEWPORT_COLS
    return w, h

class Editor:
    def __init__(self):
        pygame.init()
        # El editor usa dimensiones de juego sin escalar
        editor_w = GAME_WIDTH
        editor_viewport_h = GAME_VIEWPORT_HEIGHT
        editor_hud_h = 150
        self.editor_viewport_h = editor_viewport_h
        self.editor_h = editor_viewport_h + editor_hud_h
        self.editor_scale = 2
        self.screen = pygame.Surface((editor_w, self.editor_h))
        self.display = pygame.display.set_mode((editor_w * self.editor_scale, self.editor_h * self.editor_scale))
        pygame.display.set_caption("H.E.R.O. Level Editor")
        self.clock = pygame.time.Clock()

        # Fuentes
        try:
            self.font = pygame.font.Font("fonts/PressStart2P-vaV7.ttf", 10)
            self.small_font = pygame.font.Font("fonts/PressStart2P-vaV7.ttf", 8)
        except:
            self.font = pygame.font.Font(None, 16)
            self.small_font = pygame.font.Font(None, 12)

        # Cargar tiles (mismos que el juego)
        self.tiles = {}
        try:
            self.tiles['wall'] = pygame.image.load("tiles/wall.png").convert_alpha()
            self.tiles['floor'] = pygame.image.load("tiles/floor.png").convert_alpha()
            self.tiles['blank'] = pygame.image.load("tiles/blank.png").convert_alpha()
        except:
            self.tiles['wall'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['wall'].fill(COLOR_GRAY)
            self.tiles['floor'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['floor'].fill((100, 70, 50))
            self.tiles['blank'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['blank'].fill(COLOR_BLACK)

        # Granito (indestructible)
        try:
            self.tiles['granite'] = pygame.image.load("tiles/granite.png").convert_alpha()
        except:
            self.tiles['granite'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['granite'].fill((60, 60, 65))

        # Pared rompible
        try:
            self.tiles['rock'] = pygame.image.load("tiles/breakable_wall.png").convert_alpha()
        except:
            self.tiles['rock'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['rock'].fill((180, 170, 160))

        # Lampara
        try:
            self.tiles['lamp'] = pygame.image.load("tiles/lamp.png").convert_alpha()
        except:
            self.tiles['lamp'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['lamp'].fill((255, 200, 50))

        # Agua tóxica
        try:
            self.tiles['toxic_water'] = pygame.image.load("tiles/toxic_water.png").convert_alpha()
        except:
            self.tiles['toxic_water'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['toxic_water'].fill((30, 120, 40))

        # Lava (indestructible, mata al contacto)
        try:
            self.tiles['lava'] = pygame.image.load("tiles/lava.png").convert_alpha()
        except:
            self.tiles['lava'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['lava'].fill((200, 80, 30))

        # Roca lava (destructible)
        try:
            self.tiles['lava_rock'] = pygame.image.load("tiles/lava_breakable_wall.png").convert_alpha()
        except:
            self.tiles['lava_rock'] = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.tiles['lava_rock'].fill((180, 100, 40))

        # Cargar sprites de entidades
        self.sprites = {}
        try:
            self.sprites['player'] = pygame.image.load("sprites/player.png").convert_alpha()
            self.sprites['enemy'] = pygame.image.load("sprites/bat1.png").convert_alpha()
            self.sprites['spider'] = pygame.image.load("sprites/spider.png").convert_alpha()
            self.sprites['bug'] = pygame.image.load("sprites/bug1.png").convert_alpha()
            self.sprites['miner'] = pygame.image.load("sprites/miner.png").convert_alpha()
            self.sprites['snake_head'] = pygame.image.load("sprites/snake_head.png").convert_alpha()
        except Exception as e:
            print(f"Error cargando sprites: {e}")


        # Estado del editor
        self.screens = load_screens()
        self.current_level = 0
        self.cursor_row = 0
        self.cursor_col = 0
        self.selected_tile = 1  # Pared por defecto
        self.camera_x = 0
        self.camera_y = 0
        self.target_camera_x = 0
        self.target_camera_y = 0
        self.camera_animating = False
        self.saved_indicator = 0  # Timer para mensaje "Guardado!"
        self.confirm_shrink = None  # Pendiente de confirmacion: 'cols' o 'rows'

        # Modo textura (F3)
        self.texture_mode = False
        self.tex_params = {}           # Parámetros editables actuales
        self.tex_defaults = {}         # Valores por defecto
        self.tex_groups = []           # Grupos de parámetros
        self.tex_sel_group = 0         # Grupo seleccionado
        self.tex_sel_param = 0         # Parámetro dentro del grupo
        self.tex_dirty = False         # Cambios sin guardar
        self.tex_regen_timer = 0       # Debounce para regenerar previews
        self.tex_preview_left = None   # Surface preview izquierdo (suelo compacto)
        self.tex_preview_right = None  # Surface preview derecho (suelo + aire)
        self.tex_seed = 42             # Seed para reproducibilidad
        self._init_texture_editor()

        # Modo paleta
        self.palette_mode = False
        self.palette_editing = 0       # 0=Color1, 1=Color2, 2=Edge
        self.palette_channel = 0       # 0=R, 1=G, 2=B
        self._tinted_floors_cache = None
        self._tinted_floors_level = -1

        # Normalizar todas las pantallas cargadas
        for screen in self.screens:
            screen["map"] = normalize_map(screen["map"])

        if not self.screens:
            self.new_level()

    def new_level(self):
        """Crear un nivel vacío con bordes de pared (1x3 viewports por defecto)"""
        w = VIEWPORT_COLS
        h = VIEWPORT_ROWS * 3  # 24 filas por defecto
        empty_map = []
        for r in range(h):
            if r == 0 or r == h - 1:
                empty_map.append('#' * w)
            else:
                empty_map.append('#' + ' ' * (w - 2) + '#')
        self.screens.append({
            "name": f"Level {len(self.screens) + 1}",
            "map": empty_map
        })
        self.current_level = len(self.screens) - 1
        self.cursor_row = 1
        self.cursor_col = 1
        self.camera_x = 0
        self.camera_y = 0
        self.target_camera_x = 0
        self.target_camera_y = 0
        self.camera_animating = False

    def get_current_map(self):
        return self.screens[self.current_level]["map"]

    def get_current_palette(self):
        """Obtener paleta de profundidad del nivel actual"""
        return self.screens[self.current_level].get("depth_palette", [])

    def get_current_edge_color(self):
        """Obtener color de borde del nivel actual"""
        return self.screens[self.current_level].get("edge_color", list(DEFAULT_EDGE_COLOR))

    def _ensure_palette_entry(self, entry_index):
        """Asegurar que depth_palette tenga entrada para el índice dado"""
        screen = self.screens[self.current_level]
        if "depth_palette" not in screen:
            screen["depth_palette"] = []
        palette = screen["depth_palette"]
        while len(palette) <= entry_index:
            palette.append({"wall": list(NEUTRAL_TINT)})
        return palette[entry_index]

    def _get_editing_color(self):
        """Obtener la lista de color que se está editando (mutable, para modificar in-place)"""
        screen = self.screens[self.current_level]
        if self.palette_editing == 2:
            # Edge color
            if "edge_color" not in screen:
                screen["edge_color"] = list(DEFAULT_EDGE_COLOR)
            return screen["edge_color"]
        else:
            # Color1 (idx 0) o Color2 (idx 1)
            entry = self._ensure_palette_entry(self.palette_editing)
            return entry.get("wall", None) or entry.setdefault("wall", list(NEUTRAL_TINT))

    def get_tinted_floors(self):
        """Obtener tiles de suelo tintados con caché"""
        if self._tinted_floors_cache is not None and self._tinted_floors_level == self.current_level:
            return self._tinted_floors_cache
        palette = self.get_current_palette()
        self._tinted_floors_cache = build_tinted_floors(self.tiles['floor'], palette)
        self._tinted_floors_level = self.current_level
        return self._tinted_floors_cache

    def invalidate_tinted_cache(self):
        """Forzar reconstrucción de tiles tintados"""
        self._tinted_floors_cache = None

    def get_level_dims(self):
        """Dimensiones del nivel actual en tiles"""
        return get_map_dims(self.get_current_map())

    def get_viewport_grid(self):
        """Lista de viewport-cols por cada banda de viewport-rows"""
        level_map = self.get_current_map()
        h = len(level_map) if level_map else VIEWPORT_ROWS
        num_bands = h // VIEWPORT_ROWS
        band_vp_cols = []
        for band in range(num_bands):
            band_start = band * VIEWPORT_ROWS
            w = len(level_map[band_start]) if band_start < len(level_map) else VIEWPORT_COLS
            band_vp_cols.append(w // VIEWPORT_COLS)
        return band_vp_cols


    def _clamp_cursor_col(self):
        """Clampear cursor_col al ancho de la banda actual"""
        level_map = self.get_current_map()
        band_start = (self.cursor_row // VIEWPORT_ROWS) * VIEWPORT_ROWS
        band_w = len(level_map[band_start]) if band_start < len(level_map) else VIEWPORT_COLS
        self.cursor_col = max(0, min(band_w - 1, self.cursor_col))

    def set_tile(self, row, col, char):
        """Colocar un tile en la posicion dada"""
        level_map = self.get_current_map()
        if 0 <= row < len(level_map) and 0 <= col < len(level_map[row]):
            row_str = level_map[row]
            level_map[row] = row_str[:col] + char + row_str[col + 1:]

    def add_viewport_cols(self):
        """Agregar un viewport (VIEWPORT_COLS columnas) a la derecha de la banda actual"""
        level_map = self.get_current_map()
        band_start = (self.cursor_row // VIEWPORT_ROWS) * VIEWPORT_ROWS
        band_end = min(band_start + VIEWPORT_ROWS, len(level_map))
        extra = ' ' * VIEWPORT_COLS
        for i in range(band_start, band_end):
            level_map[i] = level_map[i] + extra
        self.invalidate_tinted_cache()

    def remove_viewport_col_at(self, vx):
        """Quitar la columna de viewports en el indice vx (solo banda actual)"""
        level_map = self.get_current_map()
        band_start = (self.cursor_row // VIEWPORT_ROWS) * VIEWPORT_ROWS
        band_end = min(band_start + VIEWPORT_ROWS, len(level_map))
        band_w = len(level_map[band_start]) if band_start < len(level_map) else VIEWPORT_COLS
        if band_w <= VIEWPORT_COLS:
            return False

        start_c = vx * VIEWPORT_COLS
        end_c = start_c + VIEWPORT_COLS
        if end_c > band_w:
            return False

        for i in range(band_start, band_end):
            level_map[i] = level_map[i][:start_c] + level_map[i][end_c:]

        new_band_w = band_w - VIEWPORT_COLS
        # Ajustar cursor y cámara si quedan fuera
        if self.cursor_col >= new_band_w:
            self.cursor_col = new_band_w - 1
        elif self.cursor_col >= start_c and self.cursor_col < end_c:
            self.cursor_col = max(0, start_c - 1)
        elif self.cursor_col >= end_c:
            self.cursor_col -= VIEWPORT_COLS
        max_cam_x = max(0, (new_band_w - VIEWPORT_COLS) * TILE_SIZE)
        if self.camera_x > max_cam_x:
            self.camera_x = max_cam_x
            self.target_camera_x = max_cam_x
        return True

    def add_viewport_rows(self):
        """Agregar un viewport (VIEWPORT_ROWS filas) abajo"""
        level_map = self.get_current_map()
        # Usar ancho de la última banda existente como default
        last_band_start = max(0, len(level_map) - VIEWPORT_ROWS)
        w = len(level_map[last_band_start]) if level_map else VIEWPORT_COLS
        for _ in range(VIEWPORT_ROWS):
            level_map.append(' ' * w)
        self.invalidate_tinted_cache()

    def remove_viewport_row_at(self, vy):
        """Quitar la fila de viewports en el indice vy"""
        level_map = self.get_current_map()
        _, h = self.get_level_dims()
        if h <= VIEWPORT_ROWS:
            return False

        start_r = vy * VIEWPORT_ROWS
        end_r = start_r + VIEWPORT_ROWS
        del level_map[start_r:end_r]

        new_h = h - VIEWPORT_ROWS
        # Ajustar cursor y cámara si quedan fuera
        if self.cursor_row >= new_h:
            self.cursor_row = new_h - 1
        elif self.cursor_row >= start_r and self.cursor_row < end_r:
            self.cursor_row = max(0, start_r - 1)
        elif self.cursor_row >= end_r:
            self.cursor_row -= VIEWPORT_ROWS
        max_cam_y = (new_h - VIEWPORT_ROWS) * TILE_SIZE
        if self.camera_y > max_cam_y:
            self.camera_y = max_cam_y
            self.target_camera_y = max_cam_y
        return True

    def _has_content_in_region(self, start_row, end_row, start_col, end_col):
        """Verifica si hay contenido no-pared en una region del mapa"""
        level_map = self.get_current_map()
        for r in range(start_row, min(end_row, len(level_map))):
            for c in range(start_col, min(end_col, len(level_map[r]))):
                if level_map[r][c] not in ('#', ' '):
                    return True
        return False

    def update_camera(self):
        """Cámara fija por bloques de viewport en ambos ejes (ancho por banda)"""
        level_map = self.get_current_map()
        _, h = self.get_level_dims()

        # Ancho de la banda actual del cursor
        band_start = (self.cursor_row // VIEWPORT_ROWS) * VIEWPORT_ROWS
        band_w = len(level_map[band_start]) if band_start < len(level_map) else VIEWPORT_COLS

        # Bloque horizontal
        block_x = VIEWPORT_COLS * TILE_SIZE
        max_cam_x = max(0, (band_w - VIEWPORT_COLS) * TILE_SIZE)
        cursor_block_x = self.cursor_col // VIEWPORT_COLS
        target_x = min(max_cam_x, cursor_block_x * block_x)

        # Bloque vertical
        block_y = VIEWPORT_ROWS * TILE_SIZE
        max_cam_y = max(0, (h - VIEWPORT_ROWS) * TILE_SIZE)
        cursor_block_y = self.cursor_row // VIEWPORT_ROWS
        target_y = min(max_cam_y, cursor_block_y * block_y)

        if abs(self.target_camera_x - target_x) > 0 or abs(self.target_camera_y - target_y) > 0:
            self.target_camera_x = target_x
            self.target_camera_y = target_y
            if abs(self.camera_x - target_x) > 1 or abs(self.camera_y - target_y) > 1:
                self.camera_animating = True

    def render_grid(self):
        """Renderizar la cuadricula del nivel"""
        level_map = self.get_current_map()
        w, h = self.get_level_dims()
        vh = self.editor_viewport_h
        cam_x = self.camera_x
        cam_y = self.camera_y
        palette = self.get_current_palette()
        edge_color = self.get_current_edge_color()
        tinted_floors = self.get_tinted_floors()

        start_row = max(0, int(cam_y / TILE_SIZE) - 1)
        end_row = min(h, int((cam_y + vh) / TILE_SIZE) + 2)
        start_col = max(0, int(cam_x / TILE_SIZE) - 1)
        end_col = min(w, int((cam_x + GAME_WIDTH) / TILE_SIZE) + 2)

        for row_index in range(start_row, end_row):
            if row_index >= len(level_map):
                break
            row = level_map[row_index]
            local_row = row_index % VIEWPORT_ROWS
            for col_index in range(start_col, end_col):
                if col_index >= len(row):
                    # Espacio fuera de la banda: mostrar como pared
                    x = col_index * TILE_SIZE - cam_x
                    y = row_index * TILE_SIZE - cam_y
                    self.screen.blit(self.tiles['wall'], (int(x), int(y)))
                    # Marcar con X que es fuera de banda
                    pygame.draw.line(self.screen, (80, 30, 30),
                                     (int(x), int(y)), (int(x + TILE_SIZE), int(y + TILE_SIZE)), 1)
                    pygame.draw.line(self.screen, (80, 30, 30),
                                     (int(x + TILE_SIZE), int(y)), (int(x), int(y + TILE_SIZE)), 1)
                    pygame.draw.rect(self.screen, (40, 40, 40),
                                     (int(x), int(y), TILE_SIZE, TILE_SIZE), 1)
                    continue
                tile = row[col_index]
                x = col_index * TILE_SIZE - cam_x
                y = row_index * TILE_SIZE - cam_y

                # Dibujar fondo del tile
                if tile == '#':
                    self.screen.blit(self.tiles['wall'], (int(x), int(y)))
                elif tile == '.':
                    self.screen.blit(tinted_floors[local_row], (int(x), int(y)))
                    # Bordes decorativos
                    draw_tile_edges(self.screen, int(x), int(y), row_index, col_index, level_map, edge_color)
                elif tile == 'G':
                    self.screen.blit(self.tiles['granite'], (int(x), int(y)))
                elif tile == 'R':
                    self.screen.blit(self.tiles['rock'], (int(x), int(y)))
                elif tile == 'L':
                    self.screen.blit(self.tiles['blank'], (int(x), int(y)))
                    self.screen.blit(self.tiles['lamp'], (int(x), int(y)))
                elif tile == '~':
                    self.screen.blit(self.tiles['toxic_water'], (int(x), int(y)))
                elif tile == 'X':
                    self.screen.blit(self.tiles['lava'], (int(x), int(y)))
                elif tile == 'W':
                    self.screen.blit(self.tiles['lava_rock'], (int(x), int(y)))
                else:
                    self.screen.blit(self.tiles['blank'], (int(x), int(y)))

                # Dibujar sprites de entidades encima
                sprite_map = {'S': 'player', 'V': 'enemy', 'A': 'spider', 'B': 'bug', 'M': 'miner'}
                if tile in ('<', '>'):
                    # Víbora: cabeza asomando por detrás de la pared
                    if 'snake_head' in self.sprites:
                        head = self.sprites['snake_head']
                        if tile == '>':
                            head = pygame.transform.flip(head, True, False)
                        peek = 14  # cuánto asoma
                        if tile == '<':
                            self.screen.blit(head, (int(x) - peek, int(y)))
                        else:
                            self.screen.blit(head, (int(x) + TILE_SIZE + peek - TILE_SIZE, int(y)))
                    # Pared encima tapando la parte interna
                    self.screen.blit(self.tiles['wall'], (int(x), int(y)))
                elif tile in sprite_map and sprite_map[tile] in self.sprites:
                    self.screen.blit(self.sprites[sprite_map[tile]], (int(x), int(y)))
                elif tile in sprite_map:
                    # Fallback: dibujar letra con color
                    colors = {'S': COLOR_BLUE, 'V': COLOR_RED, 'A': COLOR_ORANGE, 'B': COLOR_GREEN, 'M': COLOR_GREEN}
                    letter = self.font.render(tile, True, colors[tile])
                    lx = int(x) + (TILE_SIZE - letter.get_width()) // 2
                    ly = int(y) + (TILE_SIZE - letter.get_height()) // 2
                    self.screen.blit(letter, (lx, ly))

                # Lineas de cuadricula
                pygame.draw.rect(self.screen, (40, 40, 40),
                                 (int(x), int(y), TILE_SIZE, TILE_SIZE), 1)

        # Separadores de viewport (lineas mas visibles entre bloques)
        # Verticales: por banda, cada una con su propio ancho
        band_cols = self.get_viewport_grid()
        for band_idx, num_vp_cols in enumerate(band_cols):
            band_top = band_idx * VIEWPORT_ROWS * TILE_SIZE - cam_y
            band_bottom = (band_idx + 1) * VIEWPORT_ROWS * TILE_SIZE - cam_y
            for vx in range(1, num_vp_cols):
                px = vx * VIEWPORT_COLS * TILE_SIZE - cam_x
                if 0 <= px <= GAME_WIDTH:
                    top_y = max(0, int(band_top))
                    bot_y = min(vh, int(band_bottom))
                    if top_y < bot_y:
                        pygame.draw.line(self.screen, (80, 80, 120),
                                         (int(px), top_y), (int(px), bot_y), 2)
        # Horizontales
        for vy in range(1, len(band_cols)):
            py = vy * VIEWPORT_ROWS * TILE_SIZE - cam_y
            if 0 <= py <= vh:
                pygame.draw.line(self.screen, (80, 80, 120),
                                 (0, int(py)), (GAME_WIDTH, int(py)), 2)

        # Dibujar cursor
        cx = self.cursor_col * TILE_SIZE - cam_x
        cy = self.cursor_row * TILE_SIZE - cam_y
        pygame.draw.rect(self.screen, COLOR_YELLOW,
                         (int(cx), int(cy), TILE_SIZE, TILE_SIZE), 3)

    def render_minimap(self, mx, my, max_w, max_h):
        """Renderizar minimapa jagged en la posicion dada"""
        band_cols = self.get_viewport_grid()  # lista de vp_cols por banda
        num_bands = len(band_cols)
        if num_bands == 0:
            return

        max_vp_cols = max(band_cols) if band_cols else 1

        # Escala para que quepa en el espacio disponible
        cell_w = min(max_w // max_vp_cols, 16)
        cell_h = min(max_h // num_bands, 12)
        cell_w = max(cell_w, 6)
        cell_h = max(cell_h, 6)

        total_w = max_vp_cols * cell_w
        total_h = num_bands * cell_h

        # Viewport actual (basado en la cámara)
        cur_vx = int(self.camera_x) // (VIEWPORT_COLS * TILE_SIZE)
        cur_vy = int(self.camera_y) // (VIEWPORT_ROWS * TILE_SIZE)

        # Fondo del minimapa
        pygame.draw.rect(self.screen, (15, 15, 30),
                         (mx - 1, my - 1, total_w + 2, total_h + 2))

        for vy in range(num_bands):
            for vx in range(band_cols[vy]):
                rx = mx + vx * cell_w
                ry = my + vy * cell_h

                # Color de fondo: gris oscuro o highlight para viewport actual
                if vx == cur_vx and vy == cur_vy:
                    color = (60, 60, 120)
                    border = COLOR_YELLOW
                else:
                    color = (30, 30, 50)
                    border = (50, 50, 70)

                pygame.draw.rect(self.screen, color,
                                 (rx, ry, cell_w - 1, cell_h - 1))
                pygame.draw.rect(self.screen, border,
                                 (rx, ry, cell_w - 1, cell_h - 1), 1)

        # Etiqueta de dimensiones debajo (forma jagged)
        cols_str = ",".join(str(c) for c in band_cols)
        dim_text = self.small_font.render(f"{cols_str}x{num_bands}", True, COLOR_GRAY)
        self.screen.blit(dim_text, (mx, my + total_h + 2))

    def render_hud(self):
        """Renderizar barra de estado inferior"""
        hud_y = self.editor_viewport_h
        hud_bg = pygame.Surface((GAME_WIDTH, self.editor_h - self.editor_viewport_h))
        hud_bg.fill((20, 20, 50))
        self.screen.blit(hud_bg, (0, hud_y))

        w, h = self.get_level_dims()
        band_cols = self.get_viewport_grid()
        num_bands = len(band_cols)

        # --- Zona de texto (arriba) ---
        # Linea 1: Nivel + dimensiones (forma jagged)
        cols_str = ",".join(str(c) for c in band_cols)
        level_text = self.font.render(
            f"Nivel {self.current_level + 1}/{len(self.screens)}  ({cols_str}x{num_bands}vp)",
            True, COLOR_WHITE
        )
        self.screen.blit(level_text, (8, hud_y + 4))

        # Linea 2: Posicion del cursor + tile actual
        current_map = self.get_current_map()
        row_data = current_map[self.cursor_row] if self.cursor_row < len(current_map) else ''
        cursor_char = row_data[self.cursor_col] if self.cursor_col < len(row_data) else '#'
        cursor_name = next((n for c, n, *_ in TILE_TYPES if c == cursor_char), '?')

        # Viewport actual del cursor
        cur_vx = self.cursor_col // VIEWPORT_COLS + 1
        cur_vy = self.cursor_row // VIEWPORT_ROWS + 1

        pos_str = f"F:{self.cursor_row:02d} C:{self.cursor_col:02d} VP:{cur_vx},{cur_vy}  "
        pos_text = self.font.render(pos_str, True, COLOR_WHITE)
        self.screen.blit(pos_text, (8, hud_y + 18))
        tile_cursor_text = self.font.render(f"[{cursor_char}]{cursor_name}", True, (0, 255, 0))
        self.screen.blit(tile_cursor_text, (8 + pos_text.get_width(), hud_y + 18))

        # --- Minimapa (esquina superior derecha del HUD) ---
        minimap_x = GAME_WIDTH - 100
        minimap_y = hud_y + 4
        self.render_minimap(minimap_x, minimap_y, 90, 36)

        # Tile seleccionado (debajo del separador)
        char, name, color, _score, _solid = TILE_TYPES[self.selected_tile]
        tile_text = self.font.render(f"[{char}] {name}", True, COLOR_YELLOW)
        self.screen.blit(tile_text, (8, hud_y + 32))

        # --- Zona de paleta (abajo) ---
        KEY_LABELS = "123456789" + "FGHJKLZ"
        tiles_per_row = 8
        tile_spacing = 38
        preview_size = 20
        row_height = 32

        # Centrar paleta horizontalmente
        total_row_width = tiles_per_row * tile_spacing - (tile_spacing - preview_size)
        palette_x = (GAME_WIDTH - total_row_width) // 2
        palette_y = hud_y + 52

        for i, (tc, tn, tcolor, _tscore, _tsolid) in enumerate(TILE_TYPES):
            row = i // tiles_per_row
            col = i % tiles_per_row
            px = palette_x + col * tile_spacing
            py = palette_y + row * row_height

            # Preview cuadrado
            ps = preview_size
            sprite_for_tile = {
                'S': 'player', 'V': 'enemy', 'A': 'spider', 'B': 'bug', 'M': 'miner'
            }
            tile_for_tile = {
                '#': 'wall', '.': 'floor', 'G': 'granite', 'R': 'rock',
                'L': 'lamp', '~': 'toxic_water', 'X': 'lava', 'W': 'lava_rock'
            }

            preview = pygame.Surface((ps, ps), pygame.SRCALPHA)
            if tc in ('<', '>'):
                # Víbora: solo la cabeza en la paleta
                preview.fill((30, 30, 30))
                if 'snake_head' in self.sprites:
                    head = self.sprites['snake_head']
                    if tc == '>':
                        head = pygame.transform.flip(head, True, False)
                    head_scaled = pygame.transform.scale(head, (ps, ps))
                    # Centrar: la cabeza izq tiene contenido a la izquierda,
                    # la derecha (flipeada) queda corrida, compensar
                    ox = -ps // 4 if tc == '>' else 0
                    preview.blit(head_scaled, (ox, 0))
            elif tc in tile_for_tile:
                preview = pygame.transform.scale(self.tiles[tile_for_tile[tc]], (ps, ps))
            elif tc in sprite_for_tile and sprite_for_tile[tc] in self.sprites:
                preview.fill((30, 30, 30))
                scaled = pygame.transform.scale(self.sprites[sprite_for_tile[tc]], (ps, ps))
                preview.blit(scaled, (0, 0))
            else:
                preview.fill(tcolor if tc != ' ' else (30, 30, 30))
                if tc not in (' ', '#', '.', 'G', 'R'):
                    l = self.small_font.render(tc, True, COLOR_WHITE)
                    lx = (ps - l.get_width()) // 2
                    ly = (ps - l.get_height()) // 2
                    preview.blit(l, (lx, ly))

            self.screen.blit(preview, (px, py))

            # Borde de seleccion
            if i == self.selected_tile:
                pygame.draw.rect(self.screen, COLOR_YELLOW,
                                 (px - 2, py - 2, preview_size + 4, preview_size + 4), 2)

            # Etiqueta de tecla debajo
            key_label = KEY_LABELS[i] if i < len(KEY_LABELS) else "?"
            num_color = COLOR_YELLOW if i == self.selected_tile else COLOR_GRAY
            num_text = self.small_font.render(key_label, True, num_color)
            label_x = px + (preview_size - num_text.get_width()) // 2
            self.screen.blit(num_text, (label_x, py + preview_size + 3))

        # --- Controles ---
        hint = self.small_font.render(
            "Spc:Poner ^S:Guardar PgUp/Dn:Nivel",
            True, COLOR_GRAY
        )
        self.screen.blit(hint, (8, hud_y + 120))
        hint2 = self.small_font.render(
            "Q/A:VP arriba/abajo Z/X:VP izq/der",
            True, COLOR_GRAY
        )
        self.screen.blit(hint2, (8, hud_y + 130))
        hint3 = self.small_font.render(
            "^Down/Right:+VP Del:-VP ^N:Nuevo ^Del:Borrar",
            True, COLOR_GRAY
        )
        self.screen.blit(hint3, (8, hud_y + 140))
        hint4 = self.small_font.render(
            "P:Paleta  F3:Texturas",
            True, COLOR_GRAY
        )
        self.screen.blit(hint4, (GAME_WIDTH - hint4.get_width() - 8, hud_y + 140))

        # Indicador de guardado
        if self.saved_indicator > 0:
            save_text = self.font.render("Guardado!", True, COLOR_GREEN)
            self.screen.blit(save_text, (GAME_WIDTH - save_text.get_width() - 8, self.editor_h - save_text.get_height() - 4))

        # Dialogo de confirmacion para quitar viewport
        if self.confirm_shrink:
            overlay = pygame.Surface((GAME_WIDTH, self.editor_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            shrink = self.confirm_shrink
            if shrink['type'] == 'both':
                msg = "Eliminar viewport: que eje?"
                hint = "C:Columna  F:Fila  Otro:Cancelar"
            elif shrink['type'] == 'cols':
                msg = f"Eliminar columna de viewports {shrink['col'] + 1}?"
                hint = "Y:Confirmar  Otro:Cancelar"
            else:
                msg = f"Eliminar fila de viewports {shrink['row'] + 1}?"
                hint = "Y:Confirmar  Otro:Cancelar"
            msg_text = self.font.render(msg, True, COLOR_YELLOW)
            msg_rect = msg_text.get_rect(center=(GAME_WIDTH // 2, self.editor_h // 2 - 20))
            self.screen.blit(msg_text, msg_rect)

            hint_text = self.small_font.render(hint, True, COLOR_RED)
            hint_rect = hint_text.get_rect(center=(GAME_WIDTH // 2, self.editor_h // 2 + 10))
            self.screen.blit(hint_text, hint_rect)

    # =================================================================
    # Editor de Texturas (F3)
    # =================================================================

    def _init_texture_editor(self):
        """Inicializar datos del editor de texturas"""
        self.tex_defaults = self._get_texture_defaults()
        self._load_tex_params()
        self._build_tex_groups()

    def _get_texture_defaults(self):
        """Retorna dict con todos los valores default"""
        return {
            "CAVE_DOT_SIZE": 2,
            "CAVE_DOT_DENSITY": 0.002,
            "OVERLAY_CHEVRON_PERIOD": 14,
            "OVERLAY_CHEVRON_W": [10, 18],
            "OVERLAY_CHEVRON_H": [5, 9],
            "OVERLAY_CHEVRON_THICKNESS": [2, 4],
            "OVERLAY_CHEVRON_SPACING": [2, 8],
            "OVERLAY_CHEVRON_IRREGULARITY": 0.3,
            "OVERLAY_NOISE_DENSITY": 0.08,
            "OVERLAY_CLUSTER_COUNT": [2, 5],
            "OVERLAY_CLUSTER_SIZE": [2, 5],
            "OVERLAY_CLUSTER_FILL": 0.65,
            "OVERLAY_BIG_HOLE_COUNT": [1, 3],
            "OVERLAY_BIG_HOLE_W": [5, 12],
            "OVERLAY_BIG_HOLE_H": [4, 8],
            "OVERLAY_BIG_HOLE_EDGE_SKIP": 0.4,
            "OVERLAY_TEETH_COUNT": [8, 14],
            "OVERLAY_TEETH_W": [1, 5],
            "OVERLAY_TEETH_DEPTH": [3, 10],
            "OVERLAY_TEETH_BASE_GAP": 0.15,
            "OVERLAY_TEETH_BASE_EXTRA": 0.6,
            "MOSS_BASE_H": 2,
            "MOSS_BASE_W": 2,
            "MOSS_MAX_DOWN": 14,
            "MOSS_MAX_UP": 12,
            "MOSS_MAX_SIDE": 10,
            "MOSS_BASE_GAP_CHANCE": 0.15,
            "MOSS_COLOR_VARIATION": 8,
            "MOSS_ALPHA_TIP": 80,
            "MOSS_ALPHA_BASE": 240,
            "MOSS_TENDRIL_COUNT": [1, 3],
            "MOSS_TENDRIL_LENGTH": [3, 12],
            "MOSS_JAG_GAP_CHANCE": 0.25,
            "MOSS_JAG_CLUSTER_LEN": [2, 6],
            "MOSS_JAG_PEAK_CHANCE": 0.06,
            "MOSS_JAG_PEAK_EXTRA": [4, 10],
        }

    def _load_tex_params(self):
        """Cargar parámetros desde JSON o usar defaults"""
        self.tex_params = dict(self.tex_defaults)
        try:
            with open(TEXTURE_PARAMS_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            for key in self.tex_params:
                if key in saved:
                    self.tex_params[key] = saved[key]
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def _save_tex_params(self):
        """Guardar parámetros a JSON"""
        with open(TEXTURE_PARAMS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.tex_params, f, indent=2)
        self.tex_dirty = False
        self.saved_indicator = 2.0

    def _build_tex_groups(self):
        """Construir grupos de parámetros para navegación.
        Cada parámetro es (key, label, type, min, max, step, step_shift).
        type: 'int', 'float', 'range_int', 'range_float'
        Para range: el valor es [min_val, max_val], se editan ambos."""
        self.tex_groups = [
            {
                "name": "Fondo caverna",
                "params": [
                    ("CAVE_DOT_SIZE", "Tam. punto", "int", 1, 8, 1, 1),
                    ("CAVE_DOT_DENSITY", "Densidad", "float", 0.0002, 0.01, 0.0002, 0.001),
                ],
            },
            {
                "name": "Chevrones",
                "params": [
                    ("OVERLAY_CHEVRON_PERIOD", "Periodo", "int", 4, 32, 1, 4),
                    ("OVERLAY_CHEVRON_W", "Ancho", "range_int", 2, 32, 1, 4),
                    ("OVERLAY_CHEVRON_H", "Altura", "range_int", 1, 20, 1, 3),
                    ("OVERLAY_CHEVRON_THICKNESS", "Grosor", "range_int", 1, 8, 1, 2),
                    ("OVERLAY_CHEVRON_SPACING", "Espacio", "range_int", 0, 20, 1, 4),
                    ("OVERLAY_CHEVRON_IRREGULARITY", "Irregular.", "float", 0.0, 1.0, 0.05, 0.1),
                ],
            },
            {
                "name": "Ruido",
                "params": [
                    ("OVERLAY_NOISE_DENSITY", "Densidad", "float", 0.0, 0.2, 0.005, 0.02),
                ],
            },
            {
                "name": "Clusters",
                "params": [
                    ("OVERLAY_CLUSTER_COUNT", "Cantidad", "range_int", 0, 15, 1, 3),
                    ("OVERLAY_CLUSTER_SIZE", "Tamaño", "range_int", 1, 12, 1, 3),
                    ("OVERLAY_CLUSTER_FILL", "Relleno", "float", 0.1, 1.0, 0.05, 0.1),
                ],
            },
            {
                "name": "Agujeros",
                "params": [
                    ("OVERLAY_BIG_HOLE_COUNT", "Cantidad", "range_int", 0, 10, 1, 2),
                    ("OVERLAY_BIG_HOLE_W", "Ancho", "range_int", 2, 24, 1, 4),
                    ("OVERLAY_BIG_HOLE_H", "Alto", "range_int", 2, 20, 1, 3),
                    ("OVERLAY_BIG_HOLE_EDGE_SKIP", "Borde skip", "float", 0.0, 1.0, 0.05, 0.1),
                ],
            },
            {
                "name": "Dientes",
                "params": [
                    ("OVERLAY_TEETH_COUNT", "Cantidad", "range_int", 0, 30, 1, 4),
                    ("OVERLAY_TEETH_W", "Ancho", "range_int", 1, 10, 1, 2),
                    ("OVERLAY_TEETH_DEPTH", "Profund.", "range_int", 1, 20, 1, 4),
                    ("OVERLAY_TEETH_BASE_GAP", "Huecos base", "float", 0.0, 0.5, 0.02, 0.05),
                    ("OVERLAY_TEETH_BASE_EXTRA", "Doble base", "float", 0.0, 1.0, 0.05, 0.1),
                ],
            },
            {
                "name": "Musgo base",
                "params": [
                    ("MOSS_BASE_H", "Base horiz", "int", 0, 8, 1, 2),
                    ("MOSS_BASE_W", "Base vert", "int", 0, 8, 1, 2),
                    ("MOSS_MAX_DOWN", "Max abajo", "int", 0, 28, 1, 4),
                    ("MOSS_MAX_UP", "Max arriba", "int", 0, 24, 1, 4),
                    ("MOSS_MAX_SIDE", "Max lateral", "int", 0, 20, 1, 4),
                    ("MOSS_BASE_GAP_CHANCE", "Huecos", "float", 0.0, 0.5, 0.02, 0.05),
                    ("MOSS_COLOR_VARIATION", "Var. color", "int", 0, 30, 1, 4),
                    ("MOSS_ALPHA_TIP", "Alpha punta", "int", 0, 255, 5, 20),
                    ("MOSS_ALPHA_BASE", "Alpha base", "int", 100, 255, 5, 20),
                ],
            },
            {
                "name": "Tendriles",
                "params": [
                    ("MOSS_TENDRIL_COUNT", "Cantidad", "range_int", 0, 8, 1, 2),
                    ("MOSS_TENDRIL_LENGTH", "Largo", "range_int", 1, 24, 1, 4),
                ],
            },
            {
                "name": "Dentado",
                "params": [
                    ("MOSS_JAG_GAP_CHANCE", "Prob. gap", "float", 0.0, 0.6, 0.02, 0.05),
                    ("MOSS_JAG_CLUSTER_LEN", "Cluster", "range_int", 1, 12, 1, 2),
                    ("MOSS_JAG_PEAK_CHANCE", "Prob. pico", "float", 0.0, 0.3, 0.01, 0.03),
                    ("MOSS_JAG_PEAK_EXTRA", "Alto pico", "range_int", 1, 20, 1, 4),
                ],
            },
        ]

    def _apply_params_to_palette(self):
        """Monkey-patch las constantes de textura en el módulo palette"""
        for key, value in self.tex_params.items():
            if hasattr(palette_module, key):
                if key in TEXTURE_TUPLE_KEYS and isinstance(value, list):
                    setattr(palette_module, key, tuple(value))
                else:
                    setattr(palette_module, key, value)

    def _generate_tex_previews(self):
        """Generar las superficies de preview del editor de texturas"""
        self._apply_params_to_palette()

        # Colores del nivel actual (o fallback)
        palette = self.get_current_palette()
        edge_color = self.get_current_edge_color()
        tinted_floors = build_tinted_floors(self.tiles['floor'], palette)

        # Colores para fondo de caverna
        if palette and len(palette) > 0:
            wc = palette[0].get("wall", [255, 255, 255])
            base_r, base_g, base_b = wc[0], wc[1], wc[2]
        else:
            base_r, base_g, base_b = 180, 120, 60

        # Lava tile
        lava_tile = self.tiles.get('lava', None)
        if lava_tile is None:
            lava_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
            lava_tile.fill((200, 80, 30))

        seed = self.tex_seed

        # --- Preview izquierdo: suelo compacto (6x6) arriba, lava compacta (6x6) abajo ---
        cols_l, rows_floor, rows_lava = 6, 4, 4
        rows_l = rows_floor + rows_lava
        pw_l = cols_l * TILE_SIZE  # 192
        ph_l = rows_l * TILE_SIZE  # 256

        # Mapa izquierdo: mitad suelo, mitad lava, todo compacto
        left_map = []
        for _ in range(rows_floor):
            left_map.append('.' * cols_l)
        for _ in range(rows_lava):
            left_map.append('X' * cols_l)

        floor_tex_l = generate_floor_texture(left_map, seed=seed)
        surf_l = pygame.Surface((pw_l, ph_l))
        surf_l.fill(COLOR_BLACK)

        # Dibujar tiles base
        for r in range(rows_l):
            local_row = r % VIEWPORT_ROWS
            for c in range(cols_l):
                x = c * TILE_SIZE
                y = r * TILE_SIZE
                if r < rows_floor:
                    surf_l.blit(tinted_floors[local_row], (x, y))
                else:
                    surf_l.blit(lava_tile, (x, y))
        # Overlay de textura
        surf_l.blit(floor_tex_l, (0, 0))
        self.tex_preview_left = surf_l

        # --- Preview derecho: suelo arriba (3 filas), aire abajo (5 filas) ---
        cols_r, rows_r = 6, 8
        rows_solid = 3
        pw_r = cols_r * TILE_SIZE  # 192
        ph_r = rows_r * TILE_SIZE  # 256

        right_map = []
        for _ in range(rows_solid):
            right_map.append('.' * cols_r)
        for _ in range(rows_r - rows_solid):
            right_map.append(' ' * cols_r)

        floor_tex_r = generate_floor_texture(right_map, seed=seed)
        edge_ov_r = generate_edge_overlay(right_map, edge_color, seed=seed)

        surf_r = pygame.Surface((pw_r, ph_r))
        surf_r.fill(COLOR_BLACK)

        # Generar cave dots en las filas de aire
        dot_brightness = self.tex_params.get("CAVE_DOT_BRIGHTNESS", [13, 15, 18, 20, 22, 25])
        dot_colors = [
            (max(0, base_r * pct // 100), max(0, base_g * pct // 100), max(0, base_b * pct // 100))
            for pct in dot_brightness
        ]
        dot_size = self.tex_params.get("CAVE_DOT_SIZE", 2)
        dot_density = self.tex_params.get("CAVE_DOT_DENSITY", 0.002)
        air_y_start = rows_solid * TILE_SIZE
        air_area = pw_r * (ph_r - air_y_start)
        num_dots = int(air_area * dot_density)
        rng = random.Random(seed)
        for _ in range(num_dots):
            dx = rng.randint(0, pw_r - dot_size)
            dy = air_y_start + rng.randint(0, ph_r - air_y_start - dot_size)
            color = rng.choice(dot_colors)
            if dot_size <= 1:
                surf_r.set_at((dx, dy), color)
            else:
                pygame.draw.rect(surf_r, color, (dx, dy, dot_size, dot_size))

        # Dibujar tiles de suelo
        for r in range(rows_solid):
            local_row = r % VIEWPORT_ROWS
            for c in range(cols_r):
                x = c * TILE_SIZE
                y = r * TILE_SIZE
                surf_r.blit(tinted_floors[local_row], (x, y))

        # Overlays
        surf_r.blit(floor_tex_r, (0, 0))
        surf_r.blit(edge_ov_r, (0, 0))

        self.tex_preview_right = surf_r

    def _tex_adjust_param(self, direction, big=False):
        """Ajustar el parámetro seleccionado en la dirección dada (-1 o +1)"""
        group = self.tex_groups[self.tex_sel_group]
        params = group["params"]
        if self.tex_sel_param >= len(params):
            return

        key, label, ptype, pmin, pmax, step, step_shift = params[self.tex_sel_param]
        s = step_shift if big else step
        val = self.tex_params[key]

        if ptype == "int":
            val = max(pmin, min(pmax, val + direction * s))
        elif ptype == "float":
            val = round(max(pmin, min(pmax, val + direction * s)), 4)
        elif ptype == "range_int":
            # val es [lo, hi]. Mods selecciona cuál editar: sin shift=ambos, con ctrl=solo min, con alt=solo max
            mods = pygame.key.get_mods()
            lo, hi = val[0], val[1]
            if mods & pygame.KMOD_ALT:
                # Solo max
                hi = max(lo, min(pmax, hi + direction * s))
            elif mods & pygame.KMOD_CTRL:
                # Solo min
                lo = max(pmin, min(hi, lo + direction * s))
            else:
                # Ambos
                lo = max(pmin, min(pmax, lo + direction * s))
                hi = max(lo, min(pmax, hi + direction * s))
            val = [lo, hi]
        elif ptype == "range_float":
            lo, hi = val[0], val[1]
            mods = pygame.key.get_mods()
            if mods & pygame.KMOD_ALT:
                hi = round(max(lo, min(pmax, hi + direction * s)), 4)
            elif mods & pygame.KMOD_CTRL:
                lo = round(max(pmin, min(hi, lo + direction * s)), 4)
            else:
                lo = round(max(pmin, min(pmax, lo + direction * s)), 4)
                hi = round(max(lo, min(pmax, hi + direction * s)), 4)
            val = [lo, hi]

        self.tex_params[key] = val
        self.tex_dirty = True
        self.tex_regen_timer = 0.3  # Regenerar en 0.3s

    def _tex_reset_param(self):
        """Resetear parámetro seleccionado al default"""
        group = self.tex_groups[self.tex_sel_group]
        params = group["params"]
        if self.tex_sel_param >= len(params):
            return
        key = params[self.tex_sel_param][0]
        if key in self.tex_defaults:
            self.tex_params[key] = type(self.tex_defaults[key])(self.tex_defaults[key])
            self.tex_dirty = True
            self.tex_regen_timer = 0.3

    def _tex_reset_all(self):
        """Resetear todos los parámetros a defaults"""
        for key, val in self.tex_defaults.items():
            self.tex_params[key] = type(val)(val) if isinstance(val, list) else val
        self.tex_dirty = True
        self.tex_regen_timer = 0.3

    def _tex_format_value(self, key, ptype):
        """Formatear valor para mostrar"""
        val = self.tex_params[key]
        if ptype in ("range_int", "range_float"):
            if ptype == "range_float":
                return f"{val[0]:.3f} - {val[1]:.3f}"
            return f"{val[0]} - {val[1]}"
        elif ptype == "float":
            return f"{val:.4f}"
        return str(val)

    def render_texture_editor(self):
        """Renderizar la pantalla del editor de texturas"""
        self.screen.fill((12, 12, 20))

        # Layout: previews arriba (izq y der), panel de parámetros abajo
        preview_w = 192  # 6 tiles * 32
        preview_h_l = 256  # 8 tiles * 32 (left: 4 suelo + 4 lava)
        preview_h_r = 256  # 8 tiles * 32 (right: 3 suelo + 5 aire)
        # Escalar previews
        scale = 0.55
        sw = int(preview_w * scale)   # ~106
        sh_l = int(preview_h_l * scale)  # ~141
        sh_r = int(preview_h_r * scale)  # ~141
        preview_area_h = max(sh_l, sh_r) + 18  # +18 para label

        # --- Preview izquierdo ---
        lx = 8
        ly = 14
        label_l = self.small_font.render("SUELO + LAVA", True, (180, 180, 200))
        self.screen.blit(label_l, (lx, ly - 12))
        if self.tex_preview_left:
            scaled = pygame.transform.scale(self.tex_preview_left, (sw, sh_l))
            self.screen.blit(scaled, (lx, ly))
        pygame.draw.rect(self.screen, (60, 60, 80), (lx - 1, ly - 1, sw + 2, sh_l + 2), 1)

        # --- Preview derecho ---
        rx = lx + sw + 8
        label_r = self.small_font.render("SUELO + MUSGO", True, (180, 180, 200))
        self.screen.blit(label_r, (rx, ly - 12))
        if self.tex_preview_right:
            scaled = pygame.transform.scale(self.tex_preview_right, (sw, sh_r))
            self.screen.blit(scaled, (rx, ly))
        pygame.draw.rect(self.screen, (60, 60, 80), (rx - 1, ly - 1, sw + 2, sh_r + 2), 1)

        # --- Panel de parámetros (a la derecha de los previews) ---
        panel_x = rx + sw + 10
        panel_w = GAME_WIDTH - panel_x - 4
        panel_y = 2

        # Título del editor
        title = self.font.render("TEXTURAS", True, (220, 200, 80))
        self.screen.blit(title, (panel_x, panel_y))

        # Tabs de grupos
        tab_x = panel_x
        tab_y = panel_y + 14
        tab_start_x = panel_x
        for i, group in enumerate(self.tex_groups):
            name = group["name"]
            is_sel = (i == self.tex_sel_group)
            color = (220, 200, 80) if is_sel else (100, 100, 120)
            bg = (40, 40, 60) if is_sel else (20, 20, 35)
            txt = self.small_font.render(name, True, color)
            tw = txt.get_width() + 6
            th = txt.get_height() + 4
            # Wrap si se pasa del ancho
            if tab_x + tw > GAME_WIDTH - 4:
                tab_x = tab_start_x
                tab_y += th + 2
            pygame.draw.rect(self.screen, bg, (tab_x, tab_y, tw, th))
            if is_sel:
                pygame.draw.rect(self.screen, (220, 200, 80), (tab_x, tab_y, tw, th), 1)
            self.screen.blit(txt, (tab_x + 3, tab_y + 2))
            tab_x += tw + 2

        # Lista de parámetros del grupo seleccionado
        group = self.tex_groups[self.tex_sel_group]
        params = group["params"]
        list_y = tab_y + 16
        row_h = 13

        # Separador
        pygame.draw.line(self.screen, (50, 50, 70),
                         (panel_x, list_y - 2), (GAME_WIDTH - 6, list_y - 2))

        for i, (key, label, ptype, pmin, pmax, step, step_shift) in enumerate(params):
            y = list_y + i * row_h
            if y + row_h > preview_area_h + ly:
                break
            is_sel = (i == self.tex_sel_param)
            # Fondo seleccionado
            if is_sel:
                pygame.draw.rect(self.screen, (35, 35, 60),
                                 (panel_x, y, panel_w, row_h))
                pygame.draw.rect(self.screen, (220, 200, 80),
                                 (panel_x, y, 2, row_h))

            # Label
            lbl_color = (220, 200, 80) if is_sel else (160, 160, 180)
            lbl = self.small_font.render(label, True, lbl_color)
            self.screen.blit(lbl, (panel_x + 6, y + 2))

            # Valor
            val_str = self._tex_format_value(key, ptype)
            val_color = COLOR_WHITE if is_sel else (200, 200, 200)
            val_txt = self.small_font.render(val_str, True, val_color)
            self.screen.blit(val_txt, (panel_x + panel_w - val_txt.get_width() - 14, y + 2))

            # Indicador de modificado
            if self.tex_params[key] != self.tex_defaults.get(key):
                mod = self.small_font.render("*", True, (255, 100, 100))
                self.screen.blit(mod, (panel_x + panel_w - 8, y + 2))

        # --- Barra de controles (debajo de los previews) ---
        ctrl_y = ly + max(sh_l, sh_r) + 6
        hints = [
            "Tab/ShTab:Grupo  Up/Dn:Param  L/R:Valor  Sh+L/R:Grande",
            "Ctrl+L/R:solo min  Alt+L/R:solo max  R:Seed",
            "Ctrl+Z:Reset param  Ctrl+R:Reset todo  Ctrl+S:Guardar  Esc:Salir",
        ]
        for i, h in enumerate(hints):
            ht = self.small_font.render(h, True, (90, 90, 110))
            self.screen.blit(ht, (8, ctrl_y + i * 11))

        # Indicador dirty + seed (esquina inferior)
        status_y = ctrl_y + len(hints) * 11 + 4
        if self.tex_dirty:
            dirty_txt = self.small_font.render("(sin guardar)", True, (255, 140, 60))
            self.screen.blit(dirty_txt, (8, status_y))

        seed_txt = self.small_font.render(f"Seed:{self.tex_seed}", True, (80, 80, 100))
        self.screen.blit(seed_txt, (GAME_WIDTH - seed_txt.get_width() - 8, status_y))

        # Indicador de guardado
        if self.saved_indicator > 0:
            save_text = self.font.render("Guardado!", True, COLOR_GREEN)
            self.screen.blit(save_text, (GAME_WIDTH // 2 - save_text.get_width() // 2, status_y))

    def handle_texture_events(self, event):
        """Procesar eventos en modo textura. Retorna False si hay que salir del modo."""
        if event.type != pygame.KEYDOWN:
            return True

        mods = pygame.key.get_mods()
        ctrl = mods & pygame.KMOD_CTRL
        shift = mods & pygame.KMOD_SHIFT

        if event.key == pygame.K_ESCAPE or event.key == pygame.K_F3:
            return False

        elif event.key == pygame.K_TAB:
            if shift:
                self.tex_sel_group = (self.tex_sel_group - 1) % len(self.tex_groups)
            else:
                self.tex_sel_group = (self.tex_sel_group + 1) % len(self.tex_groups)
            self.tex_sel_param = 0

        elif event.key == pygame.K_UP:
            group = self.tex_groups[self.tex_sel_group]
            self.tex_sel_param = (self.tex_sel_param - 1) % len(group["params"])

        elif event.key == pygame.K_DOWN:
            group = self.tex_groups[self.tex_sel_group]
            self.tex_sel_param = (self.tex_sel_param + 1) % len(group["params"])

        elif event.key == pygame.K_RIGHT:
            self._tex_adjust_param(1, big=shift)

        elif event.key == pygame.K_LEFT:
            self._tex_adjust_param(-1, big=shift)

        elif event.key == pygame.K_z and ctrl:
            self._tex_reset_param()

        elif event.key == pygame.K_r and ctrl:
            self._tex_reset_all()

        elif event.key == pygame.K_r and not ctrl:
            # Cambiar seed
            self.tex_seed = random.randint(1, 9999)
            self.tex_regen_timer = 0.1

        elif event.key == pygame.K_s and ctrl:
            self._save_tex_params()

        return True

    def render_palette_overlay(self):
        """Renderizar overlay del modo paleta"""
        if not self.palette_mode:
            return

        palette = self.get_current_palette()
        edge_col = self.get_current_edge_color()

        # Panel semi-transparente en la parte superior
        overlay = pygame.Surface((GAME_WIDTH, 56), pygame.SRCALPHA)
        overlay.fill((0, 0, 40, 200))
        self.screen.blit(overlay, (0, 0))

        # Los 3 colores editables con sus labels
        items = [
            ("Color1 (F0-4)", palette[0].get("wall", NEUTRAL_TINT) if len(palette) > 0 else list(NEUTRAL_TINT)),
            ("Color2 (F5-7)", palette[1].get("wall", NEUTRAL_TINT) if len(palette) > 1 else list(NEUTRAL_TINT)),
            ("Edge",          edge_col),
        ]

        wy = 4
        for i, (label, color) in enumerate(items):
            px = 8 + i * 170
            is_selected = (i == self.palette_editing)
            # Cuadrado de preview
            pygame.draw.rect(self.screen, tuple(color), (px, wy, 16, 16))
            border = COLOR_YELLOW if is_selected else (60, 60, 60)
            pygame.draw.rect(self.screen, border, (px - 1, wy - 1, 18, 18), 2)
            # Label
            lbl = self.small_font.render(label, True, COLOR_YELLOW if is_selected else COLOR_GRAY)
            self.screen.blit(lbl, (px + 20, wy + 4))

        # Valores RGB del color activo
        active_color = items[self.palette_editing][1]
        channel_names = ["R", "G", "B"]
        info_y = 24
        for i in range(3):
            cx = 8 + i * 80
            ch_color = COLOR_YELLOW if i == self.palette_channel else COLOR_GRAY
            val_text = self.font.render(f"{channel_names[i]}:{active_color[i]:3d}", True, ch_color)
            self.screen.blit(val_text, (cx, info_y))

        # Controles hint
        hint = self.small_font.render(
            "Tab:Cambiar 1/2/3:RGB L/R:+-15(Sh:5) Esc:Salir",
            True, COLOR_GRAY
        )
        self.screen.blit(hint, (8, 42))

    def run(self):
        """Loop principal del editor"""
        running = True
        pygame.key.set_repeat(180, 60)

        while running:
            dt = self.clock.tick(FPS) / 1000.0

            if self.saved_indicator > 0:
                self.saved_indicator -= dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    mods = pygame.key.get_mods()
                    shift = mods & pygame.KMOD_SHIFT
                    ctrl = mods & pygame.KMOD_CTRL

                    # Dialogo de confirmacion activo
                    if self.confirm_shrink:
                        shrink = self.confirm_shrink
                        if shrink['type'] == 'both':
                            # Elegir entre columna o fila
                            if event.key == pygame.K_c:
                                self.remove_viewport_col_at(shrink['col'])
                                self.confirm_shrink = None
                            elif event.key == pygame.K_f:
                                self.remove_viewport_row_at(shrink['row'])
                                self._clamp_cursor_col()
                                self.confirm_shrink = None
                            else:
                                self.confirm_shrink = None
                        elif event.key == pygame.K_y:
                            if shrink['type'] == 'cols':
                                self.remove_viewport_col_at(shrink['col'])
                            else:
                                self.remove_viewport_row_at(shrink['row'])
                            self._clamp_cursor_col()
                            self.confirm_shrink = None
                        else:
                            self.confirm_shrink = None
                        continue

                    # Toggle modo textura con F3
                    if event.key == pygame.K_F3:
                        if not self.texture_mode:
                            self.texture_mode = True
                            self._load_tex_params()
                            self._generate_tex_previews()
                        else:
                            self.texture_mode = False
                        continue

                    # Controles del modo textura
                    if self.texture_mode:
                        if not self.handle_texture_events(event):
                            self.texture_mode = False
                        continue

                    # Toggle modo paleta con P
                    if event.key == pygame.K_p and not ctrl:
                        self.palette_mode = not self.palette_mode
                        continue

                    # Controles del modo paleta
                    if self.palette_mode:
                        if event.key == pygame.K_ESCAPE:
                            self.palette_mode = False
                        elif event.key == pygame.K_TAB:
                            # Ciclar entre Color1, Color2, Edge
                            self.palette_editing = (self.palette_editing + 1) % 3
                        elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                            # Seleccionar canal R/G/B
                            self.palette_channel = event.key - pygame.K_1
                        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                            # Ajustar color: RIGHT +, LEFT -
                            color = self._get_editing_color()
                            if color is not None:
                                step = 15 if not shift else 5
                                if event.key == pygame.K_RIGHT:
                                    color[self.palette_channel] = min(255, color[self.palette_channel] + step)
                                else:
                                    color[self.palette_channel] = max(0, color[self.palette_channel] - step)
                                self.invalidate_tinted_cache()
                        continue

                    # Dimensiones actuales del nivel
                    w, h = self.get_level_dims()

                    if event.key == pygame.K_ESCAPE:
                        running = False

                    # Movimiento del cursor (con clamp por banda)
                    elif event.key == pygame.K_UP:
                        if not ctrl:
                            self.cursor_row = max(0, self.cursor_row - 1)
                            # Clamp col al ancho de la nueva banda
                            self._clamp_cursor_col()
                            if shift:
                                self.set_tile(self.cursor_row, self.cursor_col,
                                              TILE_TYPES[self.selected_tile][0])
                    elif event.key == pygame.K_DOWN:
                        if ctrl:
                            # Ctrl+Down: agregar fila de viewports
                            self.add_viewport_rows()
                        else:
                            self.cursor_row = min(h - 1, self.cursor_row + 1)
                            # Clamp col al ancho de la nueva banda
                            self._clamp_cursor_col()
                            if shift:
                                self.set_tile(self.cursor_row, self.cursor_col,
                                              TILE_TYPES[self.selected_tile][0])
                    elif event.key == pygame.K_LEFT:
                        if not ctrl:
                            self.cursor_col = max(0, self.cursor_col - 1)
                            if shift:
                                self.set_tile(self.cursor_row, self.cursor_col,
                                              TILE_TYPES[self.selected_tile][0])
                    elif event.key == pygame.K_RIGHT:
                        if ctrl:
                            # Ctrl+Right: agregar columna de viewports
                            self.add_viewport_cols()
                        else:
                            # Clamp al ancho de la banda actual
                            level_map = self.get_current_map()
                            band_start = (self.cursor_row // VIEWPORT_ROWS) * VIEWPORT_ROWS
                            band_w = len(level_map[band_start]) if band_start < len(level_map) else VIEWPORT_COLS
                            self.cursor_col = min(band_w - 1, self.cursor_col + 1)
                            if shift:
                                self.set_tile(self.cursor_row, self.cursor_col,
                                              TILE_TYPES[self.selected_tile][0])

                    # Colocar tile
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.set_tile(self.cursor_row, self.cursor_col,
                                      TILE_TYPES[self.selected_tile][0])

                    # Seleccion de tile (teclas 1-9, F, G, H, J, K, L)
                    elif event.key == pygame.K_1:
                        self.selected_tile = 0
                    elif event.key == pygame.K_2:
                        self.selected_tile = 1
                    elif event.key == pygame.K_3:
                        self.selected_tile = 2
                    elif event.key == pygame.K_4:
                        self.selected_tile = 3
                    elif event.key == pygame.K_5:
                        self.selected_tile = 4
                    elif event.key == pygame.K_6:
                        self.selected_tile = 5
                    elif event.key == pygame.K_7:
                        self.selected_tile = 6
                    elif event.key == pygame.K_8:
                        self.selected_tile = 7
                    elif event.key == pygame.K_9:
                        if len(TILE_TYPES) > 8:
                            self.selected_tile = 8
                    elif event.key == pygame.K_f:
                        if len(TILE_TYPES) > 9:
                            self.selected_tile = 9
                    elif event.key == pygame.K_g:
                        if len(TILE_TYPES) > 10:
                            self.selected_tile = 10
                    elif event.key == pygame.K_h:
                        if len(TILE_TYPES) > 11:
                            self.selected_tile = 11
                    elif event.key == pygame.K_j:
                        if len(TILE_TYPES) > 12:
                            self.selected_tile = 12
                    elif event.key == pygame.K_k:
                        if len(TILE_TYPES) > 13:
                            self.selected_tile = 13
                    elif event.key == pygame.K_l:
                        if len(TILE_TYPES) > 14:
                            self.selected_tile = 14
                    elif event.key == pygame.K_z:
                        if len(TILE_TYPES) > 15:
                            self.selected_tile = 15

                    # Tab para ciclar tipo de tile
                    elif event.key == pygame.K_TAB:
                        if shift:
                            self.selected_tile = (self.selected_tile - 1) % len(TILE_TYPES)
                        else:
                            self.selected_tile = (self.selected_tile + 1) % len(TILE_TYPES)

                    # Guardar (Ctrl+S)
                    elif event.key == pygame.K_s and ctrl:
                        for i, screen in enumerate(self.screens):
                            flat = ''.join(screen['map'])
                            if flat.count('S') != 1:
                                print(f"ADVERTENCIA: Nivel {i+1} debe tener exactamente 1 tile S (Start)")
                            if flat.count('M') != 1:
                                print(f"ADVERTENCIA: Nivel {i+1} debe tener exactamente 1 tile M (Minero)")
                        if save_screens(self.screens):
                            self.saved_indicator = 2.0
                            print(f"Pantallas guardadas en {SCREENS_FILE}")

                    # Nuevo nivel (Ctrl+N)
                    elif event.key == pygame.K_n and ctrl:
                        self.new_level()

                    # Eliminar viewport bajo el cursor (Del sin ctrl)
                    elif event.key == pygame.K_DELETE and not ctrl:
                        band_cols = self.get_viewport_grid()
                        cur_band = self.cursor_row // VIEWPORT_ROWS
                        cur_vx = self.cursor_col // VIEWPORT_COLS
                        cur_vy = cur_band
                        band_vp_cols = band_cols[cur_band] if cur_band < len(band_cols) else 1
                        can_del_col = band_vp_cols > 1
                        can_del_row = len(band_cols) > 1
                        if can_del_col and can_del_row:
                            # Ambas opciones: preguntar cual
                            self.confirm_shrink = {'type': 'both', 'col': cur_vx, 'row': cur_vy}
                        elif can_del_col:
                            self.confirm_shrink = {'type': 'cols', 'col': cur_vx}
                        elif can_del_row:
                            self.confirm_shrink = {'type': 'rows', 'row': cur_vy}

                    # Eliminar nivel (Ctrl+Delete)
                    elif event.key == pygame.K_DELETE and ctrl:
                        if len(self.screens) > 1:
                            self.screens.pop(self.current_level)
                            if self.current_level >= len(self.screens):
                                self.current_level = len(self.screens) - 1
                            self.cursor_row = 0
                            self.cursor_col = 0
                            self.camera_x = 0
                            self.camera_y = 0
                            self.target_camera_x = 0
                            self.target_camera_y = 0
                            self.camera_animating = False

                    # Cambiar de nivel
                    elif event.key == pygame.K_PAGEUP:
                        if self.current_level > 0:
                            self.current_level -= 1
                            self.cursor_row = 0
                            self.cursor_col = 0
                            self.camera_x = 0
                            self.camera_y = 0
                            self.target_camera_x = 0
                            self.target_camera_y = 0
                            self.camera_animating = False
                    elif event.key == pygame.K_PAGEDOWN:
                        if self.current_level < len(self.screens) - 1:
                            self.current_level += 1
                            self.cursor_row = 0
                            self.cursor_col = 0
                            self.camera_x = 0
                            self.camera_y = 0
                            self.target_camera_x = 0
                            self.target_camera_y = 0
                            self.camera_animating = False

                    # Saltar por viewports con Q/A (vertical) y Z/X (horizontal)
                    elif event.key == pygame.K_q:
                        current_block = self.cursor_row // VIEWPORT_ROWS
                        if current_block > 0:
                            self.cursor_row = (current_block - 1) * VIEWPORT_ROWS
                        else:
                            self.cursor_row = 0
                        self._clamp_cursor_col()

                    elif event.key == pygame.K_a:
                        current_block = self.cursor_row // VIEWPORT_ROWS
                        max_block = (h // VIEWPORT_ROWS) - 1
                        if current_block < max_block:
                            self.cursor_row = (current_block + 1) * VIEWPORT_ROWS
                        else:
                            self.cursor_row = h - 1
                        self._clamp_cursor_col()

                    elif event.key == pygame.K_z:
                        current_block = self.cursor_col // VIEWPORT_COLS
                        if current_block > 0:
                            self.cursor_col = (current_block - 1) * VIEWPORT_COLS
                        else:
                            self.cursor_col = 0

                    elif event.key == pygame.K_x:
                        level_map = self.get_current_map()
                        band_start = (self.cursor_row // VIEWPORT_ROWS) * VIEWPORT_ROWS
                        band_w = len(level_map[band_start]) if band_start < len(level_map) else VIEWPORT_COLS
                        current_block = self.cursor_col // VIEWPORT_COLS
                        max_block = (band_w // VIEWPORT_COLS) - 1
                        if current_block < max_block:
                            self.cursor_col = (current_block + 1) * VIEWPORT_COLS
                        else:
                            self.cursor_col = band_w - 1

            # Debounce de regeneración de texturas
            if self.texture_mode and self.tex_regen_timer > 0:
                self.tex_regen_timer -= dt
                if self.tex_regen_timer <= 0:
                    self._generate_tex_previews()

            if self.texture_mode:
                # Render modo textura
                self.screen.fill(COLOR_BLACK)
                self.render_texture_editor()
                pygame.transform.scale(self.screen, self.display.get_size(), self.display)
                pygame.display.flip()
            else:
                # Cámara por bloques de viewport con animación
                self.update_camera()
                if self.camera_animating:
                    diff_x = self.target_camera_x - self.camera_x
                    diff_y = self.target_camera_y - self.camera_y
                    if abs(diff_x) < 1 and abs(diff_y) < 1:
                        self.camera_x = self.target_camera_x
                        self.camera_y = self.target_camera_y
                        self.camera_animating = False
                    else:
                        self.camera_x += diff_x * 0.15
                        self.camera_y += diff_y * 0.15

                # Render
                self.screen.fill(COLOR_BLACK)
                self.render_grid()
                self.render_hud()
                self.render_palette_overlay()
                pygame.transform.scale(self.screen, self.display.get_size(), self.display)
                pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    editor = Editor()
    editor.run()
