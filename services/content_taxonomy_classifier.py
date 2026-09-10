"""Classificação semântica compartilhada por questões, casos e desafios.

O módulo não publica taxonomia nem altera campos de origem. Ele produz
propostas versionadas, verificáveis e adequadas à montagem futura de trilhas.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

AUTO_VERIFY_THRESHOLD = 0.90
MAX_BATCH_ITEMS = 20
MAX_CODE_SEGMENT_LENGTH = 56

ALLOWED_COMPETENCIES = frozenset(
    {
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
    }
)


def normalized_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.strip())
    return re.sub(
        r"\s+",
        " ",
        "".join(char for char in decomposed if not unicodedata.combining(char)),
    ).casefold()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", normalized_text(value)).strip("_")
    if not slug:
        raise ValueError("Não foi possível gerar um identificador canônico.")
    return slug[:MAX_CODE_SEGMENT_LENGTH].rstrip("_")


def taxonomy_codes(
    specialty: str, theme: str, subject: str
) -> tuple[str, str, str]:
    specialty_code = slugify(specialty)
    theme_code = f"{specialty_code}.{slugify(theme)}"
    subject_code = f"{theme_code}.{slugify(subject)}"
    return specialty_code, theme_code, subject_code


class ContentItem(BaseModel):
    content_id: str = Field(min_length=1, max_length=120)
    content_type: Literal["questao", "caso_clinico", "desafio_visual"]
    title: str = Field(default="", max_length=300)
    body: str = Field(min_length=1)
    alternatives: list[dict[str, Any]] = Field(default_factory=list)
    correct_answer_id: str | None = None
    current_specialty: str | None = None
    current_theme: str | None = None
    current_subject: str | None = None
    current_difficulty: str | None = None

    def source_hash(self) -> str:
        encoded = json.dumps(
            self.model_dump(mode="json", exclude_none=True),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def prompt_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude_none=True)


class TaxonomyDecision(BaseModel):
    content_id: str = Field(min_length=1, max_length=120)
    specialty: str = Field(min_length=2, max_length=180)
    theme: str = Field(min_length=2, max_length=180)
    subject: str = Field(min_length=2, max_length=180)
    learning_objectives: list[str] = Field(min_length=1, max_length=3)
    competencies: list[str] = Field(min_length=1, max_length=4)
    clinical_contexts: list[str] = Field(default_factory=list, max_length=4)
    tags: list[str] = Field(default_factory=list, max_length=8)
    difficulty: Literal["basica", "intermediaria", "avancada"]
    confidence: float = Field(ge=0, le=1)
    evidence: list[str] = Field(min_length=1, max_length=5)
    ambiguity_reason: str | None = Field(default=None, max_length=700)

    @field_validator(
        "specialty",
        "theme",
        "subject",
        "learning_objectives",
        "clinical_contexts",
        "tags",
    )
    @classmethod
    def strip_text(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, list):
            return [
                item.strip()
                for item in value
                if isinstance(item, str) and item.strip()
            ]
        return value

    @field_validator("competencies")
    @classmethod
    def validate_competencies(cls, value: list[str]) -> list[str]:
        normalized = [slugify(item) for item in value]
        invalid = set(normalized) - ALLOWED_COMPETENCIES
        if invalid:
            raise ValueError(f"Competências inválidas: {sorted(invalid)}")
        return list(dict.fromkeys(normalized))

    @model_validator(mode="after")
    def validate_hierarchy_depth(self) -> TaxonomyDecision:
        labels = [
            normalized_text(self.specialty),
            normalized_text(self.theme),
            normalized_text(self.subject),
        ]
        if len(set(labels)) != 3:
            raise ValueError(
                "Especialidade, tema e assunto precisam representar níveis distintos."
            )
        return self


class ClassificationBatch(BaseModel):
    items: list[TaxonomyDecision] = Field(min_length=1, max_length=MAX_BATCH_ITEMS)


class VerificationDecision(BaseModel):
    content_id: str = Field(min_length=1, max_length=120)
    agrees: bool
    confidence: float = Field(ge=0, le=1)
    final_decision: TaxonomyDecision
    reason: str = Field(min_length=5, max_length=700)

    @model_validator(mode="after")
    def validate_content_id(self) -> VerificationDecision:
        if self.content_id != self.final_decision.content_id:
            raise ValueError("O verificador retornou IDs internos divergentes.")
        return self


class VerificationBatch(BaseModel):
    items: list[VerificationDecision] = Field(min_length=1, max_length=MAX_BATCH_ITEMS)


@dataclass(frozen=True)
class ClassificationOutcome:
    decision: TaxonomyDecision
    verifier: VerificationDecision
    status: str
    confidence: float
    reason: str | None


def ensure_exact_ids(expected: list[str], received: list[str]) -> None:
    if len(received) != len(set(received)):
        raise ValueError("A resposta contém IDs duplicados.")
    if set(received) != set(expected):
        missing = sorted(set(expected) - set(received))
        unexpected = sorted(set(received) - set(expected))
        raise ValueError(
            f"IDs divergentes. Ausentes={missing}; inesperados={unexpected}"
        )


def resolve_outcome(
    classifier: TaxonomyDecision,
    verifier: VerificationDecision,
    *,
    threshold: float = AUTO_VERIFY_THRESHOLD,
) -> ClassificationOutcome:
    if classifier.content_id != verifier.content_id:
        raise ValueError("Classificador e verificador analisaram conteúdos diferentes.")

    final = verifier.final_decision
    confidence = min(classifier.confidence, verifier.confidence, final.confidence)
    same_hierarchy = taxonomy_codes(
        classifier.specialty, classifier.theme, classifier.subject
    ) == taxonomy_codes(final.specialty, final.theme, final.subject)
    automatically_verified = (
        verifier.agrees and same_hierarchy and confidence >= threshold
    )
    reason = None if automatically_verified else verifier.reason
    if classifier.ambiguity_reason or final.ambiguity_reason:
        automatically_verified = False
        reason = final.ambiguity_reason or classifier.ambiguity_reason or reason

    return ClassificationOutcome(
        decision=final,
        verifier=verifier,
        status="verificada" if automatically_verified else "revisao_necessaria",
        confidence=confidence,
        reason=reason,
    )


CLASSIFIER_SYSTEM_PROMPT = """
Você é o classificador médico editorial da MedSync. Analise o objetivo central
real de cada conteúdo, não apenas palavras isoladas. Produza uma hierarquia útil
para estudo: especialidade (área médica), tema (capítulo clínico) e assunto
(doença, procedimento, exame ou decisão específica). É proibido repetir o mesmo
rótulo em dois níveis. Prefira nomenclatura médica consolidada e reutilizável.

