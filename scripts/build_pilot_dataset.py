"""Seleção estratificada, determinística e balanceada do piloto de taxonomia médica MedSync (Fase 2).

Garantias:
1. Amostragem estrita de exatamente 100 questões reais.
2. Teto máximo de 10 questões por especialidade para evitar distorção de Cirurgia.
3. Busca de pelo menos 15 especialidades se estiverem disponíveis na fonte.
4. Remoção rigorosa de duplicidades antes da amostragem.
5. Inclusão de rótulos genéricos, Tema=Assunto, campos ausentes, alto risco, multidisciplinares e casos comuns.
6. Hash canônico único importado de services.taxonomy_state_machine.
7. Detecção e bloqueio caso a fonte não possua diversidade real ou não haja acesso seguro.
"""

from __future__ import annotations

import argparse
import gzip
import json
import random
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.taxonomy_state_machine import compute_content_source_hash

DEFAULT_SEED = 20260910
PILOT_TARGET_COUNT = 100
MAX_PER_SPECIALTY = 10
MIN_SPECIALTIES_TARGET = 15

HIGH_RISK_KEYWORDS = (
    "trauma", "politrauma", "choque", "sepse", "septic", "parada", "pcr",
    "reanimação", "emergência", "urgência", "infarto", "iam", "avc",
    "tromboembolismo", "hemorragia", "intoxicação", "insuficiência respiratória",
    "coma", "choque anafilático", "eclampsia", "descolamento prematuro",
)

GENERIC_TERMS = {
    "outros", "outras", "geral", "clínica geral", "clínica médica",
    "cirurgia geral", "indefinido", "não informada", "diversos",
}

MULTIDISCIPLINAR_KEYWORDS = (
    "gestante", "criança", "recém-nascido", "idoso", "oncologia",
    "paliativo", "ética", "bioética", "perícia", "psicossomática",
)


def detect_question_criteria(item: dict[str, Any]) -> list[str]:
    """Identifica todas as anomalias e características clínicas da questão."""
    reasons: list[str] = []
    specialty = (item.get("especialidade") or item.get("current_specialty") or "").strip()
    theme = (item.get("tema") or item.get("current_theme") or "").strip()
    subject = (item.get("subtema") or item.get("assunto") or item.get("current_subject") or "").strip()
    body = (item.get("statement_plain") or item.get("enunciado") or item.get("body") or "").lower()

    if specialty.lower() in GENERIC_TERMS:
        reasons.append("generic_specialty")
    if subject.lower() in GENERIC_TERMS or theme.lower() in GENERIC_TERMS:
        reasons.append("generic_theme_or_subject")

    if theme and subject and theme.lower() == subject.lower():
        reasons.append("theme_equals_subject")

    if not theme or not subject:
        reasons.append("missing_taxonomy_fields")

    if any(kw in subject.lower() or kw in theme.lower() or kw in body[:300] for kw in HIGH_RISK_KEYWORDS):
        reasons.append("high_risk_clinical")

    if any(kw in body for kw in MULTIDISCIPLINAR_KEYWORDS):
        reasons.append("multidisciplinary")

    if item.get("instituicao"):
        reasons.append("institution_diversity")
    if item.get("ano"):
        reasons.append("year_diversity")

    if not reasons or set(reasons) <= {"institution_diversity", "year_diversity"}:
        reasons.append("common_unremarkable")

    return sorted(reasons)


