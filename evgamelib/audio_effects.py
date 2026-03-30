# evgamelib - Efectos de audio (emulacion SID de Commodore 64)
# Compatible con pygame.sndarray y numpy

import numpy as np
import pygame
import pygame.sndarray


class SIDEmulator:
    """Emula las características sonoras del chip SID de Commodore 64"""

    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def bitcrush(self, samples, bits=4):
        """Reduce la profundidad de bits - característica central del SID"""
        steps = 2 ** bits
        step_size = 32768 / (steps / 2)
        crushed = np.round(samples / step_size) * step_size
        return np.clip(crushed, -32768, 32767).astype(np.int16)

    def lowpass_filter(self, samples, cutoff_hz=3500):
        """Filtro paso-bajo simple para remover aliasing"""
        cutoff_norm = cutoff_hz / (self.sample_rate / 2)
        if cutoff_norm >= 1.0:
            return samples

        window_size = max(2, int(1.0 / cutoff_norm))
        kernel = np.ones(window_size) / window_size

        filtered = np.zeros_like(samples, dtype=np.float32)
        for ch in range(samples.shape[1]):
            filtered[:, ch] = np.convolve(samples[:, ch], kernel, mode='same')

        return np.clip(filtered, -32768, 32767).astype(np.int16)

    def wave_distortion(self, samples, amount=0.3):
        """Distorsión suave (soft-clipping) para sonido cálido/comprimido"""
        normalized = samples.astype(np.float32) / 32768.0
        distorted = np.tanh(normalized * (1 + amount * 3))
        return (distorted * 32768).astype(np.int16)

    def process(self, audio_array, intensity='light'):
        """Aplica efectos de emulación SID"""
        result = audio_array.copy()

        if intensity == 'light':
            result = self.bitcrush(result, bits=5)
        elif intensity == 'medium':
            result = self.bitcrush(result, bits=4)
            result = self.lowpass_filter(result, cutoff_hz=4000)
        elif intensity == 'heavy':
            result = self.bitcrush(result, bits=4)
            result = self.lowpass_filter(result, cutoff_hz=3500)
            result = self.wave_distortion(result, amount=0.2)

        return result


def apply_sid_to_sound(sound, intensity='light'):
    """Aplica emulación SID a un pygame.mixer.Sound"""
    audio_array = pygame.sndarray.array(sound)
    emulator = SIDEmulator(sample_rate=44100)
    processed = emulator.process(audio_array.copy(), intensity=intensity)
    return pygame.sndarray.make_sound(processed)
