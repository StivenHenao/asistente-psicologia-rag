import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader, DirectoryLoader, UnstructuredMarkdownLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

current_dir = os.path.dirname(os.path.abspath(__file__))

project_root = os.path.abspath(os.path.join(current_dir, "../../"))
data_path = os.path.join(project_root, "data")
db_path = os.path.join(project_root, "chroma_db")

print(f"Ruta de datos: {data_path}")
print(f"Ruta de base de datos: {db_path}")

documents = []

# Verificar si la carpeta data existe
if not os.path.exists(data_path):
    print(f"Error: La carpeta de datos no existe en: {data_path}")
    exit()

# Cargar archivos Markdown
loader_md = DirectoryLoader(
    data_path,
    glob='**/*.md',
    loader_cls=UnstructuredMarkdownLoader,
    show_progress=True
)
docs_md = loader_md.load()
documents.extend(docs_md)
print(f"   -> Encontrados {len(docs_md)} archivos Markdown.")

# Cargar PDFs (Opcional, si agregas en el futuro)
loader_pdf = PyPDFDirectoryLoader(data_path)
docs_pdf = loader_pdf.load()
documents.extend(docs_pdf)
print(f"   -> Encontrados {len(docs_pdf)} archivos PDF.")

if len(documents) == 0:
    print("Error: No se encontraron documentos. Revisa la carpeta 'data'.")
    exit()

print(f"Total documentos cargados: {len(documents)}")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Opcional: Borrar la DB anterior para asegurar una creación limpia
if os.path.exists(db_path):
    shutil.rmtree(db_path)
    print("Base de datos anterior eliminada para una regeneración limpia.")

print("Generando embeddings y guardando en ChromaDB...")
vectorstore = Chroma.from_documents(
    documents=splits, 
    embedding=embeddings, 
    persist_directory=db_path
)

print("Base de datos creada con éxito en la ruta absoluta.")