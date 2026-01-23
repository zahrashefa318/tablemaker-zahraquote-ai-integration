from fastapi import FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi.errors import RateLimitExceeded
from app.api.middleware import setup_middleware
from app.api.exceptions import unified_exception_handler
from app.api.routers import health, auth, table_request_router, quotes, openai, error
from app.db.session import engine, Base
from app.core.logging import setup_logger

logger = setup_logger() #Logging is a global process, not a per-module process.
logger.info("Logger initialized BEFORE app creation")


app = FastAPI()


@app.get("/version")
def version():
    return {"version": "AI_TIMEOUT_FIX_V3"}


# Middleware
setup_middleware(app)

# Exception handlers
app.add_exception_handler(Exception, unified_exception_handler)
app.add_exception_handler(StarletteHTTPException, unified_exception_handler)
app.add_exception_handler(RateLimitExceeded, unified_exception_handler)

# Routers
app.include_router(auth.router)
app.include_router(health.router)
app.include_router(table_request_router.router)
app.include_router(quotes.router)
app.include_router(openai.router)
app.include_router(error.router)

# Create tables AFTER app is ready
Base.metadata.create_all(bind=engine) #SQLAlchemy runs CREATE TABLE IF NOT EXISTS … behind the scenes — so if a table already exists, it skips creating it again.
