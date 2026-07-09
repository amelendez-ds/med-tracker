from fastapi.testclient import TestClient


def _add(client: TestClient, name: str, total: int, dose: int) -> None:
    r = client.post(
        "/medications/",
        json={"name": name, "total_pills": total, "daily_dosage": dose},
    )
    assert r.status_code == 200


def test_create_and_list(client: TestClient) -> None:
    _add(client, "Paracetamol", 10, 2)
    r = client.get("/medications/")
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["name"] == "Paracetamol"


def test_take_reduces_stock(client: TestClient) -> None:
    _add(client, "Med", 10, 2)
    r = client.put("/medications/1/take")
    assert r.status_code == 200
    assert "8 pills remaining" in r.json()["message"]


def test_take_missing_returns_404(client: TestClient) -> None:
    assert client.put("/medications/999/take").status_code == 404


def test_take_insufficient_returns_400(client: TestClient) -> None:
    _add(client, "Low", 1, 2)
    assert client.put("/medications/1/take").status_code == 400


def test_refill_increases_stock(client: TestClient) -> None:
    _add(client, "Med", 0, 1)
    r = client.put("/medications/1/refill", params={"amount": 30})
    assert r.status_code == 200
    assert "Total is now 30." in r.json()["message"]


def test_delete_removes(client: TestClient) -> None:
    _add(client, "Paracetamol", 10, 1)
    assert client.delete("/medications/1").status_code == 200
    assert client.get("/medications/").json() == []


def test_delete_missing_returns_404(client: TestClient) -> None:
    assert client.delete("/medications/999").status_code == 404


def test_check_stock_flags_low(client: TestClient) -> None:
    _add(client, "LowMed_Test", 10, 2)
    r = client.get("/check-stock")
    assert r.status_code == 200
    assert "LowMed_Test" in r.json()["alerts_sent_for"]


def test_daily_automation_requires_auth(client: TestClient) -> None:
    assert client.post("/daily-automation/").status_code == 401


def test_daily_automation_authorized(client: TestClient) -> None:
    r = client.post(
        "daily-automation/", headers={"authorization": "Bearer test-secret"}
    )
    assert r.status_code == 200
