import os
import json
import requests
from dotenv import load_dotenv
from web3 import Web3
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
INFURA_URL = os.getenv("INFURA_URL")
ETHEREUM_WALLET_ADDRESS = os.getenv("ETHEREUM_WALLET_ADDRESS")
ETHEREUM_PRIVATE_KEY = os.getenv("ETHEREUM_PRIVATE_KEY")

# Conectar à blockchain Ethereum via Infura
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Endereço do contrato Semaphore na Sepolia Testnet
SEMAPHORE_CONTRACT_ADDRESS = "0xYourSemaphoreContractAddress"

# ABI do contrato Semaphore
SEMAPHORE_ABI = json.loads("""
[
    {
        "constant": false,
        "inputs": [
            {"name": "identityCommitment", "type": "uint256"}
        ],
        "name": "addMember",
        "outputs": [],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            {"name": "identityCommitment", "type": "uint256"}
        ],
        "name": "isMember",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    }
]
""")

# Conectar ao contrato
semaphore_contract = w3.eth.contract(address=SEMAPHORE_CONTRACT_ADDRESS, abi=SEMAPHORE_ABI)

# Criar modelo de IA
chat_model = ChatOpenAI(openai_api_key=OPENAI_API_KEY)

# Criar memória conversacional
conversation_memory = ConversationBufferMemory(memory_key="chat_history")

# Criar banco de memória vetorial FAISS
embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
memory = FAISS.from_texts([], embedding_model)

# 🔧 Ferramentas autônomas do agente

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

# 🔒 Função para adicionar um usuário ao Semaphore
def adicionar_membro(identity_commitment):
    tx = semaphore_contract.functions.addMember(identity_commitment).build_transaction({
        'from': ETHEREUM_WALLET_ADDRESS,
        'gas': 1000000,
        'gasPrice': w3.to_wei('10', 'gwei'),
        'nonce': w3.eth.get_transaction_count(ETHEREUM_WALLET_ADDRESS),
    })
    
    signed_tx = w3.eth.account.sign_transaction(tx, ETHEREUM_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return w3.to_hex(tx_hash)

# 🔒 Função para verificar se um usuário pertence ao grupo
def verificar_membro(identity_commitment):
    return semaphore_contract.functions.isMember(identity_commitment).call()

# Função para validar o usuário antes de interagir com o AI Agent
def validar_usuario(identity_commitment):
    return verificar_membro(identity_commitment)

# Função para interação com o agente
def ai_agent_zk(user_input, identity_commitment):
    if not validar_usuario(identity_commitment):
        return "⚠️ Acesso negado. Você não tem permissão para interagir com o agente."
    
    response = agent.run(user_input)
    return response

# Simulando um novo usuário gerando um identity_commitment
novo_usuario_commitment = 1234567890  # Esse valor deve ser gerado de forma segura

# Adicionar usuário ao grupo (necessário uma carteira Ethereum com fundos)
tx_hash = adicionar_membro(novo_usuario_commitment)
print(f"Usuário adicionado com sucesso! Hash da transação: {tx_hash}")

# Simulando uma interação com o AI Agent
print("🚀 AI Agent ZK iniciado! Digite 'sair' para encerrar.")
while True:
    user_input = input("Você: ")
    if user_input.lower() == "sair":
        print("👋 Encerrando o agente...")
        break
    response = ai_agent_zk(user_input, novo_usuario_commitment)
    print("AI Agent:", response)
