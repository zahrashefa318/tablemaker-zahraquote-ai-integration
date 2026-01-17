from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import requests
from huggingface_hub import InferenceClient
from app.core.rate_limit import limiter, RATE_LIMITS
from fastapi import Request

class ChatRequest(BaseModel):
    message: str

router = APIRouter(prefix="/openai", tags=["OpenAI"])

AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")

# ---- Ollama config (local) ----
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# ---- HuggingFace config (prod) ----
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = "google/gemma-2-2b-it"


@router.post("/chat")
@limiter.limit(RATE_LIMITS["openai"])
async def openai_chat(
    request: Request,
    body: ChatRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key")
):
    prompt = body.message

    try:
        # -----------------------------
        # LOCAL: Ollama
        # -----------------------------
        if AI_PROVIDER == "ollama":
            response = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=180,
            )
            response.raise_for_status()
            data = response.json()
            return {"reply": data.get("response", "")}

        # -----------------------------
        # PROD: HuggingFace
        # -----------------------------
        if AI_PROVIDER == "huggingface":
            if not HF_API_TOKEN:
                return JSONResponse(
                    status_code=500,
                    content={"detail": "HF_API_TOKEN not set"},
                )

            client = InferenceClient(api_key=HF_API_TOKEN)
            text = client.text_generation(
                prompt,
                model=HF_MODEL,
                max_new_tokens=200,
            )
            return {"reply": text}

        return JSONResponse(
            status_code=500,
            content={"detail": f"Unknown AI_PROVIDER: {AI_PROVIDER}"},
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
        )
