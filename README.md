# MedSync API

API da plataforma MedSync construída com FastAPI.

## Execução local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
python -m scripts.seed_clinical_content
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
- `RATE_LIMIT_ENABLED`: ativa limites para cadastro, login e avaliações; o padrão
  é `true` em produção e `false` no desenvolvimento.
- `ADMIN_EMAILS`: lista separada por vírgulas dos e-mails autorizados a acessar
  os indicadores acadêmicos agregados.

Em produção, configure um PostgreSQL persistente. O SQLite padrão é destinado
somente ao desenvolvimento local.

## Banco de dados

O esquema é versionado pelo Alembic. Para aplicar todas as migrações:

```bash
alembic upgrade head
```

O catálogo legado com os 40 casos é usado somente como carga inicial idempotente:

```bash
python -m scripts.seed_clinical_content
```

No Gunicorn, migrações e carga inicial são executadas uma única vez pelo processo
principal antes da criação dos workers.

## Organização

- `main.py`: criação e configuração da aplicação.
- `routers/`: endpoints agrupados por domínio.
- `schemas.py`: contratos de entrada e saída da API.
- `services/`: regras de acesso e carga do conteúdo clínico.
- `models.py`: entidades persistentes.
- `alembic/`: histórico versionado do banco.
- `case_catalog.py`: fonte legada usada apenas para a primeira carga.

Consulte `docs/ARCHITECTURE.md` para as decisões e próximos passos da base técnica.

## Testes

```bash
pytest -q
```

Além de `/health`, a API disponibiliza `/ready`, que verifica também a conexão
com o banco. Todas as respostas incluem um `X-Request-ID` para correlação nos logs.
