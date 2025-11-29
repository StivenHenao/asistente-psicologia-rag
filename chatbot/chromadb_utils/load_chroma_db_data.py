import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def load_vectorstore():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.abspath(os.path.join(current_dir, "..", "..", "chroma_db"))

    if not os.path.exists(db_path):
        print("ERROR: La carpeta de base de datos no existe en la ruta calculada.")
        return None

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = Chroma(
        persist_directory=db_path,
        embedding_function=embeddings
    )


    cantidad = vectorstore._collection.count()
    print(f"   -> Documentos encontrados: {cantidad}")

    if cantidad == 0:
        print("ALERTA: La base de datos está vacía (o estás apuntando al lugar incorrecto).")
    
    retriever = vectorstore.as_retriever()
    return retriever