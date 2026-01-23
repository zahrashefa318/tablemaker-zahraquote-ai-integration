from slowapi import Limiter
from slowapi.util import get_remote_address
    
EXEMPT_PATHS = ["/", "/health", "/docs", "/openapi", "/quotes/process","/table_request_router/create","/generate-token"]
    
def should_exempt(path: str) -> bool:
    return any(path.startswith(p) for p in EXEMPT_PATHS)

limiter = Limiter(
    key_func=get_remote_address   
)

# Predefined limit strings
RATE_LIMITS = {
    "default": "120/minute",
    "strict": "30/minute",
    "openai": "60/minute",
}

