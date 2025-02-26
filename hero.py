# Esto sale de https://gemini.google.com/app/155caf2270872767

import pygame


# Window dimensions
SCREEN_WIDTH = 512
SCREEN_HEIGHT = 480
FPS = 60  # Set desired frame rate
TILE_SIZE = 32
# Player movement variables
PLAYER_SPEED = 200  # Adjust as needed
DEAD_ZONE = 0.1  # Adjust this value (e.g., 0.1, 0.2) as needed

#16x15
MAPS = [
    "###S############",
    "#....#.........#",
    "#..E.#.........#",
    "#..R.#.........#",
    "#..............#",
    "#..............#",
    "#..............#",
    "#..............#",
    "#..............#",
    "#..............#",
    "#..............#",
    "#..............#",
    "#..............#",
    "#..............#",
    "################",
]


class Game:
    def __init__(self):
        self.screen = None
        self.clock = None
        self.xbox_controller = None
        self.sprites = {}
        self.tiles = {}
        self.score = 0
        self.level = 1

    def load_assets(self):
        self.tiles['wall'] = pygame.image.load("tiles/wall.png").convert_alpha()

    ##################################################################################################
    # Initialize game
    ##################################################################################################
    def init():
        # Initialize Pygame
        pygame.init()

        # Initialize joysticks
        pygame.joystick.init()

        # Get the number of joysticks connected
        joystick_count = pygame.joystick.get_count()
        print(f"There are {joystick_count} joystick(s) connected.")

        # Find the Xbox controller (you might need to adjust this)
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

        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # Initialize clock for frame rate control
        clock = pygame.time.Clock()

        # Set window title
        pygame.display.set_caption("H.E.R.O. Remake")

        # Load player sprite
        player_image = pygame.image.load("sprites/player.png").convert_alpha()  # Handles transparency
        player_x = SCREEN_WIDTH // 2 - player_image.get_width() // 2  # Start in center
        player_y = SCREEN_HEIGHT // 2 - player_image.get_height() // 2
        
        # Load tile images
        tiles['wall'] = pygame.image.load("tiles/wall.png").convert_alpha()
        tiles['ground'] = pygame.image.load("tiles/ground.png").convert_alpha()

        # Find the "S" tile (start position)
        player_start_x = None
        player_start_y = None
        for row_index, row in enumerate(MAPS):
            for col_index, tile in enumerate(row):
                if tile == "S":
                    player_start_x = col_index * TILE_SIZE
                    player_start_y = row_index * TILE_SIZE
                    break  # Exit the inner loop once "S" is found
            if player_start_x is not None:
                break  # Exit the outer loop as well

        # Initialize player position
        if player_start_x is not None and player_start_y is not None:
            player_x = player_start_x
            player_y = player_start_y
        else:
            # Default position if "S" is not found
            player_x = SCREEN_WIDTH // 2
            player_y = SCREEN_HEIGHT // 2

    ##################################################################################################
    # Render level
    ##################################################################################################
    def render_level(level_map):
        for row_index, row in enumerate(level_map):
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                if tile == "#":
                    screen.blit(tiles['wall'], (x, y))
                elif tile == ".":
                    screen.blit(tiles['ground'], (x, y))
                # Add more tile types here later (E, R, etc.)
                

    ##################################################################################################
    # Game loop
    ##################################################################################################
    def loop():
        running = True
        while running:
            
            # Calculate time elapsed since last frame
            dt = clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds

            if xbox_controller:
                axis_0 = xbox_controller.get_axis(0)
                axis_1 = xbox_controller.get_axis(1)

                if abs(axis_0) < DEAD_ZONE:
                    axis_0 = 0.0
                if abs(axis_1) < DEAD_ZONE:
                    axis_1 = 0.0

                # Calculate movement *without* rounding
                player_x_change = axis_0 * PLAYER_SPEED * dt
                player_y_change = axis_1 * PLAYER_SPEED * dt

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
                elif player_x > SCREEN_WIDTH - player_image.get_width():
                    player_x = SCREEN_WIDTH - player_image.get_width()
                if player_y < 0:
                    player_y = 0
                elif player_y > SCREEN_HEIGHT - player_image.get_height():
                    player_y = SCREEN_HEIGHT - player_image.get_height()

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


    


# Defining main function
def main():
    game = Game()
    game.init()
    game.loop()
    
    pygame.quit()

# Using the special variable 
# __name__
if __name__=="__main__":
    main()