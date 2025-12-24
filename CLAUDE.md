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
├── hero.py                      # Archivo principal del juego (877 líneas)
├── constants.py                 # Constantes del juego (52 líneas)
├── player.py                    # Clase Player (141 líneas)
├── enemy.py                     # Clase Enemy (89 líneas)
├── laser.py                     # Clase Laser (40 líneas)
├── dynamite.py                  # Clase Dynamite (60 líneas)
├── miner.py                     # Clase Miner (36 líneas)
├── CLAUDE.md                    # Este archivo
├── IMPLEMENTATION_SUMMARY.md    # Resumen de implementación
├── fonts/
│   └── PressStart2P-vaV7.ttf   # Fuente estilo retro
├── sprites/
│   ├── player.png              # Sprite del jugador
│   ├── enemy.png               # Sprite de enemigo
│   ├── spider.png              # Variante araña
│   ├── miner.png               # Sprite del minero rescatado
│   └── bomb.png                # Power-up de bomba
├── tiles/
│   ├── wall.png                # Tile de pared
│   ├── floor.png               # Tile de suelo
│   └── blank.png               # Espacio vacío
└── sounds/
    ├── explosion.wav           # Efecto de explosión
    ├── shoot.wav               # Efecto de disparo
    ├── death.wav               # Efecto de muerte del héroe
    └── helicopter.wav          # Sonido del helicóptero (opcional)
```

## Arquitectura del Código

### Estructura Modular

El proyecto está organizado en módulos separados para mejor mantenibilidad:

- **constants.py**: Todas las constantes del juego (dimensiones, físicas, colores, estados)
- **player.py**: Clase Player con física de vuelo y colisiones
- **enemy.py**: Clase Enemy con comportamiento de murciélagos y arañas
- **laser.py**: Clase Laser para proyectiles
- **dynamite.py**: Clase Dynamite con explosiones
- **miner.py**: Clase Miner (objetivo a rescatar)
- **hero.py**: Juego principal (Game class, niveles, loop)

### Constantes Principales (constants.py)

```python
# Dimensiones
SCREEN_WIDTH = 512
SCREEN_HEIGHT = 480
FPS = 60
TILE_SIZE = 32

# Físicas del Juego
GRAVITY = 400              # Gravedad constante
PROPULSOR_POWER = 800      # Poder del propulsor (ajustable)
PLAYER_SPEED_X = 150       # Velocidad horizontal
MAX_FALL_SPEED = 400       # Velocidad máxima de caída
LASER_SPEED = 400          # Velocidad del láser

# Energía
ENERGY_DRAIN_PASSIVE = 7   # Drenaje pasivo por segundo
ENERGY_DRAIN_PROPULSOR = 40 # Drenaje al volar por segundo
MAX_ENERGY = 2550          # Energía máxima

# Dinamita
DYNAMITE_FUSE_TIME = 3.0   # Tiempo antes de explotar
DYNAMITE_EXPLOSION_RADIUS = 80

