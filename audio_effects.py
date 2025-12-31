"""
Audio effects para emulación SID (Commodore 64)
Compatible con pygame.sndarray y numpy
"""

import numpy as np
import pygame
import pygame.sndarray

class SIDEmulator:
    """Emula las características sonoras del chip SID de Commodore 64"""

    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def bitcrush(self, samples, bits=4):
        """
        Reduce la profundidad de bits - característica central del SID

        Args:
            samples: Array numpy de audio (int16)
            bits: Número de bits (1-8)

        Returns:
            Array numpy procesado (int16)
        """
        steps = 2 ** bits
        step_size = 32768 / (steps / 2)
        crushed = np.round(samples / step_size) * step_size
        return np.clip(crushed, -32768, 32767).astype(np.int16)

    def lowpass_filter(self, samples, cutoff_hz=3500):
        """
        Filtro paso-bajo simple para remover aliasing
        Usa convolución con kernel de media móvil

        Args:
            samples: Array numpy de audio (int16)
            cutoff_hz: Frecuencia de corte en Hz

        Returns:
            Array numpy filtrado (int16)
        """
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
        """
        Distorsión suave (soft-clipping) para sonido cálido/comprimido
        Usa tanh para saturación armónica

        Args:
            samples: Array numpy de audio (int16)
            amount: Cantidad de distorsión (0.0-1.0)

        Returns:
            Array numpy distorsionado (int16)
        """
        normalized = samples.astype(np.float32) / 32768.0
        distorted = np.tanh(normalized * (1 + amount * 3))
        return (distorted * 32768).astype(np.int16)

    def process(self, audio_array, intensity='light'):
        """
        Aplica efectos de emulación SID

        Args:
            audio_array: Array numpy de pygame.sndarray
            intensity: 'light', 'medium', o 'heavy'

        Returns:
            Array numpy procesado (int16)
        """
        result = audio_array.copy()

        if intensity == 'light':
            # Solo reduce profundidad de bits
            result = self.bitcrush(result, bits=5)

        elif intensity == 'medium':
            # Bitcrush + filtro paso-bajo sutil
            result = self.bitcrush(result, bits=4)
            result = self.lowpass_filter(result, cutoff_hz=4000)

        elif intensity == 'heavy':
            # Tratamiento completo SID
            result = self.bitcrush(result, bits=4)
            result = self.lowpass_filter(result, cutoff_hz=3500)
            result = self.wave_distortion(result, amount=0.2)

        return result


def apply_sid_to_sound(sound, intensity='light'):
    """
    Aplica emulación SID a un pygame.mixer.Sound

    Args:
        sound: Objeto pygame.mixer.Sound
        intensity: 'light', 'medium', o 'heavy'

    Returns:
        Nuevo pygame.mixer.Sound con efectos aplicados
    """
    # Obtener array de audio
    audio_array = pygame.sndarray.array(sound)

    # Procesar
    emulator = SIDEmulator(sample_rate=44100)
    processed = emulator.process(audio_array.copy(), intensity=intensity)

    # Crear y devolver nuevo sonido
    return pygame.sndarray.make_sound(processed)
