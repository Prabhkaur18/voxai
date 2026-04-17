import whisper

# Load Whisper model
model = whisper.load_model("base")

def transcribe_audio(file_path):
    result = model.transcribe(file_path)
    return result["text"]

# Test
from intent import detect_intent, generate_code_from_text
from actions import create_file, write_code

if __name__ == "__main__":
    audio_file = "test.mp4"
    text = transcribe_audio(audio_file)

    print("Transcribed Text:")
    print(text)

    intent = detect_intent(text)
    print("Detected Intent:")
    print(intent)

    if intent == "create_file":
        result = create_file("example.txt")
        print(result)

    elif intent == "write_code":
        code = generate_code_from_text(text)
        result = write_code("generated.py", code)
        print(result)