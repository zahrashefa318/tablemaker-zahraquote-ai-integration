import time
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from httpcore import request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.rate_limit import limiter, should_exempt



logger = logging.getLogger("Zahra") #Give me the logger object named Zahra from Python’s global logging registry.


def setup_middleware(app: FastAPI):
    """
    Setup global middleware: CORS, rate limiting, and request logging
    """

    # --------------- Rate limiting setup ---------------
    app.state.limiter = limiter

  

    # --------------- CORS ---------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        
    )

    #--------------- Rate limit exemption ------------------
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        if should_exempt(request.url.path):
            return await call_next(request)  # Exit middleware immediately(VIP paths ignores rate limiting)

        response = await call_next(request)  #Continue middleware AFTER route runs
        return response

    

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
