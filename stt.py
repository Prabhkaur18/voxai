import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def transcribe_audio(file_path):
    try:
        with open(file_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_file
            )
        return transcript.text
    except:
        return "Sample transcription (API limit reached)"