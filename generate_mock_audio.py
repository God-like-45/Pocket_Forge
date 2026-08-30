import wave
import struct
import math
import os

def generate_tone(filename, frequency, duration, volume=0.5):
    sample_rate = 44100
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(int(sample_rate * duration)):
            # Basic sine wave
            value = int(volume * 32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            # Add some harmonics for "texture" based on the track type
            if "tense" in filename:
                value += int(volume * 15000.0 * math.sin(2.0 * math.pi * (frequency * 1.5) * i / sample_rate))
            elif "action" in filename:
                value += int(volume * 20000.0 * math.sin(2.0 * math.pi * (frequency * 2.0) * i / sample_rate))
                
            data = struct.pack('<h', max(-32768, min(32767, value)))
            wav_file.writeframesraw(data)

if __name__ == "__main__":
    print("Generating mock BGM tracks...")
    # Tense: Low, brooding drone
    generate_tone("static/bgm/tense.wav", 65.41, 5.0, 0.3) 
    # Action: Higher pitched, slightly more aggressive
    generate_tone("static/bgm/action.wav", 110.0, 5.0, 0.4)
    # Calm: Soothing mid-tone
    generate_tone("static/bgm/calm.wav", 220.0, 5.0, 0.2)
    print("Done! Saved to static/bgm/")
