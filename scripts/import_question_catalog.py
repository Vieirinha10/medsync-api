#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import_question_catalog.py (Versão 1.1 - Canônica, Estrita e Atômica)
Importador determinístico do novo catálogo de questões médicas (v2) para o MedSync.

Garantias:
1. Contrato Canônico em Português: ano, instituicao, especialidade, tema, subtema, regiao, tipo_prova, banca, finalidade.
2. Sem Valores Artificiais: sem 2020, sem "Não informada", sem "Clínica Geral".
3. Validação Estrita de Mídia e Elegibilidade: publication_status = ACTIVE, sem quarentena, autonomia textual, has_video = False.
4. Recálculo e Validação de Hashes: content_hash_plain, content_hash_rich, answer_binding_hash, binding de gabarito.
5. Atomicidade Real: transação única. Nenhum commit parcial por lote. Rollback total em qualquer exceção.
6. Proteção do Catálogo v1: detecção e bloqueio de colisão de source_id entre versões.
7. Idempotência Rigorosa: unchanged_count separado; rejeição imediata de conflitos de conteúdo.
"""

import argparse
import hashlib
import json
import logging
import math
import os
import pathlib
import sys
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

# Permitir import dos modelos do MedSync quando executado diretamente
CURRENT_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from database import SessionLocal
    from models import ExamQuestion, QuestionSourceAlias
except ImportError:
    SessionLocal = None
    ExamQuestion = None
    QuestionSourceAlias = None

logger = logging.getLogger("import_question_catalog")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_hash_format(hash_val: Any, field_name: str, line_num: int, source_id: str) -> str:
    if not isinstance(hash_val, str) or len(hash_val) != 64 or not all(c in "0123456789abcdefABCDEF" for c in hash_val):
        raise ValueError(
            f"Linha {line_num} (source_id={source_id}): campo obrigatório '{field_name}' ausente ou malformado "
            f"(deve ter exatamente 64 caracteres hexadecimais, recebido: {hash_val!r})."
        )
    return hash_val.lower()


def validate_and_normalize_record(
    rec: Dict[str, Any],
    line_num: int
) -> Tuple[Dict[str, Any], str, str, str]:
    """
    Valida estritamente cada registro contra o contrato canônico do extrator v1.1.
    Recalcula hashes e valida integridade do gabarito.
    """
    source_id = str(rec.get("source_id") or "").strip()
    if not source_id:
        raise ValueError(f"Linha {line_num}: 'source_id' obrigatório ausente.")

    # 1. Validação de Elegibilidade e Mídia (Regra 8)
    pub_status = rec.get("publication_status")
    if pub_status != "ACTIVE":
        raise ValueError(f"Linha {line_num} (source_id={source_id}): publication_status '{pub_status}' não é ACTIVE.")

    quarantine = rec.get("quarantine_reasons") or []
    if quarantine:
        raise ValueError(f"Linha {line_num} (source_id={source_id}): registro em quarentena: {quarantine}")

    media_class = rec.get("media_classification")
    if media_class not in {"NO_VISUAL_DEPENDENCY", "VISUAL_TERM_CONTEXT_ONLY"}:
        raise ValueError(f"Linha {line_num} (source_id={source_id}): media_classification '{media_class}' inválida.")

    rights_status = rec.get("image_rights_status")
    if rights_status != "NONE_REQUIRED":
        raise ValueError(f"Linha {line_num} (source_id={source_id}): image_rights_status '{rights_status}' não é NONE_REQUIRED.")

    if rec.get("has_video") is not False:
        raise ValueError(f"Linha {line_num} (source_id={source_id}): has_video deve ser False.")

    # 2. Enunciado (Regra 1 e 9)
    stmt_plain = str(rec.get("statement_plain") or "").strip()
    stmt_rich = str(rec.get("statement_rich_html") or stmt_plain).strip()
    if not stmt_plain:
        raise ValueError(f"Linha {line_num} (source_id={source_id}): enunciado de texto plano vazio.")

    # Ano canônico (Regra 1 - sem defaults como 2020)
    ano_raw = rec.get("ano")
    if ano_raw is None:
        raise ValueError(f"Linha {line_num} (source_id={source_id}): campo obrigatório 'ano' ausente.")
    try:
        ano_val = int(ano_raw)
    except (ValueError, TypeError):
        raise ValueError(f"Linha {line_num} (source_id={source_id}): ano inválido: {ano_raw}")

    # 3. Alternativas e Gabarito (Regra 1, 3 e 9 - Vínculo explícito sem inferência)
    corr_letter = str(rec.get("correct_letter") or "").strip()
    if not corr_letter:
        raise ValueError(f"Linha {line_num} (source_id={source_id}): 'correct_letter' obrigatório ausente.")

    raw_alts = rec.get("alternatives") or []
    if len(raw_alts) < 2:
        raise ValueError(f"Linha {line_num} (source_id={source_id}): mínimo de 2 alternativas necessárias.")

    norm_alts = []
    correct_count = 0
    letters_seen = set()

    for idx, alt in enumerate(raw_alts):
        letter = str(alt.get("letter") or alt.get("id") or chr(ord("A") + idx)).strip()
        body_p = str(alt.get("body_plain") or alt.get("body") or alt.get("texto") or "").strip()
        body_r = str(alt.get("body_rich_html") or alt.get("html") or body_p).strip()

        # Item 3 do Codex: Vínculo explícito do gabarito sem qualquer inferência
        if "is_correct" not in alt:
            raise ValueError(
                f"Linha {line_num} (source_id={source_id}): alternativa '{letter}' não possui o campo obrigatório 'is_correct'."
            )
        if not isinstance(alt["is_correct"], bool):
            raise ValueError(
                f"Linha {line_num} (source_id={source_id}): campo 'is_correct' da alternativa '{letter}' deve ser booleano estrito "
                f"(recebido: {alt['is_correct']!r} do tipo {type(alt['is_correct']).__name__})."
            )

        is_corr = alt["is_correct"]

        if letter in letters_seen:
            raise ValueError(f"Linha {line_num} (source_id={source_id}): letra de alternativa duplicada '{letter}'.")
        letters_seen.add(letter)

        if is_corr:
            correct_count += 1
            if letter != corr_letter:
                raise ValueError(
                    f"Linha {line_num} (source_id={source_id}): inconsistência entre flag is_correct=True na alternativa '{letter}' "
                    f"e correct_letter='{corr_letter}'."
                )

        norm_alts.append({
            "id": letter,
            "texto": body_p,
            "body_plain": body_p,
            "body_rich_html": body_r,
            "html": body_r,
            "is_correct": is_corr,
            "answer_pct": alt.get("answer_pct")
        })

    if correct_count != 1:
        raise ValueError(
            f"Linha {line_num} (source_id={source_id}): exatamente 1 alternativa correta é esperada (encontradas {correct_count})."
        )

    if corr_letter not in letters_seen:
        raise ValueError(f"Linha {line_num} (source_id={source_id}): gabarito '{corr_letter}' não encontrado nas alternativas.")

    # 4. Recálculo e validação estrita de hashes obrigatórios (Item 2 do Codex)
    sorted_alts = sorted(norm_alts, key=lambda x: x["id"])
    alts_plain_payload = "|".join(f"{a['id']}:{a['body_plain']}" for a in sorted_alts)
    alts_rich_payload = "|".join(f"{a['id']}:{a['body_rich_html']}" for a in sorted_alts)
    alts_binding_payload = "|".join(f"{a['id']}:{1 if a['is_correct'] else 0}" for a in sorted_alts)

    calc_content_hash_plain = compute_sha256(f"{stmt_plain}||{alts_plain_payload}")
    calc_content_hash_rich = compute_sha256(f"{stmt_rich}||{alts_rich_payload}")
    calc_answer_binding = compute_sha256(f"{calc_content_hash_plain}||{corr_letter}||{alts_binding_payload}")

    exp_content_plain = validate_hash_format(rec.get("content_hash_plain"), "content_hash_plain", line_num, source_id)
    if exp_content_plain != calc_content_hash_plain:
        raise ValueError(
            f"Linha {line_num} (source_id={source_id}): divergência em content_hash_plain! "
            f"Fornecido: {exp_content_plain}, Calculado: {calc_content_hash_plain}"
        )

    exp_content_rich = validate_hash_format(rec.get("content_hash_rich"), "content_hash_rich", line_num, source_id)
    if exp_content_rich != calc_content_hash_rich:
        raise ValueError(
            f"Linha {line_num} (source_id={source_id}): divergência em content_hash_rich! "
            f"Fornecido: {exp_content_rich}, Calculado: {calc_content_hash_rich}"
        )

    exp_binding = validate_hash_format(rec.get("answer_binding_hash"), "answer_binding_hash", line_num, source_id)
    if exp_binding != calc_answer_binding:
        raise ValueError(
            f"Linha {line_num} (source_id={source_id}): divergência em answer_binding_hash! "
            f"Fornecido: {exp_binding}, Calculado: {calc_answer_binding}"
        )

    # 5. Normalização de metadados sem valores artificiais (Regra 1)
    # Campos realmente opcionais permanecem None.
    def clean_opt(val: Any) -> Optional[str]:
        if val is None:
            return None
        s = str(val).strip()
        return s if s else None

    # Cabeçalho para interface legacy
    inst_clean = clean_opt(rec.get("instituicao"))
    cabecalho = f"{inst_clean} · {ano_val}" if inst_clean else f"Prova · {ano_val}"

    # Assunto / Tema sem preenchimento artificial
    esp_clean = clean_opt(rec.get("especialidade"))
    tema_clean = clean_opt(rec.get("tema"))
    subtema_clean = clean_opt(rec.get("subtema"))
    assunto_clean = tema_clean or esp_clean

    # Rank determinístico para amostragem O(1)
    h_int = int(calc_content_hash_plain[:12], 16)
    random_rank = (h_int % 1_000_000) / 1_000_000.0

    cleaned_record = {
        "source_id": source_id,
        "catalog_version": "v2",
        "ano": ano_val,
        "instituicao": inst_clean,
        "cabecalho": cabecalho,
        "especialidade": esp_clean,
        "tema": tema_clean,
        "subtema": subtema_clean,
        "assunto": assunto_clean,
        "banca": clean_opt(rec.get("banca")),
        "finalidade": clean_opt(rec.get("finalidade")),
        "regiao": clean_opt(rec.get("regiao")),
        "tipo_prova": clean_opt(rec.get("tipo_prova")),
        "enunciado": stmt_plain,
        "statement_plain": stmt_plain,
        "statement_rich_html": stmt_rich,
        "alternativas": norm_alts,
        "alternativa_correta_id": corr_letter,
        "fingerprint": f"q_v2_{source_id}",
        "media_classification": media_class,
        "image_rights_status": rights_status,
        "content_hash_plain": calc_content_hash_plain,
        "content_hash_rich": calc_content_hash_rich,
        "answer_binding_hash": calc_answer_binding,
        "random_rank": random_rank,
        "status": "publicada",
        "explicacao": None,
        "explicacao_status": "pendente"
    }

    return cleaned_record, calc_content_hash_plain, calc_content_hash_rich, calc_answer_binding


def rollback_catalog(db: Session, catalog_version: str = "v2") -> int:
    """
    Executa o rollback atômico e reversível de todas as questões e aliases de uma versão do catálogo.
    NUNCA apaga questões de outras versões (ex.: v1).
    """
    if not catalog_version or catalog_version == "v1":
        raise ValueError(f"Rollback do catálogo versão '{catalog_version}' não permitido por segurança.")

    logger.info(f"Iniciando rollback atômico do catálogo '{catalog_version}'...")
    try:
        # Obter IDs das questões v2
        q_ids = db.scalars(
            select(ExamQuestion.id).where(ExamQuestion.catalog_version == catalog_version)
        ).all()

        if q_ids:
            # Apagar aliases vinculados
            db.execute(
                delete(QuestionSourceAlias).where(QuestionSourceAlias.canonical_question_id.in_(q_ids))
            )
            # Apagar questões
            res = db.execute(
                delete(ExamQuestion).where(ExamQuestion.catalog_version == catalog_version)
            )
            deleted_count = res.rowcount or len(q_ids)
        else:
            deleted_count = 0

        db.commit()
        logger.info(f"Rollback concluído com sucesso: {deleted_count} registros removidos.")
        return deleted_count
    except Exception as e:
        db.rollback()
        logger.error(f"Erro no rollback do catálogo '{catalog_version}': {e}")
        raise


def import_catalog(
    db: Session,
    input_jsonl: pathlib.Path,
    catalog_version: str = "v2",
    dry_run: bool = False,
    batch_size: int = 100,
    simulated_failure_step: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Importa o catálogo de questões com atomicidade absoluta e idempotência estrita.
    """
    if not input_jsonl.exists():
        raise FileNotFoundError(f"Arquivo JSONL não encontrado: {input_jsonl}")

    logger.info(f"Lendo catálogo para versão '{catalog_version}': {input_jsonl}")
    records: List[Dict[str, Any]] = []
    with open(input_jsonl, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line_str = line.strip()
            if not line_str:
                continue
            try:
                rec_raw = json.loads(line_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"Linha {line_num}: JSON inválido: {e}")

            cleaned, h_plain, h_rich, h_binding = validate_and_normalize_record(rec_raw, line_num)
            cleaned["catalog_version"] = catalog_version
            records.append(cleaned)

    total_records = len(records)
    logger.info(f"Validação estrutural e criptográfica concluída: {total_records} registros válidos.")

    if dry_run:
        logger.info("[DRY-RUN] Nenhuma gravação persistida no banco.")
        return {
            "status": "DRY_RUN_PASSED",
            "catalog_version": catalog_version,
            "total_records": total_records,
            "inserted_count": 0,
            "unchanged_count": 0,
            "records": records
        }

    # Atomicidade Real: Processamento completo com commit ÚNICO no final
    inserted_count = 0
    unchanged_count = 0

    try:
        for idx, item in enumerate(records, start=1):
            sid = item["source_id"]

            # Checagem de colisão e versão (Regra 4 e 5)
            existing_q = db.scalar(
                select(ExamQuestion).where(ExamQuestion.source_id == sid)
            )

            if existing_q:
                # Regra 4: Se o source_id pertence a outra versão, abortar totalmente!
                if existing_q.catalog_version != catalog_version:
                    raise ValueError(
                        f"COLISÃO DE VERSÃO DETECTADA: source_id '{sid}' já existe no catálogo versão "
                        f"'{existing_q.catalog_version}'. Impossível importar para versão '{catalog_version}'."
                    )

                # Regra 5: Se pertence à mesma versão, verificar igualdade estrita de hashes
                if (
                    existing_q.content_hash_plain == item["content_hash_plain"]
                    and existing_q.answer_binding_hash == item["answer_binding_hash"]
                ):
                    unchanged_count += 1
                    continue
                else:
                    raise ValueError(
                        f"CONFLITO DE HASH DETECTADO: source_id '{sid}' já existe no catálogo '{catalog_version}', "
                        f"mas o conteúdo ou gabarito diverge! "
                        f"Existente: hash_plain={existing_q.content_hash_plain}, binding={existing_q.answer_binding_hash}. "
                        f"Novo: hash_plain={item['content_hash_plain']}, binding={item['answer_binding_hash']}. "
                        f"Importação abortada para evitar sobrescrita silenciosa."
                    )
            else:
                # Novo registro
                new_q = ExamQuestion(
                    source_id=item["source_id"],
                    catalog_version=item["catalog_version"],
                    ano=item["ano"],
                    instituicao=item["instituicao"],
                    cabecalho=item["cabecalho"],
                    especialidade=item["especialidade"],
                    tema=item["tema"],
                    subtema=item["subtema"],
                    assunto=item["assunto"],
                    banca=item["banca"],
                    finalidade=item["finalidade"],
                    regiao=item["regiao"],
                    tipo_prova=item["tipo_prova"],
                    enunciado=item["enunciado"],
                    statement_plain=item["statement_plain"],
                    statement_rich_html=item["statement_rich_html"],
                    alternativas=item["alternativas"],
                    alternativa_correta_id=item["alternativa_correta_id"],
                    fingerprint=item["fingerprint"],
                    media_classification=item["media_classification"],
                    image_rights_status=item["image_rights_status"],
                    content_hash_plain=item["content_hash_plain"],
                    content_hash_rich=item["content_hash_rich"],
                    answer_binding_hash=item["answer_binding_hash"],
                    random_rank=item["random_rank"],
                    status=item["status"],
                    explicacao=item["explicacao"],
                    explicacao_status=item["explicacao_status"],
                )
                db.add(new_q)
                inserted_count += 1

            # Flush periódico opcional para alívio de memória sem efetivar transação
            if idx % batch_size == 0:
                db.flush()

            if simulated_failure_step is not None and idx == simulated_failure_step:
                raise RuntimeError(
                    f"FALHA INJETADA APÓS FLUSH: Falha intencional no registro {idx} "
                    f"(após flush dos primeiros registros) para teste estrito de rollback de persistência."
                )

        # ÚNICO commit após todo o lote ser processado com sucesso absoluto
        db.commit()
        logger.info(
            f"Importação atômica concluída com sucesso: {inserted_count} inseridos, "
            f"{unchanged_count} inalterados (total: {total_records})."
        )
        return {
            "status": "IMPORT_SUCCESSFUL",
            "catalog_version": catalog_version,
            "total_records": total_records,
            "inserted_count": inserted_count,
            "unchanged_count": unchanged_count,
        }

    except Exception as exc:
        db.rollback()
        logger.error(f"FALHA NA IMPORTAÇÃO: Rollback total executado. Zero registros parciais gravados. Causa: {exc}")
        raise


def main():
    parser = argparse.ArgumentParser(description="Importador Canônico e Atômico do Catálogo de Questões MedSync v1.1")
    parser.add_argument("--input-jsonl", type=str, required=True, help="Caminho do arquivo JSONL canônico")
    parser.add_argument("--catalog-version", type=str, default="v2", help="Versão do catálogo de destino (default: v2)")
    parser.add_argument("--dry-run", action="store_true", help="Apenas valida o arquivo sem gravar no banco")
    parser.add_argument("--batch-size", type=int, default=100, help="Tamanho do flush em memória (default: 100)")
    parser.add_argument("--rollback-catalog-version", type=str, default=None, help="Executa o rollback seguro de uma versão")
    parser.add_argument("--report-json", type=str, default=None, help="Caminho de saída para relatório em JSON")

    args = parser.parse_args()

    if SessionLocal is None:
        print("ERRO: Módulos de banco de dados não puderam ser carregados.", file=sys.stderr)
        sys.exit(1)

    db = SessionLocal()
    try:
        if args.rollback_catalog_version:
            deleted = rollback_catalog(db, args.rollback_catalog_version)
            print(f"Rollback concluído: {deleted} questões removidas para a versão '{args.rollback_catalog_version}'.")
            return

        input_p = pathlib.Path(args.input_jsonl)
        report = import_catalog(
            db=db,
            input_jsonl=input_p,
            catalog_version=args.catalog_version,
            dry_run=args.dry_run,
            batch_size=args.batch_size
        )

        if args.report_json:
            out_p = pathlib.Path(args.report_json)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            with open(out_p, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"Relatório gravado em {out_p}")

        print(json.dumps(report, indent=2, ensure_ascii=False))

    finally:
        db.close()


if __name__ == "__main__":
    main()
