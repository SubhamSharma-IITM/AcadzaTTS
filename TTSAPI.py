from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from elevenlabs.client import ElevenLabs
import uuid
import os
import logging

# ----------------- Logging Setup -------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TTS-API")

# ----------------- FastAPI Setup -------------------
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# ----------------- ElevenLabs Setup ----------------
api_key = "sk_fc04fe3c66fc91b73b5955dd83f6f5e412a07df736bfe74e"  # Not secret for this use case
client = ElevenLabs(api_key=api_key)

VOICE_ID = "1qEiC6qsybMkmnNdVMbK"  # Monika Sogam Hindi Modulated

# ----------------- Request Schema ------------------
class ScriptRequest(BaseModel):
    script: str

# ----------------- Main TTS Endpoint ----------------
@app.post("/generate-audio")
async def generate_audio(request: ScriptRequest):
    try:
        logger.info(f"🎙️ Converting to speech: {request.script}")

        audio_stream = client.text_to_speech.convert(
            text=request.script,
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )

        # 🛠️ Convert generator to bytes
        audio_bytes = b"".join(audio_stream)

        file_id = f"voice_{uuid.uuid4().hex}.mp3"
        file_path = os.path.join("static", file_id)

        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        logger.info(f"✅ Audio saved: {file_path}")
        return JSONResponse(content={"audio_url": f"/static/{file_id}"})

    except Exception as e:
        logger.error(f"❌ Failed to generate audio: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": "Audio generation failed"})
