import time

from app.utils.encryption import decrypt_text
from chatbot.chat.chat_loop import chat_loop
from chatbot.core.gemini_service import generate_question, validate_answer
from chatbot.core.redis_client import save_session
from chatbot.core.tts_engine import speak
from chatbot.core.whisper_engine import record_audio, transcribe_audio
from chatbot.db.cursor import get_cursor


def record_and_transcribe_code():
    speak("Por favor, diga su código de voz de cuatro dígitos.")
    audio = record_audio(duration=5)
    code = "".join(filter(str.isdigit, transcribe_audio(audio)))
    return code if len(code) == 4 else None


def authenticate_user():
    cur = get_cursor()

    # Paso 1: voz
    while True:
        code = record_and_transcribe_code()
        print("🔢 Código detectado:", code)

        if not code:
            speak("No se detectó un código válido. Intenta de nuevo.")
            continue

        cur.execute(
            "SELECT id, name, factor1, factor2, factor3 FROM users WHERE voice_code=%s AND active=TRUE",
            (code,),
        )
        user = cur.fetchone()

        if user:
            print("✅ Usuario encontrado:", user[1])
            break
        else:
            speak("Código inválido. Intenta nuevamente.")

    user_id, name, f1, f2, f3 = user
    factors = [decrypt_text(f) for f in (f1, f2, f3) if f]

    for factor in factors:
        print("🔐 Verificando factor:", factor)
        question = generate_question(factor)
        while True:
            speak(question)
            audio = record_audio(duration=5)
            answer = transcribe_audio(audio).lower()
            print(f"🎤 Tú dijiste: {answer}")
            if validate_answer(factor, answer):
                speak("Perfecto, continuemos.")
                break
            speak("Respuesta incorrecta, intenta nuevamente.")
            time.sleep(1)

    speak(f"Autenticación exitosa. Bienvenido, {name}.")
    save_session(user_id)
    chat_loop(user_id, name)
