# Escala do controle de qualidade das questões — versão 1

## Ponto de partida

O catálogo v2 contém 226.792 questões que passaram por auditoria estrutural. Essa
condição não representa validação científica individual. O primeiro manifesto de
Hematologia processou 209 decisões: 157 permaneceram ativas, 50 foram colocadas
em revisão e 2 anuladas foram mantidas fora da entrega aos alunos.

## Política cronológica aprovada

| Faixa | Tratamento |
|---|---|
| 2020–2026 | MedSync Atual; priorizar revisão científica por risco e exposição |
| 2016–2019 | MedSync Clássicas Revisadas; liberar somente após revisão técnica |
| Antes de 2016 | Candidatas a arquivo; não arquivar automaticamente |

## Auditoria de priorização

O modo `quality_priority` faz uma varredura somente leitura e combina:

- quarentenas e flags editoriais já existentes;
- sinalizações da auditoria de integridade textual ainda abertas;
- conflitos de gabarito, truncamentos e necessidade de fonte oficial;
- dependência de imagem e situação documental;
- sensibilidade temporal do conteúdo;
- relatos abertos e exposição aos alunos;
- política cronológica aprovada.

O resultado contém agregados por prioridade, ação, faixa cronológica e
especialidade, além de uma fila limitada aos itens mais urgentes. A leitura é
feita em fluxo, em páginas de 1.000 registros, para não manter o catálogo inteiro
na memória do serviço. Enunciados, alternativas e gabaritos não são emitidos nos
logs.

### Prioridades

| Nível | Uso |
|---|---|
| `p0_critica` | Quarentena, conflito, truncamento, relato ou combinação de riscos |
| `p1_alta` | Integridade, documento, imagem ou candidato a arquivo |
| `p2_media` | Clássicas e conteúdo que exige revisão programada |
| `p3_rotina` | Base estrutural sem sinal adicional |
| `excluida` | Anulação já confirmada; nunca retorna à fila de publicação |

## Como executar com segurança

Defina um identificador único e o modo no ambiente do serviço:

```text
QUESTION_CATALOG_AUDIT_RUN_ID=quality-priority-YYYYMMDD
QUESTION_CATALOG_AUDIT_MODE=quality_priority
QUESTION_QUALITY_PRIORITY_TOP_LIMIT=500
```

A transação usa `REPEATABLE READ`, é marcada `READ ONLY` no PostgreSQL e sempre
termina em rollback. A execução gera diagnóstico; não corrige o banco.

## Gate de correção

1. Resolver primeiro as 50 pendências únicas de Hematologia.
2. Revisar a fila P0 e depois P1, por especialidade e objetivo educacional.
3. Confirmar fontes oficiais para gabarito, anulação e conteúdo sensível ao tempo.
4. Gerar um novo manifesto com snapshot fresco, hashes e taxonomia esperada.
5. Executar dry-run, backup, aplicação atômica e verificação pós-escrita.
6. Manter explicações como `PENDING` até revisão editorial própria.

Nenhuma classificação de risco autoriza alteração automática de conteúdo,
alternativas, gabarito, taxonomia ou situação de publicação.

## Estado pós-reparo de integridade

Os 1.321 IDs do primeiro diagnóstico eram um retrato histórico, não um passivo
permanente. Em 8 de setembro de 2026 foram aplicados e verificados dois lotes
atômicos: 1.304 alinhamentos determinísticos e 16 normalizações residuais de
codificação. A auditoria fresca
`text-integrity-post-repair-20260909-1504` examinou as 226.740 questões v2
publicadas e encontrou **zero sinalizações**. O arquivo local de IDs foi
atualizado para esse resultado, impedindo que o priorizador volte a contar os
reparos concluídos como P0.

## Segundo manifesto: realocação taxonômica

O manifesto `question_quality_taxonomy_resolution_manifest.json` resolve as 19
questões que haviam sido reconhecidas como externas à Hematologia. Ele altera
somente `especialidade`, `assunto`, `tema`, `subtema` e metadados do funil:

- 17 questões sem outra pendência retornam ao catálogo como `triada`;
- 2 questões são realocadas, mas permanecem em revisão editorial;
- conteúdo, alternativas, gabarito e os três hashes são imutáveis;
- as 31 demais pendências editoriais/documentais não são liberadas.

Depois da aplicação, o gate inicial passa de 50 para 33 questões em revisão.

## Primeiro lote P0

A varredura somente leitura `quality-priority-p0-1000-20260909` examinou as
226.792 questões depois da revisão clínica da quarentena. Ela encontrou 13.371
itens P0 e selecionou os primeiros 1.000 em ordem determinística. Nesse recorte,
973 são casos de documentação visual e 27 são quarentenas já revisadas; 665 são
anteriores a 2016 e somente 16 pertencem à faixa 2020–2026.

Por isso, o primeiro lote foi convertido em auditoria de ativos visuais antes da
revisão médica. O manifesto `data/question_quality_p0_batch_001.json` fixa os
1.000 IDs, `source_id` e score por checksum. O modo `quality_visual_audit` confere
presença de `<img>`, tipo do endereço, domínio e situação documental, sem emitir
enunciados ou URLs completos e sem alterar o banco.
