from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
import logging
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger("Zahra")

async def unified_exception_handler(request: Request, exc: Exception):

    # ------------------ Rate limit ------------------
    if isinstance(exc, RateLimitExceeded):
        logger.warning(f"Rate limit exceeded: {request.url.path}")
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too many requests. Please slow down and try again shortly."
            },
        )

    # ------------------ 404 ------------------
    if isinstance(exc, StarletteHTTPException) and exc.status_code == 404:
        logger.warning(f"404 Not Found: {request.url.path}")
        return JSONResponse(status_code=404, content={"detail": "Route not found"})

    # ------------------ Everything else ------------------
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500, content={"detail": "Internal Server Error"}
    )
