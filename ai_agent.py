import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage

# Carregar variáveis do ambiente
load_dotenv()

# Configurar o modelo de IA
chat_model = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

# Instruções para o Agente
system_prompt = "Você é um assistente especialista em blockchain e Web3."

# Função para interagir com o agente
def ai_agent_response(user_input):
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_input)
    ]
    response = chat_model(messages)
    return response.content

# Loop de interação com o usuário
print("🚀 AI Agent iniciado! Digite 'sair' para encerrar.")
while True:
    user_input = input("Você: ")
    if user_input.lower() == "sair":
        print("👋 Encerrando o agente...")
        break
    response = ai_agent_response(user_input)
    print("AI Agent:", response)
