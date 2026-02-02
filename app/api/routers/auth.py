from fastapi import APIRouter
from app.core.security import generate_token
from app.core.rate_limit import limiter,RATE_LIMITS
from fastapi import Request

router = APIRouter(tags=["Auth"]) #APIRouter is a FastAPI class that lets you define a set of endpoint functions separately from your main app. You can then include this router into the main FastAPI app.

@router.get("/generate-token")

def generate_token_route(request: Request):
    token = generate_token()
    return {"token": token}
