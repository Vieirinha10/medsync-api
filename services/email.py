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
