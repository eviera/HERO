# H.E.R.O. Remake - Documentación para Claude

## Descripción del Proyecto

Este es un remake del clásico juego de Atari **H.E.R.O.** (Helicopter Emergency Rescue Operation), desarrollado en Python usando Pygame. Es un juego de acción 2D basado en tiles donde el jugador debe rescatar personas atrapadas en minas subterráneas.

**Tecnologías:**
- Python 3.13.0
- Pygame 2.6.1
- SDL 2.28.4

## Estructura del Proyecto

```
hero/
├── hero.py                      # Archivo principal del juego (~1410 líneas)
├── constants.py                 # Constantes del juego (~96 líneas)
├── player.py                    # Clase Player (~208 líneas)
├── enemy.py                     # Clase Enemy (~166 líneas)
├── laser.py                     # Clase Laser (~51 líneas)
├── dynamite.py                  # Clase Dynamite (~112 líneas)
├── miner.py                     # Clase Miner (~37 líneas)
├── audio_effects.py             # Emulación SID de Commodore 64 (numpy)
├── editor.py                    # Editor visual de niveles
├── screens.json                 # Niveles del juego (cargados en runtime)
├── scores.json                  # High scores persistidos
├── CLAUDE.md                    # Este archivo
├── IMPLEMENTATION_SUMMARY.md    # Resumen de implementación
├── fonts/
│   └── PressStart2P-vaV7.ttf   # Fuente estilo retro
├── sprites/
│   ├── player.png              # Sprite idle del jugador
│   ├── player_fly.png          # Sprite volando
│   ├── player_shooting.png     # Sprite disparando
│   ├── player_walk1.png        # Sprite caminata frame 1
│   ├── player_walk2.png        # Sprite caminata frame 2
│   ├── bat1.png                # Sprite murciélago frame 1
│   ├── bat2.png                # Sprite murciélago frame 2
│   ├── spider.png              # Sprite araña
│   ├── miner.png               # Sprite del minero rescatado
│   ├── bomb1.png               # Sprite bomba/explosión frame 1
│   ├── bomb2.png               # Sprite bomba/explosión frame 2
│   └── bomb3.png               # Sprite bomba/explosión frame 3
├── tiles/
│   ├── wall.png                # Tile de pared (#)
│   ├── floor.png               # Tile de suelo (.)
│   ├── breakable_wall.png      # Tile de pared rompible (W)
│   ├── toxic_water.png         # Tile de agua tóxica (~)
│   └── blank.png               # Espacio vacío
├── images/
│   └── hero_background.png     # Imagen de fondo para splash screen
└── sounds/
    ├── shoot.wav               # Efecto de disparo láser
    ├── explosion.wav           # Efecto de explosión de dinamita
    ├── death.wav               # Efecto de muerte del héroe
    ├── splatter.wav            # Efecto de muerte de enemigo
    ├── helicopter.wav          # Sonido del helicóptero (loop)
    ├── walk1.wav               # Sonido de paso 1
    ├── walk2.wav               # Sonido de paso 2
    ├── win_screen.wav          # Sonido de nivel completado
    └── splash_screen_theme.wav # Música del menú principal (loop)
```

## Arquitectura del Código

### Estructura Modular

- **constants.py**: Todas las constantes del juego (dimensiones, físicas, colores, estados, SID)
- **player.py**: Clase Player con física de vuelo, caminata animada y colisiones
- **enemy.py**: Clase Enemy con murciélagos (animación 2 frames) y arañas (verticales con hilo)
- **laser.py**: Clase Laser para proyectiles
- **dynamite.py**: Clase Dynamite con explosiones animadas (3 frames)
- **miner.py**: Clase Miner (objetivo a rescatar)
- **audio_effects.py**: Clase SIDEmulator para efectos de audio estilo Commodore 64
- **hero.py**: Juego principal (Game class, carga de niveles desde JSON, loop)

### Constantes Principales (constants.py)

