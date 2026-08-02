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
