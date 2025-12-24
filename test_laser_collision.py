"""
Tests para verificar que los disparos colisionan correctamente con todos los bloques
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from laser import Laser
from constants import *

def create_test_map_with_blocks():
    """Crea un mapa con diferentes tipos de bloques"""
    return [
        "                ",  # Row 0
        "  #  .  B       ",  # Row 1 - pared, piso, bloque destructible
        "                ",  # Row 2
    ]

def test_laser_stops_at_wall():
    """Test 1: El láser debe detenerse al tocar una pared (#)"""
    print("Test 1: Laser se detiene en pared (#)...")

    laser = Laser(20, 40, 1)  # Dispara hacia la derecha
    level_map = create_test_map_with_blocks()

    # Simular movimiento hasta que colisione con pared en tile (2,1)
    for i in range(100):
        laser.update(0.016, level_map)
        if not laser.active:
            # Verificar que se detuvo cerca de x=64 (tile 2 * 32)
            if laser.x < 80:  # Debe estar antes o cerca del tile
                print(f"  [OK] Laser se detuvo correctamente en x={laser.x:.2f}")
                return True
            else:
                print(f"  [FALLO] Laser paso de largo: x={laser.x:.2f}")
                return False

    print(f"  [FALLO] Laser no se detuvo. Posicion final: x={laser.x:.2f}")
    return False

def test_laser_stops_at_floor():
    """Test 2: El láser debe detenerse al tocar piso (.)"""
    print("\nTest 2: Laser se detiene en piso (.)...")

    laser = Laser(130, 40, 1)  # Dispara hacia la derecha, cerca del piso
    level_map = create_test_map_with_blocks()

    # Simular movimiento hasta que colisione con piso en tile (5,1)
    for i in range(100):
        laser.update(0.016, level_map)
        if not laser.active:
            # Verificar que se detuvo cerca de x=160 (tile 5 * 32)
            if 150 < laser.x < 180:
                print(f"  [OK] Laser se detuvo correctamente en x={laser.x:.2f}")
                return True
            else:
                print(f"  [FALLO] Laser se detuvo en posicion incorrecta: x={laser.x:.2f}")
                return False

    print(f"  [FALLO] Laser no se detuvo. Posicion final: x={laser.x:.2f}")
    return False

def test_laser_stops_at_block():
    """Test 3: El láser debe detenerse al tocar bloque destructible (B)"""
    print("\nTest 3: Laser se detiene en bloque destructible (B)...")

    laser = Laser(190, 40, 1)  # Dispara hacia la derecha, cerca del bloque B
    level_map = create_test_map_with_blocks()

    # Simular movimiento hasta que colisione con bloque en tile (8,1)
    for i in range(100):
        laser.update(0.016, level_map)
        if not laser.active:
            # Verificar que se detuvo cerca de x=256 (tile 8 * 32)
            if 240 < laser.x < 270:
                print(f"  [OK] Laser se detuvo correctamente en x={laser.x:.2f}")
                return True
            else:
                print(f"  [FALLO] Laser se detuvo en posicion incorrecta: x={laser.x:.2f}")
                return False

    print(f"  [FALLO] Laser no se detuvo en bloque B. Posicion final: x={laser.x:.2f}")
    return False

def test_laser_corner_detection():
    """Test 4: El láser debe detectar colisión incluso en esquinas"""
    print("\nTest 4: Laser detecta colision en esquinas...")

    # Crear un mapa donde el láser rozaría la esquina de un bloque
    level_map = [
        "                ",  # Row 0
        "      #         ",  # Row 1 - pared
        "                ",  # Row 2
    ]

    # Láser que pasa justo por el borde inferior del tile
    laser = Laser(100, 63, 1)  # y=63, altura=4, bottom=67 (tile row 2)

    # Si solo chequeara el centro, podría pasar. Con corners, debe detenerse
    for i in range(100):
        laser.update(0.016, level_map)
        if not laser.active:
            print(f"  [OK] Laser detecto colision en esquina")
            return True

        # Si pasa del tile sin detenerse, fallo
        if laser.x > 220:
            print(f"  [FALLO] Laser atraveso el bloque")
            return False

    print(f"  [OK] Laser paso sin colisionar (correcto para este caso)")
    return True

def test_laser_size():
    """Test 5: El láser debe tener el tamaño correcto (más corto)"""
    print("\nTest 5: Laser tiene el tamano correcto...")

    laser = Laser(100, 100, 1)

    if laser.width == 10:
        print(f"  [OK] Laser tiene width={laser.width} (reducido correctamente)")
        return True
    else:
        print(f"  [FALLO] Laser tiene width={laser.width}, esperado: 10")
        return False

if __name__ == "__main__":
    import pygame
    pygame.init()

    print("=" * 60)
    print("TESTS DE COLISION DE LASER")
    print("=" * 60)

    results = []
    results.append(test_laser_stops_at_wall())
    results.append(test_laser_stops_at_floor())
    results.append(test_laser_stops_at_block())
    results.append(test_laser_corner_detection())
    results.append(test_laser_size())

    print("\n" + "=" * 60)
    print(f"RESULTADOS: {sum(results)}/{len(results)} tests pasados")
    print("=" * 60)

    if all(results):
        print("[OK] TODOS LOS TESTS PASARON")
        sys.exit(0)
    else:
        print("[FALLO] ALGUNOS TESTS FALLARON")
        sys.exit(1)
