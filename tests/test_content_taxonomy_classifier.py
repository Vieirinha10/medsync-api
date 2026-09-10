import pytest
from pydantic import ValidationError

from services.content_taxonomy_classifier import (
    ContentItem,
    TaxonomyDecision,
    VerificationDecision,
    ensure_exact_ids,
    resolve_outcome,
    taxonomy_codes,
)


def decision(**overrides) -> TaxonomyDecision:
    payload = {
        "content_id": "42",
        "specialty": "Cardiologia",
        "theme": "Valvopatias",
        "subject": "Estenose aórtica",
        "learning_objectives": ["Reconhecer critérios de gravidade"],
        "competencies": ["interpretação de exames", "diagnóstico"],
        "clinical_contexts": ["Ambulatório"],
        "tags": ["Ecocardiografia"],
        "difficulty": "intermediaria",
        "confidence": 0.96,
        "evidence": ["Área valvar aórtica reduzida"],
        "ambiguity_reason": None,
    }
    payload.update(overrides)
    return TaxonomyDecision.model_validate(payload)


def verification(first: TaxonomyDecision, **overrides) -> VerificationDecision:
    payload = {
        "content_id": first.content_id,
        "agrees": True,
        "confidence": 0.94,
        "final_decision": first.model_dump(),
        "reason": "A hierarquia representa o objetivo central da questão.",
    }
    payload.update(overrides)
    return VerificationDecision.model_validate(payload)


def test_taxonomy_codes_are_stable_and_hierarchical():
    assert taxonomy_codes("Cardiologia", "Valvopatias", "Estenose aórtica") == (
        "cardiologia",
        "cardiologia.valvopatias",
        "cardiologia.valvopatias.estenose_aortica",
    )


def test_taxonomy_codes_fit_database_columns_even_with_long_labels():
    codes = taxonomy_codes("A" * 300, "B" * 300, "C" * 300)
    assert all(len(code) <= 180 for code in codes)


def test_repeated_theme_and_subject_are_rejected():
    with pytest.raises(ValidationError, match="níveis distintos"):
        decision(subject="Valvopatias")


def test_unknown_competency_is_rejected():
    with pytest.raises(ValidationError, match="Competências inválidas"):
        decision(competencies=["decoracao"])


def test_high_confidence_independent_agreement_is_verified():
    first = decision()
    outcome = resolve_outcome(first, verification(first))
    assert outcome.status == "verificada"
    assert outcome.confidence == 0.94
    assert outcome.reason is None


def test_disagreement_enters_review_queue_even_with_high_confidence():
    first = decision()
    corrected = decision(subject="Insuficiência aórtica", confidence=0.97)
    second = verification(
        corrected,
        agrees=False,
        confidence=0.95,
        reason="O conteúdo descreve regurgitação, não obstrução valvar.",
    )
    outcome = resolve_outcome(first, second)
    assert outcome.status == "revisao_necessaria"
    assert outcome.decision.subject == "Insuficiência aórtica"


def test_ambiguity_never_receives_automatic_approval():
    first = decision(ambiguity_reason="Duas alternativas alteram o objetivo central.")
    outcome = resolve_outcome(first, verification(first))
    assert outcome.status == "revisao_necessaria"


def test_source_hash_changes_when_content_changes():
    first = ContentItem(content_id="1", content_type="questao", body="Texto A")
    second = ContentItem(content_id="1", content_type="questao", body="Texto B")
    assert first.source_hash() != second.source_hash()


def test_batch_ids_must_be_complete_and_unique():
    with pytest.raises(ValueError, match="duplicados"):
        ensure_exact_ids(["1", "2"], ["1", "1"])
    with pytest.raises(ValueError, match="Ausentes"):
        ensure_exact_ids(["1", "2"], ["1", "3"])
