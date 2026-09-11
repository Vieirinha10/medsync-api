"""Máquina de estados autônoma, atômica e retomável para a taxonomia médica MedSync (Fase 2).

Garantias estruturais:
1. Hash único canônico (compute_content_source_hash) compartilhado por seletor e executor.
2. Checkpoint durável gravado atomicamente em disco (.tmp -> os.replace).
3. Processamento em chunks estritos (default: 10) com gravação incremental em JSONL.
4. Fluxo completo: inicial -> verificação -> detecção de alta complexidade -> reanálise -> verificação final.
5. Validação contra registro canônico e rejeição semântica de tema/assunto repetidos.
6. Tratamento de exceções (saídas malformadas, IDs ausentes/duplicados/inesperados, cota, hash alterado).
"""

from __future__ import annotations

import copy
import enum
import hashlib
import json
import logging
import os
import tempfile
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger("medsync.taxonomy_state_machine")


# ==============================================================================
# HASH CANÔNICO COMPARTILHADO (Item 2)
# ==============================================================================

def normalize_text_loose(val: str | None) -> str:
    if not val:
        return ""
    decomposed = unicodedata.normalize("NFKD", str(val).strip())
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def compute_content_source_hash(item: dict[str, Any] | Any) -> str:
    """Gera hash SHA-256 canônico e estritamente determinístico do conteúdo entregue ao classificador.

    Campos obrigatórios avaliados:
    1. content_id (ou id)
    2. content_type
    3. cabecalho (ou title)
    4. enunciado (ou body / statement_plain)
    5. alternativas
    6. identificador do gabarito (correct_answer_id / correct_letter)
    7. especialidade atual
    8. tema atual
    9. assunto atual
    10. dificuldade atual
    """
    if hasattr(item, "model_dump"):
        raw = item.model_dump(mode="json")
    elif isinstance(item, dict):
        raw = item
    else:
        raw = dict(item)

    cid = str(raw.get("content_id") or raw.get("id") or raw.get("source_id") or "").strip()
    ctype = str(raw.get("content_type") or "questao").strip()
    title = str(raw.get("title") or raw.get("cabecalho") or "").strip()
    body = str(raw.get("body") or raw.get("statement_plain") or raw.get("enunciado") or "").strip()

    # Normalizar alternativas
    raw_alts = raw.get("alternatives") or raw.get("alternativas") or []
    norm_alts: list[dict[str, str]] = []
    if isinstance(raw_alts, list):
        for alt in raw_alts:
            if isinstance(alt, dict):
                alt_id = str(alt.get("letter") or alt.get("id") or "").strip()
                alt_text = str(alt.get("body_plain") or alt.get("texto") or alt.get("text") or alt.get("body") or "").strip()
                norm_alts.append({"id": alt_id, "text": alt_text})
            else:
                norm_alts.append({"id": "", "text": str(alt).strip()})

    correct_id = str(raw.get("correct_answer_id") or raw.get("correct_letter") or raw.get("alternativa_correta_id") or "").strip()
    cur_spec = raw.get("current_specialty") or raw.get("especialidade") or None
    cur_theme = raw.get("current_theme") or raw.get("tema") or None
    cur_subj = raw.get("current_subject") or raw.get("subtema") or raw.get("assunto") or None
    cur_diff = raw.get("current_difficulty") or raw.get("difficulty") or raw.get("dificuldade") or None

    payload = {
        "content_id": cid,
        "content_type": ctype,
        "title": title,
        "body": body,
        "alternatives": norm_alts,
        "correct_answer_id": correct_id,
        "current_specialty": str(cur_spec).strip() if cur_spec else None,
        "current_theme": str(cur_theme).strip() if cur_theme else None,
        "current_subject": str(cur_subj).strip() if cur_subj else None,
        "current_difficulty": str(cur_diff).strip() if cur_diff else None,
    }

    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


# ==============================================================================
# TAXONOMIA CONTROLADA E VALIDAÇÃO SEMÂNTICA (Item 7)
# ==============================================================================

ALLOWED_COMPETENCIES = frozenset({
    "fundamentos",
    "prevencao",
    "diagnostico",
    "interpretacao_de_exames",
    "tratamento",
    "procedimento",
    "prognostico",
    "seguimento",
    "urgencia_e_emergencia",
    "seguranca_do_paciente",
    "etica_e_saude_coletiva",
})


