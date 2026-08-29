"""Lote adicional de Psiquiatria e Saúde Mental (casos 66 a 80)."""

from typing import Any

SPECIALTY = "Psiquiatria e Saúde Mental"


def _source(title: str, organization: str, year: int, url: str) -> dict[str, Any]:
    return {"titulo": title, "organizacao": organization, "ano": year, "url": url}


def _exam(
    code: str, name: str, result: str, *, appropriate: bool = True
) -> dict[str, Any]:
    return {"id": code, "nome": name, "resultado": result, "correto": appropriate}


def _case(
    case_id: int,
    title: str,
    difficulty: str,
    history: str,
    physical_exam: str,
    exams: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": case_id,
        "titulo": title,
        "especialidade": SPECIALTY,
        "nivel_dificuldade": difficulty,
        "historia_clinica": history,
        "exame_fisico": physical_exam,
        "exames_disponiveis": exams,
    }


def _criterion(name: str, points: int, *terms: str) -> dict[str, Any]:
    return {"nome": name, "pontos": points, "termos": list(terms)}


def _safety(name: str, feedback: str, *terms: str) -> dict[str, Any]:
    return {"nome": name, "termos": list(terms), "feedback_omissao": feedback}


def _vital(indicator: str, before: str, after: str, trend: str) -> dict[str, str]:
    return {
        "indicador": indicator,
        "antes": before,
        "depois": after,
        "tendencia": trend,
    }


def _outcomes(
    adequate: tuple[str, str],
    partial: tuple[str, str],
    unsafe: tuple[str, str],
    measures: list[tuple[str, str, str, str, str]],
) -> dict[str, Any]:
    def level(text: tuple[str, str], index: int) -> dict[str, Any]:
        return {
            "reacao": text[0],
            "desfecho": text[1],
            "reavaliacao": [
                _vital(
                    name, before, values[index], ("melhora", "estavel", "piora")[index]
                )
                for name, before, *values in measures
            ],
        }

    return {
        "adequada": level(adequate, 0),
        "parcial": level(partial, 1),
        "insegura": level(unsafe, 2),
    }


def _rubric(
    diagnosis: str,
    terms: list[str],
    partial_terms: list[str],
    essential: list[str],
    optional: list[str],
    unnecessary: list[str],
    reasons: dict[str, str],
    criteria: list[dict[str, Any]],
    reference_conduct: str,
    partial_feedback: str,
    incorrect_feedback: str,
    safety_feedback: str,
    objectives: list[str],
    safety: list[dict[str, Any]],
    outcomes: dict[str, Any],
    themes: list[str],
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "diagnostico_referencia": diagnosis,
        "diagnostico_termos": terms,
        "diagnostico_parcial": partial_terms,
        "exames_essenciais": essential,
        "exames_opcionais": optional,
        "exames_desnecessarios": unnecessary,
        "justificativa_exames": reasons,
        "conduta_criterios": criteria,
        "conduta_referencia": reference_conduct,
        "feedback_hipotese_parcial": partial_feedback,
        "feedback_hipotese_incorreta": incorrect_feedback,
        "feedback_seguranca": safety_feedback,
        "objetivos_aprendizagem": objectives,
        "criterios_seguranca": safety,
        "desfechos_conduta": outcomes,
        "reacao_paciente_referencia": outcomes["adequada"]["reacao"],
        "desfecho_referencia": outcomes["adequada"]["desfecho"],
        "temas_estudo": themes,
        "fontes_clinicas": sources,
    }


NICE_DEPRESSION = _source(
    "Depression in adults: treatment and management",
    "National Institute for Health and Care Excellence",
    2022,
    "https://www.nice.org.uk/guidance/ng222",
)
NICE_ANXIETY = _source(
    "Generalised anxiety disorder and panic disorder in adults",
    "National Institute for Health and Care Excellence",
    2011,
    "https://www.nice.org.uk/guidance/cg113",
)
NICE_SOCIAL_ANXIETY = _source(
    "Social anxiety disorder: recognition, assessment and treatment",
    "National Institute for Health and Care Excellence",
    2013,
    "https://www.nice.org.uk/guidance/cg159",
)
NICE_ADHD = _source(
    "Attention deficit hyperactivity disorder: diagnosis and management",
    "National Institute for Health and Care Excellence",
    2018,
    "https://www.nice.org.uk/guidance/ng87",
)
NICE_OCD = _source(
    "Obsessive-compulsive disorder and body dysmorphic disorder",
    "National Institute for Health and Care Excellence",
    2005,
    "https://www.nice.org.uk/guidance/cg31",
)
NICE_PTSD = _source(
    "Post-traumatic stress disorder",
    "National Institute for Health and Care Excellence",
    2018,
    "https://www.nice.org.uk/guidance/ng116",
)
NICE_BIPOLAR = _source(
    "Bipolar disorder: assessment and management",
    "National Institute for Health and Care Excellence",
    2014,
    "https://www.nice.org.uk/guidance/cg185",
)
NICE_ALCOHOL = _source(
    "Alcohol-use disorders: physical complications",
    "National Institute for Health and Care Excellence",
    2010,
    "https://www.nice.org.uk/guidance/cg100",
)
NICE_EATING = _source(
    "Eating disorders: recognition and treatment",
    "National Institute for Health and Care Excellence",
    2017,
    "https://www.nice.org.uk/guidance/ng69",
)
NICE_PSYCHOSIS = _source(
    "Psychosis and schizophrenia in adults",
    "National Institute for Health and Care Excellence",
    2014,
    "https://www.nice.org.uk/guidance/cg178",
)
NICE_PERINATAL = _source(
    "Antenatal and postnatal mental health",
    "National Institute for Health and Care Excellence",
    2014,
    "https://www.nice.org.uk/guidance/cg192",
)
BAP_CATATONIA = _source(
    "Evidence-based consensus guidelines for the management of catatonia",
    "British Association for Psychopharmacology",
    2023,
    "https://pubmed.ncbi.nlm.nih.gov/37039129/",
)
NICE_BORDERLINE = _source(
    "Borderline personality disorder: recognition and management",
    "National Institute for Health and Care Excellence",
    2009,
    "https://www.nice.org.uk/guidance/cg78",
)
NICE_DELIRIUM = _source(
    "Delirium: prevention, diagnosis and management",
    "National Institute for Health and Care Excellence",
    2010,
    "https://www.nice.org.uk/guidance/cg103",
)


PSYCHIATRY_TITLES = {
    66: "Perda de interesse e energia nas últimas semanas",
    67: "Preocupação constante e dificuldade para relaxar",
    68: "Crises súbitas de medo e palpitações",
    69: "Medo intenso de falar e agir em público",
    70: "Dificuldade antiga de atenção e organização",
    71: "Pensamentos repetitivos e rituais que ocupam horas",
    72: "Pesadelos e alerta constante após um acidente",
    73: "Poucas horas de sono, muita energia e gastos excessivos",
    74: "Tremores e ansiedade após parar de beber",
    75: "Perda de peso e medo intenso de engordar",
    76: "Isolamento, vozes e desconfiança crescente",
    77: "Insônia, agitação e ideias estranhas após o parto",
    78: "Parou de falar e permanece imóvel",
    79: "Relações instáveis, impulsividade e autolesão",
    80: "Confusão que varia ao longo do dia",
}


