# H.E.R.O. Remake

## Helicopter Emergency Rescue Operation

Un remake completo del clásico juego de Atari 2600 H.E.R.O., desarrollado en Python con Pygame.

## Descripción

Controla a Roderick Hero, equipado con un helicóptero personal, mientras navegas por minas subterráneas peligrosas para rescatar mineros atrapados. Enfrenta enemigos, destruye obstáculos y administra tu energía para completar los 5 niveles progresivamente más difíciles.

## Características Implementadas

### ✅ Sistema Completo de Juego

- **5 Niveles Únicos** con dificultad progresiva
- **Pantalla de Inicio (Splash Screen)** con los top 3 high scores
- **Sistema de Puntuación Persistente** guardado en JSON
- **Pantalla de Game Over** con entrada de nombre para registrar tu score
- **Física Realista** con gravedad y vuelo con helicóptero
- **Sistema de Energía** que disminuye constantemente
- **Sistema de Vidas** con vida extra cada 20,000 puntos
- **Efectos de Sonido** para disparos y explosiones

### 🎮 Mecánicas de Juego

#### Movimiento
- **Vuelo con Helicóptero**: Presiona arriba para volar (consume energía extra)
- **Gravedad**: El jugador cae cuando no está volando
- **Movimiento Horizontal**: Izquierda/Derecha para moverse

#### Combate
- **Disparo Láser**: Destruye enemigos y bloques
- **Dinamita**: Explosiones de área grande que destruyen múltiples bloques y enemigos

#### Enemigos
- **Murciélagos Voladores**: Patrullan horizontalmente
- **Movimiento Inteligente**: Cambian de dirección al chocar con paredes
- **Velocidad Variable**: Aumenta la dificultad en niveles superiores

#### Peligros
- **Magma** (desde nivel 5): Paredes ardientes que matan al contacto
- **Energía Limitada**: Se agota con el tiempo y al volar
- **Colisiones**: Con enemigos y paredes

### 🎯 Objetivos

1. **Encuentra al Minero** (marcado con 'R' en los mapas)
2. **Rescata al Minero** tocándolo con tu helicóptero
3. **Completa los 5 Niveles** para ganar el juego

### 💯 Sistema de Puntuación

- **Destruir Enemigo con Láser**: 100 puntos
- **Destruir Enemigo con Dinamita**: 150 puntos
- **Destruir Bloque con Láser**: 50 puntos
- **Destruir Bloque con Dinamita**: 25 puntos por bloque
- **Rescatar Minero**: 1000 puntos base
- **Bonus de Energía Restante**: 10 puntos por unidad de energía
- **Bonus de Bombas Restantes**: 100 puntos por bomba

**Vida Extra**: Obtienes una vida adicional cada 20,000 puntos acumulados.

## Controles

### Teclado

| Tecla | Acción |
|-------|--------|
| **←→** | Mover izquierda/derecha |
| **↑** | Volar hacia arriba (consume energía) |
| **SPACE** | Disparar láser |
| **↓ + CTRL** | Colocar dinamita |
| **ESC** | Salir del juego (en menú) |
| **ENTER** | Confirmar nombre (en game over) |

### Control Xbox/Gamepad

| Botón/Stick | Acción |
|------------|--------|
| **Stick Izquierdo** | Mover en todas direcciones |
| **Botón A** | Iniciar juego (en menú) |
| **Botón X** | Disparar láser |
| **Botón B** | Colocar dinamita |

## Niveles

### Nivel 1 - Tutorial
- Nivel simple e introductorio
- Pocos enemigos (2)
- Un bloque destructible
- Ideal para aprender las mecánicas

### Nivel 2 - Descenso Vertical
- Diseño vertical con descenso
- 4 enemigos distribuidos
- Pasajes estrechos
- Requiere manejo preciso del vuelo

### Nivel 3 - Laberinto Horizontal
- Diseño abierto y horizontal
- 5 enemigos
- Múltiples bloques destructibles (BBB)
- Requiere estrategia de navegación

### Nivel 4 - Estructura Compleja
- Diseño intrincado con múltiples caminos
- 4 enemigos en posiciones estratégicas
- Bloques destructibles en áreas clave
- Alta dificultad de navegación

### Nivel 5 - Nivel de Magma
- **PELIGRO**: Paredes de magma letales
- 3 enemigos
- Bloques destructibles cerca del magma
- Requiere precisión extrema
- El nivel más difícil

## HUD (Heads-Up Display)

### Información Mostrada

```
┌─────────────────────────────────────────────────┐
│ SCORE: 12500        LIVES: 3    ENERGY [████  ] │
│ LVL: 3              BOMBS: 5                     │
└─────────────────────────────────────────────────┘
```

