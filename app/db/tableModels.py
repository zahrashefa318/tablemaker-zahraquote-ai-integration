from sqlalchemy import String, Integer, DateTime,Column,Text
from app.db.session import Base
import datetime
from sqlalchemy import JSON
from datetime import datetime, timezone

class Idempotency_key_storage(Base):
    __tablename__="Idempotency_key_storage"
    key=Column(String(255), primary_key=True)
    created_at=Column(DateTime,default=datetime.now(timezone.utc))
    response_status=Column(Integer, nullable=False)
    response_body=Column(JSON, nullable=False)
    request_hash=Column(String(64), nullable=False)

