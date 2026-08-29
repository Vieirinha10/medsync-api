"""Rubricas clínicas revisáveis usadas pela Simulação Clínica 2.1."""

from typing import Any

from clinical_cases_batch_one import EXPANSION_BATCH_ONE_RUBRICS
from clinical_feedback_batch_final import (
    FINAL_FEEDBACK_BATCH_EXAM_UPDATES,
    FINAL_FEEDBACK_BATCH_RUBRICS,
)
from clinical_feedback_batch_five import (
    FIFTH_FEEDBACK_BATCH_EXAM_UPDATES,
    FIFTH_FEEDBACK_BATCH_RUBRICS,
)
from clinical_feedback_batch_four import (
    FOURTH_FEEDBACK_BATCH_EXAM_UPDATES,
    FOURTH_FEEDBACK_BATCH_RUBRICS,
)
from clinical_feedback_batch_one import (
    FIRST_FEEDBACK_BATCH_EXAM_UPDATES,
    FIRST_FEEDBACK_BATCH_RUBRICS,
)
from clinical_feedback_batch_three import (
    THIRD_FEEDBACK_BATCH_EXAM_UPDATES,
    THIRD_FEEDBACK_BATCH_RUBRICS,
)
from clinical_feedback_batch_two import (
    SECOND_FEEDBACK_BATCH_EXAM_UPDATES,
    SECOND_FEEDBACK_BATCH_RUBRICS,
)
from primary_care_catalog import PRIMARY_CARE_RUBRICS

CLINICAL_RUBRIC_VERSION = 6


def _source(title: str, organization: str, year: int, url: str) -> dict[str, Any]:
    return {
        "titulo": title,
        "organizacao": organization,
        "ano": year,
        "url": url,
    }


