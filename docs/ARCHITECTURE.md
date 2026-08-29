# Base técnica do MedSync

## Objetivo

A API deve crescer sem concentrar conteúdo clínico, autenticação, persistência e
avaliação no mesmo módulo. Os endpoints públicos permanecem estáveis enquanto a
implementação interna evolui por domínios.

## Módulos atuais

- `routers`: transporte HTTP e validação das dependências da requisição.
- `services`: operações de domínio e acesso ao catálogo clínico.
- `schemas`: contratos Pydantic independentes dos modelos do banco.
- `models`: entidades SQLAlchemy e relacionamentos persistentes.
- `evaluation`: rubrica objetiva e composição do feedback educacional.
- `security`: autenticação e autorização do usuário.

## Conteúdo clínico

Casos, exames e rubricas agora possuem tabelas próprias. O catálogo em Python é
mantido temporariamente somente como fonte de carga inicial dos 65 casos. Depois
da carga, a API consulta o banco como fonte principal.

Cada caso possui estado e versão de conteúdo. Cada rubrica possui versão, estado
de revisão, definição estruturada, responsável e data de revisão. Isso prepara a
plataforma para um painel editorial e para auditoria clínica.

## Migrações

Toda mudança de esquema deve gerar uma revisão Alembic. A migração inicial é
compatível com bancos que já possuem `users` e `progressos`, permitindo adotar o
versionamento sem recriar essas tabelas.

## Próximas entregas da Etapa 1

1. restringir CORS e adicionar limites de requisição por rota;
2. fortalecer sessão, recuperação de senha e eventos de segurança;
3. criar CI para API e frontend, incluindo testes de contrato e navegação;
4. adicionar logs estruturados, métricas e alertas;
5. remover o catálogo legado quando o painel editorial estiver disponível.
