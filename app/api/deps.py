from fastapi import Depends, Header
from app.core.security import get_current_user

def get_idempotency_key(
    idempotency_key: str = Header(..., alias="Idempotency-Key")
):
    return idempotency_key

def authenticated_user(user: str = Depends(get_current_user)):
    return user
