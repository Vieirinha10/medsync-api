from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from case_catalog import CLINICAL_CASES
from clinical_titles import PUBLIC_CASE_TITLES, formatted_public_title
from evaluation import (
    PILOT_RUBRIC_VERSION,
    PILOT_RUBRICS,
    ClinicalRubricDefinition,
)
from models import ClinicalCase, ClinicalExam, ClinicalRubric
from services.vital_signs import extract_vital_signs


def seed_clinical_content(db: Session) -> bool:
    """Carrega o catálogo legado somente quando o banco ainda está vazio."""
    if db.scalar(select(func.count()).select_from(ClinicalCase)):
        _sync_pilot_rubrics(db)
        return False

    now = datetime.now(UTC)
    for source in CLINICAL_CASES:
        case = ClinicalCase(
            id=source["id"],
            titulo=source["titulo"],
            titulo_publico=PUBLIC_CASE_TITLES[source["id"]],
            especialidade=source["especialidade"],
            nivel_dificuldade=source["nivel_dificuldade"],
            historia_clinica=source["historia_clinica"],
            exame_fisico=source["exame_fisico"],
            status="publicado",
            versao_conteudo=1,
        )
        case.exames = [
            ClinicalExam(
                codigo=exam["id"],
                nome=exam["nome"],
                resultado=exam["resultado"],
                referencia_adequada=exam.get("correto", True),
                ordem=index,
            )
            for index, exam in enumerate(source.get("exames_disponiveis", []))
        ]
        if source["id"] in PILOT_RUBRICS:
            case.rubrica = ClinicalRubric(
                versao=PILOT_RUBRIC_VERSION,
                status="revisada",
                definicao=_validated_rubric(PILOT_RUBRICS[source["id"]]),
                revisado_por="Equipe clínica MedSync",
                revisado_em=now,
            )
        db.add(case)

    db.commit()
    return True


def _validated_rubric(definition: dict) -> dict:
    return ClinicalRubricDefinition.model_validate(definition).model_dump(mode="json")


def _sync_pilot_rubrics(db: Session) -> None:
    """Atualiza apenas as rubricas piloto mantidas e revisadas no código."""
    now = datetime.now(UTC)
    changed = False
    for case_id, source_definition in PILOT_RUBRICS.items():
        case = db.get(ClinicalCase, case_id)
        if case is None:
            continue

        definition = _validated_rubric(source_definition)
        if case.rubrica is None:
            case.rubrica = ClinicalRubric(
                versao=PILOT_RUBRIC_VERSION,
                status="revisada",
                definicao=definition,
                revisado_por="Equipe clínica MedSync",
                revisado_em=now,
            )
            changed = True
            continue

        if (
            case.rubrica.versao < PILOT_RUBRIC_VERSION
            or case.rubrica.definicao != definition
        ):
            case.rubrica.versao = PILOT_RUBRIC_VERSION
            case.rubrica.status = "revisada"
            case.rubrica.definicao = definition
            case.rubrica.revisado_por = "Equipe clínica MedSync"
            case.rubrica.revisado_em = now
            changed = True

    if changed:
        db.commit()


def list_published_cases(db: Session) -> list[ClinicalCase]:
    return list(
        db.scalars(
            select(ClinicalCase)
            .where(ClinicalCase.status == "publicado")
            .options(
                selectinload(ClinicalCase.exames),
                selectinload(ClinicalCase.rubrica),
            )
            .order_by(ClinicalCase.id)
        ).all()
    )


def get_published_case(db: Session, case_id: int) -> ClinicalCase | None:
    return db.scalar(
        select(ClinicalCase)
        .where(ClinicalCase.id == case_id, ClinicalCase.status == "publicado")
        .options(
            selectinload(ClinicalCase.exames),
            selectinload(ClinicalCase.rubrica),
        )
    )


def serialize_case(case: ClinicalCase, *, include_details: bool = True) -> dict:
    data = {
        "id": case.id,
        "titulo": formatted_public_title(case.id, case.titulo_publico),
        "especialidade": case.especialidade,
        "nivel_dificuldade": case.nivel_dificuldade,
        "avaliacao_2_disponivel": bool(
            case.rubrica and case.rubrica.status == "revisada"
        ),
        "premium": case.is_premium,
    }
    if include_details:
        data.update(
            {
                "historia_clinica": case.historia_clinica,
                "exame_fisico": case.exame_fisico,
                "sinais_vitais": extract_vital_signs(
                    case.historia_clinica,
                    case.exame_fisico,
                ),
                "exames_disponiveis": [
                    {
                        "id": exam.codigo,
                        "nome": exam.nome,
                        "resultado": exam.resultado,
                        "correto": exam.referencia_adequada,
                    }
                    for exam in case.exames
                ],
            }
        )
    return data
