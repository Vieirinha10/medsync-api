"""Compara o contexto legado e o contexto compacto da Synapse em casos reais.

O benchmark é offline: não consome créditos da OpenAI nem depende de segredos.
Ele mede bytes enviados, uma estimativa local de tokens, tamanho do schema de
saída, roteamento de modelos e invariantes do feedback determinístico.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path
from statistics import mean
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from case_catalog import CLINICAL_CASES
from clinical_rubric_catalog import CLINICAL_CASE_EXAM_UPDATES, CLINICAL_RUBRICS
from evaluation import (
    ClinicalNarrative,
    SimulationSubmission,
    SynapseNarrativeEnhancement,
    build_compact_feedback_payload,
    build_rule_based_narrative,
    evaluate_objective,
    select_feedback_model,
    synapse_runtime_config,
)


def _json_bytes(value: Any) -> int:
    return len(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )


def _estimated_tokens(byte_count: int) -> int:
    # Somente indicador comparativo local. A cobrança real vem de response.usage.
    return round(byte_count / 4)


def _case_with_current_exams(
    case: dict[str, Any], rubric: dict[str, Any]
) -> dict[str, Any]:
    current = deepcopy(case)
    if current["id"] in CLINICAL_CASE_EXAM_UPDATES:
        current["exames_disponiveis"] = deepcopy(
            CLINICAL_CASE_EXAM_UPDATES[current["id"]]
        )
    exam_ids = {exam["id"] for exam in current.get("exames_disponiveis", [])}
    rubric_exam_ids = {
        *rubric.get("exames_essenciais", []),
        *rubric.get("exames_opcionais", []),
        *rubric.get("exames_desnecessarios", []),
    }
    current.setdefault("exames_disponiveis", []).extend(
        {
            "id": exam_id,
            "nome": exam_id.replace("_", " ").title(),
            "resultado": "Não informado no catálogo local do benchmark.",
            "correto": exam_id not in rubric.get("exames_desnecessarios", []),
        }
        for exam_id in sorted(rubric_exam_ids - exam_ids)
    )
    return current


def _representative_ids(count: int) -> list[int]:
    available = sorted({case["id"] for case in CLINICAL_CASES} & set(CLINICAL_RUBRICS))
    if count > len(available):
        raise ValueError(f"Há somente {len(available)} casos com rubrica revisada.")
    if count == 1:
        return [available[len(available) // 2]]
    positions = {
        round(index * (len(available) - 1) / (count - 1)) for index in range(count)
    }
    return [available[position] for position in sorted(positions)]


def _submission_for(rubric: dict[str, Any], scenario: str) -> SimulationSubmission:
    essential = rubric.get("exames_essenciais", [])
    optional = rubric.get("exames_opcionais", [])
    unnecessary = rubric.get("exames_desnecessarios", [])
    criteria = rubric["conduta_criterios"]
    safety = rubric.get("criterios_seguranca", [])

    if scenario == "completo":
        selected = [*essential, *optional[:1]]
        hypothesis = rubric["diagnostico_referencia"]
        conduct_terms = [item["termos"][0] for item in criteria]
        conduct_terms.extend(item["termos"][0] for item in safety)
    elif scenario == "parcial":
        essential_count = max(1, len(essential) // 2) if essential else 0
        selected = [*essential[:essential_count], *unnecessary[:1]]
        partial = rubric.get("diagnostico_parcial", [])
        hypothesis = partial[0] if partial else rubric["diagnostico_referencia"]
        conduct_terms = [
            item["termos"][0] for item in criteria[: max(1, len(criteria) // 2)]
        ]
    else:
        selected = unnecessary[:2] or optional[:1]
        hypothesis = "Hipótese alternativa inespecífica"
        conduct_terms = [
            "Alta sem necessidade de internação, estabilização ou avaliação urgente."
        ]

    rationales = {
        exam_id: rubric.get("justificativa_exames", {}).get(
            exam_id, "Avaliar se o resultado modifica a hipótese ou a conduta."
        )
        for exam_id in selected
    }
    return SimulationSubmission(
        exames_solicitados=list(dict.fromkeys(selected)),
        justificativas_exames=rationales,
        hipotese_diagnostica=hypothesis,
        conduta_proposta="; ".join(conduct_terms),
    )


def _legacy_payload(
    case: dict[str, Any],
    submission: SimulationSubmission,
    score: Any,
    exams: Any,
    rubric: dict[str, Any],
) -> dict[str, Any]:
    return {
        "caso": {
            "titulo": case["titulo"],
            "historia_clinica": case["historia_clinica"],
            "exame_fisico": case["exame_fisico"],
        },
        "respostas_do_estudante": submission.model_dump(),
        "pontuacao_objetiva": score.model_dump(),
        "avaliacao_de_exames": exams.model_dump(),
        "gabarito_clinico": rubric,
    }


def run_benchmark(count: int) -> dict[str, Any]:
    cases_by_id = {case["id"]: case for case in CLINICAL_CASES}
    scenarios = ("completo", "parcial", "risco")
    details = []
    routes = Counter()
    invariant_failures = []

    for index, case_id in enumerate(_representative_ids(count)):
        rubric = CLINICAL_RUBRICS[case_id]
        case = _case_with_current_exams(cases_by_id[case_id], rubric)
        scenario = scenarios[index % len(scenarios)]
        submission = _submission_for(rubric, scenario)
        score, exams, context = evaluate_objective(case, submission, rubric)
        fallback = build_rule_based_narrative(submission, score, exams, context)
        legacy = _legacy_payload(case, submission, score, exams, rubric)
        compact = build_compact_feedback_payload(
            case, submission, score, exams, context
        )
        legacy_bytes = _json_bytes(legacy)
        compact_bytes = _json_bytes(compact)
        route = select_feedback_model(case, score, context)
        routes[route] += 1

        invariants = {
            "pontuacao_preservada": compact["avaliacao_objetiva"]["pontuacao"]
            == score.model_dump(),
            "seguranca_deterministica": bool(fallback.feedback_seguranca),
            "impacto_deterministico": bool(fallback.desfecho_clinico),
            "sem_fontes_repetidas": "fontes_clinicas"
            not in json.dumps(compact, ensure_ascii=False),
        }
        if not all(invariants.values()):
            invariant_failures.append({"caso_id": case_id, **invariants})

        details.append(
            {
                "caso_id": case_id,
                "especialidade": case["especialidade"],
                "dificuldade": case["nivel_dificuldade"],
                "cenario": scenario,
                "modelo": route,
                "bytes_legado": legacy_bytes,
                "bytes_compacto": compact_bytes,
                "reducao_percentual": round(
                    (1 - compact_bytes / legacy_bytes) * 100, 1
                ),
            }
        )

    legacy_total = sum(item["bytes_legado"] for item in details)
    compact_total = sum(item["bytes_compacto"] for item in details)
    legacy_schema = _json_bytes(ClinicalNarrative.model_json_schema())
    compact_schema = _json_bytes(SynapseNarrativeEnhancement.model_json_schema())
    return {
        "amostra": count,
        "configuracao": synapse_runtime_config(),
        "cenarios": dict(Counter(item["cenario"] for item in details)),
        "contexto_entrada": {
            "bytes_legado": legacy_total,
            "bytes_compacto": compact_total,
            "estimativa_tokens_legado": _estimated_tokens(legacy_total),
            "estimativa_tokens_compacto": _estimated_tokens(compact_total),
            "reducao_percentual": round((1 - compact_total / legacy_total) * 100, 1),
            "reducao_media_por_caso": round(
                mean(item["reducao_percentual"] for item in details), 1
            ),
        },
        "schema_saida": {
            "bytes_legado": legacy_schema,
            "bytes_compacto": compact_schema,
            "reducao_percentual": round((1 - compact_schema / legacy_schema) * 100, 1),
        },
        "roteamento": dict(routes),
        "invariantes": {
            "casos_aprovados": count - len(invariant_failures),
            "falhas": invariant_failures,
        },
        "casos": details,
        "observacao": (
            "A estimativa local de tokens serve apenas para comparação. "
            "Tokens e custo faturáveis devem ser lidos de response.usage."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=int, default=25, choices=range(20, 31))
    args = parser.parse_args()
    print(json.dumps(run_benchmark(args.cases), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
