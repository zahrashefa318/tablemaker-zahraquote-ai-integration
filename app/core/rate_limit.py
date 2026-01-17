from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Predefined limit strings
RATE_LIMITS = {
    "default": "5/minute",
    "strict": "2/minute",
    "openai": "10/minute",
}