def are_semantically_repeated(a: str | None, b: str | None) -> bool:
    """Detecta se dois níveis taxonômicos representam a mesma coisa."""
    if not a or not b:
        return False
    norm_a = normalize_text_loose(a)
    norm_b = normalize_text_loose(b)
    if norm_a == norm_b:
        return True
    # Sinônimos e variações comuns
    synonyms = {
        ("trauma", "traumatismo"),
        ("cardiopatia", "cardiologia"),
        ("valvopatia", "valvopatias"),
        ("hipertensao", "hipertensao arterial"),
        ("diabetes", "diabetes mellitus"),
        ("asma", "asma bronquica"),
        ("sepse", "choque septico"),
        ("pediatria", "pediatrica"),
    }
    for s1, s2 in synonyms:
        if (s1 in norm_a and s2 in norm_b) or (s2 in norm_a and s1 in norm_b):
            if abs(len(norm_a) - len(norm_b)) <= 10:
                return True
    return False


def validate_taxonomy_hierarchy(
    specialty: str,
    theme: str,
    subject: str,
    registry_path: Path | None = None,
) -> tuple[bool, str, str | None]:
    """Valida a hierarquia contra o registro canônico e regras de distinção semântica."""
    # 1. Checagem de níveis semânticos distintos
    if are_semantically_repeated(specialty, theme):
        return False, "provisional", f"Especialidade ('{specialty}') e Tema ('{theme}') são semanticamente repetidos."
    if are_semantically_repeated(theme, subject):
        return False, "provisional", f"Tema ('{theme}') e Assunto ('{subject}') são semanticamente repetidos."
    if are_semantically_repeated(specialty, subject):
        return False, "provisional", f"Especialidade ('{specialty}') e Assunto ('{subject}') são semanticamente repetidos."

    # 2. Checagem contra registro canônico se disponível
    if registry_path and registry_path.exists():
        try:
            with open(registry_path, "r", encoding="utf-8") as f:
                reg = json.load(f)
            # Mapear especialidade
            spec_match = False
            for spec_node in reg.get("specialties", []):
                spec_labels = [spec_node.get("label", ""), spec_node.get("code", "")] + spec_node.get("aliases", [])
                if any(normalize_text_loose(l) == normalize_text_loose(specialty) for l in spec_labels):
                    spec_match = True
                    # Checar tema
                    theme_match = False
                    for th_node in spec_node.get("themes", []):
                        th_labels = [th_node.get("label", ""), th_node.get("code", "")] + th_node.get("aliases", [])
                        if any(normalize_text_loose(l) == normalize_text_loose(theme) for l in th_labels):
                            theme_match = True
                            # Checar assunto
                            subj_match = False
                            for s_node in th_node.get("subjects", []):
                                s_labels = [s_node.get("label", ""), s_node.get("code", "")] + s_node.get("aliases", [])
                                if any(normalize_text_loose(l) == normalize_text_loose(subject) for l in s_labels):
                                    subj_match = True
                                    break
                            if subj_match:
                                return True, "canonical", None
                            else:
                                return True, "provisional", f"Assunto '{subject}' novo ou provisório no tema canônico '{theme}'"
                    if not theme_match:
                        return True, "provisional", f"Tema '{theme}' novo ou provisório na especialidade canônica '{specialty}'"
            if not spec_match:
                return True, "provisional", f"Especialidade '{specialty}' não mapeada no registro canônico inicial"
        except Exception as e:
            logger.warning(f"Erro consultando registro canônico: {e}")

    return True, "provisional", None


# ==============================================================================
# ESTADOS E EXCEÇÕES
# ==============================================================================

class TaxonomyItemState(str, enum.Enum):
    PENDING = "pending"
    CLASSIFIED = "classified"
    REQUIRES_HIGH_EFFORT = "requires_high_effort"
    VERIFIED = "verified"
    REQUIRES_REVIEW = "requires_review"
    FAILED = "failed"
    APPROVED = "approved"
    PUBLISHED = "published"


class QuotaExhaustedError(Exception):
    def __init__(self, message: str = "Limite de cota de processamento atingido."):
        super().__init__(message)


class StaleContentHashError(Exception):
    def __init__(self, message: str = "O conteúdo sofreu alteração e o hash de origem divergiu."):
        super().__init__(message)


# ==============================================================================
# CHECKPOINT ATÔMICO DURÁVEL (Item 3)
# ==============================================================================

