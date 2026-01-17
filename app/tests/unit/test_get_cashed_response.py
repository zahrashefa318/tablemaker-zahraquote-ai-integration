import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services import idempotency
from app.db.session import session
from app.db.tableModels import Idempotency_key_storage

# Override auth dependency so tests don’t fail due to Depends(get_current_user)
from app.core.security import get_current_user
app.dependency_overrides[get_current_user] = lambda: "test-user"

client = TestClient(app)


class MockResponse:
    def __init__(self, status_code=200, json_data=None, text="OK"):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text

    def json(self):
        return self._json


@pytest.fixture(autouse=True)
def clear_idempotency_table():
    # Clear the idempotency table before each test
    db = session()
    db.query(Idempotency_key_storage).delete()
    db.commit()
    db.close()
    yield


@patch("app.api.routers.quotes.httpx.AsyncClient")
def test_quotes_process_idempotent_return(mock_async_client):
    """
    Test that /quotes/process saves the response first call
    and returns cached result second call for same Idempotency-Key.
    """

    # Prepare AsyncClient mock
    mock_instance = AsyncMock()
    mock_async_client.return_value.__aenter__.return_value = mock_instance

    # Two post calls for the first route invocation:
    #  1) token request
    #  2) quotes process
    mock_instance.post = AsyncMock(side_effect=[
        MockResponse(200, {"token": "fake-token"}),
        MockResponse(200, {"response": "This is a mocked joke"}),
    ])

    url = "/quotes/process"
    idem_key = "idem-key-test"
    payload = {"prompt": "Joke"}

    # First request — should call both token + process
    res1 = client.post(
        url,
        headers={
            "Authorization": "Bearer dummy",
            "Idempotency-Key": idem_key,
        },
        json=payload,
    )

    assert res1.status_code == 200
    body1 = res1.json()
    assert body1 == {"response": "This is a mocked joke"}

    # Second request (same Idempotency-Key) — should return cached without another HTTP
    res2 = client.post(
        url,
        headers={
            "Authorization": "Bearer dummy",
            "Idempotency-Key": idem_key,
        },
        json=payload,
    )

    assert res2.status_code == 200
    body2 = res2.json()
    assert body2 == body1

    # The AsyncClient.post was called exactly twice (token + process only once)
    assert mock_instance.post.call_count == 2

    # Check that a record was saved in idempotency
    record = idempotency.get_cached_response(idem_key)
    assert record is not None
    assert record.response_body == {"response": "This is a mocked joke"}
