"""Script de orquestração e execução da calibração taxonômica (Fase 2).

Gera os artefatos de auditoria:
- data/pilot_classifications_100.jsonl
- data/pilot_checkpoint.json
- data/pilot_execution_log.jsonl
- data/pilot_metrics.json
- data/pilot_review_sheet.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.taxonomy_state_machine import (
    DurableCheckpoint,
    PilotCalibrationRunner,
    compute_content_source_hash,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_pilot_calibration")


def generate_review_sheet(
    inputs: list[dict[str, Any]],
    classifications: list[dict[str, Any]],
    output_csv_path: Path,
) -> None:
    """Gera a planilha CSV de auditoria humana detalhada."""
    input_by_id = {str(x.get("content_id") or x.get("id")): x for x in inputs}
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "content_id",
        "enunciado_resumido",
        "especialidade_antiga",
        "especialidade_nova",
        "tema_antigo",
        "tema_novo",
        "assunto_antigo",
        "assunto_novo",
        "objetivo_principal",
        "confianca",
        "concordancia_verificador",
        "uso_reanalise",
        "status",
        "motivo_revisao",
    ]

    with open(output_csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for res in classifications:
            cid = str(res["content_id"])
            orig = input_by_id.get(cid, {})
            body = orig.get("body") or orig.get("statement_plain") or orig.get("enunciado") or ""
            resumo = body[:120].replace("\n", " ").strip() + ("..." if len(body) > 120 else "")

            writer.writerow({
                "content_id": cid,
                "enunciado_resumido": resumo,
                "especialidade_antiga": orig.get("current_specialty") or orig.get("especialidade") or "Indefinida",
                "especialidade_nova": res.get("specialty_label"),
                "tema_antigo": orig.get("current_theme") or orig.get("tema") or "Indefinido",
                "tema_novo": res.get("theme_label"),
                "assunto_antigo": orig.get("current_subject") or orig.get("subtema") or orig.get("assunto") or "Indefinido",
                "assunto_novo": res.get("subject_label"),
                "objetivo_principal": (res.get("learning_objectives") or [""])[0],
                "confianca": f"{float(res.get('final_confidence', 0.0)):.2f}",
                "concordancia_verificador": "Sim" if res.get("verifier_agrees") else "Não",
                "uso_reanalise": "Sim" if res.get("high_effort_required") else "Não",
                "status": res.get("status"),
                "motivo_revisao": res.get("ambiguity_reason") or "",
            })


def generate_metrics_report(
    classifications: list[dict[str, Any]],
    checkpoint: DurableCheckpoint,
    output_metrics_path: Path,
) -> dict[str, Any]:
    """Gera arquivo JSON com métricas consolidadas de calibração."""
    canonical_count = sum(1 for x in classifications if x.get("taxonomy_node_status") == "canonical")
    provisional_count = sum(1 for x in classifications if x.get("taxonomy_node_status") == "provisional")
    verified_count = sum(1 for x in classifications if x.get("status") == "verified")
    review_count = sum(1 for x in classifications if x.get("status") == "requires_review")
    high_effort_count = sum(1 for x in classifications if x.get("high_effort_required"))

    specs = {}
    for x in classifications:
        s = x.get("specialty_label") or "Outros"
        specs[s] = specs.get(s, 0) + 1

    metrics = {
        "generated_at": datetime.now(UTC).isoformat(),
        "total_classified": len(classifications),
        "verified_count": verified_count,
        "requires_review_count": review_count,
        "high_effort_reanalyses_count": high_effort_count,
        "canonical_nodes_count": canonical_count,
        "provisional_nodes_count": provisional_count,
        "specialty_distribution": specs,
        "checkpoint_status": checkpoint.status,
        "run_id": checkpoint.run_id,
    }

    output_metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    return metrics
