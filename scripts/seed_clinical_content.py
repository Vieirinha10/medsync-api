from database import SessionLocal
from services.clinical_content import seed_clinical_content


def main() -> None:
    with SessionLocal() as db:
        created = seed_clinical_content(db)
    print(
        "Catálogo clínico carregado." if created else "Catálogo clínico já existente."
    )


if __name__ == "__main__":
    main()
