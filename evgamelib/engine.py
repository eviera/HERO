# evgamelib - GameEngine base

import pygame

from evgamelib.rendering import RenderPipeline
from evgamelib.input_manager import InputManager
from evgamelib.sound_manager import SoundManager
from evgamelib.camera import SnapCamera
from evgamelib.scores import HighScoreManager
from evgamelib.text import FloatingTextManager
from evgamelib.state import StateMachine
from evgamelib.constants import DEFAULT_FPS, DEFAULT_DEAD_ZONE


class GameEngine:
    """Motor de juego base que compone todos los subsistemas de evgamelib.
    Los juegos pueden extender esta clase o componer sus subsistemas directamente."""

    def __init__(self, game_w, game_h, render_scale=1.5, hud_height=80,
                 tile_size=32, viewport_cols=16, viewport_rows=8,
                 fps=DEFAULT_FPS, dead_zone=DEFAULT_DEAD_ZONE,
                 scores_file=None, fullscreen=True):
        # Configuracion
        self.fps = fps
        self.tile_size = tile_size
        self.viewport_cols = viewport_cols
        self.viewport_rows = viewport_rows

        # Subsistemas
        self.pipeline = RenderPipeline(game_w, game_h, render_scale, hud_height)
        self.input = InputManager(dead_zone=dead_zone)
        self.sound = SoundManager()
        self.camera = SnapCamera(game_w, game_h, tile_size)
        self.scores = HighScoreManager(scores_file) if scores_file else None
        self.floating_texts = FloatingTextManager()
        self.state_machine = StateMachine()

        # Accesos directos
        self.game_surface = self.pipeline.game_surface
        self.screen = self.pipeline.screen

        # Estado
        self.running = False
        self.clock = None

    def init(self, fullscreen=True):
        """Inicializa pygame y los subsistemas."""
        pygame.init()
        pygame.mixer.init()
        self.input.init_controllers()
        self.pipeline.init_display(fullscreen=fullscreen)
        self.clock = pygame.time.Clock()

    def run(self):
        """Loop principal del juego."""
        self.running = True
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0

            # Input
            self.input.poll()

            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                self.handle_event(event)

            # Update
            self.update(dt)

            # Render
            self.render()

            # Present
            self.pipeline.present()

        pygame.quit()

    def handle_event(self, event):
        """Override para procesar eventos. Por defecto delega al state machine."""
        self.state_machine.handle_event(event, self)

    def update(self, dt):
        """Override para actualizar logica. Por defecto delega al state machine."""
        self.state_machine.update(dt, self)

    def render(self):
        """Override para renderizar. Por defecto delega al state machine."""
        self.state_machine.render(self)
