"""Envio transacional de e-mails da MedSync."""

import html
import logging
import os
from urllib.parse import urlencode

import httpx

from settings import environment, frontend_url

logger = logging.getLogger(__name__)


class EmailDeliveryError(RuntimeError):
    """Falha operacional no envio, sem expor credenciais ou destinatários."""


def _deliver_email(*, payload: dict[str, object], purpose: str) -> None:
    api_key = os.getenv("RESEND_API_KEY", "").strip()
    if not api_key:
        message = "RESEND_API_KEY não configurada para envio de e-mail."
        if environment() == "production":
            logger.error("email_delivery_not_configured purpose=%s", purpose)
            raise EmailDeliveryError(message)
        logger.warning("%s purpose=%s", message, purpose)
        return

    try:
        response = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.error(
            "email_delivery_rejected purpose=%s provider=resend status_code=%s",
            purpose,
            exc.response.status_code,
        )
        raise EmailDeliveryError(
            f"O provedor de e-mail recusou o envio (HTTP {exc.response.status_code})."
        ) from exc
    except httpx.RequestError as exc:
        logger.error(
            "email_delivery_transport_error purpose=%s provider=resend error_type=%s",
            purpose,
            type(exc).__name__,
        )
        raise EmailDeliveryError("Falha de conexão com o provedor de e-mail.") from exc

    message_id = None
    try:
        response_body = response.json()
        if isinstance(response_body, dict):
            message_id = response_body.get("id")
    except (TypeError, ValueError):
        pass
    logger.info(
        "email_delivery_succeeded purpose=%s provider=resend message_id=%s",
        purpose,
        message_id or "unavailable",
    )


def send_verification_email(*, email: str, nome: str, raw_token: str) -> None:
    """Envia o link de confirmação sem registrar o token em logs."""

    sender = os.getenv("EMAIL_FROM", "MedSync <contato@medsync.com.br>").strip()
    verification_url = (
        f"{frontend_url()}/verificar-email?{urlencode({'token': raw_token})}"
    )
    safe_name = html.escape(nome)
    safe_url = html.escape(verification_url, quote=True)
    _deliver_email(
        purpose="email_verification",
        payload={
            "from": sender,
            "to": [email],
            "subject": "Confirme seu e-mail na MedSync",
            "text": (
                f"Olá, {nome}. Confirme seu e-mail para ativar sua conta MedSync: "
                f"{verification_url}\n\nSe você não criou esta conta, ignore a mensagem."
            ),
            "html": (
                f"<p>Olá, {safe_name}.</p>"
                "<p>Confirme seu e-mail para ativar sua conta MedSync.</p>"
                f'<p><a href="{safe_url}">Confirmar meu e-mail</a></p>'
                "<p>Se você não criou esta conta, ignore a mensagem.</p>"
            ),
        },
    )


def send_password_reset_email(
    *, email: str, nome: str, raw_token: str, expires_minutes: int = 30
) -> None:
    """Envia um link temporário de redefinição sem registrar o token em logs."""

    sender = os.getenv("EMAIL_FROM", "MedSync <contato@medsync.com.br>").strip()
    reset_url = f"{frontend_url()}/redefinir-senha?{urlencode({'token': raw_token})}"
    safe_name = html.escape(nome)
    safe_url = html.escape(reset_url, quote=True)
    _deliver_email(
        purpose="password_reset",
        payload={
            "from": sender,
            "to": [email],
            "subject": "Redefina sua senha da MedSync",
            "text": (
                f"Olá, {nome}. Use este link para redefinir sua senha da MedSync: "
                f"{reset_url}\n\nO link expira em {expires_minutes} minutos e só pode ser usado uma vez. "
                "Se você não fez esta solicitação, ignore a mensagem."
            ),
            "html": (
                f"<p>Olá, {safe_name}.</p>"
                "<p>Recebemos uma solicitação para redefinir sua senha da MedSync.</p>"
                f'<p><a href="{safe_url}">Criar uma nova senha</a></p>'
                f"<p>O link expira em {expires_minutes} minutos e só pode ser usado uma vez.</p>"
                "<p>Se você não fez esta solicitação, ignore a mensagem.</p>"
            ),
        },
    )
