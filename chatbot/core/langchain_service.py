from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import os
from chatbot.chromadb_utils import load_chroma_db_data
from dotenv import load_dotenv

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")


retriever = load_chroma_db_data.load_vectorstore()

