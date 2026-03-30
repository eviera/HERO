# Tests para evgamelib.sound_manager

import pytest
import pygame
from evgamelib.sound_manager import SoundManager


# Inicializar pygame para mixer
pygame.init()
pygame.mixer.init()


class TestSoundManager:
    def test_init(self):
        sm = SoundManager()
        assert len(sm.sounds) == 0

    def test_is_looping_default(self):
        sm = SoundManager()
        assert sm.is_looping('anything') == False

    def test_loop_tracking(self):
        sm = SoundManager()
        sm._loops['test'] = True
        assert sm.is_looping('test') == True
        sm._loops['test'] = False
        assert sm.is_looping('test') == False

    def test_generate_beep(self):
        sm = SoundManager()
        beep = sm.generate_beep(440, duration_ms=50, volume=0.3)
        assert beep is not None
        assert isinstance(beep, pygame.mixer.Sound)

    def test_generate_beep_different_frequencies(self):
        sm = SoundManager()
        beep1 = sm.generate_beep(400)
        beep2 = sm.generate_beep(800)
        assert beep1 is not None
        assert beep2 is not None
