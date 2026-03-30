# Tests para evgamelib.input_manager

import pytest
import pygame
from evgamelib.input_manager import InputManager


# Inicializar pygame
pygame.init()


class TestInputManager:
    def test_init_defaults(self):
        im = InputManager()
        assert im.dead_zone == 0.15
        assert im.controller is None
        assert im.joy_axis_x == 0
        assert im.joy_axis_y == 0

    def test_init_custom_dead_zone(self):
        im = InputManager(dead_zone=0.3)
        assert im.dead_zone == 0.3

    def test_poll_without_controller(self):
        im = InputManager()
        im.poll()
        assert im.joy_axis_x == 0
        assert im.joy_axis_y == 0
        assert im.keys is not None
