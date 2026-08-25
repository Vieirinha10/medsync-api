from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from evaluation import (
    SimulationEvaluation,
    SimulationQuestionRequest,
    SimulationQuestionResponse,
    SimulationSubmission,
    answer_simulation_question,
    build_clinical_consequences,
    enhance_narrative_with_ai,
    evaluate_objective,
)
from models import AIUsageRecord, Progresso, SimulationRequest, User
from routers.error_notebook import register_clinical_result
from security import get_current_user, require_premium_content
from services.activity import track_activity
from services.clinical_content import get_published_case, serialize_case

router = APIRouter(prefix="/simulacoes", tags=["Simulação Clínica 2.0"])


def _evaluation_from_progress(progress: Progresso) -> dict[str, object]:
    evaluation_data = progress.respostas_usuario.get("_avaliacao")
    if evaluation_data is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este registro pertence à versão anterior da simulação.",
        )
    return {"progresso_id": progress.id, **evaluation_data}


def _duplicate_request_response(
    request_record: SimulationRequest,
    *,
    caso_id: int,
    db: Session,
) -> dict[str, object] | None:
    if request_record.id_caso != caso_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A chave de reenvio já foi usada em outro caso clínico.",
        )
    if request_record.status == "completed" and request_record.progresso_id:
        progress = db.get(Progresso, request_record.progresso_id)
        if progress is not None:
            return _evaluation_from_progress(progress)
    if request_record.status == "processing":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A Synapse ainda está processando este mesmo envio. "
                "Aguarde alguns instantes e tente novamente."
            ),
        )
    return None


def _usage_record(
    *,
    id_usuario: int,
    progresso_id: int,
    operacao: str,
    modelo: str,
    usage,
) -> AIUsageRecord:
    return AIUsageRecord(
        id_usuario=id_usuario,
        progresso_id=progresso_id,
        operacao=operacao,
        modelo=modelo,
        input_tokens=usage.input_tokens,
        cached_input_tokens=usage.cached_input_tokens,
        output_tokens=usage.output_tokens,
        reasoning_tokens=usage.reasoning_tokens,
        total_tokens=usage.total_tokens,
        duracao_ms=usage.duracao_ms,
        custo_estimado_usd=usage.custo_estimado_usd,
        response_id=usage.response_id,
    )


