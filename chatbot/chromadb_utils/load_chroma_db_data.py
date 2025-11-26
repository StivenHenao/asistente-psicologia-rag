from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = Chroma(
        persist_directory="../../chroma_db",
        embedding_function=embeddings
    )

    retriever = vectorstore.as_retriever()
    print("Vectorstore cargado con exito")
    return retriever

    