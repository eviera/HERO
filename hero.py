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

# Load tile images
wall_tile = pygame.image.load("tiles/wall.png").convert_alpha()
ground_tile = pygame.image.load("tiles/ground.png").convert_alpha()

# Initialize clock for frame rate control
clock = pygame.time.Clock()
FPS = 60  # Set desired frame rate

# Tile size
tile_size = 32


level_map = [
    "##########",
    "#....#...#",
    "#..E.#...#",
    "#..R.#...#",
    "#........#",
    "##########",
]


# Player movement variables
player_speed = 200  # Adjust as needed
dead_zone = 0.1  # Adjust this value (e.g., 0.1, 0.2) as needed


##################################################################################################
def render_level(level_map):
    for row_index, row in enumerate(level_map):
        for col_index, tile in enumerate(row):
            x = col_index * tile_size
            y = row_index * tile_size
            if tile == "#":
                screen.blit(wall_tile, (x, y))
            elif tile == ".":
                screen.blit(ground_tile, (x, y))
            # Add more tile types here later (E, R, etc.)
            

##################################################################################################
# Game loop
running = True
while running:
    
    # Calculate time elapsed since last frame
    dt = clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds

    if xbox_controller:
        axis_0 = xbox_controller.get_axis(0)
        axis_1 = xbox_controller.get_axis(1)

        if abs(axis_0) < dead_zone:
            axis_0 = 0.0
        if abs(axis_1) < dead_zone:
            axis_1 = 0.0

        # Calculate movement *without* rounding
        player_x_change = axis_0 * player_speed * dt
        player_y_change = axis_1 * player_speed * dt

        # Apply movement and *then* round for display
        player_x += player_x_change
        player_y += player_y_change
        
        #print(f"X: {player_x}, Y: {player_y}, axis_0: {axis_0}, axis_1: {axis_1}, dt: {dt}")

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
    
    # Render the level
    render_level(level_map)
        
    # Round for display *after* applying all movement
    player_x_rounded = round(player_x)
    player_y_rounded = round(player_y)

    # Draw the player
    screen.blit(player_image, (player_x_rounded, player_y_rounded))    
    
    pygame.display.flip()
    
pygame.quit()

