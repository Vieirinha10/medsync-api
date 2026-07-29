# MedSync API

API da plataforma MedSync construída com FastAPI.

## Execução local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn main:app --reload
```

A API inicia em `http://127.0.0.1:8000` e a documentação interativa fica em
`http://127.0.0.1:8000/docs`.

## Variáveis de ambiente

- `DATABASE_URL`: conexão SQLAlchemy. Usa SQLite localmente e aceita PostgreSQL.
- `JWT_SECRET_KEY`: chave de assinatura dos tokens. É obrigatória quando
  `ENVIRONMENT=production`.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: validade do token, em minutos.
- `CORS_ORIGINS`: origens permitidas, separadas por vírgula.

Em produção, configure um PostgreSQL persistente. O SQLite padrão é destinado
somente ao desenvolvimento local.

## Testes

```bash
pytest -q
```
