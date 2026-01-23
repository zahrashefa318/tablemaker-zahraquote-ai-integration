from fastapi import APIRouter, Request
import logging

from fastapi import Request

router = APIRouter(tags=["Health"])

@router.get("/health")
def health(request: Request):
    logging.getLogger("Zahra").info("Health checked")
    return {"ok": 200}
