from unittest.mock import patch, MagicMock
import pytest
import psycopg2

from app.services.idempotency import save_response
from app.db.tableModels import Idempotency_key_storage

@patch("app.services.idempotency.session")
def test_idempotency_saver_saves_correct_data(mock_session):
    mock_db = MagicMock()
    mock_session.return_value = mock_db

    idempotency_key = "test_key_123"
    response_status = 200
    response_body = {"message": "Zahra Shefa is great!"}

    save_response(idempotency_key, response_status, response_body,{"prompt": "test"})

    # Ensure add() was called once
    assert mock_db.add.call_count == 1

    saved_obj = mock_db.add.call_args[0][0]

    assert isinstance(saved_obj, Idempotency_key_storage)
    assert saved_obj.key == idempotency_key
    assert saved_obj.response_status == response_status
    assert saved_obj.response_body == response_body

    mock_db.commit.assert_called_once()
