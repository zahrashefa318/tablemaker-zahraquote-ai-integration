import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


def get_auth_headers():
    token = client.get("/generate-token").json()["token"]
    return {
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": "test-idem-key",
    }


# -------------------------------
# Ollama success
# -------------------------------
@patch("app.api.routers.openai.requests.post")
def test_openai_chat_ollama_success(mock_post):
    os.environ["AI_PROVIDER"] = "ollama"

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"response": "Hello from Ollama"}
    mock_resp.raise_for_status.return_value = None

    mock_post.return_value = mock_resp

    r = client.post(
        "/openai/chat",
        headers=get_auth_headers(),
        json={"message": "Hello"},
    )

    assert r.status_code == 200
    assert r.json()["reply"] == "Hello from Ollama"


# -------------------------------
# HuggingFace success
# -------------------------------
@patch("app.api.routers.openai.AI_PROVIDER", "huggingface")
@patch("app.api.routers.openai.HF_API_TOKEN", "test-token")
@patch("app.api.routers.openai.InferenceClient")
def test_openai_chat_huggingface_success(mock_client):
    mock_instance = MagicMock()
    mock_instance.text_generation.return_value = "Hello from HF"
    mock_client.return_value = mock_instance

    r = client.post(
        "/openai/chat",
        headers=get_auth_headers(),
        json={"message": "Hello"},
    )

    assert r.status_code == 200
    assert r.json()["reply"] == "Hello from HF"


# -------------------------------
# Error handling
# -------------------------------
@patch("app.api.routers.openai.AI_PROVIDER", "ollama")
@patch("app.api.routers.openai.requests.post")
def test_openai_chat_ollama_timeout(mock_post):
    mock_post.side_effect = Exception("timeout")

    r = client.post(
        "/openai/chat",
        headers=get_auth_headers(),
        json={"message": "Hello"},
    )

    assert r.status_code == 500
    assert "ollama inference error" in r.json()["detail"].lower()