PSYCHIATRY_CASES = [
    _case(
        66,
        "Transtorno depressivo maior",
        "Fácil",
        "MRS, 29 anos, relata há seis semanas tristeza, perda de interesse, cansaço, dificuldade de concentração, despertar precoce e culpa. O rendimento caiu e ela evita amigos. Refere pensamentos passageiros de que seria melhor não acordar, sem plano ou tentativa prévia.",
        "Lúcida, orientada, autocuidado reduzido, fala baixa, humor deprimido e afeto constrito. PA: 112/72 mmHg; FC: 76 bpm; FR: 16 irpm; SpO2: 99%; Temperatura: 36,5 °C. Sem sinais neurológicos focais.",
        [
            _exam(
                "phq9",
                "PHQ-9",
                "18/27, compatível com sintomas depressivos moderadamente graves; item 9 positivo, exigindo avaliação clínica imediata de risco.",
            ),
            _exam(
                "risco_suicidio",
                "Avaliação estruturada do risco de suicídio",
                "Ideação passiva, sem plano, intenção ou acesso declarado a meios; irmã disponível como apoio. O risco deve ser reavaliado clinicamente.",
            ),
            _exam(
                "estado_mental",
                "Entrevista clínica e exame do estado mental",
                "Sintomas depressivos persistentes com prejuízo funcional; sem história de mania, hipomania ou psicose.",
            ),
            _exam(
                "tsh_hemograma",
                "TSH e hemograma",
                "TSH 2,1 mUI/L e hemograma sem alterações, sem causa orgânica evidente para fadiga.",
            ),
            _exam("gad7", "GAD-7", "7/21, sintomas ansiosos leves associados."),
            _exam(
                "ressonancia_cranio",
                "Ressonância de crânio",
                "Sem alterações; não havia sinal neurológico que justificasse imagem inicial.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        67,
        "Transtorno de ansiedade generalizada",
        "Fácil",
        "LFA, 34 anos, há oito meses se preocupa excessivamente com trabalho, finanças e saúde dos pais. Não consegue controlar as preocupações, sente tensão muscular, irritabilidade, insônia e dificuldade de concentração, com prejuízo no trabalho.",
        "Lúcido, orientado, inquieto e com fala acelerada, porém organizada. PA: 124/78 mmHg; FC: 88 bpm; FR: 18 irpm; SpO2: 98%; Temperatura: 36,6 °C. Tireoide não palpável e exame cardiopulmonar normal.",
        [
            _exam(
                "gad7",
                "GAD-7",
                "16/21, indicando sintomas ansiosos intensos; o resultado apoia, mas não substitui a entrevista diagnóstica.",
            ),
            _exam(
                "entrevista_ansiedade",
                "Entrevista psiquiátrica estruturada",
                "Preocupação excessiva em vários domínios na maior parte dos dias, há mais de seis meses, com prejuízo funcional.",
            ),
            _exam(
                "phq9",
                "PHQ-9",
                "6/27, sintomas depressivos leves, sem ideação de morte.",
            ),
            _exam(
                "tsh_glicemia",
                "TSH e glicemia",
                "TSH 1,8 mUI/L e glicemia 91 mg/dL, sem alteração metabólica explicativa.",
            ),
            _exam(
                "audit",
                "AUDIT",
                "3/40, consumo de álcool de baixo risco no relato atual.",
            ),
            _exam(
                "tomografia_cranio",
                "Tomografia de crânio",
                "Sem alterações; exame desnecessário na ausência de sinais neurológicos.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        68,
        "Transtorno do pânico",
        "Fácil",
        "RCP, 26 anos, teve quatro crises inesperadas no último mês com medo intenso, palpitações, tremor, falta de ar e sensação de morte, atingindo o pico em minutos. Desde então teme novas crises e evita ônibus. Está sem sintomas no momento.",
        "Lúcida, orientada e ansiosa. PA: 118/74 mmHg; FC: 82 bpm; FR: 17 irpm; SpO2: 99%; Temperatura: 36,7 °C. Auscultas cardíaca e pulmonar normais, sem edema ou déficit focal.",
        [
            _exam(
                "pdss",
                "Escala de Gravidade do Transtorno do Pânico (PDSS)",
                "16/28, com crises recorrentes, ansiedade antecipatória e evitação.",
            ),
            _exam(
                "entrevista_panico",
                "Entrevista clínica para crises de pânico",
                "Crises inesperadas, pico rápido e preocupação persistente; sem episódio restrito a situação social ou trauma.",
            ),
            _exam(
                "ecg",
                "Eletrocardiograma",
                "Ritmo sinusal, FC 80 bpm, sem alteração de condução ou isquemia.",
            ),
            _exam(
                "tsh_glicemia", "TSH e glicemia", "TSH 2,4 mUI/L e glicemia 88 mg/dL."
            ),
            _exam(
                "toxicologico",
                "Triagem de substâncias",
                "Nega estimulantes; triagem urinária negativa para cocaína e anfetaminas.",
            ),
            _exam(
                "holter",
                "Holter de 24 horas",
                "Ritmo sinusal, sem arritmia; baixo rendimento após avaliação inicial normal e crises típicas.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        69,
        "Transtorno de ansiedade social",
        "Fácil",
        "AJN, 22 anos, evita apresentações, reuniões e refeições diante de outras pessoas por medo de parecer ridículo. Reconhece que o medo é excessivo, mas os sintomas persistem há três anos e já recusou uma promoção.",
        "Lúcido, orientado, evita contato visual e apresenta rubor e tremor fino ao descrever situações sociais. PA: 116/70 mmHg; FC: 84 bpm; FR: 16 irpm; SpO2: 99%; Temperatura: 36,4 °C. Exame físico sem alterações.",
        [
            _exam(
                "lsas",
                "Escala de Ansiedade Social de Liebowitz (LSAS)",
                "78/144, com medo e evitação importantes em situações de desempenho e interação.",
            ),
            _exam(
                "entrevista_social",
                "Entrevista clínica focada em ansiedade social",
                "Medo persistente de avaliação negativa, evitação e prejuízo funcional há anos.",
            ),
            _exam("phq9", "PHQ-9", "5/27, sem episódio depressivo atual."),
            _exam(
                "audit",
                "AUDIT",
                "9/40; relata beber antes de algumas apresentações, exigindo orientação preventiva.",
            ),
            _exam(
                "gad7",
                "GAD-7",
                "8/21; preocupação concentrada principalmente em situações sociais.",
            ),
            _exam(
                "eletroencefalograma",
                "Eletroencefalograma",
                "Sem alterações; não é indicado para o padrão clínico apresentado.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        70,
        "Transtorno de déficit de atenção e hiperatividade no adulto",
        "Fácil",
        "PVM, 31 anos, relata desorganização, atrasos, esquecimentos e dificuldade de concluir tarefas desde a escola. Mudou de emprego três vezes por falhas de planejamento. A mãe confirma sintomas antes dos 12 anos. Nega episódios de humor elevado ou redução persistente da necessidade de sono.",
        "Lúcido, orientado, inquieto, perde o fio da conversa e responde antes do fim das perguntas. PA: 122/76 mmHg; FC: 80 bpm; FR: 16 irpm; SpO2: 98%; Temperatura: 36,5 °C. Exame neurológico normal.",
        [
            _exam(
                "asrs",
                "ASRS v1.1 — rastreio de TDAH em adultos",
                "Cinco de seis itens da parte A positivos; rastreio positivo, sem valor diagnóstico isolado.",
            ),
            _exam(
                "entrevista_tdah",
                "Entrevista diagnóstica de TDAH",
                "Sintomas persistentes de desatenção e impulsividade em trabalho, estudo e casa, com prejuízo funcional.",
            ),
            _exam(
                "historia_desenvolvimento",
                "História escolar e informante",
                "Boletins descrevem distração e tarefas incompletas; mãe confirma início na infância.",
            ),
            _exam(
                "triagem_comorbidades",
                "Triagem de humor, ansiedade e uso de substâncias",
                "Sem mania, depressão maior ou uso de estimulantes; ansiedade leve secundária à desorganização.",
            ),
            _exam(
                "tsh_hemograma",
                "TSH e hemograma",
                "Sem anemia ou disfunção tireoidiana.",
            ),
            _exam(
                "ressonancia_cranio",
                "Ressonância de crânio",
                "Normal; não indicada sem sinais neurológicos ou início atípico.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        71,
        "Transtorno obsessivo-compulsivo",
        "Intermediário",
        "DBS, 27 anos, apresenta pensamentos intrusivos de contaminação e lava as mãos por quase três horas ao dia. Sabe que o ritual é excessivo, tenta resistir e chega atrasado ao trabalho. Os sintomas pioraram há um ano.",
        "Lúcido, orientado, ansioso, pensamento organizado e sem delírios. Escoriações nas mãos. PA: 120/76 mmHg; FC: 86 bpm; FR: 17 irpm; SpO2: 99%; Temperatura: 36,5 °C.",
        [
            _exam(
                "ybocs",
                "Escala Yale-Brown para sintomas obsessivo-compulsivos (Y-BOCS)",
                "24/40, sintomas moderados a graves com grande consumo de tempo.",
            ),
            _exam(
                "entrevista_toc",
                "Entrevista clínica para obsessões e compulsões",
                "Obsessões intrusivas e compulsões reconhecidas como excessivas, com prejuízo funcional.",
            ),
            _exam(
                "risco_humor",
                "Avaliação de depressão e risco de suicídio",
                "Sintomas depressivos leves, sem ideação suicida atual.",
            ),
            _exam(
                "tiques",
                "Avaliação de tiques",
                "Sem tiques motores ou vocais atuais ou na infância.",
            ),
            _exam(
                "dermatologica",
                "Avaliação das lesões das mãos",
                "Dermatite irritativa leve por lavagem repetitiva, sem infecção.",
            ),
            _exam(
                "ressonancia_cranio",
                "Ressonância de crânio",
                "Sem alterações; não indicada em apresentação típica e sem sinais neurológicos.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        72,
        "Transtorno de estresse pós-traumático",
        "Intermediário",
        "TMC, 38 anos, após acidente rodoviário há seis meses, apresenta pesadelos, lembranças invasivas, evita dirigir, assusta-se facilmente e sente culpa. Os sintomas duram mais de um mês e prejudicam trabalho e relações.",
        "Lúcida, orientada, hipervigilante e emocionada ao falar do acidente, sem psicose. PA: 126/80 mmHg; FC: 92 bpm; FR: 18 irpm; SpO2: 98%; Temperatura: 36,6 °C. Exame físico normal.",
        [
            _exam(
                "pcl5",
                "PCL-5 — checklist de sintomas de TEPT",
                "46/80, com sintomas relevantes nos grupos de intrusão, evitação, cognições/humor e hiperativação.",
            ),
            _exam(
                "entrevista_trauma",
                "Entrevista clínica focada em trauma",
                "Exposição traumática definida, sintomas persistentes por seis meses e prejuízo funcional.",
            ),
            _exam(
                "risco_depressao",
                "Avaliação de depressão e risco de suicídio",
                "PHQ-9 12/27; nega ideação, plano ou tentativa de suicídio.",
            ),
            _exam(
                "dissociacao",
                "Rastreio de sintomas dissociativos",
                "Desrealização breve em lembranças, sem amnésia dissociativa persistente.",
            ),
            _exam("audit", "AUDIT", "6/40, sem padrão atual de uso nocivo de álcool."),
            _exam(
                "cortisol",
                "Cortisol sérico",
                "Valor matinal normal; não confirma nem exclui TEPT e não é indicado rotineiramente.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        73,
        "Transtorno bipolar tipo I — episódio maníaco",
        "Intermediário",
        "HGS, 35 anos, dorme duas horas por noite há dez dias sem sentir cansaço, fala muito, iniciou vários projetos e gastou grande parte das economias. Está irritado quando contrariado e a família relata prejuízo importante. Teve episódio depressivo há dois anos.",
        "Alerta, agitado, expansivo, fala pressionada, pensamento acelerado e grandiosidade, sem déficit focal. PA: 138/84 mmHg; FC: 104 bpm; FR: 19 irpm; SpO2: 98%; Temperatura: 36,8 °C.",
        [
            _exam(
                "ymrs",
                "Escala de Mania de Young (YMRS)",
                "32/60, quadro maníaco de intensidade importante; a escala acompanha gravidade, não substitui diagnóstico clínico.",
            ),
            _exam(
                "estado_mental_risco",
                "Exame do estado mental e avaliação de risco",
                "Mania com julgamento comprometido, gastos arriscados e agitação; nega plano suicida, mas há risco de exposição e impulsividade.",
            ),
            _exam(
                "toxicologico",
                "Triagem toxicológica",
                "Negativa para cocaína e anfetaminas; álcool não detectado.",
            ),
            _exam(
                "tsh_metabolico",
                "TSH, função renal, hepática e eletrólitos",
                "Resultados sem alterações relevantes, úteis ao diferencial e planejamento terapêutico.",
            ),
            _exam(
                "beta_hcg",
                "Beta-hCG",
                "Não reagente; informação de segurança antes de decisões farmacológicas.",
            ),
            _exam(
                "ressonancia_cranio",
                "Ressonância de crânio",
                "Sem alterações; não indicada de rotina sem sinais neurológicos ou apresentação atípica.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        74,
        "Síndrome de abstinência alcoólica",
        "Intermediário",
        "JRO, 46 anos, consome destilados diariamente há oito anos e interrompeu o uso há 18 horas por náusea. Evoluiu com tremores, ansiedade, sudorese e insônia. Nega convulsões prévias e está orientado.",
        "Lúcido, ansioso, sudoreico, com tremor distal, sem alucinações. PA: 148/92 mmHg; FC: 112 bpm; FR: 20 irpm; SpO2: 98%; Temperatura: 37,2 °C.",
        [
            _exam(
                "ciwaar",
                "CIWA-Ar — avaliação da abstinência alcoólica",
                "17 pontos, abstinência moderada, requerendo monitorização clínica e reavaliações seriadas.",
            ),
            _exam(
                "audit",
                "AUDIT",
                "24/40, padrão compatível com provável dependência e necessidade de avaliação especializada.",
            ),
            _exam(
                "glicose_eletrólitos",
                "Glicose, eletrólitos, magnésio e função renal",
                "Glicose 82 mg/dL; potássio 3,4 mEq/L; magnésio 1,5 mg/dL; creatinina normal.",
            ),
            _exam(
                "hemograma_hepatico",
                "Hemograma e função hepática",
                "VCM 102 fL; plaquetas 138.000/mm³; AST 84 U/L e ALT 42 U/L.",
            ),
            _exam(
                "ecg",
                "Eletrocardiograma",
                "Taquicardia sinusal, QTc 462 ms, sem arritmia.",
            ),
            _exam(
                "tomografia_cranio",
                "Tomografia de crânio",
                "Sem alterações; não indicada sem trauma, déficit focal ou rebaixamento de consciência.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        75,
        "Anorexia nervosa",
        "Intermediário",
        "BLA, 20 anos, perdeu 12 kg em seis meses, restringe alimentos e faz exercício excessivo por medo intenso de engordar, embora familiares a considerem muito magra. Está há quatro meses sem menstruar e relata tontura ao levantar.",
        "Lúcida, emagrecida, extremidades frias. Peso 44 kg, altura 1,68 m, IMC 15,6 kg/m². PA: 92/58 mmHg deitada e 80/50 mmHg em pé; FC: 48 bpm; FR: 14 irpm; SpO2: 99%; Temperatura: 35,8 °C.",
        [
            _exam(
                "scoff",
                "Questionário SCOFF",
                "4/5 respostas positivas; rastreio fortemente sugestivo, sem substituir avaliação clínica completa.",
            ),
            _exam(
                "antropometria_ortostase",
                "Antropometria e sinais vitais ortostáticos",
                "IMC 15,6 kg/m², hipotensão ortostática, bradicardia e hipotermia.",
            ),
            _exam(
                "eletrólitos_renal",
                "Eletrólitos, glicose, fósforo, magnésio e função renal",
                "Potássio 3,1 mEq/L, fósforo 2,4 mg/dL, magnésio 1,6 mg/dL e glicose 68 mg/dL.",
            ),
            _exam(
                "ecg",
                "Eletrocardiograma",
                "Bradicardia sinusal, FC 46 bpm, QTc 480 ms.",
            ),
            _exam(
                "hemograma_hepatico",
                "Hemograma e função hepática",
                "Leucopenia discreta e elevação leve de transaminases.",
            ),
            _exam(
                "densitometria",
                "Densitometria óssea",
                "Baixa massa óssea; útil no seguimento, mas não deve atrasar a estabilização clínica inicial.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        76,
        "Primeiro episódio psicótico compatível com esquizofrenia",
        "Difícil",
        "EVS, 24 anos, há oito meses se isola, abandonou a faculdade e acredita que vizinhos monitoram seus pensamentos. Há três meses ouve vozes comentando suas ações. Nega uso de drogas e episódios de humor predominantes.",
        "Alerta, higiene reduzida, desconfiado, afeto embotado, delírios persecutórios e alucinações auditivas, sem déficit focal. PA: 126/78 mmHg; FC: 90 bpm; FR: 17 irpm; SpO2: 98%; Temperatura: 36,7 °C.",
        [
            _exam(
                "panss",
                "PANSS — avaliação da gravidade de sintomas psicóticos",
                "92 pontos, com sintomas positivos, negativos e prejuízo geral; a escala não define sozinha o diagnóstico.",
            ),
            _exam(
                "estado_mental_risco",
                "Exame do estado mental e avaliação de risco",
                "Psicose ativa; vozes sem comando atual, sem plano suicida, porém autocuidado e julgamento comprometidos.",
            ),
            _exam(
                "historia_colateral",
                "História longitudinal com familiar",
                "Declínio funcional progressivo por oito meses, sem síndrome afetiva dominante.",
            ),
            _exam(
                "toxicologico",
                "Triagem toxicológica",
                "Negativa para cannabis, cocaína e anfetaminas.",
            ),
            _exam(
                "laboratorio_baseline",
                "Hemograma, glicemia, lipídios, TSH, função renal e hepática",
                "Sem causa metabólica evidente; dados basais registrados antes do tratamento.",
            ),
            _exam(
                "spect_cerebral",
                "SPECT cerebral",
                "Sem achado específico; não é exame diagnóstico de rotina para esquizofrenia.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        77,
        "Psicose pós-parto",
        "Difícil",
        "FCA, 30 anos, dez dias após o parto, está há quatro noites quase sem dormir, alterna euforia e irritabilidade e afirma receber mensagens especiais sobre o bebê. A família relata fala desconexa e tentativa de sair de casa de madrugada com o recém-nascido.",
        "Alerta, agitada, fala acelerada, pensamento desorganizado, ideias delirantes e crítica ausente. PA: 132/82 mmHg; FC: 102 bpm; FR: 18 irpm; SpO2: 99%; Temperatura: 36,8 °C. Sem rigidez de nuca ou déficit focal.",
        [
            _exam(
                "estado_mental_risco",
                "Exame do estado mental e risco materno-infantil",
                "Psicose aguda com julgamento gravemente comprometido e risco potencial para mãe e bebê; exige proteção e avaliação urgente.",
            ),
            _exam(
                "historia_colateral",
                "Entrevista com familiar e história do sono",
                "Início abrupto no puerpério, privação de sono e sintomas maniformes; sem psicose anterior documentada.",
            ),
            _exam(
                "epds",
                "Escala de Depressão Pós-Natal de Edimburgo (EPDS)",
                "18/30; indica sofrimento psíquico, mas não diagnostica nem exclui psicose pós-parto.",
            ),
            _exam(
                "laboratorio_organico",
                "Hemograma, eletrólitos, função renal, hepática e TSH",
                "Sem infecção, distúrbio metabólico ou tireoidiano evidente.",
            ),
            _exam(
                "toxicologico",
                "Triagem toxicológica",
                "Negativa para substâncias pesquisadas.",
            ),
            _exam(
                "ressonancia_cranio",
                "Ressonância de crânio",
                "Sem alterações; reservada a sinais neurológicos ou suspeita orgânica específica.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        78,
        "Catatonia",
        "Difícil",
        "RGL, 41 anos, com transtorno bipolar, há dois dias deixou de falar, alimentar-se e movimentar-se espontaneamente. Mantém posições impostas, resiste a comandos e repete alguns movimentos. Não iniciou antipsicótico recentemente.",
        "Acordado, mudo, imóvel, com negativismo, postura mantida e flexibilidade cérea. PA: 110/68 mmHg; FC: 96 bpm; FR: 18 irpm; SpO2: 98%; Temperatura: 37,3 °C. Sem rigidez generalizada intensa.",
        [
            _exam(
                "bush_francis",
                "Escala de Catatonia de Bush-Francis",
                "Triagem positiva e escore de gravidade 18, com mutismo, imobilidade, postura, negativismo e flexibilidade cérea.",
            ),
            _exam(
                "teste_lorazepam",
                "Teste terapêutico com lorazepam sob monitorização",
                "Melhora clara da mobilidade e início de fala após dose teste, apoiando catatonia.",
            ),
            _exam(
                "ck_metabolico",
                "CK, eletrólitos, função renal e glicemia",
                "CK 620 U/L, função renal preservada e eletrólitos sem alteração grave; requer hidratação e seguimento.",
            ),
            _exam(
                "eeg",
                "Eletroencefalograma",
                "Sem atividade epiléptica; útil no diferencial com estado de mal não convulsivo.",
            ),
            _exam(
                "infeccioso_autoimune",
                "Investigação orgânica dirigida",
                "Sem febre alta, leucocitose ou sinais focais; exames adicionais devem seguir história e evolução.",
            ),
            _exam(
                "teste_personalidade",
                "Inventário de personalidade",
                "Inaplicável enquanto há mutismo e imobilidade; não contribui para a urgência atual.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        79,
        "Transtorno de personalidade borderline",
        "Difícil",
        "NLS, 28 anos, relata desde o fim da adolescência relações intensas e instáveis, medo de abandono, mudanças rápidas na autoimagem, impulsividade e episódios de cortes superficiais após conflitos. Os padrões ocorrem em diferentes contextos, sem fases prolongadas de mania.",
        "Lúcida, orientada, emocionada, pensamento organizado e sem psicose. Há cicatrizes antigas superficiais no antebraço. PA: 118/72 mmHg; FC: 84 bpm; FR: 16 irpm; SpO2: 99%; Temperatura: 36,6 °C.",
        [
            _exam(
                "entrevista_personalidade",
                "Entrevista clínica estruturada de personalidade",
                "Padrão persistente de instabilidade afetiva, interpessoal e da autoimagem, impulsividade e comportamento autolesivo desde o início da vida adulta.",
            ),
            _exam(
                "msibpd",
                "MSI-BPD — rastreio de sintomas borderline",
                "8/10 itens positivos; rastreio sugestivo, mas insuficiente para diagnóstico isolado.",
            ),
            _exam(
                "risco_autolesao",
                "Avaliação estruturada de suicídio e autolesão",
                "Cortes sem intenção suicida relatada; nega plano atual, mas há gatilho recente e necessidade de plano de segurança e seguimento.",
            ),
            _exam(
                "comorbidades",
                "Avaliação de humor, trauma e uso de substâncias",
                "Sintomas ansiosos e trauma prévio; sem episódio maníaco sustentado ou dependência atual.",
            ),
            _exam(
                "historia_longitudinal",
                "História longitudinal e funcional",
                "Padrão estável em diferentes relações e contextos por mais de dez anos.",
            ),
            _exam(
                "ressonancia_cranio",
                "Ressonância de crânio",
                "Sem alterações; não confirma transtorno de personalidade e não é indicada rotineiramente.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        80,
        "Delirium",
        "Difícil",
        "OSA, 73 anos, internado por infecção urinária, passou a alternar sonolência e agitação desde ontem. Não mantém atenção, vê pessoas no quarto e piora à noite. A família informa que, antes da internação, era independente e orientado.",
        "Flutua entre alerta e sonolência, desatento, desorientado no tempo, pensamento desorganizado. PA: 104/66 mmHg; FC: 106 bpm; FR: 22 irpm; SpO2: 95%; Temperatura: 38,2 °C. Dor suprapúbica, sem déficit focal.",
        [
            _exam(
                "quatro_at",
                "4AT — rastreio de delirium",
                "8 pontos, resultado sugestivo de delirium; exige avaliação clínica e investigação da causa.",
            ),
            _exam(
                "cam",
                "Confusion Assessment Method (CAM)",
                "Positivo: início agudo e flutuação, desatenção e pensamento desorganizado.",
            ),
            _exam(
                "laboratorio_infeccao",
                "Hemograma, eletrólitos, função renal, glicemia e urina",
                "Leucócitos 15.600/mm³, sódio 130 mEq/L, creatinina 1,5 mg/dL e urina com leucocitúria e nitrito positivo.",
            ),
            _exam(
                "revisao_medicamentos",
                "Revisão de medicamentos e substâncias",
                "Recebeu difenidramina à noite; carga anticolinérgica pode agravar a confusão.",
            ),
            _exam(
                "culturas",
                "Urocultura e hemoculturas",
                "Urocultura com crescimento de Escherichia coli; hemoculturas em processamento.",
            ),
            _exam(
                "inventario_personalidade",
                "Inventário de personalidade",
                "Não é válido durante alteração aguda da atenção e não ajuda a identificar a causa.",
                appropriate=False,
            ),
        ],
    ),
]


def _exam_reasons(case: dict[str, Any]) -> dict[str, str]:
    reasons: dict[str, str] = {}
    for exam in case["exames_disponiveis"]:
        if exam["correto"]:
            reasons[exam["id"]] = (
                "Contribui para quantificar sintomas, confirmar o padrão clínico, "
                "avaliar segurança ou excluir um diferencial relevante neste caso."
            )
        else:
            reasons[exam["id"]] = (
                "Não é uma avaliação inicial de rotina neste cenário e não deve atrasar "
                "a entrevista, a proteção do paciente ou a investigação dirigida."
            )
    return reasons


def _psy_rubric(
    case_id: int,
    diagnosis: str,
    terms: list[str],
    partial_terms: list[str],
    essential: list[str],
    optional: list[str],
    unnecessary: list[str],
    criteria: list[dict[str, Any]],
    conduct: str,
    partial_feedback: str,
    incorrect_feedback: str,
    safety_feedback: str,
    objectives: list[str],
    safety: list[dict[str, Any]],
    outcomes: dict[str, Any],
    themes: list[str],
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    case = next(item for item in PSYCHIATRY_CASES if item["id"] == case_id)
    return _rubric(
        diagnosis,
        terms,
        partial_terms,
        essential,
        optional,
        unnecessary,
        _exam_reasons(case),
        criteria,
        conduct,
        partial_feedback,
        incorrect_feedback,
        safety_feedback,
        objectives,
        safety,
        outcomes,
        themes,
        sources,
    )


PSYCHIATRY_RUBRICS: dict[int, dict[str, Any]] = {
    66: _psy_rubric(
        66,
        "Transtorno depressivo maior.",
        [
            "depressao",
            "depressao maior",
            "transtorno depressivo maior",
            "episodio depressivo",
        ],
        ["transtorno depressivo", "sindrome depressiva", "distimia"],
        ["phq9", "risco_suicidio", "estado_mental"],
        ["tsh_hemograma", "gad7"],
        ["ressonancia_cranio"],
        [
            _criterion(
                "Avaliar risco e construir plano de segurança",
                10,
                "risco de suicidio",
                "plano de seguranca",
                "rede de apoio",
                "urgencia",
            ),
            _criterion(
                "Oferecer tratamento baseado em gravidade",
                10,
                "psicoterapia",
                "terapia cognitivo",
                "antidepressivo",
                "decisao compartilhada",
            ),
            _criterion(
                "Organizar seguimento próximo",
                10,
                "seguimento",
                "retorno",
                "reavaliar",
                "monitorar",
            ),
        ],
        "Avaliar imediatamente risco de suicídio, combinar plano de segurança e rede de apoio, discutir psicoterapia e antidepressivo conforme gravidade e preferência, e programar reavaliação próxima.",
        "Você reconheceu sintomas depressivos, mas deve nomear o episódio depressivo maior e avaliar seu impacto e duração.",
        "Anedonia, humor deprimido e sintomas cognitivos e vegetativos por seis semanas, com prejuízo funcional, sustentam depressão maior.",
        "Qualquer ideação de morte exige avaliação direta de plano, intenção, meios, fatores protetores e necessidade de cuidado urgente.",
        [
            "Reconhecer depressão maior",
            "Usar PHQ-9 como apoio",
            "Priorizar segurança e seguimento",
        ],
        [
            _safety(
                "Avaliação do risco de suicídio",
                "A ideação passiva não deve ser ignorada e requer avaliação e plano de segurança.",
                "risco de suicidio",
                "plano de seguranca",
                "rede de apoio",
            )
        ],
        _outcomes(
            (
                "A paciente se sente acolhida, aceita o plano de segurança e inicia tratamento.",
                "Há redução progressiva dos sintomas com seguimento clínico estruturado.",
            ),
            (
                "Há orientação inicial, mas o risco ou o acompanhamento ficam incompletos.",
                "A melhora é incerta e sinais de agravamento podem ser percebidos tardiamente.",
            ),
            (
                "A ideação de morte é minimizada e a paciente deixa o atendimento sem proteção.",
                "O risco de crise e dano aumenta sem rede de apoio e reavaliação.",
            ),
            [
                ("PHQ-9", "18/27", "11/27", "16/27", "22/27"),
                ("Sono", "despertar precoce", "melhora", "pouca melhora", "piora"),
                (
                    "Funcionamento",
                    "prejudicado",
                    "retomada gradual",
                    "limitado",
                    "afastamento maior",
                ),
                (
                    "Segurança",
                    "ideação passiva",
                    "plano definido",
                    "avaliação incompleta",
                    "risco não acompanhado",
                ),
            ],
        ),
        ["Depressão maior", "Risco de suicídio", "Tratamento compartilhado"],
        [NICE_DEPRESSION],
    ),
    67: _psy_rubric(
        67,
        "Transtorno de ansiedade generalizada.",
        ["ansiedade generalizada", "transtorno de ansiedade generalizada", "tag"],
        ["transtorno de ansiedade", "ansiedade"],
        ["gad7", "entrevista_ansiedade"],
        ["phq9", "tsh_glicemia", "audit"],
        ["tomografia_cranio"],
        [
            _criterion(
                "Psicoeducação e decisão compartilhada",
                8,
                "psicoeducacao",
                "decisao compartilhada",
            ),
            _criterion(
                "Tratamento psicológico ou farmacológico",
                12,
                "terapia cognitivo",
                "psicoterapia",
                "ssri",
                "antidepressivo",
            ),
            _criterion(
                "Reavaliar sintomas e função",
                10,
                "retorno",
                "reavaliar",
                "gad 7",
                "funcionamento",
            ),
        ],
        "Explicar o diagnóstico, avaliar comorbidades e impacto funcional, oferecer terapia cognitivo-comportamental ou farmacoterapia conforme preferência e gravidade e acompanhar resposta e efeitos adversos.",
        "Ansiedade inespecífica é parcial; o caráter excessivo, multidomínio e persistente por mais de seis meses define TAG.",
        "Preocupação difícil de controlar em vários domínios, associada a tensão, insônia e prejuízo, aponta para TAG.",
        "É preciso avaliar depressão, suicídio e uso de substâncias antes de concluir o plano.",
        ["Diagnosticar TAG", "Interpretar GAD-7", "Planejar tratamento escalonado"],
        [
            _safety(
                "Avaliar comorbidades e risco",
                "Ansiedade pode coexistir com depressão, suicídio e uso de substâncias.",
                "depressao",
                "risco",
                "substancias",
            )
        ],
        _outcomes(
            (
                "A ansiedade diminui e o paciente retoma atividades.",
                "O seguimento permite ajustar o tratamento e recuperar função.",
            ),
            (
                "Há alívio discreto sem estratégia continuada.",
                "Preocupações e insônia persistem com prejuízo parcial.",
            ),
            (
                "Sem avaliação ou seguimento, os sintomas se ampliam.",
                "A evitação e a perda funcional aumentam.",
            ),
            [
                ("GAD-7", "16/21", "8/21", "14/21", "19/21"),
                ("Sono", "insônia", "mais regular", "irregular", "pior"),
                ("Tensão", "frequente", "ocasional", "frequente", "intensa"),
                ("Trabalho", "prejudicado", "melhora", "limitado", "afastamento"),
            ],
        ),
        ["Ansiedade generalizada", "GAD-7", "Terapia cognitivo-comportamental"],
        [NICE_ANXIETY],
    ),
    68: _psy_rubric(
        68,
        "Transtorno do pânico.",
        [
            "transtorno do panico",
            "panico",
            "crises de panico",
            "ataques de panico recorrentes",
        ],
        ["ataque de panico", "transtorno de ansiedade"],
        ["pdss", "entrevista_panico", "ecg"],
        ["tsh_glicemia", "toxicologico"],
        ["holter"],
        [
            _criterion(
                "Explicar o ciclo do pânico", 8, "psicoeducacao", "ciclo do panico"
            ),
            _criterion(
                "Indicar terapia cognitivo-comportamental",
                12,
                "terapia cognitivo",
                "tcc",
                "exposicao",
            ),
            _criterion(
                "Planejar tratamento e retorno",
                10,
                "ssri",
                "antidepressivo",
                "retorno",
                "reavaliar",
            ),
        ],
        "Após excluir urgência clínica pelo contexto, explicar o transtorno, oferecer terapia cognitivo-comportamental e considerar antidepressivo conforme gravidade, evitando dependência de benzodiazepínicos e programando seguimento.",
        "Um ataque isolado não basta; aqui há crises inesperadas recorrentes e preocupação e evitação persistentes.",
        "Crises abruptas com pico em minutos, seguidas de medo de recorrência e evitação, sustentam transtorno do pânico.",
        "Sintomas novos de dor torácica, síncope ou alteração objetiva exigem nova avaliação clínica; não atribua tudo automaticamente à ansiedade.",
        [
            "Reconhecer transtorno do pânico",
            "Diferenciar causas clínicas",
            "Reduzir evitação",
        ],
        [
            _safety(
                "Reavaliar sinais de alarme",
                "Dor persistente, síncope ou alterações objetivas exigem investigação clínica.",
                "sinais de alarme",
                "reavaliar",
                "ecg",
            )
        ],
        _outcomes(
            (
                "A paciente compreende as crises e reduz a evitação.",
                "Terapia e seguimento diminuem frequência e impacto das crises.",
            ),
            (
                "As crises são reconhecidas, mas a evitação permanece.",
                "O prejuízo funcional persiste sem plano terapêutico completo.",
            ),
            (
                "O quadro é banalizado ou tratado apenas com sedação repetida.",
                "A evitação e o risco de dependência medicamentosa aumentam.",
            ),
            [
                ("PDSS", "16/28", "7/28", "13/28", "20/28"),
                ("Crises", "4 no mês", "raras", "recorrentes", "mais frequentes"),
                (
                    "Ônibus",
                    "evita",
                    "retoma gradualmente",
                    "ainda evita",
                    "evita mais locais",
                ),
                ("Ansiedade antecipatória", "alta", "baixa", "moderada", "intensa"),
            ],
        ),
        ["Transtorno do pânico", "PDSS", "Exposição interoceptiva"],
        [NICE_ANXIETY],
    ),
    69: _psy_rubric(
        69,
        "Transtorno de ansiedade social.",
        ["ansiedade social", "transtorno de ansiedade social", "fobia social"],
        ["ansiedade", "transtorno de ansiedade"],
        ["lsas", "entrevista_social"],
        ["phq9", "audit", "gad7"],
        ["eletroencefalograma"],
        [
            _criterion(
                "Avaliar medo, evitação e prejuízo", 8, "medo", "evitacao", "prejuizo"
            ),
            _criterion(
                "Oferecer TCC específica", 12, "terapia cognitivo", "tcc", "exposicao"
            ),
            _criterion(
                "Abordar álcool e acompanhar",
                10,
                "alcool",
                "audit",
                "seguimento",
                "retorno",
            ),
        ],
        "Confirmar medo de avaliação negativa e prejuízo, oferecer TCC individual específica com exposição gradual, considerar farmacoterapia quando indicada e abordar o uso de álcool como estratégia de enfrentamento.",
        "Ansiedade genérica não descreve o medo persistente de avaliação negativa e a evitação social.",
        "Medo de avaliação negativa, evitação persistente e prejuízo acadêmico ou profissional caracterizam ansiedade social.",
        "Usar álcool para enfrentar situações sociais pode evoluir para dano e precisa ser abordado sem julgamento.",
        [
            "Reconhecer ansiedade social",
            "Interpretar LSAS",
            "Planejar exposição gradual",
        ],
        [
            _safety(
                "Avaliar uso de álcool",
                "O consumo para enfrentar situações sociais pode aumentar e causar dependência.",
                "alcool",
                "audit",
                "substancias",
            )
        ],
        _outcomes(
            (
                "O paciente participa do plano e inicia exposição gradual.",
                "A evitação diminui e o funcionamento profissional melhora.",
            ),
            (
                "Há orientação, mas as situações temidas continuam evitadas.",
                "O prejuízo permanece e o álcool pode continuar como estratégia.",
            ),
            (
                "A evitação é reforçada e o consumo de álcool ignorado.",
                "O isolamento e o uso nocivo podem aumentar.",
            ),
            [
                ("LSAS", "78/144", "45/144", "70/144", "92/144"),
                (
                    "Apresentações",
                    "evita",
                    "realiza com apoio",
                    "ainda evita",
                    "recusa todas",
                ),
                ("Álcool", "uso situacional", "reduzido", "mantido", "aumentado"),
                (
                    "Trabalho",
                    "promoção recusada",
                    "retomada",
                    "limitado",
                    "mais prejudicado",
                ),
            ],
        ),
        ["Ansiedade social", "TCC específica", "Uso de álcool"],
        [NICE_SOCIAL_ANXIETY],
    ),
    70: _psy_rubric(
        70,
        "Transtorno de déficit de atenção e hiperatividade no adulto.",
        [
            "tdah",
            "transtorno de deficit de atencao e hiperatividade",
            "deficit de atencao e hiperatividade",
        ],
        ["deficit de atencao", "desatencao"],
        ["asrs", "entrevista_tdah", "historia_desenvolvimento"],
        ["triagem_comorbidades", "tsh_hemograma"],
        ["ressonancia_cranio"],
        [
            _criterion(
                "Confirmar início e prejuízo em vários contextos",
                10,
                "infancia",
                "varios contextos",
                "prejuizo",
            ),
            _criterion(
                "Avaliar comorbidades e substâncias",
                8,
                "comorbidades",
                "ansiedade",
                "humor",
                "substancias",
            ),
            _criterion(
                "Construir plano multimodal",
                12,
                "psicoeducacao",
                "estrategias organizacao",
                "medicacao",
                "seguimento",
            ),
        ],
        "Confirmar sintomas desde a infância e em mais de um contexto, excluir explicações alternativas, orientar estratégias de organização e discutir tratamento psicológico e farmacológico com monitorização.",
        "Desatenção isolada é parcial; o diagnóstico requer início na infância, persistência, múltiplos contextos e prejuízo.",
        "História desde a escola, confirmação familiar e prejuízo em várias áreas sustentam TDAH no adulto.",
        "ASRS é rastreio; não deve ser usado isoladamente para diagnosticar ou prescrever estimulante.",
        [
            "Diagnosticar TDAH no adulto",
            "Distinguir rastreio de diagnóstico",
            "Planejar cuidado multimodal",
        ],
        [
            _safety(
                "Não diagnosticar apenas pelo ASRS",
                "É necessário confirmar história do desenvolvimento, prejuízo e diferenciais.",
                "infancia",
                "historia",
                "comorbidades",
            )
        ],
        _outcomes(
            (
                "O paciente entende o padrão e adota estratégias práticas.",
                "Organização e desempenho melhoram com tratamento monitorado.",
            ),
            (
                "O rastreio é aceito como hipótese, mas faltam dados longitudinais.",
                "A resposta permanece limitada e o diagnóstico incerto.",
            ),
            (
                "O rastreio é tratado como diagnóstico isolado.",
                "Há risco de tratamento inadequado e de perder comorbidades.",
            ),
            [
                (
                    "Tarefas",
                    "frequentemente incompletas",
                    "mais concluídas",
                    "pouca mudança",
                    "mais falhas",
                ),
                ("Atrasos", "frequentes", "raros", "frequentes", "aumentam"),
                (
                    "Trabalho",
                    "prejudicado",
                    "melhora",
                    "limitado",
                    "novo risco de perda",
                ),
                ("Monitorização", "não iniciada", "regular", "incompleta", "ausente"),
            ],
        ),
        ["TDAH no adulto", "ASRS", "Diagnóstico longitudinal"],
        [NICE_ADHD],
    ),
    71: _psy_rubric(
        71,
        "Transtorno obsessivo-compulsivo.",
        ["toc", "transtorno obsessivo compulsivo", "obsessivo compulsivo"],
        ["obsessao", "compulsao", "transtorno de ansiedade"],
        ["ybocs", "entrevista_toc", "risco_humor"],
        ["tiques", "dermatologica"],
        ["ressonancia_cranio"],
        [
            _criterion("Medir prejuízo e risco", 8, "ybocs", "prejuizo", "risco"),
            _criterion(
                "Oferecer TCC com exposição e prevenção de resposta",
                12,
                "exposicao",
                "prevencao de resposta",
                "tcc",
            ),
            _criterion(
                "Considerar ISRS e acompanhar",
                10,
                "isrs",
                "ssri",
                "antidepressivo",
                "seguimento",
            ),
        ],
        "Avaliar tempo, sofrimento, prejuízo e comorbidades, oferecer TCC com exposição e prevenção de resposta e considerar ISRS conforme gravidade, acompanhando pele e risco.",
        "Obsessões ou compulsões isoladas são parciais; o conjunto consome horas e causa prejuízo significativo.",
        "Pensamentos intrusivos reconhecidos como indesejados e rituais repetitivos para reduzir ansiedade caracterizam TOC.",
        "A exposição deve ser planejada terapeuticamente; não se deve impor interrupção abrupta e humilhante dos rituais.",
        [
            "Reconhecer TOC",
            "Interpretar Y-BOCS",
            "Indicar exposição e prevenção de resposta",
        ],
        [
            _safety(
                "Avaliar depressão e suicídio",
                "TOC grave pode coexistir com depressão e risco de suicídio.",
                "depressao",
                "suicidio",
                "risco",
            )
        ],
        _outcomes(
            (
                "O paciente compreende o ciclo e adere ao plano gradual.",
                "O tempo gasto em rituais e as lesões nas mãos diminuem.",
            ),
            (
                "Há reconhecimento, mas sem tratamento específico suficiente.",
                "Os rituais continuam consumindo horas do dia.",
            ),
            (
                "Os rituais são confrontados sem suporte e o risco é ignorado.",
                "Ansiedade, lesões e isolamento pioram.",
            ),
            [
                ("Y-BOCS", "24/40", "14/40", "22/40", "30/40"),
                ("Rituais", "3 h/dia", "1 h/dia", "2,5 h/dia", "4 h/dia"),
                ("Pele", "escoriada", "cicatrizando", "irritada", "infectada"),
                ("Trabalho", "atrasos", "regular", "atrasos persistem", "faltas"),
            ],
        ),
        ["TOC", "Y-BOCS", "Exposição e prevenção de resposta"],
        [NICE_OCD],
    ),
    72: _psy_rubric(
        72,
        "Transtorno de estresse pós-traumático.",
        ["tept", "transtorno de estresse pos traumatico", "estresse pos traumatico"],
        ["reacao ao trauma", "transtorno relacionado a trauma"],
        ["pcl5", "entrevista_trauma", "risco_depressao"],
        ["dissociacao", "audit"],
        ["cortisol"],
        [
            _criterion(
                "Avaliar trauma, sintomas e segurança",
                10,
                "trauma",
                "risco",
                "seguranca",
            ),
            _criterion(
                "Oferecer psicoterapia focada no trauma",
                12,
                "terapia focada no trauma",
                "tcc trauma",
                "emdr",
            ),
            _criterion(
                "Tratar comorbidades e acompanhar",
                8,
                "depressao",
                "alcool",
                "seguimento",
                "retorno",
            ),
        ],
        "Conduzir avaliação sensível ao trauma, checar segurança e comorbidades, oferecer psicoterapia focada no trauma ou EMDR conforme indicação e preferência, e acompanhar sono, funcionamento e risco.",
        "Reação ao trauma é parcial; a duração, os quatro grupos de sintomas e o prejuízo sustentam TEPT.",
        "Intrusões, evitação, alterações de humor e hiperativação por seis meses após trauma caracterizam TEPT.",
        "Não force relato detalhado do trauma nem use a escala como diagnóstico isolado; preserve autonomia e segurança.",
        [
            "Diagnosticar TEPT",
            "Interpretar PCL-5",
            "Oferecer cuidado informado pelo trauma",
        ],
        [
            _safety(
                "Avaliar risco e evitar retraumatização",
                "A abordagem deve avaliar suicídio e preservar controle e segurança da paciente.",
                "risco",
                "seguranca",
                "consentimento",
            )
        ],
        _outcomes(
            (
                "A paciente sente controle e inicia tratamento focado no trauma.",
                "Intrusões, evitação e hiperalerta diminuem gradualmente.",
            ),
            (
                "Há acolhimento, mas o tratamento permanece inespecífico.",
                "Sintomas e prejuízo persistem.",
            ),
            (
                "O trauma é explorado de forma coercitiva e sem segurança.",
                "Pode ocorrer retraumatização, abandono e piora do risco.",
            ),
            [
                ("PCL-5", "46/80", "27/80", "42/80", "58/80"),
                ("Pesadelos", "frequentes", "raros", "frequentes", "mais intensos"),
                (
                    "Direção",
                    "evita",
                    "retoma gradualmente",
                    "ainda evita",
                    "evita sair",
                ),
                ("Hiperalerta", "alto", "reduzido", "mantido", "intenso"),
            ],
        ),
        ["TEPT", "PCL-5", "Terapias focadas no trauma"],
        [NICE_PTSD],
    ),
    73: _psy_rubric(
        73,
        "Transtorno bipolar tipo I em episódio maníaco.",
        ["transtorno bipolar", "bipolar tipo i", "episodio maniaco", "mania"],
        ["hipomania", "transtorno do humor"],
        ["ymrs", "estado_mental_risco", "toxicologico", "tsh_metabolico"],
        ["beta_hcg"],
        ["ressonancia_cranio"],
        [
            _criterion(
                "Proteger e definir ambiente de cuidado",
                10,
                "internacao",
                "ambiente protegido",
                "risco",
                "psiquiatria urgente",
            ),
            _criterion(
                "Tratar mania aguda",
                12,
                "antipsicotico",
                "litio",
                "estabilizador do humor",
            ),
            _criterion(
                "Reduzir estímulos e monitorar",
                8,
                "reduzir estimulos",
                "sono",
                "monitorar",
                "reavaliar",
            ),
        ],
        "Avaliar risco e capacidade, interromper exposições financeiras e outras situações perigosas, encaminhar para cuidado psiquiátrico urgente e iniciar tratamento da mania conforme protocolo e condições clínicas, com ambiente de baixa estimulação.",
        "Hipomania não produz este grau de prejuízo e risco; o quadro configura mania e sustenta bipolar tipo I.",
        "Redução da necessidade de sono, grandiosidade, aceleração e comportamento arriscado com prejuízo importante caracterizam mania.",
        "O julgamento está comprometido; alta sem contenção de riscos e avaliação psiquiátrica urgente é insegura.",
        [
            "Reconhecer mania",
            "Diferenciar hipomania",
            "Priorizar proteção e estabilização",
        ],
        [
            _safety(
                "Cuidado psiquiátrico urgente",
                "Mania com julgamento comprometido exige ambiente seguro e avaliação urgente.",
                "internacao",
                "psiquiatria urgente",
                "ambiente protegido",
            )
        ],
        _outcomes(
            (
                "A agitação reduz e o sono começa a se reorganizar em ambiente protegido.",
                "O episódio estabiliza com tratamento e planejamento longitudinal.",
            ),
            (
                "Há sedação parcial, mas riscos e tratamento de base ficam incompletos.",
                "Impulsividade e prejuízo permanecem.",
            ),
            (
                "O paciente é liberado apesar do julgamento gravemente comprometido.",
                "Gastos, exposição, acidentes e agravamento da mania tornam-se prováveis.",
            ),
            [
                ("YMRS", "32/60", "16/60", "27/60", "40/60"),
                ("Sono", "2 h/noite", "6 h/noite", "3 h/noite", "sem dormir"),
                ("Agitação", "importante", "leve", "moderada", "grave"),
                ("Risco financeiro", "alto", "protegido", "parcial", "ativo"),
            ],
        ),
        ["Mania", "Transtorno bipolar", "Proteção na crise"],
        [NICE_BIPOLAR],
    ),
    74: _psy_rubric(
        74,
        "Síndrome de abstinência alcoólica.",
        [
            "abstinencia alcoolica",
            "sindrome de abstinencia alcoolica",
            "abstinencia de alcool",
        ],
        ["transtorno por uso de alcool", "dependencia de alcool", "alcoolismo"],
        ["ciwaar", "glicose_eletrólitos", "hemograma_hepatico"],
        ["audit", "ecg"],
        ["tomografia_cranio"],
        [
            _criterion(
                "Monitorar gravidade e complicações",
                10,
                "ciwa",
                "monitorizacao",
                "convulsao",
                "delirium tremens",
            ),
            _criterion(
                "Tratar abstinência e repor tiamina",
                12,
                "benzodiazepinico",
                "tiamina",
                "magnesio",
                "eletrólitos",
            ),
            _criterion(
                "Planejar cuidado continuado",
                8,
                "tratamento do alcool",
                "seguimento",
                "reabilitacao",
                "psicossocial",
            ),
        ],
        "Monitorar CIWA-Ar e sinais vitais, tratar abstinência conforme gravidade e protocolo, administrar tiamina e corrigir glicose e eletrólitos com sequência segura, vigiar convulsões e delirium tremens e planejar tratamento continuado do uso de álcool.",
        "Dependência explica o risco, mas o diagnóstico agudo é síndrome de abstinência alcoólica.",
        "Interrupção recente após uso diário, tremor, sudorese, ansiedade e hiperatividade autonômica indicam abstinência alcoólica.",
        "O quadro pode evoluir para convulsões ou delirium tremens; é inseguro tratar sem monitorização e tiamina.",
        [
            "Reconhecer abstinência alcoólica",
            "Aplicar CIWA-Ar",
            "Prevenir complicações",
        ],
        [
            _safety(
                "Prevenir complicações graves",
                "Monitorização, tiamina e tratamento adequado reduzem risco de convulsão e delirium tremens.",
                "ciwa",
                "tiamina",
                "convulsao",
                "delirium tremens",
            )
        ],
        _outcomes(
            (
                "Tremor e hiperatividade autonômica diminuem sob monitorização.",
                "A abstinência resolve sem convulsão e o paciente aceita cuidado continuado.",
            ),
            (
                "Os sintomas reduzem parcialmente, mas faltam reposição ou plano longitudinal.",
                "Persistem riscos metabólicos e de recaída.",
            ),
            (
                "Sem monitorização e tratamento, a agitação e a confusão aumentam.",
                "Pode evoluir para convulsão, delirium tremens e instabilidade clínica.",
            ),
            [
                ("CIWA-Ar", "17", "6", "14", "28"),
                ("Frequência cardíaca", "112 bpm", "86 bpm", "104 bpm", "132 bpm"),
                ("Tremor", "moderado", "discreto", "moderado", "intenso"),
                ("Orientação", "preservada", "preservada", "preservada", "confusa"),
            ],
        ),
        ["Abstinência alcoólica", "CIWA-Ar", "Tiamina e eletrólitos"],
        [NICE_ALCOHOL],
    ),
    75: _psy_rubric(
        75,
        "Anorexia nervosa.",
        ["anorexia", "anorexia nervosa", "transtorno alimentar restritivo"],
        ["transtorno alimentar", "baixo peso"],
        ["scoff", "antropometria_ortostase", "eletrólitos_renal", "ecg"],
        ["hemograma_hepatico"],
        ["densitometria"],
        [
            _criterion(
                "Reconhecer instabilidade e encaminhar",
                10,
                "internacao",
                "estabilizacao",
                "urgencia",
                "equipe especializada",
            ),
            _criterion(
                "Corrigir riscos e realimentar com segurança",
                12,
                "eletrólitos",
                "fosforo",
                "realimentacao",
                "monitorizacao",
            ),
            _criterion(
                "Cuidado multidisciplinar",
                8,
                "nutricao",
                "psiquiatria",
                "psicoterapia",
                "equipe multidisciplinar",
            ),
        ],
        "Reconhecer instabilidade por bradicardia, hipotensão, hipotermia, baixo IMC e distúrbios eletrolíticos, encaminhar para estabilização médica, corrigir alterações e iniciar realimentação monitorada com equipe especializada e cuidado psicológico.",
        "Baixo peso é parcial; restrição persistente, medo de engordar e distorção da autoavaliação indicam anorexia nervosa.",
        "Restrição, peso significativamente baixo e medo intenso de ganho ponderal sustentam anorexia nervosa.",
        "Esta paciente está clinicamente instável; alta simples ou realimentação rápida sem monitorização pode causar arritmia e síndrome de realimentação.",
        [
            "Diagnosticar anorexia nervosa",
            "Reconhecer instabilidade médica",
            "Prevenir síndrome de realimentação",
        ],
        [
            _safety(
                "Estabilização médica",
                "Bradicardia, hipotensão, hipotermia e eletrólitos alterados exigem cuidado médico urgente.",
                "internacao",
                "estabilizacao",
                "monitorizacao",
            )
        ],
        _outcomes(
            (
                "A paciente é acolhida e os riscos orgânicos são tratados sem julgamento.",
                "A estabilização e a realimentação monitorada permitem cuidado longitudinal.",
            ),
            (
                "Há orientação nutricional, mas instabilidade e eletrólitos não recebem vigilância suficiente.",
                "Persistem risco cardíaco e dificuldade de adesão.",
            ),
            (
                "A instabilidade é ignorada ou a alimentação é aumentada sem monitorização.",
                "Arritmia, síncope e síndrome de realimentação podem ocorrer.",
            ),
            [
                ("Frequência cardíaca", "48 bpm", "60 bpm", "50 bpm", "38 bpm"),
                (
                    "Pressão em pé",
                    "80/50 mmHg",
                    "98/64 mmHg",
                    "84/52 mmHg",
                    "70/42 mmHg",
                ),
                ("Potássio", "3,1 mEq/L", "3,8 mEq/L", "3,2 mEq/L", "2,6 mEq/L"),
                ("Fósforo", "2,4 mg/dL", "3,2 mg/dL", "2,3 mg/dL", "1,4 mg/dL"),
            ],
        ),
        ["Anorexia nervosa", "Risco cardiovascular", "Síndrome de realimentação"],
        [NICE_EATING],
    ),
    76: _psy_rubric(
        76,
        "Primeiro episódio psicótico compatível com esquizofrenia.",
        [
            "esquizofrenia",
            "primeiro episodio psicotico",
            "psicose",
            "transtorno psicotico",
        ],
        ["surto psicotico", "psicose nao especificada"],
        [
            "panss",
            "estado_mental_risco",
            "historia_colateral",
            "toxicologico",
            "laboratorio_baseline",
        ],
        [],
        ["spect_cerebral"],
        [
            _criterion(
                "Proteger e avaliar urgência",
                10,
                "risco",
                "ambiente seguro",
                "psiquiatria urgente",
                "internacao",
            ),
            _criterion(
                "Iniciar cuidado para primeiro episódio",
                12,
                "antipsicotico",
                "intervencao precoce",
                "equipe especializada",
            ),
            _criterion(
                "Incluir família e monitorar saúde física",
                8,
                "familia",
                "psicoeducacao",
                "metabolico",
                "seguimento",
            ),
        ],
        "Avaliar risco, capacidade e necessidades básicas, organizar cuidado especializado precoce e ambiente seguro, discutir antipsicótico em decisão compartilhada, envolver família com consentimento e monitorar saúde física e efeitos adversos.",
        "Psicose é aceitável como reconhecimento inicial; a duração e o declínio funcional tornam esquizofrenia uma hipótese de referência.",
        "Delírios, alucinações, sintomas negativos e declínio funcional prolongado sem síndrome afetiva ou substância predominante indicam primeiro episódio psicótico compatível com esquizofrenia.",
        "Vozes, delírios e autocuidado comprometido exigem avaliação direta de risco e capacidade; confronto hostil pode aumentar desconfiança.",
        [
            "Reconhecer primeiro episódio psicótico",
            "Avaliar causas e risco",
            "Iniciar intervenção precoce",
        ],
        [
            _safety(
                "Avaliação urgente de risco e capacidade",
                "Psicose ativa com julgamento comprometido exige proteção e cuidado especializado.",
                "risco",
                "capacidade",
                "ambiente seguro",
                "psiquiatria urgente",
            )
        ],
        _outcomes(
            (
                "O paciente aceita permanecer em ambiente seguro e a agitação diminui.",
                "O cuidado precoce melhora adesão e reduz duração da psicose não tratada.",
            ),
            (
                "A psicose é reconhecida, mas faltam proteção ou continuidade.",
                "Sintomas e declínio funcional persistem.",
            ),
            (
                "O paciente é confrontado ou liberado sem avaliação de risco.",
                "Desorganização, abandono do autocuidado e dano podem aumentar.",
            ),
            [
                ("PANSS", "92", "68", "86", "108"),
                ("Vozes", "frequentes", "menos intrusivas", "persistentes", "comandos"),
                ("Autocuidado", "reduzido", "melhora", "reduzido", "abandono"),
                ("Vínculo", "desconfiado", "colaborativo", "frágil", "rompido"),
            ],
        ),
        ["Primeiro episódio psicótico", "Esquizofrenia", "Intervenção precoce"],
        [NICE_PSYCHOSIS],
    ),
    77: _psy_rubric(
        77,
        "Psicose pós-parto.",
        [
            "psicose pos parto",
            "psicose pos-parto",
            "psicose puerperal",
            "psicose no puerperio",
        ],
        ["mania pos parto", "transtorno bipolar pos parto", "psicose"],
        ["estado_mental_risco", "historia_colateral", "laboratorio_organico"],
        ["epds", "toxicologico"],
        ["ressonancia_cranio"],
        [
            _criterion(
                "Proteger mãe e bebê imediatamente",
                12,
                "separacao supervisionada",
                "nao deixar sozinha",
                "proteger bebe",
                "internacao",
            ),
            _criterion(
                "Acionar psiquiatria perinatal urgente",
                10,
                "psiquiatria urgente",
                "equipe perinatal",
                "emergencia",
            ),
            _criterion(
                "Tratar psicose e restaurar sono",
                8,
                "antipsicotico",
                "estabilizador",
                "sono",
                "monitorizacao",
            ),
        ],
        "Não deixar mãe e bebê sozinhos, organizar supervisão segura e avaliação psiquiátrica perinatal imediata, geralmente hospitalar, tratar psicose e sintomas afetivos conforme protocolo e apoiar vínculo e amamentação com avaliação individual de riscos e benefícios.",
        "Mania ou psicose são reconhecimentos parciais; a relação temporal com o parto define a emergência perinatal.",
        "Início abrupto de insônia, sintomas maniformes, desorganização e delírios poucos dias após o parto caracteriza psicose pós-parto.",
        "É emergência psiquiátrica: mãe e bebê não devem ficar sem supervisão enquanto o risco é avaliado e tratado.",
        [
            "Reconhecer psicose pós-parto",
            "Proteger mãe e bebê",
            "Acionar cuidado perinatal urgente",
        ],
        [
            _safety(
                "Proteção materno-infantil imediata",
                "Psicose pós-parto pode trazer risco imprevisível e exige supervisão e internação urgente.",
                "proteger bebe",
                "nao deixar sozinha",
                "internacao",
                "psiquiatria urgente",
            )
        ],
        _outcomes(
            (
                "Mãe e bebê permanecem protegidos e a agitação começa a reduzir.",
                "Tratamento urgente promove estabilização e planejamento familiar seguro.",
            ),
            (
                "Há avaliação, mas supervisão ou tratamento ficam incompletos.",
                "Persistem delírios, privação de sono e risco materno-infantil.",
            ),
            (
                "A paciente permanece sozinha com o bebê apesar da psicose.",
                "O risco de dano acidental, suicídio ou violência aumenta de forma crítica.",
            ),
            [
                ("Sono", "quase ausente", "5 h/noite", "2 h/noite", "sem dormir"),
                ("Agitação", "importante", "leve", "moderada", "grave"),
                (
                    "Pensamento",
                    "desorganizado",
                    "mais organizado",
                    "ainda desorganizado",
                    "mais desorganizado",
                ),
                (
                    "Segurança",
                    "alto risco potencial",
                    "supervisão contínua",
                    "proteção parcial",
                    "sem supervisão",
                ),
            ],
        ),
        ["Psicose pós-parto", "Emergência perinatal", "Segurança materno-infantil"],
        [NICE_PERINATAL],
    ),
    78: _psy_rubric(
        78,
        "Catatonia.",
        ["catatonia", "sindrome catatonica", "estado catatonico"],
        ["estupor", "mutismo"],
        ["bush_francis", "teste_lorazepam", "ck_metabolico"],
        ["eeg", "infeccioso_autoimune"],
        ["teste_personalidade"],
        [
            _criterion(
                "Reconhecer e monitorar complicações",
                10,
                "catatonia",
                "ck",
                "trombose",
                "aspiracao",
                "monitorizacao",
            ),
            _criterion(
                "Realizar teste e tratar com benzodiazepínico",
                12,
                "lorazepam",
                "benzodiazepinico",
                "teste de lorazepam",
            ),
            _criterion(
                "Escalonar para ECT quando indicado",
                8,
                "ect",
                "eletroconvulsoterapia",
                "refrataria",
                "maligna",
            ),
        ],
        "Reconhecer catatonia, oferecer suporte de hidratação, nutrição e prevenção de complicações, realizar teste com lorazepam sob monitorização e tratar; considerar ECT rapidamente em forma grave, maligna ou refratária, investigando a causa de base.",
        "Mutismo ou estupor isolados são parciais; múltiplos sinais motores e resposta ao lorazepam sustentam catatonia.",
        "Imobilidade, mutismo, postura, negativismo e flexibilidade cérea formam síndrome catatônica.",
        "Catatonia pode causar desidratação, trombose, aspiração e hipertermia; antipsicótico sem avaliação pode agravar alguns quadros.",
        [
            "Reconhecer catatonia",
            "Aplicar Bush-Francis",
            "Tratar e prevenir complicações",
        ],
        [
            _safety(
                "Tratar urgentemente e prevenir complicações",
                "Imobilidade e recusa alimentar exigem hidratação, profilaxias e tratamento específico.",
                "lorazepam",
                "hidratacao",
                "trombose",
                "aspiracao",
            )
        ],
        _outcomes(
            (
                "O paciente volta a se mover e falar após tratamento monitorado.",
                "A catatonia resolve e a causa de base recebe tratamento.",
            ),
            (
                "Há melhora discreta, mas suporte ou escalonamento ficam incompletos.",
                "Persistem imobilidade e risco de complicações.",
            ),
            (
                "A síndrome não é reconhecida e o paciente permanece imóvel e sem hidratação.",
                "Pode evoluir com lesão renal, trombose, aspiração ou catatonia maligna.",
            ),
            [
                ("Bush-Francis", "18", "5", "14", "24"),
                ("Fala", "mutismo", "frases curtas", "palavras isoladas", "mutismo"),
                (
                    "Mobilidade",
                    "imóvel",
                    "deambula com ajuda",
                    "pouca",
                    "rigidez crescente",
                ),
                ("CK", "620 U/L", "320 U/L", "700 U/L", "2.400 U/L"),
            ],
        ),
        ["Catatonia", "Bush-Francis", "Lorazepam e ECT"],
        [BAP_CATATONIA],
    ),
    79: _psy_rubric(
        79,
        "Transtorno de personalidade borderline.",
        [
            "borderline",
            "transtorno de personalidade borderline",
            "personalidade borderline",
        ],
        ["transtorno de personalidade", "instabilidade emocional"],
        ["entrevista_personalidade", "risco_autolesao", "historia_longitudinal"],
        ["msibpd", "comorbidades"],
        ["ressonancia_cranio"],
        [
            _criterion(
                "Avaliar suicídio e autolesão sem julgamento",
                10,
                "risco de suicidio",
                "autolesao",
                "plano de seguranca",
            ),
            _criterion(
                "Construir plano colaborativo de crise",
                10,
                "plano de crise",
                "gatilhos",
                "rede de apoio",
                "colaborativo",
            ),
            _criterion(
                "Encaminhar para psicoterapia estruturada",
                10,
                "psicoterapia",
                "terapia dialetica",
                "mentalizacao",
                "seguimento",
            ),
        ],
        "Avaliar diretamente suicídio e autolesão, validar sofrimento sem reforçar condutas de risco, construir plano colaborativo de crise e encaminhar para psicoterapia estruturada, tratando comorbidades; não usar medicamento como tratamento específico do transtorno isolado.",
        "Instabilidade emocional é parcial; o diagnóstico requer padrão persistente, amplo e iniciado no começo da vida adulta.",
        "Instabilidade interpessoal e da autoimagem, medo de abandono, impulsividade e autolesão persistentes sustentam borderline.",
        "Autolesão sempre exige avaliação cuidadosa de intenção suicida, gatilhos, meios, proteção e seguimento, sem estigma.",
        [
            "Reconhecer borderline longitudinalmente",
            "Avaliar autolesão",
            "Planejar psicoterapia estruturada",
        ],
        [
            _safety(
                "Avaliar suicídio e autolesão",
                "Autolesão não deve ser banalizada; risco, intenção e proteção precisam ser avaliados em cada crise.",
                "risco de suicidio",
                "autolesao",
                "plano de seguranca",
            )
        ],
        _outcomes(
            (
                "A paciente se sente validada e participa de um plano de crise.",
                "Psicoterapia estruturada reduz crises e melhora regulação emocional.",
            ),
            (
                "Há acolhimento, mas plano de segurança ou continuidade ficam frágeis.",
                "Crises e autolesões podem continuar recorrentes.",
            ),
            (
                "A paciente é estigmatizada ou liberada sem avaliar autolesão.",
                "O vínculo se rompe e o risco de dano e abandono do cuidado aumenta.",
            ),
            [
                (
                    "Risco",
                    "gatilho recente",
                    "plano ativo",
                    "plano incompleto",
                    "não avaliado",
                ),
                ("Autolesão", "recorrente", "reduz", "persiste", "aumenta"),
                ("Vínculo", "frágil", "colaborativo", "instável", "rompido"),
                ("Seguimento", "irregular", "estruturado", "incerto", "ausente"),
            ],
        ),
        ["Borderline", "Autolesão", "Psicoterapia estruturada"],
        [NICE_BORDERLINE],
    ),
    80: _psy_rubric(
        80,
        "Delirium.",
        ["delirium", "estado confusional agudo", "confusao aguda"],
        ["encefalopatia", "demencia", "psicose organica"],
        ["quatro_at", "cam", "laboratorio_infeccao", "revisao_medicamentos"],
        ["culturas"],
        ["inventario_personalidade"],
        [
            _criterion(
                "Tratar causas e revisar medicamentos",
                12,
                "tratar infeccao",
                "antibiotico",
                "corrigir sodio",
                "suspender anticolinergico",
            ),
            _criterion(
                "Aplicar medidas não farmacológicas",
                10,
                "reorientacao",
                "familia",
                "sono",
                "oculos",
                "hidratacao",
            ),
            _criterion(
                "Proteger e monitorar",
                8,
                "monitorizacao",
                "queda",
                "ambiente seguro",
                "reavaliar",
            ),
        ],
        "Tratar infecção e alterações metabólicas, retirar fármacos precipitantes quando possível, hidratar e aplicar reorientação, mobilidade, sono e suporte sensorial, mantendo ambiente seguro e monitorização. Reservar medicação para agitação com risco após medidas não farmacológicas.",
        "Demência é parcial, mas o início agudo, a flutuação e a desatenção caracterizam delirium sobre estado basal previamente preservado.",
        "Mudança aguda e flutuante da atenção e consciência com pensamento desorganizado define delirium e exige busca de causa orgânica.",
        "Delirium é emergência clínica; sedação sem tratar infecção, eletrólitos e medicamentos precipitantes pode agravar o quadro.",
        ["Diagnosticar delirium", "Usar 4AT e CAM", "Tratar causas e prevenir danos"],
        [
            _safety(
                "Investigar e tratar causa orgânica",
                "Delirium não deve ser atribuído apenas a doença psiquiátrica; a causa clínica precisa de tratamento urgente.",
                "tratar infeccao",
                "eletrólitos",
                "medicamentos",
                "hidratacao",
            )
        ],
        _outcomes(
            (
                "A atenção e a orientação melhoram à medida que a causa é tratada.",
                "O delirium resolve gradualmente, com prevenção de quedas e complicações.",
            ),
            (
                "Há contenção da agitação, mas causas ou medidas ambientais ficam incompletas.",
                "A flutuação persiste e a internação se prolonga.",
            ),
            (
                "O quadro é tratado apenas como agitação psiquiátrica.",
                "Infecção e distúrbios metabólicos pioram, com risco de queda e disfunção orgânica.",
            ),
            [
                ("4AT", "8", "2", "7", "11"),
                ("Atenção", "muito prejudicada", "sustentada", "flutuante", "ausente"),
                ("Temperatura", "38,2 °C", "37,2 °C", "38,0 °C", "39,3 °C"),
                ("Frequência cardíaca", "106 bpm", "84 bpm", "102 bpm", "128 bpm"),
            ],
        ),
        ["Delirium", "4AT e CAM", "Causas precipitantes"],
        [NICE_DELIRIUM],
    ),
}
