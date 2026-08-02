import csv
import hashlib
import io
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from database import get_db
from evaluation import ClinicalRubricDefinition
from models import (
    Announcement,
    ClinicalCase,
    ClinicalExam,
    ClinicalRubric,
    Progresso,
    User,
    UserActivity,
    VisualChallenge,
)
from routers.content import serialize_challenge
from schemas import (
    AcademicAnalyticsResponse,
    AdminClinicalCaseResponse,
    AdminClinicalCaseUpsert,
    AdminOverviewResponse,
    AdminVisualChallengeResponse,
    AdminVisualChallengeUpsert,
    AnnouncementResponse,
    AnnouncementUpsert,
)
from security import get_current_user
from settings import is_admin_email

router = APIRouter(prefix="/admin", tags=["Administração"])


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not is_admin_email(current_user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito aos administradores do MedSync.",
        )
    return current_user


def percentage(value: int, total: int) -> float:
    return round((value / total) * 100, 1) if total else 0.0


def serialize_admin_case(case: ClinicalCase) -> dict:
    return {
        "id": case.id,
        "titulo": case.titulo,
        "especialidade": case.especialidade,
        "nivel_dificuldade": case.nivel_dificuldade,
        "historia_clinica": case.historia_clinica,
        "exame_fisico": case.exame_fisico,
        "status": case.status,
        "premium": case.is_premium,
        "versao_conteudo": case.versao_conteudo,
        "avaliacao_2_disponivel": bool(
            case.rubrica and case.rubrica.status == "revisada"
        ),
        "rubrica": case.rubrica.definicao if case.rubrica else None,
        "exames": [
            {
                "codigo": exam.codigo,
                "nome": exam.nome,
                "resultado": exam.resultado,
                "referencia_adequada": exam.referencia_adequada,
            }
            for exam in case.exames
        ],
        "updated_at": case.updated_at,
    }


def apply_case_payload(case: ClinicalCase, payload: AdminClinicalCaseUpsert) -> None:
    case.titulo = payload.titulo
    case.especialidade = payload.especialidade
    case.nivel_dificuldade = payload.nivel_dificuldade
    case.historia_clinica = payload.historia_clinica
    case.exame_fisico = payload.exame_fisico
    case.status = payload.status
    case.is_premium = payload.premium
    existing_exams = {exam.codigo: exam for exam in case.exames}
    updated_exams = []
    for index, exam in enumerate(payload.exames):
        record = existing_exams.get(exam.codigo) or ClinicalExam(codigo=exam.codigo)
        record.nome = exam.nome
        record.resultado = exam.resultado
        record.referencia_adequada = exam.referencia_adequada
        record.ordem = index
        updated_exams.append(record)
    case.exames = updated_exams
    if payload.rubrica is None:
        case.rubrica = None
    else:
        try:
            definition = ClinicalRubricDefinition.model_validate(payload.rubrica)
        except ValidationError as error:
            raise HTTPException(
                status_code=422,
                detail=f"Rubrica inválida: {error.errors()[0]['msg']}",
            ) from error
        case.rubrica = ClinicalRubric(
            versao=(case.rubrica.versao + 1 if case.rubrica else 1),
            status="revisada",
            definicao=definition.model_dump(mode="json"),
            revisado_por="Administração MedSync",
            revisado_em=datetime.now(UTC),
        )


def apply_challenge_payload(
    challenge: VisualChallenge, payload: AdminVisualChallengeUpsert
) -> None:
    challenge.id = payload.id
    challenge.titulo = payload.titulo
    challenge.especialidade = payload.especialidade
    challenge.dificuldade = payload.dificuldade
    challenge.modalidade = payload.modalidade
    challenge.pergunta = payload.pergunta
    challenge.imagem_url = payload.imagem_url
    challenge.imagem_alt = payload.imagem_alt
    challenge.alternativas = [
        {"id": f"option-{index + 1}", "texto": text}
        for index, text in enumerate(payload.alternativas)
    ]
    challenge.alternativa_correta_id = f"option-{payload.alternativa_correta + 1}"
    challenge.diagnostico_correto = payload.diagnostico_correto
    challenge.explicacao = payload.explicacao
    challenge.achados_chave = payload.achados_chave
    challenge.fonte_credito = payload.fonte_credito
    challenge.fonte_licenca = payload.fonte_licenca
    challenge.fonte_url = payload.fonte_url
    challenge.status = payload.status


