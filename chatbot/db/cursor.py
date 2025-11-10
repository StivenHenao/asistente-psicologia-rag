from chatbot.db.connection import get_connection


def get_cursor():
    """Devuelve un cursor funcional de la base de datos."""
    conn = get_connection()
    return conn.cursor()
