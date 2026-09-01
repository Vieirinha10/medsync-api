# Graph Report - medsync-api-ai-skills  (2026-09-01)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 850 nodes · 2142 edges · 56 communities (35 shown, 8 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 254 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `62ff18ba`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- evaluation.py
- models.py
- schemas.py
- MedSync — Diretriz Oficial para Criação de Desafios Visuais
- test_api.py
- payments.py
- User
- main.py
- questions.py
- synapse_providers.py
- field_validator
- users.py
- clinical_content.py
- ClinicalRubric
- clinical_cases_psychiatry.py
- clinical_rubric_catalog.py
- clinical_cases_batch_one.py
- build_question_catalog.py
- primary_care_catalog.py
- setup_agent_skills.py
- clinical_cases_batch_two.py
- case_catalog.py
- clinical_feedback_batch_final.py
- 20260811_08_public_case_titles.py
- clinical_feedback_batch_four.py
- clinical_feedback_batch_three.py
- clinical_feedback_batch_two.py
- vital_signs.py
- Simulação Clínica 2.2
- Eficiência operacional da Synapse
- routers/__init__.py
- CasoClinico
- ProgressoCreate
- StudyErrorResponse
- Homologação clínica — lote 2
- scripts/__init__.py
- Repertório de IA do MedSync — API
- Base técnica do MedSync
- services/__init__.py
- Rubricas Clínicas 2.0
- 🧠 Synapse Multi-LLM 5-Core — Guia de Arquitetura e Ativação
- Não publicado
- Instruções para agentes e colaboradores

## God Nodes (most connected - your core abstractions)
1. `User` - 93 edges
2. `_register_and_login()` - 51 edges
3. `SimulationSubmission` - 27 edges
4. `ClinicalCase` - 27 edges
5. `ExamQuestion` - 26 edges
6. `evaluate_objective()` - 25 edges
7. `ClinicalRubric` - 23 edges
8. `Base` - 22 edges
9. `finalizar_simulacao()` - 20 edges
10. `MedSync — Diretriz Oficial para Criação de Desafios Visuais` - 19 edges

## Surprising Connections (you probably didn't know these)
- `test_email_verification_can_be_resent_without_account_enumeration()` --uses--> `User`  [INFERRED]
  tests/test_api.py → models.py
- `test_registration_requires_and_records_legal_acceptance()` --uses--> `User`  [INFERRED]
  tests/test_api.py → models.py
- `finalizar_simulacao()` --uses--> `SimulationSubmission`  [INFERRED]
  routers/simulations.py → evaluation.py
- `finalizar_simulacao()` --uses--> `SimulationEvaluation`  [INFERRED]
  routers/simulations.py → evaluation.py
- `perguntar_sobre_resultado()` --uses--> `SimulationQuestionRequest`  [INFERRED]
  routers/simulations.py → evaluation.py

## Import Cycles
- None detected.

## Communities (56 total, 8 thin omitted)

### Community 0 - "evaluation.py"
Cohesion: 0.07
Nodes (77): AIUsageMetrics, answer_simulation_question(), _bounded_env_int(), build_clinical_consequences(), build_compact_feedback_payload(), build_compact_question_payload(), build_exam_rationale_feedback(), build_rule_based_narrative() (+69 more)

### Community 1 - "models.py"
Cohesion: 0.07
Nodes (65): alias, Base, get_db(), DeclarativeBase, Header, HTTPAuthorizationCredentials, AsaasWebhookEvent, Progresso (+57 more)

### Community 2 - "schemas.py"
Cohesion: 0.07
Nodes (56): AcademicAnalyticsResponse, AcademicInstitutionMetric, AcademicPeriodMetric, AdminClinicalExam, AdminContentMetric, AdminDailyMetric, AdminFinancialFailure, AdminFinancialOrder (+48 more)

### Community 3 - "MedSync — Diretriz Oficial para Criação de Desafios Visuais"
Cohesion: 0.05
Nodes (36): 10. Regras para a explicação, 11. Achados-chave, 12. Regras para imagens e licenças, 13. Limites de inferência clínica, 14. Diversidade dentro do lote, 15. Proteção do gabarito, 16. Checklist de aprovação do lote, 17. Instrução pronta para outras IAs (+28 more)

### Community 4 - "test_api.py"
Cohesion: 0.07
Nodes (44): _independent_question_explanation(), _register_and_login(), test_academic_analytics_are_restricted_and_aggregated(), test_admin_can_search_moderate_and_generate_question_explanations(), test_admin_operations_manage_content_metrics_announcements_and_export(), test_admin_synapse_usage_aggregates_tokens_cost_latency_and_models(), test_all_cases_are_available_after_final_rubric_review(), test_asaas_checkout_and_webhook_activate_premium_once() (+36 more)

