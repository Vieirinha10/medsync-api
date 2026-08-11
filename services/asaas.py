from typing import Any

import httpx

from settings import asaas_api_key, asaas_environment


class AsaasConfigurationError(RuntimeError):
    pass


class AsaasApiError(RuntimeError):
    pass


def _base_url() -> str:
    if asaas_environment() == "production":
        return "https://api.asaas.com/v3"
    return "https://api-sandbox.asaas.com/v3"


def _request(
    method: str,
    path: str,
    *,
    payload: dict[str, Any] | None = None,
    timeout: float = 20.0,
) -> dict[str, Any]:
    api_key = asaas_api_key()
    if not api_key:
        raise AsaasConfigurationError(
            f"Os pagamentos no ambiente {asaas_environment()} ainda não foram ativados. "
            "Configure a chave correspondente da Asaas."
        )

    try:
        response = httpx.request(
            method,
            f"{_base_url()}{path}",
            json=payload if method.upper() != "GET" else None,
            headers={
                "accept": "application/json",
                "access_token": api_key,
                "User-Agent": "MedSync/1.0 pagamentos@medsync.educacional",
            },
            timeout=timeout,
        )
    except httpx.RequestError as exc:
        raise AsaasApiError("Não foi possível conectar ao processamento da Asaas.") from exc

    if response.status_code >= 400:
        try:
            error_data = response.json()
            descriptions = [
                item.get("description", "") for item in error_data.get("errors", [])
            ]
            detail = " ".join(value for value in descriptions if value)
        except (ValueError, AttributeError):
            detail = ""
        raise AsaasApiError(detail or "A Asaas não conseguiu processar a solicitação.")

    return response.json()


def create_checkout(payload: dict[str, Any]) -> dict[str, Any]:
    data = _request("POST", "/checkouts", payload=payload)

    checkout_id = data.get("id")
    if not checkout_id:
        raise AsaasApiError("A Asaas não retornou o identificador do checkout.")

    if not data.get("link"):
        host = "asaas.com" if asaas_environment() == "production" else "sandbox.asaas.com"
        data["link"] = f"https://{host}/checkoutSession/show?id={checkout_id}"
    return data


def create_customer(payload: dict[str, Any]) -> dict[str, Any]:
    return _request("POST", "/customers", payload=payload)


def create_payment(payload: dict[str, Any]) -> dict[str, Any]:
    return _request("POST", "/payments", payload=payload, timeout=65.0)


def get_pix_qr_code(payment_id: str) -> dict[str, Any]:
    return _request("GET", f"/payments/{payment_id}/pixQrCode")


def create_subscription(payload: dict[str, Any]) -> dict[str, Any]:
    return _request("POST", "/subscriptions", payload=payload, timeout=65.0)