CLINICAL_RUBRICS: dict[int, dict[str, Any]] = {
    6: {
        "diagnostico_referencia": "Úlcera péptica perfurada com peritonite secundária.",
        "diagnostico_termos": [
            "ulcera peptica perfurada",
            "perfuracao de ulcera peptica",
            "perfuracao gastroduodenal",
            "ulcera perfurada",
        ],
        "diagnostico_parcial": [
            "ulcera peptica",
            "abdome agudo perfurativo",
            "hemorragia digestiva alta",
        ],
        "exames_essenciais": ["raiox_abdome", "hemo", "tc_abdome", "gaso_lactato"],
        "exames_opcionais": [],
        "exames_desnecessarios": ["eda"],
        "justificativa_exames": {
            "raiox_abdome": "Pode demonstrar pneumoperitônio quando a tomografia não está prontamente disponível.",
            "hemo": "Avalia anemia, leucocitose e repercussão sistêmica no atendimento inicial.",
            "tc_abdome": "É o exame de imagem preferencial para confirmar e localizar a perfuração.",
            "gaso_lactato": "Ajuda a avaliar hipoperfusão, disfunção orgânica e gravidade.",
            "eda": "Não é exame inicial de rotina diante de perfuração com peritonite; pode atrasar o controle da fonte.",
        },
        "conduta_criterios": [
            {
                "nome": "Reanimação e monitorização",
                "pontos": 8,
                "termos": [
                    "abc",
                    "acesso venoso",
                    "cristaloide",
                    "reposicao volemica",
                    "monitorizacao",
                    "ressuscitacao",
                ],
            },
            {
                "nome": "Jejum e descompressão",
                "pontos": 4,
                "termos": [
                    "jejum",
                    "dieta zero",
                    "sonda nasogastrica",
                    "descompressao",
                ],
            },
            {
                "nome": "Antibiótico e supressão ácida",
                "pontos": 6,
                "termos": [
                    "antibiotico",
                    "antimicrobiano",
                    "piperacilina",
                    "ceftriaxona",
                    "metronidazol",
                    "inibidor de bomba",
                    "omeprazol",
                    "pantoprazol",
                ],
            },
            {
                "nome": "Avaliação cirúrgica e controle da fonte",
                "pontos": 12,
                "termos": [
                    "cirurgia",
                    "cirurgiao",
                    "laparoscopia",
                    "laparotomia",
                    "rafia",
                    "controle da fonte",
                    "abordagem cirurgica",
                ],
            },
        ],
        "conduta_referencia": (
            "Reconhecer emergência cirúrgica, iniciar ABC, acesso venoso, reposição e monitorização; "
            "manter jejum, considerar descompressão, iniciar antibiótico de amplo espectro e supressão "
            "ácida; acionar imediatamente a cirurgia para controle da perfuração."
        ),
        "feedback_hipotese_parcial": "Você reconheceu parte do abdome agudo, mas precisa explicitar a perfuração e a peritonite.",
        "feedback_hipotese_incorreta": "O abdome em tábua e o pneumoperitônio apontam para perfuração gastroduodenal, não apenas sangramento digestivo.",
        "feedback_seguranca": "A prioridade é estabilizar e controlar rapidamente a fonte. Endoscopia não deve atrasar a avaliação cirúrgica neste cenário.",
        "objetivos_aprendizagem": [
            "Reconhecer sinais de perfuração e peritonite",
            "Priorizar imagem e avaliação de gravidade",
            "Iniciar reanimação, antibiótico e controle da fonte",
        ],
        "criterios_seguranca": [
            {
                "nome": "Acionamento cirúrgico imediato",
                "termos": ["cirurgia", "cirurgiao", "laparoscopia", "laparotomia"],
                "feedback_omissao": "A ausência de avaliação cirúrgica imediata pode atrasar o controle da fonte.",
            },
            {
                "nome": "Antibioticoterapia precoce",
                "termos": [
                    "antibiotico",
                    "antimicrobiano",
                    "piperacilina",
                    "ceftriaxona",
                ],
                "feedback_omissao": "Peritonite por perfuração exige cobertura antimicrobiana precoce.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Após reanimação e tratamento inicial, a perfusão e a taquicardia tendem a melhorar enquanto a equipe prepara o controle da fonte.",
                "desfecho": "O paciente segue para abordagem cirúrgica urgente e monitorização pós-operatória, com prognóstico dependente do tempo até o controle da perfuração.",
                "reavaliacao": [
                    {
                        "indicador": "Frequência cardíaca",
                        "antes": "taquicardia documentada",
                        "depois": "tendência de redução após reanimação",
                        "tendencia": "melhora",
                    },
                    {
                        "indicador": "Perfusão",
                        "antes": "hipoperfusão inicial",
                        "depois": "melhora clínica esperada",
                        "tendencia": "melhora",
                    },
                ],
            },
            "parcial": {
                "reacao": "Há melhora incompleta dos parâmetros, mas a contaminação peritoneal continua enquanto faltam medidas essenciais.",
                "desfecho": "O atraso no antibiótico ou na cirurgia aumenta o risco de sepse, disfunção orgânica e internação prolongada.",
                "reavaliacao": [
                    {
                        "indicador": "Frequência cardíaca",
                        "antes": "taquicardia documentada",
                        "depois": "persistência provável",
                        "tendencia": "estavel",
                    }
                ],
            },
            "insegura": {
                "reacao": "Sem reanimação e controle da fonte, o paciente mantém taquicardia e pode evoluir com hipotensão e piora da perfusão.",
                "desfecho": "A progressão para sepse e choque torna-se provável se a emergência cirúrgica não for reconhecida.",
                "reavaliacao": [
                    {
                        "indicador": "Perfusão",
                        "antes": "hipoperfusão inicial",
                        "depois": "deterioração prevista na rubrica",
                        "tendencia": "piora",
                    }
                ],
            },
        },
        "reacao_paciente_referencia": "A resposta depende da rapidez da reanimação e do controle da fonte.",
        "desfecho_referencia": "O tratamento definitivo requer avaliação cirúrgica urgente e acompanhamento hospitalar.",
        "temas_estudo": [
            "Abdome agudo perfurativo",
            "Reanimação na sepse abdominal",
            "Controle da fonte em perfuração gastroduodenal",
        ],
        "fontes_clinicas": [
            _source(
                "Perforated and bleeding peptic ulcer: WSES guidelines",
                "World Society of Emergency Surgery",
                2020,
                "https://doi.org/10.1186/s13017-019-0283-9",
            ),
        ],
    },
    7: {
        "diagnostico_referencia": "Anemia ferropriva grave após bypass gástrico.",
        "diagnostico_termos": [
            "anemia ferropriva",
            "deficiencia de ferro",
            "anemia por deficiencia de ferro",
        ],
        "diagnostico_parcial": [
            "anemia microcitica",
            "anemia carencial",
            "anemia pos bariatrica",
        ],
        "exames_essenciais": ["hemo", "ferro"],
        "exames_opcionais": ["vit_b12"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "hemo": "Confirma anemia grave com padrão microcítico e hipocrômico.",
            "ferro": "Ferritina reduzida e capacidade de ligação elevada sustentam deficiência de ferro.",
            "vit_b12": "Pode avaliar deficiências concomitantes após cirurgia bariátrica, embora não explique o padrão apresentado.",
        },
        "conduta_criterios": [
            {
                "nome": "Avaliação e estabilização urgente",
                "pontos": 8,
                "termos": [
                    "urgencia",
                    "internacao",
                    "estabilizacao",
                    "transfusao",
                    "hemacias",
                    "hemodinamica",
                ],
            },
            {
                "nome": "Reposição de ferro adequada à gravidade",
                "pontos": 10,
                "termos": [
                    "ferro intravenoso",
                    "ferro venoso",
                    "reposicao parenteral",
                    "carboximaltose",
                    "sacarato",
                ],
            },
            {
                "nome": "Pesquisa de causas e deficiências associadas",
                "pontos": 6,
                "termos": [
                    "sangramento",
                    "perdas",
                    "b12",
                    "folato",
                    "nutricional",
                    "deficiencias",
                ],
            },
            {
                "nome": "Seguimento bariátrico e laboratorial",
                "pontos": 6,
                "termos": [
                    "seguimento",
                    "acompanhamento",
                    "bariatrica",
                    "nutricionista",
                    "reavaliar",
                    "hemograma",
                    "ferritina",
                ],
            },
        ],
        "conduta_referencia": (
            "Avaliar estabilidade e sintomas em caráter urgente, considerar suporte transfusional conforme o quadro, "
            "realizar reposição de ferro — frequentemente intravenosa diante de anemia grave ou má absorção —, "
            "pesquisar perdas e outras deficiências e manter seguimento bariátrico com controle laboratorial."
        ),
        "feedback_hipotese_parcial": "O padrão microcítico foi reconhecido, mas faltou relacioná-lo à deficiência de ferro após o bypass.",
        "feedback_hipotese_incorreta": "Hemoglobina muito baixa, microcitose, ferritina reduzida e TIBC elevado caracterizam anemia ferropriva grave.",
        "feedback_seguranca": "Hemoglobina de 4 g/dL com sintomas exige avaliação urgente; reposição oral isolada pode ser insuficiente após bypass e nesta gravidade.",
        "objetivos_aprendizagem": [
            "Interpretar o perfil de ferro",
            "Reconhecer gravidade da anemia sintomática",
            "Planejar reposição e seguimento pós-bariátrico",
        ],
        "criterios_seguranca": [
            {
                "nome": "Reconhecimento da gravidade",
                "termos": ["urgencia", "internacao", "transfusao", "estabilizacao"],
                "feedback_omissao": "A gravidade da anemia sintomática precisa ser reconhecida antes do tratamento ambulatorial.",
            },
            {
                "nome": "Estratégia compatível com má absorção",
                "termos": ["ferro intravenoso", "ferro venoso", "parenteral"],
                "feedback_omissao": "Considere via intravenosa diante de anemia grave e absorção reduzida pelo bypass.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Com estabilização e reposição apropriada, palpitações, dispneia e tontura tendem a regredir progressivamente.",
                "desfecho": "A paciente permanece em acompanhamento até recuperação hematológica e reposição dos estoques de ferro.",
                "reavaliacao": [
                    {
                        "indicador": "Sintomas de hipóxia tecidual",
                        "antes": "palpitações, dispneia e tontura",
                        "depois": "regressão progressiva esperada",
                        "tendencia": "melhora",
                    }
                ],
            },
            "parcial": {
                "reacao": "Pode haver melhora lenta, mas sintomas e baixa reserva persistem se a gravidade ou a má absorção forem subestimadas.",
                "desfecho": "Sem ajuste da via de reposição e seguimento, aumenta o risco de resposta inadequada e recorrência.",
            },
            "insegura": {
                "reacao": "Sem avaliação urgente, a paciente mantém sintomas de hipóxia tecidual e risco de instabilidade.",
                "desfecho": "O atraso no suporte e na reposição efetiva pode levar a complicações cardiovasculares e necessidade de atendimento emergencial.",
                "reavaliacao": [
                    {
                        "indicador": "Sintomas de hipóxia tecidual",
                        "antes": "sintomática",
                        "depois": "persistência ou piora prevista",
                        "tendencia": "piora",
                    }
                ],
            },
        },
        "reacao_paciente_referencia": "A melhora depende de estabilização e reposição efetiva do ferro.",
        "desfecho_referencia": "O seguimento deve confirmar recuperação da hemoglobina e dos estoques.",
        "temas_estudo": [
            "Anemia ferropriva",
            "Deficiências após bypass gástrico",
            "Indicações de ferro intravenoso",
        ],
        "fontes_clinicas": [
            _source(
                "Clinical Practice Guidelines for perioperative support of the bariatric surgery patient",
                "AACE/TOS/ASMBS/OMA/ASA",
                2020,
                "https://asmbs.org/resources/aace-tos-asmbs-oma-asa-clinical-practice-guidelines-for-the-perioperative-nutritional-metabolic-and-nonsurgical-support-of-the-bariatric-surgery-patient-2020/",
            ),
        ],
    },
    8: {
        "diagnostico_referencia": "Tromboembolismo pulmonar agudo associado a trombose venosa do membro superior esquerdo em paciente com câncer.",
        "diagnostico_termos": ["tromboembolismo pulmonar", "embolia pulmonar", "tep"],
        "diagnostico_parcial": ["trombose venosa", "trombose"],
        "exames_essenciais": ["angiotc", "doppler_mmss", "gaso"],
        "exames_opcionais": [],
        "exames_desnecessarios": ["dimerod"],
        "justificativa_exames": {
            "angiotc": "Confirma tromboembolismo pulmonar e demonstra falha de enchimento.",
            "doppler_mmss": "Investiga a fonte trombótica diante do membro edemaciado e doloroso.",
            "gaso": "Avalia repercussão respiratória na hipoxemia importante.",
            "dimerod": "Tem baixo valor para exclusão neste cenário de alta probabilidade, câncer ativo e hipoxemia.",
        },
        "conduta_criterios": [
            {
                "nome": "Estabilização e oxigenoterapia",
                "pontos": 8,
                "termos": [
                    "oxigenio",
                    "oxigenoterapia",
                    "suporte ventilatorio",
                    "abc",
                    "estabilizacao",
                ],
            },
            {
                "nome": "Anticoagulação",
                "pontos": 12,
                "termos": [
                    "anticoagulacao",
                    "heparina",
                    "enoxaparina",
                    "anticoagulante",
                ],
            },
            {
                "nome": "Estratificação de risco",
                "pontos": 6,
                "termos": [
                    "estratificacao de risco",
                    "estabilidade hemodinamica",
                    "instabilidade hemodinamica",
                    "reperfusao",
                    "trombolise",
                ],
            },
            {
                "nome": "Internação e monitorização",
                "pontos": 4,
                "termos": [
                    "internacao",
                    "monitorizacao",
                    "monitoramento",
                    "hospitalar",
                ],
            },
        ],
        "conduta_referencia": "Estabilizar, ofertar oxigênio e monitorizar; iniciar anticoagulação se não houver contraindicação; estratificar risco hemodinâmico e avaliar reperfusão; manter acompanhamento hospitalar.",
        "feedback_hipotese_parcial": "Você reconheceu o fenômeno trombótico, mas precisa explicitar o tromboembolismo pulmonar.",
        "feedback_hipotese_incorreta": "A hipótese não identificou o tromboembolismo pulmonar, mais provável diante da apresentação.",
        "feedback_seguranca": "A hipoxemia exige estabilização e monitorização; anticoagulação e reperfusão dependem de contraindicações e estabilidade.",
        "objetivos_aprendizagem": [
            "Reconhecer TEP de alta probabilidade",
            "Selecionar exames de valor",
            "Estratificar risco e tratar com segurança",
        ],
        "criterios_seguranca": [
            {
                "nome": "Suporte da hipoxemia",
                "termos": ["oxigenio", "oxigenoterapia", "suporte ventilatorio", "abc"],
                "feedback_omissao": "Saturação de 83% exige suporte e monitorização imediatos.",
            },
            {
                "nome": "Anticoagulação quando segura",
                "termos": ["anticoagulacao", "heparina", "enoxaparina"],
                "feedback_omissao": "A ausência de anticoagulação sem justificativa mantém progressão trombótica.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Com suporte, anticoagulação e monitorização, a hipoxemia tende a melhorar e a progressão trombótica é contida.",
                "desfecho": "A paciente permanece internada e monitorizada para estratificação; se estável, evolui com melhora, e se deteriorar deve ser reavaliada para reperfusão.",
                "reavaliacao": [
                    {
                        "indicador": "Saturação periférica",
                        "antes": "hipoxemia documentada",
                        "depois": "tendência de melhora com suporte",
                        "tendencia": "melhora",
                    },
                    {
                        "indicador": "Estado hemodinâmico",
                        "antes": "informado no caso",
                        "depois": "mantido sob monitorização",
                        "tendencia": "estavel",
                    },
                ],
            },
            "parcial": {
                "reacao": "A resposta é incompleta enquanto faltam medidas de suporte, anticoagulação ou estratificação.",
                "desfecho": "Persistem risco respiratório e trombótico até que as omissões sejam corrigidas.",
                "reavaliacao": [
                    {
                        "indicador": "Saturação periférica",
                        "antes": "hipoxemia documentada",
                        "depois": "melhora incompleta",
                        "tendencia": "estavel",
                    }
                ],
            },
            "insegura": {
                "reacao": "Sem suporte e tratamento antitrombótico, a hipoxemia e a sobrecarga cardiovascular podem piorar.",
                "desfecho": "Há risco de instabilidade hemodinâmica e necessidade de terapia de reperfusão emergencial.",
                "reavaliacao": [
                    {
                        "indicador": "Saturação periférica",
                        "antes": "hipoxemia documentada",
                        "depois": "piora prevista na rubrica",
                        "tendencia": "piora",
                    }
                ],
            },
        },
        "reacao_paciente_referencia": "A resposta depende do suporte e do tratamento antitrombótico.",
        "desfecho_referencia": "A paciente requer internação, estratificação e reavaliação contínua.",
        "temas_estudo": [
            "Probabilidade pré-teste para TEP",
            "Limitações do D-dímero",
            "Estratificação e tratamento do TEP",
        ],
        "fontes_clinicas": [
            _source(
                "ASH Guidelines for treatment of DVT and PE",
                "American Society of Hematology",
                2020,
                "https://doi.org/10.1182/bloodadvances.2020001830",
            ),
            _source(
                "ASH Guidelines for VTE in patients with cancer",
                "American Society of Hematology",
                2021,
                "https://doi.org/10.1182/bloodadvances.2020003442",
            ),
        ],
    },
    11: {
        "diagnostico_referencia": "Macroprolactinoma com compressão do quiasma óptico.",
        "diagnostico_termos": [
            "macroprolactinoma",
            "prolactinoma",
            "macroadenoma secretor de prolactina",
        ],
        "diagnostico_parcial": [
            "macroadenoma hipofisario",
            "adenoma hipofisario",
            "hiperprolactinemia",
        ],
        "exames_essenciais": ["prolactina", "rm_sela_turcica", "campimetria"],
        "exames_opcionais": ["tsh_t4l", "beta_hcg", "funcao_renal"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "prolactina": "Quantifica hiperprolactinemia e sustenta secreção tumoral.",
            "rm_sela_turcica": "Define tamanho, extensão e compressão quiasmática.",
            "campimetria": "Documenta repercussão visual e ajuda a definir urgência e resposta.",
            "tsh_t4l": "Ajuda a excluir hipotireoidismo e avaliar o eixo tireoidiano.",
            "beta_hcg": "Exclui gestação em pessoa em idade reprodutiva.",
            "funcao_renal": "Doença renal pode causar hiperprolactinemia e deve ser considerada.",
        },
        "conduta_criterios": [
            {
                "nome": "Agonista dopaminérgico",
                "pontos": 15,
                "termos": ["cabergolina", "agonista dopaminergico", "bromocriptina"],
            },
            {
                "nome": "Avaliação visual e neurológica urgente",
                "pontos": 6,
                "termos": [
                    "campimetria",
                    "campo visual",
                    "oftalmologia",
                    "avaliacao visual",
                    "neurocirurgia",
                    "urgente",
                ],
            },
            {
                "nome": "Avaliação dos eixos hipofisários",
                "pontos": 5,
                "termos": [
                    "eixos hipofisarios",
                    "funcao hipofisaria",
                    "cortisol",
                    "tsh",
                    "t4",
                    "endocrinologia",
                ],
            },
            {
                "nome": "Monitorização de resposta",
                "pontos": 4,
                "termos": [
                    "repetir prolactina",
                    "controle de prolactina",
                    "nova ressonancia",
                    "acompanhamento",
                    "monitorizacao",
                ],
            },
        ],
        "conduta_referencia": "Avaliar com urgência o déficit visual e sinais neurológicos, iniciar cabergolina quando clinicamente apropriado, avaliar demais eixos hipofisários e acompanhar prolactina, sintomas visuais e volume tumoral; discutir cirurgia se houver indicação ou falha terapêutica.",
        "feedback_hipotese_parcial": "Hiperprolactinemia ou macroadenoma isoladamente não sintetizam o caso; integre secreção de prolactina e compressão quiasmática.",
        "feedback_hipotese_incorreta": "Prolactina muito elevada associada a macroadenoma e sintomas visuais sustenta macroprolactinoma.",
        "feedback_seguranca": "Diplopia e compressão do quiasma exigem avaliação visual/neurológica rápida e rastreio de insuficiência hipofisária.",
        "objetivos_aprendizagem": [
            "Diagnosticar macroprolactinoma",
            "Avaliar repercussão visual",
            "Planejar tratamento e monitorização",
        ],
        "criterios_seguranca": [
            {
                "nome": "Avaliação visual urgente",
                "termos": ["campimetria", "campo visual", "oftalmologia", "urgente"],
                "feedback_omissao": "A compressão quiasmática exige documentação e vigilância visual rápidas.",
            },
            {
                "nome": "Avaliação de função hipofisária",
                "termos": [
                    "eixos hipofisarios",
                    "cortisol",
                    "funcao hipofisaria",
                    "endocrinologia",
                ],
                "feedback_omissao": "Macroadenomas podem comprometer outros eixos, inclusive o corticotrófico.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Com agonista dopaminérgico e vigilância adequada, a prolactina tende a cair e os sintomas compressivos podem melhorar.",
                "desfecho": "Espera-se redução tumoral e recuperação clínica, com seguimento hormonal, visual e por imagem.",
                "reavaliacao": [
                    {
                        "indicador": "Sintomas visuais",
                        "antes": "alteração visual documentada",
                        "depois": "melhora possível sob vigilância",
                        "tendencia": "melhora",
                    }
                ],
            },
            "parcial": {
                "reacao": "A resposta pode ocorrer, mas déficits visuais ou hormonais podem não ser detectados sem avaliação completa.",
                "desfecho": "O acompanhamento incompleto aumenta o risco de persistência de compressão ou deficiência hipofisária.",
            },
            "insegura": {
                "reacao": "Sem tratamento e avaliação urgente, cefaleia e alterações visuais podem persistir ou progredir.",
                "desfecho": "Há risco de dano visual e atraso no reconhecimento de complicações do macroadenoma.",
                "reavaliacao": [
                    {
                        "indicador": "Sintomas visuais",
                        "antes": "alteração visual documentada",
                        "depois": "progressão prevista na rubrica",
                        "tendencia": "piora",
                    }
                ],
            },
        },
        "reacao_paciente_referencia": "A resposta deve ser acompanhada por sintomas, prolactina, campo visual e imagem.",
        "desfecho_referencia": "O objetivo é normalização hormonal e redução tumoral com preservação visual.",
        "temas_estudo": [
            "Investigação da hiperprolactinemia",
            "Agonistas dopaminérgicos",
            "Síndromes compressivas hipofisárias",
        ],
        "fontes_clinicas": [
            _source(
                "Diagnosis and management of prolactin-secreting pituitary adenomas",
                "Pituitary Society",
                2023,
                "https://doi.org/10.1038/s41574-023-00886-5",
            ),
        ],
    },
    12: {
        "diagnostico_referencia": "Síndrome de Cushing exógena por uso crônico de betametasona, com supressão do eixo hipotálamo-hipófise-adrenal.",
        "diagnostico_termos": [
            "cushing exogeno",
            "cushing iatrogenico",
            "sindrome de cushing iatrogenica",
            "hipercortisolismo exogeno",
        ],
        "diagnostico_parcial": [
            "sindrome de cushing",
            "supressao do eixo hpa",
            "insuficiencia adrenal induzida por glicocorticoide",
        ],
        "exames_essenciais": ["cortisol_acth"],
        "exames_opcionais": ["glicemia", "eletrolitos", "perfil_metabolico"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "cortisol_acth": "A supressão é compatível com exposição exógena prolongada.",
            "glicemia": "Avalia complicação metabólica do excesso de glicocorticoide.",
            "eletrolitos": "Ajuda a avaliar repercussões metabólicas e segurança do acompanhamento.",
            "perfil_metabolico": "Documenta complicações cardiovasculares e metabólicas associadas.",
        },
        "conduta_criterios": [
            {
                "nome": "Reconhecer e retirar a fonte com segurança",
                "pontos": 10,
                "termos": [
                    "suspender betametasona",
                    "retirar betametasona",
                    "interromper descongestionante",
                    "fonte exogena",
                    "glicocorticoide exogeno",
                ],
            },
            {
                "nome": "Desmame gradual ou troca por ação curta",
                "pontos": 10,
                "termos": [
                    "desmame gradual",
                    "reduzir gradualmente",
                    "taper",
                    "hidrocortisona",
                    "prednisona",
                    "curta acao",
                ],
            },
            {
                "nome": "Avaliar recuperação do eixo",
                "pontos": 5,
                "termos": [
                    "cortisol matinal",
                    "eixo hpa",
                    "recuperacao do eixo",
                    "insuficiencia adrenal",
                    "endocrinologia",
                ],
            },
            {
                "nome": "Prevenir e tratar complicações",
                "pontos": 5,
                "termos": [
                    "pressao arterial",
                    "hipertensao",
                    "osteoporose",
                    "glicemia",
                    "infeccao",
                    "educacao",
                    "dose de estresse",
                ],
            },
        ],
        "conduta_referencia": "Interromper a exposição inadequada sob supervisão, evitando suspensão abrupta; quando possível, substituir glicocorticoide de ação longa por ação curta e realizar desmame gradual, avaliar recuperação do eixo e orientar sobre insuficiência adrenal e doses de estresse, além de tratar complicações.",
        "feedback_hipotese_parcial": "O fenótipo de Cushing precisa ser relacionado ao uso crônico de betametasona e à supressão do eixo.",
        "feedback_hipotese_incorreta": "A exposição prolongada a glicocorticoide, o fenótipo típico e ACTH/cortisol suprimidos apontam para Cushing exógeno.",
        "feedback_seguranca": "Após uso crônico, a suspensão abrupta pode precipitar insuficiência adrenal; o desmame e a educação sobre estresse são essenciais.",
        "objetivos_aprendizagem": [
            "Reconhecer Cushing exógeno",
            "Evitar retirada abrupta",
            "Avaliar recuperação do eixo HPA e complicações",
        ],
        "criterios_seguranca": [
            {
                "nome": "Evitar suspensão abrupta",
                "termos": [
                    "desmame gradual",
                    "reduzir gradualmente",
                    "taper",
                    "hidrocortisona",
                    "prednisona",
                ],
                "feedback_omissao": "Suspensão abrupta após exposição prolongada pode precipitar insuficiência adrenal.",
            },
            {
                "nome": "Orientação para situações de estresse",
                "termos": [
                    "dose de estresse",
                    "stress dose",
                    "cartao de emergencia",
                    "educacao",
                    "insuficiencia adrenal",
                ],
                "feedback_omissao": "O paciente precisa saber reconhecer insuficiência adrenal e manejar situações de estresse.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Com retirada supervisionada e desmame, a exposição excessiva cessa sem perda abrupta da cobertura glicocorticoide.",
                "desfecho": "Os sinais cushingoides regridem gradualmente enquanto o eixo é monitorado até recuperação, com controle das complicações.",
                "reavaliacao": [
                    {
                        "indicador": "Pressão arterial",
                        "antes": "repercussão descrita no caso",
                        "depois": "controle progressivo esperado",
                        "tendencia": "melhora",
                    }
                ],
            },
            "parcial": {
                "reacao": "Algumas complicações podem melhorar, mas permanece risco de sintomas de retirada ou insuficiência se o plano não contemplar o eixo HPA.",
                "desfecho": "A recuperação pode ser prolongada e requer ajuste do desmame e seguimento endocrinológico.",
            },
            "insegura": {
                "reacao": "A suspensão abrupta pode causar fraqueza, náuseas, hipotensão e descompensação adrenal.",
                "desfecho": "Sem orientação e cobertura adequada, existe risco de crise adrenal diante de doença ou estresse.",
                "reavaliacao": [
                    {
                        "indicador": "Pressão arterial",
                        "antes": "repercussão descrita no caso",
                        "depois": "risco de hipotensão previsto",
                        "tendencia": "piora",
                    }
                ],
            },
        },
        "reacao_paciente_referencia": "A resposta depende de retirada supervisionada e proteção contra insuficiência adrenal.",
        "desfecho_referencia": "A recuperação do eixo varia e deve ser monitorada durante o desmame.",
        "temas_estudo": [
            "Cushing exógeno",
            "Desmame de glicocorticoides",
            "Insuficiência adrenal induzida por glicocorticoide",
        ],
        "fontes_clinicas": [
            _source(
                "Diagnosis and therapy of glucocorticoid-induced adrenal insufficiency",
                "European Society of Endocrinology and Endocrine Society",
                2024,
                "https://doi.org/10.1210/clinem/dgae250",
            ),
        ],
    },
}

