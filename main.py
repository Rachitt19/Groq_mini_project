from fastapi import FastAPI
from pydantic import BaseModel
import os
import httpx

app = FastAPI()

class AskRequest(BaseModel):
    prompt: str

# Load API keys from environment variable
keys_env = os.getenv("GROQ_API_KEYS", "")
API_KEYS = [key.strip() for key in keys_env.split(",") if key.strip()]

# Global state for key rotation
current_key_index = 0
MODEL = "llama-3.1-8b-instant"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

@app.post("/ask")
async def ask_endpoint(request: AskRequest):
    global current_key_index
    
    if not API_KEYS:
        return {"status": "error", "answer": "No API keys configured"}
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Return ONLY clean Python code. No markdown, no ``` blocks."},
            {"role": "user", "content": request.prompt}
        ]
    }
    
    # timeout: 15 seconds to ensure we quickly rotate keys if an endpoint hangs
    async with httpx.AsyncClient(timeout=15.0) as client:
        for _ in range(len(API_KEYS)):
            api_key = API_KEYS[current_key_index]
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            try:
                response = await client.post(
                    GROQ_API_URL,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("choices", [])[0].get("message", {}).get("content", "")
                    return {"status": "success", "answer": answer}
                
                # If rate limited or standard HTTP error occurs, rotate to next key
                current_key_index = (current_key_index + 1) % len(API_KEYS)
                
            except (httpx.TimeoutException, httpx.RequestError):
                # Rotate key on network failure or timeout
                current_key_index = (current_key_index + 1) % len(API_KEYS)
                
    return {"status": "error", "answer": "All API keys failed or timed out"}