# Control
DEAD_ZONE = 0.15           # Zona muerta del joystick
```

### Clase Player (player.py)

**Responsabilidad:** Gestionar el personaje jugable con física realista de helicóptero.

**Atributos:**
- `x`, `y`: Posición en píxeles
- `vel_x`, `vel_y`: Velocidades
- `width`, `height`: Tamaño (32x32)
- `facing_right`: Orientación
- `using_propulsor`: Estado del propulsor
- `image`: Sprite cargado

**Métodos principales:**
- `init(level_map)`: Inicializa posición buscando "S" en el mapa
- `update(dt, keys, joy_axis_x, joy_axis_y, level_map, game)`: Actualiza física y movimiento
- `check_collision(x, y, level_map)`: Verifica colisiones con tiles
- `draw(screen, camera_y)`: Renderiza al jugador

**Características:**
- Física con gravedad constante
- Propulsor para volar (mantener presionado)
- Colisión con paredes (#), suelos (.) y bloques (B)
- Movimiento independiente del framerate (delta-time)
- Drenaje de energía pasivo y activo

### Clase Enemy (enemy.py)

**Responsabilidad:** Enemigos del juego (murciélagos y arañas).

**Tipos:**
- **bat**: Vuela horizontalmente con oscilación vertical
- **spider**: Camina sobre el suelo

**Atributos:**
- `x`, `y`: Posición
- `enemy_type`: "bat" o "spider"
- `speed`: Velocidad (40 para bats, 30 para spiders)
- `direction`: Dirección de movimiento (-1 o 1)
- `active`: Estado activo/inactivo
- `exploding`: En animación de explosión
- `image`: Sprite cargado

**Métodos:**
- `update(dt, level_map)`: Actualiza movimiento y patrullaje
- `draw(screen, camera_y)`: Renderiza enemigo o explosión
- `get_rect()`: Obtiene rectángulo de colisión

**Comportamiento:**
- Patrullaje horizontal automático
- Rebote contra paredes (#), suelos (.) y bloques (B)
- Cambio de dirección al llegar a límites
- Animación de explosión al morir

### Clase Laser (laser.py)

**Responsabilidad:** Proyectiles disparados por el jugador.

**Atributos:**
- `x`, `y`: Posición
- `direction`: Dirección (1=derecha, -1=izquierda)
- `width`, `height`: Tamaño (16x4)
- `active`: Estado activo
- `color`: Color amarillo

**Métodos:**
- `update(dt, level_map)`: Actualiza posición y colisiones
- `draw(screen, camera_y)`: Renderiza láser
- `get_rect()`: Rectángulo de colisión

**Características:**
- Colisiona con paredes (#) y suelos (.)
- Se desactiva al salir de límites
- Velocidad constante

### Clase Dynamite (dynamite.py)

**Responsabilidad:** Explosivos colocados por el jugador.

**Atributos:**
- `x`, `y`: Posición
- `vel_y`: Velocidad de caída
- `fuse_time`: Tiempo restante antes de explotar
- `exploded`: Estado de explosión
- `explosion_time`: Duración de animación
- `active`: Estado activo

**Métodos:**
- `update(dt)`: Actualiza caída y temporizador
- `draw(screen, camera_y)`: Renderiza dinamita o explosión
- `get_explosion_rect()`: Rectángulo de área de explosión

**Características:**
- Cae con gravedad reducida
- Explota después de 3 segundos
- Radio de explosión de 80 píxeles
- Destruye bloques (B) y enemigos

### Clase Miner (miner.py)

**Responsabilidad:** Minero a rescatar (objetivo del nivel).

**Atributos:**
- `x`, `y`: Posición fija
- `rescued`: Estado de rescate
- `width`, `height`: Tamaño (32x32)
- `image`: Sprite del minero

**Métodos:**
- `draw(screen, camera_y)`: Renderiza minero (sprite o fallback)
- `get_rect()`: Rectángulo de colisión

**Características:**
- Sprite de pixel art con casco amarillo, camisa azul, pantalones grises
- Brazos levantados pidiendo ayuda
- Colisión con jugador completa el nivel

### Clase Game (hero.py)

**Responsabilidad:** Motor principal del juego, gestiona estado global y sistemas.

**Atributos de Estado:**
- `screen`: Superficie de Pygame
- `clock`: Controlador de FPS
- `xbox_controller`: Input del control (opcional)
- `score`: Puntuación actual
- `level_num`: Nivel actual (0-4)
- `lives`: Vidas del jugador (default: 5)
- `dynamite_count`: Cantidad de dinamita (default: 6)
- `energy`: Energía actual
- `player`: Instancia de Player
- `enemies`: Lista de enemigos
- `lasers`: Lista de láseres activos
- `dynamites`: Lista de dinamitas activas
- `miner`: Instancia de Miner
- `sprites`: Diccionario de sprites cargados
- `tiles`: Diccionario de tiles cargados
- `sounds`: Diccionario de sonidos cargados

**Métodos principales:**

1. **`init()`**: Inicializa Pygame, detecta controles Xbox, configura pantalla, carga assets
2. **`start_level()`**: Inicia un nuevo nivel, crea entidades
3. **`shoot_laser()`**: Dispara un láser
4. **`drop_dynamite()`**: Coloca dinamita
5. **`update_camera()`**: Actualiza cámara para seguir al jugador
6. **`check_collisions()`**: Verifica todas las colisiones
7. **`player_hit()`**: Maneja daño al jugador, reproduce sonido de muerte
8. **`rescue_miner()`**: Completa el nivel al rescatar
9. **`render_level()`**: Renderiza tiles visibles
10. **`render_hud()`**: Dibuja HUD con stats
11. **`render_splash()`**: Pantalla de inicio
12. **`render_entering_name()`**: Pantalla de entrada de nombre
13. **`render_level_complete()`**: Pantalla de nivel completado
14. **`loop()`**: Loop principal del juego

## Sistema de Niveles

### Formato del Mapa

Grid de 16 columnas × 30 filas usando caracteres:

- `"S"`: Posición inicial del jugador (Start)
- `"#"`: Pared sólida (indestructible)
- `"."`: Suelo/plataforma (sólido, transitable)
- `" "`: Espacio vacío (aire)
- `"E"`: Enemigo murciélago (bat)
- `"A"`: Enemigo araña (spider)
- `"B"`: Bloque destructible (solo con dinamita)
- `"M"`: Minero a rescatar (objetivo)

### Niveles Implementados

**5 niveles únicos** con dificultad progresiva (líneas 458-623 en hero.py):
1. Tutorial simple
2. Más enemigos
3. Laberinto estrecho
4. Muchos bloques
5. Nivel difícil

## Loop Principal del Juego

Secuencia de ejecución por frame:

1. Calcular delta-time (dt)
2. Leer input (teclado/control Xbox)
3. Procesar eventos (disparar, dinamita, cerrar)
4. Actualizar jugador (física, colisiones)
5. Actualizar enemigos (patrullaje)
6. Actualizar láseres y dinamitas
7. Verificar colisiones
8. Actualizar cámara
9. Limpiar pantalla
10. Renderizar nivel (tiles)
11. Renderizar entidades (miner, enemigos, láseres, dinamitas, jugador)
12. Renderizar HUD
13. Actualizar display

## Sistema de Input

**Teclado:**
- ←→: Movimiento horizontal
- ↑: Volar (consume energía)
- SPACE: Disparar láser
- ↓ o CTRL: Colocar dinamita
- ESC: Salir (en menú)
- ENTER: Confirmar nombre
- Alfanuméricos: Escribir nombre
- BACKSPACE: Borrar

**Control Xbox:**
- Stick izquierdo: Movimiento
- Botón A: Iniciar juego
- Botón X: Disparar láser
- Botón B: Colocar dinamita
- Zona muerta: 0.15 para evitar drift

## HUD (Heads-Up Display)

Posición: Parte inferior de la pantalla (últimos 64 píxeles)

**Elementos:**
- SCORE (izquierda superior)
- LVL (izquierda inferior)
- LIVES (centro-izquierda superior)
- BOMBS (centro-izquierda inferior)
- ENERGY (derecha) - Barra visual con colores dinámicos
  - Verde: >30%
  - Amarillo: 15-30%
  - Rojo: <15%

## Sistema de Sonido

**Efectos implementados:**
- `shoot.wav`: Disparo láser
- `explosion.wav`: Explosión de dinamita
- `death.wav`: Muerte del héroe (grito/crash descendente)
- `helicopter.wav`: Sonido del propulsor (opcional, loop)

**Características:**
- Reproducción automática en eventos
- Manejo de errores si faltan archivos
- Loop de helicóptero mientras se vuela

## Estado Actual del Desarrollo

### ✅ COMPLETAMENTE IMPLEMENTADO Y JUGABLE

- ✅ **Arquitectura modular** - Clases en archivos separados
- ✅ **Movimiento completo del jugador** con física de vuelo y gravedad
- ✅ **Sistema de disparo láser** con cooldown
- ✅ **Sistema de dinamita** con explosiones de área
- ✅ **Lógica completa de enemigos** con patrullaje inteligente (bats y spiders)
- ✅ **5 niveles únicos** con dificultad progresiva
- ✅ **Sistema de colisiones completo**
  - Jugador vs enemigos, paredes, suelos, bloques
  - Láser vs enemigos, paredes, suelos
  - Explosión vs enemigos y bloques
- ✅ **Sistema de puntuación** completo con bonificaciones
- ✅ **Pantalla splash** con high scores (top 3)
- ✅ **Pantalla de game over** con entrada de nombre
- ✅ **Sistema de persistencia** de scores en JSON
- ✅ **Medidor de energía** que disminuye con el tiempo
- ✅ **Sistema de vidas** con vida extra cada 20,000 puntos
- ✅ **Progresión completa** de niveles
- ✅ **Efectos de sonido** (shoot, explosion, death, helicopter)
- ✅ **HUD completo** con stats visuales
- ✅ **Renderizado de nivel** basado en tiles con cámara vertical
- ✅ **Soporte completo** para control Xbox y teclado
- ✅ **Sistema de rescate** de mineros con sprite pixel art
- ✅ **Estados del juego** (SPLASH, PLAYING, LEVEL_COMPLETE, ENTERING_NAME)
- ✅ **Tiles de suelo sólidos** - Los tiles "." funcionan como plataformas

### 🎮 El Juego está 100% Funcional y Jugable

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

### Renderizado

- Orden: Fondo → Nivel → Entidades → HUD → Flip
- Coordenadas: (0,0) es esquina superior izquierda
- Sistema de tiles: 32×32 píxeles
- Cámara vertical: Sigue al jugador en eje Y

## Cómo Modificar el Juego

### Ajustar Físicas del Jugador

Editar **constants.py**:

```python
PROPULSOR_POWER = 800  # Aumentar para subir más fácil
GRAVITY = 400          # Reducir para caída más lenta
PLAYER_SPEED_X = 150   # Aumentar para mover más rápido
```

### Ajustar Drenaje de Energía

Editar **constants.py**:

```python
ENERGY_DRAIN_PASSIVE = 7    # Drenaje base
ENERGY_DRAIN_PROPULSOR = 40 # Drenaje al volar
MAX_ENERGY = 2550           # Energía total
```

### Añadir un Nuevo Enemigo

1. Crear sprite en `sprites/nuevo_enemigo.png`
2. Cargar en `Game.init()` (hero.py):
   ```python
   self.sprites["nuevo_enemigo"] = pygame.image.load("sprites/nuevo_enemigo.png")
   ```
3. Añadir símbolo al mapa (ej: "N")
4. Parsear en `Game.start_level()` (hero.py):
   ```python
   elif tile == "N":
       enemy = Enemy(x, y, "nuevo_tipo")
       enemy.image = self.sprites["nuevo_enemigo"]
       self.enemies.append(enemy)
   ```
5. Añadir lógica en `Enemy.update()` (enemy.py) si es necesario

### Crear Nuevos Niveles

Editar el array `LEVELS` en **hero.py** (líneas 458-623):

```python
LEVELS.append([
    "################",
    "#  S           #",
    "#      E       #",
    "#              #",
    "#       M      #",
    "#..............#",
    "################",
    # ... 23 filas más (total 30)
])
```

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
- **Usar las constantes** de constants.py, no hardcodear valores
- **Comentarios en español** (es el idioma del desarrollador)
- **Los suelos (.) son sólidos** - Igual que las paredes (#)

## Archivos de Documentación

- **CLAUDE.md**: Este archivo - Documentación técnica para desarrollo
- **IMPLEMENTATION_SUMMARY.md**: Resumen completo de implementación y características
- **README.md**: Guía del usuario (si existe)

---

*Última actualización: 2025-12-24*
*Generado con Claude Sonnet 4.5*
