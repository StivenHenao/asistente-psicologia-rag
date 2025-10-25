from dotenv import load_dotenv
import os

# Cargar variables de entorno del archivo .env
load_dotenv()

from chatbot.core.redis_client import get_session, session_ttl, delete_session
from chatbot.db.cursor import get_cursor
from chatbot.auth.authentication import authenticate_user
from chatbot.chat.chat_loop import chat_loop

if __name__ == "__main__":
    user_id = get_session()

    if user_id:
        ttl = session_ttl()
        if ttl > 0:
            cur = get_cursor()
            cur.execute("SELECT name FROM users WHERE id=%s", (user_id,))
            user = cur.fetchone()
            if user:
                name = user[0]
                print(f"✅ Sesión encontrada para {name} (expira en {ttl // 60} min)")
                chat_loop(user_id, name)
            else:
                delete_session()
                authenticate_user()
        else:
            print("⏰ Sesión expirada. Reautenticando...")
            delete_session()
            authenticate_user()
    else:
        authenticate_user()