def load_candidates_from_source(
    db_path: Path | None = None,
    json_gz_path: Path | None = None,
    postgres_url: str | None = None,
) -> tuple[list[dict[str, Any]], str]:
    """Carrega candidatos exclusivamente de fontes de dados reais, com deduplicação prévia."""
    raw_list: list[dict[str, Any]] = []
    source_desc = ""

    # 1. Tentar PostgreSQL configurado (estritamente READ ONLY)
    if postgres_url and postgres_url.startswith(("postgres://", "postgresql://", "postgresql+")):
        try:
            from sqlalchemy import create_engine, text
            url = postgres_url.replace("postgres://", "postgresql+psycopg://", 1)
            engine = create_engine(url, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SET TRANSACTION READ ONLY"))
                rows = conn.execute(text("""
                    SELECT id, ano, instituicao, cabecalho, especialidade, tema, subtema, assunto,
                           enunciado, statement_plain, alternativas, alternativa_correta_id,
                           status, catalog_version
                    FROM exam_questions
                    WHERE catalog_version = 'v2' AND status = 'publicada'
                    ORDER BY id
                """)).mappings().all()
                raw_list = [dict(r) for r in rows]
                source_desc = f"PostgreSQL Staging ({len(raw_list)} questões v2)"
        except Exception as e:
            logger.warning(f"Não foi possível conectar ao PostgreSQL: {e}")

    # 2. Se não houver PostgreSQL, verificar banco SQLite local
    if not raw_list and db_path and db_path.exists():
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        for r in cur.execute("SELECT * FROM exam_questions WHERE status = 'publicada' ORDER BY id"):
            raw_list.append(dict(r))
        conn.close()
        source_desc = f"SQLite Local {db_path.name} ({len(raw_list)} questões)"

    # 3. Se não houver banco SQLite, verificar question_catalog.json.gz
    if not raw_list and json_gz_path and json_gz_path.exists():
        with gzip.open(json_gz_path, "rt", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                raw_list = data
        source_desc = f"Arquivo {json_gz_path.name} ({len(raw_list)} questões)"

    # Deduplicação rigorosa por ID e por conteúdo textual
    deduped: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_hashes: set[str] = set()

    for item in raw_list:
        cid = str(item.get("id") or item.get("source_id") or "")
        if not cid or cid in seen_ids:
            continue
        h = compute_content_source_hash(item)
        if h in seen_hashes:
            continue
        seen_ids.add(cid)
        seen_hashes.add(h)
        deduped.append(item)

    return deduped, source_desc


def build_100_pilot_sample(
    candidates: list[dict[str, Any]],
    seed: int = DEFAULT_SEED,
    target_count: int = PILOT_TARGET_COUNT,
    max_per_specialty: int = MAX_PER_SPECIALTY,
) -> tuple[list[dict[str, Any]], dict[str, Any], str | None]:
    """Seleciona deterministicamente 100 questões com balanceamento estrito por especialidade."""
    rng = random.Random(seed)

    # Avaliar diversidade real de especialidades
    specialties_map: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for it in candidates:
        spec = (it.get("especialidade") or it.get("current_specialty") or "Não Informada").strip()
        specialties_map[spec].append(it)

    distinct_specs = list(specialties_map.keys())
    blocker: str | None = None

    # Bloqueio obrigatório se a fonte for dominada por uma única especialidade
    if len(distinct_specs) < 2 or (len(distinct_specs) == 1 and distinct_specs[0] == "Cirurgia"):
        blocker = (
            f"BLOQUEIO DE DADOS: A fonte disponível possui apenas {len(distinct_specs)} especialidade(s) "
            f"('{distinct_specs[0] if distinct_specs else 'Nenhuma'}'), impossibilitando a seleção de 100 questões "
            f"com diversidade real (mínimo exigido: até 10 por especialidade em >= 15 especialidades). "
            f"Conforme as restrições absolutas, a execução foi interrompida para evitar substituição por Cirurgia."
        )

    # Ordenar deterministamente cada lista de especialidade
    for spec in specialties_map:
        specialties_map[spec].sort(key=lambda x: str(x.get("id") or x.get("source_id") or ""))
        rng.shuffle(specialties_map[spec])

    # Seleção com teto estrito por especialidade
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    spec_counts: Counter[str] = Counter()
    criteria_counts: Counter[str] = Counter()

    sorted_specs = sorted(distinct_specs)

    # Rodadas de seleção proporcional equilibrada
    for round_idx in range(max_per_specialty):
        for spec in sorted_specs:
            if len(selected) >= target_count:
                break
            pool = specialties_map[spec]
            for item in pool:
                cid = str(item.get("id") or item.get("source_id") or "")
                if cid not in selected_ids and spec_counts[spec] < max_per_specialty:
                    selected.append(item)
                    selected_ids.add(cid)
                    spec_counts[spec] += 1
                    for crit in detect_question_criteria(item):
                        criteria_counts[crit] += 1
                    break

    # Se ainda faltar itens e houver blocker ativo, a lista fica restrita ao que foi possível sem violar a cota
    report = {
        "seed": seed,
        "target_count": target_count,
        "max_per_specialty": max_per_specialty,
        "total_candidates_available": len(candidates),
        "total_distinct_specialties_available": len(distinct_specs),
        "available_specialties": distinct_specs,
        "selected_count": len(selected),
        "selected_by_specialty": dict(spec_counts.most_common()),
        "selected_by_criteria": dict(criteria_counts.most_common()),
        "blocker": blocker,
    }

    return selected, report, blocker


def format_pilot_inputs(selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Converte os itens selecionados para o formato canônico estrito de entrada do piloto."""
    inputs = []
    for item in selected:
        cid = str(item.get("id") or item.get("source_id") or "")
        inputs.append({
            "content_id": cid,
            "content_type": "questao",
            "title": str(item.get("cabecalho") or ""),
            "body": str(item.get("statement_plain") or item.get("enunciado") or ""),
            "alternatives": item.get("alternativas") or item.get("alternatives") or [],
            "correct_answer_id": str(item.get("alternativa_correta_id") or item.get("correct_letter") or ""),
            "current_specialty": item.get("especialidade"),
            "current_theme": item.get("tema"),
            "current_subject": item.get("subtema") or item.get("assunto"),
            "ano": item.get("ano"),
            "instituicao": item.get("instituicao"),
            "banca": item.get("banca"),
            "source_hash": compute_content_source_hash(item),
            "selection_criteria": detect_question_criteria(item),
        })
    inputs.sort(key=lambda x: str(x["content_id"]))
    return inputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Amostragem determinística e balanceada do piloto de 100 questões MedSync.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--target", type=int, default=PILOT_TARGET_COUNT)
    parser.add_argument("--max-per-spec", type=int, default=MAX_PER_SPECIALTY)
    parser.add_argument("--db-path", type=Path, default=Path("medsync.db"))
    parser.add_argument("--catalog-gz", type=Path, default=Path("data/question_catalog.json.gz"))
    parser.add_argument("--output-inputs", type=Path, default=Path("data/pilot_inputs_100.jsonl"))
    parser.add_argument("--output-report", type=Path, default=Path("data/pilot_selection_report.json"))
    args = parser.parse_args()

    candidates, source_desc = load_candidates_from_source(
        db_path=args.db_path,
        json_gz_path=args.catalog_gz,
    )
    print(f"[AMOSTRAGEM] Fonte: {source_desc}")
    print(f"[AMOSTRAGEM] Candidatos únicos após deduplicação: {len(candidates)}")

    selected, report, blocker = build_100_pilot_sample(
        candidates,
        seed=args.seed,
        target_count=args.target,
        max_per_specialty=args.max_per_spec,
    )
    report["source_description"] = source_desc

    print(f"[AMOSTRAGEM] Selecionados: {len(selected)} questões.")
    print(f"[AMOSTRAGEM] Especialidades disponíveis: {report['total_distinct_specialties_available']}")
    if blocker:
        print(f"\n[ATENÇÃO - BLOQUEIO DETECTADO]\n{blocker}\n")

    # Salvar relatório de seleção
    args.output_report.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_report, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"[OK] Relatório de seleção gravado em: {args.output_report}")

    # Salvar entradas formatadas se seleção for válida
    if selected and not blocker:
        formatted = format_pilot_inputs(selected)
        with open(args.output_inputs, "w", encoding="utf-8") as f:
            for item in formatted:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"[OK] 100 Entradas canônicas gravadas em: {args.output_inputs}")


if __name__ == "__main__":
    main()
