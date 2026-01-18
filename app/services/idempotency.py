from datetime import datetime, timedelta, timezone
from app.db.session import session
from app.db.tableModels import Idempotency_key_storage
import logging
import hashlib
import json
import psycopg2

logger = logging.getLogger("Zahra")
#---Helper function-------
def hash_body(body: dict) -> str:
    normalized = json.dumps(body, sort_keys=True)
    return hashlib.sha256(normalized.encode()).hexdigest()


def get_cached_response(key: str):
    db = session()
    try:
        return db.query(Idempotency_key_storage).filter_by(key=key).first()
    finally:
        db.close()


def save_response(key: str, status: int, body, request_body):
    db = session()
    try:
        record = Idempotency_key_storage(
            key=key,
            response_status=status,
            response_body=body,
            request_hash=hash_body(request_body),
        )
        db.add(record)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving idempotency key: {e}")
        raise
    finally:
        db.close()


def cleanup_expired(minutes=60):
    db = session()
    try:
        db.query(Idempotency_key_storage).filter(
            Idempotency_key_storage.created_at <= datetime.now(timezone.utc) - timedelta(minutes=minutes)
        ).delete(synchronize_session=False)
        db.commit()
        logger.info("Expired idempotency keys cleaned up")
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting expired idempotency keys: {e}")
    finally:
        db.close()