@router.post(
    "/{caso_id}/finalizar",
    response_model=SimulationEvaluation,
    status_code=status.HTTP_201_CREATED,
)
def finalizar_simulacao(
    caso_id: int,
    submission: SimulationSubmission,
    idempotency_key: Annotated[str | None, Header(alias="X-Idempotency-Key")] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case_record = get_published_case(db, caso_id)
    if case_record is None:
        raise HTTPException(status_code=404, detail="Caso não encontrado.")
    require_premium_content(current_user, is_premium=case_record.is_premium)
    if case_record.rubrica is None or case_record.rubrica.status != "revisada":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este caso ainda não possui gabarito revisado para a Simulação Clínica 2.0.",
        )

    case = serialize_case(case_record)
    case["rubrica"] = case_record.rubrica.definicao
    valid_exam_ids = {exam["id"] for exam in case["exames_disponiveis"]}
    if set(submission.exames_solicitados) - valid_exam_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A submissão contém exames que não pertencem a este caso.",
        )
    if set(submission.justificativas_exames) - valid_exam_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A submissão contém justificativas para exames que não pertencem a este caso.",
        )

    request_record = None
    if idempotency_key is not None:
        idempotency_key = idempotency_key.strip()
        if not 16 <= len(idempotency_key) <= 100:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A chave de reenvio da simulação é inválida.",
            )
        request_record = db.scalar(
            select(SimulationRequest).where(
                SimulationRequest.id_usuario == current_user.id,
                SimulationRequest.idempotency_key == idempotency_key,
            )
        )
        if request_record is not None:
            duplicate_response = _duplicate_request_response(
                request_record,
                caso_id=caso_id,
                db=db,
            )
            if duplicate_response is not None:
                return duplicate_response
            request_record.status = "processing"
            request_record.progresso_id = None
            request_record.updated_at = datetime.now(UTC)
            db.commit()
        else:
            request_record = SimulationRequest(
                id_usuario=current_user.id,
                id_caso=caso_id,
                idempotency_key=idempotency_key,
                status="processing",
            )
            db.add(request_record)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                request_record = db.scalar(
                    select(SimulationRequest).where(
                        SimulationRequest.id_usuario == current_user.id,
                        SimulationRequest.idempotency_key == idempotency_key,
                    )
                )
                if request_record is None:
                    raise
                duplicate_response = _duplicate_request_response(
                    request_record,
                    caso_id=caso_id,
                    db=db,
                )
                if duplicate_response is not None:
                    return duplicate_response

    try:
        score, exam_feedback, context = evaluate_objective(
            case,
            submission,
            rubric=case_record.rubrica.definicao,
        )
        narrative, feedback_source, model, ai_usage = enhance_narrative_with_ai(
            case, submission, score, exam_feedback, context
        )
        total_score = score.exames + score.hipotese + score.conduta
        consequences = build_clinical_consequences(exam_feedback, context)
        evaluation_data = {
            "caso_id": caso_id,
            "caso_titulo": case["titulo"],
            "diagnostico_referencia": case_record.rubrica.definicao[
                "diagnostico_referencia"
            ],
            "pontuacao_total": total_score,
            "pontuacao": score.model_dump(),
            "exames": exam_feedback.model_dump(),
            "feedback": narrative.model_dump(),
            "objetivos_aprendizagem": case_record.rubrica.definicao.get(
                "objetivos_aprendizagem", []
            ),
            "fontes_clinicas": case_record.rubrica.definicao.get("fontes_clinicas", []),
            "nivel_conduta": context.get("nivel_conduta", "parcial"),
            "consequencias": consequences.model_dump(),
            "versao_rubrica": case_record.rubrica.versao,
            "fonte_feedback": feedback_source,
            "modelo_ia": model,
            "uso_ia": ai_usage.model_dump() if ai_usage else None,
            "aviso_educacional": SimulationEvaluation.model_fields[
                "aviso_educacional"
            ].default,
        }
        entry = Progresso(
            id_usuario=current_user.id,
            id_caso=caso_id,
            respostas_usuario={
                **submission.model_dump(),
                "_avaliacao": evaluation_data,
                "_rubrica_snapshot": {
                    "versao": case_record.rubrica.versao,
                    "definicao": case_record.rubrica.definicao,
                },
            },
            pontuacao=total_score,
        )
        db.add(entry)
        db.flush()
        if ai_usage is not None and model is not None:
            db.add(
                _usage_record(
                    id_usuario=current_user.id,
                    progresso_id=entry.id,
                    operacao="avaliacao_simulacao",
                    modelo=model,
                    usage=ai_usage,
                )
            )
        if request_record is not None:
            request_record.status = "completed"
            request_record.progresso_id = entry.id
            request_record.updated_at = datetime.now(UTC)
        track_activity(db, current_user.id, "conclusao", "caso_clinico", caso_id)
        register_clinical_result(
            db,
            current_user.id,
            case,
            submission.model_dump(),
            evaluation_data,
        )
        db.commit()
        db.refresh(entry)
        return {"progresso_id": entry.id, **evaluation_data}
    except Exception:
        db.rollback()
        if request_record is not None:
            failed_request = db.get(SimulationRequest, request_record.id)
            if failed_request is not None:
                failed_request.status = "failed"
                failed_request.updated_at = datetime.now(UTC)
                db.commit()
        raise


@router.get("/resultados/{progresso_id}", response_model=SimulationEvaluation)
def obter_resultado_simulacao(
    progresso_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    progress = db.scalar(
        select(Progresso).where(
            Progresso.id == progresso_id,
            Progresso.id_usuario == current_user.id,
        )
    )
    if progress is None:
        raise HTTPException(status_code=404, detail="Resultado não encontrado.")
    return _evaluation_from_progress(progress)


@router.post(
    "/resultados/{progresso_id}/perguntar",
    response_model=SimulationQuestionResponse,
)
def perguntar_sobre_resultado(
    progresso_id: int,
    payload: SimulationQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    progress = db.scalar(
        select(Progresso).where(
            Progresso.id == progresso_id,
            Progresso.id_usuario == current_user.id,
        )
    )
    if progress is None:
        raise HTTPException(status_code=404, detail="Resultado não encontrado.")
    evaluation_data = progress.respostas_usuario.get("_avaliacao")
    if evaluation_data is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este registro pertence à versão anterior da simulação.",
        )
    case_record = get_published_case(db, progress.id_caso)
    if case_record is None or case_record.rubrica is None:
        raise HTTPException(status_code=404, detail="Caso ou rubrica não encontrado.")
    require_premium_content(current_user, is_premium=case_record.is_premium)
    case = serialize_case(case_record)
    submission = {
        key: value
        for key, value in progress.respostas_usuario.items()
        if not key.startswith("_")
    }
    rubric_snapshot = progress.respostas_usuario.get("_rubrica_snapshot", {})
    rubric_definition = rubric_snapshot.get("definicao", case_record.rubrica.definicao)
    answer = answer_simulation_question(
        question=payload.pergunta,
        case=case,
        submission=submission,
        evaluation=evaluation_data,
        rubric=rubric_definition,
    )
    if answer.uso_ia is not None and answer.modelo_ia is not None:
        db.add(
            _usage_record(
                id_usuario=current_user.id,
                progresso_id=progress.id,
                operacao="pergunta_pos_simulacao",
                modelo=answer.modelo_ia,
                usage=answer.uso_ia,
            )
        )
        db.commit()
    return answer
