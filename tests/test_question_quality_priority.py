from services.question_quality_priority import (
    prioritize_question,
    summarize_priorities,
    year_bucket,
)


def row(question_id=1, year=2024, **changes):
    value = {
        "id": question_id,
        "source_id": str(question_id),
        "ano": year,
        "especialidade": "Clínica Médica",
        "assunto": "Hematologia",
        "tema": "Hematologia",
        "subtema": "Anemias",
        "status": "publicada",
        "quality_status": "triada",
        "quality_flags": [],
        "media_classification": "NO_VISUAL_DEPENDENCY",
        "image_rights_status": "NONE_REQUIRED",
        "enunciado": "Qual é o diagnóstico?",
        "statement_plain": "Qual é o diagnóstico?",
    }
    value.update(changes)
    return value


def test_year_policy_is_explicit_and_stable():
    assert year_bucket(2026) == "atual_2020_2026"
    assert year_bucket(2020) == "atual_2020_2026"
    assert year_bucket(2019) == "classica_2016_2019"
    assert year_bucket(2016) == "classica_2016_2019"
    assert year_bucket(2015) == "arquivo_pre_2016"
    assert year_bucket(None) == "sem_ano"


def test_clean_current_question_stays_in_routine_without_scientific_claim():
    result = prioritize_question(row())
    assert result["tier"] == "p3_rotina"
    assert result["action"] == "manter_catalogo_atual"
    assert result["reasons"] == ["structural_baseline_only"]


def test_hold_and_answer_conflict_take_absolute_priority():
    result = prioritize_question(
        row(
            status="revisao",
            quality_status="revisao_necessaria",
            quality_flags=["conflicting_answer_key"],
        )
    )
    assert result["tier"] == "p0_critica"
    assert result["action"] == "resolver_quarentena"
    assert "conflicting_answer_key" in result["reasons"]


def test_text_signal_images_reports_and_exposure_are_prioritized():
    result = prioritize_question(
        row(
            media_classification="REQUIRES_IMAGE",
            image_rights_status="PENDING",
        ),
        text_integrity_flagged=True,
        attempts=120,
        open_reports=2,
    )
    assert result["tier"] == "p0_critica"
    assert result["action"] == "revisar_integridade"
    assert set(result["reasons"]) >= {
        "text_integrity_signal",
        "image_rights_review",
        "open_student_report",
        "high_student_exposure",
    }


def test_annulled_question_is_counted_but_never_reenters_queue():
    result = prioritize_question(row(quality_status="anulada", status="revisao"))
    assert result["tier"] == "excluida"
    assert result["action"] == "manter_exclusao"


def test_summary_is_bounded_deterministic_and_contains_no_question_text():
    rows = [
        row(1, 2024),
        row(2, 2018),
        row(3, 2014),
        row(4, 2023, quality_status="revisao_necessaria", status="revisao"),
    ]
    result = summarize_priorities(rows, flagged_ids={1}, top_limit=2)
    assert result["scanned"] == 4
    assert len(result["priority_queue"]) == 2
    assert result["priority_queue"][0]["id"] == 4
    assert "enunciado" not in str(result["priority_queue"])
    assert result["policy"]["scientific_validation_inferred"] is False
    assert result["policy"]["database_mutations"] == 0
