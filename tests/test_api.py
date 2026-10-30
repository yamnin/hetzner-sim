import uuid

from fastapi.testclient import TestClient

from app.main import app


def test_server_lifecycle():
    with TestClient(app) as client:
        assert client.get("/health").json()["database"] == "ok"

        name = f"web-{uuid.uuid4().hex[:8]}"
        r = client.post("/v1/servers", json={"name": name, "server_type": "cx22"})
        assert r.status_code == 201
        server = r.json()
        assert server["status"] == "running"

        assert client.post("/v1/servers", json={"name": name}).status_code == 409

        r = client.post(f"/v1/servers/{server['id']}/actions", json={"action": "poweroff"})
        assert r.json()["status"] == "off"

        assert client.delete(f"/v1/servers/{server['id']}").status_code == 204
        assert client.get(f"/v1/servers/{server['id']}").status_code == 404


def test_rejects_unknown_server_type():
    with TestClient(app) as client:
        r = client.post("/v1/servers", json={"name": "bad", "server_type": "xx99"})
        assert r.status_code == 422
