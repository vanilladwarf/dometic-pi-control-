"""Integration test: the HTTP API works end-to-end."""
import pytest
from fastapi.testclient import TestClient
from dometic.state import get_store
import dometic.api as api


@pytest.fixture
def client():
    return TestClient(api.app)


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_state(client):
    get_store().update(mode="cool", fan="high", room_f=75.0, outdoor_f=85.0)
    r = client.get("/api/state")
    assert r.status_code == 200
    data = r.json()
    assert data["mode"] == "cool"
    assert data["fan"] == "high"
    assert data["room_f"] == 75.0


def test_set_mode(client):
    r = client.post("/api/mode", json={"mode": "heat", "fan": "low"})
    assert r.status_code == 200
    state = get_store().get()
    assert state.mode == "heat"
    assert state.fan == "low"


def test_set_mode_invalid(client):
    r = client.post("/api/mode", json={"mode": "turbo", "fan": "low"})
    assert r.status_code == 400


def test_set_setpoint(client):
    r = client.post("/api/setpoint", json={"cool": 72, "heat": 66})
    assert r.status_code == 200
    state = get_store().get()
    assert state.setpoint_cool_f == 72.0
    assert state.setpoint_heat_f == 66.0


def test_set_setpoint_heat_too_high(client):
    r = client.post("/api/setpoint", json={"cool": 50, "heat": 80})
    assert r.status_code == 400


def test_set_setpoint_out_of_range(client):
    r = client.post("/api/setpoint", json={"cool": 200, "heat": 60})
    assert r.status_code == 422
