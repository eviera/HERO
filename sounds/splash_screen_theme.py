###
### de https://gemini.google.com/share/e75c02cbc2ef
###


from midiutil import MIDIFile

def create_abab_dark_midi():
    filename = "./sounds/splash_screen_theme.mid"
    track_count = 3
    tempo = 135
    
    # Estructura: A (16 compases) - B (16 compases) - A (16 compases) - B (16 compases)
    # Total = 64 compases. A 135 BPM son aprox 1 minuto 55 segundos.
    total_measures = 64
    
    midi = MIDIFile(track_count)
    
    # --- CONFIGURACIÓN DE PISTAS ---
    for i in range(track_count):
        midi.addTempo(i, 0, tempo)

    # Track 0: Lead (Sawtooth)
    midi.addProgramChange(0, 0, 0, 81)
    # Track 1: Bass (Synth Bass 2)
    midi.addProgramChange(1, 1, 0, 39)
    # Track 2: Drums (Standard Kit) - No necesita program change, es canal 9

    # ==========================================
    # DEFINICIÓN DE LA PARTE A (La que te gustó)
    # ==========================================
    
    # Progresión A: Am - F - Dm - E (Acción clásica)
    chords_A = [(45, 'minor'), (41, 'major'), (38, 'minor'), (40, 'major')]
    
    # Bajo A: Galope (Corchea, dos semicorcheas...)
    bass_pattern_A = [
        (0.0, 0, 0.25),  (0.25, 0, 0.25),  (0.5, 12, 0.25), (0.75, 0, 0.25),
        (1.0, 0, 0.25),  (1.25, 0, 0.25),  (1.5, 12, 0.25), (1.75, 0, 0.25),
        (2.0, 0, 0.25),  (2.25, 0, 0.25),  (2.5, 12, 0.25), (2.75, 0, 0.25),
        (3.0, 0, 0.25),  (3.25, 0, 0.25),  (3.5, 12, 0.25), (3.75, 0, 0.25)
    ]
    
    # Melodía A: Rítmica y pegadiza
    melody_pattern_A = [
        (0.0, 0, 0.75), (0.75, 0, 0.25), (1.0, 7, 0.5), (1.5, 3, 0.5),
        (2.0, 0, 0.5),  (2.5, 7, 0.25), (2.75, 12, 0.25), (3.0, 7, 0.5), (3.5, 3, 0.5)
    ]

    # ==========================================
    # DEFINICIÓN DE LA PARTE B ("Más Dark")
    # ==========================================
    
    # Progresión B: F - E - F - E (Tensión oscilante, sonido 'maligno')
    # Nota: El acorde E Mayor tiene G#, que choca contra la escala de Am.
    chords_B = [(41, 'major'), (40, 'major'), (41, 'major'), (40, 'major')]
    
    # Bajo B: "Machine Gun" (Semicorcheas constantes y pesadas)
    # Sin saltos de octava, puro machaque en la nota grave.
    bass_pattern_B = []
    for k in range(16):
        bass_pattern_B.append((k * 0.25, 0, 0.25)) # (offset, intervalo, duracion)

    # Melodía B: Descendente y más sostenida (tipo alarma/fatalidad)
    # Empieza en la octava aguda (12) y baja hacia la quinta (7) y tercera (3)
    melody_pattern_B = [
        (0.0, 12, 0.5), (0.5, 12, 0.5),   # Golpes agudos
        (1.0, 7, 0.5),  (1.5, 7, 0.5),    # Bajando
        (2.0, 3, 1.0),                    # Sostener nota tensa
        (3.0, 0, 0.25), (3.25, 3, 0.25), (3.5, 7, 0.25), (3.75, 12, 0.25) # Arpegio rápido final
    ]

    # ==========================================
    # MOTOR DE GENERACIÓN
    # ==========================================

    current_measure = 0
    
    while current_measure < total_measures:
        measure_start_beat = current_measure * 4
        
        # Determinar si estamos en parte A o B
        # Estructura A (0-15), B (16-31), A (32-47), B (48-63)
        section_idx = current_measure % 32 # Ciclo de 32 compases (A+B)
        is_part_a = section_idx < 16
        
        # Seleccionar patrones según la sección
        if is_part_a:
            chord_data = chords_A[current_measure % 4]
            bass_pat = bass_pattern_A
            melody_pat = melody_pattern_A
        else:
            chord_data = chords_B[current_measure % 4]
            bass_pat = bass_pattern_B
            melody_pat = melody_pattern_B

        root_note = chord_data[0]
        chord_type = chord_data[1]
        
        # Ajuste de intervalo de tercera (Mayor vs Menor)
        tercera = 4 if chord_type == 'major' else 3

        # --- 1. BATERÍA (Común a ambas partes para mantener cohesión) ---
        # Bombo 4 on the floor
        for b in range(4):
            midi.addNote(2, 9, 36, measure_start_beat + b, 1, 120)
        # Snare fuerte en 2 y 4
        midi.addNote(2, 9, 38, measure_start_beat + 1, 1, 127)
        midi.addNote(2, 9, 38, measure_start_beat + 3, 1, 127)
        # Hi-Hats
        for h in range(8):
            midi.addNote(2, 9, 42, measure_start_beat + (h * 0.5), 0.5, 90)
        
        # Crash al inicio de cada cambio de sección (cada 16 compases)
        if current_measure % 16 == 0:
             midi.addNote(2, 9, 49, measure_start_beat, 2, 115)

        # --- 2. BAJO ---
        for note_def in bass_pat:
            offset, interval, dur = note_def
            # Velocidad: Si es parte B, tocamos un poco más fuerte (115 vs 105)
            vel = 115 if not is_part_a else 105 
            midi.addNote(1, 1, root_note - 12 + interval, measure_start_beat + offset, dur, vel)

        # --- 3. MELODÍA ---
        for note_def in melody_pat:
            offset, interval_rel, dur = note_def
            
            # Mapeo de intervalos inteligentes
            real_interval = interval_rel
            if interval_rel == 3: real_interval = tercera
            
            # En la parte B, subimos la melodía una octava extra para que chille más si es necesario
            # Pero aquí mantendremos +12 para consistencia, o +24 para dramatismo.
            # Dejémoslo en +12 para que suene 'gordo' con el sinte.
            base_octave = 12
            
            midi.addNote(0, 0, root_note + base_octave + real_interval, measure_start_beat + offset, dur, 110)

        current_measure += 1

    with open(filename, "wb") as output_file:
        midi.writeFile(output_file)
    print(f"Generado: {filename}")
    print("Estructura: A (16) -> B (16) -> A (16) -> B (16)")

if __name__ == "__main__":
    create_abab_dark_midi()