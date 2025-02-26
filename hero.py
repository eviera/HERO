# Esto sale de https://gemini.google.com/app/155caf2270872767

import pygame
import math

# Initialize Pygame
pygame.init()

# Initialize joysticks
pygame.joystick.init()

# Get the number of joysticks connected
joystick_count = pygame.joystick.get_count()
print(f"There are {joystick_count} joystick(s) connected.")

# Find the Xbox controller (you might need to adjust this)
xbox_controller = None
for i in range(joystick_count):
    joystick = pygame.joystick.Joystick(i)
    if "Xbox" in joystick.get_name():  # Check if it's an Xbox controller
        xbox_controller = joystick
        print(f"Found Xbox controller: {joystick.get_name()}")
        break

if xbox_controller is None:
    print("No Xbox controller found. Using keyboard controls.")
else:
    xbox_controller.init()  # Initialize the Xbox controller

# Window dimensions
screen_width = 512
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))

# Set window title
pygame.display.set_caption("H.E.R.O. Remake")

# Load player sprite
player_image = pygame.image.load("sprites/player.png").convert_alpha()  # Handles transparency
player_x = screen_width // 2 - player_image.get_width() // 2  # Start in center
player_y = screen_height // 2 - player_image.get_height() // 2


# Player movement variables
player_speed = 0.2  # Adjust as needed
dead_zone = 0.1  # Adjust this value (e.g., 0.1, 0.2) as needed

# Game loop
running = True
while running:
    
    if xbox_controller:
        axis_0 = xbox_controller.get_axis(0)
        axis_1 = xbox_controller.get_axis(1)

        # Apply dead zone
        if abs(axis_0) < dead_zone:
            axis_0 = 0.0
        if abs(axis_1) < dead_zone:
            axis_1 = 0.0

        # Calculate the movement vector (same as before)
        movement_vector = pygame.math.Vector2(axis_0, axis_1)
    
        # Normalize the vector if it's not zero (to avoid division by zero)
        if movement_vector.length() > 0:
            movement_vector.normalize_ip()  # In-place normalization

        # Apply the normalized vector and speed
        player_x += player_speed * movement_vector.x
        player_y += player_speed * movement_vector.y
        
        # Example: Button 0 for "A" (you'll need to define actions)
        if xbox_controller.get_button(0):
            print("A button pressed!")  # Replace with actual action
    
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False            
        # Keep player within screen bounds (example, adjust as needed)
        if player_x < 0:
            player_x = 0
        elif player_x > screen_width - player_image.get_width():
            player_x = screen_width - player_image.get_width()
        if player_y < 0:
            player_y = 0
        elif player_y > screen_height - player_image.get_height():
            player_y = screen_height - player_image.get_height()

    # Clear the screen (important!)
    screen.fill((0, 0, 0))  # Black background (adjust as needed)

    # Round player position to avoid subpixel rendering
    player_x = round(player_x)
    player_y = round(player_y)
    # Draw the player
    screen.blit(player_image, (player_x, player_y))

    pygame.display.flip()
    
pygame.quit()

