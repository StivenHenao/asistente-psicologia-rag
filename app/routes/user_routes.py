import json
import secrets

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import verify_api_key
from app.db import get_cursor
from app.utils.encryption import encrypt_text

router = APIRouter()


class UserCreate(BaseModel):
    email: str
    name: str
    age: int
    city: str
    factor1: str
    factor2: str
    factor3: str
    active: bool = True


def generate_voice_code(cur):
    while True:
        code = "".join(secrets.choices("0123456789", k=4))
        cur.execute("SELECT id FROM users WHERE voice_code = %s", (code,))
        if not cur.fetchone():
            return code


@router.post("/users")
def create_user(user: UserCreate, dependencies=[Depends(verify_api_key)]):
    cur = get_cursor()
    voice_code = generate_voice_code(cur)

    try:
        # Encriptar los tres factores
        f1 = encrypt_text(user.factor1)
        f2 = encrypt_text(user.factor2)
        f3 = encrypt_text(user.factor3)

        cur.execute(
            """
            INSERT INTO users (email, name, age, city, factor1, factor2, factor3, voice_code, active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                user.email,
                user.name,
                user.age,
                user.city,
                f1,
                f2,
                f3,
                voice_code,
                user.active,
            ),
        )
        user_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO user_contexts (user_id, structured_context, encrypted) VALUES (%s, %s::jsonb, FALSE)",
            (
                user_id,
                json.dumps(
                    {"gustos": [], "actividad_favorita": None, "preferencias": {}}
                ),
            ),
        )

        return {
            "id": user_id,
            "voice_code": voice_code,
            "message": "Usuario creado exitosamente",
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
