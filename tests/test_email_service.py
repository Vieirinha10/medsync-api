import logging

import httpx
import pytest

from services import email as email_service


def test_delivery_logs_provider_message_id_without_recipient(monkeypatch, caplog):
    monkeypatch.setenv("RESEND_API_KEY", "test-key")
    response = httpx.Response(
        200,
        json={"id": "email-message-id"},
        request=httpx.Request("POST", "https://api.resend.com/emails"),
    )
    monkeypatch.setattr(email_service.httpx, "post", lambda *args, **kwargs: response)

    with caplog.at_level(logging.INFO, logger=email_service.__name__):
        email_service._deliver_email(
            purpose="password_reset",
            payload={"to": ["private@example.com"]},
        )

    assert "email_delivery_succeeded" in caplog.text
    assert "email-message-id" in caplog.text
    assert "private@example.com" not in caplog.text


def test_delivery_turns_resend_rejection_into_sanitized_error(monkeypatch, caplog):
    monkeypatch.setenv("RESEND_API_KEY", "test-key")
    response = httpx.Response(
        403,
        json={"message": "sensitive provider response"},
        request=httpx.Request("POST", "https://api.resend.com/emails"),
    )
    monkeypatch.setattr(email_service.httpx, "post", lambda *args, **kwargs: response)

    with caplog.at_level(logging.ERROR, logger=email_service.__name__):
        with pytest.raises(email_service.EmailDeliveryError, match="HTTP 403"):
            email_service._deliver_email(
                purpose="password_reset",
                payload={"to": ["private@example.com"]},
            )

    assert "email_delivery_rejected" in caplog.text
    assert "status_code=403" in caplog.text
    assert "private@example.com" not in caplog.text
    assert "sensitive provider response" not in caplog.text


def test_production_requires_resend_api_key(monkeypatch, caplog):
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.setattr(email_service, "environment", lambda: "production")

    with caplog.at_level(logging.ERROR, logger=email_service.__name__):
        with pytest.raises(email_service.EmailDeliveryError, match="não configurada"):
            email_service._deliver_email(
                purpose="password_reset",
                payload={"to": ["private@example.com"]},
            )

    assert "email_delivery_not_configured" in caplog.text
    assert "private@example.com" not in caplog.text
