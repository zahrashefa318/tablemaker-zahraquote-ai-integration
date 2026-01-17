import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from requests.exceptions import RequestException

from app.main import app  # adjust if your app import path is different

client = TestClient(app)


@pytest.mark.parametrize("message", ["Hello world", "Test traceback"])
def test_openai_chat_success(monkeypatch, message):
    """
    This tests that a successful Ollama API call returns a JSON reply.
    """

    # Mock response for requests.post
    fake_resp = Mock()
    fake_resp.json.return_value = {"response": f"Echo: {message}"}
    fake_resp.raise_for_status.return_value = None

    def fake_post(*args, **kwargs):
        return fake_resp

    # Monkeypatch requests.post
    monkeypatch.setattr("requests.post", fake_post)

    response = client.post(
        "/openai/chat",
        headers={"Idempotency-Key": "test-key-1"},
        json={"message": message}
    )

    assert response.status_code == 200
    body = response.json()
    assert "reply" in body
    assert isinstance(body["reply"], str)
    assert f"Echo: {message}" in body["reply"]


@pytest.mark.parametrize("exc", [
    RequestException("connection aborted"),
    RequestException("timeout expired")
])
def test_openai_chat_ollama_connection_error(monkeypatch, exc):
    """
    When requests.post raises a RequestException, we should return a 500
    with a detail message that contains the exception text.
    """

    def fake_post(*args, **kwargs):
        raise exc

    monkeypatch.setattr("requests.post", fake_post)

    response = client.post(
        "/openai/chat",
        headers={"Idempotency-Key": "test-key-2"},
        json={"message": "Hello"}
    )

    assert response.status_code == 500
    assert response.json()["detail"] == str(exc)


def test_openai_chat_generic_error(monkeypatch):
    """
    If something else goes wrong in the try block, we should still return
    a 500 and include the exception message.
    """

    # error while parsing JSON or accessing .json()
    class BadResponse:
        def raise_for_status(self):
            return None

        def json(self):
            raise ValueError("bad json")

    def fake_post(*args, **kwargs):
        return BadResponse()

    monkeypatch.setattr("requests.post", fake_post)

    response = client.post(
        "/openai/chat",
        headers={"Idempotency-Key": "test-key-3"},
        json={"message": "trigger error"}
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "bad json"