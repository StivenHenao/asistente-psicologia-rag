import os
import whisper
import sounddevice as sd
import numpy as np
import tempfile
from gtts import gTTS
import time
import google.generativeai as genai
from app.db import get_cursor
import pygame
import redis
from app.utils.encryption import decrypt_text

# Inicializar redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


# Configuración de Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY', ''))
genie_model = genai.GenerativeModel("models/gemini-2.5-flash")

# Inicialización de Whisper
whisper_model = whisper.load_model("base")


# Funciones de voz (gTTS)
def speak(text: str):
    """Convierte texto a voz usando gTTS (voz natural) sin bloqueo en Windows."""
    try:
        # Crear archivo temporal cerrado (para evitar bloqueo)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_path = fp.name

        # Generar voz
        tts = gTTS(text=text, lang="es", slow=False)
        tts.save(temp_path)

        # Reproducir audio
        pygame.mixer.init()
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()

        # Esperar hasta que termine
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pygame.mixer.quit()
        os.remove(temp_path)

    except Exception as e:
        print(f"[Error al hablar] {e}")
        print(f"(Mensaje que intentó decir: {text})")



# Audio y transcripción
def record_audio(duration=3, fs=16000):
    """Graba audio y devuelve array numpy."""
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    return np.squeeze(recording)


def transcribe_audio(audio):
    """Transcribe audio con Whisper y devuelve texto."""
    result = whisper_model.transcribe(audio, fp16=False)
    return result['text'].strip()


def record_and_transcribe_code(duration=5):
    """Graba y transcribe el código de voz de 4 dígitos."""
    speak("Por favor, diga su código de voz de cuatro dígitos.")
    audio = record_audio(duration)
    code = ''.join(filter(str.isdigit, transcribe_audio(audio)))
    if not code or len(code) != 4:
        print(f"Código inválido detectado: {code}")
        return None
    print(f"Transcripción detectada: {code}")
    return code


def record_and_transcribe_answer(prompt, duration=5):
    """Pregunta algo con voz y devuelve respuesta transcrita."""
    speak(prompt)
    audio = record_audio(duration)
    answer = transcribe_audio(audio).lower()
    print(f"Respuesta detectada: {answer}")
    return answer


# Funciones con Gemini
def generate_question_from_factor(factor_value):
    """
    Analiza el tipo de dato del factor y genera una pregunta natural y contextual.
    Ejemplo: 'azul' -> '¿Cuál es tu color favorito?'
             'Medellín' -> '¿En qué ciudad vives?'
             'perro' -> '¿Tienes alguna mascota? ¿Cuál?'
    """
    prompt = (
        f"El usuario tiene un factor de seguridad con valor '{factor_value}'. "
        "Analiza qué tipo de dato es (color, animal, ciudad, fecha, comida, nombre, etc.) "
        "y genera una sola pregunta natural, corta y fluida en español "
        "que permita confirmar ese valor sin mencionarlo directamente. "
        "Ejemplo: si el factor es 'azul', pregunta '¿Cuál es tu color favorito?'; "
        "si el factor es 'Bogotá', pregunta '¿En qué ciudad vives?'; "
        "si es 'pizza', pregunta '¿Cuál es tu comida favorita?'. "
        "Devuelve solo la pregunta, sin explicaciones."
    )
    try:
        response = genie_model.generate_content(prompt)
        question = response.text.strip()

        # Limpiar caracteres o saltos
        if "\n" in question:
            question = question.split("\n")[0].strip("-* ").strip()
        if not question.endswith("?"):
            question += "?"

        print(f"Pregunta generada automáticamente: {question}")
        return question
    except Exception as e:
        print(f"Error con Gemini: {e}")
        return f"Por favor responde algo relacionado con {factor_value}."


