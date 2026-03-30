# evgamelib - Motor de juegos 2D basado en Pygame
# Libreria reutilizable para juegos de accion y plataformas

__version__ = "0.1.0"

from evgamelib.engine import GameEngine
from evgamelib.entity import Entity, PhysicsEntity, AnimatedEntity
from evgamelib.camera import SnapCamera
from evgamelib.collision import mask_overlap, rect_overlap, check_corners_vs_tiles, mask_vs_tiles
from evgamelib.input_manager import InputManager
from evgamelib.sound_manager import SoundManager
from evgamelib.rendering import RenderPipeline
from evgamelib.state import StateMachine, GameState
from evgamelib.scores import HighScoreManager
from evgamelib.text import draw_text_with_outline, FloatingText, FloatingTextManager
from evgamelib.tilemap import TileMap
