# Graph Report - medsync-api-quality-block  (2026-09-09)

## Corpus Check
- 133 files · ~143,839 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1181 nodes · 2906 edges · 74 communities (53 shown, 5 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 294 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3652238e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- evaluation.py
- simulations.py
- schemas.py
- MedSync — Diretriz Oficial para Criação de Desafios Visuais
- test_api.py
- payments.py
- User
- error_notebook.py
- questions.py
- synapse_providers.py
- field_validator
- main.py
- canonical_hashes
- question_catalog_audit.py
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
- test_question_catalog_v2.py
- Simulação Clínica 2.2
- Eficiência operacional da Synapse
- routers/__init__.py
- execute
- security.py
- Documentação Técnica: Catálogo v2 e Atualização Consolidada do Banco de Questões MedSync
- Homologação clínica — lote 2
- scripts/__init__.py
- Repertório de IA do MedSync — API
- Base técnica do MedSync
- services/__init__.py
- clinical_content.py
- Rubricas Clínicas 2.0
- 🧠 Synapse Multi-LLM 5-Core — Guia de Arquitetura e Ativação
- users.py
- Não publicado
- models.py
- ClinicalRubric
- test_evaluation.py
- ExamQuestion
- Instruções para agentes e colaboradores
- Funil de qualidade das questões — versão 1
- taxonomy_normalizer.py
- vital_signs.py
- benchmark_synapse_efficiency.py
- test_visual_questions_catalog.py
- test_question_quality_priority.py
- Escala do controle de qualidade das questões — versão 1
- EmailVerificationResend
- AdminClinicalCaseUpsert

## God Nodes (most connected - your core abstractions)
1. `User` - 107 edges
2. `ExamQuestion` - 65 edges
3. `_register_and_login()` - 51 edges
4. `Base` - 33 edges
5. `SimulationSubmission` - 27 edges
6. `ClinicalCase` - 27 edges
7. `import_catalog()` - 27 edges
8. `evaluate_objective()` - 25 edges
9. `ClinicalRubric` - 23 edges
10. `finalizar_simulacao()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `test_email_verification_can_be_resent_without_account_enumeration()` --uses--> `User`  [INFERRED]
  tests/test_api.py → models.py
- `test_password_recovery_confirms_legacy_unverified_account()` --uses--> `User`  [INFERRED]
  tests/test_api.py → models.py
- `test_registration_requires_and_records_legal_acceptance()` --uses--> `User`  [INFERRED]
  tests/test_api.py → models.py
- `test_integration_frontend_api_flow()` --uses--> `Base`  [INFERRED]
  tests/test_integration_frontend_api.py → database.py
- `isolated_db()` --uses--> `Base`  [INFERRED]
  tests/test_question_catalog_v2.py → database.py

## Import Cycles
- None detected.

## Communities (74 total, 5 thin omitted)

### Community 0 - "evaluation.py"
Cohesion: 0.10
Nodes (46): AIUsageMetrics, answer_simulation_question(), _bounded_env_int(), build_clinical_consequences(), build_compact_feedback_payload(), build_compact_question_payload(), build_exam_rationale_feedback(), ClinicalConsequences (+38 more)

### Community 1 - "simulations.py"
Cohesion: 0.12
Nodes (34): alias, Header, AIUsageRecord, Progresso, Reserva persistente que torna o envio à Synapse idempotente., Métrica financeira e operacional de cada chamada feita pela Synapse., SimulationRequest, UserActivity (+26 more)

### Community 2 - "schemas.py"
Cohesion: 0.07
Nodes (56): AcademicAnalyticsResponse, AcademicInstitutionMetric, AcademicPeriodMetric, AdminClinicalExam, AdminContentMetric, AdminDailyMetric, AdminFinancialFailure, AdminFinancialOrder (+48 more)

### Community 3 - "MedSync — Diretriz Oficial para Criação de Desafios Visuais"
Cohesion: 0.05
Nodes (36): 10. Regras para a explicação, 11. Achados-chave, 12. Regras para imagens e licenças, 13. Limites de inferência clínica, 14. Diversidade dentro do lote, 15. Proteção do gabarito, 16. Checklist de aprovação do lote, 17. Instrução pronta para outras IAs (+28 more)

### Community 4 - "test_api.py"
Cohesion: 0.06
Nodes (45): _independent_question_explanation(), _register_and_login(), test_academic_analytics_are_restricted_and_aggregated(), test_admin_can_search_moderate_and_generate_question_explanations(), test_admin_operations_manage_content_metrics_announcements_and_export(), test_admin_synapse_usage_aggregates_tokens_cost_latency_and_models(), test_all_cases_are_available_after_final_rubric_review(), test_asaas_checkout_and_webhook_activate_premium_once() (+37 more)

### Community 5 - "payments.py"
Cohesion: 0.12
Nodes (46): AsaasWebhookEvent, PaymentGrant, PaymentOrder, UserEntitlement, _add_months(), _callback(), _card_payload(), _check_payment_availability() (+38 more)

### Community 6 - "User"
Cohesion: 0.09
Nodes (58): Gabaritos dos desafios nativos mantidos somente no servidor., get_db(), HTTPAuthorizationCredentials, get_learning_activity(), get_learning_path(), Announcement, LearningPathProgress, User (+50 more)

### Community 7 - "error_notebook.py"
Cohesion: 0.24
Nodes (20): StudyError, build_review_forecasts(), calculate_review_outcome(), delete_error(), _find_error(), list_due_reviews(), list_my_errors(), list_review_plan() (+12 more)

### Community 8 - "questions.py"
Cohesion: 0.17
Nodes (31): admin_questions(), answer_question(), answered_today(), current_admin(), facet(), get_active_catalog_version(), get_cached_catalog_metadata(), is_premium() (+23 more)

### Community 9 - "synapse_providers.py"
Cohesion: 0.10
Nodes (14): AnthropicProvider, calculate_cost_usd(), ConsensusResult, DeepSeekProvider, _ensure_env_loaded(), GeminiProvider, ProviderUsageMetrics, Any (+6 more)

### Community 10 - "field_validator"
Cohesion: 0.15
Nodes (7): field_validator, QuestionAnswerRequest, TransparentCard, TransparentPayer, UserCreate, _validated_public_url(), SecretStr

### Community 11 - "main.py"
Cohesion: 0.07
Nodes (41): BaseHTTPMiddleware, FastAPI, create_app(), lifespan(), Request, Response, RateLimitMiddleware, RateLimitRule (+33 more)

### Community 12 - "canonical_hashes"
Cohesion: 0.07
Nodes (61): HTMLParser, parametrize, analyze(), legacy_plain(), main(), Offline cause analysis and conditional proposals; no database access., execute_plan(), main() (+53 more)

### Community 13 - "question_catalog_audit.py"
Cohesion: 0.08
Nodes (33): export_snapshot(), Export a fixed, reviewed ID list through the internal read-only auditor., _audit_answer_integrity(), _audit_critical_details(), _audit_pilot_export(), _audit_quality_priority(), _audit_text_integrity(), _batch_size() (+25 more)

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
Nodes (9): classify_topic(), load_questions(), main(), normalize(), plain_text(), Any, Path, Converte um HTML de questões em um catálogo limpo e auditável do MedSync. O… (+1 more)

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

### Community 27 - "test_question_catalog_v2.py"
Cohesion: 0.08
Nodes (41): invalidate_catalog_metadata_cache(), Invalida o cache de metadados em memória., compute_sha256(), import_catalog(), main(), Any, Path, Session (+33 more)

### Community 38 - "Simulação Clínica 2.2"
Cohesion: 0.12
Nodes (15): Consequências educacionais, Distribuição da pontuação, Estratégia de implantação, Estrutura padronizada do feedback, Princípios do avaliador, Propósito, Simulação Clínica 2.2, Tom de voz da Synapse (+7 more)

### Community 42 - "Eficiência operacional da Synapse"
Cohesion: 0.20
Nodes (9): Arquivos principais, Comparativo de 25 casos, Contexto compacto, Eficiência operacional da Synapse, Escopo desta versão, Publicação e verificação, Separação e roteamento de modelos, Telemetria e painel (+1 more)

### Community 44 - "execute"
Cohesion: 0.16
Nodes (23): on_starting(), post_worker_init(), Aplica migrações uma única vez antes de iniciar os workers., Dispara, sem bloquear a API, uma auditoria interna explicitamente solicitada., execute(), expected_state(), main(), manifest_digest() (+15 more)

### Community 45 - "security.py"
Cohesion: 0.18
Nodes (15): create_access_token(), has_active_premium(), hash_password(), Integração da API, Banco Temporário e Importador — Piloto de 100 Questões…, test_integration_frontend_api_flow(), auth_headers(), client(), isolated_db() (+7 more)

### Community 46 - "Documentação Técnica: Catálogo v2 e Atualização Consolidada do Banco de Questões MedSync"
Cohesion: 0.09
Nodes (21): 1. Visão Geral do Sistema, 2.1. Distribuição por Especialidade Médica (Catálogo v2), 2.2. Distribuição por Tipo de Prova e Formato, 2.3. Mídia e Dependência Visual, 2. Métricas Consolidadas do Banco de Dados (`medsync.db`), 3. Histórico dos Lotes Processados e Inseridos, 4.1. Sigilo Autoral e Zero Vazamento de Comentários, 4.2. Prevenção de Fraude (Anti-Cheating) (+13 more)

### Community 47 - "Homologação clínica — lote 2"
Cohesion: 0.22
Nodes (8): Caso 33 — dor precordial e perda de consciência, Caso 36 — febre, diarreia e piora clínica, Caso 38 — dispneia intensa e tosse, Caso 39 — sintomas urinários progressivos, Caso 40 — febre, disúria e dor lombar, Critérios obrigatórios de homologação, Homologação clínica — lote 2, Registro do revisor

### Community 49 - "Repertório de IA do MedSync — API"
Cohesion: 0.29
Nodes (6): Antigravity, Configuração local, Distribuição das quatro skills, Quando usar, Repertório de IA do MedSync — API, Segurança e atualização

### Community 50 - "Base técnica do MedSync"
Cohesion: 0.29
Nodes (6): Base técnica do MedSync, Conteúdo clínico, Migrações, Módulos atuais, Objetivo, Próximas entregas da Etapa 1

### Community 52 - "clinical_content.py"
Cohesion: 0.22
Nodes (20): ClinicalCase, ClinicalExam, main(), _case_from_catalog(), list_published_cases(), datetime, Session, Atualiza apenas as rubricas piloto mantidas e revisadas no código. (+12 more)

### Community 53 - "Rubricas Clínicas 2.0"
Cohesion: 0.33
Nodes (5): Estrutura obrigatória, Primeiro lote, Processo editorial recomendado, Regra de segurança, Rubricas Clínicas 2.0

### Community 54 - "🧠 Synapse Multi-LLM 5-Core — Guia de Arquitetura e Ativação"
Cohesion: 0.33
Nodes (5): 🛠️ Como Ativar no `.env`, ⚡ Como Funciona a Ativação Plug & Play, 🧪 Como Testar a Conexão, 🔑 Onde Obter as Chaves de API e Custos Médios, 🧠 Synapse Multi-LLM 5-Core — Guia de Arquitetura e Ativação

### Community 55 - "users.py"
Cohesion: 0.20
Nodes (22): _as_utc(), login_usuario(), obter_usuario_atual(), datetime, get, post, Session, recuperar_senha() (+14 more)

### Community 56 - "Não publicado"
Cohesion: 0.33
Nodes (5): Adicionado, Alterado, Alterado, Changelog, Não publicado

### Community 57 - "models.py"
Cohesion: 0.20
Nodes (10): Base, DeclarativeBase, QuestionAttempt, QuestionReport, QuestionSourceAlias, main(), purge_batch_files(), purge_non_medical() (+2 more)

### Community 58 - "ClinicalRubric"
Cohesion: 0.21
Nodes (16): ClinicalRubricDefinition, ClinicalRubric, apply_case_payload(), test_existing_pilot_rubric_is_safely_upgraded(), test_fifth_feedback_expansion_batch_is_structured_and_clinically_corrected(), test_final_feedback_batch_is_structured_and_clinically_corrected(), test_first_expansion_batch_is_complete_rich_and_revised(), test_first_feedback_expansion_batch_is_structured_and_clinically_corrected() (+8 more)

### Community 59 - "test_evaluation.py"
Cohesion: 0.31
Nodes (17): build_rule_based_narrative(), evaluate_objective(), SimulationSubmission, test_case_without_essential_exams_rewards_avoiding_low_value_tests(), test_psychiatry_batch_accepts_short_diagnostic_answers(), test_rule_based_feedback_is_driven_by_the_reviewed_rubric(), test_second_expansion_batch_accepts_short_diagnostic_answers(), _case_seven() (+9 more)

### Community 60 - "ExamQuestion"
Cohesion: 0.22
Nodes (14): ExamQuestion, post, question_is_eligible(), regenerate_question_explanation(), report_question(), retry_question_explanation(), QuestionExplanation, _fallback_explanation() (+6 more)

### Community 62 - "Funil de qualidade das questões — versão 1"
Cohesion: 0.29
Nodes (6): Decisão do primeiro lote, Fontes oficiais das anulações, Funil de qualidade das questões — versão 1, Objetivo, Segurança de execução, Semântica dos níveis

### Community 63 - "taxonomy_normalizer.py"
Cohesion: 0.50
Nodes (4): clean_taxonomy_string(), parse_canonical_taxonomy(), scripts/taxonomy_normalizer.py Módulo canônico e centralizado de normalização…, Retorna: (especialidade, tema, subtema, assunto) Todos 100% limpos, sem…

### Community 64 - "vital_signs.py"
Cohesion: 0.67
Nodes (3): extract_vital_signs(), _item(), Extrai sinais vitais documentados sem inventar dados ausentes.

### Community 68 - "benchmark_synapse_efficiency.py"
Cohesion: 0.20
Nodes (14): ClinicalNarrative, model_validator, Pequena camada gerativa aplicada sobre o feedback determinístico., SynapseNarrativeEnhancement, _case_with_current_exams(), _estimated_tokens(), _json_bytes(), _legacy_payload() (+6 more)

### Community 69 - "test_visual_questions_catalog.py"
Cohesion: 0.14
Nodes (16): auth_headers(), client(), isolated_visual_db(), fixture, Suíte de Testes Automatizados — Catálogo de Questões Visuais (Com Imagens)…, Importa lote de amostra de questões visuais e valida persistência canônica., Atomicidade 1: Erro em registro na pré-validação bloqueia antes de qualquer…, Atomicidade 2: Falha pós-flush aciona rollback estrito e zero registros… (+8 more)

### Community 70 - "test_question_quality_priority.py"
Cohesion: 0.27
Nodes (14): prioritize_question(), Any, Priorização determinística do catálogo; não equivale a revisão clínica., Agrega o catálogo inteiro e retém uma fila limitada e reproduzível., Classifica risco operacional sem inferir mérito médico ou gabarito., summarize_priorities(), year_bucket(), row() (+6 more)

### Community 71 - "Escala do controle de qualidade das questões — versão 1"
Cohesion: 0.25
Nodes (7): Auditoria de priorização, Como executar com segurança, Escala do controle de qualidade das questões — versão 1, Gate de correção, Política cronológica aprovada, Ponto de partida, Prioridades

### Community 72 - "EmailVerificationResend"
Cohesion: 0.29
Nodes (4): EmailStr, EmailVerificationResend, PasswordRecoveryRequest, UserLogin

### Community 73 - "AdminClinicalCaseUpsert"
Cohesion: 0.33
Nodes (4): AdminClinicalCaseResponse, AdminClinicalCaseUpsert, _normalized_spoiler_text(), model_validator

## Knowledge Gaps
- **109 isolated node(s):** `RateLimitRule`, `Repertório de IA do MedSync`, `1. Visão Geral do Sistema`, `2.1. Distribuição por Especialidade Médica (Catálogo v2)`, `2.2. Distribuição por Tipo de Prova e Formato` (+104 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 344 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ExamQuestion` connect `ExamQuestion` to `test_api.py`, `test_visual_questions_catalog.py`, `questions.py`, `main.py`, `execute`, `canonical_hashes`, `security.py`, `models.py`, `test_question_catalog_v2.py`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `simulations.py`, `test_api.py`, `payments.py`, `test_visual_questions_catalog.py`, `error_notebook.py`, `questions.py`, `main.py`, `security.py`, `users.py`, `models.py`, `test_question_catalog_v2.py`, `ExamQuestion`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `SimulationSubmission` connect `test_evaluation.py` to `evaluation.py`, `simulations.py`, `benchmark_synapse_efficiency.py`, `test_api.py`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 84 inferred relationships involving `User` (e.g. with `academic_analytics()` and `admin_create_announcement()`) actually correct?**
  _`User` has 84 INFERRED edges - model-reasoned connections that need verification._
- **Are the 41 inferred relationships involving `ExamQuestion` (e.g. with `admin_questions()` and `answer_question()`) actually correct?**
  _`ExamQuestion` has 41 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `Base` (e.g. with `test_integration_frontend_api_flow()` and `isolated_db()`) actually correct?**
  _`Base` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `RateLimitRule`, `Repertório de IA do MedSync`, `1. Visão Geral do Sistema` to the rest of the system?**
  _109 weakly-connected nodes found - possible documentation gaps or missing edges._