"""Pruebas de CORS para el frontend (ADR-005)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_preflight_desde_origen_permitido():
    respuesta = client.options(
        "/api/v1/channels",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert respuesta.status_code == 200
    assert respuesta.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_preflight_desde_origen_no_permitido():
    respuesta = client.options(
        "/api/v1/channels",
        headers={
            "Origin": "http://sitio-ajeno.example.test",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in respuesta.headers
