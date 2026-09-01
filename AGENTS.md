# Instruções para agentes e colaboradores

Estas instruções abrangem todo o repositório.

## Repertório de IA do MedSync

Antes de alterar arquitetura, contratos, Synapse, autenticação, pagamentos ou
conteúdo protegido, leia `docs/ai/SKILLS.md`. Informe ao usuário quando a
skill `graphify` for utilizada e por quê.

Use `graphify` antes de mudanças que atravessem vários módulos, afetem o
contrato com o frontend ou tenham impacto arquitetural incerto. Não o exija
para uma correção pequena e já localizada. Quando
`graphify-out/graph.json` existir, consulte o grafo antes de uma investigação
ampla e execute `graphify update .` depois de alterar código.

A skill e o pacote devem permanecer idênticos às versões registradas em
`docs/ai/skills-lock.json`. Preferências e regras próprias do MedSync ficam
fora da skill original.

Não instale, atualize, envie código, abra PR, faça merge, acesse dados externos
ou publique em produção sem a autorização correspondente. Uma autorização de
implementação não implica autorização de publicação.

Antes de criar, editar, importar ou revisar desafios visuais, leia integralmente
`docs/DIRETRIZ_DESAFIOS_VISUAIS.md`.

A diretriz `MEDSYNC-DV-001` é obrigatória para novos lotes. Em especial:

- não altere os 150 desafios atuais sem solicitação expressa;
- organize cada novo lote de 10 em 6 desafios diretos e clínicos e 4 específicos
  e contextualizados;
- mantenha a distribuição preferencial de 3 básicos, 4 intermediários e
  3 avançados;
- utilize apenas imagens clínicas reais, rastreáveis e com licença compatível;
- não exponha o gabarito no frontend, na imagem, no nome do arquivo ou no texto
  alternativo;
- distribua as respostas corretas entre A, B, C e D: em cada bloco consecutivo
  de 10, cada posição deve aparecer 2 ou 3 vezes; no catálogo completo, a
  diferença entre a posição mais e menos frequente deve ser de no máximo 1;
- não declare um lote pronto enquanto o checklist clínico, editorial, visual,
  legal e técnico da diretriz não estiver concluído.

Quando a alteração envolver frontend e API, mantenha enunciados e alternativas
públicas no frontend e respostas, explicações e demais dados protegidos na API.
