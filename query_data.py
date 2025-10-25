import argparse
import os
import warnings

import google.generativeai as genai
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load environment variables
load_dotenv()

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Eres un asistente de apoyo psicologico y emocional enfocado para personas que sufren de ansiedad y depresion.
Responde de manera profesional y formal, a veces puedes ser casual y empatico como si fueras un
amigo cercano evitando modismos ofensivos y callejeros.
Es para gente de Colombia, si requieres dar consejos debes tener en cuenta el contexto cultural y social de Colombia.
Puedes usar el contexto para ayudar a responder la pregunta.
Tienes esta pregunta: {question}

Usa la siguiente información del contexto para responder la pregunta de la mejor manera posible.

{context}

Si no sabes la respuesta, di "No lo sé". Sé conciso y directo al punto.
Si es una pregunta nada ofensiva o dañina, responde de manera creativa y útil.
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text

    # Embeddings locales
    embedding_function = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Búsqueda
    results = db.similarity_search_with_relevance_scores(query_text, k=5)
    filtered_results = [doc for doc, score in results if score > 0.3]

    if not filtered_results and results:
        filtered_results = [results[0][0]]

    if not filtered_results:
        print("No se encontraron resultados relevantes.")
        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc in filtered_results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Configurar Gemini
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))

    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content(prompt)

        # sources = [doc.metadata.get("source", None) for doc in filtered_results]
        print(f"Respuesta: {response.text}")
        # print(f"Fuentes: {sources}")

    except Exception as e:
        print(f"Error con Gemini: {e}")
        print("Respuesta basada en el contexto no disponible.")


if __name__ == "__main__":
    main()
