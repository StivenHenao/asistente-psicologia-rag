import os
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv

load_dotenv()

raw_dsn = os.getenv("DATABASE_URL")

if not raw_dsn:
    raise Exception("DATABASE_URL no está definida")

# Parsear la URL
result = urlparse(raw_dsn)

conn = psycopg2.connect(
    dbname=result.path[1:],  # eliminar la /
    user=result.username,
    password=result.password,
    host=result.hostname,
    port=result.port,
)

conn.autocommit = True


def get_cursor():
    return conn.cursor()
