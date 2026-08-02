from models import UserActivity


def track_activity(
    db,
    user_id: int,
    event: str,
    content_type: str | None = None,
    content_id: str | int | None = None,
) -> None:
    db.add(
        UserActivity(
            id_usuario=user_id,
            evento=event,
            tipo_conteudo=content_type,
            id_conteudo=str(content_id) if content_id is not None else None,
        )
    )
