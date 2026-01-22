from fastapi import FastAPI
from app.api.middleware import setup_middleware
from app.api.exceptions import unified_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.routers import health, auth, table_request_router, quotes, openai,error


from app.db.session import engine, Base
Base.metadata.create_all(bind=engine)



app = FastAPI()
@app.get("/version")
def version():
    return {"version": "AI_TIMEOUT_FIX_V3"}

setup_middleware(app)
app.add_exception_handler(Exception, unified_exception_handler)#“Whenever any exception (that isn’t already handled by something more specific) occurs during a request, call the function unified_exception_handler to process that exception.”
app.add_exception_handler(StarletteHTTPException, unified_exception_handler)
app.include_router(auth.router)                                                               #This becomes a global fallback exception handler.
app.include_router(health.router)                             
app.include_router(table_request_router.router)
app.include_router(quotes.router)
app.include_router(openai.router)
app.include_router(error.router)
