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
├── hero.py                      # Archivo principal del juego (311 líneas)
├── CLAUDE.md                    # Este archivo
├── fonts/
│   └── PressStart2P-vaV7.ttf   # Fuente estilo retro
├── sprites/
│   ├── player.png              # Sprite del jugador
│   ├── enemy.png               # Sprite de enemigo
│   ├── spider.png              # Variante araña
│   └── bomb.png                # Power-up de bomba
├── tiles/
│   ├── wall.png                # Tile de pared
│   ├── floor.png               # Tile de suelo
│   └── blank.png               # Espacio vacío
└── sounds/
    ├── explosion.wav           # Efecto de explosión
    └── shoot.wav               # Efecto de disparo
```

## Arquitectura del Código

### Constantes Globales

```python
SCREEN_WIDTH = 512      # Ancho de pantalla
SCREEN_HEIGHT = 480     # Alto de pantalla
FPS = 60                # Frames por segundo
TILE_SIZE = 32          # Tamaño de cada tile (32x32)
PLAYER_SPEED = 200      # Velocidad del jugador (píxeles/segundo)
DEAD_ZONE = 0.1         # Zona muerta del control
```

### Clase `Player` (líneas 38-101)

**Responsabilidad:** Gestionar el personaje jugable.

**Atributos:**
- `image`: Sprite del jugador
- `x`, `y`: Posición en coordenadas de pantalla

**Métodos principales:**
- `__init__()`: Carga el sprite del jugador
- `init(game_map)`: Inicializa posición buscando "S" en el mapa
- `compute_movement(dt, axis_0, axis_1)`: Calcula movimiento basado en input del control
- `update(screen)`: Actualiza posición y dibuja, respeta límites de pantalla

**Características:**
- Movimiento suave usando delta-time
- Colisión con bordes de pantalla
- Soporte para control Xbox

### Clase `Enemy` (líneas 105-116)

**Responsabilidad:** Representar enemigos en el juego.

**Estado actual:** Implementación mínima (placeholder).

**Atributos:**
- `image`: Sprite del enemigo
- `x`, `y`: Posición
- `speed`: Velocidad (20 unidades)

**Métodos:**
- `__init__(x, y)`: Inicializa enemigo
- `update(dt, screen)`: Actualiza y renderiza (NO IMPLEMENTADO)

**TODO:** Implementar lógica de movimiento y comportamiento.

### Clase `Game` (líneas 122-291)

**Responsabilidad:** Motor principal del juego, gestiona estado global y sistemas.

**Atributos de Estado:**
- `screen`: Superficie de Pygame
- `clock`: Controlador de FPS
- `xbox_controller`: Input del control (opcional)
- `score`: Puntuación actual (default: 0)
- `level`: Nivel actual (default: 0)
- `bombs`: Cantidad de bombas (default: 3)
- `lives`: Vidas del jugador (default: 5)
- `player`: Instancia de Player
- `enemies`: Lista de enemigos
- `sprites`: Diccionario de sprites cargados
- `tiles`: Diccionario de tiles cargados

**Métodos principales:**

1. **`init()`**: Inicializa Pygame, detecta controles Xbox, configura pantalla
2. **`load_assets()`**: Carga todas las imágenes, fuentes y sonidos
3. **`render_level(level_map)`**: Parsea mapas y crea enemigos
4. **`render_hud()`**: Dibuja HUD con score, nivel, bombas, vidas
5. **`loop()`**: Loop principal del juego

## Sistema de Niveles

### Formato del Mapa

Grid de 16 columnas × 15 filas usando caracteres:

- `"S"`: Posición inicial del jugador (Start)
- `"#"`: Pared sólida
- `"."`: Suelo transitable
- `" "`: Espacio vacío
- `"E"`: Punto de spawn de enemigo
- `"R"`: Tile especial rojo (posible objetivo/boss)

### Estructura MAPS

```python
MAPS = [
    [
        "################",
        "S...............#",
        ...
    ]
]
```

## Loop Principal del Juego

Secuencia de ejecución por frame:

1. Limpiar pantalla (negro)
2. Renderizar nivel (tiles)
3. Calcular delta-time (dt)
4. Leer input del control Xbox con filtro de zona muerta
5. Actualizar movimiento del jugador
6. Actualizar todos los enemigos
7. Renderizar HUD
8. Actualizar display

## Sistema de Input

**Control Xbox:**
- Stick izquierdo: Movimiento del jugador
- Botón A: Debug print (sin acción asignada)
- Zona muerta: 0.1 para evitar drift

**Teclado:**
- Solo eventos de ventana (cerrar)

## HUD (Heads-Up Display)

Posición: Parte inferior de la pantalla

**Elementos:**
- Score (izquierda)
- Level (centro-izquierda)
- Bombs con icono (centro-derecha)
- Lives con icono (derecha)
- Fondo semi-transparente (alpha=128)

## Estado Actual del Desarrollo

### ✅ COMPLETAMENTE IMPLEMENTADO Y JUGABLE

- ✅ Movimiento completo del jugador con física de vuelo y gravedad
- ✅ Sistema de disparo láser con cooldown
- ✅ Sistema de dinamita con explosiones de área
- ✅ Lógica completa de enemigos con patrullaje inteligente
- ✅ 5 niveles únicos con dificultad progresiva
- ✅ Sistema de colisiones (jugador-enemigo, bala-enemigo, bala-bloque, explosión)
- ✅ Sistema de puntuación completo con bonificaciones
- ✅ Pantalla splash con high scores (top 3)
- ✅ Pantalla de game over con entrada de nombre
- ✅ Sistema de persistencia de scores en JSON
- ✅ Medidor de energía que disminuye con el tiempo
- ✅ Sistema de vidas con vida extra cada 20,000 puntos
- ✅ Tiles de magma mortales (nivel 5)
- ✅ Progresión completa de niveles
- ✅ Integración de efectos de sonido (shoot.wav, explosion.wav)
- ✅ HUD completo con score, nivel, vidas, bombas y barra de energía
- ✅ Renderizado de nivel basado en tiles
- ✅ Soporte completo para control Xbox y teclado
- ✅ Sistema de rescate de mineros
- ✅ Estados del juego (SPLASH, PLAYING, LEVEL_COMPLETE, ENTERING_NAME)

### 🎮 El Juego está 100% Funcional y Jugable

## Convenciones de Código

### Estilo

- Clases en PascalCase: `Player`, `Enemy`, `Game`
- Constantes en UPPER_CASE: `TILE_SIZE`, `FPS`
- Métodos en snake_case: `render_level()`, `compute_movement()`

### Patrones

- **Separación de responsabilidades**: Cada clase tiene un propósito específico
- **Delta-time movement**: Movimiento independiente del framerate
- **Asset management centralizado**: Game class gestiona todos los recursos
- **Coordenadas flotantes**: Cálculos en float, renderizado en int

### Renderizado

- Orden: Fondo → Nivel → Entidades → HUD → Flip
- Coordenadas: (0,0) es esquina superior izquierda
- Sistema de tiles: 32×32 píxeles

## Historial de Desarrollo (Git)

```
2350a6d 'hud'                    # ← ÚLTIMO
7378297 changes
6e83da6 reorganizacion en clases
588529e intentando poner orden
c6abad9 render level
```

## Cómo Contribuir

### Añadir un Nuevo Enemigo

1. Crear sprite en `sprites/`
2. Cargar en `load_assets()`:
   ```python
   self.sprites["nuevo_enemigo"] = pygame.image.load("sprites/nuevo_enemigo.png")
   ```
3. Añadir símbolo al mapa (ej: "N")
4. Parsear en `render_level()`:
   ```python
   elif cell == "N":
       self.enemies.append(NuevoEnemigo(x, y))
   ```
5. Crear clase heredando de Enemy o como clase nueva

### Implementar Colisiones

**Jugador vs Paredes:**
```python
# En Player.update(), antes de actualizar posición:
tile_x = int(self.x / TILE_SIZE)
tile_y = int(self.y / TILE_SIZE)
if MAPS[game.level][tile_y][tile_x] == "#":
    # Revertir movimiento
