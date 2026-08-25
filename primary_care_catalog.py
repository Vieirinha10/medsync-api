"""Casos introdutórios e rubricas para situações frequentes na atenção primária."""

from typing import Any


def _exam(
    code: str,
    name: str,
    result: str,
    *,
    appropriate: bool = True,
) -> dict[str, Any]:
    return {
        "id": code,
        "nome": name,
        "resultado": result,
        "correto": appropriate,
    }


def _case(
    case_id: int,
    title: str,
    specialty: str,
    history: str,
    physical_exam: str,
    exams: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": case_id,
        "titulo": title,
        "especialidade": specialty,
        "nivel_dificuldade": "Fácil",
        "historia_clinica": history,
        "exame_fisico": physical_exam,
        "exames_disponiveis": exams,
    }


PRIMARY_CARE_TITLES = {
    41: "Minha garganta está doendo",
    42: "Ele passou a noite chorando",
    43: "Essa secreção não melhora",
    44: "Comecei a chiar novamente",
    45: "Arde quando vou ao banheiro",
    46: "Estou com corrimento e coceira",
    47: "Meu corpo inteiro está doendo",
    48: "Não consigo parar de ir ao banheiro",
    49: "Sinto uma queimação depois de comer",
    50: "Todo mundo em casa começou a coçar",
    51: "Essa mancha está aumentando",
    52: "Travei a coluna depois do trabalho",
    53: "Minha pressão está alta",
    54: "Minha glicose vive descontrolada",
    55: "Acordei com o olho vermelho",
}


