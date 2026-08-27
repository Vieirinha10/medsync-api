"""Envio transacional de e-mails da MedSync."""

import html
import logging
import os
from urllib.parse import urlencode

import httpx

from settings import environment, frontend_url

logger = logging.getLogger(__name__)


def send_verification_email(*, email: str, nome: str, raw_token: str) -> None:
    """Envia o link de confirmação sem registrar o token em logs."""

    api_key = os.getenv("RESEND_API_KEY", "").strip()
    sender = os.getenv("EMAIL_FROM", "MedSync <contato@medsync.com.br>").strip()
    if not api_key:
        if environment() == "production":
            raise RuntimeError("RESEND_API_KEY não configurada para envio de e-mail.")
        logger.warning(
            "E-mail de verificação não enviado porque RESEND_API_KEY não está configurada."
        )
        return

    verification_url = (
        f"{frontend_url()}/verificar-email?{urlencode({'token': raw_token})}"
    )
    safe_name = html.escape(nome)
    safe_url = html.escape(verification_url, quote=True)
    response = httpx.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
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
        timeout=10.0,
    )
    response.raise_for_status()


def send_password_reset_email(
    *, email: str, nome: str, raw_token: str, expires_minutes: int = 30
) -> None:
    """Envia um link temporário de redefinição sem registrar o token em logs."""

    api_key = os.getenv("RESEND_API_KEY", "").strip()
    sender = os.getenv("EMAIL_FROM", "MedSync <contato@medsync.com.br>").strip()
    if not api_key:
        if environment() == "production":
            raise RuntimeError("RESEND_API_KEY não configurada para envio de e-mail.")
        logger.warning(
            "E-mail de recuperação não enviado porque RESEND_API_KEY não está configurada."
        )
        return

    reset_url = f"{frontend_url()}/redefinir-senha?{urlencode({'token': raw_token})}"
    safe_name = html.escape(nome)
    safe_url = html.escape(reset_url, quote=True)
    response = httpx.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
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
        timeout=10.0,
    )
    response.raise_for_status()
