import ast
import os
import shutil
import uuid
from urllib.parse import quote

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse

from app.utils.audio_processing import text_to_speech_file, transcribe_audio_file
from app.utils.encryption import decrypt_text
from chatbot.core.chat_chain import handle_chat_flow
from chatbot.core.gemini_service import generate_question, validate_answer
from chatbot.core.redis_client import get_session, redis_client, save_session
from chatbot.db.cursor import get_cursor
from chatbot.db.user_repository import UserRepository

router = APIRouter()

STATE_IDLE = "IDLE"
STATE_AUTH_FACTOR_1 = "AUTH_FACTOR_1"
STATE_AUTH_FACTOR_2 = "AUTH_FACTOR_2"
STATE_AUTH_FACTOR_3 = "AUTH_FACTOR_3"
STATE_AUTHENTICATED = "AUTHENTICATED"

def get_client_state(client_id):
    state = redis_client.get(f"esp32_state:{client_id}")
    return state if state else STATE_IDLE

def set_client_state(client_id, state):
    redis_client.set(f"esp32_state:{client_id}", state, ex=3600)

def get_temp_user_id(client_id):
    return redis_client.get(f"esp32_temp_user:{client_id}")

def set_temp_user_id(client_id, user_id):
    redis_client.set(f"esp32_temp_user:{client_id}", user_id, ex=3600)

@router.post("/api/esp32/interact")
async def interact(client_id: str = Form(...), audio_file: UploadFile = File(...)):
    temp_filename = f"temp_{uuid.uuid4()}.wav"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)
    
    try:
        text = transcribe_audio_file(temp_filename)
        print(f"[{client_id}] Transcription: {text}")
        
        state = get_client_state(client_id)
        response_text = ""
        next_state = state
        
        if state == STATE_IDLE:
            code = "".join(filter(str.isdigit, text))
            if len(code) == 4:
                cur = get_cursor()
                cur.execute(
                    "SELECT id, name, factor1, factor2, factor3 FROM users WHERE voice_code=%s AND active=TRUE",
                    (code,),
                )
                user = cur.fetchone()
                if user:
                    user_id, name, f1, f2, f3 = user
                    set_temp_user_id(client_id, user_id)
                    
                    factors = [decrypt_text(f) for f in (f1, f2, f3) if f]
                    redis_client.set(f"esp32_factors:{client_id}", str(factors), ex=3600)
                    
                    if len(factors) > 0:
                        question = generate_question(factors[0])
                        response_text = f"Hola {name}. {question}"
                        next_state = STATE_AUTH_FACTOR_1
                    else:
                        response_text = f"Bienvenido {name}. ¿En qué puedo ayudarte?"
                        save_session(user_id)
                        next_state = STATE_AUTHENTICATED
                else:
                    response_text = "Código no encontrado. Intente nuevamente."
            else:
                response_text = "No detecté un código válido. Por favor diga su código de 4 dígitos."
                
        elif state in [STATE_AUTH_FACTOR_1, STATE_AUTH_FACTOR_2, STATE_AUTH_FACTOR_3]:
            if any(p in text.lower() for p in ["cancelar", "salir", "adiós", "reiniciar", "abortar"]):
                response_text = "Operación cancelada. Por favor diga su código de 4 dígitos nuevamente."
                next_state = STATE_IDLE
                redis_client.delete(f"esp32_temp_user:{client_id}")
                redis_client.delete(f"esp32_factors:{client_id}")
            else:
                factors = ast.literal_eval(redis_client.get(f"esp32_factors:{client_id}"))
                
                current_factor_idx = 0
                if state == STATE_AUTH_FACTOR_2: current_factor_idx = 1
                if state == STATE_AUTH_FACTOR_3: current_factor_idx = 2
                
                current_factor = factors[current_factor_idx]
                
                if validate_answer(current_factor, text.lower()):
                    if current_factor_idx + 1 < len(factors):
                        next_factor = factors[current_factor_idx + 1]
                        question = generate_question(next_factor)
                        response_text = "Correcto. " + question
                        if current_factor_idx == 0: next_state = STATE_AUTH_FACTOR_2
                        elif current_factor_idx == 1: next_state = STATE_AUTH_FACTOR_3
                    else:
                        user_id = get_temp_user_id(client_id)
                        save_session(user_id)
                        
                        cur = get_cursor()
                        cur.execute("SELECT name FROM users WHERE id=%s", (user_id,))
                        name = cur.fetchone()[0]
                        
                        response_text = f"Autenticación exitosa. Bienvenido {name}. ¿En qué puedo ayudarte?"
                        next_state = STATE_AUTHENTICATED
                else:
                    response_text = "Respuesta incorrecta. Intente nuevamente o diga 'cancelar' para salir."
                
        elif state == STATE_AUTHENTICATED:
            user_id = get_temp_user_id(client_id)
            
            if not user_id:
                response_text = "Sesión expirada. Por favor autentíquese nuevamente."
                next_state = STATE_IDLE
            else:
                if any(p in text.lower() for p in ["cerrar sesión", "salir", "adiós"]):
                    response_text = "Hasta luego."
                    next_state = STATE_IDLE
                    redis_client.delete(f"esp32_temp_user:{client_id}")
                else:
                    user_repo = UserRepository()
                    user_data = user_repo.get_by_id(user_id)
                    user_context = user_data.context if user_data else {}
                    
                    ai_text, user_new_context = handle_chat_flow(text, user_context)
                    
                    user_repo.update(user_id, context=user_new_context)
                    response_text = ai_text

        set_client_state(client_id, next_state)
        
        next_duration = 5
        if next_state == STATE_AUTHENTICATED:
            next_duration = 10
        
        print(f"[{client_id}] Response: {response_text}")
        audio_response_path = text_to_speech_file(response_text)
        
        headers = {
            "X-Transcription": quote(text),
            "X-Response-Text": quote(response_text),
            "X-Record-Duration": str(next_duration)
        }
        
        return FileResponse(audio_response_path, media_type="audio/mpeg", filename="response.mp3", headers=headers)

    except Exception as e:
        print(f"Error processing request: {e}")
        error_audio = text_to_speech_file("Ocurrió un error interno.")
        return FileResponse(error_audio, media_type="audio/mpeg", filename="error.mp3")
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
