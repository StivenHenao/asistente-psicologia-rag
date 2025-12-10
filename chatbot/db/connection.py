import os
from urllib.parse import urlparse
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Devuelve una conexión activa parseando DATABASE_URL."""
    try:
        database_url = os.getenv("DATABASE_URL")
        
        if database_url:
            # Parsear la URL
            result = urlparse(database_url)
            conn = psycopg2.connect(
                host=result.hostname,
                database=result.path[1:],
                user=result.username,
                password=result.password,
                port=result.port or 5432,
                sslmode="require"
            )
        else:
            # Fallback a variables individuales
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                database=os.getenv("DB_NAME", "langchain_db"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "1234"),
                port=os.getenv("DB_PORT", "5432"),
            )
        
        return conn
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        raise