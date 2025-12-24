"""
Tests para verificar que el jugador se comporta correctamente sobre el piso
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from player import Player
from constants import *

class MockGame:
    """Mock del objeto game para testing"""
    def __init__(self):
        self.energy = 1000

def create_test_map():
    """Crea un mapa simple para testing"""
    return [
        "                ",  # Row 0
        "                ",  # Row 1
        "                ",  # Row 2
        "                ",  # Row 3
        "                ",  # Row 4
        "################",  # Row 5 - piso sólido
        "################",  # Row 6
    ]

def test_player_lands_on_ground():
    """Test 1: El jugador debe caer y detenerse sobre el piso"""
    print("Test 1: Jugador cae y se detiene sobre el piso...")

    player = Player()
    level_map = create_test_map()
    game = MockGame()

    # Posicionar jugador en el aire
    player.x = 100
    player.y = 50  # En el aire, debería caer
    player.vel_y = 0

    # Simular varios frames de caída
    keys = pygame.key.get_pressed()
    for i in range(100):  # 100 frames
        old_y = player.y
        player.update(0.016, keys, 0, 0, level_map, game)

        # Verificar que no está vibrando (cambios de posición muy pequeños)
        if abs(player.y - old_y) < 0.01 and player.y > 0:
            # Se detuvo, verificar que está sobre el piso (tile row 5)
            # El piso está en y=5*32=160
            # El jugador debe estar con sus pies justo por encima
            expected_max_y = 5 * TILE_SIZE  # 160

            if player.y + player.height <= expected_max_y + 5:  # Pequeña tolerancia
                print(f"  [OK] Jugador se detuvo correctamente en y={player.y:.2f}")
                print(f"       Pies del jugador: {player.y + player.height:.2f}")
                print(f"       Borde superior del piso: {expected_max_y}")
                return True

    print(f"  [FALLO] Jugador no se detuvo correctamente. Posicion final: y={player.y:.2f}")
    return False

def test_player_stays_stable_on_ground():
    """Test 2: El jugador debe permanecer estable sin vibrar cuando está parado"""
    print("\nTest 2: Jugador permanece estable sin vibrar...")

    player = Player()
    level_map = create_test_map()
    game = MockGame()

    # Posicionar jugador justo sobre el piso
    player.x = 100
    player.y = 5 * TILE_SIZE - player.height  # Justo sobre el tile row 5
    player.vel_y = 0

    # Simular muchos frames sin input
    keys = pygame.key.get_pressed()
    positions = []
    for i in range(60):  # 60 frames = 1 segundo
        player.update(0.016, keys, 0, 0, level_map, game)
        positions.append(player.y)

    # Verificar que la posición no varía más de 1 pixel
    min_y = min(positions)
    max_y = max(positions)
    variation = max_y - min_y

    if variation <= 1.0:
        print(f"  [OK] Jugador estable. Variacion: {variation:.4f} pixels")
        return True
    else:
        print(f"  [FALLO] Jugador vibra. Variacion: {variation:.4f} pixels")
        print(f"         Min Y: {min_y:.2f}, Max Y: {max_y:.2f}")
        return False

def test_player_walks_on_ground():
    """Test 3: El jugador puede caminar horizontalmente sobre el piso"""
    print("\nTest 3: Jugador puede caminar sobre el piso...")

    player = Player()
    level_map = create_test_map()
    game = MockGame()

    # Posicionar jugador sobre el piso
    player.x = 100
    player.y = 5 * TILE_SIZE - player.height
    player.vel_y = 0

    initial_x = player.x
    initial_y = player.y

    # Simular caminar a la derecha - crear dict simulando keys presionadas
    class KeysDict:
        def __getitem__(self, key):
            return key == pygame.K_RIGHT

    keys = KeysDict()

    for i in range(30):  # 30 frames
        player.update(0.016, keys, 0, 0, level_map, game)

    # Verificar que se movió horizontalmente
    moved_horizontally = player.x > initial_x + 10

    # Verificar que la Y no varió mucho (se mantiene en el piso)
    y_variation = abs(player.y - initial_y)
    stayed_on_ground = y_variation <= 2.0

    if moved_horizontally and stayed_on_ground:
        print(f"  [OK] Jugador camino correctamente")
        print(f"       Movimiento X: {player.x - initial_x:.2f} pixels")
        print(f"       Variacion Y: {y_variation:.2f} pixels")
        return True
    else:
        print(f"  [FALLO]:")
        if not moved_horizontally:
            print(f"         No se movio horizontalmente. Delta X: {player.x - initial_x:.2f}")
        if not stayed_on_ground:
            print(f"         No se mantuvo en el piso. Delta Y: {y_variation:.2f}")
        return False

if __name__ == "__main__":
    # Necesitamos pygame para las constantes de teclas
    import pygame
    pygame.init()

    print("=" * 60)
    print("TESTS DE COLISIÓN DEL JUGADOR")
    print("=" * 60)

    results = []
    results.append(test_player_lands_on_ground())
    results.append(test_player_stays_stable_on_ground())
    results.append(test_player_walks_on_ground())

    print("\n" + "=" * 60)
    print(f"RESULTADOS: {sum(results)}/{len(results)} tests pasados")
    print("=" * 60)

    if all(results):
        print("[OK] TODOS LOS TESTS PASARON")
        sys.exit(0)
    else:
        print("[FALLO] ALGUNOS TESTS FALLARON")
        sys.exit(1)
