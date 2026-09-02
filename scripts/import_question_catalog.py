#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import_question_catalog.py
Importador robusto, determinístico e idempotente do catálogo de questões MedSync.
Suporta execução via CLI e importação programática como módulo.
"""

import argparse
import hashlib
import json
import os
import pathlib
import random
import sys
import time
from typing import Any, Dict, List, Optional, Set

# Adicionar pasta raiz ao sys.path para importar models e database
ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from database import SessionLocal
from models import ExamQuestion, QuestionSourceAlias

def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def validate_record_for_import(rec: Dict[str, Any], line_num: int) -> List[str]:
    errors = []
    qid = str(rec.get("source_id", "DESCONHECIDO"))

    if not rec.get("source_id"):
        errors.append(f"Linha {line_num}: SOURCE_ID_AUSENTE")

    stmt_plain = rec.get("statement_plain", "")
    if not stmt_plain or len(stmt_plain.strip()) < 5:
        errors.append(f"Linha {line_num} [{qid}]: STATEMENT_PLAIN_INVALIDO")

    alts = rec.get("alternatives", [])
    if len(alts) < 2:
        errors.append(f"Linha {line_num} [{qid}]: ALTERNATIVAS_INSUFICIENTES ({len(alts)})")

    letters = [a.get("letter") for a in alts]
    if len(letters) != len(set(letters)):
        errors.append(f"Linha {line_num} [{qid}]: LETRAS_DUPLICADAS_NAS_ALTERNATIVAS")

    correct_letters = [a.get("letter") for a in alts if a.get("is_correct")]
    if len(correct_letters) != 1:
        errors.append(f"Linha {line_num} [{qid}]: CARDINALIDADE_GABARITO_INVALIDA ({len(correct_letters)})")
    else:
        if correct_letters[0] != rec.get("correct_letter"):
            errors.append(f"Linha {line_num} [{qid}]: CONFLITO_CORRECT_LETTER ({correct_letters[0]} vs {rec.get('correct_letter')})")

    if rec.get("explanation_status") != "PENDING":
        errors.append(f"Linha {line_num} [{qid}]: EXPLANATION_STATUS_DEVE_SER_PENDING ({rec.get('explanation_status')})")

    return errors

def rollback_catalog(db: Session, version: str) -> int:
    print(f"Iniciando rollback do catálogo versão '{version}'...")
    qids = list(db.scalars(select(ExamQuestion.id).where(ExamQuestion.catalog_version == version)).all())
    if not qids:
        print(f"Nenhum registro encontrado para catalog_version='{version}'.")
        return 0

    db.execute(delete(QuestionSourceAlias).where(QuestionSourceAlias.canonical_question_id.in_(qids)))
    db.execute(delete(ExamQuestion).where(ExamQuestion.catalog_version == version))
    db.commit()
    print(f"Rollback concluído: {len(qids):,} questões da versão '{version}' removidas com sucesso.")
    return len(qids)

def import_catalog(
    db: Session,
    jsonl_path: pathlib.Path,
    catalog_version: str = "v2",
    batch_size: int = 100,
    dry_run: bool = False,
    resume: bool = False
) -> Dict[str, Any]:
    print("================================================================================")
    print(f"IMPORTADOR DE QUESTÕES MEDSYNC - VERSÃO {catalog_version}")
    print(f"Arquivo de Entrada: {jsonl_path.name}")
    print(f"Modo Dry-Run      : {dry_run}")
    print(f"Batch Size        : {batch_size}")
    print("================================================================================")

    records_to_process = []
    validation_errors = []
    seen_ids = set()

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            l = line.strip()
            if not l:
                continue
            try:
                rec = json.loads(l)
            except Exception as e:
                validation_errors.append(f"Linha {line_num}: JSON_PARSE_ERROR: {e}")
                continue

            sid = str(rec.get("source_id"))
            if sid in seen_ids:
                validation_errors.append(f"Linha {line_num}: SOURCE_ID_DUPLICADO_NO_ARQUIVO: {sid}")
            seen_ids.add(sid)

            errs = validate_record_for_import(rec, line_num)
            validation_errors.extend(errs)
            records_to_process.append(rec)

    total_records = len(records_to_process)
    print(f"Total de registros lidos: {total_records:,}")

    if validation_errors:
        print(f"\nERRO CRÍTICO: {len(validation_errors)} erros de validação encontrados. Abortando!", file=sys.stderr)
        raise ValueError(f"Erros de validação na importação: {validation_errors[:10]}")

    existing_source_ids = set(
        db.scalars(
            select(ExamQuestion.source_id).where(ExamQuestion.source_id.in_(list(seen_ids)))
        ).all()
    )
    print(f"Registros já existentes no banco: {len(existing_source_ids):,}")

    if dry_run:
        print("\nMODO DRY-RUN ATIVO: Nenhuma alteração gravada no banco.")
        return {
            "catalog_version": catalog_version,
            "mode": "DRY_RUN",
            "total_validated": total_records,
            "already_in_db": len(existing_source_ids),
            "to_insert": total_records - len(existing_source_ids),
            "status": "DRY_RUN_PASSED"
        }

    inserted_count = 0
    skipped_count = 0
    random.seed(42)

    for i in range(0, total_records, batch_size):
        batch = records_to_process[i:i + batch_size]
        for rec in batch:
            sid = str(rec["source_id"])
            if sid in existing_source_ids:
                if resume:
                    skipped_count += 1
                    continue
                else:
                    existing_q = db.scalar(select(ExamQuestion).where(ExamQuestion.source_id == sid))
                    if existing_q:
                        existing_q.ano = rec.get("year") or 2020
                        existing_q.instituicao = rec.get("institution") or "Não informada"
                        existing_q.especialidade = rec.get("specialty") or "Clínica Geral"
                        existing_q.assunto = rec.get("theme") or "Geral"
                        existing_q.banca = rec.get("banca")
                        existing_q.finalidade = rec.get("finalidade")
                        existing_q.region = rec.get("region")
                        existing_q.statement_plain = rec["statement_plain"]
                        existing_q.statement_rich_html = rec.get("statement_rich_html") or rec["statement_plain"]
                        existing_q.enunciado = rec["statement_plain"]
                        frontend_alts = [{"id": a["letter"], "texto": a["body_plain"], "html": a.get("body_rich_html", a["body_plain"])} for a in rec["alternatives"]]
                        existing_q.alternativas = frontend_alts
                        existing_q.alternativa_correta_id = rec["correct_letter"]
                        existing_q.catalog_version = catalog_version
                        existing_q.content_hash = rec.get("content_hash") or rec.get("content_hash_plain")
                        existing_q.answer_binding_hash = rec.get("answer_binding_hash")
                        existing_q.media_classification = rec.get("media_classification", "NO_VISUAL_DEPENDENCY")
                        existing_q.image_rights_status = rec.get("image_rights_status", "NONE_REQUIRED")
                        skipped_count += 1
                        continue

            frontend_alts = [
                {
                    "id": a["letter"],
                    "texto": a["body_plain"],
                    "html": a.get("body_rich_html", a["body_plain"])
                }
                for a in rec["alternatives"]
            ]

            spec = rec.get("specialty") or "Clínica Geral"
            theme = rec.get("theme") or "Geral"
            ano_val = rec.get("year") or 2020
            inst_val = rec.get("institution") or "Não informada"
            banca_val = rec.get("banca")
            cabecalho_parts = [p for p in [banca_val, inst_val, str(ano_val)] if p]
            cabecalho_str = " · ".join(cabecalho_parts)[:240]

            new_q = ExamQuestion(
                ano=ano_val,
                instituicao=inst_val[:180],
                cabecalho=cabecalho_str,
                especialidade=spec[:120],
                assunto=theme[:160],
                enunciado=rec["statement_plain"],
                alternativas=frontend_alts,
                alternativa_correta_id=rec["correct_letter"],
                fingerprint=rec.get("content_hash") or rec.get("content_hash_plain") or compute_sha256(sid),
                explicacao=None,
                explicacao_status="pendente",
                status="publicada",
                catalog_version=catalog_version,
                source_id=sid,
                statement_plain=rec["statement_plain"],
                statement_rich_html=rec.get("statement_rich_html") or rec["statement_plain"],
                random_rank=random.random(),
                media_classification=rec.get("media_classification", "NO_VISUAL_DEPENDENCY"),
                image_rights_status=rec.get("image_rights_status", "NONE_REQUIRED"),
                content_hash=rec.get("content_hash") or rec.get("content_hash_plain"),
                answer_binding_hash=rec.get("answer_binding_hash"),
                banca=banca_val,
                finalidade=rec.get("finalidade"),
                region=rec.get("region")
            )
            db.add(new_q)
            inserted_count += 1

        db.commit()
        print(f"Lote {i // batch_size + 1} processado. Inseridos: {inserted_count:,}")

    print("\n================================================================================")
    print("IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
    print(f"Total Inserido          : {inserted_count:,}")
    print(f"Total Existente/Atualizado: {skipped_count:,}")
    print("================================================================================")

    return {
        "catalog_version": catalog_version,
        "input_file": str(jsonl_path),
        "total_records_in_file": total_records,
        "inserted_count": inserted_count,
        "skipped_or_updated_count": skipped_count,
        "status": "IMPORT_SUCCESSFUL",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")
    }

def main():
    parser = argparse.ArgumentParser(description="Importador de Catálogo de Questões MedSync")
    parser.add_argument("--input-jsonl", type=str, help="Caminho do arquivo JSONL pronto para importação")
    parser.add_argument("--catalog-version", type=str, default="v2", help="Versão do catálogo a importar (padrão: v2)")
    parser.add_argument("--batch-size", type=int, default=100, help="Tamanho do lote de inserção (padrão: 100)")
    parser.add_argument("--dry-run", action="store_true", help="Executa apenas validação sem persistir no banco")
    parser.add_argument("--resume", action="store_true", help="Pula source_ids já importados")
    parser.add_argument("--rollback-catalog-version", type=str, default=None, help="Executa rollback seguro apenas da versão informada")
    parser.add_argument("--report-json", type=str, default=None, help="Caminho para salvar o relatório de execução em JSON")

    args = parser.parse_args()
    db: Session = SessionLocal()

    if args.rollback_catalog_version:
        deleted = rollback_catalog(db, args.rollback_catalog_version)
        db.close()
        sys.exit(0)

    if not args.input_jsonl:
        print("ERRO: --input-jsonl é obrigatório quando não estiver em modo rollback.", file=sys.stderr)
        sys.exit(1)

    jsonl_path = pathlib.Path(args.input_jsonl)
    if not jsonl_path.exists():
        print(f"ERRO: Arquivo JSONL não encontrado: {jsonl_path}", file=sys.stderr)
        sys.exit(1)

    report = import_catalog(
        db=db,
        jsonl_path=jsonl_path,
        catalog_version=args.catalog_version,
        batch_size=args.batch_size,
        dry_run=args.dry_run,
        resume=args.resume
    )

    if args.report_json:
        with open(args.report_json, "w", encoding="utf-8") as rf:
            json.dump(report, rf, indent=2, ensure_ascii=False)

    db.close()

if __name__ == "__main__":
    main()
