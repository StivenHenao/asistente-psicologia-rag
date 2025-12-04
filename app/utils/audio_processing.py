import os
import tempfile
import traceback

import whisper
from gtts import gTTS

model = whisper.load_model("base")

def transcribe_audio_file(file_path: str) -> str:
    try:
        print(f"[WHISPER] Processing: {file_path}")
        
        result = model.transcribe(
            file_path, 
            fp16=False,
            language="es",
            initial_prompt="Este es un código de voz de 4 dígitos o una respuesta en español."
        )
        
        transcription = result["text"].strip()
        print(f"[WHISPER] Result: '{transcription}'")
        
        return transcription
    except Exception as e:
        print(f"[WHISPER] Error: {e}")
        traceback.print_exc()
        return ""

def text_to_speech_file(text: str) -> str:
    try:
        print(f"[TTS] Generating audio for: '{text[:50]}...'")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_path = fp.name
        
        tts = gTTS(text=text, lang="es", slow=False)
        tts.save(temp_path)
        
        print(f"[TTS] Saved to: {temp_path}")
        return temp_path
    except Exception as e:
        print(f"[TTS] Error: {e}")
        traceback.print_exc()
        return None