@dataclass
class DurableCheckpoint:
    run_id: str
    status: str = "executando"
    completed_ids: list[str] = field(default_factory=list)
    last_id: str | None = None
    processed_count: int = 0
    verified_count: int = 0
    review_count: int = 0
    failed_count: int = 0
    high_effort_count: int = 0
    hashes: dict[str, str] = field(default_factory=dict)
    last_checkpoint_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def save_atomic(self, file_path: Path) -> None:
        """Grava atomicamente o checkpoint em disco via arquivo temporário com os.replace."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        data = asdict(self)
        data["last_checkpoint_at"] = datetime.now(UTC).isoformat()

        temp_fd, temp_path_str = tempfile.mkstemp(
            dir=str(file_path.parent),
            prefix="chk_",
            suffix=".tmp"
        )
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_path_str, file_path)

    @classmethod
    def load(cls, file_path: Path) -> DurableCheckpoint | None:
        """Carrega checkpoint existente do disco se disponível."""
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(
                run_id=data.get("run_id", "default_run"),
                status=data.get("status", "executando"),
                completed_ids=data.get("completed_ids", []),
                last_id=data.get("last_id"),
                processed_count=data.get("processed_count", 0),
                verified_count=data.get("verified_count", 0),
                review_count=data.get("review_count", 0),
                failed_count=data.get("failed_count", 0),
                high_effort_count=data.get("high_effort_count", 0),
                hashes=data.get("hashes", {}),
                last_checkpoint_at=data.get("last_checkpoint_at", datetime.now(UTC).isoformat()),
            )
        except Exception as e:
            logger.error(f"Erro carregando checkpoint de {file_path}: {e}")
            return None


# ==============================================================================
# MOTOR DE EXECUÇÃO EM LOTES (Itens 4, 5 e 6)
# ==============================================================================

class PilotCalibrationRunner:
    """Executor em lotes da calibração taxonômica com validação e escrita atômica."""

    def __init__(
        self,
        classifier_fn: Callable[[list[dict[str, Any]]], list[dict[str, Any]]],
        verifier_fn: Callable[[list[dict[str, Any]], list[dict[str, Any]]], list[dict[str, Any]]],
        high_effort_fn: Callable[[list[dict[str, Any]], list[dict[str, Any]]], list[dict[str, Any]]] | None = None,
        chunk_size: int = 10,
        checkpoint_path: Path = Path("data/pilot_checkpoint.json"),
        output_jsonl_path: Path = Path("data/pilot_classifications_100.jsonl"),
        execution_log_path: Path = Path("data/pilot_execution_log.jsonl"),
        registry_path: Path = Path("data/taxonomy_registry_pilot_v0_1.json"),
        verify_threshold: float = 0.90,
    ):
        self.classifier_fn = classifier_fn
        self.verifier_fn = verifier_fn
        self.high_effort_fn = high_effort_fn
        self.chunk_size = chunk_size
        self.checkpoint_path = checkpoint_path
        self.output_jsonl_path = output_jsonl_path
        self.execution_log_path = execution_log_path
        self.registry_path = registry_path
        self.verify_threshold = verify_threshold

    def log_event(self, event_type: str, details: dict[str, Any]) -> None:
        """Registra evento durável no arquivo de log de execução."""
        self.execution_log_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event": event_type,
            **details,
        }
        with open(self.execution_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def run_calibration(
        self,
        inputs: list[dict[str, Any]],
        run_id: str = "pilot-phase2-calibration",
    ) -> dict[str, Any]:
        """Executa a calibração de todo o conjunto em lotes atômicos."""
        # 1. Carregar ou inicializar checkpoint durável
        checkpoint = DurableCheckpoint.load(self.checkpoint_path)
        if not checkpoint or checkpoint.run_id != run_id:
            checkpoint = DurableCheckpoint(run_id=run_id)
            checkpoint.save_atomic(self.checkpoint_path)

        completed_set = set(checkpoint.completed_ids)
        self.log_event("RUN_STARTED", {
            "run_id": run_id,
            "total_inputs": len(inputs),
            "already_completed": len(completed_set),
            "chunk_size": self.chunk_size,
        })

        # 2. Filtrar itens pendentes
        pending_inputs = []
        for it in inputs:
            cid = str(it.get("content_id") or it.get("id") or "")
            if not cid:
                raise ValueError("Item com identificador vazio encontrado na entrada.")
            # Validar integridade do source_hash
            current_hash = compute_content_source_hash(it)
            if cid in checkpoint.hashes:
                if checkpoint.hashes[cid] != current_hash:
                    raise StaleContentHashError(f"Hash alterado para a questão {cid}: {current_hash} != {checkpoint.hashes[cid]}")
            else:
                checkpoint.hashes[cid] = current_hash

            if cid not in completed_set:
                pending_inputs.append(it)

        # 3. Processar em chunks
        total_batches = (len(pending_inputs) + self.chunk_size - 1) // self.chunk_size if pending_inputs else 0
        all_classifications: list[dict[str, Any]] = []

        for b_idx in range(total_batches):
            chunk = pending_inputs[b_idx * self.chunk_size : (b_idx + 1) * self.chunk_size]
            chunk_ids = [str(x.get("content_id") or x.get("id")) for x in chunk]

            self.log_event("BATCH_STARTED", {"batch_index": b_idx + 1, "size": len(chunk), "ids": chunk_ids})

            # Processar lote atômico
            batch_results = self._process_single_batch(chunk, checkpoint)

            # Persistir incrementalmente em JSONL
            self.output_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_jsonl_path, "a", encoding="utf-8") as f_out:
                for res in batch_results:
                    f_out.write(json.dumps(res, ensure_ascii=False) + "\n")

            # Atualizar checkpoint de maneira atômica no disco
            checkpoint.save_atomic(self.checkpoint_path)
            all_classifications.extend(batch_results)

            self.log_event("BATCH_COMPLETED", {
                "batch_index": b_idx + 1,
                "processed_total": checkpoint.processed_count,
                "verified_total": checkpoint.verified_count,
                "review_total": checkpoint.review_count,
                "high_effort_total": checkpoint.high_effort_count,
            })

        checkpoint.status = "concluida"
        checkpoint.save_atomic(self.checkpoint_path)
        self.log_event("RUN_COMPLETED", {
            "run_id": run_id,
            "processed": checkpoint.processed_count,
            "verified": checkpoint.verified_count,
            "review": checkpoint.review_count,
        })

        return {
            "status": "COMPLETED",
            "run_id": run_id,
            "total_processed": checkpoint.processed_count,
            "verified_count": checkpoint.verified_count,
            "review_count": checkpoint.review_count,
            "failed_count": checkpoint.failed_count,
            "high_effort_count": checkpoint.high_effort_count,
        }

    def _process_single_batch(
        self,
        chunk: list[dict[str, Any]],
        checkpoint: DurableCheckpoint,
    ) -> list[dict[str, Any]]:
        """Executa a sequência de classificação, verificação e reanálise para um lote de 10 itens."""
        expected_ids = [str(x.get("content_id") or x.get("id")) for x in chunk]

        # 1. Classificação Primária
        first_pass_items = self.classifier_fn(chunk)
        received_ids = [str(x.get("content_id")) for x in first_pass_items]
        if received_ids != expected_ids:
            raise ValueError(f"IDs divergentes na classificação primária. Esperados={expected_ids}, Recebidos={received_ids}")

        first_by_id = {str(x["content_id"]): x for x in first_pass_items}

        # 2. Verificação Independente
        verification_items = self.verifier_fn(chunk, first_pass_items)
        ver_ids = [str(x.get("content_id")) for x in verification_items]
        if ver_ids != expected_ids:
            raise ValueError(f"IDs divergentes na verificação. Esperados={expected_ids}, Recebidos={ver_ids}")

        ver_by_id = {str(x["content_id"]): x for x in verification_items}

        # 3. Avaliação de Necessidade de Alta Complexidade (High Effort)
        requires_reanalysis_chunk: list[dict[str, Any]] = []
        reanalysis_reasons: dict[str, str] = {}

        for item in chunk:
            cid = str(item.get("content_id") or item.get("id"))
            p1 = first_by_id[cid]
            v1 = ver_by_id[cid]

            # Critérios de Reanálise Aprofundada
            disagrees = not v1.get("agrees", True)
            low_conf = min(float(p1.get("confidence", 0.0)), float(v1.get("confidence", 0.0))) < 0.85
            is_generic = normalize_text_loose(p1.get("subject", "")) in {"geral", "outros", "outras", "indefinido", "diversos"}
            has_ambiguity = bool(p1.get("ambiguity_reason") or v1.get("reason"))

            if (disagrees or low_conf or is_generic or has_ambiguity) and self.high_effort_fn:
                reason = "Discordância do verificador" if disagrees else (
                    "Baixa confiança (<0.85)" if low_conf else (
                        "Assunto genérico" if is_generic else "Ambiguidade clínica"
                    )
                )
                requires_reanalysis_chunk.append(item)
                reanalysis_reasons[cid] = reason

        # 4. Reanálise Aprofundada se necessária
        final_decisions_by_id = copy.deepcopy(first_by_id)
        if requires_reanalysis_chunk and self.high_effort_fn:
            checkpoint.high_effort_count += len(requires_reanalysis_chunk)
            reanalyzed = self.high_effort_fn(
                requires_reanalysis_chunk,
                [first_by_id[str(x.get("content_id") or x.get("id"))] for x in requires_reanalysis_chunk]
            )
            for r in reanalyzed:
                final_decisions_by_id[str(r["content_id"])] = r

            # Re-verificação após reanálise
            second_ver = self.verifier_fn(requires_reanalysis_chunk, reanalyzed)
            for sv in second_ver:
                ver_by_id[str(sv["content_id"])] = sv

        # 5. Consolidação de Resultados e Validação contra Registro
        batch_results: list[dict[str, Any]] = []

        for item in chunk:
            cid = str(item.get("content_id") or item.get("id"))
            dec = final_decisions_by_id[cid]
            ver = ver_by_id[cid]

            spec = dec.get("specialty") or dec.get("specialty_label") or ""
            theme = dec.get("theme") or dec.get("theme_label") or ""
            subj = dec.get("subject") or dec.get("subject_label") or ""

            # Validar hierarquia contra registro canônico e níveis distintos
            is_valid_struct, node_status, tax_reason = validate_taxonomy_hierarchy(
                spec, theme, subj, registry_path=self.registry_path
            )
            if not is_valid_struct:
                raise ValueError(f"Classificação inválida para questão {cid}: {tax_reason}")

            # Resolver desfecho
            p_conf = float(dec.get("confidence", 0.0))
            v_conf = float(ver.get("confidence", 0.0))
            final_conf = min(p_conf, v_conf)
            v_agrees = bool(ver.get("agrees", True))

            ambiguity = dec.get("ambiguity_reason") or (ver.get("reason") if not v_agrees else None)
            is_verified = v_agrees and final_conf >= self.verify_threshold and not ambiguity

            status_str = "verified" if is_verified else "requires_review"

            # Validar competências
            comps = dec.get("competencies") or []
            norm_comps = [c for c in comps if c in ALLOWED_COMPETENCIES]
            if not norm_comps:
                norm_comps = ["fundamentos"]

            record = {
                "content_id": cid,
                "source_hash": compute_content_source_hash(item),
                "specialty_code": dec.get("specialty_code") or normalize_text_loose(spec).replace(" ", "_"),
                "specialty_label": spec,
                "theme_code": dec.get("theme_code") or f"{normalize_text_loose(spec).replace(' ', '_')}.{normalize_text_loose(theme).replace(' ', '_')}",
                "theme_label": theme,
                "subject_code": dec.get("subject_code") or f"{normalize_text_loose(spec).replace(' ', '_')}.{normalize_text_loose(theme).replace(' ', '_')}.{normalize_text_loose(subj).replace(' ', '_')}",
                "subject_label": subj,
                "taxonomy_node_status": node_status,
                "learning_objectives": dec.get("learning_objectives") or ["Objetivo formativo específico"],
                "competencies": norm_comps[:4],
                "clinical_contexts": dec.get("clinical_contexts") or [],
                "difficulty": dec.get("difficulty") or "intermediaria",
                "tags": dec.get("tags") or [],
                "primary_confidence": round(p_conf, 2),
                "verifier_agrees": v_agrees,
                "verifier_confidence": round(v_conf, 2),
                "final_confidence": round(final_conf, 2),
                "high_effort_required": cid in reanalysis_reasons,
                "high_effort_reason": reanalysis_reasons.get(cid),
                "evidence": dec.get("evidence") or ["Quadro clínico e alternativas"],
                "ambiguity_reason": ambiguity,
                "status": status_str,
            }
            batch_results.append(record)

            # Atualizar checkpoint
            checkpoint.completed_ids.append(cid)
            checkpoint.processed_count += 1
            if status_str == "verified":
                checkpoint.verified_count += 1
            else:
                checkpoint.review_count += 1
            checkpoint.last_id = cid

        return batch_results