```

**Jugador vs Enemigos:**
```python
# En Game.loop(), después de update():
for enemy in self.enemies:
    if self.player.colisiona_con(enemy):
        self.player_hit()
```

### Añadir Sistema de Disparos

1. Crear clase `Bullet`
2. Lista `self.bullets` en Game
3. Input de disparo en loop
4. Actualizar y renderizar bullets
5. Colisiones bullet-enemy

## Próximos Pasos Sugeridos

1. **Implementar lógica de enemigos** (Enemy.update())
2. **Sistema de colisiones** (jugador-pared, jugador-enemigo)
3. **Mecánicas de bomba** (lanzar, explotar, destruir paredes)
4. **Sistema de disparos**
5. **Progresión de niveles** (cargar MAPS[self.level])
6. **Sistema de puntuación** (incrementar score)
7. **Game Over y victoria**
8. **Integrar efectos de sonido**
9. **Menú principal**
10. **Más niveles en MAPS[]**

## Recursos y Referencias

- [Pygame Documentation](https://www.pygame.org/docs/)
- [H.E.R.O. Original (Atari)](https://en.wikipedia.org/wiki/H.E.R.O._(video_game))
- Fuente: Press Start 2P (Google Fonts)

## Notas para Claude

- **Siempre leer hero.py antes de sugerir cambios**
- **Mantener consistencia con el sistema de tiles actual**
- **Respetar delta-time para movimientos**
- **No romper la compatibilidad con control Xbox**
- **Probar cambios considerando FPS=60**
- **Usar las constantes globales existentes**
- **Comentarios en español (es el idioma del desarrollador)**

---

*Última actualización: 2025-12-23*
*Generado con Claude Sonnet 4.5*
