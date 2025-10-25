import os
import tempfile
import time
import pygame
from gtts import gTTS

def speak(text: str):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_path = fp.name

        tts = gTTS(text=text, lang="es", slow=False)
        tts.save(temp_path)

        pygame.mixer.init()
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pygame.mixer.quit()
        os.remove(temp_path)

    except Exception as e:
        print(f"[Error al hablar] {e}")
        print(f"(Mensaje que intentó decir: {text})")
