"""Segundo lote de expansão, calibrado para dificuldade intermediária."""

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
        "nivel_dificuldade": "Intermediário",
        "historia_clinica": history,
        "exame_fisico": physical_exam,
        "exames_disponiveis": exams,
    }


def _source(title: str, organization: str, year: int, url: str) -> dict[str, Any]:
    return {
        "titulo": title,
        "organizacao": organization,
        "ano": year,
        "url": url,
    }


def _criterion(name: str, points: int, *terms: str) -> dict[str, Any]:
    return {"nome": name, "pontos": points, "termos": list(terms)}


def _safety(name: str, feedback: str, *terms: str) -> dict[str, Any]:
    return {
        "nome": name,
        "termos": list(terms),
        "feedback_omissao": feedback,
    }


def _vital(
    indicator: str,
    before: str,
    after: str,
    trend: str,
) -> dict[str, str]:
    return {
        "indicador": indicator,
        "antes": before,
        "depois": after,
        "tendencia": trend,
    }


CAP_SOURCE = _source(
    "Diagnosis and Treatment of Adults with Community-acquired Pneumonia",
    "American Thoracic Society and Infectious Diseases Society of America",
    2019,
    "https://www.thoracic.org/statements/guideline-implementation-tools/diagnosis-and-treatment-of-cap.php",
)
CHOLECYSTITIS_SOURCE = _source(
    "Tokyo Guidelines 2018 for acute cholecystitis",
    "Japanese Society of Hepato-Biliary-Pancreatic Surgery",
    2018,
    "https://www.jshbps.jp/modules/en/index.php?content_id=47",
)
DKA_SOURCE = _source(
    "Hyperglycemic Crises in Adults With Diabetes: A Consensus Report",
    "American Diabetes Association",
    2024,
    "https://diabetesjournals.org/care/article/47/8/1257/156808/Hyperglycemic-Crises-in-Adults-With-Diabetes-A",
)
ECTOPIC_SOURCE = _source(
    "Tubal Ectopic Pregnancy",
    "American College of Obstetricians and Gynecologists",
    2018,
    "https://www.acog.org/clinical/clinical-guidance/practice-bulletin/articles/2018/03/tubal-ectopic-pregnancy",
)
ANGLE_CLOSURE_SOURCE = _source(
    "Primary Angle-Closure Disease Preferred Practice Pattern",
    "American Academy of Ophthalmology",
    2025,
    "https://www.aao.org/education/preferred-practice-pattern/primary-angle-closure-disease-ppp",
)


EXPANSION_BATCH_TWO_TITLES = {
    61: "Febre, tosse e falta de ar há quatro dias",
    62: "Dor do lado direito do abdome após as refeições",
    63: "Muita sede, vômitos e respiração acelerada",
    64: "Atraso menstrual, sangramento e dor pélvica",
    65: "Dor intensa no olho com visão embaçada",
}


