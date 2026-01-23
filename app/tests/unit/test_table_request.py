from app.main import app
from fastapi.testclient import TestClient
 
client=TestClient(app)
def test_html_table_request():
    idempotency="table_test_idem"
    token=client.get("/generate-token").json()["token"]
    body=[{"name":"zahra","last_name":"Shefa","age":24},{"name":"hussain","last_name":"Alimi","age":28}]
    response=client.post("/table_request_router/create",headers={"Idempotency-Key":idempotency,"Authorization":f"Bearer {token}"},json={"rows": body},)
    assert response.status_code == 200
    html = response.json()["table"]

    assert "<table" in html
    assert "<thead>" in html
    assert "<tbody>" in html
    assert "tm-wrap" in html

def test_markdown_table_request():
    idempotency_key = "markdown_test_idem_v1"
    token = client.get("/generate-token").json()["token"]

    body = {
        "rows": [
        {"name": "zahra", "last_name": "Shefa", "age": 24},
        {"name": "hussain", "last_name": "Alimi", "age": 28},
    ], "format": "markdown"}

    expected_markdown = (
        "| name | last_name | age |\n"
        "| --- | --- | --- |\n"
        "| zahra | Shefa | 24 |\n"
        "| hussain | Alimi | 28 |\n"
    )

    response = client.post(
        "/table_request_router/create",
        headers={
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": idempotency_key,
        },
        json=body,   # 🔑 THIS FIXES THE 422
    )

    assert response.status_code == 200
    assert response.json()["table"].strip() == expected_markdown.strip()