```python
# Dimensiones y Render Pipeline (dos superficies)
TILE_SIZE = 32
FPS = 60
RENDER_SCALE = 1.5          # Escala de game_surface al screen final

# Viewport: porción visible del nivel (siempre fija)
VIEWPORT_COLS = 16           # tiles visibles horizontalmente
VIEWPORT_ROWS = 8            # tiles visibles verticalmente

# Superficie de juego (derivada del viewport, sin escalar)
GAME_WIDTH = VIEWPORT_COLS * TILE_SIZE             # 512
GAME_VIEWPORT_HEIGHT = VIEWPORT_ROWS * TILE_SIZE   # 256

# Pantalla final (escalada)
SCREEN_WIDTH = int(GAME_WIDTH * RENDER_SCALE)              # 768
VIEWPORT_HEIGHT = int(GAME_VIEWPORT_HEIGHT * RENDER_SCALE)  # 384
HUD_HEIGHT = 80
SCREEN_HEIGHT = VIEWPORT_HEIGHT + HUD_HEIGHT                # 464

# Dimensiones por defecto de nivel (para fallbacks)
DEFAULT_LEVEL_WIDTH = 16    # tiles
DEFAULT_LEVEL_HEIGHT = 24   # tiles
LEVEL_WIDTH = DEFAULT_LEVEL_WIDTH    # Alias legacy (editor)
LEVEL_HEIGHT = DEFAULT_LEVEL_HEIGHT  # Alias legacy (editor)

# Físicas del Juego
GRAVITY = 400              # Gravedad constante
PROPULSOR_POWER = 800      # Poder del propulsor
PLAYER_SPEED_X = 150       # Velocidad horizontal
WALK_STEP_DISTANCE = 16    # Píxeles entre pasos de caminata
MAX_FALL_SPEED = 400       # Velocidad máxima de caída
DIVE_POWER = 600           # Poder de descenso activo

# Láser
LASER_SPEED = 400
LASER_WIDTH = 10
LASER_HEIGHT = 2

# Energía
ENERGY_DRAIN_PROPULSOR = 400  # Energía por segundo al volar
ENERGY_RECOVERY = 300         # Energía recuperada por segundo en el suelo
MAX_ENERGY = 2550

# Dinamita
DYNAMITE_FUSE_TIME = 1.5      # Tiempo antes de explotar
DYNAMITE_EXPLOSION_RADIUS = 80
DYNAMITE_QUANTITY = 5

# Enemigos
BAT_SPEED = 60              # Velocidad horizontal del murciélago
BAT_SPEED_SCALE = 0.05      # +5% por nivel
BAT_ANIM_DISTANCE = 8       # Píxeles entre cambios de sprite
SPIDER_SPEED = 30            # Velocidad vertical de la araña
ENEMY_SPEED_VARIATION = 0.05 # ±5% variación aleatoria por enemigo

# Control
DEAD_ZONE = 0.15

# SID Audio Effects
SID_INTENSITY = 'light'
SID_BITDEPTH = 8
SID_LOWPASS_CUTOFF = 3500
SID_DISTORTION = 0.2
```

### Clase Player (player.py)

**Responsabilidad:** Gestionar el personaje jugable con física realista de helicóptero.

**Atributos:**
- `x`, `y`: Posición en píxeles
- `vel_x`, `vel_y`: Velocidades
- `width`, `height`: Tamaño (32x32)
- `facing_right`: Orientación (sprite base mira a la izquierda)
- `using_propulsor`: Estado del propulsor
- `is_grounded`: Si está parado sobre superficie sólida
- `image`: Sprite idle
- `image_fly`: Sprite de vuelo
- `image_shooting`: Sprite de disparo
- `shooting_timer`: Tiempo restante mostrando sprite de disparo
- `walk_frames`: Lista [walk1, walk2] sprites de caminata
- `walk_sounds`: Lista [walk1, walk2] sonidos de pasos
- `walk_distance`: Distancia acumulada para alternar pasos
- `walk_frame_index`: Frame actual de caminata (0 o 1)
- `is_walking`: Si está caminando

