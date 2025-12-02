from fastapi import APIRouter, HTTPException

from app.db import get_cursor
from app.utils.encryption import decrypt_context

router = APIRouter()


@router.get("/users/{user_id}/context")
def get_user_context(user_id: int):
    cur = get_cursor()
    cur.execute(
        "SELECT structured_context, encrypted FROM user_contexts WHERE user_id = %s",
        (user_id,),
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Contexto no encontrado")
    data, encrypted = row
    return decrypt_context(data) if encrypted else data
