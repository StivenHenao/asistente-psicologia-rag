import os

from dotenv import load_dotenv
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_google_genai import ChatGoogleGenerativeAI

from chatbot.chromadb_utils import load_chroma_db_data
from chatbot.core.system_prompt_template import prompt

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

# modelo a usar
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# cargo los datos de la base de datos
retriever = load_chroma_db_data.load_vectorstore()

question_answer_chain = create_stuff_documents_chain(llm, prompt)

# cadena rag
rag_chain = create_retrieval_chain(retriever, question_answer_chain)


