from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_token():
    response = client.get("/generate-token")

    # Status code check
    assert response.status_code == 200

    # Response body check
    data = response.json()
    assert "token" in data
    assert isinstance(data["token"], str)
    assert len(data["token"]) > 0
    print(response.json())
