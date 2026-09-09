# Funil de qualidade das questões — versão 1

## Objetivo

Separar qualidade estrutural, revisão editorial e validação científica sem alterar
gabaritos por inferência. O funil também impede que uma questão v2 ainda não
triada seja entregue ao aluno.

## Semântica dos níveis

| Nível | Significado | Entrega ao aluno |
|---|---|---|
| `importada` | Recebida, ainda sem triagem estrutural concluída | Não |
| `triada` | Estrutura, hashes e taxonomia verificáveis; não implica validação científica | Sim |
| `revisao_necessaria` | Existe pendência documental, visual, editorial ou taxonômica | Não |
| `validada` | Conteúdo revisado individualmente | Sim |
| `validada_com_fonte` | Conteúdo revisado e vinculado a fonte primária | Sim |
| `anulada` | Anulação confirmada em fonte oficial | Não |

## Decisão do primeiro lote

O manifesto `data/question_quality_funnel_manifest.json` contém 209 decisões
imutáveis e protegidas por checksum:

- 157 questões de Hematologia permanecem ativas e recebem família em `subtema`;
- 43 questões do piloto de Hematologia ficam em revisão: 19 realocações ainda sem
  destino canônico, 3 classificações pendentes e 26 alertas editoriais, descontadas
  as sobreposições;
- 7 questões ficam em quarentena documental: quatro conflitos dependentes de
  imagem, dois conflitos de gabarito sem original oficial localizado e um
  enunciado truncado;
- 2 questões SES-GO 2021 ficam marcadas como anuladas, conforme os gabaritos finais
  oficiais de Acesso Direto e Pediatria.

As famílias `Neutropenias` e `Baço e esplenectomia` são mantidas porque formam
grupos educacionais coerentes e o filtro é derivado dos dados. Nenhuma realocação
para outra especialidade é aplicada sem um mapeamento canônico completo.

## Segurança de execução

O executor:

1. exige o checksum exato em `QUESTION_QUALITY_FUNNEL_PLAN_SHA256`;
2. bloqueia e valida as 209 linhas antes da primeira escrita;
3. confere `source_id`, taxonomia e os três hashes de conteúdo/gabarito;
4. proíbe alterações em alternativas e gabarito;
5. usa uma única transação e reverte tudo diante de qualquer divergência;
6. aceita reexecução idempotente e possui modo reverso.

O modo padrão é desabilitado. `dry-run` sempre faz rollback; `apply` somente deve
ser habilitado depois de backup e autorização explícita de publicação.

## Realocação taxonômica — segundo manifesto

O segundo manifesto fecha as 19 realocações pendentes do piloto. Cada destino
foi revisto pelo objetivo educacional predominante da questão, sem inferir nem
alterar a resposta correta. O executor específico deriva o estado esperado do
primeiro manifesto, exige os dois checksums, bloqueia as 19 linhas e reverte o
lote inteiro se taxonomia, qualidade ou qualquer hash tiver mudado.

Das 19 questões, 17 não possuem outra pendência e podem voltar à entrega como
`triada`; as questões 465800 e 651659 continuam bloqueadas porque ainda possuem
revisão editorial pendente. Assim, permanecem 33 itens do piloto em revisão.

## Fontes oficiais das anulações

- Acesso Direto: <https://centrodeselecao.ufg.br/2021/coreme-ses/sistema/provas_gabaritos/gabarito_final/ACESSO%20DIRETO.pdf>
- Pré-requisito Pediatria: <https://centrodeselecao.ufg.br/2021/coreme-ses/sistema/provas_gabaritos/gabarito_final/PRE_REQUISITO_PEDIATRIA.pdf>
