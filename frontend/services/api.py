import streamlit as st
import requests
import time
import secrets
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env (busca en directorios padres si es necesario)
load_dotenv()

# Datos Mock estáticos para cuando el servidor no responde o está en modo demo
MOCK_USERS = [
    {"id": 1, "email": "ana.perez@example.com", "name": "Ana Pérez", "age": 28, "city": "Bogotá", "voice_code": "4821", "active": True},
    {"id": 2, "email": "carlos.ruiz@example.com", "name": "Carlos Ruiz", "age": 35, "city": "Medellín", "voice_code": "9102", "active": True},
    {"id": 3, "email": "maria.gonzalez@example.com", "name": "María González", "age": 22, "city": "Cali", "voice_code": "3341", "active": False},
    {"id": 4, "email": "david.l@example.com", "name": "David López", "age": 41, "city": "Bogotá", "voice_code": "1192", "active": True},
    {"id": 5, "email": "laura.s@example.com", "name": "Laura Silva", "age": 29, "city": "Barranquilla", "voice_code": "5501", "active": True},
]

class ApiService:
    """
    Servicio centralizado para manejar peticiones HTTP a la API FastAPI.
    Incluye lógica de 'Mock' para desarrollo frontend independiente del backend.
    """
    BASE_URL = "http://localhost:8000"
    
    # AQUI ESTÁ LA MAGIA: Leemos la variable de entorno, si no existe, usa una por defecto (o lanza error)
    API_KEY = os.getenv("API_KEY") 

    @staticmethod
    def get_headers():
        # Verificación de seguridad simple
        if not ApiService.API_KEY:
            st.error("⚠️ Error crítico: No se encontró la API_KEY en el archivo .env")
            return {}
            
        return {"X-API-Key": ApiService.API_KEY, "Content-Type": "application/json"}

    @staticmethod
    def get_users():
        # Verificar estado en sesión
        if st.session_state.get('use_mock', True):
            return MOCK_USERS
            
        try:
            res = requests.get(f"{ApiService.BASE_URL}/users", headers=ApiService.get_headers())
            if res.status_code == 200:
                return res.json().get('users', [])
            return []
        except Exception as e:
            st.toast(f"Error de conexión: {e}", icon="❌")
            return []

    @staticmethod
    def create_user(data):
        if st.session_state.get('use_mock', True):
            time.sleep(1) # Simular latencia de red
            new_id = len(MOCK_USERS) + 1
            # Usamos secrets que es criptográficamente seguro y SonarCloud lo ama
            voice_code = "".join(secrets.choice("0123456789") for _ in range(4))
            # Crear copia local para la sesión
            mock_user = {
                "id": new_id, 
                "email": data['email'], 
                "name": data['name'], 
                "age": data['age'], 
                "city": data['city'], 
                "voice_code": voice_code, 
                "active": True
            }
            MOCK_USERS.append(mock_user)
            return {"success": True, "voice_code": voice_code}
            
        try:
            res = requests.post(f"{ApiService.BASE_URL}/users", json=data, headers=ApiService.get_headers())
            if res.status_code == 200:
                return {"success": True, "data": res.json(), "voice_code": res.json().get('voice_code')}
            return {"success": False, "error": res.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    # Aquí puedes agregar update_user y delete_user siguiendo el mismo patrón...
    @staticmethod
    def delete_user(user_id):
        if st.session_state.get('use_mock', True):
            # Simular borrado en la lista mock
            global MOCK_USERS
            MOCK_USERS = [u for u in MOCK_USERS if u['id'] != user_id]
            return {"success": True}
            
        try:
            res = requests.delete(f"{ApiService.BASE_URL}/users/{user_id}", headers=ApiService.get_headers())
            if res.status_code == 200:
                return {"success": True}
            return {"success": False, "error": res.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
        
        
    @staticmethod
    def update_user(user_id, data):
        """Actualiza los datos de un usuario existente"""
        
        # 1. Lógica MOCK (Modo Demo)
        if st.session_state.get('use_mock', True):
            time.sleep(0.5)
            # Buscamos y actualizamos en la lista falsa
            for user in MOCK_USERS:
                if user['id'] == user_id:
                    # Actualiza solo los campos que no sean None
                    clean_data = {k: v for k, v in data.items() if k in user and v is not None}
                    user.update(clean_data)
                    # Hack para simular actualización de 'active' si viene en data
                    if 'active' in data: user['active'] = data['active']
                    break
            return {"success": True}

        # 2. Lógica REAL (Conexión al Backend)
        try:
            url = f"{ApiService.BASE_URL}/users/{user_id}"
            # Nota: Requests maneja automáticamente la conversión a JSON
            res = requests.put(url, json=data, headers=ApiService.get_headers())
            
            if res.status_code == 200:
                return {"success": True, "data": res.json()}
            else:
                # Si falla, devolvemos el error que manda el backend
                return {"success": False, "error": res.json().get('detail', res.text)}
        except Exception as e:
            return {"success": False, "error": str(e)}
        
    @staticmethod
    def generate_pdf_report(user_id):
        """
        Solicita al backend la generación del informe PDF y retorna los bytes.
        """
        # Modo Mock para pruebas rápidas sin gastar tokens de Gemini
        if st.session_state.get('use_mock', True):
            time.sleep(2) # Simular la "pensadera" de la IA
            # Retornamos un PDF vacío dummy o texto simple convertido a bytes
            return {
                "success": True, 
                "data": b"%PDF-1.4... (contenido simulado del PDF)", 
                "filename": f"informe_mock_paciente_{user_id}.pdf"
            }

        try:
            # Nota: stream=True es buena práctica para archivos grandes, 
            # pero aquí el reporte es pequeño, así que podemos bajarlo de una.
            url = f"{ApiService.BASE_URL}/users/{user_id}/report"
            res = requests.get(url, headers=ApiService.get_headers())
            
            if res.status_code == 200:
                # Intentamos sacar el nombre del archivo del header si el backend lo manda
                content_disposition = res.headers.get('content-disposition', '')
                filename = "informe_medico.pdf"
                if "filename=" in content_disposition:
                    filename = content_disposition.split("filename=")[1].strip('"')
                
                return {
                    "success": True, 
                    "data": res.content, # Aquí están los bytes del PDF
                    "filename": filename
                }
            elif res.status_code == 404:
                return {"success": False, "error": "Usuario o contexto no encontrado."}
            else:
                return {"success": False, "error": f"Error del servidor: {res.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}