from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, distinct, func, or_, select
from sqlalchemy.orm import Session

from database import get_db
from models import ExamQuestion, QuestionAttempt, QuestionReport, User
from schemas import (
    AdminQuestionReportUpdate,
    AdminQuestionsResponse,
    AdminQuestionUpdate,
    MessageResponse,
    MessageWithIdResponse,
    QuestionAnswerRequest,
    QuestionAnswerResponse,
    QuestionExplanation,
    QuestionListItem,
    QuestionMetadataResponse,
    QuestionPerformanceResponse,
    QuestionReportCreate,
)
from security import get_current_user
from services.activity import track_activity
from services.question_explanations import generate_question_explanation
from settings import is_admin_email

router = APIRouter(tags=["Questões"])
FREE_DAILY_LIMIT = 10
LOCAL_TIMEZONE = ZoneInfo("America/Fortaleza")


def current_admin(user: User = Depends(get_current_user)) -> User:
    if not is_admin_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito aos administradores do MedSync.",
        )
    return user


def is_premium(user: User) -> bool:
    entitlement = user.entitlement
    if entitlement is None or entitlement.status != "ativo":
        return False
    expiry = entitlement.valido_ate
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=UTC)
    return expiry > datetime.now(UTC)


def start_of_local_day() -> datetime:
    now = datetime.now(LOCAL_TIMEZONE)
    return now.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(UTC)


def answered_today(db: Session, user_id: int) -> int:
    return int(
        db.scalar(
            select(func.count(distinct(QuestionAttempt.id_questao))).where(
                QuestionAttempt.id_usuario == user_id,
                QuestionAttempt.created_at >= start_of_local_day(),
            )
        )
        or 0
    )


def question_answer_distribution(
    db: Session,
    question: ExamQuestion,
) -> tuple[list[dict[str, object]], int]:
    valid_alternative_ids = [item["id"] for item in question.alternativas]
    latest_attempts = (
        select(func.max(QuestionAttempt.id).label("attempt_id"))
        .where(QuestionAttempt.id_questao == question.id)
        .group_by(QuestionAttempt.id_usuario)
        .subquery()
    )
    counts = {
        str(alternative_id): int(total)
        for alternative_id, total in db.execute(
            select(
                QuestionAttempt.alternativa_selecionada_id,
                func.count(QuestionAttempt.id),
            )
            .join(
                latest_attempts,
                QuestionAttempt.id == latest_attempts.c.attempt_id,
            )
            .where(
                QuestionAttempt.alternativa_selecionada_id.in_(valid_alternative_ids)
            )
            .group_by(QuestionAttempt.alternativa_selecionada_id)
        ).all()
    }
    total_respondents = sum(counts.values())
    distribution = [
        {
            "id": alternative["id"],
            "escolhas": counts.get(alternative["id"], 0),
            "percentual": round(
                counts.get(alternative["id"], 0) * 100 / total_respondents,
                1,
            )
            if total_respondents
            else 0.0,
        }
        for alternative in question.alternativas
    ]
    return distribution, total_respondents


def serialize_question(question: ExamQuestion) -> dict:
    return {
        "id": question.id,
        "ano": question.ano,
        "instituicao": question.instituicao,
        "cabecalho": question.cabecalho,
        "especialidade": question.especialidade,
        "assunto": question.assunto,
        "enunciado": question.enunciado,
        "statement_rich_html": question.statement_rich_html or question.enunciado,
        "alternativas": question.alternativas,
        "catalog_version": question.catalog_version,
        "explicacao_disponivel": question.explicacao is not None,
    }


def facet(db: Session, column, catalog_version: str = "v1") -> list[dict[str, object]]:
    return [
        {"valor": str(value), "total": int(total)}
        for value, total in db.execute(
            select(column, func.count(ExamQuestion.id))
            .where(
                ExamQuestion.status == "publicada",
                ExamQuestion.catalog_version == catalog_version,
            )
            .group_by(column)
            .order_by(func.count(ExamQuestion.id).desc(), column)
        ).all()
    ]


