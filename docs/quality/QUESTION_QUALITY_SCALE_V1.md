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
- as 1.321 sinalizações da auditoria de integridade textual;
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
