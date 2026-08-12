from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
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
from models import Progresso, User
from routers.error_notebook import register_clinical_result
from security import get_current_user
from services.activity import track_activity
from services.clinical_content import get_published_case, serialize_case

router = APIRouter(prefix="/simulacoes", tags=["Simulação Clínica 2.0"])


@router.post(
    "/{caso_id}/finalizar",
    response_model=SimulationEvaluation,
    status_code=status.HTTP_201_CREATED,
)
def finalizar_simulacao(
    caso_id: int,
    submission: SimulationSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case_record = get_published_case(db, caso_id)
    if case_record is None:
        raise HTTPException(status_code=404, detail="Caso não encontrado.")
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

    score, exam_feedback, context = evaluate_objective(
        case,
        submission,
        rubric=case_record.rubrica.definicao,
    )
    narrative, feedback_source, model = enhance_narrative_with_ai(
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
    evaluation_data = progress.respostas_usuario.get("_avaliacao")
    if evaluation_data is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este registro pertence à versão anterior da simulação.",
        )
    return {"progresso_id": progress.id, **evaluation_data}


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
    case = serialize_case(case_record)
    submission = {
        key: value
        for key, value in progress.respostas_usuario.items()
        if not key.startswith("_")
    }
    rubric_snapshot = progress.respostas_usuario.get("_rubrica_snapshot", {})
    rubric_definition = rubric_snapshot.get(
        "definicao", case_record.rubrica.definicao
    )
    return answer_simulation_question(
        question=payload.pergunta,
        case=case,
        submission=submission,
        evaluation=evaluation_data,
        rubric=rubric_definition,
    )
