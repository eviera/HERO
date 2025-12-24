"""
Tests para verificar que los enemigos no atraviesan paredes, bloques ni pisos
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from enemy import Enemy
from constants import *

def create_test_map_with_walls():
    """Crea un mapa con paredes a los lados"""
    return [
        "################",  # Row 0
        "#              #",  # Row 1 - pasillo con paredes
        "#              #",  # Row 2
        "################",  # Row 3
    ]

def create_test_map_with_blocks():
    """Crea un mapa con bloques destructibles"""
    return [
        "                ",  # Row 0
        "      B  B      ",  # Row 1 - bloques
        "                ",  # Row 2
    ]

def create_test_map_with_floor():
    """Crea un mapa con piso"""
    return [
        "                ",  # Row 0
        "      ...       ",  # Row 1 - piso
        "                ",  # Row 2
    ]

def test_enemy_stops_at_wall():
    """Test 1: El enemigo debe rebotar en paredes (#)"""
    print("Test 1: Enemigo rebota en pared (#)...")

    enemy = Enemy(60, 50, "bat")  # Crear murciélago cerca de la pared izquierda
    enemy.direction = -1  # Moviéndose hacia la izquierda (hacia la pared)
    level_map = create_test_map_with_walls()

    initial_x = enemy.x

    # Simular movimiento hacia la pared
    for i in range(60):
        enemy.update(0.016, level_map)

    # El enemigo debería haber rebotado (cambió dirección)
    # y no debería estar dentro de la pared (x < 32)
    if enemy.x >= TILE_SIZE:  # No está dentro del tile de pared
        print(f"  [OK] Enemigo no atraveso la pared. Posicion: x={enemy.x:.2f}")
        print(f"       Direccion cambio: {enemy.direction == 1}")
        return True
    else:
        print(f"  [FALLO] Enemigo atraveso la pared. Posicion: x={enemy.x:.2f}")
        return False

def test_enemy_stops_at_block():
    """Test 2: El enemigo debe rebotar en bloques destructibles (B)"""
    print("\nTest 2: Enemigo rebota en bloque (B)...")

    enemy = Enemy(150, 40, "bat")  # Crear murciélago cerca del bloque
    enemy.direction = 1  # Moviéndose hacia la derecha (hacia el bloque)
    level_map = create_test_map_with_blocks()

    # Simular movimiento hacia el bloque en tile (6,1)
    for i in range(60):
        enemy.update(0.016, level_map)

    # El enemigo no debería atravesar el bloque en x=192 (tile 6 * 32)
    if enemy.x < 6 * TILE_SIZE:  # No llegó al tile del bloque
        print(f"  [OK] Enemigo no atraveso el bloque. Posicion: x={enemy.x:.2f}")
        print(f"       Direccion cambio: {enemy.direction == -1}")
        return True
    else:
        print(f"  [FALLO] Enemigo atraveso el bloque. Posicion: x={enemy.x:.2f}")
        return False

def test_enemy_stops_at_floor():
    """Test 3: El enemigo debe rebotar en piso (.)"""
    print("\nTest 3: Enemigo rebota en piso (.)...")

    enemy = Enemy(150, 40, "spider")  # Crear araña cerca del piso
    enemy.direction = 1  # Moviéndose hacia la derecha (hacia el piso)
    level_map = create_test_map_with_floor()

    # Simular movimiento hacia el piso en tile (6,1)
    for i in range(60):
        enemy.update(0.016, level_map)

    # El enemigo no debería atravesar el piso en x=192 (tile 6 * 32)
    if enemy.x < 6 * TILE_SIZE:  # No llegó al tile del piso
        print(f"  [OK] Enemigo no atraveso el piso. Posicion: x={enemy.x:.2f}")
        print(f"       Direccion cambio: {enemy.direction == -1}")
        return True
    else:
        print(f"  [FALLO] Enemigo atraveso el piso. Posicion: x={enemy.x:.2f}")
        return False

def test_enemy_bounces_back_and_forth():
    """Test 4: El enemigo debe rebotar de ida y vuelta entre paredes"""
    print("\nTest 4: Enemigo rebota de ida y vuelta...")

    # Crear enemigo más rápido y más cerca de la pared para que rebote
    enemy = Enemy(400, 50, "bat")  # Más cerca de la pared derecha
    enemy.direction = 1  # Moviéndose hacia la derecha
    enemy.speed = 80  # Más rápido para alcanzar la pared
    level_map = create_test_map_with_walls()

    direction_changes = 0
    last_direction = enemy.direction

    # Simular varios frames - más tiempo para rebotar múltiples veces
    for i in range(400):
        enemy.update(0.016, level_map)

        # Contar cambios de dirección
        if enemy.direction != last_direction:
            direction_changes += 1
            last_direction = enemy.direction

    # Debería haber rebotado al menos una vez (cambió de dirección)
    # Y siempre debe estar dentro de los límites válidos (no dentro de paredes)
    in_bounds = TILE_SIZE < enemy.x < (LEVEL_WIDTH - 1) * TILE_SIZE

    if direction_changes >= 1 and in_bounds:
        print(f"  [OK] Enemigo reboto {direction_changes} veces y permanece en bounds")
        print(f"       Posicion final: x={enemy.x:.2f}")
        return True
    else:
        print(f"  [FALLO] Rebotes: {direction_changes}, En bounds: {in_bounds}")
        print(f"       Posicion final: x={enemy.x:.2f}")
        return False

def test_enemy_corner_collision():
    """Test 5: El enemigo debe detectar colisión con todas sus esquinas"""
    print("\nTest 5: Enemigo detecta colision en esquinas...")

    # Crear mapa con un bloque específico
    level_map = [
        "                ",  # Row 0
        "      #         ",  # Row 1 - pared
        "                ",  # Row 2
    ]

    # Posicionar enemigo justo antes de la pared
    enemy = Enemy(160, 40, "bat")
    enemy.direction = 1  # Moviéndose hacia la derecha (hacia x=192, tile 6)

    # Simular movimiento
    for i in range(50):
        old_x = enemy.x
        enemy.update(0.016, level_map)

        # Si pasó del tile de pared sin rebotar, fallo
        if enemy.x > 6 * TILE_SIZE:
            print(f"  [FALLO] Enemigo atraveso la pared en x={enemy.x:.2f}")
            return False

    # Verificar que se detuvo antes de la pared
    if enemy.x < 6 * TILE_SIZE:
        print(f"  [OK] Enemigo detecto colision correctamente")
        print(f"       Posicion final: x={enemy.x:.2f}, esperado < {6 * TILE_SIZE}")
        return True
    else:
        print(f"  [FALLO] Enemigo no detecto colision")
        return False

if __name__ == "__main__":
    import pygame
    pygame.init()

    print("=" * 60)
    print("TESTS DE COLISION DE ENEMIGOS")
    print("=" * 60)

    results = []
    results.append(test_enemy_stops_at_wall())
    results.append(test_enemy_stops_at_block())
    results.append(test_enemy_stops_at_floor())
    results.append(test_enemy_bounces_back_and_forth())
    results.append(test_enemy_corner_collision())

    print("\n" + "=" * 60)
    print(f"RESULTADOS: {sum(results)}/{len(results)} tests pasados")
    print("=" * 60)

    if all(results):
        print("[OK] TODOS LOS TESTS PASARON")
        sys.exit(0)
    else:
        print("[FALLO] ALGUNOS TESTS FALLARON")
        sys.exit(1)
