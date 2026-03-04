# H.E.R.O. Level Editor
# Editor de pantallas para el juego H.E.R.O.

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
    """Asegurar que el mapa sea exactamente LEVEL_WIDTH x LEVEL_HEIGHT"""
    result = []
    for row in level_map:
        if len(row) < LEVEL_WIDTH:
            row = row + '#' * (LEVEL_WIDTH - len(row))
        elif len(row) > LEVEL_WIDTH:
            row = row[:LEVEL_WIDTH]
        result.append(row)
    while len(result) < LEVEL_HEIGHT:
        result.append('#' * LEVEL_WIDTH)
    return result[:LEVEL_HEIGHT]

class Editor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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

        # Cargar sprites de entidades
        self.sprites = {}
        try:
            self.sprites['player'] = pygame.image.load("sprites/player.png").convert_alpha()
            self.sprites['enemy'] = pygame.image.load("sprites/bat.png").convert_alpha()
            self.sprites['spider'] = pygame.image.load("sprites/spider.png").convert_alpha()
            self.sprites['miner'] = pygame.image.load("sprites/miner.png").convert_alpha()
        except Exception as e:
            print(f"Error cargando sprites: {e}")

        # Estado del editor
        self.screens = load_screens()
        self.current_level = 0
        self.cursor_row = 0
        self.cursor_col = 0
        self.selected_tile = 1  # Pared por defecto
        self.camera_y = 0
        self.saved_indicator = 0  # Timer para mensaje "Guardado!"

        # Normalizar todas las pantallas cargadas
        for screen in self.screens:
            screen["map"] = normalize_map(screen["map"])

        if not self.screens:
            self.new_level()

    def new_level(self):
        """Crear un nivel vacio con bordes de pared"""
        empty_map = []
        for r in range(LEVEL_HEIGHT):
            if r == 0 or r == LEVEL_HEIGHT - 1:
                empty_map.append('#' * LEVEL_WIDTH)
            else:
                empty_map.append('#' + ' ' * (LEVEL_WIDTH - 2) + '#')
        self.screens.append({
            "name": f"Level {len(self.screens) + 1}",
            "map": empty_map
        })
        self.current_level = len(self.screens) - 1
        self.cursor_row = 1
        self.cursor_col = 1
        self.camera_y = 0

    def get_current_map(self):
        return self.screens[self.current_level]["map"]

    def set_tile(self, row, col, char):
        """Colocar un tile en la posicion dada"""
        level_map = self.get_current_map()
        row_str = level_map[row]
        level_map[row] = row_str[:col] + char + row_str[col + 1:]

    def update_camera(self):
        """Mantener el cursor visible en pantalla"""
        cursor_pixel_y = self.cursor_row * TILE_SIZE
        margin = 3 * TILE_SIZE

        if cursor_pixel_y - self.camera_y < margin:
            self.camera_y = max(0, cursor_pixel_y - margin)
        elif cursor_pixel_y - self.camera_y > VIEWPORT_HEIGHT - margin - TILE_SIZE:
            max_camera = LEVEL_HEIGHT * TILE_SIZE - VIEWPORT_HEIGHT
            self.camera_y = min(max_camera,
                                cursor_pixel_y - VIEWPORT_HEIGHT + margin + TILE_SIZE)

    def render_grid(self):
        """Renderizar la cuadricula del nivel"""
        level_map = self.get_current_map()

        start_row = max(0, int(self.camera_y / TILE_SIZE) - 1)
        end_row = min(LEVEL_HEIGHT, int((self.camera_y + VIEWPORT_HEIGHT) / TILE_SIZE) + 2)

        for row_index in range(start_row, end_row):
            if row_index >= len(level_map):
                break
            row = level_map[row_index]
            for col_index in range(min(len(row), LEVEL_WIDTH)):
                tile = row[col_index]
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE - self.camera_y

                # Dibujar fondo del tile
                if tile == '#':
                    self.screen.blit(self.tiles['wall'], (x, int(y)))
                elif tile == '.':
                    self.screen.blit(self.tiles['floor'], (x, int(y)))
                elif tile == 'G':
                    self.screen.blit(self.tiles['granite'], (x, int(y)))
                elif tile == 'R':
                    self.screen.blit(self.tiles['rock'], (x, int(y)))
                else:
                    self.screen.blit(self.tiles['blank'], (x, int(y)))

                # Dibujar sprites de entidades encima
                sprite_map = {'S': 'player', 'V': 'enemy', 'A': 'spider', 'M': 'miner'}
                if tile in sprite_map and sprite_map[tile] in self.sprites:
                    self.screen.blit(self.sprites[sprite_map[tile]], (x, int(y)))
                elif tile in sprite_map:
                    # Fallback: dibujar letra con color
                    colors = {'S': COLOR_BLUE, 'V': COLOR_RED, 'A': COLOR_ORANGE, 'M': COLOR_GREEN}
                    letter = self.font.render(tile, True, colors[tile])
                    lx = x + (TILE_SIZE - letter.get_width()) // 2
                    ly = int(y) + (TILE_SIZE - letter.get_height()) // 2
                    self.screen.blit(letter, (lx, ly))

                # Lineas de cuadricula
                pygame.draw.rect(self.screen, (40, 40, 40),
                                 (x, int(y), TILE_SIZE, TILE_SIZE), 1)

        # Dibujar cursor
        cx = self.cursor_col * TILE_SIZE
        cy = self.cursor_row * TILE_SIZE - self.camera_y
        pygame.draw.rect(self.screen, COLOR_YELLOW,
                         (cx, int(cy), TILE_SIZE, TILE_SIZE), 3)

    def render_hud(self):
        """Renderizar barra de estado inferior"""
        hud_y = VIEWPORT_HEIGHT
        hud_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - VIEWPORT_HEIGHT))
        hud_bg.fill((20, 20, 50))
        self.screen.blit(hud_bg, (0, hud_y))

        # Info del nivel
        level_text = self.font.render(
            f"Nivel {self.current_level + 1}/{len(self.screens)}",
            True, COLOR_WHITE
        )
        self.screen.blit(level_text, (8, hud_y + 4))

        # Posicion del cursor
        pos_text = self.font.render(
            f"Fila:{self.cursor_row:02d} Col:{self.cursor_col:02d}",
            True, COLOR_WHITE
        )
        self.screen.blit(pos_text, (8, hud_y + 18))

        # Tile seleccionado
        char, name, color = TILE_TYPES[self.selected_tile]
        tile_text = self.font.render(f"[{char}] {name}", True, COLOR_YELLOW)
        self.screen.blit(tile_text, (8, hud_y + 32))

        # Tile bajo el cursor
        current_map = self.get_current_map()
        cursor_char = current_map[self.cursor_row][self.cursor_col]
        cursor_name = next((n for c, n, _ in TILE_TYPES if c == cursor_char), '?')
        cursor_text = self.font.render(
            f"Actual:[{cursor_char}] {cursor_name}", True, COLOR_GRAY
        )
        self.screen.blit(cursor_text, (170, hud_y + 4))

        # Paleta de tiles (lado derecho)
        palette_x = 170
        palette_y = hud_y + 22
        for i, (tc, tn, tcolor) in enumerate(TILE_TYPES):
            px = palette_x + i * 30

            # Preview cuadrado pequeno
            preview = pygame.Surface((20, 20))
            if tc == '#':
                preview = pygame.transform.scale(self.tiles['wall'], (20, 20))
            elif tc == '.':
                preview = pygame.transform.scale(self.tiles['floor'], (20, 20))
            elif tc == 'G':
                preview = pygame.transform.scale(self.tiles['granite'], (20, 20))
            elif tc == 'R':
                preview = pygame.transform.scale(self.tiles['rock'], (20, 20))
            else:
                preview.fill(tcolor if tc != ' ' else (30, 30, 30))
                # Letra para entidades
                if tc in ('S', 'V', 'A', 'M'):
                    l = self.small_font.render(tc, True, COLOR_WHITE)
                    preview.blit(l, (6, 6))

            self.screen.blit(preview, (px, palette_y))

            # Numero de tecla
            num_color = COLOR_YELLOW if i == self.selected_tile else COLOR_GRAY
            num_text = self.small_font.render(str(i + 1), True, num_color)
            self.screen.blit(num_text, (px + 7, palette_y + 22))

            # Borde de seleccion
            if i == self.selected_tile:
                pygame.draw.rect(self.screen, COLOR_YELLOW,
                                 (px - 2, palette_y - 2, 24, 24), 2)

        # Controles
        hint = self.small_font.render(
            "Spc:Poner ^S:Guardar PgUp/Dn:Nivel ^N:Nuevo",
            True, COLOR_GRAY
        )
        self.screen.blit(hint, (8, hud_y + 52))

        # Indicador de guardado
        if self.saved_indicator > 0:
            save_text = self.font.render("Guardado!", True, COLOR_GREEN)
            self.screen.blit(save_text, (410, hud_y + 52))

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

                    if event.key == pygame.K_ESCAPE:
                        running = False

                    # Movimiento del cursor
                    elif event.key == pygame.K_UP:
                        self.cursor_row = max(0, self.cursor_row - 1)
                        if shift:
                            self.set_tile(self.cursor_row, self.cursor_col,
                                          TILE_TYPES[self.selected_tile][0])
                    elif event.key == pygame.K_DOWN:
                        self.cursor_row = min(LEVEL_HEIGHT - 1, self.cursor_row + 1)
                        if shift:
                            self.set_tile(self.cursor_row, self.cursor_col,
                                          TILE_TYPES[self.selected_tile][0])
                    elif event.key == pygame.K_LEFT:
                        self.cursor_col = max(0, self.cursor_col - 1)
                        if shift:
                            self.set_tile(self.cursor_row, self.cursor_col,
                                          TILE_TYPES[self.selected_tile][0])
                    elif event.key == pygame.K_RIGHT:
                        self.cursor_col = min(LEVEL_WIDTH - 1, self.cursor_col + 1)
                        if shift:
                            self.set_tile(self.cursor_row, self.cursor_col,
                                          TILE_TYPES[self.selected_tile][0])

                    # Colocar tile
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.set_tile(self.cursor_row, self.cursor_col,
                                      TILE_TYPES[self.selected_tile][0])

                    # Seleccion de tile (teclas 1-8)
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

                    # Tab para ciclar tipo de tile
                    elif event.key == pygame.K_TAB:
                        if shift:
                            self.selected_tile = (self.selected_tile - 1) % len(TILE_TYPES)
                        else:
                            self.selected_tile = (self.selected_tile + 1) % len(TILE_TYPES)

                    # Guardar (Ctrl+S)
                    elif event.key == pygame.K_s and ctrl:
                        # Validar niveles antes de guardar
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
                            self.camera_y = 0

                    # Cambiar de nivel
                    elif event.key == pygame.K_PAGEUP:
                        if self.current_level > 0:
                            self.current_level -= 1
                            self.cursor_row = 0
                            self.cursor_col = 0
                            self.camera_y = 0
                    elif event.key == pygame.K_PAGEDOWN:
                        if self.current_level < len(self.screens) - 1:
                            self.current_level += 1
                            self.cursor_row = 0
                            self.cursor_col = 0
                            self.camera_y = 0

            self.update_camera()

            # Render
            self.screen.fill(COLOR_BLACK)
            self.render_grid()
            self.render_hud()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    editor = Editor()
    editor.run()
