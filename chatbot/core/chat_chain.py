
from chatbot.core.extract_user_info import extract_user_info
from chatbot.core.langchain_service import rag_chain
# dentro de esta usamos las funcionalidades de langchain y la cadena que nos permite extraer
# información, dar respuesta y almacenar información (contexto)
def handle_chat_flow(user_input, user_context):
    
    # 2. extraer información del usuario de su pregunta/respuesta
    structured_user_info = extract_user_info(user_input, user_context)
    print(f"[INFO] User info (paso 2): {structured_user_info}")
    # 3. dar respuesta al usuario
    result = rag_chain.invoke({
        "input": f"{user_input}",
        "info": f"{user_context}",
    })
   
    
    print(f"\n[INFO] Documentos recuperados de la base de datos vectorial: {result["context"]}\n")
    
    # 5. retornar la respuesta generada anteiormente
    return result["answer"], structured_user_info