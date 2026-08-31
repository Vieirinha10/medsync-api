# Eficiência operacional da Synapse

## Escopo desta versão

Esta atualização reduz contexto, saída, latência e custo da Synapse sem alterar
a pontuação clínica ou limitar perguntas dos estudantes. A franquia por usuário
foi deliberadamente excluída desta versão.

O sistema determinístico continua responsável por:

- pontuação de exames, hipótese e conduta;
- acertos, omissões e exames de baixo valor;
- critérios de segurança;
- reação e desfecho clínico simulados;
- reavaliação e consequências temporais.

A IA passou a atuar somente como uma camada de tutoria: síntese educativa,
feedback dos exames, feedback da hipótese, feedback da conduta e até três
próximos passos. Os três eixos são obrigatórios, e o eixo de menor desempenho
recebe maior profundidade. O resultado final mantém o mesmo contrato
`ClinicalNarrative`, porque os demais campos são preservados do avaliador
determinístico.

## Contexto compacto

`build_compact_feedback_payload` substitui o envio integral da rubrica por:

- história e exame físico compactados;
- decisões do estudante com limites de caracteres;
- pontuação e classificações já calculadas;
- exames adequados, ausentes e de baixo valor;
- condutas identificadas, ausentes e omissões de segurança;
- diagnóstico, conduta e feedbacks clínicos estritamente necessários.

`build_compact_question_payload` também deixa de reenviar o resultado completo,
fontes, telemetria e campos repetidos a cada pergunta. Ele conserva o resumo do
caso, decisões, resultado objetivo, feedback relevante e referências dos exames
que podem ser discutidos.

## Teto de saída

Os limites são aplicados diretamente em `max_output_tokens`:

| Operação | Padrão | Faixa aceita |
|---|---:|---:|
| Feedback da simulação | 1100 | 400–1600 |
| Pergunta pós-simulação | 450 | 200–800 |

O limite inclui tokens visíveis e não visíveis. Caso uma resposta estruturada
termine incompleta, o MedSync usa o feedback determinístico e ainda registra a
telemetria da chamada quando ela estiver disponível.

As duas operações usam `reasoning.effort=low` e baixa verbosidade por padrão. O
esforço pode ser alterado por `OPENAI_REASONING_EFFORT`, mas a camada gerativa não
deve recalcular a avaliação objetiva. Isso evita consumir o teto com raciocínio
desnecessário para uma tarefa curta de tutoria.

Referência oficial: [contagem de tokens da OpenAI](https://developers.openai.com/api/docs/guides/token-counting).

## Separação e roteamento de modelos

Configuração padrão:

- rotina: `gpt-5.6-luna`;
- avançado: `gpt-5.6-terra`;
- `OPENAI_MODEL`: fallback legado do modelo avançado;
- `OPENAI_SIMULATION_QUESTION_MODEL`: substituição opcional que desativa o
  roteamento automático das perguntas pós-simulação.

`OPENAI_QUESTION_MODEL` permanece reservado às explicações do banco de questões
e não interfere no roteamento das simulações.

O feedback é escalado ao modelo avançado quando ocorre ao menos uma condição:

1. conduta classificada como insegura;
2. hipótese classificada como parcial;
3. caso difícil ou crítico com hipótese, conduta ou investigação incompletas.

Perguntas são escaladas quando o resultado é inseguro, o texto é longo, envolve
risco/instabilidade/contraindicação ou pede uma análise de diferencial ou de
alternativa clinicamente aceitável. As demais usam o modelo de rotina.

Referência oficial: [família GPT-5.6 e papéis Sol, Terra e Luna](https://developers.openai.com/api/docs/guides/latest-model).

## Telemetria e painel

As chamadas continuam persistidas em `ai_usage_records`; nenhuma migração foi
necessária. A rota administrativa protegida é:

```text
GET /admin/synapse/consumo?dias=30
```

O parâmetro aceita 1–180 dias. A resposta contém:

- chamadas e usuários ativos;
- custo médio por caso e por usuário;
- média de chamadas por assinante Premium ativo;
- tokens de entrada, cache, saída e total;
- custo estimado e indicação de cobertura da precificação;
- latência média e p95;
- distribuição por modelo e operação;
- série diária;
- dez usuários com maior consumo;
- configuração operacional sem segredos.

O frontend apresenta esses dados em `Administração → Financeiro → Synapse`, com
períodos de 7, 30 e 90 dias. A lista por usuário serve
somente para monitoramento de padrões e anomalias. Não há bloqueio, franquia ou
contador visível ao estudante.

## Comparativo de 25 casos

Comando reproduzível, sem chamar a OpenAI:

```bash
python scripts/benchmark_synapse_efficiency.py --cases 25
```

A amostra foi distribuída pelo catálogo inteiro e contém 9 respostas completas,
8 parciais e 8 inseguras.

| Métrica | Legado | Compacto | Redução |
|---|---:|---:|---:|
| Contexto total dos 25 casos | 162.515 bytes | 66.150 bytes | 59,3% |
| Estimativa local de entrada | 40.629 tokens | 16.538 tokens | 59,3% |
| Schema estruturado de saída | 2.129 bytes | 1.192 bytes | 44,0% |

Todos os 25 casos preservaram pontuação, feedback de segurança, impacto clínico e
ausência de fontes repetidas. O schema compacto permanece 44% menor que o legado,
mesmo após incluir a análise obrigatória e personalizada dos três eixos. O
roteamento levou 8 cenários completos à rota econômica e escalou 17 cenários
ambíguos, incompletos ou de risco.

A estimativa local de tokens é apenas comparativa. Após a publicação, o painel
deve ser usado para validar os números faturáveis de `response.usage`, o custo e
a latência reais.

## Arquivos principais

- `evaluation.py`: contexto compacto, schema curto, limites e roteamento;
- `routers/admin.py`: agregação administrativa;
- `schemas.py`: contrato do painel;
- `scripts/benchmark_synapse_efficiency.py`: comparativo reproduzível;
- `tests/test_evaluation.py`: limites, payload e roteamento;
- `tests/test_api.py`: segurança e agregação da rota administrativa.

No frontend:

- `src/components/AdminSynapseUsage.jsx`;
- `src/pages/AdminAcademicPage.jsx`;
- `src/services/api.js`;
- `src/styles/admin-operations.css`.

## Publicação e verificação

1. Publicar a API primeiro.
2. Configurar ou confirmar as variáveis dos modelos e dos tetos.
3. Confirmar `/health` e `/ready`.
4. Publicar o frontend.
5. Abrir Administração → Financeiro → Synapse e validar uma janela de 7 dias.
6. Após 20–30 chamadas reais, comparar entrada, saída, latência e custo com o
   período anterior.

Não existe nova migração. O rollback do frontend apenas remove a aba; o rollback
da API restaura o payload anterior e mantém os registros históricos intactos.
