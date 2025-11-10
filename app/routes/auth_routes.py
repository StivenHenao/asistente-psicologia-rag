from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db import get_cursor
from app.utils.whisper_utils import record_and_transcribe

router = APIRouter()


class VoiceAuthRequest(BaseModel):
    voice_code: str = None  # opcional si usas Whisper
    factor1: str
    factor2: str
    factor3: str


@router.post("/auth/verify-voice")
def verify_voice(body: VoiceAuthRequest):
    cur = get_cursor()

    # Si no se pasa voice_code, usar Whisper
    voice_code = body.voice_code or record_and_transcribe()

    cur.execute(
        "SELECT id, factor1, factor2, factor3, active FROM users WHERE voice_code = %s",
        (voice_code,),
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user_id, f1, f2, f3, active = row

    if not active:
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    if body.factor1 != f1 or body.factor2 != f2 or body.factor3 != f3:
        raise HTTPException(status_code=401, detail="Factores incorrectos")

    # Cargar contexto
    cur.execute(
        "SELECT structured_context, encrypted FROM user_contexts WHERE user_id = %s",
        (user_id,),
    )
    context_row = cur.fetchone()
    context = context_row[0] if context_row else {}

    return {"message": "Autenticación exitosa", "user_id": user_id, "context": context}
