import os
import httpx
from pathlib import Path


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio file to text using Groq Whisper API.
    Falls back to a stub if no API key is set (for testing UI).
    """
    api_key = os.getenv("GROQ_API_KEY", "")

    if not api_key:
        return _local_whisper_fallback(audio_path)

    try:
        with open(audio_path, "rb") as f:
            audio_data = f.read()

        # Detect file type from extension
        ext = Path(audio_path).suffix.lower().lstrip(".")
        mime_map = {
            "wav": "audio/wav",
            "mp3": "audio/mpeg",
            "m4a": "audio/mp4",
            "ogg": "audio/ogg",
            "flac": "audio/flac",
        }
        mime_type = mime_map.get(ext, "audio/wav")

        response = httpx.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": (Path(audio_path).name, audio_data, mime_type)},
            data={
                "model": "whisper-large-v3",
                "response_format": "text",
                "language": "en",
            },
            timeout=30.0,
        )

        if response.status_code == 200:
            return response.text.strip()
        else:
            raise Exception(f"Groq API error {response.status_code}: {response.text}")

    except Exception as e:
        return f"[Transcription error: {str(e)}]"


def _local_whisper_fallback(audio_path: str) -> str:
    """
    Local Whisper fallback using the `whisper` package.
    Only used if GROQ_API_KEY is not set.
    Install with: pip install openai-whisper
    """
    try:
        import whisper
        model = whisper.load_model("base")  # Use 'small' or 'medium' for better accuracy
        result = model.transcribe(audio_path)
        return result["text"].strip()
    except ImportError:
        return (
            "GROQ_API_KEY not set and `openai-whisper` not installed. "
            "Please set GROQ_API_KEY in your .env file or run: pip install openai-whisper"
        )
    except Exception as e:
        return f"[Local Whisper error: {str(e)}]"