CLINICAL_RUBRICS.update(FIRST_FEEDBACK_BATCH_RUBRICS)
CLINICAL_RUBRICS.update(SECOND_FEEDBACK_BATCH_RUBRICS)
CLINICAL_RUBRICS.update(THIRD_FEEDBACK_BATCH_RUBRICS)
CLINICAL_RUBRICS.update(FOURTH_FEEDBACK_BATCH_RUBRICS)
CLINICAL_RUBRICS.update(FIFTH_FEEDBACK_BATCH_RUBRICS)
CLINICAL_RUBRICS.update(FINAL_FEEDBACK_BATCH_RUBRICS)
CLINICAL_RUBRICS.update(PRIMARY_CARE_RUBRICS)
CLINICAL_RUBRICS.update(EXPANSION_BATCH_ONE_RUBRICS)


# Segunda leva em preparação editorial. A presença neste catálogo não libera a
# Simulação 2.0: o serviço persiste estas definições com status ``rascunho``.
DRAFT_CLINICAL_RUBRICS: dict[int, dict[str, Any]] = {
    33: {
        "diagnostico_referencia": "Parada cardiorrespiratória em fibrilação ventricular, ritmo chocável.",
        "diagnostico_termos": [
            "parada cardiorrespiratoria",
            "pcr em fibrilacao ventricular",
            "fibrilacao ventricular",
        ],
        "diagnostico_parcial": ["parada cardiaca", "ritmo chocavel"],
        "exames_essenciais": ["dea"],
        "exames_opcionais": [],
        "exames_desnecessarios": ["glicemia_capilar", "ecg_12_derivacoes"],
        "justificativa_exames": {
            "dea": "A análise imediata do ritmo identifica fibrilação ventricular e direciona a desfibrilação.",
            "glicemia_capilar": "Pode ter utilidade posterior, mas não deve interromper compressões ou atrasar o choque.",
            "ecg_12_derivacoes": "É considerado após retorno da circulação; durante a parada atrasaria prioridades críticas.",
        },
        "conduta_criterios": [
            {
                "nome": "RCP de alta qualidade",
                "pontos": 10,
                "termos": ["rcp", "compressao", "100 a 120", "minimizar interrupcoes"],
            },
            {
                "nome": "Desfibrilação precoce",
                "pontos": 10,
                "termos": ["desfibrilar", "desfibrilacao", "choque"],
            },
            {
                "nome": "Suporte avançado e causas reversíveis",
                "pontos": 10,
                "termos": [
                    "adrenalina",
                    "epinefrina",
                    "amiodarona",
                    "acesso venoso",
                    "causas reversiveis",
                    "5h",
                    "5t",
                ],
            },
        ],
        "conduta_referencia": "Iniciar RCP de alta qualidade, conectar monitor/desfibrilador e desfibrilar imediatamente a fibrilação ventricular; retomar RCP, obter acesso IV/IO, administrar fármacos conforme o algoritmo e tratar causas reversíveis.",
        "feedback_hipotese_parcial": "Você reconheceu a parada, mas precisa classificar a fibrilação ventricular como ritmo chocável.",
        "feedback_hipotese_incorreta": "Ausência de pulso e respiração confirma parada; a análise mostra fibrilação ventricular.",
        "feedback_seguranca": "Nenhum exame deve atrasar compressões de alta qualidade e desfibrilação precoce.",
        "objetivos_aprendizagem": [
            "Reconhecer PCR",
            "Identificar ritmo chocável",
            "Executar prioridades do algoritmo de FV/TV sem pulso",
        ],
        "criterios_seguranca": [
            {
                "nome": "Desfibrilação imediata",
                "termos": ["desfibrilar", "desfibrilacao", "choque"],
                "feedback_omissao": "Atrasar a desfibrilação em fibrilação ventricular reduz a chance de reversão.",
            },
            {
                "nome": "RCP contínua",
                "termos": ["rcp", "compressao"],
                "feedback_omissao": "Compressões de alta qualidade são indispensáveis entre as análises do ritmo.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Após choque e RCP de alta qualidade, o ritmo se organiza e há retorno da circulação espontânea.",
                "desfecho": "A paciente segue para cuidados pós-parada e investigação de síndrome coronariana.",
                "reavaliacao": [
                    {
                        "indicador": "Pulso central",
                        "antes": "ausente",
                        "depois": "presente após retorno da circulação",
                        "tendencia": "melhora",
                    }
                ],
            },
            "parcial": {
                "reacao": "A fibrilação ventricular persiste porque etapas críticas foram incompletas ou tardias.",
                "desfecho": "A equipe mantém ciclos de RCP e corrige a omissão antes de nova análise.",
            },
            "insegura": {
                "reacao": "Sem RCP e choque imediatos, a paciente permanece sem circulação efetiva.",
                "desfecho": "O atraso provoca deterioração rápida e reduz a probabilidade de retorno da circulação.",
                "reavaliacao": [
                    {
                        "indicador": "Circulação",
                        "antes": "ausente",
                        "depois": "permanece ausente",
                        "tendencia": "piora",
                    }
                ],
            },
        },
        "reacao_paciente_referencia": "A resposta depende principalmente da qualidade da RCP e do tempo até o choque.",
        "desfecho_referencia": "Após retorno da circulação, iniciar cuidados pós-parada e tratar a causa provável.",
        "temas_estudo": [
            "PCR em ritmo chocável",
            "RCP de alta qualidade",
            "Cuidados pós-parada",
        ],
        "fontes_clinicas": [
            _source(
                "Adult Cardiac Arrest Algorithm",
                "American Heart Association",
                2014,
                "https://cpr.heart.org/-/media/CPR-Files/CPR-Guidelines-Files/2025-Algorithms/Algorithm-ACLS-CA-250527.pdf",
            )
        ],
    },
    36: {
        "diagnostico_referencia": "Sepse com provável foco gastrointestinal e sinais de hipoperfusão.",
        "diagnostico_termos": [
            "sepse de foco gastrointestinal",
            "sepse gastrointestinal",
            "sepse com foco abdominal",
        ],
        "diagnostico_parcial": ["sepse", "choque septico", "infeccao intestinal"],
        "exames_essenciais": [
            "lactato",
            "hemoculturas",
            "hemo",
            "funcao_renal_eletrolitos",
        ],
        "exames_opcionais": ["tc_abdome"],
        "exames_desnecessarios": ["colonoscopia"],
        "justificativa_exames": {
            "lactato": "Ajuda a reconhecer hipoperfusão e deve ser interpretado no contexto clínico.",
            "hemoculturas": "Devem ser coletadas antes do antimicrobiano se isso não causar atraso relevante.",
            "hemo": "Caracteriza resposta inflamatória e alterações hematológicas.",
            "funcao_renal_eletrolitos": "Avalia disfunção orgânica e orienta reposição e doses.",
            "tc_abdome": "Pode localizar foco e complicações após a estabilização inicial.",
            "colonoscopia": "Não é prioridade em paciente instável e pode atrasar ressuscitação e antimicrobiano.",
        },
        "conduta_criterios": [
            {
                "nome": "Ressuscitação e monitorização",
                "pontos": 10,
                "termos": [
                    "cristaloide",
                    "reposicao volemica",
                    "acesso venoso",
                    "monitorizacao",
                    "pressao arterial media",
                ],
            },
            {
                "nome": "Antimicrobiano precoce",
                "pontos": 10,
                "termos": ["antibiotico", "antimicrobiano", "amplo espectro"],
            },
            {
                "nome": "Reavaliação e controle do foco",
                "pontos": 10,
                "termos": [
                    "reavaliar",
                    "controle do foco",
                    "controle da fonte",
                    "imagem",
                    "vasopressor",
                    "noradrenalina",
                ],
            },
        ],
        "conduta_referencia": "Obter acesso e monitorização, colher culturas sem atrasar tratamento, iniciar antimicrobiano adequado, ressuscitar com cristaloide e reavaliar perfusão; usar vasopressor se necessário e buscar controle precoce do foco.",
        "feedback_hipotese_parcial": "Você reconheceu sepse, mas deve integrar o provável foco gastrointestinal e os sinais de hipoperfusão.",
        "feedback_hipotese_incorreta": "Infecção provável, alteração do sensório, hipotensão e taquicardia exigem reconhecimento imediato de sepse.",
        "feedback_seguranca": "Culturas e exames não podem atrasar antimicrobiano e ressuscitação no paciente instável.",
        "objetivos_aprendizagem": [
            "Reconhecer sepse",
            "Avaliar perfusão e disfunção orgânica",
            "Priorizar antimicrobiano, ressuscitação e controle do foco",
        ],
        "criterios_seguranca": [
            {
                "nome": "Antimicrobiano precoce",
                "termos": ["antibiotico", "antimicrobiano"],
                "feedback_omissao": "A omissão do antimicrobiano permite progressão da infecção e disfunção orgânica.",
            },
            {
                "nome": "Suporte hemodinâmico",
                "termos": [
                    "cristaloide",
                    "reposicao volemica",
                    "noradrenalina",
                    "vasopressor",
                ],
                "feedback_omissao": "Hipotensão e hipoperfusão exigem suporte hemodinâmico e reavaliação frequente.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Após ressuscitação e antimicrobiano, a perfusão e o estado mental começam a melhorar.",
                "desfecho": "O paciente permanece monitorizado, com investigação do foco e ajuste conforme culturas.",
                "reavaliacao": [
                    {
                        "indicador": "Pressão arterial",
                        "antes": "90x65 mmHg",
                        "depois": "tendência de recuperação da perfusão",
                        "tendencia": "melhora",
                    }
                ],
            },
            "parcial": {
                "reacao": "A resposta é incompleta e persistem taquicardia ou sinais de hipoperfusão.",
                "desfecho": "É necessária correção imediata das medidas omitidas e nova avaliação do foco.",
            },
            "insegura": {
                "reacao": "Sem antimicrobiano ou suporte circulatório, hipotensão e alteração do sensório pioram.",
                "desfecho": "O paciente pode evoluir para choque e falência orgânica.",
                "reavaliacao": [
                    {
                        "indicador": "Perfusão",
                        "antes": "comprometida",
                        "depois": "deterioração progressiva",
                        "tendencia": "piora",
                    }
                ],
            },
        },
        "reacao_paciente_referencia": "A resposta é acompanhada por perfusão, pressão, estado mental, diurese e lactato seriado quando indicado.",
        "desfecho_referencia": "O prognóstico depende de tratamento precoce e controle adequado do foco.",
        "temas_estudo": [
            "Reconhecimento de sepse",
            "Ressuscitação hemodinâmica",
            "Controle de foco abdominal",
        ],
        "fontes_clinicas": [
            _source(
                "Surviving Sepsis Campaign Guidelines",
                "Society of Critical Care Medicine",
                2026,
                "https://www.sccm.org/clinical-resources/guidelines/guidelines/surviving-sepsis-campaign-international-guidelines-for-management-of-sepsis-and-septic-shock-2026",
            )
        ],
    },
    38: {
        "diagnostico_referencia": "Edema agudo de pulmão cardiogênico hipertensivo com insuficiência respiratória hipoxêmica.",
        "diagnostico_termos": [
            "edema agudo de pulmao",
            "edema pulmonar cardiogenico",
            "insuficiencia cardiaca aguda hipertensiva",
        ],
        "diagnostico_parcial": ["insuficiencia cardiaca aguda", "congestao pulmonar"],
        "exames_essenciais": ["raiox_torax", "ecg", "gaso", "funcao_renal_eletrolitos"],
        "exames_opcionais": ["bnp"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "raiox_torax": "Documenta congestão pulmonar e ajuda a avaliar diagnósticos alternativos.",
            "ecg": "Pesquisa isquemia e arritmia como precipitantes.",
            "gaso": "Quantifica a insuficiência respiratória e auxilia a monitorar suporte ventilatório.",
            "funcao_renal_eletrolitos": "Orienta segurança do tratamento e identifica disfunção associada.",
            "bnp": "Pode reforçar origem cardíaca quando o diagnóstico permanece incerto.",
        },
        "conduta_criterios": [
            {
                "nome": "Suporte respiratório imediato",
                "pontos": 10,
                "termos": [
                    "oxigenio",
                    "ventilacao nao invasiva",
                    "vni",
                    "cpap",
                    "bipap",
                ],
            },
            {
                "nome": "Redução segura da congestão e pós-carga",
                "pontos": 10,
                "termos": [
                    "nitrato",
                    "nitroglicerina",
                    "vasodilatador",
                    "diuretico",
                    "furosemida",
                ],
            },
            {
                "nome": "Monitorização e causa precipitante",
                "pontos": 10,
                "termos": [
                    "monitorizacao",
                    "monitorar",
                    "sindrome coronariana",
                    "isquemia",
                    "ecg",
                    "reavaliar",
                ],
            },
        ],
        "conduta_referencia": "Tratar imediatamente a hipoxemia, considerar ventilação não invasiva pela insuficiência respiratória, reduzir a pós-carga com vasodilatador diante da hipertensão, tratar congestão, monitorizar e investigar precipitantes.",
        "feedback_hipotese_parcial": "Você reconheceu insuficiência cardíaca, mas deve explicitar o edema pulmonar agudo hipertensivo e a insuficiência respiratória.",
        "feedback_hipotese_incorreta": "Dispneia súbita, expectoração rósea, crepitações, hipoxemia e padrão radiográfico bilateral favorecem edema pulmonar cardiogênico.",
        "feedback_seguranca": "Saturação de 82% e esforço respiratório exigem suporte imediato; atrasar ventilação e controle da pós-carga pode causar deterioração.",
        "objetivos_aprendizagem": [
            "Reconhecer edema pulmonar agudo",
            "Priorizar suporte respiratório",
            "Tratar o fenótipo hipertensivo e pesquisar precipitantes",
        ],
        "criterios_seguranca": [
            {
                "nome": "Suporte respiratório",
                "termos": [
                    "oxigenio",
                    "vni",
                    "cpap",
                    "bipap",
                    "ventilacao nao invasiva",
                ],
                "feedback_omissao": "A hipoxemia grave com esforço respiratório requer suporte imediato e reavaliação.",
            },
            {
                "nome": "Controle da hipertensão",
                "termos": [
                    "nitrato",
                    "nitroglicerina",
                    "vasodilatador",
                    "reduzir pressao",
                ],
                "feedback_omissao": "A pós-carga muito elevada perpetua a congestão e deve ser tratada com monitorização.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Com suporte ventilatório e redução da pós-carga, a dispneia e a saturação melhoram progressivamente.",
                "desfecho": "O paciente permanece monitorizado para tratamento da congestão e investigação do fator precipitante.",
                "reavaliacao": [
                    {
                        "indicador": "Saturação",
                        "antes": "82%",
                        "depois": "elevação progressiva com suporte",
                        "tendencia": "melhora",
                    }
                ],
            },
            "parcial": {
                "reacao": "Há melhora incompleta, com persistência de taquipneia ou hipertensão.",
                "desfecho": "É necessário completar o suporte e reavaliar resposta hemodinâmica e respiratória.",
            },
            "insegura": {
                "reacao": "Sem suporte respiratório e controle da pós-carga, a hipoxemia e o esforço respiratório pioram.",
                "desfecho": "O paciente pode evoluir para fadiga, necessidade de via aérea avançada e instabilidade.",
                "reavaliacao": [
                    {
                        "indicador": "Trabalho respiratório",
                        "antes": "aumentado",
                        "depois": "deterioração progressiva",
                        "tendencia": "piora",
                    }
                ],
            },
        },
        "reacao_paciente_referencia": "A melhora deve ser acompanhada por saturação, frequência respiratória, pressão e trabalho respiratório.",
        "desfecho_referencia": "Após estabilização, tratar a congestão e identificar o precipitante da insuficiência cardíaca aguda.",
        "temas_estudo": [
            "Edema pulmonar agudo",
            "Ventilação não invasiva",
            "Insuficiência cardíaca aguda hipertensiva",
        ],
        "fontes_clinicas": [
            _source(
                "Acute heart failure: diagnosis and management",
                "National Institute for Health and Care Excellence",
                2025,
                "https://www.nice.org.uk/guidance/cg187/chapter/recommendations",
            )
        ],
    },
    39: {
        "diagnostico_referencia": "Obstrução infravesical por hiperplasia prostática benigna, complicada por retenção, hidroureteronefrose bilateral e disfunção renal.",
        "diagnostico_termos": [
            "hiperplasia prostatica benigna",
            "obstrucao prostatica benigna",
            "obstrucao infravesical por hpb",
        ],
        "diagnostico_parcial": [
            "sintomas do trato urinario inferior",
            "obstrucao infravesical",
            "retencao urinaria",
        ],
        "exames_essenciais": ["urina1", "usg_vias_urinarias", "funcao_renal"],
        "exames_opcionais": ["psa", "urofluxometria"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "urina1": "Pesquisa infecção, hematúria, proteinúria e outros diagnósticos associados.",
            "usg_vias_urinarias": "Avalia próstata, resíduo pós-miccional e repercussão no trato urinário superior.",
            "funcao_renal": "É essencial diante de hidronefrose e suspeita de obstrução com repercussão renal.",
            "psa": "Auxilia decisão quando o resultado puder mudar manejo e exige aconselhamento e interpretação contextual.",
            "urofluxometria": "Objetiva redução do fluxo, mas isoladamente não define o mecanismo da obstrução.",
        },
        "conduta_criterios": [
            {
                "nome": "Reconhecer complicação obstrutiva",
                "pontos": 10,
                "termos": [
                    "retencao",
                    "obstrucao",
                    "hidronefrose",
                    "disfuncao renal",
                    "insuficiencia renal",
                ],
            },
            {
                "nome": "Descompressão e avaliação urológica",
                "pontos": 10,
                "termos": [
                    "sondagem",
                    "cateter",
                    "descompressao",
                    "urologia",
                    "urologista",
                ],
            },
            {
                "nome": "Tratamento definitivo e seguimento",
                "pontos": 10,
                "termos": [
                    "cirurgia",
                    "tratamento cirurgico",
                    "desobstrucao",
                    "reavaliar creatinina",
                    "monitorar diurese",
                ],
            },
        ],
        "conduta_referencia": "Reconhecer retenção com repercussão renal, promover descompressão vesical e monitorar diurese e função renal; solicitar avaliação urológica para definição do tratamento desobstrutivo e interpretar PSA no contexto adequado.",
        "feedback_hipotese_parcial": "Os sintomas urinários foram reconhecidos, mas faltou integrar retenção, hidronefrose e disfunção renal à obstrução prostática.",
        "feedback_hipotese_incorreta": "Próstata aumentada e lisa, fluxo reduzido, resíduo elevado e dilatação bilateral sustentam obstrução prostática benigna complicada.",
        "feedback_seguranca": "Hidronefrose bilateral e creatinina elevada afastam simples observação; é necessário aliviar a obstrução e avaliar repercussões.",
        "objetivos_aprendizagem": [
            "Avaliar LUTS masculinos",
            "Reconhecer obstrução complicada",
            "Priorizar descompressão e avaliação urológica",
        ],
        "criterios_seguranca": [
            {
                "nome": "Alívio da obstrução",
                "termos": ["sondagem", "cateter", "descompressao"],
                "feedback_omissao": "Manter retenção com hidronefrose pode agravar lesão renal e sintomas.",
            },
            {
                "nome": "Avaliação da função renal",
                "termos": [
                    "creatinina",
                    "funcao renal",
                    "insuficiencia renal",
                    "diurese",
                ],
                "feedback_omissao": "A repercussão renal precisa ser monitorada após a descompressão.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Após descompressão, o desconforto vesical melhora e a diurese é monitorada.",
                "desfecho": "O paciente segue com reavaliação renal e planejamento urológico definitivo.",
                "reavaliacao": [
                    {
                        "indicador": "Distensão vesical",
                        "antes": "globo vesical palpável",
                        "depois": "redução após descompressão",
                        "tendencia": "melhora",
                    }
                ],
            },
            "parcial": {
                "reacao": "Os sintomas podem aliviar parcialmente, mas a repercussão renal permanece sem plano definitivo.",
                "desfecho": "É necessário completar avaliação urológica e seguimento da função renal.",
            },
            "insegura": {
                "reacao": "Sem aliviar a obstrução, retenção e dilatação urinária persistem.",
                "desfecho": "Há risco de piora da função renal, infecção e nova retenção.",
                "reavaliacao": [
                    {
                        "indicador": "Função renal",
                        "antes": "creatinina elevada",
                        "depois": "risco de piora",
                        "tendencia": "piora",
                    }
                ],
            },
        },
        "reacao_paciente_referencia": "A resposta é acompanhada por dor, distensão, diurese, resíduo e função renal.",
        "desfecho_referencia": "A obstrução complicada requer seguimento urológico e definição de tratamento definitivo.",
        "temas_estudo": [
            "LUTS masculinos",
            "Retenção urinária",
            "Obstrução prostática com repercussão renal",
        ],
        "fontes_clinicas": [
            _source(
                "EAU Guidelines on Non-neurogenic Male LUTS: Diagnostic Evaluation",
                "European Association of Urology",
                2026,
                "https://uroweb.org/guidelines/management-of-non-neurogenic-male-luts/chapter/diagnostic-evaluation",
            )
        ],
    },
    40: {
        "diagnostico_referencia": "Pielonefrite aguda direita com sinais sistêmicos, sem obstrução demonstrada.",
        "diagnostico_termos": [
            "pielonefrite aguda",
            "pielonefrite direita",
            "infeccao urinaria alta",
        ],
        "diagnostico_parcial": [
            "infeccao urinaria",
            "itu",
            "infeccao urinaria sistemica",
        ],
        "exames_essenciais": [
            "urina1",
            "urocultura",
            "hemo",
            "funcao_renal_eletrolitos",
        ],
        "exames_opcionais": ["hemoculturas", "usg_vias_urinarias"],
        "exames_desnecessarios": ["tc_abdome"],
        "justificativa_exames": {
            "urina1": "Leucocitúria, nitrito e cilindros apoiam infecção do trato urinário superior.",
            "urocultura": "É recomendada em todos os casos para identificação e ajuste do antimicrobiano.",
            "hemo": "Ajuda a avaliar resposta sistêmica e gravidade.",
            "funcao_renal_eletrolitos": "Avalia repercussão e orienta escolha e dose de antimicrobianos.",
            "hemoculturas": "São consideradas diante de doença sistêmica grave ou suspeita de sepse.",
            "usg_vias_urinarias": "Pesquisa obstrução ou cálculo quando há fatores de risco ou dúvida clínica.",
            "tc_abdome": "Não é obrigatória de rotina sem deterioração, suspeita de complicação ou falha após 48–72 horas.",
        },
        "conduta_criterios": [
            {
                "nome": "Antimicrobiano empírico adequado",
                "pontos": 10,
                "termos": [
                    "antibiotico",
                    "antimicrobiano",
                    "ceftriaxona",
                    "fluoroquinolona",
                    "cefalosporina",
                ],
            },
            {
                "nome": "Suporte e estratificação",
                "pontos": 10,
                "termos": [
                    "hidratacao",
                    "cristaloide",
                    "analgesia",
                    "antitermico",
                    "internacao",
                    "gravidade",
                ],
            },
            {
                "nome": "Cultura, reavaliação e ajuste",
                "pontos": 10,
                "termos": [
                    "urocultura",
                    "antibiograma",
                    "ajustar antibiotico",
                    "reavaliar",
                    "48",
                    "72",
                ],
            },
        ],
        "conduta_referencia": "Coletar urocultura, iniciar antimicrobiano empírico conforme gravidade, fatores individuais e resistência local, oferecer hidratação e controle sintomático, decidir necessidade de internação e reavaliar em 48–72 horas, ajustando pela cultura.",
        "feedback_hipotese_parcial": "Você reconheceu infecção urinária, mas febre, dor lombar e Giordano positivo indicam acometimento renal.",
        "feedback_hipotese_incorreta": "A combinação de febre, calafrios, dor lombar, sintomas urinários e Giordano positivo é típica de pielonefrite.",
        "feedback_seguranca": "Nitrofurantoína e fosfomicina oral não são adequadas para pielonefrite; sinais de gravidade ou obstrução exigem escalonamento e imagem.",
        "objetivos_aprendizagem": [
            "Diagnosticar pielonefrite",
            "Estratificar gravidade e obstrução",
            "Usar cultura e reavaliação para orientar tratamento",
        ],
        "criterios_seguranca": [
            {
                "nome": "Antimicrobiano efetivo no parênquima renal",
                "termos": [
                    "ceftriaxona",
                    "fluoroquinolona",
                    "cefalosporina",
                    "antibiotico intravenoso",
                    "antimicrobiano",
                ],
                "feedback_omissao": "Sem antimicrobiano apropriado, a infecção pode progredir para sepse.",
            },
            {
                "nome": "Reavaliar gravidade e obstrução",
                "termos": [
                    "reavaliar",
                    "internacao",
                    "imagem",
                    "ultrassom",
                    "obstrucao",
                    "sepse",
                ],
                "feedback_omissao": "Piora ou ausência de resposta exige busca de obstrução e complicações.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Com hidratação e antimicrobiano adequado, febre, taquicardia e dor começam a regredir.",
                "desfecho": "A cultura permite ajuste do tratamento e a paciente é reavaliada em 48–72 horas.",
                "reavaliacao": [
                    {
                        "indicador": "Temperatura",
                        "antes": "38,6 °C",
                        "depois": "tendência de queda",
                        "tendencia": "melhora",
                    }
                ],
            },
            "parcial": {
                "reacao": "A melhora é incompleta se faltam cultura, avaliação de gravidade ou seguimento definido.",
                "desfecho": "A paciente necessita reavaliação precoce para corrigir o plano.",
            },
            "insegura": {
                "reacao": "Sem antimicrobiano apropriado ou diante de obstrução não reconhecida, febre e instabilidade podem piorar.",
                "desfecho": "Há risco de urosepse, abscesso ou dano renal.",
                "reavaliacao": [
                    {
                        "indicador": "Estado sistêmico",
                        "antes": "febre e taquicardia",
                        "depois": "deterioração prevista",
                        "tendencia": "piora",
                    }
                ],
            },
        },
        "reacao_paciente_referencia": "A resposta é acompanhada por febre, dor, tolerância oral, pressão, frequência cardíaca e função renal.",
        "desfecho_referencia": "Resposta inadequada em 48–72 horas requer nova cultura, imagem e busca de complicação.",
        "temas_estudo": [
            "Pielonefrite",
            "Urocultura e resistência",
            "Obstrução e urosepse",
        ],
        "fontes_clinicas": [
            _source(
                "EAU Guidelines on Urological Infections: Pyelonephritis",
                "European Association of Urology",
                2026,
                "https://uroweb.org/guidelines/urological-infections/chapter/the-guideline",
            )
        ],
    },
}


