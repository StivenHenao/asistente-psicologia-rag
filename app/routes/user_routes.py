import json
import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.core.security import verify_api_key
from app.db import get_cursor
from app.utils.encryption import encrypt_text
from app.templates import render_template, WELCOME_EMAIL

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

class UserUpdate(BaseModel):
    email: str | None = None
    name: str | None = None
    age: int | None = None
    city: str | None = None
    factor1: str | None = None
    factor2: str | None = None
    factor3: str | None = None
    regenerate_voice_code: bool = False 
    active: bool | None = None

def generate_voice_code(cur):
    while True:
        code = "".join(secrets.choice("0123456789") for _ in range(4))
        cur.execute("SELECT id FROM users WHERE voice_code = %s", (code,))
        if not cur.fetchone():
            return code

@router.post("/users", dependencies=[Depends(verify_api_key)])
async def create_user(user: UserCreate, request: Request):
    cur = get_cursor()
    conn = cur.connection

    try:
        voice_code = generate_voice_code(cur)

        # Encriptar factores
        f1 = encrypt_text(user.factor1)
        f2 = encrypt_text(user.factor2)
        f3 = encrypt_text(user.factor3)

        cur.execute(
            """
            INSERT INTO users (email, name, age, city, factor1, factor2, factor3, voice_code, active, context)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            RETURNING id
            """,
            (user.email, user.name, user.age, user.city, f1, f2, f3, voice_code, user.active, json.dumps({"gustos": [], "actividad_favorita": None, "preferencias": {}}))
        )

        user_id = cur.fetchone()[0]

        conn.commit()
        
        # Usar el template desde archivo
        html_content = render_template(
            WELCOME_EMAIL,
            name=user.name,
            voice_code=voice_code,
            factor1=user.factor1,
            factor2=user.factor2,
            factor3=user.factor3,
        )
        
        # Acceder al servicio de email
        email_service = request.app.state.email_service
        await email_service.send_email(
            to=user.email,
            subject="Bienvenido a Gisee",
            html=html_content,
        )
        
        return {"id": user_id, "voice_code": voice_code, "message": "Usuario creado exitosamente"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/users", dependencies=[Depends(verify_api_key)])
def list_users():
    cur = get_cursor()
    cur.execute(
        "SELECT id, email, name, age, city, voice_code, active FROM users"
    )
    rows = cur.fetchall()
    users = [
        {
            "id": row[0],
            "email": row[1],
            "name": row[2],
            "age": row[3],
            "city": row[4],
            "voice_code": row[5],
            "active": row[6],
        }
        for row in rows
    ]
    return {"users": users}


@router.get("/users/{user_id}", dependencies=[Depends(verify_api_key)])
def get_user(user_id: int):
    cur = get_cursor()
    cur.execute(
        "SELECT id, email, name, age, city, voice_code, active FROM users WHERE id = %s",
        (user_id,),
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user = {
        "id": row[0],
        "email": row[1],
        "name": row[2],
        "age": row[3],
        "city": row[4],
        "voice_code": row[5],
        "active": row[6],
    }
    return {"user": user}


@router.delete("/users/{user_id}", dependencies=[Depends(verify_api_key)])
def delete_user(user_id: int):
    cur = get_cursor()
    cur.execute("DELETE FROM users WHERE id = %s RETURNING id", (user_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Usuario eliminado exitosamente", "user_id": user_id}


@router.put("/users/{user_id}", dependencies=[Depends(verify_api_key)])
async def update_user(user_id: int, user: UserUpdate, request: Request):
    cur = get_cursor()
    conn = cur.connection

    try:
        # Variables para controlar si hubo cambios en factores
        auth_changes = False
        new_voice_code = None
        updated_factors = {}
        
        # Construir consulta dinámica
        updates = []
        values = []

        if user.email is not None:
            updates.append("email = %s")
            values.append(user.email)

        if user.name is not None:
            updates.append("name = %s")
            values.append(user.name)

        if user.age is not None:
            updates.append("age = %s")
            values.append(user.age)

        if user.city is not None:
            updates.append("city = %s")
            values.append(user.city)

        if user.factor1 is not None:
            updates.append("factor1 = %s")
            encrypted_f1 = encrypt_text(user.factor1)
            values.append(encrypted_f1)
            auth_changes = True
            updated_factors['factor1'] = user.factor1

        if user.factor2 is not None:
            updates.append("factor2 = %s")
            encrypted_f2 = encrypt_text(user.factor2)
            values.append(encrypted_f2)
            auth_changes = True
            updated_factors['factor2'] = user.factor2

        if user.factor3 is not None:
            updates.append("factor3 = %s")
            encrypted_f3 = encrypt_text(user.factor3)
            values.append(encrypted_f3)
            auth_changes = True
            updated_factors['factor3'] = user.factor3

        # Manejar regeneración de voice_code
        if user.regenerate_voice_code:
            new_voice_code = generate_voice_code(cur)
            updates.append("voice_code = %s")
            values.append(new_voice_code)
            auth_changes = True

        if user.active is not None:
            updates.append("active = %s")
            values.append(user.active)

        if not updates:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")

        # Obtener datos actuales del usuario para el email
        user_data = None
        if auth_changes:
            cur.execute(
                "SELECT email, name FROM users WHERE id = %s",
                (user_id,)
            )
            user_row = cur.fetchone()
            if user_row:
                user_data = {
                    'email': user_row[0],
                    'name': user_row[1]
                }

        # Añadir ID al final
        values.append(user_id)

        query = f"""
            UPDATE users
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id
        """

        cur.execute(query, tuple(values))
        result = cur.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        conn.commit()
        
        # Preparar respuesta
        response = {"message": "Usuario actualizado exitosamente"}
        
        # Enviar email solo si hubo cambios en factores de autenticación
        if auth_changes and user_data:
            cur.execute(
                """
                SELECT 
                    COALESCE(factor1, '') as f1,
                    COALESCE(factor2, '') as f2, 
                    COALESCE(factor3, '') as f3,
                    voice_code
                FROM users WHERE id = %s
                """,
                (user_id,)
            )
            factors_row = cur.fetchone()
            
            if factors_row:
                from app.utils.encryption import decrypt_text
                
                all_factors = {
                    'factor1': decrypt_text(factors_row[0]) if factors_row[0] else '',
                    'factor2': decrypt_text(factors_row[1]) if factors_row[1] else '',
                    'factor3': decrypt_text(factors_row[2]) if factors_row[2] else '',
                    'voice_code': factors_row[3]
                }
                
                from app.templates import render_template, FACTOR_UPDATED_EMAIL
                
                html_content = render_template(
                    FACTOR_UPDATED_EMAIL,
                    name=user_data['name'],
                    factor1=all_factors['factor1'],
                    factor2=all_factors['factor2'],
                    factor3=all_factors['factor3'],
                    voice_code=all_factors['voice_code']
                )
                
                # Enviar email
                email_service = request.app.state.email_service
                await email_service.send_email(
                    to=user_data['email'],
                    subject="Tus factores de autenticación han sido actualizados",
                    html=html_content,
                )
                
                # Añadir información a la respuesta si se regeneró el código
                if user.regenerate_voice_code:
                    response["new_voice_code"] = new_voice_code
                    response["message"] = "Usuario actualizado exitosamente. Se ha enviado un email con los nuevos factores."

        return response

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
