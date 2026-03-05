# H.E.R.O. Remake

## Helicopter Emergency Rescue Operation

Un remake del clasico juego de Atari 2600 H.E.R.O., desarrollado en Python con Pygame.

## Descripcion

Controla a Roderick Hero, equipado con un helicoptero personal, mientras navegas por minas subterraneas peligrosas para rescatar mineros atrapados. Enfrenta enemigos, destruye obstaculos y administra tu energia para completar los 5 niveles progresivamente mas dificiles.

## Caracteristicas

### Sistema de Juego

- **5 Niveles** cargados desde archivo externo (`screens.json`), editables con el editor incluido
- **Pantalla de Inicio** con imagen de fondo, musica de tema y top 3 high scores
- **Sistema de Puntuacion Persistente** guardado en JSON (top 10)
- **Pantalla de Game Over** con entrada de nombre para registrar score
- **Fisica Realista** con gravedad, vuelo con helicoptero y descenso activo
- **Sistema de Energia** que se consume al volar y se recupera al estar en el suelo
- **Sistema de Vidas** con vida extra cada 20,000 puntos
- **Efectos de Sonido** completos (disparos, explosiones, muerte, helicoptero, pasos, victoria, splatter)
- **HUD estilo ColecoVision** con paneles 3D, iconos de vidas y bombas
- **Pantalla Completa** por defecto con escalado manteniendo aspect ratio (Alt+Enter para alternar)
- **Confirmacion de Salida** con dialogo Y/N
- **Fondo de Caverna** procedural con textura de roca
- **Puntuaciones Flotantes** que aparecen al destruir enemigos y bloques
- **Animacion de Nivel Completo** en 3 fases estilo ColecoVision
- **Emulacion de Audio SID** (Commodore 64) disponible para efectos de sonido
- **Editor de Niveles** incluido (`editor.py`)

### Mecanicas de Juego

#### Movimiento
- **Vuelo con Helicoptero**: Presiona arriba para volar (consume energia)
- **Descenso Activo**: Presiona abajo para bajar mas rapido (helice invertida)
- **Caminata Animada**: Al moverse en el suelo, con pasos alternados y sonido
- **Gravedad**: El jugador cae cuando no esta volando
- **Recuperacion de Energia**: La energia se recupera automaticamente al estar en el suelo

#### Combate
- **Disparo Laser**: Destruye enemigos y colisiona con paredes/bloques
- **Dinamita**: Explosiones de area que destruyen bloques, paredes y enemigos cercanos

#### Enemigos
- **Murcielagos** (V): Patrullan horizontalmente, rebotan contra paredes. Velocidad aumenta por nivel (+5%)
- **Aranas** (A): Se mueven verticalmente desde el techo, colgando de un hilo. Descienden hasta 2 tiles y vuelven

#### Efectos Visuales
- **Flash de Explosion**: La pantalla parpadea blanco/negro durante explosiones de dinamita
- **Animacion de Explosion**: Sprites animados (bomb1, bomb2, bomb3) para dinamita
- **Sprites de Jugador**: Idle, volando, disparando y caminando (2 frames)
- **Hilo de Arana**: Linea blanca que conecta la arana con el techo

### Objetivos

1. **Encuentra al Minero** (M) en cada nivel
2. **Rescata al Minero** tocandolo
3. **Completa los 5 Niveles** para ganar el juego

### Sistema de Puntuacion

