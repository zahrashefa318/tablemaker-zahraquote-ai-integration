from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import os
import requests
from app.core.security import get_current_user




# -----------------------------
# Request model
# -----------------------------
class ChatRequest(BaseModel):
    message: str


router = APIRouter(prefix="/openai", tags=["OpenAI"])


# -----------------------------
# Ollama (LOCAL ONLY)
# -----------------------------
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


# -----------------------------
# HuggingFace (PRODUCTION)
# -----------------------------
HF_MODEL_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"


@router.post("/chat")

async def openai_chat(
    request: Request,
    body: ChatRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    user: str = Depends(get_current_user),
):
    ai_provider = os.getenv("AI_PROVIDER", "huggingface").lower()
    prompt = body.message.strip()

    if not prompt:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # =====================================================
    # LOCAL: Ollama
    # =====================================================
    if ai_provider == "ollama":
        # Ollama MUST never run on Render
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
    # PRODUCTION: HuggingFace (Render-safe)
    # =====================================================
    if ai_provider == "huggingface":
        hf_token = os.getenv("HF_API_TOKEN")
        if not hf_token:
            return JSONResponse(
                status_code=500,
                content={"detail": "HF_API_TOKEN not set"},
            )

        try:
            response = requests.post(
                HF_MODEL_URL,
                headers={"Authorization": f"Bearer {hf_token}"},
                json={"inputs": prompt},
                timeout=12,   # VERY IMPORTANT
            )

            response.raise_for_status()
            data = response.json()
            reply = data[0]["generated_text"]

            return {"reply": reply}

        except requests.exceptions.Timeout:
            return {
                "reply": "⚠️ AI is temporarily unavailable. The free HuggingFace model is taking too long to respond, and the hosting server blocks long requests. Please try again in a few seconds."
            }

        except Exception:
            return {
                "reply": "⚠️ AI service is currently busy (free-tier model delay). Please retry shortly."
            }


    # =====================================================
    # Invalid provider
    # =====================================================
    raise HTTPException(
        status_code=500,
        detail=f"Unknown AI_PROVIDER: {ai_provider}",
    )
