import pytest

from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["app"] == "s16-calculator-api"
    assert "add" in body["operations"]


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_add_endpoint(client):
    resp = client.get("/api/add?a=2&b=3")
    assert resp.status_code == 200
    assert resp.get_json()["result"] == 5


def test_divide_by_zero_endpoint(client):
    resp = client.get("/api/divide?a=1&b=0")
    assert resp.status_code == 400
    assert "zero" in resp.get_json()["error"]


def test_unknown_operation(client):
    resp = client.get("/api/modulo?a=1&b=2")
    assert resp.status_code == 404


def test_missing_params(client):
    assert client.get("/api/add?a=1").status_code == 400


def test_non_numeric_params(client):
    assert client.get("/api/add?a=x&b=2").status_code == 400


def test_secure_ping_not_configured(client, monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    assert client.get("/api/secure/ping").status_code == 503


def test_secure_ping_rejects_wrong_key(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "expected-key")
    resp = client.get("/api/secure/ping", headers={"X-API-Key": "wrong"})
    assert resp.status_code == 401


def test_secure_ping_accepts_right_key(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "expected-key")
    resp = client.get("/api/secure/ping", headers={"X-API-Key": "expected-key"})
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "authorized"
