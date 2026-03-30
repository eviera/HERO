# evgamelib - Manejo de input (teclado + gamepad)

import pygame

from evgamelib.constants import DEFAULT_DEAD_ZONE


class InputManager:
    """Maneja input de teclado y gamepad con dead zones."""

    def __init__(self, dead_zone=DEFAULT_DEAD_ZONE):
        self.keys = []
        self.joy_axis_x = 0
        self.joy_axis_y = 0
        self.controller = None
        self.dead_zone = dead_zone

    def init_controllers(self):
        """Detecta y conecta controllers."""
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            if "Xbox" in joystick.get_name() or "Controller" in joystick.get_name():
                self.controller = joystick
                self.controller.init()
                print(f"Controller found: {joystick.get_name()}")
                break

    def poll(self):
        """Lee el estado actual de teclado y joystick."""
        self.keys = pygame.key.get_pressed()

        if self.controller:
            self.joy_axis_x = self.controller.get_axis(0)
            self.joy_axis_y = self.controller.get_axis(1)

            if abs(self.joy_axis_x) < self.dead_zone:
                self.joy_axis_x = 0
            if abs(self.joy_axis_y) < self.dead_zone:
                self.joy_axis_y = 0
        else:
            self.joy_axis_x = 0
            self.joy_axis_y = 0
