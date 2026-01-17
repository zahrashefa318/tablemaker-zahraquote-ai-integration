from app.services.idempotency import save_response
from app.db.tableModels import Idempotency_key_storage
from app.db.session import session
from sqlalchemy import text
import pytest

@pytest.mark.integration
def test_idempotency_saver_db_integration():
    db = session()
    print(db.execute(text("SELECT DATABASE()")).fetchone())

    idempotency_key = "DB_Test_123"
    response_status = 200
    response_body = {"detail": "Zahra is great!"}

    record = None
    try:
        save_response(idempotency_key, response_status, response_body,{"prompt":"test"})

        record = db.query(Idempotency_key_storage).filter_by(key=idempotency_key).first()

        assert record is not None
        assert record.key == idempotency_key
        assert record.response_status == response_status
        assert record.response_body == response_body

    finally:
        if record:
            db.delete(record)
            db.commit()
