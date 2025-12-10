import os
from urllib.parse import urlparse, parse_qs
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

raw_dsn = os.getenv("DATABASE_URL")

if not raw_dsn:
    raise Exception("DATABASE_URL no está definida")

# Parsear la URL
result = urlparse(raw_dsn)
query_params = parse_qs(result.query)

def get_connection():
    return connect(
        dbname=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port or 5432,
        sslmode=query_params.get("sslmode", ["require"])[0],
        cursor_factory=RealDictCursor
    )

def get_cursor():
    conn = get_connection()
    return conn.cursor(), conn

def release_connection(conn):
    conn.close()
