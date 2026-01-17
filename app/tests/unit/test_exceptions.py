from app.api.exceptions import unified_exception_handler
from fastapi.testclient import TestClient
from app.services.idempotency import save_response
from app.main import app
client=TestClient(app,raise_server_exceptions=False)

def test_not_found():
    response = client.get("/myHealth")
    assert response.status_code == 404
    assert response.json() == {"detail": "Route not found"}

def test_internal_issue():
    response = client.get("/error")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}