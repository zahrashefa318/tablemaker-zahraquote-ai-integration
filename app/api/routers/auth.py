from fastapi import APIRouter
from app.core.security import generate_token
from app.core.rate_limit import limiter,RATE_LIMITS
from fastapi import Request

router = APIRouter(tags=["Auth"])

@router.get("/generate-token")

def generate_token_route(request: Request):
    token = generate_token()
    return {"token": token}
