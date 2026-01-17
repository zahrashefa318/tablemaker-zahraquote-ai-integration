from fastapi import APIRouter, Request
import logging

from app.core.rate_limit import limiter, RATE_LIMITS
from fastapi import Request

router = APIRouter(tags=["Health"])

@router.get("/health")
@limiter.limit(RATE_LIMITS["default"])
def health(request: Request):
    logging.getLogger("Zahra").info("Health checked")
    return {"ok": 200}
