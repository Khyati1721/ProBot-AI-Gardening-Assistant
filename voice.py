from gtts import gTTS
import tempfile
import whisper
import os


def text_to_speech(text, accent):
    tts = gTTS(text=text, lang=accent)
    tts.save("output.mp3")
    return "output.mp3"

# Transcribe audio using Whisper
def transcribe(audio_file):
    extension = audio_file.name.split(".")[-1]

    # Store uploaded audio in a temporary file for Whisper
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}") as tmpfile:
        file_path = tmpfile.name
        tmpfile.write(audio_file.read())

    try:
        result = model.transcribe(file_path)
        return result['text']

    except Exception as e:
        return e

    finally:
        # Remove temporary file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

model = whisper.load_model('base')

