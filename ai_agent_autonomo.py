import os
import requests
from dotenv import load_dotenv
from langchain.agents import initialize_agent, Tool
from langchain.tools import tool
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import SystemMessage, HumanMessage

# Carregar variáveis do ambiente
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Criar modelo de IA
chat_model = ChatOpenAI(openai_api_key=OPENAI_API_KEY)

# Criar memória conversacional
conversation_memory = ConversationBufferMemory(memory_key="chat_history")

# Criar banco de memória vetorial FAISS
embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
memory = FAISS.from_texts([], embedding_model)

# 🔧 Criando ferramentas autônomas para o agente

@tool
def consultar_precos_cripto(cripto: str):
    """Consulta o preço atual de uma criptomoeda usando a API CoinGecko"""
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={cripto}&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return f"O preço atual do {cripto} é ${data[cripto]['usd']} USD."
    else:
        return "Erro ao buscar os dados."

@tool
def buscar_noticias():
    """Busca notícias recentes sobre blockchain"""
    url = "https://newsapi.org/v2/everything?q=blockchain&apiKey=SUA_API_NEWS"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json()["articles"][:3]
        noticias = [f"{a['title']} - {a['url']}" for a in articles]
        return "Últimas notícias sobre Blockchain:\n" + "\n".join(noticias)
    else:
        return "Erro ao buscar notícias."

# Criar o agente com ferramentas autônomas
tools = [consultar_precos_cripto, buscar_noticias]
agent = initialize_agent(
    tools=tools,
    llm=chat_model,
    agent="zero-shot-react-description",
    memory=conversation_memory,
    verbose=True
)

# Função para interação com o agente
def ai_agent_autonomo(user_input):
    response = agent.run(user_input)
    return response

# Loop interativo
print("🚀 AI Agent Autônomo iniciado! Digite 'sair' para encerrar.")
while True:
    user_input = input("Você: ")
    if user_input.lower() == "sair":
        print("👋 Encerrando o agente...")
        break
    response = ai_agent_autonomo(user_input)
    print("AI Agent:", response)