**Métodos:**
- `init(level_map)`: Inicializa posición buscando "S" en el mapa
- `update(dt, keys, joy_axis_x, joy_axis_y, level_map, game)`: Actualiza física y movimiento
- `check_collision(x, y, level_map)`: Verifica colisiones con tiles (#, ., G, R)
- `draw(surface, camera_x, camera_y)`: Renderiza al jugador (prioridad: disparo > vuelo > caminata > idle)
- `get_rect()`: Rectángulo de colisión

**Características:**
- Física con gravedad constante
- Propulsor para volar (mantener presionado, intensidad gradual con joystick)
- Descenso activo con tecla ↓ o joystick abajo (DIVE_POWER)
- Colisión con paredes (#), suelos (.), granito (G) y rocas (R) — bounds dinámicos del mapa
- Movimiento independiente del framerate (delta-time)
- Energía: se drena al volar, se recupera en el suelo (no hay drenaje pasivo)
- Animación de caminata con sonidos alternados cada WALK_STEP_DISTANCE píxeles
- Sprite se voltea (flip) según dirección

### Clase Enemy (enemy.py)

**Responsabilidad:** Enemigos del juego (murciélagos y arañas).

**Tipos:**
- **bat**: Vuela horizontalmente, rebota contra paredes. Animación de 2 frames (bat1/bat2) alternando cada BAT_ANIM_DISTANCE píxeles. Velocidad escala +5% por nivel.
- **spider**: Se mueve verticalmente desde su spawn hasta 2 tiles abajo y vuelve. Dibuja hilo de seda hasta el techo más cercano.

**Atributos:**
- `x`, `y`: Posición actual
- `start_x`, `start_y`: Posición de spawn (para límites de araña)
- `enemy_type`: "bat" o "spider"
- `speed`: Velocidad (BAT_SPEED para bats, SPIDER_SPEED para spiders)
- `direction`: Dirección de movimiento (-1 o 1)
- `active`: Estado activo/inactivo
- `exploding`: En animación de explosión
- `image`: Sprite actual
- `images`: Lista de sprites para animación [bat1, bat2] (solo bats)
- `distance_traveled`: Distancia acumulada para alternar sprites
- `anim_frame`: Frame actual de animación (0 o 1)

**Métodos:**
- `update(dt, level_map)`: Actualiza movimiento y patrullaje
- `check_collision(x, y, level_map)`: Colisión con tiles (#, ., G, R)
- `draw(surface, camera_x, camera_y, level_map)`: Renderiza enemigo, hilo de araña o explosión
- `get_rect()`: Rectángulo de colisión
- `_find_ceiling_y(level_map)`: (privado) Busca techo para hilo de araña

### Clase Laser (laser.py)

**Responsabilidad:** Proyectiles disparados por el jugador.

**Atributos:**
- `x`, `y`: Posición
- `direction`: Dirección (1=derecha, -1=izquierda)
- `width`, `height`: Tamaño (LASER_WIDTH x LASER_HEIGHT = 10x2)
- `active`: Estado activo
- `color`: COLOR_YELLOW

**Métodos:**
- `update(dt, level_map)`: Actualiza posición y colisiones
- `draw(surface, camera_x, camera_y)`: Renderiza láser
- `get_rect()`: Rectángulo de colisión

**Características:**
- Colisiona con paredes (#), suelos (.), granito (G) y rocas (R)
- Se desactiva al salir de límites del nivel
- Sale de la punta del arma del jugador (posición ajustada según dirección)

### Clase Dynamite (dynamite.py)

**Responsabilidad:** Explosivos colocados por el jugador.

**Atributos:**
- `x`, `y`: Posición
- `vel_y`: Velocidad de caída
- `fuse_time`: Tiempo restante antes de explotar (DYNAMITE_FUSE_TIME = 1.5s)
- `exploded`: Estado de explosión
- `explosion_time`: Duración restante de animación (0.5s)
- `active`: Estado activo
- `on_ground`: Si aterrizó
- `width`, `height`: Tamaño (8x16)
- `explosion_sprites`: Lista [bomb1, bomb2, bomb3] para animación

**Métodos:**
- `update(dt, level_map)`: Actualiza caída, colisión con suelo y temporizador
- `check_collision(x, y, level_map)`: Colisión con tiles
- `draw(surface, camera_x, camera_y)`: Renderiza dinamita animada o explosión animada
- `get_explosion_rect()`: Rectángulo de área de explosión

**Características:**
- Cae con gravedad reducida (30% de GRAVITY)
- Se coloca enfrente del héroe según su dirección
- Explota después de 1.5 segundos
- Radio de explosión de DYNAMITE_EXPLOSION_RADIUS píxeles
- Destruye paredes (#), rocas (R) y enemigos (G es indestructible)
- Animación con sprites bomb1/bomb2/bomb3 tanto en cuenta regresiva como en explosión
- Explosión daña al jugador si está en el radio

### Clase Miner (miner.py)

**Responsabilidad:** Minero a rescatar (objetivo del nivel).

**Atributos:**
- `x`, `y`: Posición fija
- `rescued`: Estado de rescate
- `width`, `height`: Tamaño (32x32)
- `image`: Sprite del minero

**Métodos:**
- `draw(surface, camera_x, camera_y)`: Renderiza minero (sprite o fallback con brazos animados)
- `get_rect()`: Rectángulo de colisión

### Clase Game (hero.py)

**Responsabilidad:** Motor principal del juego, gestiona estado global y sistemas.

**Atributos principales:**
- `screen`: Superficie final de composición (768x464)
- `game_surface`: Superficie de juego sin escalar (512x256, 8 tiles visibles)
- `_scaled_game`: Superficie pre-alocada para escalar game_surface (768x384)
- `splash_surface`: Superficie del splash (512x480, tamaño original)
- `display_surface`: Superficie de display real (fullscreen)
- `fullscreen`: Estado de pantalla completa (default: True)
- `render_scale/w/h/x/y`: Parámetros de escalado con aspect ratio
- `clock`: Controlador de FPS
- `xbox_controller`: Input del control (opcional)
- `score`, `level_num`, `lives`, `dynamite_count`, `energy`: Estado del juego
- `player`, `enemies`, `lasers`, `dynamites`, `miner`: Entidades
- `sprites`, `tiles`, `sounds`: Diccionarios de assets
- `background_image`, `gray_overlay`: Splash screen
- `cave_bg`: Fondo de caverna con pintitas generadas proceduralmente
- `camera_x`, `camera_y`: Posición de la cámara en ambos ejes (scrolling 2D)
- `helicopter_playing`, `splash_theme_playing`: Estado de sonidos en loop
- `explosion_flash`: Efecto de flash blanco/negro durante explosiones
- `floating_scores`: Textos flotantes de puntuación
- `level_complete_phase`: Fase de animación ColecoVision (0=energy, 1=bombs, 2=display)
- `show_quit_confirm`: Diálogo de confirmación de salida
- `score_beeps`: Beep sounds pre-generados para animación de score

**Métodos principales:**

1. **`init()`**: Inicializa Pygame, detecta controles, fullscreen por defecto, carga assets
2. **`start_level()`**: Inicia nivel, parsea mapa, crea entidades, genera fondo de caverna
3. **`shoot_laser()`**: Dispara láser con cooldown de 0.2s
4. **`drop_dynamite()`**: Coloca dinamita enfrente del héroe
5. **`update_camera()`**: Cámara suave en ambos ejes que sigue al jugador (lerp 0.1)
6. **`check_collisions()`**: Todas las colisiones (jugador/enemigos/láser/explosión)
7. **`player_hit()`**: Daño al jugador, pierde vida o game over
8. **`rescue_miner()`**: Inicia animación de nivel completado (3 fases)
9. **`update_playing(dt)`**: Actualización del estado PLAYING
10. **`update_level_complete(dt)`**: Animación ColecoVision de 3 fases
11. **`render_level()`**: Renderiza tiles visibles con fondo de caverna (en game_surface)
12. **`render_lamps()`**: Dibuja lámparas en game_surface
13. **`_render_dark_mode_overlay()`**: Modo oscuridad estilo C64 (en game_surface)
14. **`_render_game_to_screen()`**: Escala game_surface (512x256) → screen (768x384)
15. **`render_hud()`**: HUD estilo ColecoVision con paneles grises (en screen)
16. **`render_splash()`**: Splash screen a 512x480 escalado con aspect ratio
17. **`render_entering_name()`**: Pantalla de entrada de nombre
18. **`render_level_complete()`**: Renderiza las 3 fases de level complete
19. **`toggle_fullscreen()`**: Alterna ventana/fullscreen
20. **`add_floating_score()`**: Agrega texto flotante de puntos
21. **`render_floating_scores()`**: Renderiza textos flotantes (en game_surface)
22. **`draw_text_with_outline()`**: Texto con contorno (acepta surface opcional)
23. **`loop()`**: Loop principal del juego

## Sistema de Niveles

### Concepto de Viewport

El **viewport** es la porción visible del nivel: **8 filas x 16 columnas** (VIEWPORT_ROWS x VIEWPORT_COLS = 256x512 px). El viewport es siempre fijo; lo que cambia es el tamaño del nivel.

### Tamaño Dinámico de Niveles

Los niveles pueden tener cualquier tamaño que sea **múltiplo del viewport** en ambos ejes:
- Ancho: múltiplos de 16 columnas (VIEWPORT_COLS)
- Alto: múltiplos de 8 filas (VIEWPORT_ROWS)

Ejemplos: 16x24 (1x3 vp), 32x24 (2x3 vp), 48x32 (3x4 vp), etc.

Las dimensiones se **infieren automáticamente** del mapa cargado (no requieren propiedades explícitas). Si las filas no son múltiplos exactos, se normalizan rellenando con `#`.

### Formato del Mapa

Grid de caracteres con ancho y alto dinámicos (múltiplos del viewport):

- `"S"`: Posición inicial del jugador (Start)
- `"#"`: Tierra (sólida, destructible con dinamita)
- `"."`: Suelo/plataforma (sólido, indestructible)
- `"G"`: Granito (sólido, indestructible)
- `"R"`: Rocas (sólido, destructible con dinamita)
- `" "`: Espacio vacío (aire)
- `"V"`: Enemigo murciélago (bat)
- `"A"`: Enemigo araña (spider)
- `"B"`: Enemigo bicho (bug)
- `"L"`: Lámpara (toggle modo oscuridad al tocar)
- `"~"`: Agua tóxica (mata al jugador al contacto, animada con scroll)
- `"M"`: Minero a rescatar (objetivo)

### Carga de Niveles

Los niveles se cargan desde **screens.json** (no están hardcodeados en hero.py). Cada entrada tiene un campo `"map"` con el array de strings. Las dimensiones se infieren del mapa: ancho = fila más larga, alto = cantidad de filas. Se normalizan al múltiplo de viewport más cercano.

### Dimensiones Dinámicas en el Código

Las clases **NO usan constantes fijas** para el tamaño del nivel. En su lugar, derivan las dimensiones del `level_map` en runtime:
- `level_w = len(level_map[0])` — ancho en tiles
- `level_h = len(level_map)` — alto en tiles

Esto aplica a: `Player.check_collision()`, `Player.update()`, `Enemy.check_collision()`, `Laser.update()`, `Dynamite.check_collision()`, `Game.update_camera()`, `Game.render_level()`, `Game._generate_cave_background()`.

## Loop Principal del Juego

Secuencia de ejecución por frame:

1. Calcular delta-time (dt)
2. Leer input (teclado/control Xbox con zona muerta)
3. Procesar eventos (disparar, dinamita, fullscreen, quit confirm)
4. Según estado:
   - PLAYING: `update_playing(dt)` (jugador, enemigos, láseres, dinamitas, colisiones, cámara, flash)
   - LEVEL_COMPLETE: `update_level_complete(dt)` (3 fases de animación)
5. Gestionar música de splash (play/stop según estado)
6. Limpiar screen
7. Renderizar según estado:
   - SPLASH: render_splash() (512x480 → escala a screen)
   - PLAYING: game_surface → render_level/entidades/dark_mode → _render_game_to_screen() → render_hud()
   - LEVEL_COMPLETE: igual que PLAYING + overlay fase 2
   - ENTERING_NAME: directo en screen
8. Renderizar quit confirm overlay si activo
9. Escalar screen a display con aspect ratio y flip

## Sistema de Input

**Teclado:**
- ←→: Movimiento horizontal
- ↑: Volar (consume energía, intensidad fija)
- ↓: Descenso activo (DIVE_POWER)
- SPACE: Disparar láser
- Z: Colocar dinamita
- ESC: Volver a splash (en juego) / Confirmar salida (en splash)
- Y: Confirmar salida
- Alt+Enter: Alternar fullscreen/ventana
- ENTER: Confirmar nombre
- Alfanuméricos: Escribir nombre (máx 10 caracteres, se pasa a mayúsculas)
- BACKSPACE: Borrar

**Control Xbox:**
- Stick izquierdo: Movimiento (intensidad gradual horizontal y vertical)
- Botón A (0): Iniciar juego
- Botón X (2): Disparar láser
- Botón B (1): Colocar dinamita
- Zona muerta: DEAD_ZONE para evitar drift

## HUD (Heads-Up Display)

Estilo ColecoVision TMS9918A. Posición: parte inferior de la pantalla (HUD_HEIGHT = 80 píxeles).

**Layout:**
- Paneles grises laterales con bisel 3D (70px cada uno)
- Area central con 3 filas:
  1. **POWER** label + barra de energía (amarillo = restante, rojo = gastada)
  2. **Vidas** (iconos de player a la izquierda) + **Bombas** (iconos de bomba a la derecha)
  3. **LEVEL: N** (izquierda) + **Score** (derecha)

**Paleta de colores ColecoVision:**
- Amarillo: (212, 193, 84)
- Rojo: (212, 82, 77)
- Gris: (192, 192, 192)

## Level Complete - Animación ColecoVision

3 fases secuenciales:
1. **Energy drain**: Drenar energía restante a puntos con beeps ascendentes
2. **Bomb explosions**: Explotar bombas restantes una por una (+50 pts cada una)
3. **Display**: Mostrar "LEVEL COMPLETE!" con overlay oscuro por 2 segundos

## Sistema de Sonido

**Efectos implementados:**
- `shoot.wav`: Disparo láser
- `explosion.wav`: Explosión de dinamita y bombas en level complete
- `death.wav`: Muerte del héroe
- `splatter.wav`: Muerte de enemigo (láser o explosión)
- `helicopter.wav`: Loop mientras el jugador está en el aire (no grounded)
- `walk1.wav` / `walk2.wav`: Pasos alternados al caminar
- `win_screen.wav`: Sonido al completar nivel (fase 2)
- `splash_screen_theme.wav`: Música de menú principal (loop)

**Beeps generados proceduralmente:**
- 10 tonos de 400Hz a 1120Hz para animación de score en level complete

**Audio effects (audio_effects.py):**
- Emulación SID de Commodore 64 (bitcrush, lowpass, distorsión)
- Actualmente deshabilitado en el código (comentado)

## Sistema de Puntuación

- **Rescatar minero**: +1000 pts
- **Matar enemigo con láser**: +50 pts
- **Matar enemigo con explosión**: +75 pts
- **Destruir tierra (#) con dinamita**: +20 pts
- **Destruir rocas (R) con dinamita**: +10 pts
- **Energía restante al completar nivel**: se convierte 1:1 en puntos
- **Bombas restantes al completar nivel**: +50 pts cada una
- **Vida extra**: cada 20,000 puntos

**Textos flotantes:** Al ganar puntos aparece un texto amarillo que flota hacia arriba y se desvanece.

## Convenciones de Código

### Estilo

- Clases en PascalCase: `Player`, `Enemy`, `Game`
- Constantes en UPPER_CASE: `TILE_SIZE`, `FPS`
- Métodos en snake_case: `render_level()`, `check_collision()`
- Archivos en snake_case: `constants.py`, `player.py`

### Patrones

- **Separación de responsabilidades**: Cada clase en su archivo
- **Delta-time movement**: Movimiento independiente del framerate
- **Asset management centralizado**: Game class gestiona todos los recursos
- **Coordenadas flotantes**: Cálculos en float, renderizado en int
- **Importación de módulos**: `from constants import *`, `from player import Player`
- **Fallbacks visuales**: Todas las entidades tienen renderizado fallback si falta el sprite

### Renderizado (pipeline de dos superficies)

- **game_surface** (512x256): Toda la lógica de juego se renderiza aquí a escala 1:1 (tiles 32x32). Tamaño fijo = viewport.
- **screen** (768x464): game_surface se escala x1.5 (→768x384) + HUD (80px) se dibuja directo
- **display_surface** (fullscreen): screen se escala manteniendo aspect ratio al monitor
- **splash_surface** (512x480): Splash se renderiza al tamaño original, se escala con aspect ratio al screen
- Orden en game_surface: Fondo caverna → Tiles → Floor texture overlay → Edge/moss overlay → Lámparas → Entidades → Dark overlay → Floating scores
- Orden en screen: game_surface escalado → HUD → Overlays (quit confirm, level complete fase 2)
- Coordenadas de juego: (0,0) esquina superior izquierda del nivel, tiles 32x32
- **Cámara 2D suave**: Sigue al jugador en ambos ejes con lerp 0.1 (usa camera_x y camera_y)
- **Todas las entidades reciben camera_x y camera_y** en sus métodos draw() para offset de renderizado
- Solo se renderizan tiles visibles en el viewport (culling en ambos ejes para eficiencia)

## Sistema de Texturas del Suelo y Musgo (palette.py)

Ambos sistemas viven en **palette.py** y generan superficies SRCALPHA del tamaño completo del nivel, que se pre-computan una vez al cargar el nivel (`start_level()`) y se blitean por viewport en `render_level()`. Se regeneran cuando la dinamita destruye tiles (para reflejar el nuevo mapa).

### Textura Porosa del Suelo (floor_texture)

**Función:** `generate_floor_texture(level_map, seed)` → superficie SRCALPHA

Genera un overlay con "hoyos" oscuros sobre cada tile de suelo (`.`) para darle un aspecto cavernoso y poroso. Solo afecta tiles de suelo, nunca paredes ni espacios vacíos.

**Capas de detalle por tile (3 tipos):**
1. **Franjas horizontales** (`FLOOR_STREAKS`): Líneas oscuras alargadas (5-9 por tile, ancho 6-18px, alto 1-3px). Simulan grietas o vetas en la roca.
2. **Manchas irregulares** (`FLOOR_BLOBS`): Parches más grandes y cuadrados (3-7 por tile, ancho 3-10px, alto 2-5px). Dan textura irregular.
3. **Poros pequeños** (`FLOOR_DOTS`): Puntos individuales de 1-2px (15-25 por tile). Detalle fino granular.

**Colores:** Tonos oscuros casi negros definidos en `_HOLE_COLORS` (negro puro, marrón muy oscuro). Se aplican con alta opacidad (200-230 alpha) para simular profundidad.

**Constantes en palette.py:**
```python
FLOOR_STREAKS = (5, 9)       # Cantidad de franjas por tile
FLOOR_STREAK_W = (6, 18)     # Ancho de franjas en px
FLOOR_STREAK_H = (1, 3)      # Alto de franjas en px
FLOOR_BLOBS = (3, 7)         # Cantidad de manchas por tile
FLOOR_BLOB_W = (3, 10)       # Ancho de manchas en px
FLOOR_BLOB_H = (2, 5)        # Alto de manchas en px
FLOOR_DOTS = (15, 25)        # Cantidad de poros por tile
```

**Importante:** Todos los píxeles se clampean a los límites del tile individual (`px <= bx < px + TILE_SIZE`) para que la textura no se escape a tiles adyacentes.

### Overlay de Musgo/Raíces (edge_overlay)

**Función:** `generate_edge_overlay(level_map, edge_color, seed)` → superficie SRCALPHA

Genera vegetación decorativa en los bordes expuestos de tiles de suelo (`.`). Solo crece donde un tile sólido tiene un vecino vacío (aire).

**Tipos de crecimiento:**
- **Stalactitas** (`_draw_moss_down`): Cuelgan de la cara inferior del suelo hacia abajo. Largo máximo: `MOSS_MAX_DOWN` (14px). Aparecen cuando el tile de abajo es vacío.
- **Stalagmitas** (`_draw_moss_up`): Crecen desde la cara superior del suelo hacia arriba. Largo máximo: `MOSS_MAX_UP` (12px). Aparecen cuando el tile de arriba es vacío.

**Anatomía de cada borde:**
1. **Banda base**: Línea sólida de `MOSS_BASE_H` (2px) de grosor pegada al borde del tile. Tiene huecos aleatorios (15% de probabilidad) para no ser uniforme.
2. **Dentado irregular**: Generado por `_jagged_heights()` — alturas variables con clusters (grupos de alturas similares), gaps (zonas bajas), y picos largos ocasionales (6% de probabilidad). Da aspecto orgánico.
3. **Tendriles finos**: 1-3 hilos extra que se extienden más allá del dentado principal, con alpha decreciente para efecto de desvanecimiento.

**Color:** Configurable por nivel via `edge_color` en screens.json. Default: verde musgo `[80, 180, 60]`. Se aplica variación aleatoria de ±8 por canal RGB a cada píxel para dar textura. El alpha decrece hacia las puntas (240→80) para un efecto de transparencia gradual.

**Constantes en palette.py:**
```python
MOSS_BASE_H = 2        # Grosor base del borde sólido
MOSS_MAX_DOWN = 14     # Largo máximo de stalactitas
MOSS_MAX_UP = 12       # Largo máximo de stalagmitas
```

### Pipeline de Renderizado de Suelo

El suelo (`.`) se renderiza en 3 capas superpuestas:
1. **Tile base tintado** (`tinted_floors`): Tile floor.png tintado según la profundidad (fila del viewport). Construido por `build_tinted_floors()`.
2. **Floor texture overlay** (`floor_texture`): Hoyos oscuros porosos encima del tile. Se blitea después de todos los tiles.
3. **Edge/moss overlay** (`edge_overlay`): Musgo/raíces en bordes expuestos. Se blitea último.

Las 3 capas se generan en `start_level()` y se regeneran tras destrucción con dinamita (llamando `_generate_edge_overlay()` y `_generate_floor_texture()`).

## Cómo Modificar el Juego

### Ajustar Físicas del Jugador

Editar **constants.py**:

```python
PROPULSOR_POWER = 800  # Aumentar para subir más fácil
GRAVITY = 400          # Reducir para caída más lenta
PLAYER_SPEED_X = 150   # Aumentar para mover más rápido
DIVE_POWER = 600       # Poder de descenso activo
```

### Ajustar Energía

Editar **constants.py**:

```python
ENERGY_DRAIN_PROPULSOR = 400  # Drenaje al volar por segundo
ENERGY_RECOVERY = 300         # Recuperación en el suelo por segundo
MAX_ENERGY = 2550             # Energía total
```

### Añadir un Nuevo Enemigo

1. Crear sprite en `sprites/nuevo_enemigo.png`
2. Cargar en `Game.init()` (hero.py):
   ```python
   self.sprites["nuevo_enemigo"] = pygame.image.load("sprites/nuevo_enemigo.png").convert_alpha()
   ```
3. Añadir símbolo al mapa en screens.json (ej: "N")
4. Añadir a TILE_TYPES en constants.py
5. Parsear en `Game.start_level()` (hero.py):
   ```python
   elif tile == "N":
       enemy = Enemy(x, y, "nuevo_tipo")
       enemy.image = self.sprites["nuevo_enemigo"]
       self.enemies.append(enemy)
   ```
6. Añadir lógica en `Enemy.update()` (enemy.py) si es necesario

### Crear Nuevos Niveles

Editar **screens.json** o usar el **editor visual** (`python editor.py`).

Cada nivel es un objeto con un campo `"map"` que contiene un array de strings. Las dimensiones son libres pero se normalizan a múltiplos del viewport (8 filas x 16 columnas):
- Un nivel de 16x24 tiene filas de 16 caracteres y 24 filas (1x3 viewports)
- Un nivel de 32x24 tiene filas de 32 caracteres y 24 filas (2x3 viewports)
- Las dimensiones se infieren automáticamente del mapa (no requieren propiedades explícitas)

El editor permite agregar/quitar viewports con Ctrl+Flechas.

## Recursos y Referencias

- [Pygame Documentation](https://www.pygame.org/docs/)
- [H.E.R.O. Original (Atari)](https://en.wikipedia.org/wiki/H.E.R.O._(video_game))
- Fuente: Press Start 2P (Google Fonts)

## Notas para Claude

- **Siempre leer los archivos modulares** antes de sugerir cambios
- **Mantener la estructura modular** - No fusionar clases de vuelta a hero.py
- **Respetar delta-time** para movimientos
- **No romper la compatibilidad** con control Xbox
- **Probar cambios** considerando FPS=60
- **No usar magic numbers** - Todo valor numérico debe ser una constante con nombre en constants.py
- **Usar las constantes** de constants.py, no hardcodear valores
- **Comentarios en español** (es el idioma del desarrollador)
- **Los suelos (.) son sólidos** - Igual que las paredes (#)
- **Tiles sólidos para colisión**: #, ., G, R
- **Tiles destructibles con dinamita**: # (tierra), R (rocas). G (granito) es indestructible
- **Renderizado de juego en game_surface** - Entidades dibujan en game_surface, NO en self.screen
- **Cámara 2D (camera_x, camera_y)** - Scrolling en ambos ejes, usar GAME_VIEWPORT_HEIGHT (256) y GAME_WIDTH (512) para el viewport
- **Niveles de tamaño dinámico** - NO usar LEVEL_WIDTH/LEVEL_HEIGHT para bounds check. Usar `len(level_map[0])` y `len(level_map)` en su lugar
- **Viewport fijo** - VIEWPORT_COLS=16, VIEWPORT_ROWS=8. Los niveles son múltiplos de este tamaño
- **Niveles en screens.json** - No hardcodear niveles en hero.py
- **Entidades reciben camera_x y camera_y** - Todos los métodos draw() usan (camera_x, camera_y) para offset
- **Sprites con fondo transparente** - Todo sprite generado debe usar `pygame.SRCALPHA` y fondo transparente

---

*Última actualización: 2026-03-09*
