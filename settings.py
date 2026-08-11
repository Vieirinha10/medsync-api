import os

PRODUCTION_FRONTENDS = (
    "https://medsync-frontend-vieirinha10s-projects.vercel.app",
    "https://medsync-frontend-git-main-vieirinha10s-projects.vercel.app",
)


def environment() -> str:
    return os.getenv("ENVIRONMENT", "development").lower()


def cors_origins() -> list[str]:
    configured = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    if configured:
        return configured
    if environment() == "production":
        return list(PRODUCTION_FRONTENDS)
    return ["http://localhost:5173", "http://127.0.0.1:5173"]


def rate_limit_enabled() -> bool:
    default = "true" if environment() == "production" else "false"
    return os.getenv("RATE_LIMIT_ENABLED", default).lower() == "true"


def admin_emails() -> set[str]:
    return {
        email.strip().lower()
        for email in os.getenv("ADMIN_EMAILS", "").split(",")
        if email.strip()
    }


def is_admin_email(email: str) -> bool:
    return email.strip().lower() in admin_emails()


def frontend_url() -> str:
    return os.getenv("FRONTEND_URL", cors_origins()[0]).rstrip("/")


def asaas_environment() -> str:
    value = os.getenv("ASAAS_ENVIRONMENT", "sandbox").strip().lower()
    if value not in {"sandbox", "production"}:
        raise RuntimeError("ASAAS_ENVIRONMENT deve ser sandbox ou production.")
    return value


def asaas_api_key() -> str | None:
    current_environment = asaas_environment()
    scoped_key = os.getenv(f"ASAAS_{current_environment.upper()}_API_KEY")
    if scoped_key:
        return scoped_key
    if current_environment == "sandbox":
        return os.getenv("ASAAS_API_KEY") or None
    return None


def asaas_webhook_token() -> str | None:
    current_environment = asaas_environment()
    scoped_token = os.getenv(f"ASAAS_{current_environment.upper()}_WEBHOOK_TOKEN")
    if scoped_token:
        return scoped_token
    if current_environment == "sandbox":
        return os.getenv("ASAAS_WEBHOOK_TOKEN") or None
    return None
