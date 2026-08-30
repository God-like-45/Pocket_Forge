import wave
import struct
import math
import os

def generate_sfx(filename, effect_type):
    sample_rate = 44100
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        duration = 1.0
        if effect_type == "door":
            duration = 0.5
        elif effect_type == "laser":
            duration = 0.3
            
        for i in range(int(sample_rate * duration)):
            t = i / sample_rate
            value = 0
            if effect_type == "alarm":
                # Siren sweep
                freq = 800 + 400 * math.sin(10 * math.pi * t)
                value = int(0.6 * 32767.0 * math.sin(2.0 * math.pi * freq * t))
            elif effect_type == "explosion":
                # Noise burst with decay
                import random
                noise = random.uniform(-1.0, 1.0)
                decay = math.exp(-5 * t)
                value = int(0.8 * 32767.0 * noise * decay)
            elif effect_type == "laser":
                # High pitch frequency drop
                freq = 2000 - 4000 * t
                if freq < 100: freq = 100
                value = int(0.5 * 32767.0 * math.sin(2.0 * math.pi * freq * t))
            elif effect_type == "door":
                # Low frequency slide
                freq = 300 - 200 * t
                value = int(0.7 * 32767.0 * math.sin(2.0 * math.pi * freq * t))
                
            data = struct.pack('<h', max(-32768, min(32767, value)))
            wav_file.writeframesraw(data)

if __name__ == "__main__":
    print("Generating mock SFX tracks...")
    generate_sfx("static/sfx/alarm.wav", "alarm")
    generate_sfx("static/sfx/explosion.wav", "explosion")
    generate_sfx("static/sfx/laser.wav", "laser")
    generate_sfx("static/sfx/door.wav", "door")
    print("Done! Saved to static/sfx/")