PRIMARY_CARE_CASES = [
    _case(
        41,
        "Infecção viral de vias aéreas superiores",
        "Medicina de Família e Comunidade",
        (
            "LFS, 24 anos, relata dor de garganta, coriza e tosse seca há dois dias. "
            "Nega falta de ar, dificuldade para engolir saliva, exantema ou contato "
            "conhecido com pessoa com infecção estreptocócica. Alimenta-se e hidrata-se bem."
        ),
        (
            "BEG, hidratado. Temperatura: 37,4 °C; FC: 82 bpm; FR: 16 irpm; "
            "SpO2: 98%. Orofaringe discretamente hiperemiada, sem exsudato; "
            "sem linfonodos cervicais dolorosos e sem sinais de obstrução de via aérea."
        ),
        [
            _exam(
                "teste_estreptococo",
                "Teste rápido para estreptococo",
                "Negativo.",
                appropriate=False,
            ),
            _exam(
                "hemograma",
                "Hemograma",
                "Sem leucocitose ou outras alterações relevantes.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        42,
        "Otite média aguda não complicada",
        "Pediatria",
        (
            "MRS, 3 anos, levado pela mãe por dor no ouvido direito e irritabilidade "
            "desde a noite anterior, após quatro dias de coriza. Aceita líquidos. "
            "Nega vômitos persistentes, convulsão, edema atrás da orelha ou prostração."
        ),
        (
            "REG, responsivo e hidratado. Temperatura: 38,1 °C; FC: 108 bpm; "
            "FR: 24 irpm. Otoscopia direita com membrana timpânica abaulada, opaca "
            "e com mobilidade reduzida; sem edema ou dor mastoidea."
        ),
        [
            _exam(
                "timpanometria",
                "Timpanometria",
                "Curva tipo B à direita, compatível com efusão em orelha média.",
            ),
            _exam(
                "tomografia_mastoide",
                "TC de mastoides",
                "Sem sinais de mastoidite.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        43,
        "Rinossinusite aguda viral",
        "Medicina de Família e Comunidade",
        (
            "ACA, 31 anos, apresenta obstrução nasal, secreção amarelada e pressão "
            "facial leve há cinco dias. Os sintomas começaram junto de um resfriado "
            "e não houve piora após melhora inicial. Nega edema ao redor dos olhos, "
            "alteração visual, cefaleia intensa ou febre persistente."
        ),
        (
            "BEG. Temperatura: 37,3 °C; FC: 78 bpm; FR: 16 irpm; SpO2: 99%. "
            "Mucosa nasal edemaciada, dor leve à palpação maxilar, sem edema orbitário "
            "ou sinais neurológicos."
        ),
        [
            _exam(
                "tomografia_seios_face",
                "TC dos seios da face",
                "Espessamento mucoso inespecífico, sem complicações.",
                appropriate=False,
            ),
            _exam(
                "hemograma",
                "Hemograma",
                "Sem alterações relevantes.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        44,
        "Exacerbação leve de asma",
        "Pneumologia",
        (
            "JPF, 22 anos, com asma conhecida, relata chiado e aperto no peito após "
            "limpar um cômodo com muita poeira. Usou o inalador de alívio uma vez, "
            "com melhora parcial. Fala frases completas e nega febre ou dor torácica."
        ),
        (
            "BEG, sem uso de musculatura acessória. FC: 92 bpm; FR: 22 irpm; "
            "SpO2: 96%. Sibilos expiratórios difusos e murmúrio vesicular preservado. "
            "Pico de fluxo expiratório: 78% do melhor valor pessoal."
        ),
        [
            _exam(
                "pico_fluxo",
                "Pico de fluxo expiratório após broncodilatador",
                "Melhora para 88% do melhor valor pessoal.",
            ),
            _exam(
                "raiox_torax",
                "Radiografia de tórax",
                "Sem consolidações ou pneumotórax.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        45,
        "Cistite aguda não complicada",
        "Medicina de Família e Comunidade",
        (
            "BMS, 28 anos, não gestante, com ardor ao urinar, urgência e aumento da "
            "frequência urinária há dois dias. Nega corrimento vaginal, febre, dor "
            "lombar, náuseas ou vômitos. Sem doença renal ou episódios recentes de ITU."
        ),
        (
            "BEG, hidratada. Temperatura: 36,8 °C; FC: 80 bpm; PA: 112/72 mmHg. "
            "Discreto desconforto suprapúbico; punho-percussão lombar negativa bilateralmente."
        ),
        [
            _exam(
                "urina_tipo_1",
                "Urina tipo 1",
                "Leucocitúria, esterase leucocitária positiva e nitrito positivo.",
            ),
            _exam(
                "urocultura",
                "Urocultura",
                "Crescimento de Escherichia coli sensível às opções usuais.",
            ),
            _exam(
                "ultrassom_rins",
                "Ultrassonografia de rins e vias urinárias",
                "Sem alterações estruturais.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        46,
        "Candidíase vulvovaginal não complicada",
        "Ginecologia",
        (
            "CRL, 30 anos, refere prurido vulvar intenso e corrimento branco espesso "
            "há quatro dias. Nega odor forte, dor pélvica, febre, sangramento ou nova "
            "parceria sexual. Não está gestante e não tem diabetes conhecida."
        ),
        (
            "BEG, afebril. Vulva hiperemiada; corrimento branco grumoso, sem odor. "
            "pH vaginal: 4,2. Sem dor à mobilização do colo ou à palpação anexial."
        ),
        [
            _exam(
                "microscopia_vaginal",
                "Microscopia a fresco da secreção vaginal",
                "Leveduras e pseudohifas presentes.",
            ),
            _exam(
                "cultura_vaginal",
                "Cultura da secreção vaginal",
                "Crescimento de Candida albicans.",
            ),
            _exam(
                "ultrassom_transvaginal",
                "Ultrassonografia transvaginal",
                "Sem alterações pélvicas.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        47,
        "Dengue sem sinais de alarme",
        "Infectologia",
        (
            "RVS, 26 anos, mora em área com circulação de dengue e apresenta febre, "
            "cefaleia, dor atrás dos olhos e mialgia há dois dias. Consegue ingerir "
            "líquidos e urina normalmente. Nega dor abdominal intensa, vômitos "
            "persistentes, sangramento, tontura ou falta de ar."
        ),
        (
            "REG, consciente e hidratado. Temperatura: 38,4 °C; FC: 94 bpm; "
            "PA: 118/76 mmHg; FR: 18 irpm; SpO2: 98%. Prova do laço negativa, "
            "abdome indolor e perfusão periférica preservada."
        ),
        [
            _exam(
                "hemograma",
                "Hemograma com hematócrito e plaquetas",
                "Hematócrito 43%; leucócitos 3.800/mm³; plaquetas 156.000/mm³.",
            ),
            _exam(
                "teste_ns1",
                "Pesquisa de antígeno NS1",
                "Reagente.",
            ),
            _exam(
                "tomografia_abdome",
                "TC de abdome",
                "Sem alterações agudas.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        48,
        "Gastroenterite aguda sem desidratação",
        "Gastroenterologia",
        (
            "MOT, 35 anos, relata cinco evacuações líquidas e um episódio de vômito "
            "nas últimas 24 horas, após refeição fora de casa. Tolera água e soro de "
            "reidratação. Nega sangue nas fezes, febre alta, dor abdominal localizada, "
            "viagem recente ou uso de antibiótico."
        ),
        (
            "BEG, hidratado. Temperatura: 37,2 °C; FC: 84 bpm; PA: 116/74 mmHg. "
            "Mucosas úmidas, perfusão normal e abdome flácido, com ruídos aumentados, "
            "sem defesa ou dor localizada."
        ),
        [
            _exam(
                "eletrólitos",
                "Eletrólitos e função renal",
                "Sódio, potássio e creatinina dentro da referência.",
            ),
            _exam(
                "coprocultura",
                "Coprocultura",
                "Sem crescimento de enteropatógenos pesquisados.",
                appropriate=False,
            ),
            _exam(
                "tomografia_abdome",
                "TC de abdome",
                "Sem alterações agudas.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        49,
        "Doença do refluxo gastroesofágico sem sinais de alarme",
        "Gastroenterologia",
        (
            "DAS, 39 anos, apresenta queimação retroesternal e regurgitação após "
            "refeições volumosas há três meses, duas a três vezes por semana. Refere "
            "piora ao deitar. Nega disfagia, perda de peso, anemia, vômitos persistentes, "
            "sangramento digestivo ou história familiar de câncer gastrointestinal."
        ),
        (
            "BEG. FC: 76 bpm; PA: 120/78 mmHg; IMC: 29 kg/m². Exame cardiopulmonar "
            "normal e abdome flácido, indolor, sem massas ou visceromegalias."
        ),
        [
            _exam(
                "teste_h_pylori",
                "Teste respiratório para Helicobacter pylori",
                "Não reagente.",
            ),
            _exam(
                "endoscopia",
                "Endoscopia digestiva alta",
                "Sem erosões, úlceras ou lesões suspeitas.",
                appropriate=False,
            ),
            _exam(
                "tomografia_torax",
                "TC de tórax",
                "Sem alterações.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        50,
        "Escabiose",
        "Dermatologia",
        (
            "APL, 34 anos, relata coceira intensa, pior à noite, há três semanas. "
            "A companheira e dois filhos começaram a apresentar o mesmo sintoma. "
            "Nega febre, secreção purulenta ou uso de medicamento novo."
        ),
        (
            "BEG, afebril. Pápulas escoriadas e pequenos sulcos em espaços interdigitais, "
            "punhos e região periumbilical. Sem crostas extensas ou sinais de infecção bacteriana."
        ),
        [
            _exam(
                "raspado_pele",
                "Raspado de pele com microscopia",
                "Ácaro e ovos compatíveis com Sarcoptes scabiei.",
            ),
            _exam(
                "painel_alergia",
                "Painel sérico de alergias",
                "Sem sensibilizações relevantes.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        51,
        "Tínea do corpo",
        "Dermatologia",
        (
            "GLC, 29 anos, apresenta mancha pruriginosa no antebraço que aumenta "
            "lentamente há duas semanas. Tem um gato recém-adotado com áreas de perda "
            "de pelos. Nega febre, dor intensa, secreção ou lesões em mucosas."
        ),
        (
            "BEG, afebril. Placa anular eritematodescamativa de 4 cm, com borda ativa "
            "e clareamento central no antebraço direito. Sem celulite ou linfangite."
        ),
        [
            _exam(
                "exame_micologico",
                "Exame micológico direto",
                "Hifas septadas compatíveis com dermatófito.",
            ),
            _exam(
                "biopsia_pele",
                "Biópsia de pele",
                "Dermatite superficial inespecífica.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        52,
        "Lombalgia mecânica aguda sem sinais de alarme",
        "Ortopedia",
        (
            "FAM, 41 anos, iniciou dor lombar após levantar uma caixa pesada no trabalho "
            "ontem. A dor piora ao movimentar-se e melhora em repouso relativo. Nega "
            "trauma importante, febre, perda de peso, câncer, uso de corticoide, retenção "
            "urinária, anestesia em sela ou fraqueza nas pernas."
        ),
        (
            "BEG. Marcha preservada. Dor e tensão paravertebral lombar, sem dor vertebral "
            "focal. Lasègue negativo, força e sensibilidade preservadas, reflexos simétricos."
        ),
        [
            _exam(
                "raiox_coluna",
                "Radiografia da coluna lombar",
                "Sem fratura ou desalinhamento.",
                appropriate=False,
            ),
            _exam(
                "ressonancia_lombar",
                "Ressonância magnética da coluna lombar",
                "Discreta discopatia, sem compressão neural relevante.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        53,
        "Hipertensão arterial sem emergência hipertensiva",
        "Cardiologia",
        (
            "JCO, 52 anos, descobriu pressão elevada em uma ação comunitária e procura "
            "a UBS. Está assintomático. Nega dor torácica, falta de ar, déficit neurológico, "
            "confusão ou alteração visual aguda. Tem sobrepeso e pai hipertenso."
        ),
        (
            "BEG. PA após repouso: 164/96 mmHg no braço direito e 162/94 mmHg no "
            "esquerdo; FC: 78 bpm. Exames neurológico, cardiovascular e pulmonar sem "
            "sinais de lesão aguda de órgão-alvo."
        ),
        [
            _exam(
                "mrpa_mapa",
                "MRPA ou MAPA",
                "Média residencial/ambulatorial persistentemente elevada, compatível com hipertensão.",
            ),
            _exam(
                "avaliacao_risco",
                "Creatinina, potássio, glicemia, perfil lipídico e urina",
                "Função renal preservada, potássio normal, LDL elevado e glicemia limítrofe.",
            ),
            _exam(
                "ecg",
                "Eletrocardiograma",
                "Ritmo sinusal, sem sinais de isquemia aguda.",
            ),
            _exam(
                "tomografia_cranio",
                "TC de crânio",
                "Sem alterações agudas.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        54,
        "Diabetes mellitus tipo 2 fora da meta",
        "Endocrinologia",
        (
            "SMF, 58 anos, com diabetes tipo 2 há seis anos, retorna à UBS após faltar "
            "a consultas e usar a medicação de forma irregular. Refere sede discreta, "
            "mas nega vômitos, dor abdominal, respiração ofegante, sonolência ou perda "
            "de peso rápida. Não trouxe registros de glicemia."
        ),
        (
            "BEG, hidratada. PA: 136/84 mmHg; FC: 82 bpm; IMC: 31 kg/m². Glicemia "
            "capilar: 220 mg/dL. Pés sem úlceras, pulsos palpáveis e sensibilidade preservada."
        ),
        [
            _exam(
                "hemoglobina_glicada",
                "Hemoglobina glicada",
                "HbA1c: 8,8%.",
            ),
            _exam(
                "funcao_renal_albuminuria",
                "Creatinina, TFG estimada e relação albumina/creatinina",
                "TFG preservada e albuminúria moderadamente aumentada.",
            ),
            _exam(
                "perfil_lipidico",
                "Perfil lipídico",
                "LDL: 142 mg/dL; triglicerídeos: 188 mg/dL.",
            ),
            _exam(
                "gasometria",
                "Gasometria arterial",
                "Sem acidose metabólica.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        55,
        "Conjuntivite viral aguda",
        "Oftalmologia",
        (
            "RPL, 27 anos, acordou com olho direito vermelho, lacrimejamento e sensação "
            "de areia. O filho está resfriado e teve quadro semelhante. Nega dor ocular "
            "intensa, fotofobia, redução visual, trauma, secreção purulenta ou uso de lente de contato."
        ),
        (
            "BEG, afebril. Acuidade visual preservada, pupilas isocóricas e fotorreagentes. "
            "Hiperemia conjuntival difusa e secreção aquosa, sem opacidade corneana, "
            "proptose ou dor à movimentação ocular."
        ),
        [
            _exam(
                "fluoresceina",
                "Teste com fluoresceína",
                "Sem defeito epitelial ou captação corneana.",
            ),
            _exam(
                "cultura_secrecao",
                "Cultura da secreção conjuntival",
                "Sem crescimento bacteriano.",
                appropriate=False,
            ),
            _exam(
                "tomografia_orbitas",
                "TC de órbitas",
                "Sem alterações orbitárias.",
                appropriate=False,
            ),
        ],
    ),
]


def _source(title: str, organization: str, year: int, url: str) -> dict[str, Any]:
    return {
        "titulo": title,
        "organizacao": organization,
        "ano": year,
        "url": url,
    }


APS_SOURCE = _source(
    "Carteira de Serviços da Atenção Primária à Saúde",
    "Ministério da Saúde",
    2020,
    "https://www.gov.br/saude/pt-br/composicao/saps/publicacoes/cartazes-e-cartilhas/casaps_versao_profissionais_saude_gestores_completa.pdf/view",
)
LINES_SOURCE = _source(
    "Linhas de Cuidado na Atenção Primária",
    "Ministério da Saúde",
    2025,
    "https://linhasdecuidado.saude.gov.br/portal/todas-linhas",
)
WOMEN_SOURCE = _source(
    "Protocolos da Atenção Básica: Saúde das Mulheres",
    "Ministério da Saúde",
    2025,
    "https://www.gov.br/saude/pt-br/composicao/saps/publicacoes/livro/protocolos-da-atencao-basica-saude-das-mulheres",
)
DENGUE_SOURCE = _source(
    "Dengue: diagnóstico e manejo clínico — adulto e criança",
    "Ministério da Saúde",
    2024,
    "https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/svsa/dengue/dengue-diagnostico-e-manejo-clinico-adulto-e-crianca/view",
)


def _criterion(name: str, points: int, *terms: str) -> dict[str, Any]:
    return {"nome": name, "pontos": points, "termos": list(terms)}


def _safety(name: str, feedback: str, *terms: str) -> dict[str, Any]:
    return {"nome": name, "termos": list(terms), "feedback_omissao": feedback}


def _outcomes(
    adequate_reaction: str,
    adequate_outcome: str,
    partial_reaction: str,
    partial_outcome: str,
    unsafe_reaction: str,
    unsafe_outcome: str,
) -> dict[str, Any]:
    return {
        "adequada": {
            "reacao": adequate_reaction,
            "desfecho": adequate_outcome,
            "reavaliacao": [
                {
                    "indicador": "Estado clínico",
                    "antes": "sintomas descritos no atendimento",
                    "depois": "melhora esperada com manejo adequado",
                    "tendencia": "melhora",
                }
            ],
        },
        "parcial": {
            "reacao": partial_reaction,
            "desfecho": partial_outcome,
            "reavaliacao": [
                {
                    "indicador": "Estado clínico",
                    "antes": "sintomas descritos no atendimento",
                    "depois": "resposta incompleta e necessidade de reavaliação",
                    "tendencia": "estavel",
                }
            ],
        },
        "insegura": {
            "reacao": unsafe_reaction,
            "desfecho": unsafe_outcome,
            "reavaliacao": [
                {
                    "indicador": "Segurança",
                    "antes": "sem complicação reconhecida",
                    "depois": "maior risco de atraso ou evento adverso",
                    "tendencia": "piora",
                }
            ],
        },
    }


def _rubric(
    *,
    diagnosis: str,
    terms: list[str],
    partial_terms: list[str],
    essential_exams: list[str],
    optional_exams: list[str],
    unnecessary_exams: list[str],
    exam_rationales: dict[str, str],
    conduct: list[dict[str, Any]],
    reference_conduct: str,
    partial_feedback: str,
    incorrect_feedback: str,
    safety_feedback: str,
    learning_goals: list[str],
    safety_criteria: list[dict[str, Any]],
    outcomes: dict[str, Any],
    reaction_reference: str,
    outcome_reference: str,
    study_topics: list[str],
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "diagnostico_referencia": diagnosis,
        "diagnostico_termos": terms,
        "diagnostico_parcial": partial_terms,
        "exames_essenciais": essential_exams,
        "exames_opcionais": optional_exams,
        "exames_desnecessarios": unnecessary_exams,
        "justificativa_exames": exam_rationales,
        "conduta_criterios": conduct,
        "conduta_referencia": reference_conduct,
        "feedback_hipotese_parcial": partial_feedback,
        "feedback_hipotese_incorreta": incorrect_feedback,
        "feedback_seguranca": safety_feedback,
        "objetivos_aprendizagem": learning_goals,
        "criterios_seguranca": safety_criteria,
        "desfechos_conduta": outcomes,
        "reacao_paciente_referencia": reaction_reference,
        "desfecho_referencia": outcome_reference,
        "temas_estudo": study_topics,
        "fontes_clinicas": sources,
    }


PRIMARY_CARE_RUBRICS = {
    41: _rubric(
        diagnosis="Infecção viral de vias aéreas superiores com faringite viral.",
        terms=["infeccao viral de vias aereas", "faringite viral", "ivas viral"],
        partial_terms=["faringite", "resfriado comum", "infeccao de vias aereas"],
        essential_exams=[],
        optional_exams=[],
        unnecessary_exams=["teste_estreptococo", "hemograma"],
        exam_rationales={
            "teste_estreptococo": "Tosse e coriza, sem exsudato ou adenopatia dolorosa, tornam a etiologia viral mais provável e não sustentam testagem rotineira neste cenário.",
            "hemograma": "Não costuma mudar a conduta em quadro viral leve e sem sinais de gravidade.",
        },
        conduct=[
            _criterion(
                "Cuidado sintomático",
                12,
                "analgesico",
                "antitermico",
                "hidratacao",
                "repouso",
            ),
            _criterion(
                "Evitar antibiótico",
                10,
                "sem antibiotico",
                "nao prescrever antibiotico",
                "viral",
            ),
            _criterion(
                "Orientar retorno",
                8,
                "retorno",
                "piora",
                "falta de ar",
                "dificuldade para engolir",
            ),
        ],
        reference_conduct="Explicar a provável origem viral, oferecer hidratação, analgesia/antitérmico se necessário e orientar retorno se surgirem sinais de gravidade; não prescrever antibiótico.",
        partial_feedback="Você reconheceu uma faringite, mas faltou caracterizar o padrão viral e a baixa probabilidade de infecção estreptocócica.",
        incorrect_feedback="Tosse, coriza e ausência de exsudato ou adenopatia cervical dolorosa favorecem uma infecção viral autolimitada.",
        safety_feedback="Evite antibiótico sem indicação e oriente retorno diante de dispneia, incapacidade de engolir saliva, piora importante ou persistência.",
        learning_goals=[
            "Reconhecer sinais de etiologia viral",
            "Evitar exames e antibióticos de baixo valor",
            "Explicar sinais de retorno",
        ],
        safety_criteria=[
            _safety(
                "Reconhecimento de sinais de alarme",
                "Sem orientação de retorno, uma complicação respiratória ou infecciosa pode ser reconhecida tardiamente.",
                "falta de ar",
                "dificuldade para engolir",
                "retorno",
                "piora",
            )
        ],
        outcomes=_outcomes(
            "A dor e o desconforto começam a ceder com suporte sintomático.",
            "A evolução tende a ser autolimitada, com retorno se houver piora.",
            "Há alívio parcial, mas as orientações ficam incompletas.",
            "O paciente pode procurar novamente a unidade por dúvidas ou persistência.",
            "Antibiótico desnecessário expõe a efeitos adversos sem acelerar a melhora.",
            "A conduta aumenta dano evitável e resistência antimicrobiana.",
        ),
        reaction_reference="Espera-se melhora progressiva com suporte e hidratação.",
        outcome_reference="Quadros virais leves geralmente evoluem bem, desde que sinais de alarme sejam monitorados.",
        study_topics=[
            "Faringite viral",
            "Uso racional de antibióticos",
            "Sinais de alarme respiratórios",
        ],
        sources=[APS_SOURCE],
    ),
    42: _rubric(
        diagnosis="Otite média aguda direita não complicada.",
        terms=["otite media aguda", "oma", "otite media direita"],
        partial_terms=["otite", "infeccao de ouvido", "otalgia"],
        essential_exams=[],
        optional_exams=["timpanometria"],
        unnecessary_exams=["tomografia_mastoide"],
        exam_rationales={
            "timpanometria": "Pode documentar efusão, mas a otoscopia típica já sustenta o diagnóstico.",
            "tomografia_mastoide": "Não é indicada sem edema, dor mastoidea ou suspeita de complicação.",
        },
        conduct=[
            _criterion(
                "Controle da dor",
                10,
                "analgesico",
                "analgesia",
                "paracetamol",
                "ibuprofeno",
            ),
            _criterion(
                "Estratégia antimicrobiana adequada",
                12,
                "observacao",
                "antibiotico",
                "amoxicilina",
                "reavaliacao",
            ),
            _criterion(
                "Orientação à família",
                8,
                "retorno",
                "mastoid",
                "piora",
                "48 horas",
                "72 horas",
            ),
        ],
        reference_conduct="Priorizar analgesia, decidir entre observação com reavaliação e antibiótico conforme idade, gravidade e protocolo local, e orientar retorno em 48–72 horas ou antes se houver piora.",
        partial_feedback="Você percebeu um problema no ouvido, mas precisa relacionar o abaulamento da membrana timpânica à otite média aguda.",
        incorrect_feedback="A otoscopia com membrana abaulada após infecção viral de vias aéreas é o achado central deste caso.",
        safety_feedback="Dor mastoidea, edema retroauricular, toxicidade ou piora exigem reavaliação rápida por possível complicação.",
        learning_goals=[
            "Interpretar a otoscopia",
            "Priorizar analgesia",
            "Escolher observação ou antibiótico com segurança",
        ],
        safety_criteria=[
            _safety(
                "Vigilância de mastoidite",
                "A família deve saber reconhecer edema ou dor atrás da orelha e piora sistêmica.",
                "mastoid",
                "edema atras",
                "piora",
                "retorno",
            )
        ],
        outcomes=_outcomes(
            "A criança fica mais confortável após analgesia e aceita melhor líquidos.",
            "Com observação segura ou tratamento indicado, a infecção tende a resolver sem complicações.",
            "A dor melhora, mas faltam critérios claros de reavaliação.",
            "Persistência dos sintomas pode atrasar ajuste do tratamento.",
            "Omissão de analgesia ou de sinais de complicação mantém sofrimento e atrasa atendimento.",
            "Uma mastoidite poderia evoluir sem reconhecimento oportuno.",
        ),
        reaction_reference="O primeiro efeito esperado é melhora da dor e da ingestão oral.",
        outcome_reference="A maioria dos episódios não complicados evolui bem com analgesia e acompanhamento apropriado.",
        study_topics=[
            "Otoscopia na OMA",
            "Analgesia pediátrica",
            "Critérios de observação e antibiótico",
        ],
        sources=[APS_SOURCE],
    ),
    43: _rubric(
        diagnosis="Rinossinusite aguda viral não complicada.",
        terms=["rinossinusite viral", "sinusite viral", "rinossinusite aguda viral"],
        partial_terms=["rinossinusite", "sinusite", "resfriado"],
        essential_exams=[],
        optional_exams=[],
        unnecessary_exams=["tomografia_seios_face", "hemograma"],
        exam_rationales={
            "tomografia_seios_face": "Imagem não é necessária em quadro agudo curto e sem suspeita de complicação orbitária ou intracraniana.",
            "hemograma": "Não diferencia de forma útil a etiologia em um caso leve e autolimitado.",
        },
        conduct=[
            _criterion(
                "Tratamento sintomático",
                12,
                "lavagem nasal",
                "soro fisiologico",
                "analgesico",
                "hidratacao",
            ),
            _criterion(
                "Evitar antibiótico precoce",
                10,
                "sem antibiotico",
                "viral",
                "nao prescrever",
            ),
            _criterion(
                "Reavaliar evolução",
                8,
                "10 dias",
                "dupla piora",
                "febre alta",
                "edema orbitario",
                "retorno",
            ),
        ],
        reference_conduct="Realizar manejo sintomático com lavagem nasal, hidratação e analgesia; evitar antibiótico e imagem neste momento; reavaliar se durar mais de dez dias sem melhora, houver piora após melhora inicial ou sinais orbitários/neurológicos.",
        partial_feedback="Você identificou rinossinusite, mas a duração curta e a ausência de piora bifásica favorecem etiologia viral.",
        incorrect_feedback="Secreção colorida isoladamente não confirma infecção bacteriana; duração e padrão de evolução são mais úteis.",
        safety_feedback="Edema orbitário, alteração visual, cefaleia intensa ou sinais neurológicos exigem avaliação urgente.",
        learning_goals=[
            "Diferenciar padrão viral e bacteriano",
            "Evitar imagem sem indicação",
            "Reconhecer complicações orbitárias",
        ],
        safety_criteria=[
            _safety(
                "Sinais orbitários ou neurológicos",
                "Complicações são raras, mas precisam de avaliação urgente quando presentes.",
                "edema orbitario",
                "alteracao visual",
                "cefaleia intensa",
                "neurologico",
            )
        ],
        outcomes=_outcomes(
            "A obstrução e a pressão facial diminuem gradualmente com medidas locais.",
            "O quadro tende a resolver sem antibiótico.",
            "Há algum alívio, mas o paciente não sabe quando retornar.",
            "Persistência ou piora pode gerar nova consulta sem orientação clara.",
            "Exames e antibiótico desnecessários acrescentam efeitos adversos e custo.",
            "Uma complicação real pode ser mascarada se a reavaliação não for explicada.",
        ),
        reaction_reference="Espera-se melhora gradual dos sintomas ao longo dos próximos dias.",
        outcome_reference="Rinossinusite viral costuma ser autolimitada; a evolução determina necessidade de nova avaliação.",
        study_topics=[
            "Rinossinusite aguda",
            "Critérios de provável etiologia bacteriana",
            "Uso racional de imagem",
        ],
        sources=[APS_SOURCE],
    ),
    44: _rubric(
        diagnosis="Exacerbação leve de asma desencadeada por poeira.",
        terms=["exacerbacao leve de asma", "crise leve de asma", "asma em exacerbacao"],
        partial_terms=["asma", "broncoespasmo", "sibilancia"],
        essential_exams=["pico_fluxo"],
        optional_exams=[],
        unnecessary_exams=["raiox_torax"],
        exam_rationales={
            "pico_fluxo": "Ajuda a quantificar a obstrução e documentar resposta ao broncodilatador quando disponível.",
            "raiox_torax": "Não é rotineiro em crise leve típica, sem febre, dor focal ou suspeita de pneumotórax.",
        },
        conduct=[
            _criterion(
                "Broncodilatador inalatório",
                12,
                "salbutamol",
                "broncodilatador",
                "inalatorio",
                "espacador",
            ),
            _criterion(
                "Reavaliar gravidade",
                10,
                "reavaliar",
                "saturacao",
                "pico de fluxo",
                "frequencia respiratoria",
            ),
            _criterion(
                "Plano e prevenção",
                8,
                "plano de acao",
                "tecnica inalatoria",
                "controlador",
                "gatilho",
                "retorno",
            ),
        ],
        reference_conduct="Administrar broncodilatador inalatório de alívio com técnica adequada, reavaliar sintomas, saturação e fluxo expiratório; revisar tratamento controlador, técnica, gatilhos e plano de ação.",
        partial_feedback="Você reconheceu asma, mas deve classificar a exacerbação e documentar a resposta ao tratamento.",
        incorrect_feedback="Sibilância após exposição a gatilho em pessoa com asma, fala preservada e melhora ao inalador sugerem exacerbação leve.",
        safety_feedback="Piora da dispneia, fala entrecortada, queda da saturação, exaustão ou pouca resposta ao broncodilatador exigem escalonamento imediato.",
        learning_goals=[
            "Classificar gravidade da crise",
            "Usar broncodilatador com espaçador",
            "Reavaliar resposta e prevenção",
        ],
        safety_criteria=[
            _safety(
                "Reavaliação respiratória",
                "Sem reavaliação, uma resposta insuficiente ao broncodilatador pode passar despercebida.",
                "reavaliar",
                "saturacao",
                "pico de fluxo",
                "fala",
            )
        ],
        outcomes=_outcomes(
            "O chiado e o aperto diminuem após broncodilatador inalatório.",
            "Com plano de ação e controle do gatilho, o paciente pode seguir em acompanhamento ambulatorial.",
            "A melhora é parcial, mas fatores de recorrência permanecem sem abordagem.",
            "Há maior chance de nova crise e retorno não planejado.",
            "Sem broncodilatador ou reavaliação, a obstrução pode progredir.",
            "O paciente pode evoluir para crise moderada ou grave e precisar de urgência.",
        ),
        reaction_reference="A melhora clínica e do pico de fluxo deve ser verificada após o broncodilatador.",
        outcome_reference="Boa resposta e ausência de sinais de gravidade permitem seguimento com plano estruturado.",
        study_topics=[
            "Exacerbação de asma",
            "Técnica inalatória",
            "Plano de ação para asma",
        ],
        sources=[LINES_SOURCE],
    ),
    45: _rubric(
        diagnosis="Cistite aguda não complicada.",
        terms=[
            "cistite aguda",
            "infeccao urinaria baixa",
            "itu baixa",
            "cistite nao complicada",
        ],
        partial_terms=["infeccao urinaria", "itu", "disuria"],
        essential_exams=[],
        optional_exams=["urina_tipo_1", "urocultura"],
        unnecessary_exams=["ultrassom_rins"],
        exam_rationales={
            "urina_tipo_1": "Pode apoiar o diagnóstico, embora sintomas típicos sem corrimento já tenham alto valor clínico.",
            "urocultura": "É mais útil em recorrência, falha terapêutica, gestação, apresentação atípica ou maior risco de resistência.",
            "ultrassom_rins": "Não é indicado em primeiro episódio típico sem febre, dor lombar ou suspeita de obstrução.",
        },
        conduct=[
            _criterion(
                "Antimicrobiano apropriado",
                12,
                "antibiotico",
                "nitrofurantoina",
                "fosfomicina",
            ),
            _criterion("Alívio e orientação", 8, "hidratacao", "analgesia", "orientar"),
            _criterion(
                "Excluir complicação",
                10,
                "febre",
                "dor lombar",
                "pielonefrite",
                "gestacao",
                "retorno",
            ),
        ],
        reference_conduct="Tratar como cistite não complicada com antimicrobiano de primeira linha conforme protocolo local e perfil da paciente, orientar hidratação e retorno se febre, dor lombar, vômitos ou ausência de melhora.",
        partial_feedback="Você reconheceu uma ITU, mas precisa localizá-la como infecção baixa e afastar gestação ou sinais de pielonefrite.",
        incorrect_feedback="Disúria, urgência e frequência sem corrimento vaginal ou dor lombar formam um quadro típico de cistite.",
        safety_feedback="Febre, dor lombar, vômitos, gestação ou instabilidade mudam o risco e a estratégia de investigação e tratamento.",
        learning_goals=[
            "Reconhecer cistite típica",
            "Indicar urocultura seletivamente",
            "Diferenciar pielonefrite",
        ],
        safety_criteria=[
            _safety(
                "Excluir pielonefrite e gestação",
                "Esses fatores alteram o risco, a investigação e o tratamento.",
                "febre",
                "dor lombar",
                "pielonefrite",
                "gestacao",
            )
        ],
        outcomes=_outcomes(
            "A disúria e a urgência tendem a melhorar após o início do tratamento adequado.",
            "A infecção resolve com seguimento ambulatorial e retorno se necessário.",
            "Há melhora incompleta ou demora por escolha terapêutica pouco clara.",
            "Persistência requer reavaliação e possível cultura.",
            "Ignorar sinais de infecção alta ou tratar de forma inadequada permite progressão.",
            "Pode ocorrer pielonefrite e necessidade de atendimento urgente.",
        ),
        reaction_reference="Espera-se redução progressiva da disúria nas primeiras etapas do tratamento.",
        outcome_reference="Cistite não complicada costuma resolver com tratamento de primeira linha e orientação de retorno.",
        study_topics=[
            "Cistite não complicada",
            "Indicações de urocultura",
            "Sinais de pielonefrite",
        ],
        sources=[WOMEN_SOURCE],
    ),
    46: _rubric(
        diagnosis="Candidíase vulvovaginal não complicada.",
        terms=[
            "candidiase vulvovaginal",
            "vulvovaginite por candida",
            "candidiase vaginal",
        ],
        partial_terms=["vulvovaginite", "vaginite", "corrimento vaginal"],
        essential_exams=[],
        optional_exams=["microscopia_vaginal", "cultura_vaginal"],
        unnecessary_exams=["ultrassom_transvaginal"],
        exam_rationales={
            "microscopia_vaginal": "Pode confirmar leveduras ou pseudohifas, especialmente quando o diagnóstico clínico é incerto.",
            "cultura_vaginal": "É reservada sobretudo para recorrência, complicação ou microscopia negativa com sintomas persistentes.",
            "ultrassom_transvaginal": "Não avalia a causa de uma vaginite típica sem dor pélvica ou massa.",
        },
        conduct=[
            _criterion(
                "Antifúngico adequado",
                12,
                "antifungico",
                "fluconazol",
                "azol",
                "miconazol",
                "clotrimazol",
            ),
            _criterion(
                "Avaliar fatores especiais",
                10,
                "gestacao",
                "diabetes",
                "recorrente",
                "imunossupressao",
            ),
            _criterion(
                "Orientar reavaliação",
                8,
                "retorno",
                "persistencia",
                "dor pelvica",
                "febre",
            ),
        ],
        reference_conduct="Tratar candidíase não complicada com antifúngico tópico ou oral conforme perfil e protocolo local, verificar gestação e fatores de complicação, e reavaliar se persistente ou recorrente.",
        partial_feedback="Você reconheceu vaginite, mas o prurido, o corrimento grumoso e o pH normal apontam especificamente para candidíase.",
        incorrect_feedback="O padrão clínico é mais compatível com Candida do que com vaginose bacteriana, tricomoníase ou doença inflamatória pélvica.",
        safety_feedback="Gestação, diabetes descompensado, imunossupressão, recorrência ou dor pélvica mudam a avaliação e a escolha terapêutica.",
        learning_goals=[
            "Diferenciar causas comuns de corrimento",
            "Reconhecer candidíase complicada",
            "Evitar investigação de baixo valor",
        ],
        safety_criteria=[
            _safety(
                "Avaliação de gestação e complicação",
                "A escolha do tratamento e a investigação mudam nesses cenários.",
                "gestacao",
                "diabetes",
                "recorrente",
                "imunossupressao",
            )
        ],
        outcomes=_outcomes(
            "O prurido e o desconforto começam a diminuir após o antifúngico.",
            "O quadro tende a resolver; persistência exige confirmação diagnóstica.",
            "Há alívio parcial, mas fatores de recorrência ficam sem avaliação.",
            "Sintomas podem retornar e exigir nova consulta.",
            "Tratamento inadequado pode irritar a mucosa ou mascarar outro diagnóstico.",
            "Uma IST ou doença pélvica poderia ter reconhecimento tardio se surgirem sinais atípicos.",
        ),
        reaction_reference="A resposta esperada é redução do prurido e da inflamação vulvar.",
        outcome_reference="Casos não complicados costumam responder ao antifúngico; recorrência pede investigação dirigida.",
        study_topics=[
            "Corrimento vaginal",
            "Candidíase vulvovaginal",
            "Vaginites diferenciais",
        ],
        sources=[WOMEN_SOURCE],
    ),
    47: _rubric(
        diagnosis="Dengue sem sinais de alarme.",
        terms=["dengue sem sinais de alarme", "dengue grupo a", "dengue"],
        partial_terms=["arbovirose", "sindrome febril", "virose"],
        essential_exams=[],
        optional_exams=["hemograma", "teste_ns1"],
        unnecessary_exams=["tomografia_abdome"],
        exam_rationales={
            "hemograma": "Pode ser indicado conforme classificação de risco e momento clínico, mas não substitui a avaliação seriada de sinais de alarme.",
            "teste_ns1": "Pode apoiar a confirmação nos primeiros dias, conforme disponibilidade e vigilância local.",
            "tomografia_abdome": "Não é indicada em paciente estável, sem dor abdominal ou sinais de complicação.",
        },
        conduct=[
            _criterion(
                "Hidratação e sintomáticos seguros",
                12,
                "hidratacao oral",
                "soro de reidratacao",
                "paracetamol",
                "dipirona",
            ),
            _criterion(
                "Evitar medicamentos de risco",
                8,
                "evitar aines",
                "sem aines",
                "ibuprofeno",
                "aas",
                "aspirina",
            ),
            _criterion(
                "Orientar sinais de alarme",
                10,
                "dor abdominal",
                "vomitos persistentes",
                "sangramento",
                "tontura",
                "retorno",
            ),
        ],
        reference_conduct="Classificar o risco, orientar hidratação oral e sintomáticos seguros, evitar AAS e anti-inflamatórios e entregar orientação clara para retorno imediato se surgirem sinais de alarme, especialmente na defervescência.",
        partial_feedback="Você reconheceu síndrome febril ou arbovirose, mas deve nomear dengue e registrar explicitamente a ausência atual de sinais de alarme.",
        incorrect_feedback="Febre, mialgia, cefaleia e dor retro-orbitária em área de circulação, sem foco alternativo, sustentam suspeita de dengue.",
        safety_feedback="A classificação pode mudar rapidamente: dor abdominal intensa, vômitos persistentes, sangramento, tontura, dispneia ou redução da diurese exigem retorno imediato.",
        learning_goals=[
            "Classificar dengue por risco",
            "Orientar hidratação",
            "Reconhecer sinais de alarme e medicamentos contraindicados",
        ],
        safety_criteria=[
            _safety(
                "Orientação de sinais de alarme",
                "Sem essa orientação, a fase crítica pode começar fora da unidade sem reconhecimento oportuno.",
                "dor abdominal",
                "vomitos persistentes",
                "sangramento",
                "tontura",
                "retorno",
            ),
            _safety(
                "Evitar AAS e anti-inflamatórios",
                "Esses medicamentos podem aumentar o risco de sangramento.",
                "evitar aines",
                "sem aines",
                "aas",
                "aspirina",
                "ibuprofeno",
            ),
        ],
        outcomes=_outcomes(
            "O paciente mantém boa perfusão e tolera o plano de hidratação oral.",
            "Segue em acompanhamento, sabendo quando retornar durante a possível fase crítica.",
            "A hidratação ajuda, mas a orientação de segurança fica incompleta.",
            "Uma piora pode ser percebida mais tarde do que o ideal.",
            "Anti-inflamatórios ou ausência de retorno programado aumentam o risco evitável.",
            "Sinais de alarme podem progredir para dengue grave sem avaliação rápida.",
        ),
        reaction_reference="A hidratação deve manter diurese e perfusão enquanto a evolução é monitorada.",
        outcome_reference="O desfecho costuma ser favorável quando a classificação e os sinais de alarme são reavaliados no momento correto.",
        study_topics=[
            "Classificação de risco da dengue",
            "Hidratação oral",
            "Fase crítica e sinais de alarme",
        ],
        sources=[DENGUE_SOURCE],
    ),
    48: _rubric(
        diagnosis="Gastroenterite aguda sem sinais de desidratação.",
        terms=[
            "gastroenterite aguda",
            "diarreia aguda infecciosa",
            "gastroenterite sem desidratacao",
        ],
        partial_terms=["diarreia aguda", "intoxicacao alimentar", "gastroenterite"],
        essential_exams=[],
        optional_exams=["eletrólitos"],
        unnecessary_exams=["coprocultura", "tomografia_abdome"],
        exam_rationales={
            "eletrólitos": "São mais úteis quando há desidratação moderada/grave, comorbidade ou perda persistente; neste caso podem ser dispensados.",
            "coprocultura": "Não é rotina em diarreia aquosa curta, sem sangue, febre alta ou contexto epidemiológico especial.",
            "tomografia_abdome": "Não há dor localizada, peritonismo ou suspeita de complicação abdominal.",
        },
        conduct=[
            _criterion(
                "Reidratação oral",
                12,
                "soro de reidratacao",
                "hidratacao oral",
                "liquidos",
            ),
            _criterion(
                "Alimentação e suporte",
                8,
                "manter alimentacao",
                "dieta",
                "antiemetico",
                "higiene",
            ),
            _criterion(
                "Sinais de retorno",
                10,
                "sangue nas fezes",
                "desidratacao",
                "febre alta",
                "dor intensa",
                "retorno",
            ),
        ],
        reference_conduct="Priorizar solução de reidratação oral, manter alimentação conforme tolerância e orientar higiene; evitar exames ou antibióticos de rotina e retornar se houver sangue, febre alta, pouca urina, incapacidade de hidratar ou dor localizada.",
        partial_feedback="Você reconheceu diarreia aguda, mas deve registrar o estado de hidratação e a ausência de sinais invasivos.",
        incorrect_feedback="O início agudo de diarreia aquosa após alimento, sem sangue, febre alta ou peritonismo, é compatível com gastroenterite não complicada.",
        safety_feedback="A principal decisão é identificar desidratação, sangue nas fezes, dor localizada, imunossupressão ou incapacidade de ingerir líquidos.",
        learning_goals=[
            "Avaliar hidratação",
            "Indicar reidratação oral",
            "Evitar exames e antibióticos rotineiros",
        ],
        safety_criteria=[
            _safety(
                "Vigilância de desidratação",
                "A perda persistente de líquidos pode levar a deterioração rápida se não houver retorno.",
                "desidratacao",
                "pouca urina",
                "incapacidade de hidratar",
                "retorno",
            )
        ],
        outcomes=_outcomes(
            "A sede e o mal-estar diminuem com reidratação oral fracionada.",
            "O episódio tende a resolver com suporte e alimentação tolerada.",
            "A hidratação é insuficiente ou as orientações ficam vagas.",
            "Persistência das perdas pode exigir reavaliação.",
            "Antibiótico ou antidiarreico inadequado pode causar efeitos adversos e atrasar reconhecimento de gravidade.",
            "O paciente pode evoluir com desidratação e alteração renal/eletrolítica.",
        ),
        reaction_reference="A resposta imediata esperada é manutenção da hidratação e da diurese.",
        outcome_reference="Quadros aquosos não complicados costumam ser autolimitados com reidratação adequada.",
        study_topics=[
            "Avaliação da desidratação",
            "Terapia de reidratação oral",
            "Indicações de coprocultura",
        ],
        sources=[APS_SOURCE],
    ),
    49: _rubric(
        diagnosis="Doença do refluxo gastroesofágico sem sinais de alarme.",
        terms=["doenca do refluxo gastroesofagico", "refluxo gastroesofagico", "drge"],
        partial_terms=["dispepsia", "refluxo", "pirose"],
        essential_exams=[],
        optional_exams=["teste_h_pylori"],
        unnecessary_exams=["endoscopia", "tomografia_torax"],
        exam_rationales={
            "teste_h_pylori": "Pode ser considerado quando predominam sintomas dispépticos, mas não é necessário para confirmar refluxo típico.",
            "endoscopia": "Não é exame inicial em pessoa jovem com sintomas típicos e sem sinais de alarme.",
            "tomografia_torax": "Não esclarece refluxo típico e não há sinal clínico que justifique o exame.",
        },
        conduct=[
            _criterion(
                "Mudanças comportamentais",
                10,
                "perder peso",
                "refeicoes menores",
                "evitar deitar",
                "elevar cabeceira",
                "gatilhos",
            ),
            _criterion(
                "Teste terapêutico",
                12,
                "inibidor de bomba",
                "ibp",
                "omeprazol",
                "tratamento empirico",
            ),
            _criterion(
                "Reavaliar alarmes",
                8,
                "disfagia",
                "perda de peso",
                "sangramento",
                "anemia",
                "retorno",
            ),
        ],
        reference_conduct="Orientar redução de fatores desencadeantes, evitar deitar após refeições, abordar excesso de peso e realizar tratamento antissecretor empírico conforme protocolo, com reavaliação e investigação se houver alarme ou falha.",
        partial_feedback="Você reconheceu síndrome dispéptica, mas a pirose e a regurgitação pós-prandial predominantes sugerem refluxo.",
        incorrect_feedback="O padrão recorrente após refeições e ao deitar, sem sinais de alarme, é típico de refluxo gastroesofágico.",
        safety_feedback="Disfagia, sangramento, anemia, perda de peso, vômitos persistentes ou falha terapêutica indicam investigação adicional.",
        learning_goals=[
            "Reconhecer refluxo típico",
            "Identificar sinais de alarme",
            "Evitar endoscopia precoce sem indicação",
        ],
        safety_criteria=[
            _safety(
                "Triagem de sinais de alarme",
                "Sinais de alarme mudam a necessidade e a urgência da investigação.",
                "disfagia",
                "perda de peso",
                "sangramento",
                "anemia",
                "vomitos",
            )
        ],
        outcomes=_outcomes(
            "A queimação diminui com ajustes de hábitos e tratamento inicial.",
            "O paciente segue em teste terapêutico com reavaliação programada.",
            "Há melhora parcial, mas gatilhos ou seguimento não foram abordados.",
            "Sintomas podem persistir e exigir nova avaliação.",
            "Investigar demais ou ignorar alarmes cria, respectivamente, dano de baixo valor ou atraso diagnóstico.",
            "Uma causa estrutural pode permanecer sem diagnóstico se sinais de alarme surgirem e forem ignorados.",
        ),
        reaction_reference="Espera-se redução da frequência e intensidade da pirose.",
        outcome_reference="Sintomas típicos sem alarme podem ser manejados inicialmente na atenção primária, com reavaliação.",
        study_topics=[
            "DRGE",
            "Sinais de alarme digestivos",
            "Tratamento empírico e reavaliação",
        ],
        sources=[APS_SOURCE],
    ),
    50: _rubric(
        diagnosis="Escabiose familiar.",
        terms=["escabiose", "sarna", "infestacao por sarcoptes"],
        partial_terms=[
            "dermatose contagiosa",
            "prurido familiar",
            "parasitose cutanea",
        ],
        essential_exams=[],
        optional_exams=["raspado_pele"],
        unnecessary_exams=["painel_alergia"],
        exam_rationales={
            "raspado_pele": "Pode confirmar o ácaro, mas o padrão noturno, familiar e interdigital permite diagnóstico clínico.",
            "painel_alergia": "Não explica o padrão contagioso e não contribui para o manejo inicial.",
        },
        conduct=[
            _criterion(
                "Tratamento escabicida", 10, "permetrina", "ivermectina", "escabicida"
            ),
            _criterion(
                "Tratar contatos simultaneamente",
                12,
                "contatos",
                "familia",
                "todos da casa",
                "simultaneo",
            ),
            _criterion(
                "Ambiente e retorno",
                8,
                "roupas",
                "roupa de cama",
                "lavar",
                "persistencia",
                "retorno",
            ),
        ],
        reference_conduct="Tratar o paciente e os contatos domiciliares simultaneamente com esquema apropriado ao perfil de cada pessoa, orientar manejo de roupas e roupa de cama e explicar que o prurido pode persistir após a erradicação.",
        partial_feedback="Você reconheceu uma dermatose contagiosa, mas o prurido noturno e o acometimento familiar são clássicos de escabiose.",
        incorrect_feedback="A distribuição interdigital, os sulcos e vários moradores com prurido noturno apontam para escabiose.",
        safety_feedback="Falhar em tratar todos os contatos ao mesmo tempo favorece reinfestação; crostas extensas ou infecção secundária exigem avaliação específica.",
        learning_goals=[
            "Reconhecer distribuição típica",
            "Tratar contatos",
            "Orientar controle ambiental sem excessos",
        ],
        safety_criteria=[
            _safety(
                "Tratamento simultâneo dos contatos",
                "Sem tratar os contatos, a reinfestação familiar é muito provável.",
                "contatos",
                "familia",
                "todos da casa",
                "simultaneo",
            )
        ],
        outcomes=_outcomes(
            "O surgimento de novas lesões diminui após tratamento correto de toda a família.",
            "A cadeia de transmissão é interrompida, embora o prurido residual possa durar algum tempo.",
            "O paciente melhora, mas um contato não tratado mantém a transmissão.",
            "Há recorrência e necessidade de repetir o manejo.",
            "Corticoide isolado ou tratamento apenas do paciente mascara sintomas sem eliminar o ácaro.",
            "A infestação se mantém e pode ocorrer infecção bacteriana por escoriação.",
        ),
        reaction_reference="O controle é percebido pela ausência de novas lesões, não pelo desaparecimento imediato de toda coceira.",
        outcome_reference="Tratamento simultâneo e orientação ambiental adequada costumam interromper a transmissão.",
        study_topics=["Escabiose", "Tratamento de contatos", "Prurido pós-escabiose"],
        sources=[APS_SOURCE],
    ),
    51: _rubric(
        diagnosis="Tínea do corpo (tinea corporis).",
        terms=["tinea corporis", "tinea do corpo", "tinea corporal", "dermatofitose"],
        partial_terms=["micose", "infeccao fungica", "lesao anular"],
        essential_exams=[],
        optional_exams=["exame_micologico"],
        unnecessary_exams=["biopsia_pele"],
        exam_rationales={
            "exame_micologico": "Pode confirmar dermatófito quando o aspecto é atípico ou há dúvida diagnóstica.",
            "biopsia_pele": "É invasiva e desnecessária em lesão superficial típica sem falha terapêutica.",
        },
        conduct=[
            _criterion(
                "Antifúngico tópico",
                12,
                "antifungico topico",
                "terbinafina",
                "azol",
                "clotrimazol",
            ),
            _criterion(
                "Evitar corticoide isolado",
                10,
                "sem corticoide",
                "evitar corticoide",
                "tinea incognito",
            ),
            _criterion(
                "Fonte e reavaliação",
                8,
                "animal",
                "gato",
                "higiene",
                "retorno",
                "persistencia",
            ),
        ],
        reference_conduct="Tratar a lesão localizada com antifúngico tópico, evitar corticoide isolado, orientar higiene e avaliação do animal potencialmente infectado e reavaliar se extensa, recorrente ou sem resposta.",
        partial_feedback="Você reconheceu micose, mas pode especificar dermatofitose do corpo pela borda ativa e clareamento central.",
        incorrect_feedback="A placa anular descamativa com crescimento centrífugo e contato com animal é típica de tinea corporis.",
        safety_feedback="Corticoide tópico isolado pode modificar e ampliar a micose; doença extensa, imunossupressão ou falha requerem reavaliação.",
        learning_goals=[
            "Reconhecer lesão anular por dermatófito",
            "Evitar corticoide isolado",
            "Definir quando confirmar com exame micológico",
        ],
        safety_criteria=[
            _safety(
                "Evitar corticoide isolado",
                "O corticoide pode mascarar a borda e favorecer progressão da dermatofitose.",
                "sem corticoide",
                "evitar corticoide",
                "tinea incognito",
            )
        ],
        outcomes=_outcomes(
            "O prurido e a borda ativa diminuem com o antifúngico.",
            "A lesão regride gradualmente, com reavaliação se não houver resposta.",
            "O tratamento é iniciado, mas a fonte ou o seguimento ficam sem abordagem.",
            "Pode ocorrer recorrência após novo contato.",
            "Corticoide isolado reduz temporariamente a vermelhidão e facilita expansão do fungo.",
            "A apresentação fica mascarada e mais extensa, dificultando o diagnóstico.",
        ),
        reaction_reference="Espera-se redução da borda ativa antes do desaparecimento completo da mancha.",
        outcome_reference="Lesões localizadas costumam responder ao tratamento tópico corretamente utilizado.",
        study_topics=["Dermatofitoses", "Exame micológico direto", "Tinea incógnita"],
        sources=[APS_SOURCE],
    ),
    52: _rubric(
        diagnosis="Lombalgia mecânica aguda inespecífica, sem sinais de alarme.",
        terms=[
            "lombalgia mecanica aguda",
            "dor lombar mecanica",
            "lombalgia aguda inespecifica",
        ],
        partial_terms=["lombalgia", "distensao lombar", "dor muscular lombar"],
        essential_exams=[],
        optional_exams=[],
        unnecessary_exams=["raiox_coluna", "ressonancia_lombar"],
        exam_rationales={
            "raiox_coluna": "Sem trauma relevante, risco de fratura ou outro sinal de alarme, a radiografia não melhora o manejo inicial.",
            "ressonancia_lombar": "Não é indicada na lombalgia aguda inespecífica sem déficit neurológico ou suspeita de causa grave.",
        },
        conduct=[
            _criterion(
                "Manter atividade",
                10,
                "manter atividade",
                "evitar repouso",
                "retorno gradual",
                "movimentar",
            ),
            _criterion(
                "Analgesia e medidas locais",
                10,
                "analgesico",
                "calor local",
                "fisioterapia",
                "orientacao postural",
            ),
            _criterion(
                "Sinais de alarme",
                10,
                "anestesia em sela",
                "retencao urinaria",
                "fraqueza",
                "febre",
                "retorno",
            ),
        ],
        reference_conduct="Explicar o caráter mecânico, incentivar atividade e retorno gradual, oferecer analgesia e medidas não farmacológicas individualizadas e orientar retorno imediato diante de déficit neurológico, alteração esfincteriana, febre ou piora.",
        partial_feedback="Você identificou lombalgia, mas deve registrar a ausência de sinais de alarme e evitar atribuir uma lesão estrutural não demonstrada.",
        incorrect_feedback="Relação temporal com esforço, dor ao movimento e exame neurológico normal favorecem lombalgia mecânica inespecífica.",
        safety_feedback="Retenção urinária, anestesia em sela, fraqueza progressiva, febre, trauma ou câncer mudam a urgência e a investigação.",
        learning_goals=[
            "Triar sinais de alarme",
            "Evitar imagem precoce",
            "Promover recuperação ativa",
        ],
        safety_criteria=[
            _safety(
                "Síndrome da cauda equina e déficit",
                "Alterações esfincterianas, anestesia em sela ou fraqueza exigem avaliação urgente.",
                "anestesia em sela",
                "retencao urinaria",
                "fraqueza",
                "cauda equina",
            )
        ],
        outcomes=_outcomes(
            "A dor fica mais controlável e o paciente mantém mobilidade segura.",
            "A recuperação funcional ocorre gradualmente, sem exames desnecessários.",
            "Há alívio parcial, mas medo do movimento ou seguimento inadequado prolonga limitação.",
            "O retorno às atividades pode atrasar.",
            "Repouso prolongado, opioide sem critério ou omissão de sinais neurológicos aumenta dano.",
            "Pode haver cronificação ou atraso no reconhecimento de compressão neurológica.",
        ),
        reaction_reference="A meta inicial é melhorar função e tolerância ao movimento, não eliminar toda dor imediatamente.",
        outcome_reference="Lombalgia mecânica aguda sem alarme costuma melhorar com manejo conservador e atividade.",
        study_topics=[
            "Lombalgia inespecífica",
            "Red flags",
            "Uso racional de exames de imagem",
        ],
        sources=[LINES_SOURCE],
    ),
    53: _rubric(
        diagnosis="Hipertensão arterial sistêmica sem emergência hipertensiva.",
        terms=["hipertensao arterial sistemica", "has", "hipertensao sem emergencia"],
        partial_terms=["pressao alta", "hipertensao", "elevacao pressorica"],
        essential_exams=["mrpa_mapa", "avaliacao_risco"],
        optional_exams=["ecg"],
        unnecessary_exams=["tomografia_cranio"],
        exam_rationales={
            "mrpa_mapa": "Confirma persistência da elevação fora do consultório e ajuda a excluir efeito do avental branco.",
            "avaliacao_risco": "Pesquisa fatores de risco, função renal e lesão de órgão-alvo para orientar o plano.",
            "ecg": "Pode compor a avaliação inicial de risco e hipertrofia ventricular.",
            "tomografia_cranio": "Não há déficit neurológico ou outra suspeita de evento agudo que justifique imagem.",
        },
        conduct=[
            _criterion(
                "Confirmar e estratificar",
                10,
                "mrpa",
                "mapa",
                "confirmar",
                "risco cardiovascular",
                "orgao alvo",
            ),
            _criterion(
                "Tratamento longitudinal",
                12,
                "anti hipertensivo",
                "antihipertensivo",
                "mudanca de estilo",
                "reduzir sal",
                "atividade fisica",
            ),
            _criterion(
                "Evitar redução abrupta",
                8,
                "sem urgencia",
                "nao reduzir abruptamente",
                "acompanhamento",
                "retorno",
            ),
        ],
        reference_conduct="Confirmar hipertensão com medidas padronizadas e domiciliares/ambulatoriais, avaliar risco e órgão-alvo, iniciar mudanças de estilo de vida e tratamento farmacológico conforme risco e protocolo, com seguimento próximo; não realizar redução abrupta em assintomático sem lesão aguda.",
        partial_feedback="Você reconheceu pressão elevada, mas precisa diferenciar hipertensão persistente de uma medida isolada e afastar emergência.",
        incorrect_feedback="Medidas repetidamente elevadas, ausência de sintomas e de lesão aguda apontam para hipertensão a confirmar e tratar longitudinalmente, não para emergência.",
        safety_feedback="Dor torácica, dispneia, déficit neurológico, confusão ou alteração visual aguda exigem avaliação imediata por possível lesão de órgão-alvo.",
        learning_goals=[
            "Confirmar hipertensão corretamente",
            "Estratificar risco cardiovascular",
            "Diferenciar hipertensão grave de emergência",
        ],
        safety_criteria=[
            _safety(
                "Excluir emergência hipertensiva",
                "Elevação pressórica com lesão aguda de órgão-alvo exige atendimento imediato.",
                "dor toracica",
                "deficit neurologico",
                "dispneia",
                "orgao alvo",
                "emergencia",
            )
        ],
        outcomes=_outcomes(
            "O paciente compreende que a pressão será controlada com plano progressivo e acompanhamento.",
            "O risco cardiovascular começa a ser reduzido com adesão e metas individualizadas.",
            "Há orientação inicial, mas confirmação ou estratificação ficam incompletas.",
            "O controle pode atrasar ou o tratamento pode ser mal ajustado.",
            "Redução abrupta sem indicação pode causar hipotensão e hipoperfusão.",
            "O paciente sofre dano iatrogênico ou permanece sem avaliação de risco adequada.",
        ),
        reaction_reference="A pressão não precisa normalizar imediatamente; a prioridade é um plano seguro e longitudinal.",
        outcome_reference="Confirmação, estratificação e adesão permitem controle progressivo e redução de risco.",
        study_topics=["Diagnóstico de HAS", "MRPA e MAPA", "Emergência hipertensiva"],
        sources=[LINES_SOURCE],
    ),
    54: _rubric(
        diagnosis="Diabetes mellitus tipo 2 fora da meta, sem emergência hiperglicêmica.",
        terms=[
            "diabetes mellitus tipo 2 descompensado",
            "dm2 fora da meta",
            "diabetes tipo 2 fora da meta",
        ],
        partial_terms=["diabetes mellitus tipo 2", "dm2", "hiperglicemia"],
        essential_exams=["hemoglobina_glicada", "funcao_renal_albuminuria"],
        optional_exams=["perfil_lipidico"],
        unnecessary_exams=["gasometria"],
        exam_rationales={
            "hemoglobina_glicada": "Quantifica o controle glicêmico recente e orienta ajuste terapêutico.",
            "funcao_renal_albuminuria": "Avalia complicação renal e influencia escolha e segurança de medicamentos.",
            "perfil_lipidico": "Compõe a avaliação de risco cardiovascular e prevenção.",
            "gasometria": "Sem vômitos, respiração anormal, alteração mental ou desidratação, não há suspeita clínica de cetoacidose.",
        },
        conduct=[
            _criterion(
                "Revisar adesão e barreiras",
                8,
                "adesao",
                "barreira",
                "uso irregular",
                "educacao",
            ),
            _criterion(
                "Ajustar plano terapêutico",
                12,
                "ajustar tratamento",
                "metformina",
                "antidiabetico",
                "meta individual",
                "alimentacao",
                "atividade fisica",
            ),
            _criterion(
                "Prevenir complicações",
                10,
                "pes",
                "retina",
                "albuminuria",
                "risco cardiovascular",
                "retorno",
            ),
        ],
        reference_conduct="Explorar barreiras e adesão, definir meta individual, otimizar tratamento e hábitos conforme função renal e risco, revisar pés, rins, retina e risco cardiovascular e programar seguimento; não encaminhar à urgência apenas pela glicemia estável deste caso.",
        partial_feedback="Você reconheceu diabetes e hiperglicemia, mas deve caracterizar controle crônico fora da meta e avaliar complicações.",
        incorrect_feedback="HbA1c elevada e uso irregular, sem acidose ou instabilidade, indicam DM2 fora da meta em acompanhamento longitudinal.",
        safety_feedback="Vômitos, dor abdominal, respiração profunda, alteração de consciência, desidratação ou glicemia muito elevada com sintomas exigem investigação de emergência.",
        learning_goals=[
            "Interpretar HbA1c",
            "Avaliar rim, pés e risco cardiovascular",
            "Distinguir descontrole crônico de emergência",
        ],
        safety_criteria=[
            _safety(
                "Triagem de crise hiperglicêmica",
                "Sinais de cetoacidose ou estado hiperosmolar exigem atendimento urgente.",
                "vomitos",
                "dor abdominal",
                "respiracao profunda",
                "alteracao de consciencia",
                "desidratacao",
            )
        ],
        outcomes=_outcomes(
            "A paciente entende as metas e participa de um plano viável para retomar o tratamento.",
            "O controle melhora progressivamente e as complicações passam a ser monitoradas.",
            "O medicamento é ajustado, mas barreiras ou prevenção ficam incompletas.",
            "A adesão pode continuar baixa e a HbA1c permanecer elevada.",
            "Ignorar sinais de crise ou função renal pode tornar o tratamento inseguro.",
            "Há risco de evento adverso, progressão de complicações ou emergência hiperglicêmica não reconhecida.",
        ),
        reaction_reference="A glicemia melhora gradualmente; a resposta deve ser avaliada por sintomas, registros e HbA1c futura.",
        outcome_reference="O cuidado longitudinal deve integrar controle glicêmico, adesão e prevenção renal e cardiovascular.",
        study_topics=[
            "Metas de HbA1c",
            "Doença renal diabética",
            "Prevenção cardiovascular no DM2",
        ],
        sources=[LINES_SOURCE],
    ),
    55: _rubric(
        diagnosis="Conjuntivite viral aguda não complicada.",
        terms=["conjuntivite viral", "conjuntivite aguda viral", "adenoconjuntivite"],
        partial_terms=["conjuntivite", "olho vermelho", "infeccao ocular"],
        essential_exams=[],
        optional_exams=["fluoresceina"],
        unnecessary_exams=["cultura_secrecao", "tomografia_orbitas"],
        exam_rationales={
            "fluoresceina": "É útil quando há dor, trauma, fotofobia ou suspeita de lesão corneana; neste caso pode ser dispensada.",
            "cultura_secrecao": "Não é rotina em secreção aquosa e quadro viral típico.",
            "tomografia_orbitas": "Não há proptose, dor à movimentação ou sinais de infecção orbitária.",
        },
        conduct=[
            _criterion(
                "Suporte sintomático",
                10,
                "compressa fria",
                "lubrificante",
                "lagrima artificial",
                "higiene",
            ),
            _criterion(
                "Reduzir transmissão",
                10,
                "lavar as maos",
                "nao compartilhar",
                "toalha",
                "contagioso",
            ),
            _criterion(
                "Reconhecer urgência ocular",
                10,
                "dor intensa",
                "fotofobia",
                "baixa visual",
                "lente de contato",
                "retorno",
            ),
        ],
        reference_conduct="Oferecer compressas frias e lubrificação, orientar higiene das mãos e não compartilhar objetos, evitar antibiótico rotineiro e retornar imediatamente se houver dor, fotofobia, redução visual, opacidade corneana ou piora.",
        partial_feedback="Você reconheceu conjuntivite, mas a secreção aquosa, o contato domiciliar e a ausência de dor ou baixa visual favorecem etiologia viral.",
        incorrect_feedback="Hiperemia difusa com lacrimejamento, sensação de areia e contato com caso semelhante é típica de conjuntivite viral.",
        safety_feedback="Dor intensa, fotofobia, redução visual, opacidade corneana, trauma químico ou uso de lentes de contato exigem avaliação prioritária.",
        learning_goals=[
            "Diferenciar causas comuns de olho vermelho",
            "Orientar prevenção de transmissão",
            "Reconhecer sinais de doença corneana",
        ],
        safety_criteria=[
            _safety(
                "Sinais de ameaça à visão",
                "Dor, fotofobia ou perda visual não combinam com conjuntivite simples e exigem avaliação rápida.",
                "dor intensa",
                "fotofobia",
                "baixa visual",
                "opacidade corneana",
                "lente de contato",
            )
        ],
        outcomes=_outcomes(
            "O desconforto diminui com compressas e lubrificação, mantendo a visão preservada.",
            "O quadro tende a resolver e a transmissão é reduzida pelas medidas de higiene.",
            "Há suporte, mas faltam medidas de prevenção ou sinais de retorno.",
            "Outras pessoas podem ser expostas ou uma piora pode ser percebida tarde.",
            "Antibiótico desnecessário ou omissão de sinais corneanos aumenta risco sem benefício.",
            "Uma ceratite ou outra causa grave de olho vermelho pode ter avaliação atrasada.",
        ),
        reaction_reference="A visão deve permanecer preservada enquanto o desconforto melhora progressivamente.",
        outcome_reference="Conjuntivite viral costuma ser autolimitada; higiene e sinais de alarme são essenciais.",
        study_topics=[
            "Diagnóstico diferencial de olho vermelho",
            "Conjuntivite viral",
            "Sinais de urgência oftalmológica",
        ],
        sources=[APS_SOURCE],
    ),
}
