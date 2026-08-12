"""Rubricas clínicas revisáveis usadas pela Simulação Clínica 2.1."""

from typing import Any

CLINICAL_RUBRIC_VERSION = 4


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
                "termos": ["abc", "acesso venoso", "cristaloide", "reposicao volemica", "monitorizacao", "ressuscitacao"],
            },
            {
                "nome": "Jejum e descompressão",
                "pontos": 4,
                "termos": ["jejum", "dieta zero", "sonda nasogastrica", "descompressao"],
            },
            {
                "nome": "Antibiótico e supressão ácida",
                "pontos": 6,
                "termos": ["antibiotico", "antimicrobiano", "piperacilina", "ceftriaxona", "metronidazol", "inibidor de bomba", "omeprazol", "pantoprazol"],
            },
            {
                "nome": "Avaliação cirúrgica e controle da fonte",
                "pontos": 12,
                "termos": ["cirurgia", "cirurgiao", "laparoscopia", "laparotomia", "rafia", "controle da fonte", "abordagem cirurgica"],
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
            {"nome": "Acionamento cirúrgico imediato", "termos": ["cirurgia", "cirurgiao", "laparoscopia", "laparotomia"], "feedback_omissao": "A ausência de avaliação cirúrgica imediata pode atrasar o controle da fonte."},
            {"nome": "Antibioticoterapia precoce", "termos": ["antibiotico", "antimicrobiano", "piperacilina", "ceftriaxona"], "feedback_omissao": "Peritonite por perfuração exige cobertura antimicrobiana precoce."},
        ],
        "desfechos_conduta": {
            "adequada": {"reacao": "Após reanimação e tratamento inicial, a perfusão e a taquicardia tendem a melhorar enquanto a equipe prepara o controle da fonte.", "desfecho": "O paciente segue para abordagem cirúrgica urgente e monitorização pós-operatória, com prognóstico dependente do tempo até o controle da perfuração."},
            "parcial": {"reacao": "Há melhora incompleta dos parâmetros, mas a contaminação peritoneal continua enquanto faltam medidas essenciais.", "desfecho": "O atraso no antibiótico ou na cirurgia aumenta o risco de sepse, disfunção orgânica e internação prolongada."},
            "insegura": {"reacao": "Sem reanimação e controle da fonte, o paciente mantém taquicardia e pode evoluir com hipotensão e piora da perfusão.", "desfecho": "A progressão para sepse e choque torna-se provável se a emergência cirúrgica não for reconhecida."},
        },
        "reacao_paciente_referencia": "A resposta depende da rapidez da reanimação e do controle da fonte.",
        "desfecho_referencia": "O tratamento definitivo requer avaliação cirúrgica urgente e acompanhamento hospitalar.",
        "temas_estudo": ["Abdome agudo perfurativo", "Reanimação na sepse abdominal", "Controle da fonte em perfuração gastroduodenal"],
        "fontes_clinicas": [
            _source("Perforated and bleeding peptic ulcer: WSES guidelines", "World Society of Emergency Surgery", 2020, "https://doi.org/10.1186/s13017-019-0283-9"),
        ],
    },
    7: {
        "diagnostico_referencia": "Anemia ferropriva grave após bypass gástrico.",
        "diagnostico_termos": ["anemia ferropriva", "deficiencia de ferro", "anemia por deficiencia de ferro"],
        "diagnostico_parcial": ["anemia microcitica", "anemia carencial", "anemia pos bariatrica"],
        "exames_essenciais": ["hemo", "ferro"],
        "exames_opcionais": ["vit_b12"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "hemo": "Confirma anemia grave com padrão microcítico e hipocrômico.",
            "ferro": "Ferritina reduzida e capacidade de ligação elevada sustentam deficiência de ferro.",
            "vit_b12": "Pode avaliar deficiências concomitantes após cirurgia bariátrica, embora não explique o padrão apresentado.",
        },
        "conduta_criterios": [
            {"nome": "Avaliação e estabilização urgente", "pontos": 8, "termos": ["urgencia", "internacao", "estabilizacao", "transfusao", "hemacias", "hemodinamica"]},
            {"nome": "Reposição de ferro adequada à gravidade", "pontos": 10, "termos": ["ferro intravenoso", "ferro venoso", "reposicao parenteral", "carboximaltose", "sacarato"]},
            {"nome": "Pesquisa de causas e deficiências associadas", "pontos": 6, "termos": ["sangramento", "perdas", "b12", "folato", "nutricional", "deficiencias"]},
            {"nome": "Seguimento bariátrico e laboratorial", "pontos": 6, "termos": ["seguimento", "acompanhamento", "bariatrica", "nutricionista", "reavaliar", "hemograma", "ferritina"]},
        ],
        "conduta_referencia": (
            "Avaliar estabilidade e sintomas em caráter urgente, considerar suporte transfusional conforme o quadro, "
            "realizar reposição de ferro — frequentemente intravenosa diante de anemia grave ou má absorção —, "
            "pesquisar perdas e outras deficiências e manter seguimento bariátrico com controle laboratorial."
        ),
        "feedback_hipotese_parcial": "O padrão microcítico foi reconhecido, mas faltou relacioná-lo à deficiência de ferro após o bypass.",
        "feedback_hipotese_incorreta": "Hemoglobina muito baixa, microcitose, ferritina reduzida e TIBC elevado caracterizam anemia ferropriva grave.",
        "feedback_seguranca": "Hemoglobina de 4 g/dL com sintomas exige avaliação urgente; reposição oral isolada pode ser insuficiente após bypass e nesta gravidade.",
        "objetivos_aprendizagem": ["Interpretar o perfil de ferro", "Reconhecer gravidade da anemia sintomática", "Planejar reposição e seguimento pós-bariátrico"],
        "criterios_seguranca": [
            {"nome": "Reconhecimento da gravidade", "termos": ["urgencia", "internacao", "transfusao", "estabilizacao"], "feedback_omissao": "A gravidade da anemia sintomática precisa ser reconhecida antes do tratamento ambulatorial."},
            {"nome": "Estratégia compatível com má absorção", "termos": ["ferro intravenoso", "ferro venoso", "parenteral"], "feedback_omissao": "Considere via intravenosa diante de anemia grave e absorção reduzida pelo bypass."},
        ],
        "desfechos_conduta": {
            "adequada": {"reacao": "Com estabilização e reposição apropriada, palpitações, dispneia e tontura tendem a regredir progressivamente.", "desfecho": "A paciente permanece em acompanhamento até recuperação hematológica e reposição dos estoques de ferro."},
            "parcial": {"reacao": "Pode haver melhora lenta, mas sintomas e baixa reserva persistem se a gravidade ou a má absorção forem subestimadas.", "desfecho": "Sem ajuste da via de reposição e seguimento, aumenta o risco de resposta inadequada e recorrência."},
            "insegura": {"reacao": "Sem avaliação urgente, a paciente mantém sintomas de hipóxia tecidual e risco de instabilidade.", "desfecho": "O atraso no suporte e na reposição efetiva pode levar a complicações cardiovasculares e necessidade de atendimento emergencial."},
        },
        "reacao_paciente_referencia": "A melhora depende de estabilização e reposição efetiva do ferro.",
        "desfecho_referencia": "O seguimento deve confirmar recuperação da hemoglobina e dos estoques.",
        "temas_estudo": ["Anemia ferropriva", "Deficiências após bypass gástrico", "Indicações de ferro intravenoso"],
        "fontes_clinicas": [
            _source("Clinical Practice Guidelines for perioperative support of the bariatric surgery patient", "AACE/TOS/ASMBS/OMA/ASA", 2020, "https://asmbs.org/resources/aace-tos-asmbs-oma-asa-clinical-practice-guidelines-for-the-perioperative-nutritional-metabolic-and-nonsurgical-support-of-the-bariatric-surgery-patient-2020/"),
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
            {"nome": "Estabilização e oxigenoterapia", "pontos": 8, "termos": ["oxigenio", "oxigenoterapia", "suporte ventilatorio", "abc", "estabilizacao"]},
            {"nome": "Anticoagulação", "pontos": 12, "termos": ["anticoagulacao", "heparina", "enoxaparina", "anticoagulante"]},
            {"nome": "Estratificação de risco", "pontos": 6, "termos": ["estratificacao de risco", "estabilidade hemodinamica", "instabilidade hemodinamica", "reperfusao", "trombolise"]},
            {"nome": "Internação e monitorização", "pontos": 4, "termos": ["internacao", "monitorizacao", "monitoramento", "hospitalar"]},
        ],
        "conduta_referencia": "Estabilizar, ofertar oxigênio e monitorizar; iniciar anticoagulação se não houver contraindicação; estratificar risco hemodinâmico e avaliar reperfusão; manter acompanhamento hospitalar.",
        "feedback_hipotese_parcial": "Você reconheceu o fenômeno trombótico, mas precisa explicitar o tromboembolismo pulmonar.",
        "feedback_hipotese_incorreta": "A hipótese não identificou o tromboembolismo pulmonar, mais provável diante da apresentação.",
        "feedback_seguranca": "A hipoxemia exige estabilização e monitorização; anticoagulação e reperfusão dependem de contraindicações e estabilidade.",
        "objetivos_aprendizagem": ["Reconhecer TEP de alta probabilidade", "Selecionar exames de valor", "Estratificar risco e tratar com segurança"],
        "criterios_seguranca": [
            {"nome": "Suporte da hipoxemia", "termos": ["oxigenio", "oxigenoterapia", "suporte ventilatorio", "abc"], "feedback_omissao": "Saturação de 83% exige suporte e monitorização imediatos."},
            {"nome": "Anticoagulação quando segura", "termos": ["anticoagulacao", "heparina", "enoxaparina"], "feedback_omissao": "A ausência de anticoagulação sem justificativa mantém progressão trombótica."},
        ],
        "desfechos_conduta": {
            "adequada": {"reacao": "Com suporte, anticoagulação e monitorização, a hipoxemia tende a melhorar e a progressão trombótica é contida.", "desfecho": "A paciente permanece internada e monitorizada para estratificação; se estável, evolui com melhora, e se deteriorar deve ser reavaliada para reperfusão."},
            "parcial": {"reacao": "A resposta é incompleta enquanto faltam medidas de suporte, anticoagulação ou estratificação.", "desfecho": "Persistem risco respiratório e trombótico até que as omissões sejam corrigidas."},
            "insegura": {"reacao": "Sem suporte e tratamento antitrombótico, a hipoxemia e a sobrecarga cardiovascular podem piorar.", "desfecho": "Há risco de instabilidade hemodinâmica e necessidade de terapia de reperfusão emergencial."},
        },
        "reacao_paciente_referencia": "A resposta depende do suporte e do tratamento antitrombótico.",
        "desfecho_referencia": "A paciente requer internação, estratificação e reavaliação contínua.",
        "temas_estudo": ["Probabilidade pré-teste para TEP", "Limitações do D-dímero", "Estratificação e tratamento do TEP"],
        "fontes_clinicas": [
            _source("ASH Guidelines for treatment of DVT and PE", "American Society of Hematology", 2020, "https://doi.org/10.1182/bloodadvances.2020001830"),
            _source("ASH Guidelines for VTE in patients with cancer", "American Society of Hematology", 2021, "https://doi.org/10.1182/bloodadvances.2020003442"),
        ],
    },
    11: {
        "diagnostico_referencia": "Macroprolactinoma com compressão do quiasma óptico.",
        "diagnostico_termos": ["macroprolactinoma", "prolactinoma", "macroadenoma secretor de prolactina"],
        "diagnostico_parcial": ["macroadenoma hipofisario", "adenoma hipofisario", "hiperprolactinemia"],
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
            {"nome": "Agonista dopaminérgico", "pontos": 15, "termos": ["cabergolina", "agonista dopaminergico", "bromocriptina"]},
            {"nome": "Avaliação visual e neurológica urgente", "pontos": 6, "termos": ["campimetria", "campo visual", "oftalmologia", "avaliacao visual", "neurocirurgia", "urgente"]},
            {"nome": "Avaliação dos eixos hipofisários", "pontos": 5, "termos": ["eixos hipofisarios", "funcao hipofisaria", "cortisol", "tsh", "t4", "endocrinologia"]},
            {"nome": "Monitorização de resposta", "pontos": 4, "termos": ["repetir prolactina", "controle de prolactina", "nova ressonancia", "acompanhamento", "monitorizacao"]},
        ],
        "conduta_referencia": "Avaliar com urgência o déficit visual e sinais neurológicos, iniciar cabergolina quando clinicamente apropriado, avaliar demais eixos hipofisários e acompanhar prolactina, sintomas visuais e volume tumoral; discutir cirurgia se houver indicação ou falha terapêutica.",
        "feedback_hipotese_parcial": "Hiperprolactinemia ou macroadenoma isoladamente não sintetizam o caso; integre secreção de prolactina e compressão quiasmática.",
        "feedback_hipotese_incorreta": "Prolactina muito elevada associada a macroadenoma e sintomas visuais sustenta macroprolactinoma.",
        "feedback_seguranca": "Diplopia e compressão do quiasma exigem avaliação visual/neurológica rápida e rastreio de insuficiência hipofisária.",
        "objetivos_aprendizagem": ["Diagnosticar macroprolactinoma", "Avaliar repercussão visual", "Planejar tratamento e monitorização"],
        "criterios_seguranca": [
            {"nome": "Avaliação visual urgente", "termos": ["campimetria", "campo visual", "oftalmologia", "urgente"], "feedback_omissao": "A compressão quiasmática exige documentação e vigilância visual rápidas."},
            {"nome": "Avaliação de função hipofisária", "termos": ["eixos hipofisarios", "cortisol", "funcao hipofisaria", "endocrinologia"], "feedback_omissao": "Macroadenomas podem comprometer outros eixos, inclusive o corticotrófico."},
        ],
        "desfechos_conduta": {
            "adequada": {"reacao": "Com agonista dopaminérgico e vigilância adequada, a prolactina tende a cair e os sintomas compressivos podem melhorar.", "desfecho": "Espera-se redução tumoral e recuperação clínica, com seguimento hormonal, visual e por imagem."},
            "parcial": {"reacao": "A resposta pode ocorrer, mas déficits visuais ou hormonais podem não ser detectados sem avaliação completa.", "desfecho": "O acompanhamento incompleto aumenta o risco de persistência de compressão ou deficiência hipofisária."},
            "insegura": {"reacao": "Sem tratamento e avaliação urgente, cefaleia e alterações visuais podem persistir ou progredir.", "desfecho": "Há risco de dano visual e atraso no reconhecimento de complicações do macroadenoma."},
        },
        "reacao_paciente_referencia": "A resposta deve ser acompanhada por sintomas, prolactina, campo visual e imagem.",
        "desfecho_referencia": "O objetivo é normalização hormonal e redução tumoral com preservação visual.",
        "temas_estudo": ["Investigação da hiperprolactinemia", "Agonistas dopaminérgicos", "Síndromes compressivas hipofisárias"],
        "fontes_clinicas": [
            _source("Diagnosis and management of prolactin-secreting pituitary adenomas", "Pituitary Society", 2023, "https://doi.org/10.1038/s41574-023-00886-5"),
        ],
    },
    12: {
        "diagnostico_referencia": "Síndrome de Cushing exógena por uso crônico de betametasona, com supressão do eixo hipotálamo-hipófise-adrenal.",
        "diagnostico_termos": ["cushing exogeno", "cushing iatrogenico", "sindrome de cushing iatrogenica", "hipercortisolismo exogeno"],
        "diagnostico_parcial": ["sindrome de cushing", "supressao do eixo hpa", "insuficiencia adrenal induzida por glicocorticoide"],
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
            {"nome": "Reconhecer e retirar a fonte com segurança", "pontos": 10, "termos": ["suspender betametasona", "retirar betametasona", "interromper descongestionante", "fonte exogena", "glicocorticoide exogeno"]},
            {"nome": "Desmame gradual ou troca por ação curta", "pontos": 10, "termos": ["desmame gradual", "reduzir gradualmente", "taper", "hidrocortisona", "prednisona", "curta acao"]},
            {"nome": "Avaliar recuperação do eixo", "pontos": 5, "termos": ["cortisol matinal", "eixo hpa", "recuperacao do eixo", "insuficiencia adrenal", "endocrinologia"]},
            {"nome": "Prevenir e tratar complicações", "pontos": 5, "termos": ["pressao arterial", "hipertensao", "osteoporose", "glicemia", "infeccao", "educacao", "dose de estresse"]},
        ],
        "conduta_referencia": "Interromper a exposição inadequada sob supervisão, evitando suspensão abrupta; quando possível, substituir glicocorticoide de ação longa por ação curta e realizar desmame gradual, avaliar recuperação do eixo e orientar sobre insuficiência adrenal e doses de estresse, além de tratar complicações.",
        "feedback_hipotese_parcial": "O fenótipo de Cushing precisa ser relacionado ao uso crônico de betametasona e à supressão do eixo.",
        "feedback_hipotese_incorreta": "A exposição prolongada a glicocorticoide, o fenótipo típico e ACTH/cortisol suprimidos apontam para Cushing exógeno.",
        "feedback_seguranca": "Após uso crônico, a suspensão abrupta pode precipitar insuficiência adrenal; o desmame e a educação sobre estresse são essenciais.",
        "objetivos_aprendizagem": ["Reconhecer Cushing exógeno", "Evitar retirada abrupta", "Avaliar recuperação do eixo HPA e complicações"],
        "criterios_seguranca": [
            {"nome": "Evitar suspensão abrupta", "termos": ["desmame gradual", "reduzir gradualmente", "taper", "hidrocortisona", "prednisona"], "feedback_omissao": "Suspensão abrupta após exposição prolongada pode precipitar insuficiência adrenal."},
            {"nome": "Orientação para situações de estresse", "termos": ["dose de estresse", "stress dose", "cartao de emergencia", "educacao", "insuficiencia adrenal"], "feedback_omissao": "O paciente precisa saber reconhecer insuficiência adrenal e manejar situações de estresse."},
        ],
        "desfechos_conduta": {
            "adequada": {"reacao": "Com retirada supervisionada e desmame, a exposição excessiva cessa sem perda abrupta da cobertura glicocorticoide.", "desfecho": "Os sinais cushingoides regridem gradualmente enquanto o eixo é monitorado até recuperação, com controle das complicações."},
            "parcial": {"reacao": "Algumas complicações podem melhorar, mas permanece risco de sintomas de retirada ou insuficiência se o plano não contemplar o eixo HPA.", "desfecho": "A recuperação pode ser prolongada e requer ajuste do desmame e seguimento endocrinológico."},
            "insegura": {"reacao": "A suspensão abrupta pode causar fraqueza, náuseas, hipotensão e descompensação adrenal.", "desfecho": "Sem orientação e cobertura adequada, existe risco de crise adrenal diante de doença ou estresse."},
        },
        "reacao_paciente_referencia": "A resposta depende de retirada supervisionada e proteção contra insuficiência adrenal.",
        "desfecho_referencia": "A recuperação do eixo varia e deve ser monitorada durante o desmame.",
        "temas_estudo": ["Cushing exógeno", "Desmame de glicocorticoides", "Insuficiência adrenal induzida por glicocorticoide"],
        "fontes_clinicas": [
            _source("Diagnosis and therapy of glucocorticoid-induced adrenal insufficiency", "European Society of Endocrinology and Endocrine Society", 2024, "https://doi.org/10.1210/clinem/dgae250"),
        ],
    },
}


