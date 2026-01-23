from wsgiref import headers
from fastapi import APIRouter, Depends, Header,Request
from fastapi.responses import JSONResponse
from app.services import idempotency
from app.core.security import get_current_user
import httpx
import logging

from fastapi import Request

router = APIRouter(prefix="/quotes", tags=["ZahraQuotes"])
logger = logging.getLogger("Zahra")

QUOTE_TOKEN_URL = "https://zahra-quotes-api.onrender.com/give_token"
QUOTE_PROCESS_URL = "https://zahra-quotes-api.onrender.com/process"

@router.post("/process")

async def process_quote(
    request: Request,
    payload: dict,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    current_user: str = Depends(get_current_user),
):
    prompt = payload.get("prompt")

    cached = idempotency.get_cached_response(idempotency_key)
    if cached:
        if cached.request_hash != idempotency.hash_body(payload):
            return JSONResponse(
                status_code=409,
                content={"detail": "Idempotency key reuse with different request body"},
            )
        return cached.response_body

    async with httpx.AsyncClient(timeout=10) as client:
        token_resp = await client.post(QUOTE_TOKEN_URL, headers={
        "Content-Type": "application/json", })
   
        if token_resp.status_code != 200:
            return JSONResponse(status_code=502, content={"detail": "Failed to get token"})

        access_token = token_resp.json().get("token")
        if not access_token:
            return JSONResponse(status_code=502, content={"detail": "Invalid token"})

        response = await client.post(
            QUOTE_PROCESS_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Idempotency-Key": idempotency_key,
            },
            json={"prompt": prompt},
        )

        if response.status_code == 200:
            res_json = response.json()
            idempotency.save_response(
                            key=idempotency_key,
                            status=200,
                            body=res_json,
                            request_body=payload,
                        )

            return res_json

        return JSONResponse(status_code=response.status_code, content={"detail": response.text})
