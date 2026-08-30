import os
import asyncio
import edge_tts

STATIC_DIR = os.path.join(os.getcwd(), "static", "audio")
os.makedirs(STATIC_DIR, exist_ok=True)

# A simple map for character to voice. In a real app, this might be saved in the database.
VOICE_MAP = {
    "NARRATOR": "en-US-AriaNeural",
    "Dr. Aris": "en-GB-SoniaNeural", # Or male voice if appropriate, edge-tts has many. E.g. "en-GB-RyanNeural"
    "Captain Vance": "en-US-ChristopherNeural"
}

DEFAULT_VOICE = "en-US-GuyNeural"

async def generate_line_audio(job_id: int, index: int, speaker: str, text: str) -> str:
    """Generates an MP3 chunk for a single line using edge-tts."""
    
    file_name = f"chunk_{job_id}_{index}.mp3"
    file_path = os.path.join(STATIC_DIR, file_name)
    
    # Idempotency: skip if already downloaded
    if os.path.exists(file_path):
        return file_path
        
    voice = VOICE_MAP.get(speaker, DEFAULT_VOICE)
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file_path)
    
    return file_path

def merge_audio(job_id: int, chunk_paths: list[str]) -> str:
    """Merges all mp3 chunks sequentially by appending bytes and returns the static URL."""
    
    if not chunk_paths:
        return ""
        
    final_file_name = f"final_{job_id}.mp3"
    final_file_path = os.path.join(STATIC_DIR, final_file_name)
    
    with open(final_file_path, 'wb') as outfile:
        for path in chunk_paths:
            with open(path, 'rb') as infile:
                outfile.write(infile.read())
                
    return f"/static/audio/{final_file_name}"
