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
├── hero.py                      # Archivo principal del juego (~1255 líneas)
├── constants.py                 # Constantes del juego (~90 líneas)
├── player.py                    # Clase Player (~208 líneas)
├── enemy.py                     # Clase Enemy (~166 líneas)
├── laser.py                     # Clase Laser (~51 líneas)
├── dynamite.py                  # Clase Dynamite (~112 líneas)
├── miner.py                     # Clase Miner (~37 líneas)
├── audio_effects.py             # Emulación SID de Commodore 64 (numpy)
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
# Dimensiones
SCREEN_WIDTH = 512
SCREEN_HEIGHT = 480
FPS = 60
TILE_SIZE = 32

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
BAT_SPEED = 52              # Velocidad horizontal del murciélago
BAT_SPEED_SCALE = 0.05      # +5% por nivel
BAT_ANIM_DISTANCE = 16      # Píxeles entre cambios de sprite
SPIDER_SPEED = 30            # Velocidad vertical de la araña

# Control
DEAD_ZONE = 0.15

# Nivel
LEVEL_WIDTH = 16   # tiles
LEVEL_HEIGHT = 30  # tiles

# Viewport
HUD_HEIGHT = 80
VIEWPORT_HEIGHT = SCREEN_HEIGHT - HUD_HEIGHT

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
- `check_collision(x, y, level_map)`: Verifica colisiones con tiles (#, B, ., W)
- `draw(screen, camera_y)`: Renderiza al jugador (prioridad: disparo > vuelo > caminata > idle)
- `get_rect()`: Rectángulo de colisión

**Características:**
- Física con gravedad constante
- Propulsor para volar (mantener presionado, intensidad gradual con joystick)
- Descenso activo con tecla ↓ o joystick abajo (DIVE_POWER)
- Colisión con paredes (#), suelos (.), bloques (B) y rompibles (W)
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
- `check_collision(x, y, level_map)`: Colisión con tiles (#, B, ., W)
- `draw(screen, camera_y, level_map)`: Renderiza enemigo, hilo de araña o explosión
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
- `draw(screen, camera_y)`: Renderiza láser
- `get_rect()`: Rectángulo de colisión

**Características:**
- Colisiona con paredes (#), suelos (.), bloques (B) y rompibles (W)
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
- `draw(screen, camera_y)`: Renderiza dinamita animada o explosión animada
- `get_explosion_rect()`: Rectángulo de área de explosión

**Características:**
- Cae con gravedad reducida (30% de GRAVITY)
- Se coloca enfrente del héroe según su dirección
- Explota después de 1.5 segundos
- Radio de explosión de DYNAMITE_EXPLOSION_RADIUS píxeles
- Destruye bloques (B), paredes (#), rompibles (W) y enemigos
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
- `draw(screen, camera_y)`: Renderiza minero (sprite o fallback con brazos animados)
- `get_rect()`: Rectángulo de colisión

### Clase Game (hero.py)

**Responsabilidad:** Motor principal del juego, gestiona estado global y sistemas.

**Atributos principales:**
- `screen`: Superficie de renderizado (512x480)
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
- `camera_y`: Posición vertical de la cámara
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
5. **`update_camera()`**: Cámara suave que sigue al jugador (lerp 0.1)
6. **`check_collisions()`**: Todas las colisiones (jugador/enemigos/láser/explosión)
7. **`player_hit()`**: Daño al jugador, pierde vida o game over
8. **`rescue_miner()`**: Inicia animación de nivel completado (3 fases)
9. **`update_playing(dt)`**: Actualización del estado PLAYING
10. **`update_level_complete(dt)`**: Animación ColecoVision de 3 fases
11. **`render_level()`**: Renderiza tiles visibles con fondo de caverna
12. **`render_hud()`**: HUD estilo ColecoVision con paneles grises
13. **`render_splash()`**: Splash screen con imagen de fondo
14. **`render_entering_name()`**: Pantalla de entrada de nombre
15. **`render_level_complete()`**: Renderiza las 3 fases de level complete
16. **`toggle_fullscreen()`**: Alterna ventana/fullscreen
17. **`add_floating_score()`**: Agrega texto flotante de puntos
18. **`render_floating_scores()`**: Renderiza textos flotantes
19. **`draw_text_with_outline()`**: Texto con contorno para splash
20. **`loop()`**: Loop principal del juego

## Sistema de Niveles

### Formato del Mapa

Grid de 16 columnas x 30 filas (LEVEL_WIDTH x LEVEL_HEIGHT) usando caracteres:

- `"S"`: Posición inicial del jugador (Start)
- `"#"`: Pared sólida (destructible con dinamita)
- `"."`: Suelo/plataforma (sólido, transitable)
- `" "`: Espacio vacío (aire)
- `"V"`: Enemigo murciélago (bat)
- `"A"`: Enemigo araña (spider)
- `"B"`: Bloque destructible (solo con dinamita)
- `"W"`: Pared rompible (destructible con dinamita)
- `"M"`: Minero a rescatar (objetivo)

### Carga de Niveles

Los niveles se cargan desde **screens.json** (no están hardcodeados en hero.py). Cada entrada tiene un campo `"map"` con el array de strings. Las dimensiones se normalizan automáticamente a LEVEL_WIDTH x LEVEL_HEIGHT.

## Loop Principal del Juego

Secuencia de ejecución por frame:

1. Calcular delta-time (dt)
2. Leer input (teclado/control Xbox con zona muerta)
3. Procesar eventos (disparar, dinamita, fullscreen, quit confirm)
4. Según estado:
   - PLAYING: `update_playing(dt)` (jugador, enemigos, láseres, dinamitas, colisiones, cámara, flash)
   - LEVEL_COMPLETE: `update_level_complete(dt)` (3 fases de animación)
5. Gestionar música de splash (play/stop según estado)
6. Limpiar pantalla
7. Renderizar según estado (splash/playing/level_complete/entering_name)
8. Renderizar quit confirm overlay si activo
9. Escalar a display con aspect ratio y flip

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
- **Destruir pared (#) con dinamita**: +20 pts
- **Destruir bloque (B/W) con dinamita**: +10 pts
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

### Renderizado

- Fullscreen por defecto con escalado manteniendo aspect ratio
- Render a superficie interna (512x480), luego escala al display
- Orden: Fondo caverna → Tiles → Entidades → Floating scores → HUD → Flip
- Coordenadas: (0,0) es esquina superior izquierda
- Sistema de tiles: 32x32 píxeles
- Cámara vertical suave: Sigue al jugador en eje Y con lerp

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

Editar **screens.json**. Cada nivel es un objeto con un campo `"map"` que contiene un array de 30 strings de 16 caracteres. Las dimensiones se normalizan automáticamente.

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
- **Tiles sólidos para colisión**: #, B, ., W
- **Niveles en screens.json** - No hardcodear niveles en hero.py

---

*Última actualización: 2026-02-25*
