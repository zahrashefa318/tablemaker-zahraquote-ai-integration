from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("Zahra")

async def unified_exception_handler(request: Request, exc: Exception): #FastAPI automatically passes those arguments(request and exc) when it calls your handler.

    if isinstance(exc, StarletteHTTPException) and exc.status_code == 404:
        logger.warning(f"404 Not Found: {request.url.path}")
        return JSONResponse(status_code=404, content={"detail": "Route not found"})

    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500, content={"detail": "Internal Server Error"}
    )
