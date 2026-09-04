# Documentação Técnica: Catálogo v2 e Atualização Consolidada do Banco de Questões MedSync

> **Nota para o ChatGPT / Próximos Agentes de IA / Desenvolvedores:**  
> Este documento é o registro definitivo de arquitetura, dados, qualidade e segurança da atualização massiva do banco de questões da plataforma **MedSync**. Leia atentamente as seções abaixo para manter a integridade operacional do projeto.

---

## 1. Visão Geral do Sistema

* **Plataforma:** MedSync — Plataforma de Educação Médica, Banco de Questões e Simulações Clínicas.
* **Backend:** FastAPI (Python 3.12, SQLAlchemy, SQLite WAL mode, Uvicorn). Diretório: `medsync-api/`.
* **Frontend:** React 18, Vite, React Router, Lucide/React Icons. Diretório: `medsync-frontend/`.
* **Banco de Dados Principal:** `medsync-api/medsync.db` (SQLite operando em modo **WAL - Write-Ahead Logging**).
* **Versão Ativa do Catálogo:** `v2` (configurada via `QUESTION_CATALOG_ACTIVE_VERSION=v2` no `.env`).

---

## 2. Métricas Consolidadas do Banco de Dados (`medsync.db`)

* **Total no Catálogo Ativo (v2):** **226.792 questões médicas homologadas**.
* **Total no Catálogo Legado (v1):** **2.811 questões** (piloto original preservado).
* **Total Geral de Questões no Banco:** **229.603 questões**.
* **Faixa Cronológica de Provas:** Exames de **2004 a 2026**.

### 2.1. Distribuição por Especialidade Médica (Catálogo v2)

| Especialidade | Questões | % do Catálogo |
| :--- | :--- | :--- |
| **Clínica Médica** | 77.690 | 34,25% |
| **Cirurgia Geral e Especializada** | 31.922 | 14,08% |
| **Medicina Preventiva e Social** | 31.067 | 13,70% |
| **Pediatria** | 30.494 | 13,45% |
| **Ginecologia** | 22.433 | 9,89% |
| **Obstetrícia** | 19.325 | 8,52% |
| **Outros Médicos** | 9.028 | 3,98% |
| **Psiquiatria** | 1.758 | 0,78% |
| **Oftalmologia** | 1.313 | 0,58% |
| **Otorrinolaringologia** | 1.309 | 0,58% |
| **Ortopedia** | 447 | 0,20% |
| **Medicina Legal** | 6 | <0,01% |

### 2.2. Distribuição por Tipo de Prova e Formato

* **Múltipla Escolha Clássica (5 alternativas - A, B, C, D, E):** 193.299
* **Múltipla Escolha (4 alternativas - A, B, C, D):** 26.215
* **Certo / Errado (2 opções - Padrão Cebraspe/CESPE):** 7.278

### 2.3. Mídia e Dependência Visual

* **Autonomia Textual Pura (`NO_VISUAL_DEPENDENCY`):** 215.550 questões (95,04%)
* **Imagens Preservadas em CDN/S3 (`REQUIRES_IMAGE`):** 11.237 questões (4,95%)
* **Termo Visual Contextual (`VISUAL_TERM_CONTEXT_ONLY`):** 5 questões (<0,01%)

---

## 3. Histórico dos Lotes Processados e Inseridos

O acervo de origem continha 246.089 registros brutos em `questoes.db`. Foram processados os seguintes lotes atômicos com o importador `scripts/import_question_catalog.py`:

1. **Lote 1 & 2 (Recentes 2026-2024 e Certo/Errado):** Ingestão de abertura com auditoria de integridade.
2. **Lote 3 (Visual CDN):** 3.837 questões com suporte a imagens hospedadas em CDN/S3.
3. **Lote 4 (Ciclo 2023-2022):** 13.661 questões canônicas.
4. **Lote 5 (Ciclo 2021):** 10.069 questões canônicas.
5. **Lote 6 (Ciclo 2020-2018):** 19.615 questões canônicas.
6. **Lote 7A (Ciclo 2017-2016):** 19.055 questões canônicas.
7. **Lote 7B (Ciclo 2015-2014):** 18.704 questões canônicas.
8. **Lote 8A (Ciclo 2013-2012):** 14.760 questões canônicas.
9. **Lote 8B (Ciclo 2011-2009):** 16.541 questões canônicas.
10. **Lote 9 (Ciclo Histórico 2008-2004):** 5.029 questões canônicas.
11. **Lote 10 (Varredura de Residuais de Provas Oficiais):** 159 questões canônicas.

---

## 4. Diretrizes de Qualidade e Segurança (Padrão Ouro Codex)

### 4.1. Sigilo Autoral e Zero Vazamento de Comentários
* **Regra Fundamental:** É terminantemente proibido exibir comentários, anotações de aula ou explicações de professores de plataformas terceiras.
* **Estado Atual:** Em 100% das 226.792 questões ativas, a coluna `explicacao` no banco de dados é `null` e o `explicacao_status` é `'pendente'`.
* **API Shield:** A rota `/questoes/{id}/explicacao` retorna HTTP 400 com a mensagem `"Comentário editorial em preparação pela equipe do MedSync"`, evitando geração automática sem supervisão técnica da equipe médica.