- **SCORE**: Puntuación actual
- **LVL**: Nivel actual (1-5)
- **LIVES**: Vidas restantes
- **BOMBS**: Dinamita restante
- **ENERGY**: Barra de energía visual
  - Verde: >30% energía
  - Amarilla: 15-30% energía
  - Roja: <15% energía

## Instalación y Ejecución

### Requisitos

```bash
Python 3.8+
pygame 2.0+
```

### Instalación

```bash
# Instalar dependencias
pip install pygame

# Ejecutar el juego
python hero.py
```

### Estructura de Archivos

```
hero/
├── hero.py              # Juego principal (TODO incluido)
├── scores.json          # High scores (generado automáticamente)
├── README.md            # Este archivo
├── CLAUDE.md            # Documentación técnica
├── fonts/
│   └── PressStart2P-vaV7.ttf
├── sprites/
│   ├── player.png       # (Opcional, usa gráficos generados)
│   ├── enemy.png
│   └── bomb.png
├── tiles/
│   ├── wall.png         # (Opcional, usa gráficos generados)
│   ├── floor.png
│   └── blank.png
└── sounds/
    ├── explosion.wav    # (Opcional)
    └── shoot.wav
```

**Nota**: El juego funciona sin los archivos de sprites/tiles/sounds. Genera gráficos procedurales si no encuentra las imágenes.

## Sistema de High Scores

### Persistencia
- Los scores se guardan automáticamente en `scores.json`
- Se mantienen los top 10 scores
- Los top 3 se muestran en la pantalla de inicio

### Formato JSON
```json
[
  {
    "name": "PLAYER1",
    "score": 50000
  },
  {
    "name": "PLAYER2",
    "score": 35000
  }
]
```

## Tips y Estrategias

### Conservar Energía
- ⚡ La energía se agota constantemente
- ⚡⚡ Volar consume el doble de energía
- Usa la gravedad a tu favor para descender
- Planifica tu ruta antes de volar

### Uso de Dinamita
- La dinamita tiene área de efecto grande
- Útil para destruir múltiples bloques
- Puede eliminar varios enemigos a la vez
- Espera 2 segundos antes de explotar

### Combate
- Los disparos láser tienen cooldown corto (0.3s)
- Enemigos patrullan horizontalmente
- Dispara desde distancia segura
- Usa dinamita para grupos de enemigos

### Nivel de Magma (5)
- ⚠️ NO toques las paredes naranjas/rojas
- Muerte instantánea al contacto con magma
- Vuelo preciso es esencial
- Conserva energía para el final

### Puntuación Alta
- Rescata rápido para conservar energía
- Bonus por energía restante al rescatar
- Conserva bombas para bonus adicional
- Destruye todos los enemigos posibles

## Leyenda del Mapa

| Símbolo | Significado |
|---------|-------------|
| `S` | Start - Posición inicial del jugador |
| `#` | Pared sólida (gris) |
| `.` | Suelo transitable (marrón) |
| `B` | Bloque destructible (marrón claro) |
| `E` | Enemigo - Murciélago |
| `R` | Rescue - Minero a rescatar (verde) |
| `M` | Magma - Pared letal (naranja/rojo) |
| ` ` | Espacio vacío (negro) |

## Créditos

### Juego Original
- **H.E.R.O.** (1984) por Activision
- Diseñado por John Van Ryzin
- Plataforma original: Atari 2600

### Este Remake
- Desarrollado con Python y Pygame
- Remake completo y jugable
- 5 niveles diseñados desde cero
- Sistema de scores moderno

## Tecnología

- **Lenguaje**: Python 3
- **Framework**: Pygame 2.6.1
- **Gráficos**: Procedurales con Pygame.draw
- **Audio**: Pygame.mixer
- **Persistencia**: JSON
- **Input**: Teclado + Xbox Controller

## Futuras Mejoras Posibles

- [ ] Más niveles (6-20 como el original)
- [ ] Sprites personalizados mejorados
- [ ] Más tipos de enemigos (serpientes, arañas)
- [ ] Sistema de power-ups
- [ ] Música de fondo
- [ ] Modo de dificultad seleccionable
- [ ] Leaderboard online
- [ ] Animaciones mejoradas

## Licencia

Este es un proyecto educativo y de fan remake. H.E.R.O. es propiedad de Activision.

## Contacto y Contribuciones

¿Encontraste un bug? ¿Tienes sugerencias? ¡Contribuciones bienvenidas!

---

**¡Disfruta salvando mineros!** 🚁⛏️

**Objetivo: Rescatar a todos los mineros y convertirte en H.E.R.O.!**
