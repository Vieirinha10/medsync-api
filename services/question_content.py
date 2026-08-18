"""Carga idempotente do catálogo validado de questões."""

import gzip
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import ExamQuestion

CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "question_catalog.json.gz"


def seed_question_content(db: Session) -> int:
    if not CATALOG_PATH.exists():
        return 0

    with gzip.open(CATALOG_PATH, "rt", encoding="utf-8") as handle:
        catalog = json.load(handle)

    existing_ids = set(db.scalars(select(ExamQuestion.id)).all())
    new_items = [
        ExamQuestion(
            id=item["id"],
            ano=item["ano"],
            instituicao=item["instituicao"],
            cabecalho=item["cabecalho"],
            especialidade=item["especialidade"],
            assunto=item["assunto"],
            enunciado=item["enunciado"],
            alternativas=item["alternativas"],
            alternativa_correta_id=item["alternativa_correta_id"],
            fingerprint=item["fingerprint"],
            status=item["status"],
        )
        for item in catalog
        if item["id"] not in existing_ids
    ]
    if not new_items:
        return 0

    db.add_all(new_items)
    db.commit()
    return len(new_items)
