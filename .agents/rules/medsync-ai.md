---
trigger: always_on
description: Aplica o repertório oficial de IA e os limites de segurança e publicação da API MedSync.
---

# Repertório oficial da API MedSync

Leia `AGENTS.md` e `docs/ai/SKILLS.md` antes de modificar o projeto.

No início de cada tarefa:

1. identifique se a mudança exige análise arquitetural;
2. informe ao usuário quando `graphify` será usado e por quê;
3. preserve contratos, dados protegidos e decisões clínicas existentes;
4. execute os testes adequados;
5. atualize o grafo depois de alterar código.

Consulte `graphify` antes de trabalhar em Synapse, avaliação clínica,
autenticação, pagamentos, migrations ou contratos que atravessem frontend e
API. Não o exija para uma correção pequena e já localizada.

Não envie código, documentos, banco de dados, rubricas ou informações clínicas
a um provedor externo por meio do Graphify sem autorização explícita. O modo
padrão deste repositório é análise local de código.

Nenhuma tarefa autoriza implicitamente push, PR, merge, migração remota ou
publicação no Render.
