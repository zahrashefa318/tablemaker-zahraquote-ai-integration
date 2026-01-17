import time
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.rate_limit import limiter


logger = logging.getLogger("Zahra")


def setup_middleware(app: FastAPI):
    """
    Setup global middleware: CORS, rate limiting, and request logging
    """

    # --------------- Rate limiting setup ---------------
    app.state.limiter = limiter

    # Register the rate limit exceeded handler
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # --------------- CORS ---------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    # --------------- Request logging ---------------
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """
        Logs every incoming HTTP request with timing, idempotency key, and client info.
        """
        idem_key = request.headers.get("Idempotency-Key", "N/A")

        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        formatted_time = f"{process_time:.4f}s"

        logger.info(
            f"{request.method} {request.url.path} -"
            f"Idempotency-Key:{idem_key} "
            f"-Status code:{response.status_code} "
            f"-process time:{formatted_time} "
            f"-Client host:{request.client.host}"
        )

        return response
