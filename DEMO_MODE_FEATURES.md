# H.E.R.O. - Modo Demo y Pantalla de Fondo

## Nuevas Características Implementadas

### ✅ Pantalla de Inicio con Imagen de Fondo

**Características:**
- Imagen de fondo semi-transparente (alpha=100) en la pantalla splash
- Generación automática de imagen procedural al primer inicio
- La imagen muestra el nivel 1 con jugador, enemigo y minero
- Archivo: `hero_background.png` (18KB)

**Implementación:**
- Si no existe `hero_background.png`, se genera automáticamente
- La imagen se carga al iniciar el juego
- Se muestra con transparencia detrás del menú principal

### ✅ Modo Demo Automático

**Características:**
- IA simple que juega automáticamente
- Se activa después de 3 segundos en la pantalla splash (si no hay imagen de fondo)
- Se activa después de 3 segundos en la pantalla splash (si ya hay imagen de fondo)
- Juega en bucle infinito los niveles 0 y 1
- Muestra "DEMO MODE - Press any key to play" en overlay amarillo

**Comportamiento de la IA:**

1. **Navegación:**
   - Se mueve hacia el minero automáticamente
   - Vuela cuando el minero está arriba o cuando está cayendo rápido
   - Controla la dirección hacia el objetivo

2. **Combate:**
   - Dispara a enemigos cercanos (< 150 píxeles)
   - Verifica que el enemigo esté en la misma altura (±50 píxeles)
   - Cooldown de 1 segundo entre disparos

3. **Destrucción:**
   - Usa dinamita cerca de bloques destructibles
   - Solo si está lejos del minero (> 100 píxeles)
   - Verifica bloques en tiles adyacentes

### ✅ Interacción con el Demo

**Salir del Demo:**
- Presionar cualquier tecla → Vuelve al splash screen
- Presionar cualquier botón del control → Vuelve al splash screen
- El timer del splash se reinicia a 3 segundos

**Iniciar Juego desde Splash:**
- Presionar SPACE o botón A → Inicia juego normal
- El timer del demo se reinicia

### ✅ Loop del Demo

**Flujo:**
1. Splash screen (3 segundos) → Demo automático
2. Demo juega nivel 1
3. Rescata minero → Transición (1 segundo)
4. Demo juega nivel 2
5. Rescata minero → Vuelve al nivel 1
6. **Loop infinito** hasta que el usuario presione una tecla

**Condiciones de Reinicio:**
- Si el jugador muere (energía = 0)
- Si el jugador pierde todas las vidas
- El demo se reinicia automáticamente

## Nuevo Estado del Juego

```
STATE_DEMO = "demo"
```

**Estados del Juego Actualizados:**
- `STATE_SPLASH` → Menú principal con fondo
- `STATE_DEMO` → Modo demo activo
- `STATE_PLAYING` → Juego normal
- `STATE_LEVEL_COMPLETE` → Transición de nivel
- `STATE_ENTERING_NAME` → Entrada de nombre
- `STATE_GAME_OVER` → (implícito)

## Configuración

```python
# Demo settings
DEMO_LEVELS = [0, 1]  # Demo plays levels 0 and 1
DEMO_SWITCH_TIME = 3.0  # Time to show splash before starting demo
SCREENSHOT_FILE = "hero_background.png"
```

## Nuevas Clases

### DemoAI (líneas 170-234)

```python
class DemoAI:
    """Simple AI to play the game automatically in demo mode"""
    def __init__(self):
        self.shoot_timer = 0
        self.shoot_cooldown = 1.0

    def update(self, dt, player, miner, enemies, game):
        """Calculate AI input for demo mode"""
        # Returns: (move_x, move_y, shoot, use_dynamite)
```

**Métodos:**
- `update()`: Calcula el input de la IA basado en el estado del juego

## Nuevos Métodos de Game

### load_background()
Carga la imagen de fondo o la crea si no existe.

### create_procedural_background()
Genera una imagen procedural del nivel 1 con elementos del juego.

### start_demo()
Inicializa el modo demo con niveles específicos.

### update_demo(dt)
Actualiza el juego en modo demo usando la IA.

### capture_screenshot()
Captura una screenshot del estado actual del juego.

## Modificaciones en Métodos Existentes

### Player.update()
- Nuevo parámetro: `ai_input=None`
- Acepta input de la IA en modo demo
- `ai_input = (move_x, move_y, shoot, dynamite)`

