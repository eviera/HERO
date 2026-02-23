"""Script para analizar el sprite del jugador y crear sprites de caminata"""
import pygame

pygame.init()
screen = pygame.display.set_mode((64, 64))

original = pygame.image.load("sprites/player.png").convert_alpha()

# Mostrar TODOS los pixeles con RGB para las piernas (y=18-31)
print("Full pixel dump (y=18-31, legs area):")
for y in range(18, 32):
    for x in range(0, 32):
        r, g, b, a = original.get_at((x, y))
        if a > 0:
            print(f"  ({x:2d},{y:2d}): ({r:3d},{g:3d},{b:3d},{a:3d})")

# Tambien la zona del torso bajo para contexto
print("\nTorso/belt area (y=15-19):")
for y in range(15, 20):
    for x in range(0, 32):
        r, g, b, a = original.get_at((x, y))
        if a > 0:
            print(f"  ({x:2d},{y:2d}): ({r:3d},{g:3d},{b:3d},{a:3d})")

pygame.quit()
