from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from case_catalog import CLINICAL_CASES
from clinical_rubric_catalog import (
    CLINICAL_CASE_EXAM_UPDATES,
    DRAFT_CLINICAL_RUBRICS,
    RELEASED_CLINICAL_RUBRIC_IDS,
)
from clinical_titles import PUBLIC_CASE_TITLES, formatted_public_title
from evaluation import (
    PILOT_RUBRIC_VERSION,
    PILOT_RUBRICS,
    ClinicalRubricDefinition,
)
from models import ClinicalCase, ClinicalExam, ClinicalRubric
from services.vital_signs import extract_vital_signs


def seed_clinical_content(db: Session) -> bool:
    """Carrega o catálogo e acrescenta novos casos sem duplicar os existentes."""
    if db.scalar(select(func.count()).select_from(ClinicalCase)):
        _sync_missing_catalog_cases(db)
        _sync_case_exam_updates(db)
        _sync_pilot_rubrics(db)
        _sync_draft_rubrics(db)
        return False

    now = datetime.now(UTC)
    for source in CLINICAL_CASES:
        db.add(_case_from_catalog(source, now=now))

    db.commit()
    _sync_case_exam_updates(db)
    _sync_draft_rubrics(db)
    return True


def _case_from_catalog(source: dict, *, now: datetime) -> ClinicalCase:
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
            revisado_por="Rubrica editorial MedSync",
            revisado_em=now,
        )
    return case


def _sync_missing_catalog_cases(db: Session) -> None:
    """Inclui expansões do catálogo em bancos já inicializados."""
    existing_ids = set(db.scalars(select(ClinicalCase.id)).all())
    missing = [source for source in CLINICAL_CASES if source["id"] not in existing_ids]
    if not missing:
        return

    now = datetime.now(UTC)
    db.add_all([_case_from_catalog(source, now=now) for source in missing])
    db.commit()


def _sync_case_exam_updates(db: Session) -> None:
    """Corrige e completa exames necessários às rubricas clínicas revisadas."""
    changed = False
    for case_id, updates in CLINICAL_CASE_EXAM_UPDATES.items():
        case = db.scalar(
            select(ClinicalCase)
            .where(ClinicalCase.id == case_id)
            .options(selectinload(ClinicalCase.exames))
        )
        if case is None:
            continue

        exams_by_code = {exam.codigo: exam for exam in case.exames}
        for order, source in enumerate(updates, start=len(case.exames)):
            exam = exams_by_code.get(source["id"])
            if exam is None:
                case.exames.append(
                    ClinicalExam(
                        codigo=source["id"],
                        nome=source["nome"],
                        resultado=source["resultado"],
                        referencia_adequada=source.get("correto", True),
                        ordem=order,
                    )
                )
                changed = True
                continue
            for attribute, value in (
                ("nome", source["nome"]),
                ("resultado", source["resultado"]),
                ("referencia_adequada", source.get("correto", True)),
            ):
                if getattr(exam, attribute) != value:
                    setattr(exam, attribute, value)
                    changed = True
    if changed:
        db.commit()


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
                revisado_por="Rubrica editorial MedSync",
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
            case.rubrica.revisado_por = "Rubrica editorial MedSync"
            case.rubrica.revisado_em = now
            changed = True

    if changed:
        db.commit()


def _sync_draft_rubrics(db: Session) -> None:
    """Sincroniza rubricas de expansão respeitando a decisão editorial."""
    now = datetime.now(UTC)
    changed = False
    for case_id, source_definition in DRAFT_CLINICAL_RUBRICS.items():
        case = db.get(ClinicalCase, case_id)
        if case is None:
            continue

        definition = _validated_rubric(source_definition)
        released = case_id in RELEASED_CLINICAL_RUBRIC_IDS
        desired_status = "revisada" if released else "rascunho"
        reviewer = "Administração MedSync — liberação editorial" if released else None
        if case.rubrica is None:
            case.rubrica = ClinicalRubric(
                versao=PILOT_RUBRIC_VERSION,
                status=desired_status,
                definicao=definition,
                revisado_por=reviewer,
                revisado_em=now if released else None,
            )
            changed = True
            continue

        # Nunca rebaixa uma rubrica já homologada; libera apenas IDs aprovados.
        if case.rubrica.status != "revisada" and (
            case.rubrica.definicao != definition
            or case.rubrica.status != desired_status
        ):
            case.rubrica.versao = PILOT_RUBRIC_VERSION
            case.rubrica.status = desired_status
            case.rubrica.definicao = definition
            case.rubrica.revisado_por = reviewer
            case.rubrica.revisado_em = now if released else None
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
