# Simulação Clínica 2.2

## Propósito

A MedSync é uma plataforma educacional para treinamento e aperfeiçoamento do
raciocínio clínico por meio de casos interativos que simulam situações reais da
prática médica.

O estudante deve analisar história e exame físico, solicitar exames
complementares, formular hipóteses, definir uma conduta e receber uma avaliação
personalizada ao finalizar o caso.

## Princípios do avaliador

1. Cada caso precisa de um gabarito clínico estruturado e revisado.
2. A pontuação objetiva não pode depender exclusivamente de um modelo de IA.
3. A IA pode aprimorar a explicação, mas não pode alterar a nota calculada.
4. O feedback deve diferenciar erro, omissão e alternativa aceitável.
5. O resultado deve explicar exames essenciais, desnecessários e ausentes.
6. O feedback é educacional e não substitui supervisão ou decisão médica real.
7. Casos sem gabarito revisado não podem ser habilitados na versão 2.0.

## Tom de voz da Synapse

A explicação segue a sequência reconhecimento específico, significado clínico e
próximo passo. O texto deve ser acolhedor, claro e profissional, sem elogios
genéricos, infantilização ou repetição. Alertas de segurança permanecem diretos
e prioritários.

O contrato completo e os critérios de regressão estão em
[`SYNAPSE_VOICE.md`](SYNAPSE_VOICE.md).

## Distribuição da pontuação

- Exames: 40 pontos
- Hipótese diagnóstica: 30 pontos
- Conduta: 30 pontos

## Estrutura padronizada do feedback

- síntese do raciocínio do estudante;
- acertos;
- omissões;
- exames de baixo valor;
- análise das justificativas opcionais dos exames;
- análise da hipótese;
- análise da conduta;
- segurança do paciente;
- reação clínica simulada;
- desfecho delimitado pela rubrica;
- plano pessoal de melhoria.

## Consequências educacionais

- exame de baixo valor adiciona tempo fictício à simulação;
- exame essencial omitido adiciona atraso fictício ao diagnóstico;
- conduta adequada, parcial ou insegura determina o estado simulado do paciente;
- a reavaliação mostra apenas indicadores previamente definidos na rubrica;
- o tempo não representa prazo real de atendimento ou liberação de exames.

Após o resultado, o estudante pode fazer perguntas à Synapse. Cada pergunta é
respondida com o contexto do caso, da resolução e da rubrica, sem reutilizar
dados de pacientes reais e sem permitir que a IA invente evolução clínica.

## Estratégia de implantação

O caso de tromboembolismo pulmonar (caso 8) é o primeiro piloto. Novos casos
somente devem ser habilitados após revisão do respectivo gabarito por uma pessoa
com competência clínica.

O avaliador por regras é orientado integralmente pela rubrica: diagnóstico de
referência, termos aceitos, exames, critérios de conduta, alertas de segurança e
recomendações de estudo. Assim, nenhum texto clínico específico de um caso fica
embutido no mecanismo geral, e novos casos podem ser habilitados sem depender de IA.
