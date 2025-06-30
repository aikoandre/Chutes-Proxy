# Chutes AI OpenAI Proxy

This project provides a simple proxy server to make the Chutes AI API directly compatible with applications designed to work with OpenAI's API structure, such as SillyTavern, eliminating the need for intermediaries like OpenRouter.

## Features

-   **OpenAI API Compatibility:** Translates requests from OpenAI-compatible clients to the Chutes AI API format.
-   **Streaming Support:** Handles streaming responses for real-time interaction with language models.
-   **Model Listing:** Provides a static list of available models at the `/v1/models` endpoint.

## Setup

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone https://github.com/aikoandre/Chutes-Proxy.git
    cd chutes-router
    ```

2.  **Install Dependencies:**
    ```bash
    pip install fastapi uvicorn httpx python-dotenv
    ```

3.  **Configure API Key:**
    Create a file named `.env` in the root directory of the project.
    Inside the `.env` file, add your Chutes AI API token:

    ```
    CHUTES_API_TOKEN=your_api_key_here
    ```

    **Important:** Replace `your_api_key_here` with your actual API token obtained from Chutes AI.

4.  **Run the Server:**
    ```bash
    uvicorn proxy:app --host 0.0.0.0 --port 6000 --reload
    ```
    The proxy will be accessible at `http://localhost:6000`.

## Model Information

Please note that all models have a global limit of 200 requests per minute. Only a few models currently work reliably with this proxy method. The list will be updated as more models are tested and confirmed.

**Currently Working Models:**
*   `Deepseek R1 Distill Qwen 32B AWQ`
*   `Devstral Small 2505`
*   `Llama 4 Maverick 17B 128E Instruct FP8`
*   `Llama 4 Scout 17B 16E Instruct`
*   `Mistral Small 3.2 24B Instruct 2506`
*   `Deepseek R1 0528`
*   `Deepseek R1 Distill Llama 70B`
*   `Llama Poro 2 70B Instruct`
*   `MAI DS R1 FP8`
*   `MiniMax M1 80K`
*   `Kimi Dev 72B`
*   `DeepHermes 3 Mistral 24B Preview`
*   `InternVL3 78B`
*   `Qwen2.5 Coder 32B Instruct`
*   `Qwen2.5 VL 72B Instruct`
*   `Qwen3 235B A22B`
*   `Reka Flash 3`
*   `Llama XLAM 2 70B FC R`
*   `Cydonia 24B V2.1`
*   `Skyfall 36B V2`
*   `TEMPLAR I`
*   `Deepseek R1T Chimera`
*   `Mistral Nemo Instruct 2407`

## Endpoints

-   `POST /v1/chat/completions` and `POST /chat/completions`: Proxy for chat completions to Chutes AI.
-   `GET /v1/models` and `GET /models`: Returns a list of available models.
-   `GET /`: Health check endpoint.