### Community 5 - "payments.py"
Cohesion: 0.11
Nodes (46): PaymentGrant, PaymentOrder, UserEntitlement, _add_months(), _callback(), _card_payload(), _check_payment_availability(), _checkout_payload() (+38 more)

### Community 6 - "User"
Cohesion: 0.12
Nodes (48): Gabaritos dos desafios nativos mantidos somente no servidor., AIUsageRecord, Announcement, Métrica financeira e operacional de cada chamada feita pela Synapse., User, VisualChallenge, put, academic_analytics() (+40 more)

### Community 7 - "main.py"
Cohesion: 0.09
Nodes (31): BaseHTTPMiddleware, FastAPI, on_starting(), Aplica migrações uma única vez antes de iniciar os workers., get_learning_activity(), get_learning_path(), create_app(), lifespan() (+23 more)

### Community 8 - "questions.py"
Cohesion: 0.16
Nodes (34): ExamQuestion, QuestionAttempt, QuestionReport, admin_questions(), answer_question(), answered_today(), current_admin(), facet() (+26 more)

### Community 9 - "synapse_providers.py"
Cohesion: 0.10
Nodes (14): AnthropicProvider, calculate_cost_usd(), ConsensusResult, DeepSeekProvider, _ensure_env_loaded(), GeminiProvider, ProviderUsageMetrics, Any (+6 more)

### Community 10 - "field_validator"
Cohesion: 0.11
Nodes (11): EmailStr, field_validator, EmailVerificationResend, PasswordRecoveryRequest, QuestionAnswerRequest, TransparentCard, TransparentPayer, UserCreate (+3 more)

### Community 11 - "users.py"
Cohesion: 0.18
Nodes (25): _as_utc(), login_usuario(), obter_usuario_atual(), datetime, get, post, Session, recuperar_senha() (+17 more)

### Community 12 - "clinical_content.py"
Cohesion: 0.22
Nodes (20): ClinicalCase, ClinicalExam, main(), _case_from_catalog(), list_published_cases(), datetime, Session, Atualiza apenas as rubricas piloto mantidas e revisadas no código. (+12 more)

### Community 13 - "ClinicalRubric"
Cohesion: 0.22
Nodes (15): ClinicalRubricDefinition, ClinicalRubric, test_existing_pilot_rubric_is_safely_upgraded(), test_fifth_feedback_expansion_batch_is_structured_and_clinically_corrected(), test_final_feedback_batch_is_structured_and_clinically_corrected(), test_first_expansion_batch_is_complete_rich_and_revised(), test_first_feedback_expansion_batch_is_structured_and_clinically_corrected(), test_first_rubric_v2_batch_is_available_and_has_clinical_sources() (+7 more)

### Community 14 - "clinical_cases_psychiatry.py"
Cohesion: 0.28
Nodes (11): _case(), _criterion(), _exam(), _exam_reasons(), _outcomes(), _psy_rubric(), Any, Lote adicional de Psiquiatria e Saúde Mental (casos 66 a 80). (+3 more)

### Community 15 - "clinical_rubric_catalog.py"
Cohesion: 0.15
Nodes (9): Any, Quinto lote de rubricas estruturadas para casos clínicos legados., _source(), Any, Primeiro lote de rubricas estruturadas para casos clínicos legados., _source(), Any, Rubricas clínicas revisáveis usadas pela Simulação Clínica 2.1. (+1 more)

### Community 16 - "clinical_cases_batch_one.py"
Cohesion: 0.23
Nodes (9): _case(), _criterion(), _exam(), Any, Primeiro lote de expansão: emergências cardiovasculares de maior complexidade., _safety(), _source(), formatted_public_title() (+1 more)

### Community 17 - "build_question_catalog.py"
Cohesion: 0.40
Nodes (9): Path, classify_topic(), load_questions(), main(), normalize(), plain_text(), Any, Converte um HTML de questões em um catálogo limpo e auditável do MedSync. O… (+1 more)

### Community 18 - "primary_care_catalog.py"
Cohesion: 0.33
Nodes (9): _case(), _criterion(), _exam(), _outcomes(), Any, Casos introdutórios e rubricas para situações frequentes na atenção primária., _rubric(), _safety() (+1 more)

### Community 19 - "setup_agent_skills.py"
Cohesion: 0.42
Nodes (9): download_local_files(), git_blob_sha1(), graphify_tool_matches(), install_local_tools(), load_lock(), main(), verify_file(), verify_local_files() (+1 more)

### Community 20 - "clinical_cases_batch_two.py"
Cohesion: 0.33
Nodes (7): _case(), _criterion(), _exam(), Any, Segundo lote de expansão, calibrado para dificuldade intermediária., _safety(), _source()

