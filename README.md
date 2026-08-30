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
- `OPENAI_ROUTINE_MODEL`: modelo econômico usado nos feedbacks e perguntas
  comuns; padrão `gpt-5.6-luna`.
- `OPENAI_ADVANCED_MODEL`: modelo reservado a ambiguidade, complexidade e risco
  clínico; padrão `gpt-5.6-terra`. `OPENAI_MODEL` permanece como fallback legado.
- `OPENAI_QUESTION_MODEL`: modelo opcional das explicações próprias do banco de
  questões; quando vazio, utiliza `OPENAI_MODEL`.
- `OPENAI_SIMULATION_QUESTION_MODEL`: substituição opcional das perguntas
  pós-simulação. Quando vazio, elas são roteadas automaticamente entre rotina e
  avançado.
- `OPENAI_REASONING_EFFORT`: esforço de raciocínio das chamadas interativas;
  padrão `low`, pois a avaliação clínica objetiva já foi calculada pelo sistema.
- `OPENAI_FEEDBACK_MAX_OUTPUT_TOKENS` e `OPENAI_QUESTION_MAX_OUTPUT_TOKENS`:
  tetos de saída, limitados em código a 400–1600 e 200–800, respectivamente.

O painel administrativo consulta `GET /admin/synapse/consumo?dias=30` para
acompanhar chamadas, tokens, cache, custo estimado, latência, modelos, operações
e usuários com maior consumo. Esta versão não cria franquia nem bloqueio de
perguntas por usuário.

Em produção, configure um PostgreSQL persistente. O SQLite padrão é destinado
somente ao desenvolvimento local.

## Checkout transparente

`POST /pagamentos/transparente` mantém a jornada de Pix e cartão dentro do
MedSync. O endpoint cria o cliente na Asaas uma única vez, gera o QR Code Pix
ou processa cartão/assinatura diretamente e depende do webhook para liberar o
Premium. Número do cartão e CVV são apenas encaminhados à Asaas durante a
requisição e nunca são persistidos pelo MedSync.

O checkout hospedado em `POST /pagamentos/checkout` continua disponível como
contingência operacional.

## Banco de dados

O esquema é versionado pelo Alembic. Para aplicar todas as migrações:

```bash
alembic upgrade head
```

O catálogo em código com os 80 casos é usado somente como carga inicial idempotente:

```bash
python -m scripts.seed_clinical_content
```

O módulo de questões usa o catálogo compactado e auditável em
`data/question_catalog.json.gz`. A carga é idempotente e mantém tentativas e
relatos em tabelas próprias, sem alimentar revisões ou o caderno de erros. Para
refazer o catálogo a partir de uma exportação autorizada:

```bash
python scripts/build_question_catalog.py questoes.html data/question_catalog.json.gz
```

O gerador remove duplicatas, questões anuladas, gabaritos inconsistentes,
alternativas incompletas e itens que dependem de imagens ausentes. Comentários,
vídeos e links de mídia da exportação não são incorporados.

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
