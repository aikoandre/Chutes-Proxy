import os
import httpx
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- ENV FILE ---
load_dotenv()

CHUTES_API_URL = "https://llm.chutes.ai/v1/chat/completions"

# Initializes the FastAPI application
app = FastAPI()

# Creates an asynchronous HTTP client that will be reused for all requests.
# This is more efficient than creating a new client for each call.
client = httpx.AsyncClient()

# --- PROXY ROUTE DEFINITION ---
# This is the main route. It will "listen" on /v1/chat/completions
# and accept POST requests, just as SillyTavern expects from OpenAI.
@app.post("/v1/chat/completions")
async def proxy_to_chutes(request: Request):
    """
    This function acts as the proxy.
    1. Receives the request from SillyTavern.
    2. Reads the request body (the JSON with the prompt, model, etc.).
    3. Prepares a new request for the Chutes AI API.
    4. Sends the request and transmits the response back to SillyTavern.
    """
    
    # Reads the body (payload) of the original request sent by SillyTavern
    request_data = await request.json()
    logging.info(f"Request data from SillyTavern: {request_data}")
    
    # Gets the headers of the original request (useful for Content-Type, etc.)
    # and modifies them for our new request.
    
    # Gets the API key from the .env file
    api_key_to_use = os.getenv("CHUTES_API_TOKEN")

    if not api_key_to_use:
        logging.error("CHUTES_API_TOKEN not found in .env file.")
        raise ValueError("CHUTES_API_TOKEN not found in .env file.")

    logging.info("Using API key from .env file.")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key_to_use}"
    }

    # Checks if the original request asked for streaming
    is_streaming = request_data.get("stream", False)

    # Prepares the request for the Chutes AI API
    req = client.build_request(
        method="POST",
        url=CHUTES_API_URL,
        json=request_data,
        headers=headers,
        timeout=300.0
    )

    # If the request is for streaming, we need to handle it in a special way
    if is_streaming:
        # Opens a streaming connection with the Chutes API
        response_stream = await client.send(req, stream=True)
        
        # Defines a generator function that will "pull" the pieces of the response
        # as they arrive and send them back to the client (SillyTavern).
        async def stream_generator():
            async for chunk in response_stream.aiter_bytes():
                logging.info(f"Streaming chunk from Chutes AI: {chunk.decode('utf-8', errors='ignore')}")
                yield chunk
        
        # Returns a StreamingResponse that sends the data in real time.
        return StreamingResponse(stream_generator(), media_type=response_stream.headers.get("content-type"))
    
    # If it's not streaming, makes a normal request
    else:
        response = await client.send(req)
        # Reads the response body as JSON
        response_data = response.json()
        logging.info(f"Raw response from Chutes AI: {response_data}")
        return response_data

# An optional "health" route to check if the server is running
@app.get("/")
def health_check():
    return {"status": "Proxy for Chutes AI is online!"}
@app.get("/v1/models")
async def get_manual_models():
    """
    Returns a manually defined list of models.
    """
    models = [
        {"id": "casperhansen/deepseek-r1-distill-qwen-32b-awq"},
        {"id": "chutesai/Devstral-Small-2505"},
        {"id": "chutesai/Llama-4-Maverick-17B-128E-Instruct-FP8"},
        {"id": "chutesai/Llama-4-Scout-17B-16E-Instruct"},
        {"id": "chutesai/Mistral-Small-3.2-24B-Instruct-2506"},
        {"id": "deepseek-ai/DeepSeek-R1-0528"},
        {"id": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"},
        {"id": "LGAI-EXAONE/EXAONE-Deep-32B"},
        {"id": "LumiOpen/Llama-Poro-2-70B-Instruct"},
        {"id": "microsoft/MAI-DS-R1-FP8"},
        {"id": "MiniMaxAI/MiniMax-M1-80k"},
        {"id": "moonshotai/Kimi-Dev-72B"},
        {"id": "NousResearch/DeepHermes-3-Mistral-24B-Preview"},
        {"id": "OpenGVLab/InternVL3-78B"},
        {"id": "Qwen/Qwen2.5-Coder-32B-Instruct"},
        {"id": "Qwen/Qwen2.5-VL-72B-Instruct"},
        {"id": "Qwen/Qwen3-235B-A22B"},
        {"id": "RekaAI/reka-flash-3"},
        {"id": "Salesforce/Llama-xLAM-2-70b-fc-r"},
        {"id": "TheDrummer/Cydonia-24B-v2.1"},
        {"id": "thedrummer/skyfall-36b-v2"},
        {"id": "tplr/TEMPLAR-I"},
        {"id": "tngtech/DeepSeek-R1T-Chimera"},
        {"id": "unsloth/Mistral-Nemo-Instruct-2407"}
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