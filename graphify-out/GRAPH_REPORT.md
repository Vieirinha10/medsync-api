# Graph Report - medsync-api-quality-block  (2026-09-09)

## Corpus Check
- 136 files · ~145,430 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1207 nodes · 2974 edges · 73 communities (51 shown, 5 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 295 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cba158fe`
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
- models.py
- questions.py
- synapse_providers.py
- invalidate_catalog_metadata_cache
- learning_paths.py
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
- ExamQuestion
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
- import_question_catalog.py
- ClinicalRubric
- database_bootstrap.py
- question_explanations.py
- Instruções para agentes e colaboradores
- Funil de qualidade das questões — versão 1
- taxonomy_normalizer.py
- vital_signs.py
- update_admin_question
- database.py
- test_question_quality_priority.py
- Escala do controle de qualidade das questões — versão 1

## God Nodes (most connected - your core abstractions)
1. `User` - 107 edges
2. `ExamQuestion` - 67 edges
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

## Communities (73 total, 5 thin omitted)

### Community 0 - "evaluation.py"
Cohesion: 0.07
Nodes (77): AIUsageMetrics, answer_simulation_question(), _bounded_env_int(), build_clinical_consequences(), build_compact_feedback_payload(), build_compact_question_payload(), build_exam_rationale_feedback(), build_rule_based_narrative() (+69 more)

### Community 1 - "simulations.py"
Cohesion: 0.08
Nodes (54): alias, Header, HTTPAuthorizationCredentials, Progresso, StudyError, UserActivity, listar_casos_clinicos(), obter_caso_clinico() (+46 more)

### Community 2 - "schemas.py"
Cohesion: 0.08
Nodes (48): AcademicAnalyticsResponse, AcademicInstitutionMetric, AcademicPeriodMetric, AdminClinicalExam, AdminContentMetric, AdminDailyMetric, AdminFinancialFailure, AdminFinancialOrder (+40 more)

### Community 3 - "MedSync — Diretriz Oficial para Criação de Desafios Visuais"
Cohesion: 0.05
Nodes (36): 10. Regras para a explicação, 11. Achados-chave, 12. Regras para imagens e licenças, 13. Limites de inferência clínica, 14. Diversidade dentro do lote, 15. Proteção do gabarito, 16. Checklist de aprovação do lote, 17. Instrução pronta para outras IAs (+28 more)

### Community 4 - "test_api.py"
Cohesion: 0.07
Nodes (39): _register_and_login(), test_academic_analytics_are_restricted_and_aggregated(), test_admin_operations_manage_content_metrics_announcements_and_export(), test_all_cases_are_available_after_final_rubric_review(), test_asaas_checkout_and_webhook_activate_premium_once(), test_checkout_paid_activates_detached_plan_without_double_grant(), test_checkout_rejects_unknown_plan(), test_clinical_simulation_v2_scores_and_persists_structured_feedback() (+31 more)

### Community 5 - "payments.py"
Cohesion: 0.07
Nodes (66): BaseHTTPMiddleware, FastAPI, create_app(), lifespan(), Request, Response, RateLimitMiddleware, RateLimitRule (+58 more)

### Community 6 - "User"
Cohesion: 0.09
Nodes (51): Gabaritos dos desafios nativos mantidos somente no servidor., Announcement, User, VisualChallenge, put, academic_analytics(), admin_create_announcement(), admin_create_case() (+43 more)

### Community 7 - "models.py"
Cohesion: 0.14
Nodes (21): Base, DeclarativeBase, AIUsageRecord, AsaasWebhookEvent, PaymentGrant, QuestionAttempt, QuestionReport, Reserva persistente que torna o envio à Synapse idempotente. (+13 more)

### Community 8 - "questions.py"
Cohesion: 0.11
Nodes (42): answer_question(), answered_today(), current_admin(), facet(), get_cached_catalog_metadata(), is_premium(), list_questions(), organize_filter_metadata() (+34 more)

### Community 9 - "synapse_providers.py"
Cohesion: 0.10
Nodes (14): AnthropicProvider, calculate_cost_usd(), ConsensusResult, DeepSeekProvider, _ensure_env_loaded(), GeminiProvider, ProviderUsageMetrics, Any (+6 more)

### Community 10 - "invalidate_catalog_metadata_cache"
Cohesion: 0.22
Nodes (11): on_starting(), Aplica migrações uma única vez antes de iniciar os workers., invalidate_catalog_metadata_cache(), Invalida o cache de metadados em memória., prepare_database(), Aplica migrações e garante o catálogo clínico uma vez por processo., Executor de inicialização explicitamente habilitado para o funil de qualidade., run_requested_quality_funnel() (+3 more)

### Community 11 - "learning_paths.py"
Cohesion: 0.13
Nodes (23): get_db(), get_learning_activity(), get_learning_path(), LearningPathProgress, complete_learning_activity(), list_learning_paths(), _progress_map(), get (+15 more)

### Community 12 - "canonical_hashes"
Cohesion: 0.07
Nodes (61): HTMLParser, parametrize, analyze(), legacy_plain(), main(), Offline cause analysis and conditional proposals; no database access., execute_plan(), main() (+53 more)

### Community 13 - "question_catalog_audit.py"
Cohesion: 0.07
Nodes (36): post_worker_init(), Dispara, sem bloquear a API, uma auditoria interna explicitamente solicitada., export_snapshot(), Export a fixed, reviewed ID list through the internal read-only auditor., _audit_answer_integrity(), _audit_critical_details(), _audit_pilot_export(), _audit_quality_priority() (+28 more)

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
Cohesion: 0.12
Nodes (22): compute_sha256(), Any, Valida estritamente cada registro contra o contrato canônico do extrator v1.1.…, validate_and_normalize_record(), validate_hash_format(), auth_headers(), client(), isolated_db() (+14 more)

### Community 38 - "Simulação Clínica 2.2"
Cohesion: 0.12
Nodes (15): Consequências educacionais, Distribuição da pontuação, Estratégia de implantação, Estrutura padronizada do feedback, Princípios do avaliador, Propósito, Simulação Clínica 2.2, Tom de voz da Synapse (+7 more)

### Community 42 - "Eficiência operacional da Synapse"
Cohesion: 0.20
Nodes (9): Arquivos principais, Comparativo de 25 casos, Contexto compacto, Eficiência operacional da Synapse, Escopo desta versão, Publicação e verificação, Separação e roteamento de modelos, Telemetria e painel (+1 more)

### Community 44 - "execute"
Cohesion: 0.14
Nodes (34): execute(), expected_state(), main(), manifest_digest(), matches(), normalized(), Aplica o funil editorial revisado com travas, atomicidade e dry-run padrão., Bloqueia e valida todas as linhas antes de realizar qualquer alteração. (+26 more)

### Community 45 - "ExamQuestion"
Cohesion: 0.11
Nodes (25): ExamQuestion, import_catalog(), Path, Importa o catálogo de questões com atomicidade absoluta e idempotência estrita., Executor desabilitado por padrão para a realocação taxonômica revisada., Testes comprobatórios específicos dos bloqueadores v1.5: 1. Inexistência de…, Importa os 100 registros em banco isolado e compara campo a campo os 100…, Testa falha na pré-validação: - O arquivo contém um registro estruturalmente… (+17 more)

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
Nodes (19): ClinicalCase, ClinicalExam, main(), _case_from_catalog(), datetime, Session, Atualiza apenas as rubricas piloto mantidas e revisadas no código., Sincroniza rubricas de expansão respeitando a decisão editorial. (+11 more)

### Community 53 - "Rubricas Clínicas 2.0"
Cohesion: 0.33
Nodes (5): Estrutura obrigatória, Primeiro lote, Processo editorial recomendado, Regra de segurança, Rubricas Clínicas 2.0

### Community 54 - "🧠 Synapse Multi-LLM 5-Core — Guia de Arquitetura e Ativação"
Cohesion: 0.33
Nodes (5): 🛠️ Como Ativar no `.env`, ⚡ Como Funciona a Ativação Plug & Play, 🧪 Como Testar a Conexão, 🔑 Onde Obter as Chaves de API e Custos Médios, 🧠 Synapse Multi-LLM 5-Core — Guia de Arquitetura e Ativação

### Community 55 - "users.py"
Cohesion: 0.10
Nodes (27): EmailStr, field_validator, _as_utc(), login_usuario(), obter_usuario_atual(), datetime, get, post (+19 more)

### Community 56 - "Não publicado"
Cohesion: 0.33
Nodes (5): Adicionado, Alterado, Alterado, Changelog, Não publicado

### Community 57 - "import_question_catalog.py"
Cohesion: 0.24
Nodes (10): QuestionSourceAlias, main(), Session, Executa o rollback atômico e reversível de todas as questões e aliases de uma…, rollback_catalog(), main(), purge_batch_files(), purge_non_medical() (+2 more)

### Community 58 - "ClinicalRubric"
Cohesion: 0.27
Nodes (13): ClinicalRubricDefinition, ClinicalRubric, test_existing_pilot_rubric_is_safely_upgraded(), test_fifth_feedback_expansion_batch_is_structured_and_clinically_corrected(), test_final_feedback_batch_is_structured_and_clinically_corrected(), test_first_expansion_batch_is_complete_rich_and_revised(), test_first_feedback_expansion_batch_is_structured_and_clinically_corrected(), test_fourth_feedback_expansion_batch_is_structured_and_clinically_corrected() (+5 more)

### Community 59 - "database_bootstrap.py"
Cohesion: 0.40
Nodes (4): Prepara o banco antes que a API aceite tráfego., Session, Carga idempotente do catálogo validado de questões., seed_question_content()

### Community 60 - "question_explanations.py"
Cohesion: 0.29
Nodes (8): QuestionExplanation, _fallback_explanation(), generate_question_explanation(), GeneratedAlternativeExplanation, GeneratedQuestionExplanation, BaseModel, model_validator, Gera comentários próprios para questões sem reutilizar material editorial…

### Community 62 - "Funil de qualidade das questões — versão 1"
Cohesion: 0.25
Nodes (7): Decisão do primeiro lote, Fontes oficiais das anulações, Funil de qualidade das questões — versão 1, Objetivo, Realocação taxonômica — segundo manifesto, Segurança de execução, Semântica dos níveis

### Community 63 - "taxonomy_normalizer.py"
Cohesion: 0.50
Nodes (4): clean_taxonomy_string(), parse_canonical_taxonomy(), scripts/taxonomy_normalizer.py Módulo canônico e centralizado de normalização…, Retorna: (especialidade, tema, subtema, assunto) Todos 100% limpos, sem…

### Community 64 - "vital_signs.py"
Cohesion: 0.67
Nodes (3): extract_vital_signs(), _item(), Extrai sinais vitais documentados sem inventar dados ausentes.

### Community 68 - "update_admin_question"
Cohesion: 0.40
Nodes (5): patch, update_admin_question(), update_question_report(), AdminQuestionReportUpdate, AdminQuestionUpdate

### Community 69 - "database.py"
Cohesion: 0.14
Nodes (18): create_access_token(), hash_password(), Integração da API, Banco Temporário e Importador — Piloto de 100 Questões…, test_integration_frontend_api_flow(), Testa Item 6 do Codex: - Configuração de catálogo ativo determina versão…, Testa rigorosamente o Item 3 da auditoria Codex v1.4: - rnd no início da…, test_09_active_catalog_configuration_and_override_protection(), test_12_circular_selection_deterministic_scenarios() (+10 more)

### Community 70 - "test_question_quality_priority.py"
Cohesion: 0.27
Nodes (14): prioritize_question(), Any, Priorização determinística do catálogo; não equivale a revisão clínica., Agrega o catálogo inteiro e retém uma fila limitada e reproduzível., Classifica risco operacional sem inferir mérito médico ou gabarito., summarize_priorities(), year_bucket(), row() (+6 more)

### Community 71 - "Escala do controle de qualidade das questões — versão 1"
Cohesion: 0.20
Nodes (9): Auditoria de priorização, Como executar com segurança, Escala do controle de qualidade das questões — versão 1, Estado pós-reparo de integridade, Gate de correção, Política cronológica aprovada, Ponto de partida, Prioridades (+1 more)

## Knowledge Gaps
- **112 isolated node(s):** `RateLimitRule`, `Repertório de IA do MedSync`, `1. Visão Geral do Sistema`, `2.1. Distribuição por Especialidade Médica (Catálogo v2)`, `2.2. Distribuição por Tipo de Prova e Formato` (+107 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 351 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ExamQuestion` connect `ExamQuestion` to `update_admin_question`, `test_api.py`, `database.py`, `models.py`, `questions.py`, `test_question_catalog_v2.py`, `invalidate_catalog_metadata_cache`, `learning_paths.py`, `execute`, `canonical_hashes`, `import_question_catalog.py`, `database_bootstrap.py`, `question_explanations.py`?**
  _High betweenness centrality (0.163) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `simulations.py`, `update_admin_question`, `payments.py`, `database.py`, `models.py`, `questions.py`, `test_api.py`, `learning_paths.py`, `ExamQuestion`, `users.py`, `test_question_catalog_v2.py`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `SimulationSubmission` connect `evaluation.py` to `simulations.py`, `test_api.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 84 inferred relationships involving `User` (e.g. with `academic_analytics()` and `admin_create_announcement()`) actually correct?**
  _`User` has 84 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `ExamQuestion` (e.g. with `admin_questions()` and `answer_question()`) actually correct?**
  _`ExamQuestion` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `Base` (e.g. with `test_integration_frontend_api_flow()` and `isolated_db()`) actually correct?**
  _`Base` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `RateLimitRule`, `Repertório de IA do MedSync`, `1. Visão Geral do Sistema` to the rest of the system?**
  _112 weakly-connected nodes found - possible documentation gaps or missing edges._