| Accion | Puntos |
|--------|--------|
| Destruir enemigo con laser | 50 |
| Destruir enemigo con dinamita | 75 |
| Destruir tierra (#) con dinamita | 20 |
| Destruir rocas (R) con dinamita | 10 |
| Rescatar minero | 1,000 |
| Bonus energia restante | 1:1 (se drena en animacion) |
| Bonus bombas restantes | 50 por bomba |

**Vida Extra**: Obtienes una vida adicional cada 20,000 puntos acumulados.

## Controles

### Teclado

| Tecla | Accion |
|-------|--------|
| **Flechas izq/der** | Mover izquierda/derecha |
| **Flecha arriba** | Volar hacia arriba (consume energia) |
| **Flecha abajo** | Descenso rapido (helice invertida) |
| **SPACE** | Disparar laser |
| **Z** | Colocar dinamita |
| **ESC** | Volver al menu (en juego) / Salir (en menu, con confirmacion) |
| **ALT+ENTER** | Alternar pantalla completa/ventana |
| **ENTER** | Confirmar nombre (en game over) |

### Control Xbox/Gamepad

| Boton/Stick | Accion |
|------------|--------|
| **Stick Izquierdo** | Mover (gradual, con zona muerta) |
| **Boton A** | Iniciar juego (en menu) |
| **Boton X** | Disparar laser |
| **Boton B** | Colocar dinamita |

## Niveles

Los niveles se cargan desde `screens.json` y pueden editarse con `editor.py`.

### Nivel 1 - Tutorial: Rescate con dinamita
- Nivel introductorio con rocas destructibles
- 2 murcielagos y 1 arana
- Rocas (R) y tierra (#) destructibles, granito (G) indestructible
- Minero encerrado en una seccion inferior

### Nivel 2 - Minero encerrado
- Diseño vertical con secciones separadas por plataformas
- Multiples murcielagos y aranas distribuidos
- Minero encerrado detras de bloques destructibles
- Requiere manejo preciso del vuelo y dinamita

### Nivel 3 - Laberinto estrecho
- Pasajes estrechos con secciones bloqueadas
- Navegacion compleja entre secciones
- Bloques destructibles en puntos clave

### Nivel 4 - Muchos bloques
- Capas horizontales de bloques destructibles
- Requiere uso intensivo de dinamita
- Aranas y murcielagos entre capas

### Nivel 5 - Dificil
- Combinacion de pasajes estrechos y bloques
- Multiples secciones verticales
- Alta dificultad de navegacion

## Animacion de Nivel Completo

Al rescatar al minero, se ejecuta una animacion en 3 fases:

1. **Drenaje de Energia**: La energia restante se convierte en puntos 1:1, con beeps ascendentes
2. **Explosion de Bombas**: Las bombas restantes explotan una por una en el HUD, sumando 50 puntos cada una
3. **Pantalla de Victoria**: Overlay oscuro con "LEVEL COMPLETE!" y sonido de victoria

## HUD (Heads-Up Display)

HUD estilo ColecoVision TMS9918A con paneles grises 3D en los laterales:

```
+--------+------------------------------------+--------+
| Panel  | POWER [================          ] | Panel  |
| gris   | [vida][vida][vida]    [bomba][bomba]| gris   |
|        | LEVEL: 1                     12500  |        |
+--------+------------------------------------+--------+
```

- **POWER**: Barra de energia (amarillo=llena, rojo=vacia)
- **Vidas**: Iconos del jugador en miniatura
- **Bombas**: Iconos de bomba alineados a la derecha
- **LEVEL**: Numero de nivel actual
- **Score**: Puntuacion alineada a la derecha

## Instalacion y Ejecucion

### Requisitos

```
Python 3.8+
pygame 2.0+
numpy (opcional, para emulacion SID)
```

### Instalacion

```bash
# Instalar dependencias
pip install pygame numpy

# Ejecutar el juego
python hero.py

# Ejecutar el editor de niveles
python editor.py
```

### Estructura de Archivos

```
hero/
├── hero.py                  # Juego principal (Game class, loop, render)
├── constants.py             # Constantes del juego
├── player.py                # Clase Player (fisica, animacion, caminata)
├── enemy.py                 # Clase Enemy (murcielagos y aranas)
├── laser.py                 # Clase Laser (proyectiles)
├── dynamite.py              # Clase Dynamite (explosivos con sprites animados)
├── miner.py                 # Clase Miner (objetivo a rescatar)
├── audio_effects.py         # Emulacion SID de Commodore 64
├── editor.py                # Editor de niveles visual
├── screens.json             # Definicion de niveles (editable)
├── scores.json              # High scores (generado automaticamente)
├── CLAUDE.md                # Documentacion tecnica para desarrollo
├── README.md                # Este archivo
├── fonts/
│   └── PressStart2P-vaV7.ttf
├── images/
│   └── hero_background.png  # Fondo de pantalla de inicio
├── sprites/
│   ├── player.png           # Sprite idle del jugador
│   ├── player_fly.png       # Sprite volando
│   ├── player_shooting.png  # Sprite disparando
│   ├── player_walk1.png     # Animacion de caminata frame 1
│   ├── player_walk2.png     # Animacion de caminata frame 2
│   ├── bat1.png             # Sprite de murcielago frame 1
│   ├── bat2.png             # Sprite de murcielago frame 2
│   ├── spider.png           # Sprite de arana
│   ├── miner.png            # Sprite del minero
│   ├── bomb1.png            # Animacion de bomba frame 1
│   ├── bomb2.png            # Animacion de bomba frame 2
│   └── bomb3.png            # Animacion de bomba frame 3
├── tiles/
│   ├── wall.png             # Tierra (#)
│   ├── floor.png            # Suelo/plataforma (.)
│   ├── granite.png          # Granito indestructible (G)
│   ├── breakable_wall.png   # Rocas destructibles (R)
│   ├── lamp.png             # Lampara (L)
│   └── blank.png            # Espacio vacio
└── sounds/
    ├── shoot.wav            # Efecto de disparo
    ├── explosion.wav        # Efecto de explosion
    ├── death.wav            # Efecto de muerte
    ├── splatter.wav         # Efecto de muerte de enemigo
    ├── helicopter.wav       # Sonido del helicoptero (loop)
    ├── walk1.wav            # Paso izquierdo
    ├── walk2.wav            # Paso derecho
    ├── win_screen.wav       # Sonido de nivel completo
    └── splash_screen_theme.wav  # Musica del menu principal
```

El juego genera graficos procedurales como fallback si no encuentra las imagenes.

## Sistema de High Scores

### Persistencia
- Los scores se guardan automaticamente en `scores.json`
- Se mantienen los top 10 scores
- Los top 3 se muestran en la pantalla de inicio

## Leyenda del Mapa

| Simbolo | Significado |
|---------|-------------|
| `S` | Start - Posicion inicial del jugador |
| `#` | Tierra (solida, destructible con dinamita) |
| `.` | Suelo/plataforma (solido, indestructible) |
| `G` | Granito (solido, indestructible) |
| `R` | Rocas (solido, destructible con dinamita) |
| `V` | Enemigo - Murcielago (patrulla horizontal) |
| `A` | Enemigo - Arana (se mueve verticalmente con hilo) |
| `L` | Lampara (toggle modo oscuridad al tocar) |
| `M` | Minero a rescatar (objetivo del nivel) |
| ` ` | Espacio vacio (fondo de caverna) |

## Tips y Estrategias

### Conservar Energia
- La energia se consume al volar con el propulsor
- Se recupera automaticamente al estar parado en el suelo
- Usa la gravedad y el descenso activo (flecha abajo) para bajar rapido sin gastar energia
- Planifica tu ruta antes de volar

### Uso de Dinamita
- La dinamita explota en 1.5 segundos
- Area de efecto de 80 pixeles de radio
- Destruye tierra (#) y rocas (R). No destruye granito (G) ni suelo (.)
- Puede eliminar varios enemigos a la vez
- Cuidado: la explosion tambien daña al jugador

### Combate
- Los disparos laser tienen cooldown corto (0.2s)
- El laser colisiona con paredes, suelos y bloques (no los destruye)
- Dispara desde distancia segura
- Las aranas se mueven verticalmente, los murcielagos horizontalmente

### Puntuacion Alta
- Rescata rapido para conservar energia (se convierte en puntos)
- Conserva bombas para bonus adicional (50 pts cada una)
- Destruye todos los enemigos posibles

## Editor de Niveles

Ejecuta `python editor.py` para abrir el editor visual de niveles. Permite crear y modificar los niveles guardados en `screens.json`.

## Creditos

### Juego Original
- **H.E.R.O.** (1984) por Activision
- Diseñado por John Van Ryzin
- Plataforma original: Atari 2600

### Este Remake
- Desarrollado con Python y Pygame
- Arquitectura modular con clases separadas
- 5 niveles editables con editor incluido
- HUD estilo ColecoVision
- Emulacion de audio SID

## Tecnologia

- **Lenguaje**: Python 3.13
- **Framework**: Pygame 2.6.1
- **Audio**: Pygame.mixer + emulacion SID (Commodore 64)
- **Graficos**: Sprites PNG + generacion procedural (fallback)
- **Persistencia**: JSON (scores y niveles)
- **Input**: Teclado + Xbox Controller (con joystick gradual)

## Futuras Mejoras Posibles

- [ ] Mas niveles (6-20 como el original)
- [ ] Animar murcielagos (alas)
- [ ] Tiles de fondo decorativos
- [x] Lamparas que al tocar apagan la luz
- [ ] Serpientes que salen desde la cueva
- [ ] Enemigos que vibran en el lugar
- [ ] Bloques y nivel de magma

## Licencia

Este es un proyecto educativo y de fan remake. H.E.R.O. es propiedad de Activision.
