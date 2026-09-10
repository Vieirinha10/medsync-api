# Taxonomia unificada de conteúdo — MedSync

## Objetivo

Esta taxonomia conecta questões, casos clínicos e desafios visuais. Ela serve
simultaneamente aos filtros públicos, à busca, às recomendações da Synapse e à
montagem futura de trilhas de aprendizagem.

A implantação é feita em modo sombra: os campos de origem permanecem intactos
até que uma versão completa seja validada e publicada de forma atômica.

## Hierarquia principal

| Nível | Pergunta respondida | Exemplo |
| --- | --- | --- |
| Especialidade | Qual área médica decide a resolução? | Cardiologia |
| Tema | Qual capítulo clínico está sendo estudado? | Valvopatias |
| Assunto | Qual entidade ou decisão específica é cobrada? | Estenose aórtica |

Regras obrigatórias:

- especialidade, tema e assunto devem ser semanticamente distintos;
- o assunto deve ser uma escolha de estudo útil, não uma cópia do tema;
- a especialidade principal é definida pelo conhecimento decisivo;
- áreas secundárias são etiquetas, não duplicações da especialidade;
- IDs canônicos são estáveis e hierárquicos; textos de exibição podem evoluir;
- nenhuma classificação é publicada diretamente pelo classificador.

Exemplo de IDs:

```text
cardiologia
cardiologia.valvopatias
cardiologia.valvopatias.estenose_aortica
```

## Metadados para trilhas

Além da hierarquia, cada conteúdo recebe:

- objetivos de aprendizagem;
- competências clínicas;
- contextos assistenciais;
- dificuldade educacional;
- etiquetas clínicas secundárias;
- confiança, evidências e motivo de eventual ambiguidade.

Esses campos permitem combinar formatos diferentes dentro de uma mesma trilha
sem acrescentar um quarto filtro visível ao aluno.

## Processo de classificação

1. O classificador analisa o conteúdo integral e propõe a hierarquia.
2. Um segundo revisor independente confere o objetivo central e a profundidade.
3. A classificação só recebe `verificada` quando há concordância de hierarquia,
   confiança mínima e ausência de ambiguidade.
4. Divergências entram em `revisao_necessaria` sem bloquear o restante do lote.
5. Execuções possuem checkpoint por conteúdo e podem ser retomadas.
6. A consolidação agrupa sinônimos e materializa os nós canônicos.
7. Somente uma versão aprovada pode alimentar os filtros públicos.

## Estados editoriais

Versão: `rascunho → validando → publicada → arquivada`.

Classificação:
`proposta → verificada/revisao_necessaria → aprovada → publicada`.

Nó canônico: `rascunho/proposto → aprovado → descontinuado`.

## Critérios mínimos para publicação

- zero repetição entre tema e assunto;
- todos os IDs pertencem à versão publicada;
- ausência de colisões de rótulos para um mesmo ID;
- amostra estratificada com precisão editorial definida pelo manifesto;
- categorias genéricas e assuntos excessivamente pequenos dentro dos limites;
- registros incertos permanecem fora dos filtros até resolução;
- relatório de cobertura por especialidade, tema, assunto e formato aprovado.

## Operação

O executor é desativado por padrão e nunca roda no boot da API.

```bash
python -m scripts.classify_content_taxonomy --content-type questao --estimate
python -m scripts.classify_content_taxonomy --content-type questao --apply
python -m scripts.classify_content_taxonomy --resume-run RUN_ID --apply
```

Casos clínicos e desafios visuais usam o mesmo comando, alterando apenas
`--content-type`. O processamento remoto e seus custos devem ser autorizados
antes do uso de `--apply`.
