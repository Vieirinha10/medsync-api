import importlib
import os
import sys
import uuid
from pathlib import Path

from fastapi.testclient import TestClient


TEST_DB = Path("/tmp") / f"medsync-{uuid.uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["JWT_SECRET_KEY"] = "test-secret-with-at-least-32-characters"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
main = importlib.import_module("main")
client = TestClient(main.app)


def _register_and_login(email: str = "aluno@example.com") -> str:
    response = client.post(
        "/usuarios/registrar",
        json={"nome": "Aluno MedSync", "email": email, "password": "senha-segura"},
    )
    assert response.status_code == 201

    response = client.post(
        "/usuarios/login", json={"email": email, "password": "senha-segura"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_duplicate_registration_is_rejected():
    _register_and_login()
    response = client.post(
        "/usuarios/registrar",
        json={
            "nome": "Outro nome",
            "email": "ALUNO@example.com",
            "password": "outra-senha",
        },
    )
    assert response.status_code == 409


def test_protected_routes_require_a_valid_token():
    assert client.get("/casos-clinicos/").status_code == 401
    assert (
        client.get(
            "/casos-clinicos/", headers={"Authorization": "Bearer token-invalido"}
        ).status_code
        == 401
    )


def test_progress_is_persistent_and_isolated_by_user():
    first_token = _register_and_login("primeiro@example.com")
    second_token = _register_and_login("segundo@example.com")

    payload = {
        "id_caso": 1,
        "respostas_usuario": {"hipotese_diagnostica": "Pericardite"},
        "pontuacao": 85,
    }
    response = client.post(
        "/progresso/registrar",
        json=payload,
        headers={"Authorization": f"Bearer {first_token}"},
    )
    assert response.status_code == 201
    assert response.json()["id_usuario"] != 0

    first_progress = client.get(
        "/progresso/meu", headers={"Authorization": f"Bearer {first_token}"}
    )
    second_progress = client.get(
        "/progresso/meu", headers={"Authorization": f"Bearer {second_token}"}
    )
    assert len(first_progress.json()) == 1
    assert second_progress.json() == []
