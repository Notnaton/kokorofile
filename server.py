from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import io
import wave
import sounddevice as sd
import soundfile as sf
from kokoro import KPipeline, KModel
from pydantic import BaseModel
from typing import List
from pathlib import Path

app = FastAPI(title="Kokoro TTS API")

# Paths to models
CORE_MODEL_PATH = Path("models/kokoro-v1_0.pth")
VOICE_DIR = Path("models/voices")

# Pydantic models for settings
class Settings(BaseModel):
    lang_code: str = "a"    # Default: American English
    voice: str = "af_sky"  # Default voice filename

class SettingsOut(Settings):
    available_voices: List[str]

# Ensure core model exists
if not CORE_MODEL_PATH.exists():
    raise RuntimeError(f"Core model not found at {CORE_MODEL_PATH}")

# Initialize shared core model for reuse
core_model = KModel(model=str(CORE_MODEL_PATH))

# Function to create a new pipeline given language code
def create_pipeline(lang_code: str) -> KPipeline:
    return KPipeline(model=core_model, lang_code=lang_code)

# Global settings and pipeline
settings = Settings()
pipeline = create_pipeline(settings.lang_code)

def get_available_voices() -> List[str]:
    """Scan VOICE_DIR for .pt files and return filenames."""
    if not VOICE_DIR.exists():
        return []
    return [p.name for p in VOICE_DIR.glob("*.pt")]

@app.get("/settings", response_model=SettingsOut)
async def get_settings():
    """
    Retrieve current synthesis settings and available voices.
    """
    return SettingsOut(
        lang_code=settings.lang_code,
        voice=settings.voice,
        available_voices=get_available_voices()
    )

@app.post("/settings", response_model=SettingsOut)
async def update_settings(new: Settings):
    """
    Update synthesis settings: lang_code, voice. Validates voice is available.
    """
    global settings, pipeline
    voices = get_available_voices()
    if new.voice not in voices:
        raise HTTPException(status_code=400, detail=f"Voice '{new.voice}' not found. Available: {voices}")
    settings = new
    pipeline = create_pipeline(settings.lang_code)
    return SettingsOut(
        lang_code=settings.lang_code,
        voice=settings.voice,
        available_voices=voices
    )

@app.post("/synthesize_file")
async def synthesize_file(request: Request):
    """
    Synthesize the full text and return it as a WAV file.
    """
    data = await request.json()
    text = data.get("text", "").strip()
    voice = data.get("voice", settings.voice)
    if not text:
        raise HTTPException(status_code=400, detail="`text` required")

    frames = []
    for (_, _, audio) in pipeline(text, voice=voice):
        frames.append(audio)
    if not frames:
        raise HTTPException(status_code=500, detail="No audio generated")

    pcm = b"".join(f.tobytes() for f in frames)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(pcm)
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="audio/wav",
        headers={"Content-Disposition": "attachment; filename=output.wav"}
    )

@app.post("/play_live")
async def play_live(request: Request):
    """
    Synthesize text and play audio live on the server using sounddevice.
    """
    data = await request.json()
    text = data.get("text", "").strip()
    voice = data.get("voice", settings.voice)
    if not text:
        raise HTTPException(status_code=400, detail="`text` required")

    for (_, _, audio) in pipeline(text, voice=voice):
        sd.play(audio, samplerate=24000)
        sd.wait()

    return {"status": "played"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

