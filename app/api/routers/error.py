from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from app.core.rate_limit import limiter, RATE_LIMITS
from fastapi import Request

from app.core.rate_limit import RATE_LIMITS
router=APIRouter(tags=["Error"])
@router.get("/error")
@limiter.limit(RATE_LIMITS["default"])
def error(request: Request):
     raise RuntimeError("Internal issues!")