"""
Prueba mínima del scaffold — health check.

No requiere base de datos ni mocks de servicios externos. Las pruebas reales
de HU-RSS-001 a 009 (con mocks/stubs para llamadas HTTP a feeds RSS, nunca
llamadas reales) quedan pendientes de implementación por el equipo, conforme
a la sección 14 de las instrucciones del proyecto (DoD — cobertura >= 80%).
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# Scaffold / DoD — Health check del servicio (arranque de la app sin BD ni mocks)
def test_health_check_responde_ok():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
