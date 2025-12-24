"""
Genera un sonido de helicóptero estilo 8-bit loopeable
"""
import numpy as np
import wave
import struct

def generate_helicopter_sound(filename, duration=2.0, sample_rate=22050):
    """
    Genera un sonido de helicóptero 8-bit loopeable

    Args:
        filename: Nombre del archivo a guardar
        duration: Duración en segundos
        sample_rate: Frecuencia de muestreo
    """
    # Generar array de tiempo
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Componente 1: Motor base - frecuencias medias/altas
    # Frecuencia base del motor (aumentada para remover graves)
    motor_freq = 200  # Hz - sonido medio-agudo del motor
    motor_sound = np.sin(2 * np.pi * motor_freq * t)

    # Añadir armónicos en frecuencias más altas
    motor_sound += 0.4 * np.sin(2 * np.pi * motor_freq * 1.5 * t)
    motor_sound += 0.3 * np.sin(2 * np.pi * motor_freq * 2.2 * t)

    # Componente 2: Aspas "whop whop whop"
    # Frecuencia de rotación de las aspas (más lento que el motor)
    blade_freq = 8  # Hz - 8 golpes por segundo

    # Crear pulsos para las aspas usando una onda cuadrada modificada
    blade_sound = np.zeros_like(t)
    for i in range(int(blade_freq * duration)):
        # Posición del pulso
        pulse_time = i / blade_freq
        pulse_idx = int(pulse_time * sample_rate)
        pulse_width = int(0.05 * sample_rate)  # Pulso de 50ms

        if pulse_idx + pulse_width < len(blade_sound):
            # Crear envolvente del pulso
            envelope = np.exp(-np.linspace(0, 8, pulse_width))
            # Frecuencia del pulso (más aguda - aumentada para remover graves)
            pulse_freq = 400 + 150 * np.sin(2 * np.pi * blade_freq * pulse_time)
            pulse = np.sin(2 * np.pi * pulse_freq * np.linspace(0, 0.05, pulse_width))
            blade_sound[pulse_idx:pulse_idx+pulse_width] += pulse * envelope

    # Componente 3: Ruido de aire (whoosh)
    # Generar ruido rosa para simular el aire
    np.random.seed(42)  # Para reproducibilidad
    noise = np.random.uniform(-1, 1, len(t))

    # Filtrar el ruido para hacerlo más suave (filtro de media móvil simple)
    window_size = 20
    noise = np.convolve(noise, np.ones(window_size)/window_size, mode='same')

    # Modular el ruido con el ritmo de las aspas
    noise_modulation = 0.5 + 0.5 * np.sin(2 * np.pi * blade_freq * t)
    noise = noise * noise_modulation * 0.3

    # Mezclar todos los componentes (motor reducido, más énfasis en aspas)
    helicopter = (
        motor_sound * 0.25 +     # Motor base reducido
        blade_sound * 0.55 +     # Aspas dominantes
        noise * 0.35             # Ruido de aire aumentado
    )

    # Normalizar para evitar clipping
    helicopter = helicopter / np.max(np.abs(helicopter))

    # Aplicar fade in/out muy corto para suavizar el loop
    fade_samples = int(0.01 * sample_rate)  # 10ms fade
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)

    helicopter[:fade_samples] *= fade_in
    helicopter[-fade_samples:] *= fade_out

    # Escalar a 16-bit (simular 8-bit pero guardar como 16-bit para compatibilidad)
    # Reducir resolución para efecto 8-bit
    helicopter = np.round(helicopter * 127) / 127  # Simular 8-bit (valores -1 a 1 en 256 pasos)
    helicopter = np.int16(helicopter * 32767)

    # Guardar como WAV
    with wave.open(filename, 'w') as wav_file:
        # Configurar parámetros: mono, 16-bit
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 2 bytes = 16 bit
        wav_file.setframerate(sample_rate)

        # Escribir datos
        for sample in helicopter:
            wav_file.writeframes(struct.pack('<h', sample))

    print(f"Sonido de helicoptero generado: {filename}")
    print(f"  Duracion: {duration}s")
    print(f"  Sample rate: {sample_rate}Hz")
    print(f"  Loopeable: Si (con fade de 10ms)")

if __name__ == "__main__":
    generate_helicopter_sound("sounds/helicopter.wav", duration=2.0)
