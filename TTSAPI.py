from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os
import uuid
import logging
from elevenlabs.client import ElevenLabs

# 🧠 Hardcoded API key and voice config (as per your instruction)
ELEVENLABS_API_KEY = "sk_fc04fe3c66fc91b73b5955dd83f6f5e412a07df736bfe74e"
VOICE_ID = "1qEiC6qsybMkmnNdVMbK"  # Monika Sogam Hindi Modulated
MODEL_ID = "eleven_multilingual_v2"

# Static folder setup (Render requires this to exist)
os.makedirs("static", exist_ok=True)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TTS-API")

# FastAPI app
app = FastAPI()

# Request body format
class TTSRequest(BaseModel):
    script: str

# POST endpoint
@app.post("/generate-audio")
def generate_audio(data: TTSRequest):
    script = data.script
    logger.info("🎙️ Converting to speech: %s", script)

    try:
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio = client.text_to_speech.convert(
            text=script,
            voice_id=VOICE_ID,
            model_id=MODEL_ID,
            output_format="mp3_44100_128"
        )

        filename = f"voice_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join("static", filename)
        with open(filepath, "wb") as f:
            f.write(audio)

        logger.info("✅ Audio saved: %s", filepath)
        return {"audio_url": f"/static/{filename}"}

    except Exception as e:
        logger.error("❌ Failed to generate audio: %s", str(e))
        raise HTTPException(status_code=500, detail="Audio generation failed")

# Serve audio files
@app.get("/static/{filename}")
def serve_audio(filename: str):
    filepath = os.path.join("static", filename)
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type="audio/mpeg")
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")
