#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
purge_non_medical_questions.py
Remove questões de assuntos não-médicos (Direito, Português, Informática,
Inglês, USMLE, Matemática, RLM, Atualidades, Sexualidade, etc.) do catálogo v2.
"""

import json
import logging
import pathlib
import sys
from typing import Dict, List

# Permitir imports da API
CURRENT_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sqlalchemy import delete, select, func
from database import SessionLocal
from models import ExamQuestion, QuestionAttempt, QuestionReport, QuestionSourceAlias

logger = logging.getLogger("purge_non_medical_questions")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

EXCLUDED_TOPICS = [
    "Direito",
    "Língua Portuguesa (Português)",
    "USMLE",
    "Informática",
    "Outros",
    "Raciocínio Lógico",
    "Inglês",
    "Maus tratos à crianças e adolescentes",
    "Matemática",
    "Atualidades",
    "Sexualidade",
    "Formação Geral - ENADE"
]

def purge_non_medical(db_session, catalog_version: str = "v2") -> Dict[str, object]:
    logger.info(f"Iniciando auditoria para expurgo de questões não-médicas no catálogo '{catalog_version}'...")

    breakdown = {}
    total_to_remove = 0
    all_qids = []

    for topic in EXCLUDED_TOPICS:
        qids = db_session.scalars(
            select(ExamQuestion.id).where(
                ExamQuestion.catalog_version == catalog_version,
                ExamQuestion.assunto == topic
            )
        ).all()
        cnt = len(qids)
        breakdown[topic] = cnt
        total_to_remove += cnt
        all_qids.extend(qids)
        logger.info(f"  - {topic}: {cnt} questões identificadas")

    logger.info(f"Total de questões identificadas para expurgo: {total_to_remove}")

    if total_to_remove == 0:
        logger.info("Nenhuma questão não-médica encontrada.")
        return {
            "catalog_version": catalog_version,
            "total_purged": 0,
            "breakdown": breakdown
        }

    # Transação atômica de remoção
    try:
        # 1. Apagar tentativas vinculadas
        del_attempts = db_session.execute(
            delete(QuestionAttempt).where(QuestionAttempt.id_questao.in_(all_qids))
        ).rowcount

        # 2. Apagar relatos vinculados
        del_reports = db_session.execute(
            delete(QuestionReport).where(QuestionReport.id_questao.in_(all_qids))
        ).rowcount

        # 3. Apagar aliases vinculados
        del_aliases = db_session.execute(
            delete(QuestionSourceAlias).where(QuestionSourceAlias.canonical_question_id.in_(all_qids))
        ).rowcount

        # 4. Apagar questões
        del_questions = db_session.execute(
            delete(ExamQuestion).where(ExamQuestion.id.in_(all_qids))
        ).rowcount

        db_session.commit()
        logger.info(
            f"Expurgo atômico concluído com sucesso: {del_questions} questões removidas "
            f"({del_attempts} tentativas, {del_reports} relatos, {del_aliases} aliases)."
        )

        return {
            "status": "PURGE_SUCCESSFUL",
            "catalog_version": catalog_version,
            "total_purged": del_questions,
            "attempts_removed": del_attempts,
            "reports_removed": del_reports,
            "aliases_removed": del_aliases,
            "breakdown": breakdown
        }

    except Exception as e:
        db_session.rollback()
        logger.error(f"Erro durante o expurgo: {e}")
        raise

def purge_batch_files(batch_dir: pathlib.Path, excluded_topics: List[str]):
    """Filtra também os arquivos JSONL nos fixtures locais para garantir consistência reproduzível."""
    if not batch_dir.exists():
        return

    excluded_set = set(excluded_topics)
    logger.info(f"Filtrando arquivos JSONL em {batch_dir}...")
    for jsonl_file in batch_dir.glob("*.jsonl"):
        temp_file = jsonl_file.with_suffix(".jsonl.tmp")
        kept = 0
        removed = 0
        with open(jsonl_file, "r", encoding="utf-8") as in_f, open(temp_file, "w", encoding="utf-8") as out_f:
            for line in in_f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                assunto = rec.get("tema") or rec.get("especialidade") or "Outros"
                if assunto in excluded_set or rec.get("tema") in excluded_set or rec.get("especialidade") in excluded_set:
                    removed += 1
                    continue
                out_f.write(line)
                kept += 1

        temp_file.replace(jsonl_file)
        logger.info(f"  {jsonl_file.name}: {kept:,} mantidos | {removed:,} removidos")

def main():
    db = SessionLocal()
    try:
        report = purge_non_medical(db, catalog_version="v2")
        reports_dir = REPO_ROOT / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = reports_dir / "purged_non_medical_questions_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Relatório gravado em {report_path}")

        batch_dir = REPO_ROOT / "data" / "catalog_batches"
        purge_batch_files(batch_dir, EXCLUDED_TOPICS)

        print(json.dumps(report, indent=2, ensure_ascii=False))
    finally:
        db.close()

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    main()
