from cryptography.fernet import Fernet
import os, json

key = os.getenv("CONTEXT_ENCRYPTION_KEY")
if not key:
    raise ValueError("❌ Falta la variable de entorno CONTEXT_ENCRYPTION_KEY")

fernet = Fernet(key.encode())

def encrypt_text(text: str) -> str:
    """Cifra un texto plano (factor, palabra, etc.)"""
    return fernet.encrypt(text.encode()).decode()

def decrypt_text(token: str) -> str:
    """Descifra un texto cifrado"""
    try:
        return fernet.decrypt(token.encode()).decode()
    except Exception as e:
        print(f"❌ Error al descifrar token: {token[:50]}... -> {e}")
        raise

def encrypt_context(context_dict):
    data = json.dumps(context_dict)
    return fernet.encrypt(data.encode()).decode()

def decrypt_context(encrypted_str):
    data = fernet.decrypt(encrypted_str.encode()).decode()
    return json.loads(data)
