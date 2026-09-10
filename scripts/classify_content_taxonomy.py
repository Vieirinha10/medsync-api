"""Classifica conteúdos em lotes retomáveis e grava somente na camada sombra.

Exemplos:
  python -m scripts.classify_content_taxonomy --content-type questao --estimate
  python -m scripts.classify_content_taxonomy --content-type questao --apply
  python -m scripts.classify_content_taxonomy --resume-run <run_id> --apply
"""

from __future__ import annotations

import argparse
import json
import os
import uuid
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from database import SessionLocal
from models import (
    ClinicalCase,
    ContentTaxonomyClassification,
    ExamQuestion,
    MedicalTaxonomyVersion,
    TaxonomyClassificationRun,
    VisualChallenge,
)
from services.content_taxonomy_classifier import (
    AUTO_VERIFY_THRESHOLD,
    MAX_BATCH_ITEMS,
    ClassificationBatch,
    ContentItem,
    OpenAITaxonomyClassifier,
    VerificationBatch,
    resolve_outcome,
    taxonomy_codes,
)

DEFAULT_TAXONOMY_VERSION = "semantic-v1"


def chunks(items: Iterable[Any], size: int) -> Iterable[list[Any]]:
    batch: list[Any] = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def _alternative_payload(alternatives: list[dict[str, Any]] | None) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for item in alternatives or []:
        body = (
            item.get("body_plain")
            or item.get("texto")
            or item.get("text")
            or item.get("body")
            or ""
        )
        result.append({"id": str(item.get("id") or ""), "text": str(body)})
    return result


def question_item(question: ExamQuestion) -> ContentItem:
    return ContentItem(
        content_id=str(question.id),
        content_type="questao",
        title=question.cabecalho or "",
        body=question.statement_plain or question.enunciado,
        alternatives=_alternative_payload(question.alternativas),
        correct_answer_id=question.alternativa_correta_id,
        current_specialty=question.especialidade,
        current_theme=question.tema,
        current_subject=question.subtema or question.assunto,
    )


def case_item(case: ClinicalCase) -> ContentItem:
    exams = "\n".join(
        f"{exam.nome}: {exam.resultado}" for exam in sorted(case.exames, key=lambda row: row.ordem)
    )
    return ContentItem(
        content_id=str(case.id),
        content_type="caso_clinico",
        title=case.titulo_publico or case.titulo,
        body="\n\n".join(
            part
            for part in (case.historia_clinica, case.exame_fisico, exams)
            if part
        ),
        current_specialty=case.especialidade,
        current_difficulty=case.nivel_dificuldade,
    )


def challenge_item(challenge: VisualChallenge) -> ContentItem:
    return ContentItem(
        content_id=challenge.id,
        content_type="desafio_visual",
        title=challenge.titulo,
        body="\n".join(
            part
            for part in (
                challenge.pergunta,
                f"Descrição visual: {challenge.imagem_alt}",
                f"Diagnóstico de referência: {challenge.diagnostico_correto}",
            )
            if part
        ),
        alternatives=_alternative_payload(challenge.alternativas),
        correct_answer_id=challenge.alternativa_correta_id,
        current_specialty=challenge.especialidade,
        current_difficulty=challenge.dificuldade,
    )


def load_source_rows(
    db: Session,
    content_type: str,
    *,
    cursor_after_id: str | None,
    limit: int | None,
) -> list[Any]:
    if content_type == "questao":
        statement = select(ExamQuestion).where(
            ExamQuestion.catalog_version == "v2",
            ExamQuestion.status == "publicada",
        )
        if cursor_after_id:
            statement = statement.where(ExamQuestion.id > int(cursor_after_id))
        statement = statement.order_by(ExamQuestion.id)
    elif content_type == "caso_clinico":
        statement = (
            select(ClinicalCase)
            .where(ClinicalCase.status == "publicado")
            .options(selectinload(ClinicalCase.exames))
        )
        if cursor_after_id:
            statement = statement.where(ClinicalCase.id > int(cursor_after_id))
        statement = statement.order_by(ClinicalCase.id)
    elif content_type == "desafio_visual":
        statement = select(VisualChallenge).where(
            VisualChallenge.status == "publicado"
        )
        if cursor_after_id:
            statement = statement.where(VisualChallenge.id > cursor_after_id)
        statement = statement.order_by(VisualChallenge.id)
    else:
        raise ValueError(f"Tipo de conteúdo inválido: {content_type}")
    if limit is not None:
        statement = statement.limit(limit)
    return list(db.scalars(statement).all())


