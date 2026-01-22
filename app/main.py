from fastapi import FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.middleware import setup_middleware
from app.api.exceptions import unified_exception_handler
from app.api.routers import health, auth, table_request_router, quotes, openai, error
from app.db.session import engine, Base

app = FastAPI()


@app.get("/version")
def version():
    return {"version": "AI_TIMEOUT_FIX_V3"}


# Middleware
setup_middleware(app)

# Exception handlers
app.add_exception_handler(Exception, unified_exception_handler)
app.add_exception_handler(StarletteHTTPException, unified_exception_handler)

# Routers
app.include_router(auth.router)
app.include_router(health.router)
app.include_router(table_request_router.router)
app.include_router(quotes.router)
app.include_router(openai.router)
app.include_router(error.router)

# Create tables AFTER app is ready
Base.metadata.create_all(bind=engine)
