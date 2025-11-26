from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders import DirectoryLoader

#1. Cargar los documentos
documents = PyPDFDirectoryLoader("../../data").load() # en este caso en la carpeta data no hay pdfs, hay un documento md

loader = DirectoryLoader(
    '../../data',
    glob='**/*.md',
    loader_cls=UnstructuredMarkdownLoader,         # Clase específica para procesar el Markdown
    show_progress=True
)

documents += loader.load()

print("Cantidad de documentos:", len(documents))

#2. Dividir los documentos
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2") # modelo de embeddings

#3. Crear la base de datos
vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory="../../chroma_db")
print("Base de datos creada con exito")

# con la bd creada, podemos usar el load_chrome_db_data.py para cargarla 