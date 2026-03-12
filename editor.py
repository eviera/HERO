# H.E.R.O. Level Editor
# Editor de pantallas para el juego H.E.R.O.
# Soporta niveles de tamaño dinámico (múltiplos del viewport 8x16)

import pygame
import json
import os
from constants import *

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
    """Normalizar mapa a múltiplos del viewport (VIEWPORT_COLS x VIEWPORT_ROWS)"""
    if not level_map:
        return ['#' * VIEWPORT_COLS] * VIEWPORT_ROWS

    map_height = len(level_map)
    map_width = max(len(row) for row in level_map) if level_map else VIEWPORT_COLS

    # Redondear al múltiplo de viewport más cercano
    target_w = max(VIEWPORT_COLS, ((map_width + VIEWPORT_COLS - 1) // VIEWPORT_COLS) * VIEWPORT_COLS)
    target_h = max(VIEWPORT_ROWS, ((map_height + VIEWPORT_ROWS - 1) // VIEWPORT_ROWS) * VIEWPORT_ROWS)

    result = []
    for row in level_map:
        if len(row) < target_w:
            row = row + '#' * (target_w - len(row))
        elif len(row) > target_w:
            row = row[:target_w]
        result.append(row)
    while len(result) < target_h:
        result.append('#' * target_w)
    return result[:target_h]

def get_map_dims(level_map):
    """Obtener dimensiones del mapa en tiles"""
    h = len(level_map) if level_map else VIEWPORT_ROWS
    w = len(level_map[0]) if level_map else VIEWPORT_COLS
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
        self.screen = pygame.display.set_mode((editor_w, self.editor_h))
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

    def get_level_dims(self):
        """Dimensiones del nivel actual en tiles"""
        return get_map_dims(self.get_current_map())

    def get_viewport_grid(self):
        """Cantidad de viewports en cada eje"""
        w, h = self.get_level_dims()
        return w // VIEWPORT_COLS, h // VIEWPORT_ROWS

    def set_tile(self, row, col, char):
        """Colocar un tile en la posicion dada"""
        level_map = self.get_current_map()
        if 0 <= row < len(level_map) and 0 <= col < len(level_map[row]):
            row_str = level_map[row]
            level_map[row] = row_str[:col] + char + row_str[col + 1:]

    def add_viewport_cols(self):
        """Agregar un viewport (VIEWPORT_COLS columnas) a la derecha"""
        level_map = self.get_current_map()
        extra = '#' * VIEWPORT_COLS
        for i in range(len(level_map)):
            level_map[i] = level_map[i] + extra

    def remove_viewport_cols(self):
        """Quitar el viewport más a la derecha (VIEWPORT_COLS columnas)"""
        level_map = self.get_current_map()
        w, _ = self.get_level_dims()
        if w <= VIEWPORT_COLS:
            return False  # No quitar si solo queda 1 viewport de ancho

        new_w = w - VIEWPORT_COLS
        for i in range(len(level_map)):
            level_map[i] = level_map[i][:new_w]

        # Ajustar cursor y cámara si quedan fuera
        if self.cursor_col >= new_w:
            self.cursor_col = new_w - 1
        max_cam_x = (new_w - VIEWPORT_COLS) * TILE_SIZE
        if self.camera_x > max_cam_x:
            self.camera_x = max_cam_x
            self.target_camera_x = max_cam_x
        return True

    def add_viewport_rows(self):
        """Agregar un viewport (VIEWPORT_ROWS filas) abajo"""
        level_map = self.get_current_map()
        w, _ = self.get_level_dims()
        for _ in range(VIEWPORT_ROWS):
            level_map.append('#' * w)

    def remove_viewport_rows(self):
        """Quitar el viewport más abajo (VIEWPORT_ROWS filas)"""
        level_map = self.get_current_map()
        _, h = self.get_level_dims()
        if h <= VIEWPORT_ROWS:
            return False  # No quitar si solo queda 1 viewport de alto

        new_h = h - VIEWPORT_ROWS
        del level_map[new_h:]

        # Ajustar cursor y cámara si quedan fuera
        if self.cursor_row >= new_h:
            self.cursor_row = new_h - 1
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
        """Cámara fija por bloques de viewport en ambos ejes"""
        w, h = self.get_level_dims()

        # Bloque horizontal
        block_x = VIEWPORT_COLS * TILE_SIZE
        max_cam_x = max(0, (w - VIEWPORT_COLS) * TILE_SIZE)
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

        start_row = max(0, int(cam_y / TILE_SIZE) - 1)
        end_row = min(h, int((cam_y + vh) / TILE_SIZE) + 2)
        start_col = max(0, int(cam_x / TILE_SIZE) - 1)
        end_col = min(w, int((cam_x + GAME_WIDTH) / TILE_SIZE) + 2)

        for row_index in range(start_row, end_row):
            if row_index >= len(level_map):
                break
            row = level_map[row_index]
            for col_index in range(start_col, end_col):
                if col_index >= len(row):
                    break
                tile = row[col_index]
                x = col_index * TILE_SIZE - cam_x
                y = row_index * TILE_SIZE - cam_y

                # Dibujar fondo del tile
                if tile == '#':
                    self.screen.blit(self.tiles['wall'], (int(x), int(y)))
                elif tile == '.':
                    self.screen.blit(self.tiles['floor'], (int(x), int(y)))
                elif tile == 'G':
                    self.screen.blit(self.tiles['granite'], (int(x), int(y)))
                elif tile == 'R':
                    self.screen.blit(self.tiles['rock'], (int(x), int(y)))
                elif tile == 'L':
                    self.screen.blit(self.tiles['blank'], (int(x), int(y)))
                    self.screen.blit(self.tiles['lamp'], (int(x), int(y)))
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
        for vx in range(1, w // VIEWPORT_COLS):
            px = vx * VIEWPORT_COLS * TILE_SIZE - cam_x
            if 0 <= px <= GAME_WIDTH:
                pygame.draw.line(self.screen, (80, 80, 120),
                                 (int(px), 0), (int(px), vh), 2)
        for vy in range(1, h // VIEWPORT_ROWS):
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
        """Renderizar minimapa en la posicion dada"""
        vp_cols, vp_rows = self.get_viewport_grid()
        if vp_cols == 0 or vp_rows == 0:
            return

        # Escala para que quepa en el espacio disponible
        cell_w = min(max_w // vp_cols, 16)
        cell_h = min(max_h // vp_rows, 12)
        cell_w = max(cell_w, 6)
        cell_h = max(cell_h, 6)

        total_w = vp_cols * cell_w
        total_h = vp_rows * cell_h

        # Viewport actual (basado en la cámara)
        cur_vx = int(self.camera_x) // (VIEWPORT_COLS * TILE_SIZE)
        cur_vy = int(self.camera_y) // (VIEWPORT_ROWS * TILE_SIZE)

        # Fondo del minimapa
        pygame.draw.rect(self.screen, (15, 15, 30),
                         (mx - 1, my - 1, total_w + 2, total_h + 2))

        for vy in range(vp_rows):
            for vx in range(vp_cols):
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

        # Etiqueta de dimensiones debajo
        dim_text = self.small_font.render(f"{vp_cols}x{vp_rows}", True, COLOR_GRAY)
        self.screen.blit(dim_text, (mx, my + total_h + 2))

    def render_hud(self):
        """Renderizar barra de estado inferior"""
        hud_y = self.editor_viewport_h
        hud_bg = pygame.Surface((GAME_WIDTH, self.editor_h - self.editor_viewport_h))
        hud_bg.fill((20, 20, 50))
        self.screen.blit(hud_bg, (0, hud_y))

        w, h = self.get_level_dims()
        vp_cols, vp_rows = self.get_viewport_grid()

        # --- Zona de texto (arriba) ---
        # Linea 1: Nivel + dimensiones
        level_text = self.font.render(
            f"Nivel {self.current_level + 1}/{len(self.screens)}  {w}x{h}t ({vp_cols}x{vp_rows}vp)",
            True, COLOR_WHITE
        )
        self.screen.blit(level_text, (8, hud_y + 4))

        # Linea 2: Posicion del cursor + tile actual
        current_map = self.get_current_map()
        cursor_char = current_map[self.cursor_row][self.cursor_col]
        cursor_name = next((n for c, n, *_ in TILE_TYPES if c == cursor_char), '?')

        # Viewport actual del cursor
        cur_vx = self.cursor_col // VIEWPORT_COLS + 1
        cur_vy = self.cursor_row // VIEWPORT_ROWS + 1

        pos_text = self.font.render(
            f"F:{self.cursor_row:02d} C:{self.cursor_col:02d} VP:{cur_vx},{cur_vy}  [{cursor_char}]{cursor_name}",
            True, COLOR_WHITE
        )
        self.screen.blit(pos_text, (8, hud_y + 18))

        # Linea 3: Tile seleccionado
        char, name, color, _score = TILE_TYPES[self.selected_tile]
        tile_text = self.font.render(f"[{char}] {name}", True, COLOR_YELLOW)
        self.screen.blit(tile_text, (8, hud_y + 32))

        # --- Minimapa (esquina superior derecha del HUD) ---
        minimap_x = GAME_WIDTH - 100
        minimap_y = hud_y + 4
        self.render_minimap(minimap_x, minimap_y, 90, 36)

        # --- Separador ---
        pygame.draw.line(self.screen, (60, 60, 80),
                         (8, hud_y + 46), (GAME_WIDTH - 8, hud_y + 46))

        # --- Zona de paleta (abajo) ---
        KEY_LABELS = "123456789" + "FGHJKL"
        tiles_per_row = 8
        tile_spacing = 38
        preview_size = 20
        row_height = 32

        # Centrar paleta horizontalmente
        total_row_width = tiles_per_row * tile_spacing - (tile_spacing - preview_size)
        palette_x = (GAME_WIDTH - total_row_width) // 2
        palette_y = hud_y + 52

        for i, (tc, tn, tcolor, _tscore) in enumerate(TILE_TYPES):
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
                'L': 'lamp'
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
            "^Arrows:+/- viewports ^N:Nuevo ^Del:Borrar",
            True, COLOR_GRAY
        )
        self.screen.blit(hint3, (8, hud_y + 140))

        # Indicador de guardado
        if self.saved_indicator > 0:
            save_text = self.font.render("Guardado!", True, COLOR_GREEN)
            self.screen.blit(save_text, (GAME_WIDTH - 130, hud_y + 46))

        # Dialogo de confirmacion para quitar viewport
        if self.confirm_shrink:
            overlay = pygame.Surface((GAME_WIDTH, self.editor_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            if self.confirm_shrink == 'cols':
                msg = "Quitar columna de viewports?"
            else:
                msg = "Quitar fila de viewports?"
            msg_text = self.font.render(msg, True, COLOR_YELLOW)
            msg_rect = msg_text.get_rect(center=(GAME_WIDTH // 2, self.editor_h // 2 - 20))
            self.screen.blit(msg_text, msg_rect)

            warn_text = self.small_font.render("Hay contenido! Y:Confirmar N:Cancelar", True, COLOR_RED)
            warn_rect = warn_text.get_rect(center=(GAME_WIDTH // 2, self.editor_h // 2 + 10))
            self.screen.blit(warn_text, warn_rect)

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
                        if event.key == pygame.K_y:
                            if self.confirm_shrink == 'cols':
                                self.remove_viewport_cols()
                            else:
                                self.remove_viewport_rows()
                            self.confirm_shrink = None
                        else:
                            self.confirm_shrink = None
                        continue

                    # Dimensiones actuales del nivel
                    w, h = self.get_level_dims()

                    if event.key == pygame.K_ESCAPE:
                        running = False

                    # Movimiento del cursor
                    elif event.key == pygame.K_UP:
                        if ctrl:
                            # Ctrl+Up: quitar fila de viewports
                            if h > VIEWPORT_ROWS:
                                # Verificar contenido en las filas a eliminar
                                start_r = h - VIEWPORT_ROWS
                                if self._has_content_in_region(start_r, h, 0, w):
                                    self.confirm_shrink = 'rows'
                                else:
                                    self.remove_viewport_rows()
                        else:
                            self.cursor_row = max(0, self.cursor_row - 1)
                            if shift:
                                self.set_tile(self.cursor_row, self.cursor_col,
                                              TILE_TYPES[self.selected_tile][0])
                    elif event.key == pygame.K_DOWN:
                        if ctrl:
                            # Ctrl+Down: agregar fila de viewports
                            self.add_viewport_rows()
                        else:
                            self.cursor_row = min(h - 1, self.cursor_row + 1)
                            if shift:
                                self.set_tile(self.cursor_row, self.cursor_col,
                                              TILE_TYPES[self.selected_tile][0])
                    elif event.key == pygame.K_LEFT:
                        if ctrl:
                            # Ctrl+Left: quitar columna de viewports
                            if w > VIEWPORT_COLS:
                                start_c = w - VIEWPORT_COLS
                                if self._has_content_in_region(0, h, start_c, w):
                                    self.confirm_shrink = 'cols'
                                else:
                                    self.remove_viewport_cols()
                        else:
                            self.cursor_col = max(0, self.cursor_col - 1)
                            if shift:
                                self.set_tile(self.cursor_row, self.cursor_col,
                                              TILE_TYPES[self.selected_tile][0])
                    elif event.key == pygame.K_RIGHT:
                        if ctrl:
                            # Ctrl+Right: agregar columna de viewports
                            self.add_viewport_cols()
                        else:
                            self.cursor_col = min(w - 1, self.cursor_col + 1)
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

                    elif event.key == pygame.K_a:
                        current_block = self.cursor_row // VIEWPORT_ROWS
                        max_block = (h // VIEWPORT_ROWS) - 1
                        if current_block < max_block:
                            self.cursor_row = (current_block + 1) * VIEWPORT_ROWS
                        else:
                            self.cursor_row = h - 1

                    elif event.key == pygame.K_z:
                        current_block = self.cursor_col // VIEWPORT_COLS
                        if current_block > 0:
                            self.cursor_col = (current_block - 1) * VIEWPORT_COLS
                        else:
                            self.cursor_col = 0

                    elif event.key == pygame.K_x:
                        current_block = self.cursor_col // VIEWPORT_COLS
                        max_block = (w // VIEWPORT_COLS) - 1
                        if current_block < max_block:
                            self.cursor_col = (current_block + 1) * VIEWPORT_COLS
                        else:
                            self.cursor_col = w - 1

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
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    editor = Editor()
    editor.run()
