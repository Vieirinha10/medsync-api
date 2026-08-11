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


def create_checkout(payload: dict[str, Any]) -> dict[str, Any]:
    api_key = asaas_api_key()
    if not api_key:
        raise AsaasConfigurationError(
            "O checkout ainda não foi ativado. Configure a chave Sandbox da Asaas."
        )

    try:
        response = httpx.post(
            f"{_base_url()}/checkouts",
            json=payload,
            headers={
                "accept": "application/json",
                "access_token": api_key,
                "User-Agent": "MedSync/1.0 pagamentos@medsync.educacional",
            },
            timeout=20.0,
        )
    except httpx.RequestError as exc:
        raise AsaasApiError("Não foi possível conectar ao checkout da Asaas.") from exc

    if response.status_code >= 400:
        try:
            error_data = response.json()
            descriptions = [
                item.get("description", "") for item in error_data.get("errors", [])
            ]
            detail = " ".join(value for value in descriptions if value)
        except (ValueError, AttributeError):
            detail = ""
        raise AsaasApiError(detail or "A Asaas recusou a criação do checkout.")

    data = response.json()
    checkout_id = data.get("id")
    if not checkout_id:
        raise AsaasApiError("A Asaas não retornou o identificador do checkout.")

    if not data.get("link"):
        host = "asaas.com" if asaas_environment() == "production" else "sandbox.asaas.com"
        data["link"] = f"https://{host}/checkoutSession/show?id={checkout_id}"
    return data