# Casos cuja liberação educacional foi aprovada pela Administração MedSync.
# O feedback continua sujeito ao aviso educacional exibido pela plataforma.
RELEASED_CLINICAL_RUBRIC_IDS = frozenset({33, 36, 38, 39, 40})


CLINICAL_CASE_EXAM_UPDATES: dict[int, list[dict[str, Any]]] = {
    6: [
        {
            "id": "eda",
            "nome": "Endoscopia Digestiva Alta",
            "resultado": "Não é exame inicial de rotina diante de perfuração com peritonite.",
            "correto": False,
        },
        {
            "id": "tc_abdome",
            "nome": "TC de abdome com contraste",
            "resultado": "Pneumoperitônio e descontinuidade da parede gastroduodenal, compatíveis com perfuração.",
            "correto": True,
        },
        {
            "id": "gaso_lactato",
            "nome": "Gasometria e lactato",
            "resultado": "Lactato elevado, compatível com hipoperfusão inicial.",
            "correto": True,
        },
    ],
    11: [
        {
            "id": "campimetria",
            "nome": "Campimetria visual",
            "resultado": "Defeito de campo visual compatível com compressão quiasmática.",
            "correto": True,
        },
        {
            "id": "beta_hcg",
            "nome": "Beta-HCG",
            "resultado": "Negativo.",
            "correto": True,
        },
        {
            "id": "funcao_renal",
            "nome": "Função renal",
            "resultado": "Sem alterações.",
            "correto": True,
        },
    ],
    12: [
        {
            "id": "eletrolitos",
            "nome": "Eletrólitos",
            "resultado": "Sódio e potássio sem alterações relevantes.",
            "correto": True,
        },
        {
            "id": "perfil_metabolico",
            "nome": "Perfil metabólico",
            "resultado": "Dislipidemia e hipertensão associadas à exposição crônica a glicocorticoide.",
            "correto": True,
        },
    ],
    33: [
        {
            "id": "dea",
            "nome": "Análise imediata do ritmo (DEA/monitor)",
            "resultado": "Fibrilação ventricular, ritmo chocável.",
            "correto": True,
        },
        {
            "id": "glicemia_capilar",
            "nome": "Glicemia capilar",
            "resultado": "118 mg/dL.",
            "correto": False,
        },
        {
            "id": "ecg_12_derivacoes",
            "nome": "ECG de 12 derivações durante a parada",
            "resultado": "Não deve atrasar RCP, desfibrilação e análise do ritmo; considerar após retorno da circulação espontânea.",
            "correto": False,
        },
    ],
    36: [
        {
            "id": "lactato",
            "nome": "Lactato sérico",
            "resultado": "2,1 mmol/L, acima do valor de referência do laboratório.",
            "correto": True,
        },
        {
            "id": "hemoculturas",
            "nome": "Hemoculturas (dois conjuntos)",
            "resultado": "Amostras coletadas antes do antimicrobiano; crescimento ainda não disponível.",
            "correto": True,
        },
        {
            "id": "funcao_renal_eletrolitos",
            "nome": "Função renal e eletrólitos",
            "resultado": "Creatinina 1,8 mg/dL, sódio 132 mEq/L e potássio 3,4 mEq/L.",
            "correto": True,
        },
        {
            "id": "tc_abdome",
            "nome": "TC de abdome com contraste, após estabilização inicial",
            "resultado": "Colite extensa, sem pneumoperitônio ou coleção drenável.",
            "correto": True,
        },
        {
            "id": "colonoscopia",
            "nome": "Colonoscopia imediata",
            "resultado": "Exame adiado por instabilidade clínica e risco de atrasar a ressuscitação.",
            "correto": False,
        },
    ],
    38: [
        {
            "id": "raiox_torax",
            "nome": "Raio-X de tórax",
            "resultado": "Infiltrado alveolar bilateral em asa de borboleta e cardiomegalia.",
            "correto": True,
        },
        {
            "id": "bnp",
            "nome": "BNP",
            "resultado": "1.120 pg/mL, elevado.",
            "correto": True,
        },
        {
            "id": "ecg",
            "nome": "ECG de 12 derivações",
            "resultado": "Taquicardia sinusal e critérios de sobrecarga ventricular esquerda, sem supradesnivelamento de ST.",
            "correto": True,
        },
        {
            "id": "gaso",
            "nome": "Gasometria arterial",
            "resultado": "Hipoxemia importante e alcalose respiratória inicial.",
            "correto": True,
        },
        {
            "id": "funcao_renal_eletrolitos",
            "nome": "Função renal e eletrólitos",
            "resultado": "Creatinina 1,4 mg/dL; sódio e potássio sem alterações críticas.",
            "correto": True,
        },
    ],
    39: [
        {
            "id": "psa",
            "nome": "PSA total",
            "resultado": "6,0 ng/mL; resultado que exige interpretação conforme idade, volume prostático e contexto clínico.",
            "correto": True,
        },
        {
            "id": "usg_vias_urinarias",
            "nome": "USG de rins e vias urinárias com resíduo pós-miccional",
            "resultado": "Próstata estimada em 70 g, parede vesical espessada, resíduo pós-miccional elevado e hidroureteronefrose bilateral.",
            "correto": True,
        },
        {
            "id": "urina1",
            "nome": "Urina tipo 1",
            "resultado": "Sem leucocitúria, nitrito, hematúria ou proteinúria significativas.",
            "correto": True,
        },
        {
            "id": "funcao_renal",
            "nome": "Função renal",
            "resultado": "Creatinina 2,0 mg/dL, com redução da função renal em contexto de obstrução urinária.",
            "correto": True,
        },
        {
            "id": "urofluxometria",
            "nome": "Urofluxometria",
            "resultado": "Fluxo urinário máximo reduzido, compatível com obstrução infravesical.",
            "correto": True,
        },
    ],
    40: [
        {
            "id": "urocultura",
            "nome": "Urocultura com antibiograma",
            "resultado": "Crescimento de Escherichia coli; antibiograma pendente no momento da decisão inicial.",
            "correto": True,
        },
        {
            "id": "funcao_renal_eletrolitos",
            "nome": "Função renal e eletrólitos",
            "resultado": "Creatinina 1,3 mg/dL, sem distúrbio eletrolítico grave.",
            "correto": True,
        },
        {
            "id": "hemoculturas",
            "nome": "Hemoculturas",
            "resultado": "Sem crescimento nas primeiras horas; resultado definitivo pendente.",
            "correto": True,
        },
        {
            "id": "usg_vias_urinarias",
            "nome": "USG de rins e vias urinárias",
            "resultado": "Sem hidronefrose ou cálculo obstrutivo.",
            "correto": True,
        },
        {
            "id": "tc_abdome",
            "nome": "TC de abdome",
            "resultado": "Reservada para suspeita de obstrução, complicação ou ausência de resposta clínica; não é obrigatória de rotina neste momento.",
            "correto": False,
        },
    ],
}

CLINICAL_CASE_EXAM_UPDATES.update(FIRST_FEEDBACK_BATCH_EXAM_UPDATES)
CLINICAL_CASE_EXAM_UPDATES.update(SECOND_FEEDBACK_BATCH_EXAM_UPDATES)
CLINICAL_CASE_EXAM_UPDATES.update(THIRD_FEEDBACK_BATCH_EXAM_UPDATES)
CLINICAL_CASE_EXAM_UPDATES.update(FOURTH_FEEDBACK_BATCH_EXAM_UPDATES)
CLINICAL_CASE_EXAM_UPDATES.update(FIFTH_FEEDBACK_BATCH_EXAM_UPDATES)
CLINICAL_CASE_EXAM_UPDATES.update(FINAL_FEEDBACK_BATCH_EXAM_UPDATES)
