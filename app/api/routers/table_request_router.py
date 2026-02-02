from fastapi import APIRouter, Depends, Header, BackgroundTasks
from app.schema.request_format import TableRequest
from app.services import table_service, idempotency
from app.core.security import get_current_user
from fastapi import HTTPException

from fastapi import Request


router = APIRouter(prefix="/table_request_router", tags=["TableRequest"])

@router.post("/create")

def create_table(
    request: Request,
    req: TableRequest,
    bg: BackgroundTasks,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    user: str = Depends(get_current_user),
):
    cached = idempotency.get_cached_response(idempotency_key)
    incoming_hash = idempotency.hash_body(req.model_dump())

    if cached:
        if cached.request_hash != incoming_hash:
            raise HTTPException(
                status_code=409,
                detail="Idempotency-Key reused with a different request body.",
            )
        return cached.response_body

    cols = table_service.order_columns(req.rows, req.columns)
    result = (
        table_service.to_html(req.rows, cols)
        if req.format == "html"
        else table_service.to_markdown(req.rows, cols)
    )

    final_response = {"table": result}

    idempotency.save_response(
        idempotency_key,
        200,
        final_response,      # ✅ full response
        req.model_dump(),   # It serializes the model into a dictionary
    )

    bg.add_task(idempotency.cleanup_expired)

    return {"table": result}
