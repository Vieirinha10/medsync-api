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


def test_v2_case_is_identified_in_case_catalog():
    token = _register_and_login("catalogo-v2@example.com")
    response = client.get(
        "/casos-clinicos/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    cases = response.json()
    pilot = next(case for case in cases if case["id"] == 8)
    legacy = next(case for case in cases if case["id"] == 1)
    assert pilot["avaliacao_2_disponivel"] is True
    assert legacy["avaliacao_2_disponivel"] is False


def test_clinical_simulation_v2_scores_and_persists_structured_feedback():
    token = _register_and_login("simulacao-v2@example.com")
    response = client.post(
        "/simulacoes/8/finalizar",
        json={
            "exames_solicitados": ["angiotc", "doppler_mmss", "gaso"],
            "hipotese_diagnostica": "Tromboembolismo pulmonar agudo",
            "conduta_proposta": (
                "Estabilização pelo ABC, oxigenoterapia, anticoagulação com "
                "heparina, estratificação de risco e internação para monitorização."
            ),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    result = response.json()
    assert result["pontuacao_total"] == 100
    assert result["pontuacao"] == {
        "exames": 40,
        "hipotese": 30,
        "conduta": 30,
    }
    assert result["fonte_feedback"] == "agente_regras"
    assert result["exames"]["essenciais_ausentes"] == []
    assert result["exames"]["desnecessarios"] == []
    assert result["feedback"]["feedback_seguranca"]

    saved = client.get(
        f"/simulacoes/resultados/{result['progresso_id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert saved.status_code == 200
    assert saved.json() == result


def test_simulation_v2_penalizes_low_value_exam_and_missing_actions():
    token = _register_and_login("simulacao-parcial@example.com")
    response = client.post(
        "/simulacoes/8/finalizar",
        json={
            "exames_solicitados": ["angiotc", "dimerod"],
            "hipotese_diagnostica": "Trombose venosa",
            "conduta_proposta": "Iniciar anticoagulação com heparina.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    result = response.json()
    assert result["pontuacao"]["exames"] < 40
    assert result["pontuacao"]["hipotese"] == 15
    assert result["pontuacao"]["conduta"] == 12
    assert result["exames"]["desnecessarios"] == ["D-dímero"]
    assert len(result["exames"]["essenciais_ausentes"]) == 2


def test_legacy_case_cannot_use_v2_until_its_rubric_is_reviewed():
    token = _register_and_login("caso-legado@example.com")
    response = client.post(
        "/simulacoes/1/finalizar",
        json={
            "exames_solicitados": ["ecg"],
            "hipotese_diagnostica": "Pericardite aguda",
            "conduta_proposta": "Monitorização e tratamento conforme avaliação.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 409
