from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from case_catalog import CLINICAL_CASES
from evaluation import PILOT_RUBRICS
from models import ClinicalCase, ClinicalExam, ClinicalRubric


def seed_clinical_content(db: Session) -> bool:
    """Carrega o catálogo legado somente quando o banco ainda está vazio."""
    if db.scalar(select(func.count()).select_from(ClinicalCase)):
        return False

    now = datetime.now(UTC)
    for source in CLINICAL_CASES:
        case = ClinicalCase(
            id=source["id"],
            titulo=source["titulo"],
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
                versao=1,
                status="revisada",
                definicao=PILOT_RUBRICS[source["id"]],
                revisado_por="Equipe clínica MedSync",
                revisado_em=now,
            )
        db.add(case)

    db.commit()
    return True


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
        "titulo": case.titulo,
        "especialidade": case.especialidade,
        "nivel_dificuldade": case.nivel_dificuldade,
        "avaliacao_2_disponivel": bool(
            case.rubrica and case.rubrica.status == "revisada"
        ),
    }
    if include_details:
        data.update(
            {
                "historia_clinica": case.historia_clinica,
                "exame_fisico": case.exame_fisico,
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
