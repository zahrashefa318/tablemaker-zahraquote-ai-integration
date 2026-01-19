from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel
import os
import requests
from huggingface_hub import InferenceClient
from fastapi.responses import JSONResponse

from app.core.rate_limit import limiter, RATE_LIMITS

# -----------------------------
# Request model
# -----------------------------
class ChatRequest(BaseModel):
    message: str


router = APIRouter(prefix="/openai", tags=["OpenAI"])

# -----------------------------
# Provider selection
# -----------------------------
AI_PROVIDER = os.getenv("AI_PROVIDER", "huggingface").lower()

# -----------------------------
# Ollama (LOCAL ONLY)
# -----------------------------
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# -----------------------------
# Hugging Face (PRODUCTION)
# -----------------------------
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = "HuggingFaceH4/zephyr-7b-beta"


@router.post("/chat")
@limiter.limit(RATE_LIMITS["openai"])
async def openai_chat(
    request: Request,
    body: ChatRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
):
    prompt = body.message.strip()

    if not prompt:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        # =====================================================
        # LOCAL DEV: Ollama
        # =====================================================
        if AI_PROVIDER == "ollama":
            if os.getenv("RENDER"):
                return JSONResponse(
                    status_code=503,
                    content={"detail": "Ollama is not available in production"},
                )
            try:
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

            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content={"detail": f"Ollama inference error: {str(e)}"},
                )

        # =====================================================
        # PRODUCTION: Hugging Face
        # =====================================================
        if AI_PROVIDER == "huggingface":
            if not HF_API_TOKEN:
                raise HTTPException(
                    status_code=500,
                    detail="HF_API_TOKEN not configured",
                )

            try:
                client = InferenceClient(
                    api_key=HF_API_TOKEN,
                    timeout=25,  # ⬅️ REQUIRED for Render
                )

                text = client.text_generation(
                    prompt,
                    model=HF_MODEL,
                    max_new_tokens=150,
                )

                return {"reply": text}

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"HuggingFace inference error: {str(e)}",
                )

        # =====================================================
        # Invalid provider
        # =====================================================
        raise HTTPException(
            status_code=500,
            detail=f"Unknown AI_PROVIDER: {AI_PROVIDER}",
        )

    except HTTPException:
        # Let FastAPI handle proper JSON + status code
        raise

    except Exception as e:
        # Absolute last-resort safety net (prevents 502)
        raise HTTPException(
            status_code=500,
            detail=f"Unhandled AI error: {str(e)}",
        )