### Community 21 - "case_catalog.py"
Cohesion: 0.50
Nodes (3): clinical_case_exists(), get_clinical_case(), Catálogo clínico legado enquanto os casos migram para o banco de dados.

### Community 22 - "clinical_feedback_batch_final.py"
Cohesion: 0.40
Nodes (3): Any, Lote final de rubricas estruturadas para casos clínicos legados., _source()

### Community 24 - "clinical_feedback_batch_four.py"
Cohesion: 0.50
Nodes (3): Any, Quarto lote de rubricas estruturadas para casos clínicos legados., _source()

### Community 25 - "clinical_feedback_batch_three.py"
Cohesion: 0.50
Nodes (3): Any, Terceiro lote de rubricas estruturadas para casos clínicos legados., _source()

### Community 26 - "clinical_feedback_batch_two.py"
Cohesion: 0.50
Nodes (3): Any, Segundo lote de rubricas estruturadas para casos clínicos legados., _source()

### Community 27 - "vital_signs.py"
Cohesion: 0.67
Nodes (3): extract_vital_signs(), _item(), Extrai sinais vitais documentados sem inventar dados ausentes.

### Community 38 - "Simulação Clínica 2.2"
Cohesion: 0.12
Nodes (15): Consequências educacionais, Distribuição da pontuação, Estratégia de implantação, Estrutura padronizada do feedback, Princípios do avaliador, Propósito, Simulação Clínica 2.2, Tom de voz da Synapse (+7 more)

### Community 42 - "Eficiência operacional da Synapse"
Cohesion: 0.20
Nodes (9): Arquivos principais, Comparativo de 25 casos, Contexto compacto, Eficiência operacional da Synapse, Escopo desta versão, Publicação e verificação, Separação e roteamento de modelos, Telemetria e painel (+1 more)

### Community 47 - "Homologação clínica — lote 2"
Cohesion: 0.22
Nodes (8): Caso 33 — dor precordial e perda de consciência, Caso 36 — febre, diarreia e piora clínica, Caso 38 — dispneia intensa e tosse, Caso 39 — sintomas urinários progressivos, Caso 40 — febre, disúria e dor lombar, Critérios obrigatórios de homologação, Homologação clínica — lote 2, Registro do revisor

### Community 49 - "Repertório de IA do MedSync — API"
Cohesion: 0.29
Nodes (6): Antigravity, Configuração local, Distribuição das quatro skills, Quando usar, Repertório de IA do MedSync — API, Segurança e atualização

### Community 50 - "Base técnica do MedSync"
Cohesion: 0.29
Nodes (6): Base técnica do MedSync, Conteúdo clínico, Migrações, Módulos atuais, Objetivo, Próximas entregas da Etapa 1

### Community 53 - "Rubricas Clínicas 2.0"
Cohesion: 0.33
Nodes (5): Estrutura obrigatória, Primeiro lote, Processo editorial recomendado, Regra de segurança, Rubricas Clínicas 2.0

### Community 54 - "🧠 Synapse Multi-LLM 5-Core — Guia de Arquitetura e Ativação"
Cohesion: 0.33
Nodes (5): 🛠️ Como Ativar no `.env`, ⚡ Como Funciona a Ativação Plug & Play, 🧪 Como Testar a Conexão, 🔑 Onde Obter as Chaves de API e Custos Médios, 🧠 Synapse Multi-LLM 5-Core — Guia de Arquitetura e Ativação

### Community 56 - "Não publicado"
Cohesion: 0.40
Nodes (4): Adicionado, Alterado, Changelog, Não publicado

## Knowledge Gaps
- **81 isolated node(s):** `10. Regras para a explicação`, `11. Achados-chave`, `12. Regras para imagens e licenças`, `13. Limites de inferência clínica`, `14. Diversidade dentro do lote` (+76 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 221 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `models.py`, `test_api.py`, `payments.py`, `main.py`, `questions.py`, `users.py`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Why does `prepare_database()` connect `main.py` to `build_question_catalog.py`, `clinical_content.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `SimulationSubmission` connect `evaluation.py` to `models.py`, `test_api.py`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 77 inferred relationships involving `User` (e.g. with `academic_analytics()` and `admin_create_announcement()`) actually correct?**
  _`User` has 77 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SimulationSubmission` (e.g. with `finalizar_simulacao()` and `_legacy_payload()`) actually correct?**
  _`SimulationSubmission` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `ClinicalCase` (e.g. with `admin_list_cases()` and `admin_update_case()`) actually correct?**
  _`ClinicalCase` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `10. Regras para a explicação`, `11. Achados-chave`, `12. Regras para imagens e licenças` to the rest of the system?**
  _81 weakly-connected nodes found - possible documentation gaps or missing edges._