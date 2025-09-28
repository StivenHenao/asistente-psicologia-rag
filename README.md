
# Sistema RAG de Apoyo Psicológico

Un sistema de **Retrieval-Augmented Generation (RAG)** especializado en brindar apoyo psicológico y emocional para personas que sufren de ansiedad y depresión, con enfoque en el contexto cultural y social de Colombia.

----------

## Descripción

Este proyecto utiliza inteligencia artificial para proporcionar respuestas empáticas y profesionales sobre temas de salud mental, combinando:

-   Base de conocimiento vectorizada con documentos especializados.
    
-   Búsqueda semántica inteligente.
    
-   Generación de respuestas contextualizadas con Google Gemini.
    
-   Enfoque cultural adaptado a Colombia.
    

----------

## Arquitectura

<p align="center">
  <img src="https://i.imgur.com/Z2mM9G8.png" alt="Arquitectura" width="600"/>
</p>

----------

## Características

-   **Asistente especializado** en ansiedad y depresión.
    
-   **Respuestas contextualizadas** basadas en documentos especializados.
    
-   **Tono empático y profesional** adaptado al contexto colombiano.
    
-   **Búsqueda semántica** con embeddings locales.
    
-   **Fallback inteligente** cuando no hay información suficiente.
    
-   **Interfaz de línea de comandos** simple y directa.
    

----------

## Tecnologías Utilizadas

-   **LangChain**: Framework para aplicaciones con LLM.
    
-   **ChromaDB**: Base de datos vectorial para almacenamiento de embeddings.
    
-   **HuggingFace Transformers**: Generación de embeddings locales.
    
-   **Google Gemini**: Modelo de lenguaje para generación de respuestas.
    
-   **Python 3.12+**: Lenguaje de programación principal.
    

----------

## Instalación

### Prerrequisitos

-   Python 3.12 o superior
    
-   `uv` (para crear entornos virtuales y manejar dependencias)
    
-   Cuenta de Google AI Studio para API de Gemini
    

### Pasos de instalación

1.  **Clonar el repositorio**
    

`git clone [URL_DEL_REPOSITORIO] cd langchaing-rag-psicologia` 

2.  **Crear y activar entorno virtual con `uv`**
    

`uv venv
uv activate` 

3.  **Instalar dependencias**
    

`uv pip install -r requirements.txt` 

4.  **Configurar variables de entorno**
    

`# Crear archivo .env en la raíz del proyecto  echo  "GEMINI_API_KEY=tu_api_key_aqui" > .env` 

### Obtener API Key de Gemini

1.  Ve a [Google AI Studio](https://makersuite.google.com/app/apikey).
    
2.  Inicia sesión con tu cuenta de Google.
    
3.  Crea una nueva API key.
    
4.  Copia la key en tu archivo `.env`.
    

----------


## Estructura del Proyecto

```
langchain-rag-tutorial/
├── query_data.py          # Script principal de consulta
├── create_database.py     # Script para crear la base de datos (si existe)
├── chroma/               # Base de datos vectorial ChromaDB
├── .env                  # Variables de entorno (API keys)
├── requirements.txt      # Dependencias del proyecto
└── README.md            # Documentación del proyecto
```

----------
## Uso ### Consulta básica

```
uv run query_data.py "¿Qué es la ansiedad?"
```

### Ejemplos de consultas **Definiciones:**

```
uv run query_data.py "¿Qué es la depresión?"
uv run query_data.py "Dime tres palabras que definan depresión"
```

**Consejos y apoyo:**

```

uv run query_data.py "¿Cómo puedo manejar la ansiedad?"
uv run query_data.py "Técnicas de relajación para la depresión"
```

**Contexto cultural:**

```
uv run query_data.py "¿Dónde buscar ayuda psicológica en Colombia?"
uv run query_data.py "¿Cómo hablar de salud mental en Colombia?"
```

### Formato de respuesta

El sistema proporciona:

-   Respuesta empática y profesional.
    
-   Basada en el contexto de documentos especializados.
    
-   Adaptada al contexto cultural colombiano.
    
-   Fuentes de información (opcional en salida).
    

----------

## Configuración

### Parámetros principales

-   **CHROMA_PATH**: Directorio de la base de datos vectorial (`"chroma"`).
    
-   **Modelo de embeddings**: `sentence-transformers/all-MiniLM-L6-v2`.
    
-   **Modelo Gemini**: `models/gemini-2.5-flash`.
    
-   **Umbral de relevancia**: 0.3.
    
-   **Resultados de búsqueda**: Top 5.
    

### Personalización del prompt

El sistema utiliza un prompt especializado que define:

-   Rol como asistente de apoyo psicológico.
    
-   Enfoque en ansiedad y depresión.
    
-   Contexto cultural colombiano.
    
-   Tono empático pero profesional.
    

----------

## Características Técnicas

-   **Búsqueda semántica**: Utiliza similarity search con scores de relevancia.
    
-   **Filtrado inteligente**: Solo usa resultados con score > 0.3.
    
-   **Fallback**: Si no hay resultados relevantes, usa el más similar disponible.
    
-   **Manejo de errores**: Respuesta informativa cuando Gemini no está disponible.
    
-   **Supresión de warnings**: Oculta advertencias de deprecación para UX limpia.
    

----------

## Dependencias Principales

`langchain-community
langchain
chromadb
sentence-transformers
google-generativeai
python-dotenv
argparse` 

----------

## Seguridad y Privacidad

-   **API Keys**: Almacenadas en variables de entorno.
    
-   **Datos locales**: Embeddings generados y almacenados localmente.
    
-   **Sin logs**: No se guardan consultas del usuario.
    
-   **Respuestas responsables**: Evita contenido dañino u ofensivo.
    

----------

## Limitaciones y Consideraciones

### Limitaciones técnicas

-   Requiere conexión a internet para Gemini API.
    
-   Base de conocimiento limitada a documentos cargados.
    
-   Respuestas basadas en información hasta la fecha de entrenamiento.
    

### Consideraciones de uso

-   **No reemplaza ayuda profesional**: Es una herramienta de apoyo complementaria.
    
-   **Para emergencias**: Recomienda contactar profesionales o líneas de crisis.
    
-   **Contexto cultural**: Optimizado para Colombia, puede requerir ajustes para otros países.
    

----------

## Licencia

Este proyecto está bajo la **Licencia MIT**. Ver el archivo `LICENSE` para más detalles.

----------

## Créditos

Desarrollado con fines educativos y de apoyo comunitario en salud mental.

**⚠️ Aviso importante**: Este sistema es una herramienta de apoyo y **no reemplaza la atención psicológica profesional**. En caso de crisis o emergencia, contacta inmediatamente a servicios de salud mental profesionales.