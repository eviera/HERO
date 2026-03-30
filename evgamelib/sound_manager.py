# evgamelib - Manejo de sonido

import math
import array
import pygame


class SoundManager:
    """Maneja sonidos nombrados con tracking de loops."""

    def __init__(self):
        self.sounds = {}
        self._loops = {}  # name -> bool (esta en loop)

    def load(self, name, filepath):
        """Carga un sonido desde archivo."""
        self.sounds[name] = pygame.mixer.Sound(filepath)
        return self.sounds[name]

    def get(self, name):
        """Obtiene un sonido por nombre."""
        return self.sounds.get(name)

    def play(self, name, loops=0):
        """Reproduce un sonido. loops=-1 para loop infinito."""
        sound = self.sounds.get(name)
        if sound:
            sound.play(loops=loops)

    def stop(self, name):
        """Detiene un sonido."""
        sound = self.sounds.get(name)
        if sound:
            sound.stop()

    def start_loop(self, name):
        """Inicia un sonido en loop si no esta ya en loop."""
        if not self._loops.get(name, False):
            self.play(name, loops=-1)
            self._loops[name] = True

    def stop_loop(self, name):
        """Detiene un sonido en loop."""
        if self._loops.get(name, False):
            self.stop(name)
            self._loops[name] = False

    def is_looping(self, name):
        """Retorna True si el sonido esta en loop."""
        return self._loops.get(name, False)

    def generate_beep(self, frequency, duration_ms=50, volume=0.3):
        """Genera un sonido corto sine wave sin dependencia de numpy."""
        mixer_info = pygame.mixer.get_init()
        sample_rate, bit_size, channels = mixer_info
        n_samples = int(sample_rate * duration_ms / 1000)
        samples = []
        max_val = int(32767 * volume)
        for i in range(n_samples):
            val = int(max_val * math.sin(2 * math.pi * frequency * i / sample_rate))
            samples.append(val)
            if channels == 2:
                samples.append(val)
        return pygame.mixer.Sound(buffer=array.array('h', samples))
