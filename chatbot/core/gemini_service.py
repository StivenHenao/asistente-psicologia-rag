import os

import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
model = genai.GenerativeModel("models/gemini-2.0-flash")


def safe_get_text(response):
    if hasattr(response, "text") and response.text:
        return response.text
    elif hasattr(response, "candidates") and response.candidates:
        parts = response.candidates[0].content.parts
        if parts and hasattr(parts[0], "text"):
            return parts[0].text
    return ""


def generate_question(factor_value):
    """
    Genera una pregunta personal coherente según el tipo de dato.
    Ejemplo:
      'rojo' -> '¿Cuál es tu color favorito?'
      'pizza' -> '¿Cuál es tu comida favorita?'
      'Bogotá' -> '¿En qué ciudad vives?'
      'perro' -> '¿Tienes mascota? ¿Cuál?'
    """
    prompt = (
        f"Tengo un valor de autenticación: '{factor_value}'. "
        "Tu única tarea es identificar qué tipo de dato parece ser "
        "(color, comida, ciudad, animal, nombre propio, fecha, deporte, etc.) "
        "y formular una sola pregunta directa, personal y predecible para confirmarlo. "
        "Debe ser una pregunta en segunda persona, clara, de este estilo:\n"
        "- Si es un color: '¿Cuál es tu color favorito?'\n"
        "- Si es una comida: '¿Cuál es tu comida favorita?'\n"
        "- Si es una ciudad: '¿En qué ciudad vives?'\n"
        "- Si es un animal: '¿Tienes alguna mascota? ¿Cuál?'\n"
        "- Si es una persona: '¿Cómo se llama tu mejor amigo o amiga?'\n"
        "No inventes preguntas creativas o hipotéticas, ni hables de situaciones. "
        "Responde solo con una pregunta natural y nada más."
    )

    try:
        response = model.generate_content(prompt)
        text = safe_get_text(response).strip().split("\n")[0]
        if not text.endswith("?"):
            text += "?"
        print(f"🧠 Pregunta generada: {text}")
        return text
    except Exception as e:
        print(f"❌ Error con Gemini (pregunta): {e}")
        return f"Responde algo relacionado con {factor_value}."


def validate_answer(factor_value, answer):
    prompt = (
        f"El valor esperado es '{factor_value}' y el usuario respondió '{answer}'. "
        "Responde solo con 'sí' si significan lo mismo o son equivalentes, "
        "o 'no' si no coinciden. No agregues texto adicional."
    )

    try:
        response = model.generate_content(prompt)
        result = safe_get_text(response).lower().strip()
        print(f"🔍 Resultado validación: {result}")
        return "sí" in result
    except Exception as e:
        print(f"❌ Error con Gemini (validación): {e}")
        return False