### Game.update_level_complete()
- Maneja transición especial para modo demo
- Loop entre niveles 0 y 1
- Timer más corto (1 segundo vs 2 segundos)

### Game.rescue_miner()
- Detecta si está en modo demo
- Ajusta timer de transición

### Game.render_splash()
- Dibuja imagen de fondo con transparencia
- Superpone menú sobre el fondo

## Flujo de Renderizado del Demo

```
1. render_level() → Dibuja tiles del nivel
2. Draw entities → Minero, enemigos, balas, dinamita
3. Draw player → Jugador controlado por IA
4. render_hud() → HUD completo
5. Demo overlay → Barra negra con texto amarillo
```

## Estadísticas de la Implementación

- **Líneas agregadas:** ~200
- **Clases nuevas:** 1 (DemoAI)
- **Métodos nuevos:** 4 (load_background, create_procedural_background, start_demo, update_demo)
- **Métodos modificados:** 5
- **Nuevo estado:** STATE_DEMO
- **Archivo generado:** hero_background.png (18KB)

## Comportamiento del Fondo

### Primera Ejecución:
1. No existe `hero_background.png`
2. Se genera imagen procedural automáticamente
3. Muestra nivel 1 con jugador, enemigo y minero
4. Se guarda para futuras ejecuciones

### Ejecuciones Posteriores:
1. Carga `hero_background.png` existente
2. Lo muestra en splash screen
3. Demo se activa después de 3 segundos

### Reemplazo del Fondo:
- Para generar nuevo fondo: Eliminar `hero_background.png`
- El juego lo recreará al siguiente inicio
- O dejarlo ejecutar en demo por 3+ segundos (actualmente deshabilitado para usar fondo procedural)

## Debugging

**Mensajes de Consola:**
```
"Creating procedural background image..."
"Created and saved procedural background: hero_background.png"
"Loaded background image: hero_background.png"
"No background image found, will generate from demo..."
"Taking screenshot at X.Xs, score=Y"
"Screenshot saved: hero_background.png"
```

## Controles en Modo Demo

| Acción | Resultado |
|--------|-----------|
| Presionar cualquier tecla | Vuelve al splash |
| Presionar cualquier botón | Vuelve al splash |
| ESC (en splash) | Sale del juego |
| SPACE/A (en splash) | Inicia juego normal |

## Características Técnicas

### IA del Demo:
- **Pathfinding:** Simple dirección hacia objetivo
- **Combate:** Detección de enemigos por distancia y ángulo
- **Supervivencia:** Vuelo automático para evitar caídas
- **Destrucción:** Búsqueda de bloques en área 3×3

### Rendimiento:
- Sin impacto en FPS
- IA actualizada a 60 Hz
- Transiciones suaves entre estados

### Compatibilidad:
- Funciona con teclado y control
- No interfiere con controles normales
- Estado independiente del juego principal

## Mejoras Futuras Posibles

- [ ] IA más inteligente (evita enemigos)
- [ ] Múltiples fondos aleatorios
- [ ] Captura de screenshot en momento óptimo durante demo
- [ ] Fade in/out en transiciones
- [ ] Texto animado en demo overlay
- [ ] Estadísticas del demo (tiempo jugado, score alcanzado)
- [ ] Diferentes niveles para el demo
- [ ] Música de fondo en demo

## Testing

**Pruebas Realizadas:**
- ✅ Generación de fondo procedural
- ✅ Carga de fondo existente
- ✅ IA navega hacia minero
- ✅ IA dispara a enemigos
- ✅ Loop entre 2 niveles funciona
- ✅ Transición a splash al presionar tecla
- ✅ Transición a juego desde splash
- ✅ Demo se reinicia al morir

**Resultado:** Todas las funcionalidades operativas.

---

## Resumen

Se ha implementado exitosamente:
1. ✅ **Imagen de fondo ilustrativa** en pantalla de inicio
2. ✅ **Modo demo automático** con IA jugable
3. ✅ **Loop de 2 niveles** (0 y 1) en el demo
4. ✅ **Generación automática de fondo** procedural
5. ✅ **Interacción fluida** entre splash y demo

El juego ahora ofrece una experiencia completa de demostración que se activa automáticamente, mostrando las mecánicas del juego a nuevos jugadores mientras esperan en el menú principal.

---

*Implementado el 2025-12-23*
*Desarrollado con Claude Sonnet 4.5*
