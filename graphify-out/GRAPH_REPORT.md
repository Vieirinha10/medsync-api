# Graph Report - medsync-api-taxonomy  (2026-09-10)

## Corpus Check
- 152 files · ~155,078 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1394 nodes · 3417 edges · 83 communities (58 shown, 6 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 321 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f9cc3b04`
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
- ExamQuestion
- synapse_providers.py
- execute
- learning_paths.py
- canonical_hashes
- test_question_catalog_audit.py
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
- test_visual_questions_catalog.py
- Simulação Clínica 2.2
- Eficiência operacional da Synapse
- routers/__init__.py
- apply_question_quality_clinical_review.py
- classify_content_taxonomy.py
- Documentação Técnica: Catálogo v2 e Atualização Consolidada do Banco de Questões MedSync
- Homologação clínica — lote 2
- scripts/__init__.py
- Repertório de IA do MedSync — API
- Base técnica do MedSync
- services/__init__.py
- ClinicalCase
- Rubricas Clínicas 2.0
- 🧠 Synapse Multi-LLM 5-Core — Guia de Arquitetura e Ativação
- users.py
- Não publicado
- question_catalog_audit.py
- field_validator
- error_notebook.py
- test_question_visual_audit.py
- Instruções para agentes e colaboradores
- Funil de qualidade das questões — versão 1
- taxonomy_normalizer.py
- Taxonomia unificada de conteúdo — MedSync
- content.py
- _Result
- test_question_quality_priority.py
- Escala do controle de qualidade das questões — versão 1
- EmailVerificationResend
- test_question_catalog_v2.py
- export_question_quality_snapshot.py
- import_catalog
- test_integration_frontend_api.py
- validate_and_normalize_record
- import_question_catalog.py
- obter_meu_progresso
- compute_sha256

## God Nodes (most connected - your core abstractions)
1. `User` - 108 edges
2. `ExamQuestion` - 81 edges
3. `_register_and_login()` - 51 edges
4. `Base` - 37 edges
5. `ClinicalCase` - 31 edges
6. `SimulationSubmission` - 27 edges
7. `import_catalog()` - 27 edges
8. `evaluate_objective()` - 25 edges
9. `ClinicalRubric` - 23 edges
10. `run_question_catalog_audit()` - 23 edges

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

## Communities (83 total, 6 thin omitted)

### Community 0 - "evaluation.py"
Cohesion: 0.07
Nodes (77): AIUsageMetrics, answer_simulation_question(), _bounded_env_int(), build_clinical_consequences(), build_compact_feedback_payload(), build_compact_question_payload(), build_exam_rationale_feedback(), build_rule_based_narrative() (+69 more)

### Community 1 - "models.py"
Cohesion: 0.11
Nodes (39): alias, Base, get_db(), DeclarativeBase, Header, HTTPAuthorizationCredentials, AIUsageRecord, AsaasWebhookEvent (+31 more)

### Community 2 - "schemas.py"
Cohesion: 0.07
Nodes (58): AcademicAnalyticsResponse, AcademicInstitutionMetric, AcademicPeriodMetric, AdminClinicalExam, AdminContentMetric, AdminDailyMetric, AdminFinancialFailure, AdminFinancialOrder (+50 more)

### Community 3 - "MedSync — Diretriz Oficial para Criação de Desafios Visuais"
Cohesion: 0.05
Nodes (36): 10. Regras para a explicação, 11. Achados-chave, 12. Regras para imagens e licenças, 13. Limites de inferência clínica, 14. Diversidade dentro do lote, 15. Proteção do gabarito, 16. Checklist de aprovação do lote, 17. Instrução pronta para outras IAs (+28 more)

### Community 4 - "test_api.py"
Cohesion: 0.06
Nodes (61): Gabaritos dos desafios nativos mantidos somente no servidor., ClinicalRubricDefinition, ClinicalRubric, _independent_question_explanation(), _register_and_login(), test_academic_analytics_are_restricted_and_aggregated(), test_admin_can_search_moderate_and_generate_question_explanations(), test_admin_operations_manage_content_metrics_announcements_and_export() (+53 more)

### Community 5 - "payments.py"
Cohesion: 0.08
Nodes (58): PaymentGrant, PaymentOrder, UserEntitlement, _add_months(), _callback(), _card_payload(), _check_payment_availability(), _checkout_payload() (+50 more)

### Community 6 - "User"
Cohesion: 0.19
Nodes (30): Announcement, User, put, academic_analytics(), admin_create_announcement(), admin_create_case(), admin_list_announcements(), admin_list_cases() (+22 more)

### Community 8 - "ExamQuestion"
Cohesion: 0.06
Nodes (80): ExamQuestion, QuestionAttempt, QuestionReport, admin_questions(), answer_question(), answered_today(), current_admin(), facet() (+72 more)

### Community 9 - "synapse_providers.py"
Cohesion: 0.10
Nodes (14): AnthropicProvider, calculate_cost_usd(), ConsensusResult, DeepSeekProvider, _ensure_env_loaded(), GeminiProvider, ProviderUsageMetrics, Any (+6 more)

### Community 10 - "execute"
Cohesion: 0.19
Nodes (19): execute(), expected_state(), main(), manifest_digest(), _matches(), _normalized(), Any, Coloca em quarentena questões P0 dependentes de imagem sem marcação visual. (+11 more)

### Community 11 - "learning_paths.py"
Cohesion: 0.35
Nodes (9): get_learning_activity(), get_learning_path(), LearningPathProgress, complete_learning_activity(), list_learning_paths(), _progress_map(), get, post (+1 more)

### Community 12 - "canonical_hashes"
Cohesion: 0.07
Nodes (60): parametrize, analyze(), legacy_plain(), main(), Offline cause analysis and conditional proposals; no database access., execute_plan(), main(), matches() (+52 more)

### Community 13 - "test_question_catalog_audit.py"
Cohesion: 0.11
Nodes (15): Inicia a auditoria uma vez por instância quando o gatilho está ativo., start_requested_audit(), _Connection, test_audit_enforces_read_only_transaction_and_emits_sections(), test_critical_details_mode_is_read_only_and_emits_empty_summary(), test_json_value_normalizes_postgres_decimal(), test_pilot_export_roundtrip_and_bounded_queries(), test_quality_hold_snapshot_mode_is_read_only() (+7 more)

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

### Community 27 - "test_visual_questions_catalog.py"
Cohesion: 0.14
Nodes (16): auth_headers(), client(), isolated_visual_db(), fixture, Suíte de Testes Automatizados — Catálogo de Questões Visuais (Com Imagens)…, Importa lote de amostra de questões visuais e valida persistência canônica., Atomicidade 1: Erro em registro na pré-validação bloqueia antes de qualquer…, Atomicidade 2: Falha pós-flush aciona rollback estrito e zero registros… (+8 more)

### Community 38 - "Simulação Clínica 2.2"
Cohesion: 0.12
Nodes (15): Consequências educacionais, Distribuição da pontuação, Estratégia de implantação, Estrutura padronizada do feedback, Princípios do avaliador, Propósito, Simulação Clínica 2.2, Tom de voz da Synapse (+7 more)

### Community 42 - "Eficiência operacional da Synapse"
Cohesion: 0.20
Nodes (9): Arquivos principais, Comparativo de 25 casos, Contexto compacto, Eficiência operacional da Synapse, Escopo desta versão, Publicação e verificação, Separação e roteamento de modelos, Telemetria e painel (+1 more)

### Community 44 - "apply_question_quality_clinical_review.py"
Cohesion: 0.07
Nodes (62): on_starting(), post_worker_init(), Aplica migrações uma única vez antes de iniciar os workers., Dispara, sem bloquear a API, uma auditoria interna explicitamente solicitada., execute(), expected_state(), main(), manifest_digest() (+54 more)

### Community 45 - "classify_content_taxonomy.py"
Cohesion: 0.07
Nodes (56): ContentTaxonomyClassification, Classificação semântica versionada sem alterar o conteúdo de origem., Checkpoint retomável e métricas de uma classificação em massa., TaxonomyClassificationRun, _alternative_payload(), case_item(), challenge_item(), chunks() (+48 more)

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

### Community 52 - "ClinicalCase"
Cohesion: 0.17
Nodes (23): ClinicalCase, ClinicalExam, main(), _case_from_catalog(), list_published_cases(), datetime, Session, Atualiza apenas as rubricas piloto mantidas e revisadas no código. (+15 more)

### Community 53 - "Rubricas Clínicas 2.0"
Cohesion: 0.33
Nodes (5): Estrutura obrigatória, Primeiro lote, Processo editorial recomendado, Regra de segurança, Rubricas Clínicas 2.0

### Community 54 - "🧠 Synapse Multi-LLM 5-Core — Guia de Arquitetura e Ativação"
Cohesion: 0.33
Nodes (5): 🛠️ Como Ativar no `.env`, ⚡ Como Funciona a Ativação Plug & Play, 🧪 Como Testar a Conexão, 🔑 Onde Obter as Chaves de API e Custos Médios, 🧠 Synapse Multi-LLM 5-Core — Guia de Arquitetura e Ativação

### Community 55 - "users.py"
Cohesion: 0.19
Nodes (23): _as_utc(), login_usuario(), obter_usuario_atual(), datetime, get, post, Session, recuperar_senha() (+15 more)

### Community 56 - "Não publicado"
Cohesion: 0.33
Nodes (5): Adicionado, Alterado, Alterado, Changelog, Não publicado

### Community 57 - "question_catalog_audit.py"
Cohesion: 0.17
Nodes (25): export_snapshot(), _audit_answer_integrity(), _audit_critical_details(), _audit_pilot_export(), _audit_quality_hold_snapshot(), _audit_quality_priority(), _audit_quality_visual(), _audit_taxonomy_inventory() (+17 more)

### Community 58 - "field_validator"
Cohesion: 0.15
Nodes (7): field_validator, QuestionAnswerRequest, TransparentCard, TransparentPayer, UserCreate, _validated_public_url(), SecretStr

### Community 59 - "error_notebook.py"
Cohesion: 0.09
Nodes (39): BaseHTTPMiddleware, FastAPI, create_app(), lifespan(), Request, Response, RateLimitMiddleware, RateLimitRule (+31 more)

### Community 60 - "test_question_visual_audit.py"
Cohesion: 0.14
Nodes (15): audit_batch(), _ImageParser, inspect_markup(), load_batch_manifest(), manifest_digest(), Any, HTMLParser, Path (+7 more)

### Community 62 - "Funil de qualidade das questões — versão 1"
Cohesion: 0.22
Nodes (8): Decisão do primeiro lote, Fontes oficiais das anulações, Funil de qualidade das questões — versão 1, Objetivo, Realocação taxonômica — segundo manifesto, Revisão clínica da quarentena, Segurança de execução, Semântica dos níveis

### Community 63 - "taxonomy_normalizer.py"
Cohesion: 0.50
Nodes (4): clean_taxonomy_string(), parse_canonical_taxonomy(), scripts/taxonomy_normalizer.py Módulo canônico e centralizado de normalização…, Retorna: (especialidade, tema, subtema, assunto) Todos 100% limpos, sem…

### Community 64 - "Taxonomia unificada de conteúdo — MedSync"
Cohesion: 0.22
Nodes (8): Critérios mínimos para publicação, Estados editoriais, Hierarquia principal, Metadados para trilhas, Objetivo, Operação, Processo de classificação, Taxonomia unificada de conteúdo — MedSync

### Community 68 - "content.py"
Cohesion: 0.24
Nodes (16): VisualChallenge, admin_create_challenge(), admin_update_challenge(), apply_challenge_payload(), answer_visual_challenge(), list_active_announcements(), list_dynamic_challenges(), get (+8 more)

### Community 69 - "_Result"
Cohesion: 0.25
Nodes (3): _Result, test_full_scan_keyset_read_only_and_rolls_back_on_failure(), test_snapshot_transport_exact_and_database_read_only()

### Community 70 - "test_question_quality_priority.py"
Cohesion: 0.26
Nodes (15): prioritize_question(), Any, Priorização determinística do catálogo; não equivale a revisão clínica., Agrega o catálogo inteiro e retém uma fila limitada e reproduzível., Classifica risco operacional sem inferir mérito médico ou gabarito., summarize_priorities(), year_bucket(), row() (+7 more)

### Community 71 - "Escala do controle de qualidade das questões — versão 1"
Cohesion: 0.18
Nodes (10): Auditoria de priorização, Como executar com segurança, Escala do controle de qualidade das questões — versão 1, Estado pós-reparo de integridade, Gate de correção, Política cronológica aprovada, Ponto de partida, Primeiro lote P0 (+2 more)

### Community 72 - "EmailVerificationResend"
Cohesion: 0.29
Nodes (4): EmailStr, EmailVerificationResend, PasswordRecoveryRequest, UserLogin

### Community 73 - "test_question_catalog_v2.py"
Cohesion: 0.17
Nodes (14): invalidate_catalog_metadata_cache(), Invalida o cache de metadados em memória., auth_headers(), client(), isolated_db(), fixture, Suíte de Testes Automatizados — Novo Catálogo de Questões MedSync (v1.2)…, Testa o ciclo completo da migração Alembic (upgrade -> downgrade -> upgrade) em… (+6 more)

### Community 77 - "import_catalog"
Cohesion: 0.15
Nodes (13): import_catalog(), Path, Importa o catálogo de questões com atomicidade absoluta e idempotência estrita., Importa os 100 registros em banco isolado e compara campo a campo os 100…, Testa falha na pré-validação: - O arquivo contém um registro estruturalmente…, Testa falha durante a persistência após db.flush(): - Todos os registros passam…, Testa Item 11 do Codex: - O aluno abre a questão: enunciado e alternativas sem…, Testa Item 1 da auditoria Codex v1.3: - Com QUESTION_CATALOG_ACTIVE_VERSION=v2;… (+5 more)

### Community 78 - "test_integration_frontend_api.py"
Cohesion: 0.27
Nodes (10): create_access_token(), hash_password(), Integração da API, Banco Temporário e Importador — Piloto de 100 Questões…, test_integration_frontend_api_flow(), Testes comprobatórios específicos dos bloqueadores v1.5: 1. Inexistência de…, Testa Item 6 do Codex: - Configuração de catálogo ativo determina versão…, Testa rigorosamente o Item 3 da auditoria Codex v1.4: - rnd no início da…, test_09_active_catalog_configuration_and_override_protection() (+2 more)

### Community 79 - "validate_and_normalize_record"
Cohesion: 0.25
Nodes (9): Any, Valida estritamente cada registro contra o contrato canônico do extrator v1.1.…, validate_and_normalize_record(), validate_hash_format(), Testa Item 2 do Codex: - hash ausente -> rejeitado com erro; - hash malformado…, Testa Item 3 do Codex: - ausência do campo is_correct; - valor não-booleano; -…, test_06_hashes_mandatory_presence_and_recalculation(), test_07_explicit_answer_binding_without_inference() (+1 more)

### Community 80 - "import_question_catalog.py"
Cohesion: 0.47
Nodes (5): QuestionSourceAlias, main(), Session, Executa o rollback atômico e reversível de todas as questões e aliases de uma…, rollback_catalog()

### Community 81 - "obter_meu_progresso"
Cohesion: 0.40
Nodes (5): obter_meu_progresso(), delete, get, Session, resetar_meu_progresso()

### Community 82 - "compute_sha256"
Cohesion: 0.40
Nodes (5): compute_sha256(), Valida a preservação integral da v1 em uma coleção sintética controlada: -…, Testa: 1. Idempotência sem alterações: informa unchanged_count = 100 e…, test_04_v1_preservation_and_collision_prevention(), test_05_idempotency_detects_unchanged_and_rejects_hash_conflict()

## Knowledge Gaps
- **121 isolated node(s):** `RateLimitRule`, `Repertório de IA do MedSync`, `1. Visão Geral do Sistema`, `2.1. Distribuição por Especialidade Médica (Catálogo v2)`, `2.2. Distribuição por Tipo de Prova e Formato` (+116 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 402 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ExamQuestion` connect `ExamQuestion` to `models.py`, `test_api.py`, `test_visual_questions_catalog.py`, `test_question_catalog_v2.py`, `execute`, `apply_question_quality_clinical_review.py`, `classify_content_taxonomy.py`, `canonical_hashes`, `import_catalog`, `import_question_catalog.py`, `test_integration_frontend_api.py`, `compute_sha256`, `error_notebook.py`?**
  _High betweenness centrality (0.163) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `models.py`, `content.py`, `payments.py`, `test_api.py`, `ExamQuestion`, `test_question_catalog_v2.py`, `test_visual_questions_catalog.py`, `learning_paths.py`, `test_integration_frontend_api.py`, `obter_meu_progresso`, `users.py`, `error_notebook.py`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `TransparentCard` connect `field_validator` to `schemas.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 85 inferred relationships involving `User` (e.g. with `academic_analytics()` and `admin_create_announcement()`) actually correct?**
  _`User` has 85 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `ExamQuestion` (e.g. with `admin_questions()` and `answer_question()`) actually correct?**
  _`ExamQuestion` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `Base` (e.g. with `test_integration_frontend_api_flow()` and `isolated_db()`) actually correct?**
  _`Base` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `RateLimitRule`, `Repertório de IA do MedSync`, `1. Visão Geral do Sistema` to the rest of the system?**
  _121 weakly-connected nodes found - possible documentation gaps or missing edges._