def validate_answer_with_gemini(factor_value, answer):
    """
    Usa comprensión semántica con Gemini para evaluar si la respuesta
    tiene relación o similitud con el valor del factor.
    """
    prompt = (
        f"Compara semánticamente si la respuesta '{answer}' tiene relación "
        f"con el valor esperado '{factor_value}'. "
        "Por ejemplo, si el factor es 'azul' y la respuesta es 'mi color favorito es azul', "
        "debe considerarse como correcta. "
        "Responde solo con 'sí' si coinciden o 'no' si no coinciden."
    )
    try:
        response = genie_model.generate_content(prompt)
        result = response.text.strip().lower()
        print(f"Gemini analizó similitud: {result}")
        return "sí" in result
    except Exception as e:
        print(f"Error con Gemini: {e}")
        return False


# Lógica de autenticación
def authenticate_user():
    cur = get_cursor()

    # Paso 1: Código de voz
    while True:
        code = record_and_transcribe_code(duration=5)
        if not code:
            speak("No se detectó un código válido. Por favor, intenta nuevamente.")
            time.sleep(1)
            continue

        cur.execute(
            "SELECT id, name, factor1, factor2, factor3 FROM users WHERE voice_code=%s AND active=TRUE",
            (code,)
        )
        user = cur.fetchone()

        if user:
            break
        else:
            speak("Código inválido o usuario inactivo. Intenta nuevamente.")
            time.sleep(1)

    user_id, name, f1, f2, f3 = user
    f1 = decrypt_text(f1) if f1 else None
    f2 = decrypt_text(f2) if f2 else None
    f3 = decrypt_text(f3) if f3 else None
    print(f"Usuario detectado: {name}")

    # Paso 2: Autenticación por factores
    for factor in [f1, f2, f3]:
        if not factor:
            continue

        question = generate_question_from_factor(factor)

        # Repetir hasta que la respuesta sea válida
        while True:
            speak(question)
            answer = record_and_transcribe_answer("", duration=5)

            valid = validate_answer_with_gemini(factor, answer)
            if valid:
                speak("Perfecto, continuemos.")
                time.sleep(0.8)
                break  # Sale del bucle y pasa al siguiente factor
            else:
                speak("Tu respuesta no coincide con lo que esperaba. Intenta nuevamente.")
                print(f"Respuesta incorrecta para el factor: {factor}")
                time.sleep(1)  # Pausa antes de repetir

    # Paso 3: Éxito
    speak(f"Autenticación exitosa. Bienvenido, {name}.")
    print(f"✅ Autenticación exitosa para {name}")

    # 🧠 Paso 4: Guardar sesión en Redis
    redis_client.set("auth_user_id", user_id)
    print(f"🗝️ Sesión guardada en Redis para el usuario {name} (ID: {user_id})")

    # Paso 5 (opcional): Continuar con el chat automáticamente
    chat_loop(user_id, name)

    

def chat_loop(user_id, name):
    """Modo conversación con la IA tras autenticación."""
    speak(f"Hola {name}, ya estás autenticado. ¿En qué puedo ayudarte hoy?")
    
    while True:
        audio = record_audio(duration=5)
        user_input = transcribe_audio(audio).lower()
        print(f"Tú dijiste: {user_input}")

        # Palabras clave para cerrar sesión
        if any(palabra in user_input for palabra in ["cerrar sesión", "salir", "adiós", "chao", "hasta luego"]):
            speak("Sesión cerrada correctamente. ¡Hasta pronto!")
            redis_client.delete("auth_user_id")
            break

        # Generar respuesta natural con Gemini
        try:
            response = genie_model.generate_content(user_input + "\nPor favor, responde de manera clara y concisa.")
            ai_text = response.text.strip()
            speak(ai_text)
            print(f"IA: {ai_text}")
        except Exception as e:
            print(f"Error con Gemini: {e}")
            speak("Lo siento, tuve un problema para responder.")


# Ejecución principal
if __name__ == "__main__":
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    user_id = redis_client.get("auth_user_id")

    if user_id:
        cur = get_cursor()
        cur.execute("SELECT name FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()
        if user:
            name = user[0]
            print(f"✅ Sesión encontrada para {name}")
            chat_loop(user_id, name)
        else:
            print("⚠️ Usuario no encontrado, autenticando de nuevo.")
            redis_client.delete("auth_user_id")
            authenticate_user()
    else:
        authenticate_user()