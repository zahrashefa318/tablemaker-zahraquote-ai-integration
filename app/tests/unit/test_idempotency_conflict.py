import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app

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


@patch("app.api.routers.quotes.httpx.AsyncClient")
def test_idempotency_key_reuse_with_different_body_returns_409(mock_client):
    """
    GIVEN a request with an idempotency key and body A
    WHEN the same idempotency key is reused with body B
    THEN the server must reject with 409 Conflict
    """

    # Mock AsyncClient context manager
    mock_instance = AsyncMock()
    mock_client.return_value.__aenter__.return_value = mock_instance

    # Mock external Quotes API calls:
    # First POST for token
    # Then POST for process
    mock_instance.post = AsyncMock(side_effect=[
        MockResponse(200, {"token": "fake-access-token"}),
        MockResponse(200, {"response": "This is the first response"}),
    ])

    url = "/quotes/process"
    idem_key = "idem_conflict_test"

    # -------------------------------
    # First request (valid)
    # -------------------------------
    response_1 = client.post(
        url,
        headers={
            "Authorization": f"Bearer faketoken",
            "Idempotency-Key": idem_key,
        },
        json={"prompt": "Tell me a joke"},
    )

    # must be 200
    assert response_1.status_code == 200
    assert response_1.json() == {"response": "This is the first response"}

    # -------------------------------
    # Second request (same key, DIFFERENT body)
    # -------------------------------
    response_2 = client.post(
        url,
        headers={
            "Authorization": f"Bearer faketoken",
            "Idempotency-Key": idem_key,
        },
        json={"prompt": "Write me a poem"},
    )

    # -------------------------------
    # Assertions
    # -------------------------------
    assert response_2.status_code == 409
    assert response_2.json() == {
        "detail": "Idempotency key reuse with different request body"
    }
