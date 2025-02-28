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
    [
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
]

##################################################################################################
# Player
##################################################################################################
class Player:
    def __init__(self):
        self.image = None
        self.x = 0
        self.y = 0
        
    ##################################################################################################
    # Initialize player
    ##################################################################################################
    def init(self):
        self.image = pygame.image.load("sprites/player.png").convert_alpha()  # Handles transparency

        # Find the "S" tile (start position)
        player_start_x = None
        player_start_y = None
        for row_index, row in enumerate(MAPS[0]):
            for col_index, tile in enumerate(row):
                if tile == "S":
                    player_start_x = col_index * TILE_SIZE
                    player_start_y = row_index * TILE_SIZE
                    break  # Exit the inner loop once "S" is found
            if player_start_x is not None:
                break  # Exit the outer loop as well

        # Initialize player position
        if player_start_x is not None and player_start_y is not None:
            self.x = player_start_x
            self.y = player_start_y
        else:
            # Default position if "S" is not found
            self.x = SCREEN_WIDTH // 2 - self.image.get_width() // 2  # Start in center
            self.y = SCREEN_HEIGHT // 2 - self.image.get_height() // 2

    ##################################################################################################
    # Compute player movement
    ##################################################################################################
    def compute_movement(self, dt, axis_0, axis_1):
        # Calculate movement *without* rounding
        player_x_change = axis_0 * PLAYER_SPEED * dt
        player_y_change = axis_1 * PLAYER_SPEED * dt

        # Apply movement and *then* round for display
        self.x += player_x_change
        self.y += player_y_change

    ##################################################################################################
    # Update and draw player
    #################################################################################################
    def update(self, screen):
        # Keep player within screen bounds (example, adjust as neededself.screen)
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.image.get_width():
            self.x = SCREEN_WIDTH - self.image.get_width()
        if self.y < 0:
            self.y = 0
        elif self.y > SCREEN_HEIGHT - self.image.get_height():
            self.y = SCREEN_HEIGHT - self.image.get_height()
            
        # Round for display *after* applying all movement
        player_x_rounded = round(self.x)
        player_y_rounded = round(self.y)

        # Draw the player
        screen.blit(self.image, (player_x_rounded, player_y_rounded))
            


##################################################################################################
# Game
##################################################################################################
class Game:
    def __init__(self):
        self.screen = None
        self.clock = None
        self.xbox_controller = None
        self.sprites = {}
        self.tiles = {}
        self.score = 0
        self.level = 0
        self.player = Player()

    ##################################################################################################
    # Load assets
    ##################################################################################################
    def load_assets(self):
        self.tiles['wall'] = pygame.image.load("tiles/wall.png").convert_alpha()
        self.tiles['ground'] = pygame.image.load("tiles/ground.png").convert_alpha()
        self.tiles['blank'] = pygame.image.load("tiles/blank.png").convert_alpha()

    ##################################################################################################
    # Initialize game
    ##################################################################################################
    def init(self):
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
                self.xbox_controller = joystick
                print(f"Found Xbox controller: {joystick.get_name()}")
                break

        if self.xbox_controller is None:
            print("No Xbox controller found. Using keyboard controls.")
        else:
            self.xbox_controller.init()  # Initialize the Xbox controller

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # Initialize clock for frame rate control
        self.clock = pygame.time.Clock()

        # Set window title
        pygame.display.set_caption("H.E.R.O. Remake")

        # Load tile images
        self.load_assets()
        # Load and init player
        self.player.init()        

    ##################################################################################################
    # Render level
    ##################################################################################################
    def render_level(self, level_map):
        for row_index, row in enumerate(level_map):
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                tile_actions = {
                    "#": self.tiles['wall'],
                    ".": self.tiles['ground'],
                    " ": self.tiles['blank']
                }                                
                if tile in tile_actions:
                    self.screen.blit(tile_actions[tile], (x, y))
                

    ##################################################################################################
    # Game loop
    ##################################################################################################
    def loop(self):
        running = True
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False            

            # Clear the screen (important!)
            self.screen.fill((0, 0, 0))  # Black background (adjust as needed)

            # Render the level
            self.render_level(MAPS[self.level])
            
            # Calculate time elapsed since last frame
            dt = self.clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds

            if self.xbox_controller:
                axis_0 = self.xbox_controller.get_axis(0)
                axis_1 = self.xbox_controller.get_axis(1)

                if abs(axis_0) < DEAD_ZONE:
                    axis_0 = 0.0
                if abs(axis_1) < DEAD_ZONE:
                    axis_1 = 0.0

                self.player.compute_movement(dt, axis_0, axis_1)

                # Example: Button 0 for "A" (you'll need to define actions)
                if self.xbox_controller.get_button(0):
                    print("A button pressed!")  # Replace with actual action

            # Update player
            self.player.update(self.screen)
                            
            pygame.display.flip()


##################################################################################################
# Main
##################################################################################################
def main():
    game = Game()
    game.init()
    
    try:
        game.loop()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.quit()  # Ase

# Using the special variable 
# __name__
if __name__=="__main__":
    main()