### 4.2. Prevenção de Fraude (Anti-Cheating)
* Na rota de busca e listagem (`/questoes`) e detalhes (`/questoes/{id}`), a função `serialize_question()` **remove**:
  * `is_correct` de cada alternativa
  * `alternativa_correta_id`
  * `correct_letter`
  * `fingerprint`
  * `answer_binding_hash`
* O cliente recebe apenas `{ id, texto, html }`.
* A validação do acerto é estritamente **server-side** no endpoint `/questoes/{id}/responder`. O gabarito só é entregue após a submissão formal da tentativa.

### 4.3. Tríplice Hash SHA-256 (Anti-Tampering)
Cada questão possui 3 hashes criptográficos de 64 caracteres hexadecimais:
1. `content_hash_plain`: SHA-256 de `{enunciado_puro}||{alt_id}:{alt_texto_puro}|...`
2. `content_hash_rich`: SHA-256 de `{enunciado_html}||{alt_id}:{alt_html}|...`
3. `answer_binding_hash`: SHA-256 de `{content_hash_plain}||{gabarito}||{alt_id}:{is_correct_bool}|...`

### 4.4. Higienização de Taxonomia e Filtros
* **Módulo Normalizador:** `medsync-api/scripts/taxonomy_normalizer.py`.
* Converte arrays serializados (`[{"n": "...", "p": "..."}]`) e hierarquias com delimitador `[$$]` em strings limpas e padronizadas para `especialidade`, `tema`, `subtema` e `assunto`.
* A API (`/questoes/meta`) e o Frontend (`QuestoesPage.jsx`) possuem camadas complementares de higienização (`sanitize_facet_label` e `formatFilterLabel`).
* Resultado: **Zero anomalias** ou dicionários nos filtros.

### 4.5. Prevenção de XSS e Sanitização HTML
* Todas as questões com formatação visual foram submetidas ao `CodexHTMLSanitizer`.
* Tags permitidas: `<p>`, `<b>`, `<strong>`, `<i>`, `<em>`, `<u>`, `<sub>`, `<sup>`, `<ul>`, `<ol>`, `<li>`, `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>`, `<blockquote>`, `<span>`, `<div>`, `<img>`.
* Tags proibidas e eliminadas com seu conteúdo: `<script>`, `<style>`, `<iframe>`, `<video>`, `<audio>`, `<object>`, `<embed>`, `<form>`, `<input>`, `<button>`, `<meta>`, `<link>`.
* Eventos inline (`onclick`, `onerror`, `onload`) e protocolos perigosos (`javascript:`, `data:`) foram completamente expurgados (0 ocorrências em 104.541 questões com HTML).

### 4.6. Concorrência e Resiliência SQLite
* O banco `medsync.db` opera com `PRAGMA journal_mode=WAL;` (Write-Ahead Logging) e `PRAGMA synchronous=NORMAL;`.
* Leituras concorrentes múltiplas de estudantes não bloqueiam escritas, e gravações de tentativas não causam `database is locked`.

---

## 5. Estrutura de Rotas e Endpoints Relevantes

| Método | Endpoint | Proteção | Descrição |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Pública | Healthcheck da API (`{"status": "ok"}`). |
| `GET` | `/questoes/meta` | JWT | Retorna estatísticas e facetas limpas de filtros (anos, especialidades, temas, limite diário). |
| `GET` | `/questoes` | JWT | Retorna lote de questões (máx 30 por chamada, filtradas ou aleatórias via `random_rank`). |
| `POST` | `/questoes/{id}/responder` | JWT | Valida resposta do aluno, grava tentativa e entrega gabarito com estatísticas de acerto. |
| `POST` | `/questoes/{id}/sinalizar` | JWT | Permite ao aluno apontar erro ou sugestão na questão. |
| `POST` | `/questoes/{id}/explicacao` | JWT | Bloqueada em v2 (status editorial pendente). |

---

## 6. Comandos Operacionais

### Executar a API em Desenvolvimento / Produção
```powershell
# No diretório: medsync-api
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### Executar o Frontend
```powershell
# No diretório: medsync-frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

### Executar Suíte de Testes do Backend (110 testes)
```powershell
# No diretório: medsync-api
.\.venv\Scripts\pytest
```

### Executar Suíte de Testes do Frontend (87 testes em 27 arquivos)
```powershell
# No diretório: medsync-frontend
npx vitest run
```

---

## 7. Arquivos Chave para Manutenção Futura

* `medsync-api/routers/questions.py`: Router principal de questões, serialização segura e validação server-side.
* `medsync-api/scripts/import_question_catalog.py`: Importador determinístico atômico v1.1.
* `medsync-api/scripts/taxonomy_normalizer.py`: Normalizador canônico de especialidades, temas e assuntos.
* `medsync-api/middleware.py`: Middleware de Rate Limiting, observabilidade e injeção de headers de segurança (CSP, HSTS, X-Frame-Options).
* `medsync-frontend/src/pages/QuestoesPage.jsx`: Interface de estudo de questões, filtros, descarte de alternativas e sinalização de erros.
