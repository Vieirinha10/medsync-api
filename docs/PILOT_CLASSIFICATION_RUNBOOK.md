# Runbook Operacional: Calibração da Taxonomia Médica MedSync (Fase 2)

Este documento descreve os procedimentos de execução, validação, auditoria e retomada do motor de calibração taxonômica semântica do catálogo MedSync.

---

## 1. Arquitetura e Contrato de Execução

* **Modelo Operacional:** Camada sombra isolada em tabelas dedicadas (`content_taxonomy_classifications`, `taxonomy_classification_runs`, `medical_taxonomy_versions`).
* **Proteção de Produção:** Zero mutações na tabela `exam_questions`. Os enunciados, alternativas, gabaritos e explicações de produção permanecem 100% inalterados.
* **Zero API Paga:** A calibração é executada dentro do contexto interativo com a assinatura do assistente ou via runner local com mocks/regras determinísticas, sem invocar endpoints faturados externamente.
* **Isolamento de Filtros:** Nenhuma proposta taxonômica é publicada automaticamente nos filtros públicos de estudantes antes de auditoria humana completa.

---

## 2. Hash Canônico Único (`compute_content_source_hash`)

Tanto o seletor de amostragem (`scripts/build_pilot_dataset.py`) quanto o executor de lotes (`services/taxonomy_state_machine.py`) compartilham rigorosamente a mesma função de hash SHA-256 baseada em 10 campos:

1. `content_id`
2. `content_type`
3. `cabecalho`
4. `enunciado`
5. `alternativas` (normalizadas)
6. `identificador do gabarito`
7. `especialidade atual`
8. `tema atual`
9. `assunto atual`
10. `dificuldade atual`

Qualquer alteração em enunciado, opções ou gabarito invalida o hash imediatamente (`StaleContentHashError`), impedindo associação de classificações desatualizadas.

---

## 3. Checkpoint Durável e Atômico

* O checkpoint é gravado em disco no caminho `data/pilot_checkpoint.json`.
* **Atomicidade:** A escrita ocorre inicialmente em arquivo temporário (`.tmp`) no mesmo diretório, seguida de flush do sistema operacional e substituição atômica via `os.replace`.
* **Campos Persistidos:**
  * `run_id`: Identificador da execução.
  * `status`: Estado atual (`executando`, `pausada`, `concluida`).
  * `completed_ids`: Lista de IDs já finalizados.
  * `last_id`: Último ID processado com sucesso.
  * `processed_count`: Total de itens concluídos.
  * `verified_count`: Total com status `verified`.
  * `review_count`: Total enviado para `requires_review`.
  * `failed_count`: Total com erro temporário.
  * `high_effort_count`: Total que demandou reanálise aprofundada.
  * `hashes`: Mapeamento de `content_id -> source_hash`.
  * `last_checkpoint_at`: Timestamp ISO da última gravação.

---

## 4. Ciclo de Execução em Lotes de 10 Questões

O executor opera em lotes atômicos de 10 itens (`chunk_size = 10`):

1. **Leitura do Checkpoint:** Carrega o estado em disco e ignora qualquer questão já registrada em `completed_ids`.
2. **Passe Primário:** Classificação médica inicial gerando Especialidade, Tema, Assunto, Objetivos, Competências e Confiança.
3. **Passe de Verificação Independente:** Avaliação cega sem aceitar a primeira resposta por padrão.
4. **Detecção de Alta Complexidade (High Effort):**
   * Discordância entre classificador e verificador;
   * Confiança final < 0.85;
   * Assunto genérico detectado;
   * Ambiguidade clínica manifesta.
5. **Reanálise Aprofundada:** Segunda rodada de inferência clínica e nova checagem de consistência.
6. **Validação contra Registro Canônico:** Validação de níveis semânticos distintos (rejeitando repetições como `Cardiologia -> Cardiologia`) e classificação como `canonical` ou `provisional` via `data/taxonomy_registry_pilot_v0_1.json`.
7. **Persistência Incremental:** Anexação em `data/pilot_classifications_100.jsonl` e gravação atômica do checkpoint no disco.

---

## 5. Instruções de Retomada Após Interrupção

Caso ocorra interrupção por rede, limite temporário de requisições ou reinicialização da máquina:

1. Execute novamente o runner apontando para o mesmo `run_id` e arquivo de checkpoint:
   ```bash
   python -m scripts.run_pilot_calibration --resume
   ```
2. O runner detecta automaticamente os IDs presentes em `completed_ids` no arquivo `data/pilot_checkpoint.json` e retoma imediatamente a partir do lote seguinte, garantindo **zero reprocessamento**.

---

## 6. Resolução do Bloqueio de Dados (Catálogo de 226k Questões)

* **Diagnóstico Atual:** A base local SQLite (`medsync.db`) contém 2.811 questões legadas, todas classificadas sob a especialidade de Cirurgia.
* **Diretriz de Segurança:** Conforme as restrições contratuais do projeto, é proibido substituir a amostra por questões exclusivamente cirúrgicas ou utilizar fixtures de teste sintéticas.
* **Ação Necessária:** Para realizar a amostragem real de 100 questões com >= 15 especialidades e <= 10 por especialidade, deve-se disponibilizar no arquivo `.env` uma `DATABASE_URL` apontando para o banco de dados PostgreSQL do catálogo completo (em modo estritamente `READ ONLY`), ou fornecer um dump consolidado não-sintético do catálogo v2.
