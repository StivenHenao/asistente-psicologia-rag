from chatbot.core.gemini_service import model
from chatbot.core.redis_client import delete_session
from chatbot.core.tts_engine import speak
from chatbot.core.whisper_engine import record_audio, transcribe_audio


def chat_loop(user_id, name):
    speak(f"Hola {name}, ya estás autenticado. ¿En qué puedo ayudarte hoy?")

    while True:
        # --------- WHISPER DESACTIVADO PARA PRUEBAS ---------
        # audio = record_audio(duration=5)
        # user_input = transcribe_audio(audio).lower()
        
        # --------- entrada de texto manual ---------
        user_input = input("Escribe tu pregunta -> ").lower()
        
        print(f"Tú dijiste: {user_input}")

        if any(
            p in user_input for p in ["cerrar sesión", "salir", "adiós", "hasta luego"]
        ):
            speak("Sesión cerrada correctamente. ¡Hasta pronto!")
            delete_session()
            break

        try:
            
            # --------- uso de gemini sin intervención ni contexto ---------
            response = model.generate_content(user_input)
            ai_text = response.text.strip()
            # response = 
            # ai_text =   
            
            speak(ai_text)
            print(f"IA: {ai_text}")
        except Exception as e:
            print(f"Error con Gemini: {e}")
            speak("Lo siento, tuve un problema para responder.")
