# Changelog

Todas as mudanças relevantes da API MedSync são registradas neste arquivo.

## Não publicado

### Adicionado

- Arquitetura Synapse Multi-LLM 5-Core (`synapse_providers.py` e `evaluation.py`), integrando clientes assíncronos e motor de consenso de Junta Médica para 5 grandes provedores de IA: OpenAI (GPT-4o/5), Anthropic (Claude 3.5), Google Gemini (2.0 Flash), xAI (Grok 2) e DeepSeek (R1 Reasoning).
- Sistema de ativação Plug & Play sob demanda por variáveis de ambiente (`ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `XAI_API_KEY`, `DEEPSEEK_API_KEY`), operando com OpenAI isolada por padrão e alternando automaticamente para consenso quando novas chaves forem inseridas.
- Guia técnico e de custos da Synapse em `docs/SYNAPSE_MULTI_LLM.md`.
- Painel administrativo da Synapse em `GET /admin/synapse/consumo`, com filtros
  de período, tokens, custo estimado, cache, latência, modelos, operações e
  usuários com maior consumo, sem franquia ou bloqueio de perguntas.
- Indicadores financeiros da Synapse com custo médio por caso, custo médio por
  usuário e chamadas por assinante Premium ativo.
- Benchmark offline reproduzível com 25 casos reais, cobrindo respostas
  completas, parciais e inseguras.
- Área de Psiquiatria e Saúde Mental com 15 novos casos clínicos, elevando o
  catálogo de 65 para 80 casos e a meta final do projeto de 100 para 115 casos.
- Casos distribuídos igualmente entre os níveis fácil, intermediário e difícil,
  com escalas psicológicas e psiquiátricas integradas às opções de avaliação.
- Segundo lote da expansão, elevando o catálogo de 60 para 65 casos com
  pneumonia comunitária, colecistite aguda, cetoacidose diabética, gravidez
  ectópica e crise aguda de fechamento angular.
- Casos intermediários com seis exames cada e aceitação de respostas
  diagnósticas curtas, sem exigir a descrição completa das complicações.
- Primeiro lote da expansão para 100 casos clínicos, elevando o catálogo de 55
  para 60 casos.
- Cinco simulações cardiovasculares de nível difícil: infarto inferior com
  acometimento do ventrículo direito, dissecção aguda de aorta Stanford A,
  fibrilação atrial pré-excitada, endocardite infecciosa complicada e
  tamponamento cardíaco.
- Dez exames disponíveis por novo caso, com resultados quantitativos,
  referências laboratoriais e interpretação clínica.
- Desfechos adequado, parcial e inseguro com pelo menos quatro parâmetros de
  reavaliação em cada novo caso.
- Fontes clínicas institucionais e títulos públicos neutros que não revelam o
  diagnóstico.

### Alterado

- O feedback principal da Synapse passa a analisar obrigatoriamente exames,
  hipótese e conduta, priorizando o eixo de menor desempenho e explicando de
  forma explícita condutas zeradas, omissões e sequência clínica corrigida.
- Respostas com conduta abaixo de 40% são encaminhadas ao modelo avançado, e o
  teto padrão do feedback foi ampliado para 1100 tokens para comportar a análise
  personalizada sem alterar a pontuação determinística.
- Contexto da Synapse compactado para remover rubrica, resultado e campos
  repetidos; a IA passou a gerar somente a camada curta de tutoria sobre o
  feedback determinístico.
- Roteamento entre `gpt-5.6-luna` para tarefas comuns e `gpt-5.6-terra` para
  ambiguidade, complexidade incompleta e risco clínico, com modelos configuráveis.
- Tetos de saída aplicados ao feedback (1100 tokens) e às perguntas (450 tokens),
  com limites seguros configuráveis por ambiente.
- Esforço de raciocínio reduzido para `low` e verbosidade baixa nas chamadas
  interativas, preservando a avaliação clínica no mecanismo determinístico.
- Comparativo de 25 casos mediu redução de 59,3% no contexto de entrada e 62,8%
  no schema de saída, preservando as invariantes clínicas em toda a amostra.
- Tom de voz da Synapse reformulado para funcionar como uma preceptora clínica
  atenta: reconhecimento específico, explicação clínica e próximo passo prático,
  sem perder firmeza em alertas de segurança.
- Avaliador por regras e respostas pós-simulação alinhados ao mesmo contrato de
  voz usado pela IA, com menos repetição literal das respostas do estudante.
- Plano pessoal de melhoria tornado contextual, priorizando segurança, hipótese,
  exames e conduta conforme as lacunas realmente identificadas.
- Versão editorial das rubricas elevada de 7 para 8 para sincronizar o lote de
  Psiquiatria e Saúde Mental em bancos existentes.
- Versão editorial das rubricas elevada de 6 para 7 para sincronizar o segundo
  lote em bancos existentes.
- Versão editorial das rubricas elevada de 5 para 6 para sincronizar o novo
  conteúdo em bancos existentes.
- Testes e documentação atualizados para o catálogo de 80 casos.