CLINICAL_CASE_EXAM_UPDATES: dict[int, list[dict[str, Any]]] = {
    6: [
        {"id": "eda", "nome": "Endoscopia Digestiva Alta", "resultado": "Não é exame inicial de rotina diante de perfuração com peritonite.", "correto": False},
        {"id": "tc_abdome", "nome": "TC de abdome com contraste", "resultado": "Pneumoperitônio e descontinuidade da parede gastroduodenal, compatíveis com perfuração.", "correto": True},
        {"id": "gaso_lactato", "nome": "Gasometria e lactato", "resultado": "Lactato elevado, compatível com hipoperfusão inicial.", "correto": True},
    ],
    11: [
        {"id": "campimetria", "nome": "Campimetria visual", "resultado": "Defeito de campo visual compatível com compressão quiasmática.", "correto": True},
        {"id": "beta_hcg", "nome": "Beta-HCG", "resultado": "Negativo.", "correto": True},
        {"id": "funcao_renal", "nome": "Função renal", "resultado": "Sem alterações.", "correto": True},
    ],
    12: [
        {"id": "eletrolitos", "nome": "Eletrólitos", "resultado": "Sódio e potássio sem alterações relevantes.", "correto": True},
        {"id": "perfil_metabolico", "nome": "Perfil metabólico", "resultado": "Dislipidemia e hipertensão associadas à exposição crônica a glicocorticoide.", "correto": True},
    ],
}