EXPANSION_BATCH_TWO_CASES = [
    _case(
        61,
        "Pneumonia adquirida na comunidade",
        "Pneumologia",
        (
            "ALP, 67 anos, masculino, apresenta febre, tosse com expectoração amarelada, "
            "dor no lado direito do tórax ao respirar e falta de ar há quatro dias. "
            "Tem hipertensão controlada, nega internação recente e não usou antibiótico "
            "nos últimos três meses."
        ),
        (
            "REG, lúcido e hidratado. PA: 112/70 mmHg; FC: 108 bpm; FR: 26 irpm; "
            "SpO2: 90%; Temperatura: 38,7 °C. Estertores e redução do murmúrio "
            "vesicular na base direita, sem uso intenso da musculatura acessória."
        ),
        [
            _exam(
                "radiografia_torax",
                "Radiografia de tórax",
                "Consolidação no lobo inferior direito com broncograma aéreo; sem derrame pleural volumoso.",
            ),
            _exam(
                "hemograma_pcr",
                "Hemograma e proteína C reativa",
                "Leucócitos 15.200/mm³ com neutrofilia; PCR 126 mg/L (VR: < 5 mg/L).",
            ),
            _exam(
                "funcao_renal_eletrólitos",
                "Função renal e eletrólitos",
                "Ureia 48 mg/dL; creatinina 1,2 mg/dL; sódio 136 mEq/L; potássio 4,0 mEq/L.",
            ),
            _exam(
                "gasometria_arterial",
                "Gasometria arterial",
                "pH 7,44; PaCO2 34 mmHg; PaO2 61 mmHg em ar ambiente, confirmando hipoxemia.",
            ),
            _exam(
                "painel_viral",
                "Painel viral respiratório",
                "Influenza A/B e SARS-CoV-2 não detectados.",
            ),
            _exam(
                "tomografia_torax",
                "Tomografia de tórax",
                "Consolidação basal direita sem abscesso; exame sem necessidade inicial diante da radiografia conclusiva.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        62,
        "Colecistite aguda calculosa",
        "Cirurgia",
        (
            "VRS, 44 anos, feminina, relata dor contínua no hipocôndrio direito há "
            "18 horas, iniciada após refeição gordurosa, acompanhada de náuseas e dois "
            "episódios de vômito. Já teve cólicas semelhantes mais curtas, mas nega "
            "icterícia, urina escura ou gravidez."
        ),
        (
            "REG, orientada e levemente desidratada. PA: 118/74 mmHg; FC: 102 bpm; "
            "FR: 20 irpm; SpO2: 98%; Temperatura: 38,1 °C. Dor e defesa localizada "
            "no hipocôndrio direito, com sinal de Murphy positivo e sem rigidez difusa."
        ),
        [
            _exam(
                "ultrassom_abdome",
                "Ultrassonografia de abdome superior",
                "Cálculo impactado no colo da vesícula, parede de 5 mm, líquido perivesicular e Murphy ultrassonográfico positivo; colédoco com 5 mm.",
            ),
            _exam(
                "hemograma_pcr",
                "Hemograma e proteína C reativa",
                "Leucócitos 14.100/mm³ com neutrofilia; PCR 78 mg/L (VR: < 5 mg/L).",
            ),
            _exam(
                "provas_hepaticas",
                "Bilirrubinas e enzimas hepáticas",
                "Bilirrubina total 1,1 mg/dL; AST 38 U/L; ALT 42 U/L; fosfatase alcalina 118 U/L, sem padrão de obstrução biliar.",
            ),
            _exam(
                "lipase",
                "Lipase sérica",
                "42 U/L (VR: 13–60 U/L), sem evidência de pancreatite associada.",
            ),
            _exam(
                "beta_hcg",
                "Beta-hCG",
                "Não reagente.",
            ),
            _exam(
                "tomografia_abdome",
                "Tomografia de abdome",
                "Espessamento da vesícula e inflamação local; exame redundante após ultrassom típico e sem complicação suspeita.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        63,
        "Cetoacidose diabética",
        "Endocrinologia",
        (
            "LCM, 23 anos, feminino, com diabetes tipo 1, apresenta muita sede, aumento "
            "do volume urinário, náuseas, vômitos e dor abdominal há um dia. Relata "
            "que interrompeu a insulina durante um quadro gripal por estar comendo pouco."
        ),
        (
            "REG, sonolenta, porém desperta ao chamado, desidratada e com hálito cetônico. "
            "PA: 96/62 mmHg; FC: 118 bpm; FR: 30 irpm; SpO2: 97%; Temperatura: 37,8 °C. "
            "Respiração profunda, mucosas secas e abdome difusamente doloroso, sem defesa."
        ),
        [
            _exam(
                "glicemia_cetonemia",
                "Glicemia e beta-hidroxibutirato",
                "Glicose 428 mg/dL; beta-hidroxibutirato 5,8 mmol/L (elevado).",
            ),
            _exam(
                "gasometria_eletrólitos",
                "Gasometria venosa e eletrólitos",
                "pH 7,19; bicarbonato 11 mEq/L; sódio 132 mEq/L; potássio 5,2 mEq/L; ânion gap 22 mEq/L.",
            ),
            _exam(
                "funcao_renal",
                "Função renal",
                "Ureia 62 mg/dL e creatinina 1,6 mg/dL, compatíveis com desidratação e lesão renal pré-renal.",
            ),
            _exam(
                "urina_tipo_1",
                "Urina tipo 1",
                "Glicosúria e cetonúria 3+; leucócitos 2 por campo e nitrito negativo.",
            ),
            _exam(
                "ecg",
                "ECG",
                "Taquicardia sinusal, sem arritmia ou alterações importantes relacionadas ao potássio.",
            ),
            _exam(
                "tomografia_abdome",
                "Tomografia de abdome",
                "Sem alterações agudas; a dor abdominal é explicada pela acidose e deve ser reavaliada após correção metabólica.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        64,
        "Gravidez ectópica tubária não rota",
        "Ginecologia",
        (
            "RFS, 29 anos, feminina, com atraso menstrual de sete semanas, apresenta "
            "sangramento vaginal discreto e dor pélvica à direita há dois dias. Teve "
            "doença inflamatória pélvica há três anos. Nega síncope, dor no ombro ou "
            "sangramento volumoso."
        ),
        (
            "REG, consciente e corada. PA: 104/68 mmHg; FC: 96 bpm; FR: 18 irpm; "
            "SpO2: 99%; Temperatura: 36,7 °C. Abdome doloroso em fossa ilíaca direita, "
            "sem defesa; colo fechado, pequeno sangramento e dor anexial direita."
        ),
        [
            _exam(
                "beta_hcg_quantitativo",
                "Beta-hCG quantitativo",
                "3.240 mUI/mL; valor acima do qual se espera visualizar gestação intrauterina com ultrassonografia transvaginal, conforme contexto e equipamento.",
            ),
            _exam(
                "ultrassom_transvaginal",
                "Ultrassonografia transvaginal",
                "Cavidade uterina vazia e massa anexial direita de 2,2 cm, sem atividade cardíaca; pequena quantidade de líquido livre pélvico.",
            ),
            _exam(
                "hemograma",
                "Hemograma",
                "Hb 11,8 g/dL; hematócrito 35%; leucócitos 8.900/mm³; plaquetas 256.000/mm³.",
            ),
            _exam(
                "tipagem_rh",
                "Tipagem sanguínea e fator Rh",
                "Grupo A, Rh negativo; pesquisa de anticorpos irregulares negativa.",
            ),
            _exam(
                "funcao_renal_hepatica",
                "Função renal e hepática",
                "Creatinina 0,8 mg/dL; AST 24 U/L; ALT 21 U/L, sem contraindicação laboratorial evidente ao metotrexato.",
            ),
            _exam(
                "tomografia_pelve",
                "Tomografia de pelve",
                "Massa anexial direita; exame usa radiação e não acrescenta informação útil ao ultrassom neste cenário.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        65,
        "Crise aguda de fechamento angular",
        "Oftalmologia",
        (
            "MDS, 62 anos, feminina e hipermétrope, apresenta dor súbita intensa no "
            "olho direito há seis horas, visão embaçada com halos coloridos, cefaleia, "
            "náuseas e um episódio de vômito. Os sintomas começaram após permanecer em "
            "ambiente escuro. Nega trauma ocular."
        ),
        (
            "REG, ansiosa e orientada. PA: 148/88 mmHg; FC: 104 bpm; FR: 20 irpm; "
            "SpO2: 98%; Temperatura: 36,5 °C. Olho direito vermelho, córnea opaca, "
            "câmara anterior rasa e pupila em meia midríase pouco reagente."
        ),
        [
            _exam(
                "tonometria",
                "Tonometria",
                "Pressão intraocular de 52 mmHg no olho direito e 17 mmHg no esquerdo.",
            ),
            _exam(
                "acuidade_pupilas",
                "Acuidade visual e exame pupilar",
                "Acuidade 20/200 à direita e 20/25 à esquerda; pupila direita em meia midríase, pouco reagente.",
            ),
            _exam(
                "biomicroscopia",
                "Biomicroscopia em lâmpada de fenda",
                "Edema de córnea, hiperemia ciliar e câmara anterior rasa no olho direito.",
            ),
            _exam(
                "gonioscopia",
                "Gonioscopia",
                "Ângulo fechado no olho direito e estreito no olho contralateral.",
            ),
            _exam(
                "avaliacao_nervo_optico",
                "Avaliação do nervo óptico após clareamento da córnea",
                "Sem escavação avançada evidente; exame inicial limitado pelo edema corneano.",
            ),
            _exam(
                "tomografia_orbitas",
                "Tomografia de órbitas",
                "Sem massa ou fratura; exame não avalia adequadamente o ângulo e atrasaria o tratamento ocular.",
                appropriate=False,
            ),
        ],
    ),
]


EXPANSION_BATCH_TWO_RUBRICS: dict[int, dict[str, Any]] = {
    61: {
        "diagnostico_referencia": "Pneumonia adquirida na comunidade.",
        "diagnostico_termos": [
            "pneumonia",
            "pneumonia comunitaria",
            "pneumonia adquirida na comunidade",
            "pneumonia bacteriana",
        ],
        "diagnostico_parcial": ["infeccao respiratoria", "infeccao pulmonar"],
        "exames_essenciais": [
            "radiografia_torax",
            "hemograma_pcr",
            "funcao_renal_eletrólitos",
            "gasometria_arterial",
        ],
        "exames_opcionais": ["painel_viral"],
        "exames_desnecessarios": ["tomografia_torax"],
        "justificativa_exames": {
            "radiografia_torax": "Confirma consolidação pulmonar e avalia complicações visíveis.",
            "hemograma_pcr": "Apoia a avaliação da resposta inflamatória e o acompanhamento.",
            "funcao_renal_eletrólitos": "Ajuda a avaliar gravidade e segurança do tratamento.",
            "gasometria_arterial": "Quantifica a hipoxemia sugerida pela saturação de 90%.",
            "painel_viral": "Pode identificar etiologia viral e apoiar isolamento, sem substituir a radiografia.",
            "tomografia_torax": "Não é necessária quando a radiografia é típica e não há suspeita de complicação.",
        },
        "conduta_criterios": [
            _criterion(
                "Oxigênio e monitorização", 8, "oxigenio", "saturacao", "monitorizacao"
            ),
            _criterion(
                "Antibiótico empírico",
                12,
                "antibiotico",
                "antimicrobiano",
                "tratamento empirico",
            ),
            _criterion(
                "Avaliar gravidade e hidratação",
                6,
                "curb",
                "gravidade",
                "internacao",
                "hidratacao",
            ),
            _criterion(
                "Reavaliar resposta", 4, "reavaliar", "retorno", "sinais vitais"
            ),
        ],
        "conduta_referencia": "Oferecer oxigênio pela hipoxemia, iniciar antibiótico empírico conforme protocolo local, avaliar necessidade de internação e hidratação e reavaliar sinais vitais e resposta clínica.",
        "feedback_hipotese_parcial": "Você reconheceu uma infecção respiratória; a consolidação focal confirma pneumonia.",
        "feedback_hipotese_incorreta": "Febre, tosse produtiva, estertores e consolidação focal são compatíveis com pneumonia comunitária.",
        "feedback_seguranca": "A saturação de 90% exige correção da hipoxemia e avaliação presencial; tomografia não deve atrasar o tratamento.",
        "objetivos_aprendizagem": [
            "Reconhecer pneumonia comunitária",
            "Interpretar radiografia e oxigenação",
            "Definir tratamento e local de cuidado",
        ],
        "criterios_seguranca": [
            _safety(
                "Tratar hipoxemia",
                "Não corrigir a hipoxemia aumenta o risco de deterioração.",
                "oxigenio",
                "saturacao",
            ),
            _safety(
                "Antibiótico oportuno",
                "O antibiótico não deve ser atrasado por tomografia sem indicação.",
                "antibiotico",
                "antimicrobiano",
            ),
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "A febre e a falta de ar começam a melhorar após suporte e antibiótico.",
                "desfecho": "O paciente permanece estável e segue com acompanhamento da resposta clínica.",
                "reavaliacao": [
                    _vital("SpO2", "90%", "95% com oxigênio", "melhora"),
                    _vital("Frequência respiratória", "26 irpm", "20 irpm", "melhora"),
                    _vital("Frequência cardíaca", "108 bpm", "92 bpm", "melhora"),
                    _vital("Temperatura", "38,7 °C", "37,8 °C", "melhora"),
                ],
            },
            "parcial": {
                "reacao": "Há melhora discreta, mas a hipoxemia ou o tratamento permanecem incompletos.",
                "desfecho": "O paciente necessita revisão do plano e vigilância mais próxima.",
                "reavaliacao": [
                    _vital("SpO2", "90%", "92%", "estavel"),
                    _vital("Frequência respiratória", "26 irpm", "24 irpm", "estavel"),
                    _vital("Frequência cardíaca", "108 bpm", "104 bpm", "estavel"),
                    _vital("Temperatura", "38,7 °C", "38,3 °C", "estavel"),
                ],
            },
            "insegura": {
                "reacao": "Sem suporte e antibiótico, a dispneia e a hipoxemia pioram.",
                "desfecho": "O quadro evolui para insuficiência respiratória e sepse.",
                "reavaliacao": [
                    _vital("SpO2", "90%", "84%", "piora"),
                    _vital("Frequência respiratória", "26 irpm", "34 irpm", "piora"),
                    _vital("Pressão arterial", "112/70 mmHg", "88/54 mmHg", "piora"),
                    _vital("Consciência", "lúcido", "confuso", "piora"),
                ],
            },
        },
        "reacao_paciente_referencia": "A resposta deve ser acompanhada por sintomas, oxigenação, frequência respiratória e temperatura.",
        "desfecho_referencia": "O tratamento oportuno reduz progressão para insuficiência respiratória e sepse.",
        "temas_estudo": [
            "Pneumonia comunitária",
            "Avaliação de gravidade",
            "Antibioticoterapia empírica",
        ],
        "fontes_clinicas": [CAP_SOURCE],
    },
    62: {
        "diagnostico_referencia": "Colecistite aguda calculosa.",
        "diagnostico_termos": [
            "colecistite",
            "colecistite aguda",
            "colecistite calculosa",
            "colecistite aguda calculosa",
        ],
        "diagnostico_parcial": ["colica biliar", "inflamacao da vesicula"],
        "exames_essenciais": [
            "ultrassom_abdome",
            "hemograma_pcr",
            "provas_hepaticas",
            "lipase",
        ],
        "exames_opcionais": ["beta_hcg"],
        "exames_desnecessarios": ["tomografia_abdome"],
        "justificativa_exames": {
            "ultrassom_abdome": "É o exame inicial para cálculos, inflamação da vesícula e dilatação biliar.",
            "hemograma_pcr": "Demonstra inflamação sistêmica e ajuda na avaliação de gravidade.",
            "provas_hepaticas": "Pesquisa obstrução do colédoco e orienta exames adicionais.",
            "lipase": "Ajuda a excluir pancreatite biliar.",
            "beta_hcg": "É adequado antes de medicações, exames e cirurgia em pessoa com potencial reprodutivo.",
            "tomografia_abdome": "É dispensável quando o ultrassom é típico e não há suspeita de complicação.",
        },
        "conduta_criterios": [
            _criterion(
                "Jejum, hidratação e analgesia",
                8,
                "jejum",
                "hidratacao",
                "analgesia",
                "antiemetico",
            ),
            _criterion(
                "Antibiótico quando indicado", 6, "antibiotico", "antimicrobiano"
            ),
            _criterion(
                "Avaliação cirúrgica", 10, "cirurgia", "cirurgiao", "colecistectomia"
            ),
            _criterion(
                "Colecistectomia precoce",
                6,
                "colecistectomia precoce",
                "laparoscopia precoce",
                "mesma internacao",
            ),
        ],
        "conduta_referencia": "Manter jejum, hidratar, controlar dor e náusea, iniciar antibiótico conforme gravidade e protocolo local e solicitar avaliação cirúrgica para colecistectomia laparoscópica precoce.",
        "feedback_hipotese_parcial": "Cólica biliar costuma ser mais curta e sem inflamação; febre, Murphy positivo e alterações no ultrassom indicam colecistite.",
        "feedback_hipotese_incorreta": "Dor persistente no hipocôndrio direito, febre, Murphy positivo e vesícula inflamada com cálculo confirmam colecistite aguda.",
        "feedback_seguranca": "Atrasar avaliação cirúrgica pode favorecer necrose, perfuração e sepse.",
        "objetivos_aprendizagem": [
            "Diferenciar cólica biliar de colecistite",
            "Interpretar ultrassom e provas hepáticas",
            "Planejar tratamento inicial e cirurgia",
        ],
        "criterios_seguranca": [
            _safety(
                "Avaliação cirúrgica",
                "Colecistite confirmada requer avaliação cirúrgica durante a internação.",
                "cirurgia",
                "colecistectomia",
            ),
            _safety(
                "Suporte inicial",
                "Jejum, hidratação e analgesia reduzem sintomas e risco perioperatório.",
                "jejum",
                "hidratacao",
                "analgesia",
            ),
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "A dor, a febre e a taquicardia reduzem com suporte e tratamento definitivo organizado.",
                "desfecho": "A paciente segue para colecistectomia precoce sem sinais de complicação.",
                "reavaliacao": [
                    _vital("Dor", "8/10", "3/10", "melhora"),
                    _vital("Frequência cardíaca", "102 bpm", "88 bpm", "melhora"),
                    _vital("Temperatura", "38,1 °C", "37,4 °C", "melhora"),
                    _vital(
                        "Hidratação", "leve desidratação", "mucosas úmidas", "melhora"
                    ),
                ],
            },
            "parcial": {
                "reacao": "A dor melhora, mas a inflamação persiste sem definição cirúrgica.",
                "desfecho": "A internação se prolonga e o risco de recorrência ou complicação permanece.",
                "reavaliacao": [
                    _vital("Dor", "8/10", "5/10", "melhora"),
                    _vital("Frequência cardíaca", "102 bpm", "98 bpm", "estavel"),
                    _vital("Temperatura", "38,1 °C", "37,9 °C", "estavel"),
                    _vital("Murphy", "positivo", "permanece positivo", "estavel"),
                ],
            },
            "insegura": {
                "reacao": "Sem tratamento, aumentam dor, febre e sinais de irritação peritoneal.",
                "desfecho": "A paciente pode evoluir para gangrena, perfuração e sepse.",
                "reavaliacao": [
                    _vital("Dor", "8/10", "10/10", "piora"),
                    _vital("Frequência cardíaca", "102 bpm", "126 bpm", "piora"),
                    _vital("Pressão arterial", "118/74 mmHg", "90/56 mmHg", "piora"),
                    _vital("Temperatura", "38,1 °C", "39,2 °C", "piora"),
                ],
            },
        },
        "reacao_paciente_referencia": "Dor, febre e sinais inflamatórios devem melhorar com suporte e controle da fonte.",
        "desfecho_referencia": "Colecistectomia precoce trata a causa e reduz recorrência e complicações.",
        "temas_estudo": [
            "Colecistite aguda",
            "Ultrassonografia biliar",
            "Colecistectomia precoce",
        ],
        "fontes_clinicas": [CHOLECYSTITIS_SOURCE],
    },
    63: {
        "diagnostico_referencia": "Cetoacidose diabética.",
        "diagnostico_termos": [
            "cetoacidose",
            "cetoacidose diabetica",
            "cad",
            "crise de cetoacidose diabetica",
        ],
        "diagnostico_parcial": [
            "descompensacao diabetica",
            "hiperglicemia",
            "crise hiperglicemica",
        ],
        "exames_essenciais": [
            "glicemia_cetonemia",
            "gasometria_eletrólitos",
            "funcao_renal",
            "urina_tipo_1",
        ],
        "exames_opcionais": ["ecg"],
        "exames_desnecessarios": ["tomografia_abdome"],
        "justificativa_exames": {
            "glicemia_cetonemia": "Confirma hiperglicemia e cetose significativa.",
            "gasometria_eletrólitos": "Demonstra acidose, ânion gap e potássio, essenciais ao tratamento.",
            "funcao_renal": "Avalia desidratação e repercussão renal.",
            "urina_tipo_1": "Ajuda na pesquisa de cetose e possível gatilho urinário.",
            "ecg": "É útil para avaliar repercussões do potássio e ritmo, sem atrasar hidratação.",
            "tomografia_abdome": "A dor é comum na acidose e deve ser reavaliada após correção antes de imagem sem indicação focal.",
        },
        "conduta_criterios": [
            _criterion(
                "Reposição de volume",
                8,
                "cristaloide",
                "soro",
                "hidratacao venosa",
                "reposicao volêmica",
            ),
            _criterion(
                "Insulina após avaliar potássio",
                10,
                "insulina intravenosa",
                "insulina regular",
                "avaliar potassio",
            ),
            _criterion(
                "Monitorar e repor potássio",
                8,
                "potassio",
                "repor potassio",
                "monitorar eletrólitos",
            ),
            _criterion(
                "Tratar fator desencadeante",
                4,
                "causa",
                "gatilho",
                "infeccao",
                "retomar insulina",
            ),
        ],
        "conduta_referencia": "Iniciar cristaloide, verificar e acompanhar potássio, administrar insulina IV quando seguro, acrescentar glicose conforme a glicemia cair e manter tratamento até resolução da cetose e acidose; investigar e corrigir o gatilho.",
        "feedback_hipotese_parcial": "Hiperglicemia isolada não explica a respiração profunda; cetonas elevadas e acidose com ânion gap confirmam cetoacidose.",
        "feedback_hipotese_incorreta": "Hiperglicemia, cetonemia e acidose metabólica com ânion gap definem cetoacidose diabética.",
        "feedback_seguranca": "Insulina sem conhecer e acompanhar o potássio pode causar hipocalemia grave; o tratamento não termina apenas quando a glicose normaliza.",
        "objetivos_aprendizagem": [
            "Diagnosticar cetoacidose",
            "Interpretar pH, cetonas, ânion gap e potássio",
            "Sequenciar fluidos, insulina e eletrólitos",
        ],
        "criterios_seguranca": [
            _safety(
                "Avaliar potássio antes da insulina",
                "Potássio muito baixo exige reposição antes da insulina.",
                "potassio",
                "avaliar potassio",
            ),
            _safety(
                "Reposição volêmica inicial",
                "A desidratação importante exige cristaloide e reavaliação frequente.",
                "cristaloide",
                "hidratacao venosa",
                "soro",
            ),
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "A perfusão e a respiração melhoram enquanto a cetose e o ânion gap diminuem.",
                "desfecho": "A crise resolve com transição segura para insulina subcutânea e orientação sobre dias de doença.",
                "reavaliacao": [
                    _vital("Pressão arterial", "96/62 mmHg", "112/72 mmHg", "melhora"),
                    _vital("Frequência cardíaca", "118 bpm", "92 bpm", "melhora"),
                    _vital("Frequência respiratória", "30 irpm", "20 irpm", "melhora"),
                    _vital("Bicarbonato", "11 mEq/L", "19 mEq/L", "melhora"),
                    _vital("Ânion gap", "22 mEq/L", "11 mEq/L", "melhora"),
                ],
            },
            "parcial": {
                "reacao": "A glicemia cai, mas a acidose persiste por reposição ou monitorização incompletas.",
                "desfecho": "A paciente continua necessitando tratamento da cetose e correção de eletrólitos.",
                "reavaliacao": [
                    _vital("Pressão arterial", "96/62 mmHg", "102/66 mmHg", "melhora"),
                    _vital("Frequência cardíaca", "118 bpm", "108 bpm", "estavel"),
                    _vital("Frequência respiratória", "30 irpm", "26 irpm", "estavel"),
                    _vital("Bicarbonato", "11 mEq/L", "13 mEq/L", "estavel"),
                    _vital("Ânion gap", "22 mEq/L", "19 mEq/L", "estavel"),
                ],
            },
            "insegura": {
                "reacao": "Sem hidratação ou controle do potássio, pioram desidratação, acidose e risco de arritmia.",
                "desfecho": "A paciente evolui para choque, alteração de consciência e distúrbio eletrolítico grave.",
                "reavaliacao": [
                    _vital("Pressão arterial", "96/62 mmHg", "78/46 mmHg", "piora"),
                    _vital("Frequência cardíaca", "118 bpm", "136 bpm", "piora"),
                    _vital("Consciência", "sonolenta", "torporosa", "piora"),
                    _vital("pH", "7,19", "7,05", "piora"),
                    _vital(
                        "Potássio",
                        "5,2 mEq/L",
                        "2,8 mEq/L após insulina sem reposição",
                        "piora",
                    ),
                ],
            },
        },
        "reacao_paciente_referencia": "A melhora clínica deve acompanhar a resolução da cetose e da acidose, não apenas a queda da glicose.",
        "desfecho_referencia": "A alta exige transição de insulina, causa precipitante tratada e educação para prevenir recorrência.",
        "temas_estudo": [
            "Cetoacidose diabética",
            "Potássio na crise hiperglicêmica",
            "Resolução da cetose",
        ],
        "fontes_clinicas": [DKA_SOURCE],
    },
    64: {
        "diagnostico_referencia": "Gravidez ectópica tubária não rota.",
        "diagnostico_termos": [
            "gravidez ectopica",
            "gestacao ectopica",
            "gravidez tubaria",
            "gestacao tubaria",
        ],
        "diagnostico_parcial": ["gestacao de localizacao desconhecida", "abortamento"],
        "exames_essenciais": [
            "beta_hcg_quantitativo",
            "ultrassom_transvaginal",
            "hemograma",
            "tipagem_rh",
        ],
        "exames_opcionais": ["funcao_renal_hepatica"],
        "exames_desnecessarios": ["tomografia_pelve"],
        "justificativa_exames": {
            "beta_hcg_quantitativo": "Deve ser interpretado em conjunto com ultrassonografia e evolução clínica.",
            "ultrassom_transvaginal": "Localiza a gestação e procura massa anexial e líquido livre.",
            "hemograma": "Avalia anemia e fornece parâmetro caso o sangramento aumente.",
            "tipagem_rh": "Identifica necessidade de imunoglobulina anti-D conforme protocolo.",
            "funcao_renal_hepatica": "É útil para avaliar elegibilidade e segurança do metotrexato.",
            "tomografia_pelve": "Não é indicada quando ultrassom e beta-hCG definem o cenário, além de usar radiação.",
        },
        "conduta_criterios": [
            _criterion(
                "Avaliar estabilidade e ruptura",
                8,
                "estabilidade",
                "sangramento",
                "ruptura",
                "sinais vitais",
            ),
            _criterion(
                "Acionar ginecologia",
                7,
                "ginecologia",
                "obstetricia",
                "avaliacao especializada",
            ),
            _criterion(
                "Tratamento adequado ao perfil",
                10,
                "metotrexato",
                "laparoscopia",
                "tratamento cirurgico",
            ),
            _criterion(
                "Rh e seguimento",
                5,
                "anti d",
                "imunoglobulina",
                "beta hcg seriado",
                "seguimento",
            ),
        ],
        "conduta_referencia": "Confirmar estabilidade e ausência de ruptura, solicitar avaliação ginecológica e discutir metotrexato ou cirurgia conforme critérios clínicos, ultrassonográficos e preferência. Administrar anti-D quando indicada e garantir seguimento seriado do beta-hCG.",
        "feedback_hipotese_parcial": "Gestação de localização desconhecida é uma etapa possível, mas a massa anexial com útero vazio sustenta gravidez ectópica.",
        "feedback_hipotese_incorreta": "Atraso menstrual, dor unilateral, sangramento, beta-hCG positivo e massa anexial indicam gravidez ectópica.",
        "feedback_seguranca": "Piora da dor, síncope, hipotensão ou líquido livre crescente sugerem ruptura e exigem cirurgia imediata.",
        "objetivos_aprendizagem": [
            "Reconhecer gravidez ectópica",
            "Integrar beta-hCG e ultrassom",
            "Escolher tratamento e seguimento seguros",
        ],
        "criterios_seguranca": [
            _safety(
                "Vigiar ruptura",
                "Instabilidade ou sinais de hemoperitônio exigem abordagem cirúrgica imediata.",
                "ruptura",
                "instabilidade",
                "sangramento",
            ),
            _safety(
                "Garantir seguimento",
                "Tratamento medicamentoso só é seguro com acompanhamento seriado e acesso a urgência.",
                "beta hcg seriado",
                "seguimento",
                "retorno",
            ),
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "A dor permanece controlada e não surgem sinais de sangramento interno durante o tratamento escolhido.",
                "desfecho": "O beta-hCG reduz progressivamente até resolução, com orientação clara de retorno.",
                "reavaliacao": [
                    _vital("Pressão arterial", "104/68 mmHg", "108/70 mmHg", "estavel"),
                    _vital("Frequência cardíaca", "96 bpm", "88 bpm", "melhora"),
                    _vital("Dor", "6/10", "3/10", "melhora"),
                    _vital("Sangramento", "discreto", "em redução", "melhora"),
                ],
            },
            "parcial": {
                "reacao": "A paciente permanece estável, mas faltam seguimento seriado ou orientação de alarme.",
                "desfecho": "Existe risco de falha terapêutica ser reconhecida tardiamente.",
                "reavaliacao": [
                    _vital("Pressão arterial", "104/68 mmHg", "102/66 mmHg", "estavel"),
                    _vital("Frequência cardíaca", "96 bpm", "98 bpm", "estavel"),
                    _vital("Dor", "6/10", "5/10", "estavel"),
                    _vital("Sangramento", "discreto", "persistente", "estavel"),
                ],
            },
            "insegura": {
                "reacao": "Sem reconhecimento ou seguimento, a dor aumenta e surgem sinais de sangramento interno.",
                "desfecho": "A gestação rompe e a paciente evolui para choque hemorrágico.",
                "reavaliacao": [
                    _vital("Pressão arterial", "104/68 mmHg", "76/42 mmHg", "piora"),
                    _vital("Frequência cardíaca", "96 bpm", "132 bpm", "piora"),
                    _vital("Dor", "6/10", "10/10", "piora"),
                    _vital("Consciência", "consciente", "confusa", "piora"),
                ],
            },
        },
        "reacao_paciente_referencia": "A estabilidade e a queda seriada do beta-hCG orientam a resposta; sinais de ruptura mudam imediatamente a conduta.",
        "desfecho_referencia": "O tratamento é concluído apenas após resolução documentada e orientação reprodutiva.",
        "temas_estudo": [
            "Gravidez ectópica",
            "Beta-hCG e ultrassom",
            "Metotrexato e tratamento cirúrgico",
        ],
        "fontes_clinicas": [ECTOPIC_SOURCE],
    },
    65: {
        "diagnostico_referencia": "Crise aguda de fechamento angular.",
        "diagnostico_termos": [
            "glaucoma agudo",
            "glaucoma de angulo fechado",
            "fechamento angular agudo",
            "crise aguda de fechamento angular",
        ],
        "diagnostico_parcial": [
            "glaucoma",
            "hipertensao ocular",
            "olho vermelho doloroso",
        ],
        "exames_essenciais": [
            "tonometria",
            "acuidade_pupilas",
            "biomicroscopia",
            "gonioscopia",
        ],
        "exames_opcionais": ["avaliacao_nervo_optico"],
        "exames_desnecessarios": ["tomografia_orbitas"],
        "justificativa_exames": {
            "tonometria": "Confirma elevação acentuada da pressão intraocular.",
            "acuidade_pupilas": "Documenta perda visual e alteração pupilar no olho afetado.",
            "biomicroscopia": "Identifica edema corneano e câmara anterior rasa.",
            "gonioscopia": "Confirma fechamento do ângulo e avalia o olho contralateral.",
            "avaliacao_nervo_optico": "É importante após clareamento da córnea, mas pode ser limitada na crise.",
            "tomografia_orbitas": "Não avalia o mecanismo do fechamento angular e atrasaria o tratamento.",
        },
        "conduta_criterios": [
            _criterion(
                "Urgência oftalmológica",
                8,
                "oftalmologia urgente",
                "encaminhamento imediato",
                "emergencia oftalmologica",
            ),
            _criterion(
                "Reduzir pressão intraocular",
                10,
                "acetazolamida",
                "beta bloqueador topico",
                "agonista alfa",
                "manitol",
            ),
            _criterion(
                "Iridotomia definitiva", 8, "iridotomia", "laser", "olho contralateral"
            ),
            _criterion(
                "Evitar dilatação",
                4,
                "evitar dilatacao",
                "nao dilatar",
                "midriatico contraindicado",
            ),
        ],
        "conduta_referencia": "Acionar oftalmologia imediatamente, iniciar medicamentos para reduzir a pressão intraocular conforme contraindicações, controlar dor e náusea e realizar iridotomia periférica a laser assim que possível, avaliando também o olho contralateral. Evitar dilatação pupilar durante a crise.",
        "feedback_hipotese_parcial": "Glaucoma é uma categoria ampla; dor súbita, halos, pupila em meia midríase, câmara rasa e pressão muito alta caracterizam fechamento angular agudo.",
        "feedback_hipotese_incorreta": "Olho vermelho doloroso com perda visual, córnea opaca e pressão intraocular de 52 mmHg indica crise aguda de fechamento angular.",
        "feedback_seguranca": "Atraso do tratamento pode causar perda visual permanente; dilatar a pupila pode agravar o fechamento.",
        "objetivos_aprendizagem": [
            "Reconhecer fechamento angular agudo",
            "Interpretar tonometria e exame anterior",
            "Reduzir pressão e indicar iridotomia",
        ],
        "criterios_seguranca": [
            _safety(
                "Atendimento oftalmológico imediato",
                "Pressão muito elevada ameaça a visão e exige tratamento urgente.",
                "oftalmologia urgente",
                "emergencia oftalmologica",
            ),
            _safety(
                "Evitar dilatação",
                "Midriáticos podem agravar o bloqueio angular durante a crise.",
                "evitar dilatacao",
                "nao dilatar",
            ),
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "A pressão, a dor e a náusea diminuem, permitindo a iridotomia definitiva.",
                "desfecho": "A visão melhora parcialmente e o outro olho recebe prevenção adequada.",
                "reavaliacao": [
                    _vital(
                        "Pressão intraocular direita", "52 mmHg", "20 mmHg", "melhora"
                    ),
                    _vital("Dor ocular", "9/10", "2/10", "melhora"),
                    _vital("Acuidade visual direita", "20/200", "20/60", "melhora"),
                    _vital("Náusea", "presente", "ausente", "melhora"),
                ],
            },
            "parcial": {
                "reacao": "A pressão reduz parcialmente, mas falta tratamento definitivo ou avaliação do outro olho.",
                "desfecho": "Persistem risco de nova crise e dano progressivo do nervo óptico.",
                "reavaliacao": [
                    _vital(
                        "Pressão intraocular direita", "52 mmHg", "34 mmHg", "melhora"
                    ),
                    _vital("Dor ocular", "9/10", "6/10", "melhora"),
                    _vital("Acuidade visual direita", "20/200", "20/160", "estavel"),
                    _vital("Córnea", "opaca", "edema persistente", "estavel"),
                ],
            },
            "insegura": {
                "reacao": "Sem redução da pressão ou após dilatação, pioram dor, edema corneano e visão.",
                "desfecho": "O nervo óptico sofre dano irreversível, com risco de perda visual permanente.",
                "reavaliacao": [
                    _vital(
                        "Pressão intraocular direita", "52 mmHg", "64 mmHg", "piora"
                    ),
                    _vital("Dor ocular", "9/10", "10/10", "piora"),
                    _vital(
                        "Acuidade visual direita",
                        "20/200",
                        "percepção de vultos",
                        "piora",
                    ),
                    _vital("Resposta pupilar", "reduzida", "fixa", "piora"),
                ],
            },
        },
        "reacao_paciente_referencia": "Dor, pressão ocular e visão devem ser reavaliadas até o tratamento definitivo.",
        "desfecho_referencia": "A rapidez da redução da pressão e da iridotomia influencia a preservação visual.",
        "temas_estudo": [
            "Fechamento angular agudo",
            "Hipertensão ocular",
            "Iridotomia periférica",
        ],
        "fontes_clinicas": [ANGLE_CLOSURE_SOURCE],
    },
}