def source_count(db: Session, content_type: str) -> int:
    if content_type == "questao":
        statement = select(func.count(ExamQuestion.id)).where(
            ExamQuestion.catalog_version == "v2",
            ExamQuestion.status == "publicada",
        )
    elif content_type == "caso_clinico":
        statement = select(func.count(ClinicalCase.id)).where(
            ClinicalCase.status == "publicado"
        )
    elif content_type == "desafio_visual":
        statement = select(func.count(VisualChallenge.id)).where(
            VisualChallenge.status == "publicado"
        )
    else:
        raise ValueError(f"Tipo de conteúdo inválido: {content_type}")
    return int(db.scalar(statement) or 0)


def to_content_item(row: Any, content_type: str) -> ContentItem:
    if content_type == "questao":
        return question_item(row)
    if content_type == "caso_clinico":
        return case_item(row)
    return challenge_item(row)


def ensure_taxonomy_version(db: Session, version_id: str) -> None:
    if db.get(MedicalTaxonomyVersion, version_id):
        return
    db.add(
        MedicalTaxonomyVersion(
            id=version_id,
            nome="Taxonomia semântica unificada v1",
            descricao=(
                "Classificação em sombra de questões, casos clínicos e desafios "
                "visuais para filtros e trilhas de aprendizagem."
            ),
            status="rascunho",
        )
    )
    db.flush()


def create_or_resume_run(
    db: Session,
    *,
    content_type: str,
    taxonomy_version: str,
    classifier_model: str,
    verifier_model: str,
    batch_size: int,
    threshold: float,
    resume_run: str | None,
) -> TaxonomyClassificationRun:
    if resume_run:
        run = db.get(TaxonomyClassificationRun, resume_run)
        if not run:
            raise ValueError(f"Execução não encontrada: {resume_run}")
        if run.content_type != content_type or run.taxonomy_version != taxonomy_version:
            raise ValueError("A execução não pertence ao tipo/versão solicitados.")
        return run

    run = TaxonomyClassificationRun(
        id=uuid.uuid4().hex,
        taxonomy_version=taxonomy_version,
        content_type=content_type,
        status="preparando",
        configuration={
            "classifier_model": classifier_model,
            "verifier_model": verifier_model,
            "batch_size": batch_size,
            "automatic_threshold": threshold,
        },
    )
    db.add(run)
    db.flush()
    return run


def persist_batch(
    db: Session,
    *,
    run: TaxonomyClassificationRun,
    contents: list[ContentItem],
    classified: ClassificationBatch,
    verified: VerificationBatch,
    classifier_model: str,
    verifier_model: str,
    threshold: float,
) -> tuple[int, int]:
    classified_by_id = {item.content_id: item for item in classified.items}
    verified_by_id = {item.content_id: item for item in verified.items}
    verified_count = 0
    review_count = 0

    for content in contents:
        first = classified_by_id[content.content_id]
        second = verified_by_id[content.content_id]
        outcome = resolve_outcome(first, second, threshold=threshold)
        decision = outcome.decision
        specialty_code, theme_code, subject_code = taxonomy_codes(
            decision.specialty, decision.theme, decision.subject
        )
        assignment = db.scalar(
            select(ContentTaxonomyClassification).where(
                ContentTaxonomyClassification.content_type == content.content_type,
                ContentTaxonomyClassification.content_id == content.content_id,
                ContentTaxonomyClassification.taxonomy_version == run.taxonomy_version,
            )
        )
        if assignment is None:
            assignment = ContentTaxonomyClassification(
                content_type=content.content_type,
                content_id=content.content_id,
                taxonomy_version=run.taxonomy_version,
                source_hash=content.source_hash(),
                classification_method="semantic_double_pass_v1",
            )
            db.add(assignment)

        assignment.specialty_code = specialty_code
        assignment.specialty_label = decision.specialty
        assignment.theme_code = theme_code
        assignment.theme_label = decision.theme
        assignment.subject_code = subject_code
        assignment.subject_label = decision.subject
        assignment.learning_objectives = decision.learning_objectives
        assignment.competencies = decision.competencies
        assignment.clinical_contexts = decision.clinical_contexts
        assignment.tags = decision.tags
        assignment.difficulty = decision.difficulty
        assignment.confidence = outcome.confidence
        assignment.classifier_confidence = first.confidence
        assignment.verifier_confidence = second.confidence
        assignment.verifier_agrees = second.agrees
        assignment.status = outcome.status
        assignment.classification_method = "semantic_double_pass_v1"
        assignment.classifier_model = classifier_model
        assignment.verifier_model = verifier_model
        assignment.evidence = decision.evidence
        assignment.ambiguity_reason = outcome.reason
        assignment.classifier_payload = first.model_dump(mode="json")
        assignment.verifier_payload = second.model_dump(mode="json")
        assignment.source_hash = content.source_hash()
        assignment.run_id = run.id
        if outcome.status == "verificada":
            verified_count += 1
        else:
            review_count += 1

    return verified_count, review_count


