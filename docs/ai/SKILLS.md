# Repertório de IA do MedSync — API

Este documento orienta Codex, Google Antigravity e colaboradores no uso do
Graphify na API. A versão oficial está fixada em `skills-lock.json` e não deve
ser atualizada sem auditoria e autorização.

## Configuração local

No primeiro uso de cada clone:

```bash
python scripts/setup_agent_skills.py install-local
python scripts/setup_agent_skills.py check-local
```

O script instala `graphifyy==0.9.53` em ambiente isolado do `uv`. Ele não
instala hooks Git, não configura provedores e não envia arquivos.

Se o executável não entrar imediatamente no `PATH`, execute
`uv tool update-shell` e reabra o terminal.

## Quando usar

Use Graphify antes de:

- alterar o motor Synapse ou os provedores Multi-LLM;
- modificar a avaliação e o feedback clínico;
- mudar autenticação, permissões ou dados protegidos;
- alterar pagamentos e integração com o Asaas;
- criar migrations ou modificar modelos;
- alterar contratos consumidos pelo frontend;
- realizar refatorações em vários módulos.

Não exija Graphify para uma correção pequena cujo arquivo e causa já estejam
identificados.

Consultas úteis:

```bash
graphify query "synapse"
graphify query "evaluation"
graphify query "payments"
graphify affected "SynapseMultiEngine"
```

Depois de modificar código:

```bash
graphify update .
```

O grafo inicial foi gerado em modo `--code-only`, sem API ou LLM. São
versionados `graph.json`, `GRAPH_REPORT.md`, `manifest.json` e os metadados
de análise e agrupamento.
Cache, custos, caminhos absolutos e memórias locais não entram no Git.

## Antigravity

O Antigravity encontra a skill em `.agents/skills/graphify`, aplica as regras
de `.agents/rules/` e disponibiliza o workflow `/graphify`.

Abra `medsync-api` como workspace e execute o script de configuração local.
Para tarefas que atravessam a interface e a API, abra também
`medsync-frontend` e consulte o grafo de cada repositório.

O MCP do Graphify é opcional. Para habilitá-lo, instale o extra `mcp` da mesma
versão e use a configuração exibida por
`graphify antigravity install`. Configurações pessoais e chaves não devem ser
adicionadas ao Git.

## Distribuição das quatro skills

| Repositório | Skills |
| --- | --- |
| `medsync-frontend` | Graphify, Frontend Design, Copywriting e Humanizer |
| `medsync-api` | Graphify |

Frontend Design, Copywriting e Humanizer não são instaladas na API porque não
devem influenciar regras clínicas, contratos ou código de backend.

## Segurança e atualização

- Use análise local de código como padrão.
- Não envie documentos, rubricas, banco de dados ou dados clínicos a um backend
  externo sem autorização explícita.
- Não ative hooks restritivos automaticamente.
- Não atualize a skill ou o pacote sem revisar origem, licença, diff e
  checksums.
- Push, PR, merge, migração remota e deploy continuam dependendo de autorização
  explícita.

Fonte fixada: [Graphify](https://github.com/Graphify-Labs/graphify).
