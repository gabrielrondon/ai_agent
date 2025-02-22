import json
import web3
from web3 import Web3

# Configurar conexão com a blockchain (usando um nó público do Ethereum)
INFURA_URL = "https://sepolia.infura.io/v3/SUA_INFURA_API_KEY"
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Endereço do contrato do Semaphore (Sepolia Testnet)
SEMAPHORE_CONTRACT_ADDRESS = "0xYourSemaphoreContractAddress"

# ABI do contrato (definição das funções disponíveis)
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

# Função para adicionar um membro ao grupo
def adicionar_membro(identity_commitment, sender_address, sender_private_key):
    tx = semaphore_contract.functions.addMember(identity_commitment).build_transaction({
        'from': sender_address,
        'gas': 1000000,
        'gasPrice': w3.to_wei('10', 'gwei'),
        'nonce': w3.eth.get_transaction_count(sender_address),
    })

    # Assinar e enviar transação
    signed_tx = w3.eth.account.sign_transaction(tx, sender_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return w3.to_hex(tx_hash)

# Função para verificar se um usuário faz parte do grupo
def verificar_membro(identity_commitment):
    return semaphore_contract.functions.isMember(identity_commitment).call()

# Simulando um novo usuário
novo_usuario_commitment = 1234567890  # Exemplo de Identity Commitment

# Adicionar usuário ao grupo (necessário uma carteira Ethereum com fundos)
# Endereço e chave privada fictícios para fins de demonstração
MEU_ENDERECO = "0xYourEthereumAddress"
MINHA_CHAVE_PRIVADA = "0xYourPrivateKey"

# Adicionar usuário ao grupo
tx_hash = adicionar_membro(novo_usuario_commitment, MEU_ENDERECO, MINHA_CHAVE_PRIVADA)
print(f"Usuário adicionado com sucesso! Hash da transação: {tx_hash}")

# Verificar se o usuário foi adicionado
if verificar_membro(novo_usuario_commitment):
    print("✅ O usuário está no grupo!")
else:
    print("❌ O usuário NÃO está no grupo!")