Os campos atuais são apenas pistas e podem estar errados. Em questões, considere
o comando, o enunciado, todas as alternativas e o gabarito validado. O objetivo
de aprendizagem deve descrever o que o aluno precisa saber fazer. Use somente as
competências permitidas: fundamentos, prevencao, diagnostico,
interpretacao_de_exames, tratamento, procedimento, prognostico, seguimento,
urgencia_e_emergencia, seguranca_do_paciente, etica_e_saude_coletiva.

Use confiança alta apenas quando a hierarquia completa estiver inequívoca. Em
conteúdo multidisciplinar, escolha a especialidade do conhecimento decisivo e
registre as demais áreas como etiquetas. Não invente informação clínica.
""".strip()


VERIFIER_SYSTEM_PROMPT = """
Você é o segundo revisor médico independente da MedSync. Compare a proposta com
o conteúdo original e verifique especialmente: objetivo central, especialidade
decisiva, profundidade real do tema e especificidade útil do assunto. Tema e
assunto nunca podem ser sinônimos ou meras repetições. Corrija a decisão quando
necessário e reduza a confiança diante de ambiguidade. Não aceite uma categoria
por concordância superficial com palavras do texto.
""".strip()


class OpenAITaxonomyClassifier:
    """Adaptador síncrono; o orquestrador controla retomada e persistência."""

    def __init__(
        self,
        *,
        api_key: str,
        classifier_model: str,
        verifier_model: str,
        timeout: float = 180,
    ) -> None:
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key, timeout=timeout, max_retries=3)
        self.classifier_model = classifier_model
        self.verifier_model = verifier_model

    def classify(self, contents: list[ContentItem]) -> ClassificationBatch:
        _validate_batch(contents)
        response = self.client.responses.parse(
            model=self.classifier_model,
            input=[
                {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        [item.prompt_payload() for item in contents],
                        ensure_ascii=False,
                    ),
                },
            ],
            text_format=ClassificationBatch,
            max_output_tokens=max(4000, len(contents) * 1100),
        )
        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("O classificador não retornou uma resposta estruturada.")
        ensure_exact_ids(
            [item.content_id for item in contents],
            [item.content_id for item in parsed.items],
        )
        return parsed

    def verify(
        self,
        contents: list[ContentItem],
        classifications: ClassificationBatch,
    ) -> VerificationBatch:
        _validate_batch(contents)
        ensure_exact_ids(
            [item.content_id for item in contents],
            [item.content_id for item in classifications.items],
        )
        payload = {
            "contents": [item.prompt_payload() for item in contents],
            "proposals": [
                item.model_dump(mode="json") for item in classifications.items
            ],
        }
        response = self.client.responses.parse(
            model=self.verifier_model,
            input=[
                {"role": "system", "content": VERIFIER_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            text_format=VerificationBatch,
            max_output_tokens=max(4500, len(contents) * 1250),
        )
        parsed = response.output_parsed
        if parsed is None:
            raise ValueError("O verificador não retornou uma resposta estruturada.")
        ensure_exact_ids(
            [item.content_id for item in contents],
            [item.content_id for item in parsed.items],
        )
        return parsed


def _validate_batch(contents: Iterable[ContentItem]) -> None:
    items = list(contents)
    if not items or len(items) > MAX_BATCH_ITEMS:
        raise ValueError(f"O lote deve conter entre 1 e {MAX_BATCH_ITEMS} itens.")
    ids = [item.content_id for item in items]
    ensure_exact_ids(ids, ids)
