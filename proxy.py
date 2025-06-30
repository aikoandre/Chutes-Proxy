import os
from dotenv import load_dotenv
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carrega variáveis do arquivo .env
load_dotenv()

# --- CONFIGURAÇÃO ---
# É uma prática de segurança muito melhor ler a chave de uma variável de ambiente
# do que colocá-la diretamente no código.
CHUTES_API_KEY = os.getenv("CHUTES_API_TOKEN")
CHUTES_API_URL = "https://llm.chutes.ai/v1/chat/completions"

# Verificação inicial para garantir que a chave de API foi configurada
if not CHUTES_API_KEY:
    raise ValueError("A variável de ambiente CHUTES_API_TOKEN não foi definida.")

# Inicializa o aplicativo FastAPI
app = FastAPI()

# Cria um cliente HTTP assíncrono que será reutilizado para todas as requisições.
# Isso é mais eficiente do que criar um novo cliente a cada chamada.
client = httpx.AsyncClient()

# --- DEFINIÇÃO DA ROTA DO PROXY ---
# Esta é a rota principal. Ela vai "escutar" em /v1/chat/completions
# e aceitará requisições POST, exatamente como o SillyTavern espera da OpenAI.
@app.post("/v1/chat/completions")
async def proxy_to_chutes(request: Request):
    """
    Esta função atua como o proxy.
    1. Recebe a requisição do SillyTavern.
    2. Lê o corpo da requisição (o JSON com o prompt, modelo, etc.).
    3. Prepara uma nova requisição para a API do Chutes AI.
    4. Envia a requisição e transmite a resposta de volta para o SillyTavern.
    """
    
    # Lê o corpo (payload) da requisição original enviada pelo SillyTavern
    request_data = await request.json()
    logging.info(f"Request data from SillyTavern: {request_data}")
    
    # Pega os cabeçalhos da requisição original (útil para Content-Type, etc.)
    # e os modifica para a nossa nova requisição.
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHUTES_API_KEY}"
    }

    # Verifica se a requisição original pedia streaming
    is_streaming = request_data.get("stream", False)

    # Prepara a requisição para a API do Chutes AI
    req = client.build_request(
        method="POST",
        url=CHUTES_API_URL,
        json=request_data,
        headers=headers,
        timeout=300.0  # Aumenta o timeout para acomodar modelos lentos
    )

    # Se a requisição for de streaming, precisamos lidar com ela de forma especial
    if is_streaming:
        # Abre uma conexão de streaming com a API do Chutes
        response_stream = await client.send(req, stream=True)
        
        # Define uma função geradora que irá "puxar" os pedaços da resposta
        # à medida que eles chegam e os envia de volta ao cliente (SillyTavern).
        async def stream_generator():
            async for chunk in response_stream.aiter_bytes():
                logging.info(f"Streaming chunk from Chutes AI: {chunk.decode('utf-8', errors='ignore')}")
                yield chunk
        
        # Retorna uma StreamingResponse que envia os dados em tempo real.
        # O media_type é importante para o SillyTavern entender a resposta.
        return StreamingResponse(stream_generator(), media_type=response_stream.headers.get("content-type"))
    
    # Se não for streaming, faz uma requisição normal
    else:
        response = await client.send(req)
        # Lê o corpo da resposta como JSON
        response_data = response.json()
        logging.info(f"Raw response from Chutes AI: {response_data}")
        # Retorna os dados diretamente
        return response_data

# Uma rota de "saúde" opcional para verificar se o servidor está rodando
@app.get("/")
def health_check():
    return {"status": "Proxy para Chutes AI está online!"}
@app.get("/v1/models")
async def get_manual_models():
    """
    Returns a manually defined list of models.
    """
    models = [
        {"id": "deepseek-ai/DeepSeek-R1-0528"},
        {"id": "NousResearch/DeepHermes-3-Mistral-24B-Preview"},
        {"id": "RekaAI/reka-flash-3"},
        {"id": "TheDrummer/Cydonia-24B-v2.1"},
        {"id": "all-hands/openhands-lm-32b-v0.1-ep3"},
        {"id": "OpenGVLab/InternVL3-78B"},
        {"id": "thedrummer/skyfall-36b-v2"},
        {"id": "TheDrummer/Tunguska-39B-v1"},
        {"id": "TheDrummer/Donnager-70B-v1"}
    ]
    return {"data": models}

@app.get("/models")
async def get_manual_models_alias():
    """
    Alias for /v1/models to support OpenAI-compatible clients.
    """
    return await get_manual_models()


@app.post("/chat/completions")
async def proxy_to_chutes_no_v1(request: Request):
    """
    Alias for /v1/chat/completions to support OpenAI-compatible clients.
    """
    return await proxy_to_chutes(request)