@router.get("/questoes/meta", response_model=QuestionMetadataResponse)
def question_metadata(
    catalog_version: str = Query(default="v1"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    premium = is_premium(current_user) or is_admin_email(current_user.email)
    used = answered_today(db, current_user.id)
    return {
        "total_questoes": db.scalar(
            select(func.count(ExamQuestion.id)).where(
                ExamQuestion.status == "publicada",
                ExamQuestion.catalog_version == catalog_version,
            )
        )
        or 0,
        "especialidades": facet(db, ExamQuestion.especialidade, catalog_version),
        "assuntos": facet(db, ExamQuestion.assunto, catalog_version),
        "anos": facet(db, ExamQuestion.ano, catalog_version),
        "instituicoes": facet(db, ExamQuestion.instituicao, catalog_version),
        "premium_ativo": premium,
        "limite_diario": None if premium else FREE_DAILY_LIMIT,
        "respondidas_hoje": used,
        "restantes_hoje": None if premium else max(0, FREE_DAILY_LIMIT - used),
    }


@router.get("/questoes", response_model=list[QuestionListItem])
def list_questions(
    especialidade: str | None = None,
    assunto: str | None = None,
    ano: int | None = None,
    instituicao: str | None = None,
    catalog_version: str = Query(default="v1"),
    quantidade: int = Query(default=10, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    premium = is_premium(current_user) or is_admin_email(current_user.email)
    if not premium:
        quantidade = min(
            quantidade, max(0, FREE_DAILY_LIMIT - answered_today(db, current_user.id))
        )
    if quantidade == 0:
        return []

    statement = select(ExamQuestion).where(
        ExamQuestion.status == "publicada",
        ExamQuestion.catalog_version == catalog_version,
    )
    if especialidade:
        statement = statement.where(ExamQuestion.especialidade == especialidade)
    if assunto:
        statement = statement.where(ExamQuestion.assunto == assunto)
    if ano:
        statement = statement.where(ExamQuestion.ano == ano)
    if instituicao:
        statement = statement.where(ExamQuestion.instituicao == instituicao)

    recently_answered = select(QuestionAttempt.id_questao).where(
        QuestionAttempt.id_usuario == current_user.id,
        QuestionAttempt.created_at >= start_of_local_day(),
    )
    statement = statement.where(ExamQuestion.id.not_in(recently_answered))

    if catalog_version == "v2":
        import random
        rnd = random.random()
        statement = statement.order_by(
            case((ExamQuestion.random_rank >= rnd, 0), else_=1),
            ExamQuestion.random_rank,
        ).limit(quantidade)
    else:
        statement = statement.order_by(func.random()).limit(quantidade)

    return [serialize_question(item) for item in db.scalars(statement).all()]


@router.post("/questoes/{question_id}/responder", response_model=QuestionAnswerResponse)
def answer_question(
    question_id: int,
    payload: QuestionAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    question = db.get(ExamQuestion, question_id)
    if question is None or question.status != "publicada":
        raise HTTPException(status_code=404, detail="Questão não encontrada.")

    valid_ids = {item["id"] for item in question.alternativas}
    if payload.alternativa_id not in valid_ids:
        raise HTTPException(status_code=422, detail="Alternativa inválida.")

    already_answered_today = db.scalar(
        select(QuestionAttempt.id)
        .where(
            QuestionAttempt.id_usuario == current_user.id,
            QuestionAttempt.id_questao == question.id,
            QuestionAttempt.created_at >= start_of_local_day(),
        )
        .limit(1)
    )
    premium = is_premium(current_user) or is_admin_email(current_user.email)
    used = answered_today(db, current_user.id)
    if not premium and not already_answered_today and used >= FREE_DAILY_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Você concluiu as 10 questões gratuitas de hoje. "
                "O Premium libera listas ilimitadas."
            ),
        )

    correct = payload.alternativa_id == question.alternativa_correta_id
    explanation = question.explicacao
    explanation_status = "PENDING"

    if question.catalog_version == "v2":
        # ZERO SYNAPSE para o novo catálogo v2: Não chama gerador de IA, preserva comentário pendente
        explanation = None
        explanation_status = "PENDING"
    elif explanation is None:
        generated = generate_question_explanation(question)
        explanation = generated.model_dump(mode="json")
        if generated.fonte != "resumo_automatico":
            question.explicacao = explanation
            question.explicacao_status = "gerada"
        explanation_status = question.explicacao_status
    else:
        explanation_status = "PUBLISHED"

    db.add(
        QuestionAttempt(
            id_usuario=current_user.id,
            id_questao=question.id,
            alternativa_selecionada_id=payload.alternativa_id,
            correta=correct,
            tempo_segundos=payload.tempo_segundos,
        )
    )
    track_activity(
        db,
        current_user.id,
        "questao_respondida",
        "questao",
        str(question.id),
    )
    db.commit()
    used_after = answered_today(db, current_user.id)
    distribution, total_respondents = question_answer_distribution(db, question)
    return {
        "correta": correct,
        "alternativa_correta_id": question.alternativa_correta_id,
        "explicacao": explanation,
        "explanation_status": explanation_status,
        "distribuicao_alternativas": distribution,
        "total_respondentes": total_respondents,
        "respondidas_hoje": used_after,
        "restantes_hoje": None if premium else max(0, FREE_DAILY_LIMIT - used_after),
    }


@router.post(
    "/questoes/{question_id}/explicacao",
    response_model=QuestionExplanation,
)
def retry_question_explanation(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    question = db.get(ExamQuestion, question_id)
    if question is None or question.status != "publicada":
        raise HTTPException(status_code=404, detail="Questão não encontrada.")
    if question.catalog_version == "v2":
        raise HTTPException(
            status_code=400,
            detail="Comentário editorial em preparação pela equipe do MedSync.",
        )
    attempted = db.scalar(
        select(QuestionAttempt.id)
        .where(
            QuestionAttempt.id_usuario == current_user.id,
            QuestionAttempt.id_questao == question.id,
        )
        .limit(1)
    )
    if attempted is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Responda à questão antes de solicitar a explicação.",
        )
    if question.explicacao is not None:
        return question.explicacao

    explanation = generate_question_explanation(question)
    if explanation.fonte == "resumo_automatico":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "A explicação clínica completa não ficou pronta. "
                "Aguarde alguns instantes e tente novamente."
            ),
        )
    question.explicacao = explanation.model_dump(mode="json")
    question.explicacao_status = "gerada"
    db.commit()
    return explanation


@router.get("/questoes/desempenho", response_model=QuestionPerformanceResponse)
def question_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    attempts = int(
        db.scalar(
            select(func.count(QuestionAttempt.id)).where(
                QuestionAttempt.id_usuario == current_user.id
            )
        )
        or 0
    )
    correct = int(
        db.scalar(
            select(func.count(QuestionAttempt.id)).where(
                QuestionAttempt.id_usuario == current_user.id,
                QuestionAttempt.correta.is_(True),
            )
        )
        or 0
    )
    average_time = db.scalar(
        select(func.avg(QuestionAttempt.tempo_segundos)).where(
            QuestionAttempt.id_usuario == current_user.id,
            QuestionAttempt.tempo_segundos.is_not(None),
        )
    )
    topic_rows = db.execute(
        select(
            ExamQuestion.assunto,
            func.count(QuestionAttempt.id),
            func.sum(case((QuestionAttempt.correta.is_(True), 1), else_=0)),
        )
        .join(QuestionAttempt, QuestionAttempt.id_questao == ExamQuestion.id)
        .where(QuestionAttempt.id_usuario == current_user.id)
        .group_by(ExamQuestion.assunto)
        .order_by(func.count(QuestionAttempt.id).desc())
    ).all()
    return {
        "respondidas": attempts,
        "acertos": correct,
        "percentual": round((correct / attempts) * 100, 1) if attempts else 0,
        "tempo_medio_segundos": round(average_time)
        if average_time is not None
        else None,
        "assuntos": [
            {
                "assunto": topic,
                "respondidas": total,
                "acertos": hits,
                "percentual": round((hits / total) * 100, 1) if total else 0,
            }
            for topic, total, hits in topic_rows
        ],
    }


@router.post("/questoes/{question_id}/reportar", response_model=MessageWithIdResponse)
def report_question(
    question_id: int,
    payload: QuestionReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if db.get(ExamQuestion, question_id) is None:
        raise HTTPException(status_code=404, detail="Questão não encontrada.")
    existing_report = db.scalar(
        select(QuestionReport)
        .where(
            QuestionReport.id_usuario == current_user.id,
            QuestionReport.id_questao == question_id,
            QuestionReport.status != "resolvido",
        )
        .order_by(QuestionReport.created_at.desc())
        .limit(1)
    )
    if existing_report is not None:
        existing_report.motivo = payload.motivo
        existing_report.descricao = payload.descricao
        db.commit()
        return {
            "id": existing_report.id,
            "message": "Seu relato aberto foi atualizado para revisão editorial.",
        }
    report = QuestionReport(
        id_usuario=current_user.id,
        id_questao=question_id,
        motivo=payload.motivo,
        descricao=payload.descricao,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return {"id": report.id, "message": "Relato enviado para revisão editorial."}


@router.get("/admin/questoes", response_model=AdminQuestionsResponse)
def admin_questions(
    busca: str | None = Query(default=None, min_length=1, max_length=160),
    situacao: str | None = Query(default=None, pattern="^(publicada|oculta|revisao)$"),
    assunto: str | None = Query(default=None, max_length=160),
    relato_status: str | None = Query(
        default=None, pattern="^(aberto|em_analise|resolvido)$"
    ),
    limite: int = Query(default=100, ge=1, le=200),
    _: User = Depends(current_admin),
    db: Session = Depends(get_db),
):
    attempt_stats = (
        select(
            QuestionAttempt.id_questao.label("question_id"),
            func.count(QuestionAttempt.id).label("attempts"),
            func.sum(case((QuestionAttempt.correta.is_(True), 1), else_=0)).label(
                "hits"
            ),
        )
        .group_by(QuestionAttempt.id_questao)
        .subquery()
    )
    report_stats = (
        select(
            QuestionReport.id_questao.label("question_id"),
            func.count(QuestionReport.id).label("reports"),
        )
        .where(QuestionReport.status != "resolvido")
        .group_by(QuestionReport.id_questao)
        .subquery()
    )
    question_statement = (
        select(
            ExamQuestion,
            func.coalesce(attempt_stats.c.attempts, 0),
            func.coalesce(attempt_stats.c.hits, 0),
            func.coalesce(report_stats.c.reports, 0),
        )
        .outerjoin(attempt_stats, attempt_stats.c.question_id == ExamQuestion.id)
        .outerjoin(report_stats, report_stats.c.question_id == ExamQuestion.id)
    )
    if busca:
        term = busca.strip()
        search_conditions = [
            ExamQuestion.cabecalho.ilike(f"%{term}%"),
            ExamQuestion.enunciado.ilike(f"%{term}%"),
            ExamQuestion.instituicao.ilike(f"%{term}%"),
            ExamQuestion.assunto.ilike(f"%{term}%"),
        ]
        if term.isdigit():
            search_conditions.append(ExamQuestion.id == int(term))
        question_statement = question_statement.where(or_(*search_conditions))
    if situacao:
        question_statement = question_statement.where(ExamQuestion.status == situacao)
    if assunto:
        question_statement = question_statement.where(ExamQuestion.assunto == assunto)
    rows = db.execute(
        question_statement.order_by(
            func.coalesce(report_stats.c.reports, 0).desc(),
            func.coalesce(attempt_stats.c.attempts, 0).desc(),
            ExamQuestion.id.desc(),
        ).limit(limite)
    ).all()

    report_statement = (
        select(QuestionReport, ExamQuestion, User)
        .join(ExamQuestion, ExamQuestion.id == QuestionReport.id_questao)
        .join(User, User.id == QuestionReport.id_usuario)
    )
    if relato_status:
        report_statement = report_statement.where(
            QuestionReport.status == relato_status
        )
    reports = db.execute(
        report_statement.order_by(QuestionReport.created_at.desc()).limit(100)
    ).all()
    return {
        "resumo": {
            "total": db.scalar(select(func.count(ExamQuestion.id))) or 0,
            "publicadas": db.scalar(
                select(func.count(ExamQuestion.id)).where(
                    ExamQuestion.status == "publicada"
                )
            )
            or 0,
            "explicacoes_pendentes": db.scalar(
                select(func.count(ExamQuestion.id)).where(
                    ExamQuestion.explicacao_status == "pendente"
                )
            )
            or 0,
            "explicacoes_geradas": db.scalar(
                select(func.count(ExamQuestion.id)).where(
                    ExamQuestion.explicacao_status.in_(("gerada", "revisada"))
                )
            )
            or 0,
            "relatos_abertos": db.scalar(
                select(func.count(QuestionReport.id)).where(
                    QuestionReport.status != "resolvido"
                )
            )
            or 0,
            "tentativas": db.scalar(select(func.count(QuestionAttempt.id))) or 0,
        },
        "questoes": [
            {
                "id": item.id,
                "cabecalho": item.cabecalho,
                "especialidade": item.especialidade,
                "assunto": item.assunto,
                "enunciado": item.enunciado,
                "alternativas": item.alternativas,
                "alternativa_correta_id": item.alternativa_correta_id,
                "explicacao": item.explicacao,
                "explicacao_status": item.explicacao_status,
                "status": item.status,
                "tentativas": attempts,
                "percentual_acerto": round((hits / attempts) * 100, 1)
                if attempts
                else 0,
                "relatos_abertos": open_reports,
            }
            for item, attempts, hits, open_reports in rows
        ],
        "relatos": [
            {
                "id": report.id,
                "questao_id": question.id,
                "questao_cabecalho": question.cabecalho,
                "usuario_nome": user.nome,
                "usuario_email": user.email,
                "motivo": report.motivo,
                "descricao": report.descricao,
                "status": report.status,
                "created_at": report.created_at,
            }
            for report, question, user in reports
        ],
    }


@router.patch("/admin/questoes/{question_id}", response_model=MessageResponse)
def update_admin_question(
    question_id: int,
    payload: AdminQuestionUpdate,
    _: User = Depends(current_admin),
    db: Session = Depends(get_db),
):
    question = db.get(ExamQuestion, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Questão não encontrada.")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(question, field, value)
    db.commit()
    return {"message": "Questão atualizada."}


@router.patch("/admin/questoes/relatos/{report_id}", response_model=MessageResponse)
def update_question_report(
    report_id: int,
    payload: AdminQuestionReportUpdate,
    _: User = Depends(current_admin),
    db: Session = Depends(get_db),
):
    report = db.get(QuestionReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Relato não encontrado.")
    report.status = payload.status
    report.resolved_at = datetime.now(UTC) if payload.status == "resolvido" else None
    db.commit()
    return {"message": "Relato atualizado."}


@router.post(
    "/admin/questoes/{question_id}/gerar-explicacao",
    response_model=MessageResponse,
)
def regenerate_question_explanation(
    question_id: int,
    _: User = Depends(current_admin),
    db: Session = Depends(get_db),
):
    question = db.get(ExamQuestion, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Questão não encontrada.")
    explanation = generate_question_explanation(question)
    if explanation.fonte == "resumo_automatico":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A Synapse não está disponível para gerar a explicação agora.",
        )
    question.explicacao = explanation.model_dump(mode="json")
    question.explicacao_status = "gerada"
    db.commit()
    return {"message": "Explicação própria gerada e armazenada."}