@router.get("/analytics/academico", response_model=AcademicAnalyticsResponse)
def academic_analytics(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    total_users = db.scalar(select(func.count(User.id))) or 0
    completed_profiles = (
        db.scalar(
            select(func.count(User.id)).where(
                User.periodo_curso.is_not(None),
                User.faculdade.is_not(None),
            )
        )
        or 0
    )
    new_users = (
        db.scalar(
            select(func.count(User.id)).where(
                User.created_at >= datetime.now(UTC) - timedelta(days=30)
            )
        )
        or 0
    )

    period_rows = db.execute(
        select(User.periodo_curso, func.count(User.id))
        .where(User.periodo_curso.is_not(None))
        .group_by(User.periodo_curso)
        .order_by(User.periodo_curso)
    ).all()

    normalized_faculty = func.lower(func.trim(User.faculdade))
    faculty_rows = db.execute(
        select(func.min(User.faculdade), func.count(User.id))
        .where(User.faculdade.is_not(None), func.trim(User.faculdade) != "")
        .group_by(normalized_faculty)
        .order_by(func.count(User.id).desc(), func.min(User.faculdade))
    ).all()

    return {
        "total_usuarios": total_users,
        "perfis_academicos_preenchidos": completed_profiles,
        "cobertura_percentual": percentage(completed_profiles, total_users),
        "novos_ultimos_30_dias": new_users,
        "periodos": [
            {
                "periodo": period,
                "total": count,
                "percentual": percentage(count, completed_profiles),
            }
            for period, count in period_rows
        ],
        "faculdades": [
            {
                "faculdade": faculty,
                "total": count,
                "percentual": percentage(count, completed_profiles),
            }
            for faculty, count in faculty_rows
        ],
    }


@router.get("/overview", response_model=AdminOverviewResponse)
def operational_overview(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    now = datetime.now(UTC)
    total_users = db.scalar(select(func.count(User.id))) or 0
    active_7 = (
        db.scalar(
            select(func.count(User.id)).where(
                User.last_login_at >= now - timedelta(days=7)
            )
        )
        or 0
    )
    active_30 = (
        db.scalar(
            select(func.count(User.id)).where(
                User.last_login_at >= now - timedelta(days=30)
            )
        )
        or 0
    )
    new_30 = (
        db.scalar(
            select(func.count(User.id)).where(
                User.created_at >= now - timedelta(days=30)
            )
        )
        or 0
    )
    users_with_completion = (
        db.scalar(select(func.count(func.distinct(Progresso.id_usuario)))) or 0
    )

    eligible_users = db.scalars(
        select(User).where(User.created_at <= now - timedelta(days=7))
    ).all()
    retained = sum(
        1
        for user in eligible_users
        if user.last_login_at is not None
        and user.last_login_at.replace(tzinfo=UTC)
        >= user.created_at.replace(tzinfo=UTC) + timedelta(days=7)
    )

    case_rows = db.execute(
        select(
            ClinicalCase.id,
            ClinicalCase.titulo,
            func.count(Progresso.id),
            func.count(func.distinct(Progresso.id_usuario)),
        )
        .join(Progresso, Progresso.id_caso == ClinicalCase.id)
        .group_by(ClinicalCase.id, ClinicalCase.titulo)
    ).all()
    challenge_rows = db.execute(
        select(UserActivity.id_conteudo, func.count(UserActivity.id))
        .where(UserActivity.tipo_conteudo == "desafio_visual")
        .group_by(UserActivity.id_conteudo)
    ).all()
    challenge_titles = {
        item.id: item.titulo for item in db.scalars(select(VisualChallenge)).all()
    }
    popular = [
        {
            "tipo": "caso_clinico",
            "id": str(case_id),
            "titulo": title,
            "acessos": completions,
            "conclusoes": unique_users,
        }
        for case_id, title, completions, unique_users in case_rows
    ]
    popular.extend(
        {
            "tipo": "desafio_visual",
            "id": challenge_id or "",
            "titulo": challenge_titles.get(
                challenge_id, challenge_id or "Desafio visual"
            ),
            "acessos": accesses,
            "conclusoes": accesses,
        }
        for challenge_id, accesses in challenge_rows
    )
    popular.sort(key=lambda item: item["acessos"], reverse=True)

    activities = db.scalars(
        select(UserActivity).where(UserActivity.created_at >= now - timedelta(days=13))
    ).all()
    daily = defaultdict(lambda: {"users": set(), "events": 0})
    for activity in activities:
        key = activity.created_at.date().isoformat()
        daily[key]["users"].add(activity.id_usuario)
        daily[key]["events"] += 1
    daily_metrics = []
    for offset in range(13, -1, -1):
        key = (now - timedelta(days=offset)).date().isoformat()
        daily_metrics.append(
            {
                "data": key,
                "usuarios": len(daily[key]["users"]),
                "eventos": daily[key]["events"],
            }
        )

    return {
        "total_usuarios": total_users,
        "ativos_7_dias": active_7,
        "ativos_30_dias": active_30,
        "novos_30_dias": new_30,
        "taxa_conclusao": percentage(users_with_completion, total_users),
        "retencao_7_dias": percentage(retained, len(eligible_users)),
        "casos_publicados": db.scalar(
            select(func.count(ClinicalCase.id)).where(
                ClinicalCase.status == "publicado"
            )
        )
        or 0,
        "desafios_publicados": db.scalar(
            select(func.count(VisualChallenge.id)).where(
                VisualChallenge.status == "publicado"
            )
        )
        or 0,
        "avisos_ativos": db.scalar(
            select(func.count(Announcement.id)).where(Announcement.ativo.is_(True))
        )
        or 0,
        "conteudos_populares": popular[:10],
        "atividade_diaria": daily_metrics,
    }


@router.get("/casos", response_model=list[AdminClinicalCaseResponse])
def admin_list_cases(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    cases = db.scalars(
        select(ClinicalCase)
        .options(selectinload(ClinicalCase.exames), selectinload(ClinicalCase.rubrica))
        .order_by(ClinicalCase.updated_at.desc())
    ).all()
    return [serialize_admin_case(case) for case in cases]


@router.post(
    "/casos",
    response_model=AdminClinicalCaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def admin_create_case(
    payload: AdminClinicalCaseUpsert,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    case = ClinicalCase(versao_conteudo=1)
    apply_case_payload(case, payload)
    db.add(case)
    db.commit()
    db.refresh(case)
    return serialize_admin_case(case)


@router.put("/casos/{case_id}", response_model=AdminClinicalCaseResponse)
def admin_update_case(
    case_id: int,
    payload: AdminClinicalCaseUpsert,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    case = db.scalar(
        select(ClinicalCase)
        .where(ClinicalCase.id == case_id)
        .options(selectinload(ClinicalCase.exames), selectinload(ClinicalCase.rubrica))
    )
    if case is None:
        raise HTTPException(status_code=404, detail="Caso não encontrado.")
    apply_case_payload(case, payload)
    case.versao_conteudo += 1
    db.commit()
    db.refresh(case)
    return serialize_admin_case(case)


@router.get("/desafios", response_model=list[AdminVisualChallengeResponse])
def admin_list_challenges(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return [
        serialize_challenge(challenge)
        for challenge in db.scalars(
            select(VisualChallenge).order_by(VisualChallenge.updated_at.desc())
        ).all()
    ]


@router.post(
    "/desafios",
    response_model=AdminVisualChallengeResponse,
    status_code=status.HTTP_201_CREATED,
)
def admin_create_challenge(
    payload: AdminVisualChallengeUpsert,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    challenge = VisualChallenge()
    apply_challenge_payload(challenge, payload)
    db.add(challenge)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Já existe um desafio com esse ID."
        ) from None
    db.refresh(challenge)
    return serialize_challenge(challenge)


@router.put("/desafios/{challenge_id}", response_model=AdminVisualChallengeResponse)
def admin_update_challenge(
    challenge_id: str,
    payload: AdminVisualChallengeUpsert,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    challenge = db.get(VisualChallenge, challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail="Desafio não encontrado.")
    if payload.id != challenge_id:
        raise HTTPException(
            status_code=422, detail="O ID do desafio não pode ser alterado."
        )
    apply_challenge_payload(challenge, payload)
    db.commit()
    db.refresh(challenge)
    return serialize_challenge(challenge)


@router.get("/avisos", response_model=list[AnnouncementResponse])
def admin_list_announcements(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(Announcement).order_by(Announcement.created_at.desc())
    ).all()


@router.post(
    "/avisos",
    response_model=AnnouncementResponse,
    status_code=status.HTTP_201_CREATED,
)
def admin_create_announcement(
    payload: AnnouncementUpsert,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    data = payload.model_dump()
    data["inicia_em"] = data["inicia_em"] or datetime.now(UTC)
    announcement = Announcement(**data, criado_por=admin.id)
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return announcement


@router.put("/avisos/{announcement_id}", response_model=AnnouncementResponse)
def admin_update_announcement(
    announcement_id: int,
    payload: AnnouncementUpsert,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    announcement = db.get(Announcement, announcement_id)
    if announcement is None:
        raise HTTPException(status_code=404, detail="Aviso não encontrado.")
    for key, value in payload.model_dump(exclude={"inicia_em"}).items():
        setattr(announcement, key, value)
    if payload.inicia_em is not None:
        announcement.inicia_em = payload.inicia_em
    db.commit()
    db.refresh(announcement)
    return announcement


@router.get("/relatorios/anonimizado.csv")
def export_anonymized_report(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    users = db.scalars(select(User).order_by(User.id)).all()
    progress_rows = db.execute(
        select(
            Progresso.id_usuario,
            func.count(Progresso.id),
            func.avg(Progresso.pontuacao),
        ).group_by(Progresso.id_usuario)
    ).all()
    progress = {user_id: (count, average) for user_id, count, average in progress_rows}
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "usuario_anonimo",
            "periodo",
            "faculdade",
            "mes_cadastro",
            "casos_concluidos",
            "media_pontuacao",
            "ativo_ultimos_30_dias",
        ]
    )
    cutoff = datetime.now(UTC) - timedelta(days=30)
    for user in users:
        count, average = progress.get(user.id, (0, 0))
        anonymous_id = hashlib.sha256(f"medsync:{user.id}".encode()).hexdigest()[:12]
        writer.writerow(
            [
                f"USR-{anonymous_id}",
                user.periodo_curso or "",
                user.faculdade or "",
                user.created_at.strftime("%Y-%m"),
                count,
                round(float(average or 0), 1),
                "sim"
                if user.last_login_at is not None
                and user.last_login_at.replace(tzinfo=UTC) >= cutoff
                else "nao",
            ]
        )
    return Response(
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=medsync-relatorio-anonimizado.csv"
        },
    )