def execute(args: argparse.Namespace) -> dict[str, Any]:
    with SessionLocal() as db:
        total = source_count(db, args.content_type)
        if args.estimate:
            effective = min(total, args.limit) if args.limit else total
            return {
                "content_type": args.content_type,
                "source_items": total,
                "items_to_process": effective,
                "batch_size": args.batch_size,
                "classifier_batches": (effective + args.batch_size - 1) // args.batch_size,
                "verifier_batches": (effective + args.batch_size - 1) // args.batch_size,
                "database_mutations": 0,
            }
        if not args.apply:
            raise ValueError("Use --estimate ou confirme a execução com --apply.")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY não configurada.")

        ensure_taxonomy_version(db, args.taxonomy_version)
        run = create_or_resume_run(
            db,
            content_type=args.content_type,
            taxonomy_version=args.taxonomy_version,
            classifier_model=args.classifier_model,
            verifier_model=args.verifier_model,
            batch_size=args.batch_size,
            threshold=args.threshold,
            resume_run=args.resume_run,
        )
        run.status = "executando"
        db.commit()

        rows = load_source_rows(
            db,
            args.content_type,
            cursor_after_id=run.cursor_after_id,
            limit=args.limit,
        )
        client = OpenAITaxonomyClassifier(
            api_key=api_key,
            classifier_model=args.classifier_model,
            verifier_model=args.verifier_model,
        )

        try:
            for source_batch in chunks(rows, args.batch_size):
                contents = [to_content_item(row, args.content_type) for row in source_batch]
                classified = client.classify(contents)
                verified = client.verify(contents, classified)
                accepted, review = persist_batch(
                    db,
                    run=run,
                    contents=contents,
                    classified=classified,
                    verified=verified,
                    classifier_model=args.classifier_model,
                    verifier_model=args.verifier_model,
                    threshold=args.threshold,
                )
                run.processed_count += len(contents)
                run.verified_count += accepted
                run.review_count += review
                run.cursor_after_id = contents[-1].content_id
                db.commit()
                print(
                    json.dumps(
                        {
                            "run_id": run.id,
                            "cursor": run.cursor_after_id,
                            "processed": run.processed_count,
                            "verified": run.verified_count,
                            "review": run.review_count,
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
        except Exception as exc:
            db.rollback()
            run = db.get(TaxonomyClassificationRun, run.id)
            run.status = "falhou"
            run.failed_count += len(source_batch)
            run.error_summary = str(exc)[:4000]
            db.commit()
            raise

        run.status = "concluida"
        run.finished_at = datetime.now(UTC)
        db.commit()
        return {
            "run_id": run.id,
            "content_type": run.content_type,
            "processed": run.processed_count,
            "verified": run.verified_count,
            "review_required": run.review_count,
            "failed": run.failed_count,
            "status": run.status,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--content-type",
        choices=("questao", "caso_clinico", "desafio_visual"),
        default="questao",
    )
    parser.add_argument("--taxonomy-version", default=DEFAULT_TAXONOMY_VERSION)
    parser.add_argument(
        "--classifier-model",
        default=os.getenv("TAXONOMY_CLASSIFIER_MODEL", "gpt-5.6"),
    )
    parser.add_argument(
        "--verifier-model",
        default=os.getenv("TAXONOMY_VERIFIER_MODEL", "gpt-5.6"),
    )
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--threshold", type=float, default=AUTO_VERIFY_THRESHOLD)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume-run")
    parser.add_argument("--estimate", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.batch_size <= MAX_BATCH_ITEMS:
        parser.error(f"--batch-size deve estar entre 1 e {MAX_BATCH_ITEMS}")
    if not 0.5 <= args.threshold <= 1:
        parser.error("--threshold deve estar entre 0.5 e 1")
    if args.estimate and args.apply:
        parser.error("Escolha somente --estimate ou --apply")
    return args


if __name__ == "__main__":
    print(json.dumps(execute(parse_args()), ensure_ascii=False, indent=2))
