"""Primeiro lote de expansão: emergências cardiovasculares de maior complexidade."""

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
    history: str,
    physical_exam: str,
    exams: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": case_id,
        "titulo": title,
        "especialidade": "Cardiologia",
        "nivel_dificuldade": "Difícil",
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


ACS_SOURCE = _source(
    "2023 ESC Guidelines for the management of acute coronary syndromes",
    "European Society of Cardiology",
    2023,
    "https://www.escardio.org/guidelines/clinical-practice-guidelines/all-esc-practice-guidelines/acute-coronary-syndromes/",
)
AORTA_SOURCE = _source(
    "2024 ESC Guidelines for the management of peripheral arterial and aortic diseases",
    "European Society of Cardiology",
    2024,
    "https://www.escardio.org/guidelines/clinical-practice-guidelines/all-esc-practice-guidelines/peripheral-arterial-and-aortic-diseases/",
)
SVT_SOURCE = _source(
    "2015 ACC/AHA/HRS Guideline for the Management of Adult Patients With Supraventricular Tachycardia",
    "American Heart Association",
    2015,
    "https://professional.heart.org/en/science-news/-/media/028ddd505f514ea2b3a4e74bb72e3557.ashx",
)
ENDOCARDITIS_SOURCE = _source(
    "2023 ESC Guidelines for the management of endocarditis",
    "European Society of Cardiology",
    2023,
    "https://www.escardio.org/guidelines/clinical-practice-guidelines/all-esc-practice-guidelines/endocarditis/",
)
TAMPONADE_SOURCE = _source(
    "Cardiac tamponade: a clinical challenge",
    "European Society of Cardiology",
    2017,
    "https://www.escardio.org/communities/councils/cardiology-practice/scientific-documents-and-publications/ejournal/volume-15/Cardiac-tamponade-a-clinical-challenge/",
)


EXPANSION_BATCH_ONE_TITLES = {
    56: "Dor no peito com náusea e queda da pressão",
    57: "Dor súbita entre o peito e as costas",
    58: "Palpitações muito rápidas e irregulares",
    59: "Febre persistente com falta de ar",
    60: "Falta de ar, fraqueza e pressão baixa",
}


EXPANSION_BATCH_ONE_CASES = [
    _case(
        56,
        "Infarto inferior com acometimento do ventrículo direito",
        (
            "RMA, 64 anos, masculino, hipertenso e tabagista, apresenta dor retroesternal "
            "em pressão há 70 minutos, irradiada para braço esquerdo, acompanhada de "
            "náusea, sudorese e fraqueza intensa. Nega trauma, febre e uso recente de "
            "sildenafila ou outro inibidor de PDE5."
        ),
        (
            "REG, pálido, sudoreico e orientado. PA: 86/58 mmHg; FC: 48 bpm; "
            "FR: 24 irpm; SpO2: 93%; Temperatura: 36,1 °C. Turgência jugular a 45°, "
            "extremidades frias e pulsos finos. Bulhas rítmicas e hipofonéticas, sem "
            "sopro novo. Pulmões limpos, sem estertores."
        ),
        [
            _exam(
                "ecg_12_derivacoes",
                "ECG de 12 derivações",
                "Supradesnivelamento de ST de 2 mm em DII, DIII e aVF, maior em DIII, com infradesnivelamento recíproco em DI e aVL; bradicardia sinusal a 48 bpm.",
            ),
            _exam(
                "ecg_derivacoes_direitas",
                "ECG com derivações direitas V3R e V4R",
                "Supradesnivelamento de ST de 1,5 mm em V4R, compatível com acometimento do ventrículo direito.",
            ),
            _exam(
                "troponina_serial",
                "Troponina cardíaca ultrassensível seriada",
                "Troponina I inicial 1.850 ng/L (VR: < 34 ng/L), com elevação para 3.420 ng/L em 1 hora.",
            ),
            _exam(
                "eco_beira_leito",
                "Ecocardiograma à beira-leito",
                "Hipocinesia inferoposterior do VE; ventrículo direito dilatado e hipocinético. FEVE 48%. Sem derrame pericárdico ou complicação mecânica evidente.",
            ),
            _exam(
                "eletrólitos_funcao_renal",
                "Eletrólitos e função renal",
                "Sódio 138 mEq/L; potássio 4,3 mEq/L; magnésio 1,9 mg/dL; creatinina 1,1 mg/dL; ureia 37 mg/dL.",
            ),
            _exam(
                "hemograma_coagulacao",
                "Hemograma e coagulograma",
                "Hb 14,2 g/dL; leucócitos 11.800/mm³; plaquetas 238.000/mm³; INR 1,0; TTPa 30 s.",
            ),
            _exam(
                "radiografia_torax",
                "Radiografia de tórax",
                "Área cardíaca normal, pulmões sem congestão e mediastino sem alargamento.",
            ),
            _exam(
                "gasometria_lactato",
                "Gasometria arterial e lactato",
                "pH 7,35; PaCO2 34 mmHg; HCO3 19 mEq/L; lactato 3,1 mmol/L (VR: < 2,0), sugerindo hipoperfusão.",
            ),
            _exam(
                "dimero_d",
                "Dímero-D",
                "860 ng/mL FEU (elevado, porém inespecífico no contexto de infarto agudo).",
                appropriate=False,
            ),
            _exam(
                "angiotomografia_coronarias",
                "Angiotomografia de coronárias",
                "Estenose importante em coronária direita; exame redundante e capaz de atrasar a reperfusão indicada pelo ECG.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        57,
        "Dissecção aguda de aorta Stanford A",
        (
            "MLC, 59 anos, masculino, hipertenso com tratamento irregular, apresenta "
            "dor torácica máxima desde o início há 35 minutos, descrita como rasgando e "
            "irradiando para a região interescapular. Teve síncope breve e agora refere "
            "dormência no braço esquerdo. Nega dor semelhante prévia."
        ),
        (
            "REG, ansioso, sudoreico e orientado. PA: 190/108 mmHg no braço direito; "
            "PA: 146/84 mmHg no braço esquerdo; FC: 112 bpm; FR: 26 irpm; SpO2: 96%; "
            "Temperatura: 36,5 °C. Pulso radial esquerdo reduzido, sopro diastólico novo "
            "em foco aórtico e extremidades perfundidas. Sem déficit motor persistente."
        ),
        [
            _exam(
                "angiotomografia_aorta",
                "Angiotomografia de aorta com contraste",
                "Flap intimal desde a raiz da aorta até o arco, envolvendo a aorta ascendente; falsa luz patente. Dissecção Stanford A, sem ruptura livre.",
            ),
            _exam(
                "eco_beira_leito",
                "Ecocardiograma à beira-leito",
                "Dilatação da raiz da aorta, flap proximal móvel e insuficiência aórtica moderada. Pequeno derrame pericárdico, sem tamponamento.",
            ),
            _exam(
                "ecg_12_derivacoes",
                "ECG de 12 derivações",
                "Taquicardia sinusal, hipertrofia ventricular esquerda e alterações inespecíficas de ST-T, sem padrão de infarto com supra de ST.",
            ),
            _exam(
                "hemograma_coagulacao_reserva",
                "Hemograma, coagulograma e reserva de hemocomponentes",
                "Hb 13,1 g/dL; plaquetas 205.000/mm³; INR 1,0; tipagem O positivo e provas de compatibilidade iniciadas.",
            ),
            _exam(
                "funcao_renal_eletrólitos",
                "Função renal e eletrólitos",
                "Creatinina 1,3 mg/dL; ureia 42 mg/dL; sódio 140 mEq/L; potássio 4,1 mEq/L.",
            ),
            _exam(
                "radiografia_torax",
                "Radiografia de tórax",
                "Mediastino alargado e contorno aórtico proeminente; achado sugestivo, mas não confirmatório.",
            ),
            _exam(
                "troponina",
                "Troponina cardíaca ultrassensível",
                "Troponina I 48 ng/L (VR: < 34 ng/L), discreta elevação que não exclui síndrome aórtica aguda.",
            ),
            _exam(
                "gasometria_lactato",
                "Gasometria arterial e lactato",
                "pH 7,38; HCO3 22 mEq/L; lactato 2,6 mmol/L, indicando estresse circulatório inicial.",
            ),
            _exam(
                "dimero_d",
                "Dímero-D",
                "4.200 ng/mL FEU; resultado inespecífico e desnecessário diante de alta probabilidade clínica com imagem disponível.",
                appropriate=False,
            ),
            _exam(
                "cinecoronariografia",
                "Cinecoronariografia diagnóstica",
                "Sem oclusão coronariana; a realização antes do controle aórtico atrasaria a cirurgia urgente.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        58,
        "Fibrilação atrial pré-excitada com instabilidade hemodinâmica",
        (
            "TGF, 27 anos, masculino, relata palpitações abruptas há 25 minutos, "
            "associadas a dor torácica, dispneia, tontura intensa e sensação de desmaio. "
            "Já teve episódios breves autolimitados e um ECG antigo descrito como tendo "
            "intervalo PR curto. Nega uso de drogas estimulantes."
        ),
        (
            "REG, confuso, diaforético e com perfusão periférica lenta. PA: 82/54 mmHg; "
            "FC: 228 bpm, irregular; FR: 28 irpm; SpO2: 92%; Temperatura: 36,4 °C. "
            "Pulsos rápidos e irregulares, enchimento capilar de 4 segundos e pulmões limpos."
        ),
        [
            _exam(
                "ecg_12_derivacoes",
                "ECG de 12 derivações",
                "Taquicardia irregular de complexos largos, 190–260 bpm, com morfologia variável e intervalos RR muito curtos; padrão compatível com fibrilação atrial pré-excitada.",
            ),
            _exam(
                "monitorizacao_continua",
                "Monitorização cardíaca contínua",
                "Ritmo irregular de alta resposta ventricular, com períodos de RR pré-excitado próximos de 220 ms e sem pausa sustentada.",
            ),
            _exam(
                "eletrólitos_magnesio",
                "Eletrólitos, cálcio e magnésio",
                "Potássio 3,7 mEq/L; magnésio 1,8 mg/dL; cálcio ionizado 1,17 mmol/L; sem distúrbio grave precipitante.",
            ),
            _exam(
                "glicemia_capilar",
                "Glicemia capilar",
                "112 mg/dL, sem hipoglicemia como causa da alteração do estado mental.",
            ),
            _exam(
                "gasometria_lactato",
                "Gasometria venosa e lactato",
                "pH 7,31; HCO3 19 mEq/L; lactato 4,0 mmol/L, compatível com hipoperfusão pela taquiarritmia.",
            ),
            _exam(
                "troponina_serial",
                "Troponina cardíaca ultrassensível seriada",
                "Troponina I 62 ng/L e 88 ng/L (VR: < 34 ng/L), pequena variação compatível com lesão por demanda.",
            ),
            _exam(
                "ecocardiograma_pos_estabilizacao",
                "Ecocardiograma após estabilização",
                "Câmaras de dimensões normais, FEVE 58% e ausência de cardiopatia estrutural relevante.",
            ),
            _exam(
                "tsh_t4_livre",
                "TSH e T4 livre",
                "TSH 1,7 mUI/L e T4 livre 1,1 ng/dL, dentro da referência.",
            ),
            _exam(
                "holter_24h",
                "Holter de 24 horas durante a instabilidade",
                "Registro posterior sem nova arritmia; não substitui o ECG nem deve atrasar a cardioversão.",
                appropriate=False,
            ),
            _exam(
                "angiotomografia_pulmonar",
                "Angiotomografia de artérias pulmonares",
                "Sem tromboembolismo pulmonar; exame sem prioridade diante da arritmia documentada e instabilidade.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        59,
        "Endocardite infecciosa de valva aórtica com insuficiência cardíaca aguda",
        (
            "JAR, 47 anos, masculino, com valva aórtica bicúspide conhecida, relata "
            "febre diária, calafrios, inapetência e perda de 4 kg há três semanas. "
            "Há cinco dias iniciou dispneia progressiva, ortopneia e edema nas pernas. "
            "Tratou abscesso cutâneo no antebraço há um mês."
        ),
        (
            "REG, dispneico, orientado e com extremidades mornas. PA: 102/58 mmHg; "
            "FC: 118 bpm; FR: 30 irpm; SpO2: 89%; Temperatura: 39,1 °C. Petéquias "
            "em conjuntivas, sopro diastólico novo em foco aórtico, terceira bulha, "
            "estertores até campos médios e edema de membros inferiores 2+/4+."
        ),
        [
            _exam(
                "hemoculturas_tres_pares",
                "Três pares de hemoculturas antes do antibiótico",
                "Staphylococcus aureus sensível à meticilina em todos os frascos, com tempo de positividade inferior a 12 horas.",
            ),
            _exam(
                "ecocardiograma_transtoracico",
                "Ecocardiograma transtorácico",
                "Vegetação móvel de 14 mm na valva aórtica bicúspide, insuficiência aórtica importante e FEVE 52%.",
            ),
            _exam(
                "ecocardiograma_transesofagico",
                "Ecocardiograma transesofágico",
                "Vegetação de 15 × 7 mm, perfuração de cúspide e regurgitação aórtica grave; sem abscesso perivalvar definido.",
            ),
            _exam(
                "hemograma_inflamatorios",
                "Hemograma e marcadores inflamatórios",
                "Hb 9,8 g/dL; leucócitos 17.600/mm³ com neutrofilia; plaquetas 132.000/mm³; PCR 186 mg/L; VHS 72 mm/h.",
            ),
            _exam(
                "funcao_renal_hepatica_urina",
                "Função renal, hepática e urina tipo 1",
                "Creatinina 1,8 mg/dL; ureia 68 mg/dL; AST 62 U/L; ALT 55 U/L; hematúria microscópica e proteinúria leve.",
            ),
            _exam(
                "ecg_12_derivacoes",
                "ECG de 12 derivações",
                "Taquicardia sinusal a 116 bpm, PR 210 ms e sem sinais de isquemia aguda; prolongamento do PR exige vigilância para extensão perivalvar.",
            ),
            _exam(
                "radiografia_torax",
                "Radiografia de tórax",
                "Congestão pulmonar bilateral e pequenos derrames pleurais, sem consolidação focal.",
            ),
            _exam(
                "gasometria_lactato",
                "Gasometria arterial e lactato",
                "pH 7,44; PaO2 58 mmHg em ar ambiente; PaCO2 31 mmHg; lactato 2,4 mmol/L.",
            ),
            _exam(
                "procalcitonina",
                "Procalcitonina",
                "6,8 ng/mL; reforça infecção bacteriana sistêmica, mas não confirma isoladamente endocardite.",
            ),
            _exam(
                "pet_ct",
                "PET-CT cardíaco",
                "Captação valvar inespecífica; exame não prioritário em valva nativa com ecocardiografia e hemoculturas diagnósticas.",
                appropriate=False,
            ),
        ],
    ),
    _case(
        60,
        "Tamponamento cardíaco por derrame pericárdico neoplásico",
        (
            "MFS, 58 anos, feminina, em tratamento de câncer de mama metastático, "
            "apresenta dispneia progressiva há sete dias, pior ao deitar, associada a "
            "fraqueza e dois episódios de pré-síncope. Nega febre, dor pleurítica ou "
            "sangramento. A última quimioterapia foi há três semanas."
        ),
        (
            "MEG, ansiosa, orientada, fria e com fala entrecortada. PA: 78/52 mmHg; "
            "FC: 128 bpm; FR: 30 irpm; SpO2: 91%; Temperatura: 36,4 °C. Turgência "
            "jugular, bulhas hipofonéticas, pulsos paradoxais de 18 mmHg, enchimento "
            "capilar de 5 segundos e pulmões sem estertores."
        ),
        [
            _exam(
                "ecocardiograma_beira_leito",
                "Ecocardiograma à beira-leito",
                "Derrame pericárdico circunferencial volumoso, colapso diastólico de átrio e ventrículo direitos, variação respiratória acentuada dos fluxos e veia cava inferior pletórica.",
            ),
            _exam(
                "ecg_12_derivacoes",
                "ECG de 12 derivações",
                "Taquicardia sinusal, baixa voltagem difusa e alternância elétrica.",
            ),
            _exam(
                "ultrassom_pulmonar",
                "Ultrassonografia pulmonar à beira-leito",
                "Predomínio de linhas A, deslizamento pleural presente e ausência de congestão pulmonar difusa.",
            ),
            _exam(
                "hemograma_coagulacao",
                "Hemograma e coagulograma",
                "Hb 10,4 g/dL; leucócitos 7.800/mm³; plaquetas 96.000/mm³; INR 1,2; TTPa 34 s.",
            ),
            _exam(
                "funcao_renal_eletrólitos",
                "Função renal e eletrólitos",
                "Creatinina 1,5 mg/dL; ureia 61 mg/dL; sódio 134 mEq/L; potássio 4,5 mEq/L.",
            ),
            _exam(
                "gasometria_lactato",
                "Gasometria arterial e lactato",
                "pH 7,32; PaO2 62 mmHg; HCO3 19 mEq/L; lactato 4,7 mmol/L, compatível com choque obstrutivo.",
            ),
            _exam(
                "radiografia_torax",
                "Radiografia de tórax",
                "Silhueta cardíaca aumentada, sem edema pulmonar; achado não define repercussão hemodinâmica.",
            ),
            _exam(
                "analise_liquido_pericardico",
                "Citologia e análise do líquido pericárdico após drenagem",
                "Líquido hemorrágico com células malignas compatíveis com adenocarcinoma mamário; culturas sem crescimento.",
            ),
            _exam(
                "tomografia_torax",
                "Tomografia de tórax antes da drenagem",
                "Derrame pericárdico volumoso e doença metastática; o transporte atrasaria o alívio do tamponamento instável.",
                appropriate=False,
            ),
            _exam(
                "peptideos_natriureticos",
                "BNP e NT-proBNP",
                "BNP 118 pg/mL; resultado não explica o choque e não altera a necessidade de drenagem imediata.",
                appropriate=False,
            ),
        ],
    ),
]


EXPANSION_BATCH_ONE_RUBRICS: dict[int, dict[str, Any]] = {
    56: {
        "diagnostico_referencia": "Infarto agudo do miocárdio com supradesnivelamento de ST inferior e acometimento do ventrículo direito, complicado por hipotensão e bradicardia.",
        "diagnostico_termos": [
            "infarto inferior com ventrículo direito",
            "iam inferior com acometimento de vd",
            "stemi inferior com infarto de vd",
            "infarto de parede inferior e ventrículo direito",
        ],
        "diagnostico_parcial": [
            "infarto agudo do miocardio",
            "stemi inferior",
            "sindrome coronariana aguda",
        ],
        "exames_essenciais": [
            "ecg_12_derivacoes",
            "ecg_derivacoes_direitas",
            "troponina_serial",
            "eco_beira_leito",
            "eletrólitos_funcao_renal",
            "hemograma_coagulacao",
            "gasometria_lactato",
        ],
        "exames_opcionais": ["radiografia_torax"],
        "exames_desnecessarios": ["dimero_d", "angiotomografia_coronarias"],
        "justificativa_exames": {
            "ecg_12_derivacoes": "Confirma o infarto inferior e identifica bradicardia associada sem aguardar biomarcadores.",
            "ecg_derivacoes_direitas": "O supra em V4R confirma acometimento do ventrículo direito e muda o manejo da pré-carga.",
            "troponina_serial": "Documenta necrose miocárdica, mas não deve atrasar a reperfusão indicada pelo ECG.",
            "eco_beira_leito": "Avalia ventrículo direito, função ventricular e complicações mecânicas sem retardar a angioplastia.",
            "eletrólitos_funcao_renal": "Orienta correção de fatores arrítmicos e segurança do contraste e dos medicamentos.",
            "hemograma_coagulacao": "Estabelece parâmetros basais para terapia antitrombótica e procedimento invasivo.",
            "gasometria_lactato": "Quantifica hipoperfusão diante de hipotensão e extremidades frias.",
            "radiografia_torax": "Ajuda em diagnósticos alternativos, mas é opcional e não deve atrasar a reperfusão.",
            "dimero_d": "É inespecífico neste contexto e não acrescenta valor diante do ECG diagnóstico.",
            "angiotomografia_coronarias": "Não é necessária no infarto com supra e atrasaria a estratégia invasiva de reperfusão.",
        },
        "conduta_criterios": [
            _criterion(
                "Estabilização e monitorização",
                7,
                "abc",
                "monitorizacao",
                "acesso venoso",
                "desfibrilador",
                "oxigenio se hipoxemia",
            ),
            _criterion(
                "Reperfusão coronariana imediata",
                10,
                "angioplastia primaria",
                "cateterismo urgente",
                "reperfusao",
                "hemodinamica",
            ),
            _criterion(
                "Terapia antitrombótica",
                6,
                "aspirina",
                "antiagregacao",
                "p2y12",
                "anticoagulacao",
            ),
            _criterion(
                "Suporte do ventrículo direito e bradicardia",
                7,
                "cristaloide cauteloso",
                "volume cauteloso",
                "evitar nitrato",
                "atropina",
                "marcapasso",
            ),
        ],
        "conduta_referencia": "Monitorizar e obter acessos, oferecer oxigênio apenas se necessário, iniciar terapia antitrombótica conforme protocolo e acionar imediatamente a angioplastia primária. Na hipotensão por infarto de VD, fazer reposição volêmica cautelosa e reavaliada, evitar nitratos e diuréticos e tratar bradicardia sintomática sem atrasar a reperfusão.",
        "feedback_hipotese_parcial": "Você reconheceu o infarto inferior, mas a hipotensão com jugulares ingurgitadas, pulmões limpos e supra em V4R exige identificar o acometimento do ventrículo direito.",
        "feedback_hipotese_incorreta": "O supra inferior com alteração recíproca e V4R positivo caracteriza infarto inferior com envolvimento do ventrículo direito.",
        "feedback_seguranca": "Nitratos ou diuréticos podem agravar a hipotensão dependente de pré-carga; nenhum exame deve atrasar a reperfusão.",
        "objetivos_aprendizagem": [
            "Reconhecer infarto inferior e de ventrículo direito",
            "Relacionar o diagnóstico ao manejo da pré-carga",
            "Priorizar reperfusão e antitrombóticos",
        ],
        "criterios_seguranca": [
            _safety(
                "Reperfusão sem atraso",
                "Aguardar troponina ou tomografia diante de um ECG diagnóstico prolonga isquemia miocárdica.",
                "angioplastia",
                "cateterismo",
                "reperfusao",
            ),
            _safety(
                "Evitar redução inadequada da pré-carga",
                "Nitrato e diurético podem precipitar colapso circulatório no infarto de VD hipotenso.",
                "evitar nitrato",
                "nao administrar nitrato",
                "volume cauteloso",
            ),
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Com suporte cauteloso da pré-carga e reperfusão, a dor e a hipoperfusão diminuem.",
                "desfecho": "A coronária direita é reperfundida e o paciente segue monitorizado para recuperação do VD e vigilância de bloqueios.",
                "reavaliacao": [
                    _vital("Pressão arterial", "86/58 mmHg", "104/68 mmHg", "melhora"),
                    _vital("Frequência cardíaca", "48 bpm", "62 bpm", "melhora"),
                    _vital("SpO2", "93%", "96%", "melhora"),
                    _vital("Lactato", "3,1 mmol/L", "1,8 mmol/L", "melhora"),
                ],
            },
            "parcial": {
                "reacao": "A dor persiste e a perfusão melhora pouco enquanto a reperfusão ou o suporte do VD ficam incompletos.",
                "desfecho": "Há maior risco de choque e bloqueio atrioventricular até a correção das omissões.",
                "reavaliacao": [
                    _vital("Pressão arterial", "86/58 mmHg", "90/60 mmHg", "estavel"),
                    _vital("Frequência cardíaca", "48 bpm", "50 bpm", "estavel"),
                    _vital("SpO2", "93%", "94%", "estavel"),
                    _vital("Lactato", "3,1 mmol/L", "3,3 mmol/L", "piora"),
                ],
            },
            "insegura": {
                "reacao": "Atraso da reperfusão ou redução da pré-carga agrava a hipotensão e a bradicardia.",
                "desfecho": "O paciente evolui para choque cardiogênico e instabilidade elétrica.",
                "reavaliacao": [
                    _vital("Pressão arterial", "86/58 mmHg", "68/42 mmHg", "piora"),
                    _vital("Frequência cardíaca", "48 bpm", "38 bpm", "piora"),
                    _vital("SpO2", "93%", "88%", "piora"),
                    _vital("Lactato", "3,1 mmol/L", "5,6 mmol/L", "piora"),
                ],
            },
        },
        "reacao_paciente_referencia": "A resposta depende de reperfusão rápida, manutenção prudente da pré-carga e controle da bradicardia.",
        "desfecho_referencia": "O prognóstico é determinado pelo tempo até reperfusão e pela prevenção de choque e bloqueio avançado.",
        "temas_estudo": [
            "Infarto inferior",
            "Infarto de ventrículo direito",
            "Reperfusão no STEMI",
        ],
        "fontes_clinicas": [ACS_SOURCE],
    },
    57: {
        "diagnostico_referencia": "Dissecção aguda de aorta Stanford A com insuficiência aórtica e ameaça de complicações malperfusionais.",
        "diagnostico_termos": [
            "disseccao aortica stanford a",
            "disseccao aguda de aorta tipo a",
            "sindrome aortica aguda tipo a",
        ],
        "diagnostico_parcial": [
            "disseccao de aorta",
            "sindrome aortica aguda",
            "aneurisma de aorta",
        ],
        "exames_essenciais": [
            "angiotomografia_aorta",
            "eco_beira_leito",
            "ecg_12_derivacoes",
            "hemograma_coagulacao_reserva",
            "funcao_renal_eletrólitos",
            "gasometria_lactato",
        ],
        "exames_opcionais": ["radiografia_torax", "troponina"],
        "exames_desnecessarios": ["dimero_d", "cinecoronariografia"],
        "justificativa_exames": {
            "angiotomografia_aorta": "Confirma extensão e ramos envolvidos no paciente ainda estável o suficiente para imagem rápida.",
            "eco_beira_leito": "Detecta flap proximal, insuficiência aórtica e tamponamento, sobretudo se houver deterioração.",
            "ecg_12_derivacoes": "Avalia isquemia concomitante sem excluir dissecção quando inespecífico.",
            "hemograma_coagulacao_reserva": "Prepara cirurgia de grande porte e eventual transfusão.",
            "funcao_renal_eletrólitos": "Estabelece função renal antes do contraste e detecta malperfusão.",
            "gasometria_lactato": "Avalia hipoperfusão sistêmica e tendência evolutiva.",
            "radiografia_torax": "Pode mostrar mediastino alargado, mas não confirma nem exclui o diagnóstico.",
            "troponina": "Pode estar elevada por comprometimento coronariano; não deve induzir trombólise sem integrar o quadro.",
            "dimero_d": "Não deve atrasar imagem definitiva em paciente de alta probabilidade.",
            "cinecoronariografia": "Não é exame inicial rotineiro e pode atrasar a correção cirúrgica urgente.",
        },
        "conduta_criterios": [
            _criterion(
                "Monitorização, analgesia e acessos",
                6,
                "monitorizacao",
                "acesso venoso",
                "analgesia",
                "linha arterial",
            ),
            _criterion(
                "Controle anti-impulso",
                9,
                "esmolol",
                "labetalol",
                "betabloqueador",
                "frequencia cardiaca menor que 60",
            ),
            _criterion(
                "Controle pressórico após beta-bloqueio",
                5,
                "nitroprussiato",
                "vasodilatador apos betabloqueio",
                "pressao sistolica 100 a 120",
            ),
            _criterion(
                "Cirurgia cardiovascular imediata",
                10,
                "cirurgia cardiovascular",
                "cirurgiao cardiaco",
                "reparo urgente",
                "centro aortico",
            ),
        ],
        "conduta_referencia": "Monitorizar, prover analgesia e acesso arterial; iniciar beta-bloqueio IV para reduzir frequência e força de ejeção, acrescentando vasodilatador apenas após o controle da frequência se a pressão continuar elevada. Acionar cirurgia cardiovascular imediatamente para reparo da aorta ascendente e evitar anticoagulação ou trombólise.",
        "feedback_hipotese_parcial": "Você reconheceu síndrome aórtica, mas o envolvimento da aorta ascendente define Stanford A e exige cirurgia urgente.",
        "feedback_hipotese_incorreta": "Dor máxima no início, assimetria de pulsos e pressão, sopro aórtico novo e flap na aorta ascendente sustentam dissecção Stanford A.",
        "feedback_seguranca": "Trombólise ou anticoagulação por suposto infarto pode ser catastrófica; vasodilatação isolada aumenta o estresse de cisalhamento.",
        "objetivos_aprendizagem": [
            "Reconhecer síndrome aórtica aguda",
            "Escolher imagem conforme estabilidade",
            "Aplicar controle anti-impulso e encaminhamento cirúrgico",
        ],
        "criterios_seguranca": [
            _safety(
                "Cirurgia imediata",
                "Dissecção da aorta ascendente requer avaliação cirúrgica emergencial.",
                "cirurgia",
                "reparo urgente",
                "cirurgiao cardiaco",
            ),
            _safety(
                "Evitar trombólise",
                "Trombólise ou anticoagulação inadequada aumenta sangramento e risco de ruptura.",
                "evitar trombolise",
                "nao trombolisar",
                "evitar anticoagulacao",
            ),
            _safety(
                "Beta-bloqueio antes de vasodilatador",
                "Vasodilatação isolada pode causar taquicardia reflexa e elevar o estresse aórtico.",
                "betabloqueador",
                "esmolol",
                "labetalol",
            ),
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Analgesia e controle anti-impulso reduzem dor, frequência e pressão enquanto a cirurgia é preparada.",
                "desfecho": "O paciente segue para reparo emergencial antes de ruptura ou malperfusão irreversível.",
                "reavaliacao": [
                    _vital(
                        "PA no braço direito", "190/108 mmHg", "112/70 mmHg", "melhora"
                    ),
                    _vital("Frequência cardíaca", "112 bpm", "60 bpm", "melhora"),
                    _vital("Dor", "10/10", "3/10", "melhora"),
                    _vital("Lactato", "2,6 mmol/L", "1,9 mmol/L", "melhora"),
                ],
            },
            "parcial": {
                "reacao": "A pressão diminui, mas a frequência ou o encaminhamento cirúrgico permanecem inadequados.",
                "desfecho": "A aorta continua exposta a estresse e o risco de extensão permanece elevado.",
                "reavaliacao": [
                    _vital(
                        "PA no braço direito", "190/108 mmHg", "150/88 mmHg", "melhora"
                    ),
                    _vital("Frequência cardíaca", "112 bpm", "96 bpm", "estavel"),
                    _vital("Dor", "10/10", "7/10", "estavel"),
                    _vital("Lactato", "2,6 mmol/L", "2,8 mmol/L", "piora"),
                ],
            },
            "insegura": {
                "reacao": "Sem controle anti-impulso e cirurgia, a dor piora e surgem sinais de ruptura ou malperfusão.",
                "desfecho": "O paciente evolui para choque obstrutivo/hemorrágico e dano de órgãos-alvo.",
                "reavaliacao": [
                    _vital("Pressão arterial", "190/108 mmHg", "72/44 mmHg", "piora"),
                    _vital("Frequência cardíaca", "112 bpm", "132 bpm", "piora"),
                    _vital(
                        "Consciência", "orientado", "rebaixamento progressivo", "piora"
                    ),
                    _vital("Lactato", "2,6 mmol/L", "6,2 mmol/L", "piora"),
                ],
            },
        },
        "reacao_paciente_referencia": "A dor e o estresse hemodinâmico devem reduzir durante a ponte para reparo cirúrgico.",
        "desfecho_referencia": "A dissecção Stanford A permanece uma emergência cirúrgica mesmo com melhora temporária da pressão.",
        "temas_estudo": [
            "Síndromes aórticas agudas",
            "Controle anti-impulso",
            "Dissecção Stanford A",
        ],
        "fontes_clinicas": [AORTA_SOURCE],
    },
    58: {
        "diagnostico_referencia": "Fibrilação atrial pré-excitada por via acessória, com taquicardia de complexos largos e instabilidade hemodinâmica.",
        "diagnostico_termos": [
            "fibrilacao atrial pre excitada",
            "fa com wolff parkinson white",
            "fa pre excitada instavel",
            "fibrilacao atrial com via acessoria",
        ],
        "diagnostico_parcial": [
            "fibrilacao atrial",
            "taquicardia de complexo largo",
            "wolff parkinson white",
            "taquiarritmia instavel",
        ],
        "exames_essenciais": [
            "ecg_12_derivacoes",
            "monitorizacao_continua",
            "eletrólitos_magnesio",
            "glicemia_capilar",
            "gasometria_lactato",
        ],
        "exames_opcionais": [
            "troponina_serial",
            "ecocardiograma_pos_estabilizacao",
            "tsh_t4_livre",
        ],
        "exames_desnecessarios": ["holter_24h", "angiotomografia_pulmonar"],
        "justificativa_exames": {
            "ecg_12_derivacoes": "O ritmo irregular, muito rápido e largo sugere condução anterógrada por via acessória.",
            "monitorizacao_continua": "Permite acompanhar instabilidade e preparar cardioversão com segurança.",
            "eletrólitos_magnesio": "Identifica fatores reversíveis que favorecem arritmia.",
            "glicemia_capilar": "Exclui rapidamente hipoglicemia como causa de confusão.",
            "gasometria_lactato": "Quantifica hipoperfusão decorrente da taquiarritmia.",
            "troponina_serial": "Pode caracterizar lesão por demanda após estabilização, sem mudar a prioridade imediata.",
            "ecocardiograma_pos_estabilizacao": "Avalia cardiopatia estrutural depois que a instabilidade foi tratada.",
            "tsh_t4_livre": "Pesquisa gatilho metabólico em etapa posterior.",
            "holter_24h": "Não tem papel durante instabilidade com arritmia já documentada.",
            "angiotomografia_pulmonar": "Não deve atrasar o tratamento do ritmo responsável pelo choque.",
        },
        "conduta_criterios": [
            _criterion(
                "Reconhecer instabilidade",
                7,
                "instabilidade",
                "hipotensao",
                "alteracao de consciencia",
                "choque",
            ),
            _criterion(
                "Cardioversão elétrica sincronizada",
                12,
                "cardioversao sincronizada",
                "choque sincronizado",
                "cardioversao eletrica",
            ),
            _criterion(
                "Evitar bloqueadores nodais",
                7,
                "evitar bloqueador nodal",
                "nao usar adenosina",
                "nao usar verapamil",
                "nao usar diltiazem",
                "nao usar digoxina",
                "nao usar amiodarona",
            ),
            _criterion(
                "Plano após estabilização",
                4,
                "eletrofisiologia",
                "ablacao",
                "via acessoria",
            ),
        ],
        "conduta_referencia": "Reconhecer a instabilidade e realizar cardioversão elétrica sincronizada imediata, com sedação somente se não causar atraso. Não administrar fármacos bloqueadores do nó AV, incluindo adenosina, verapamil, diltiazem, beta-bloqueador, digoxina ou amiodarona. Após estabilização, encaminhar para estudo eletrofisiológico e ablação da via acessória.",
        "feedback_hipotese_parcial": "Fibrilação atrial isolada não explica a largura e a extrema variabilidade dos complexos; a via acessória é decisiva para o risco e a conduta.",
        "feedback_hipotese_incorreta": "Taquicardia irregular, muito rápida, de complexos largos e variáveis, com PR curto prévio, caracteriza fibrilação atrial pré-excitada.",
        "feedback_seguranca": "Bloqueadores do nó AV podem acelerar a condução pela via acessória e precipitar fibrilação ventricular; a instabilidade exige cardioversão sincronizada.",
        "objetivos_aprendizagem": [
            "Reconhecer fibrilação atrial pré-excitada",
            "Diferenciar de outras taquicardias largas",
            "Evitar bloqueio nodal e priorizar cardioversão",
        ],
        "criterios_seguranca": [
            _safety(
                "Cardioversão imediata",
                "Hipotensão e alteração de consciência tornam a cardioversão sincronizada prioritária.",
                "cardioversao sincronizada",
                "choque sincronizado",
            ),
            _safety(
                "Evitar bloqueio nodal",
                "Bloqueadores nodais podem aumentar a condução pela via acessória e degenerar o ritmo para fibrilação ventricular.",
                "evitar bloqueador nodal",
                "nao usar adenosina",
                "nao usar verapamil",
                "nao usar digoxina",
            ),
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Após cardioversão sincronizada, o ritmo sinusal retorna e a perfusão melhora rapidamente.",
                "desfecho": "O paciente é estabilizado e encaminhado para avaliação eletrofisiológica e ablação definitiva.",
                "reavaliacao": [
                    _vital("Pressão arterial", "82/54 mmHg", "118/72 mmHg", "melhora"),
                    _vital(
                        "Frequência cardíaca",
                        "228 bpm irregular",
                        "84 bpm regular",
                        "melhora",
                    ),
                    _vital("SpO2", "92%", "97%", "melhora"),
                    _vital("Lactato", "4,0 mmol/L", "1,7 mmol/L", "melhora"),
                ],
            },
            "parcial": {
                "reacao": "A monitorização é iniciada, mas o atraso na cardioversão mantém sintomas e hipoperfusão.",
                "desfecho": "O paciente continua sob risco de degeneração para fibrilação ventricular.",
                "reavaliacao": [
                    _vital("Pressão arterial", "82/54 mmHg", "84/56 mmHg", "estavel"),
                    _vital(
                        "Frequência cardíaca",
                        "228 bpm irregular",
                        "218 bpm irregular",
                        "estavel",
                    ),
                    _vital("SpO2", "92%", "93%", "estavel"),
                    _vital("Lactato", "4,0 mmol/L", "4,4 mmol/L", "piora"),
                ],
            },
            "insegura": {
                "reacao": "O bloqueio nodal favorece condução ainda mais rápida pela via acessória e deterioração elétrica.",
                "desfecho": "A arritmia degenera para fibrilação ventricular e parada circulatória.",
                "reavaliacao": [
                    _vital("Pressão arterial", "82/54 mmHg", "não mensurável", "piora"),
                    _vital(
                        "Frequência cardíaca",
                        "228 bpm irregular",
                        "fibrilação ventricular",
                        "piora",
                    ),
                    _vital("Consciência", "confuso", "inconsciente", "piora"),
                    _vital("Pulso central", "presente e fino", "ausente", "piora"),
                ],
            },
        },
        "reacao_paciente_referencia": "A conversão rápida para ritmo sinusal deve restaurar pressão, consciência e perfusão.",
        "desfecho_referencia": "A estabilização aguda deve ser seguida por avaliação da via acessória e estratégia definitiva.",
        "temas_estudo": [
            "Fibrilação atrial pré-excitada",
            "Síndrome de Wolff-Parkinson-White",
            "Cardioversão sincronizada",
        ],
        "fontes_clinicas": [SVT_SOURCE],
    },
    59: {
        "diagnostico_referencia": "Endocardite infecciosa por Staphylococcus aureus em valva aórtica nativa, complicada por insuficiência aórtica grave e insuficiência cardíaca aguda.",
        "diagnostico_termos": [
            "endocardite infecciosa aortica",
            "endocardite por staphylococcus aureus",
            "endocardite em valva aortica nativa",
            "endocardite com insuficiencia aortica",
        ],
        "diagnostico_parcial": [
            "endocardite infecciosa",
            "sepse",
            "insuficiencia aortica",
            "insuficiencia cardiaca aguda",
        ],
        "exames_essenciais": [
            "hemoculturas_tres_pares",
            "ecocardiograma_transtoracico",
            "ecocardiograma_transesofagico",
            "hemograma_inflamatorios",
            "funcao_renal_hepatica_urina",
            "ecg_12_derivacoes",
            "radiografia_torax",
            "gasometria_lactato",
        ],
        "exames_opcionais": ["procalcitonina"],
        "exames_desnecessarios": ["pet_ct"],
        "justificativa_exames": {
            "hemoculturas_tres_pares": "Identificam bacteremia persistente e permitem terapia dirigida; devem ser colhidas antes do antibiótico se isso não causar atraso perigoso.",
            "ecocardiograma_transtoracico": "É a avaliação inicial de vegetação, lesão valvar e repercussão cardíaca.",
            "ecocardiograma_transesofagico": "Define perfuração, extensão perivalvar e anatomia para decisão cirúrgica.",
            "hemograma_inflamatorios": "Avalia resposta inflamatória, anemia e plaquetas para seguimento e procedimento.",
            "funcao_renal_hepatica_urina": "Detecta disfunção orgânica, fenômenos imunes e condiciona escolha e dose dos antimicrobianos.",
            "ecg_12_derivacoes": "Novo atraso de condução pode indicar extensão perivalvar e precisa ser monitorado.",
            "radiografia_torax": "Documenta congestão e ajuda a acompanhar a insuficiência cardíaca.",
            "gasometria_lactato": "Avalia hipoxemia e perfusão no quadro de insuficiência cardíaca e infecção sistêmica.",
            "procalcitonina": "Pode apoiar avaliação sistêmica, mas não substitui hemocultura e ecocardiografia.",
            "pet_ct": "Não é prioritário em valva nativa quando hemoculturas e ecocardiografia já estabelecem diagnóstico e complicação.",
        },
        "conduta_criterios": [
            _criterion(
                "Culturas e antimicrobiano IV precoce",
                9,
                "hemoculturas",
                "antibiotico intravenoso",
                "antimicrobiano",
                "ajustar pela cultura",
            ),
            _criterion(
                "Estabilizar insuficiência cardíaca e hipoxemia",
                6,
                "oxigenio",
                "monitorizacao",
                "acesso venoso",
                "insuficiencia cardiaca",
            ),
            _criterion(
                "Equipe de endocardite e cirurgia urgente",
                10,
                "equipe de endocardite",
                "cirurgia valvar urgente",
                "cirurgia cardiaca",
                "insuficiencia aortica grave",
            ),
            _criterion(
                "Monitorar complicações",
                5,
                "funcao renal",
                "embolia",
                "bloqueio atrioventricular",
                "hemocultura de controle",
            ),
        ],
        "conduta_referencia": "Colher três pares de hemoculturas rapidamente e iniciar antimicrobiano IV empírico conforme protocolo local, ajustando ao antibiograma. Tratar hipoxemia e congestão com monitorização estreita, envolver equipe de endocardite e cirurgia cardíaca e indicar cirurgia urgente pela insuficiência aórtica grave com insuficiência cardíaca. Vigiar embolização, função renal, condução e esterilização das culturas.",
        "feedback_hipotese_parcial": "Você reconheceu endocardite, mas precisa integrar a insuficiência aórtica grave e a insuficiência cardíaca, que tornam a avaliação cirúrgica urgente.",
        "feedback_hipotese_incorreta": "Bacteremia por S. aureus, vegetação aórtica e nova regurgitação valvar com congestão caracterizam endocardite infecciosa complicada.",
        "feedback_seguranca": "Antibiótico isolado é insuficiente diante de regurgitação grave e insuficiência cardíaca; a cirurgia não deve ser adiada por exames de baixo valor.",
        "objetivos_aprendizagem": [
            "Aplicar hemoculturas e ecocardiografia no diagnóstico",
            "Reconhecer complicações valvares e perivalvares",
            "Identificar indicação de cirurgia urgente",
        ],
        "criterios_seguranca": [
            _safety(
                "Antimicrobiano após culturas rápidas",
                "O atraso de tratamento aumenta bacteremia e complicações; as culturas devem ser obtidas sem retardar a estabilização.",
                "hemoculturas",
                "antibiotico",
                "antimicrobiano",
            ),
            _safety(
                "Avaliação cirúrgica urgente",
                "Insuficiência aórtica grave com edema pulmonar é indicação de avaliação cirúrgica urgente.",
                "cirurgia",
                "equipe de endocardite",
                "insuficiencia aortica grave",
            ),
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Oxigenação e perfusão melhoram enquanto antimicrobiano dirigido e cirurgia são organizados.",
                "desfecho": "A fonte valvar é tratada precocemente, com menor risco de choque, abscesso e embolização recorrente.",
                "reavaliacao": [
                    _vital("Temperatura", "39,1 °C", "37,8 °C", "melhora"),
                    _vital("Frequência cardíaca", "118 bpm", "96 bpm", "melhora"),
                    _vital("SpO2", "89%", "95% com suporte", "melhora"),
                    _vital("Frequência respiratória", "30 irpm", "22 irpm", "melhora"),
                    _vital("Lactato", "2,4 mmol/L", "1,7 mmol/L", "melhora"),
                ],
            },
            "parcial": {
                "reacao": "A febre começa a cair, mas congestão e lesão valvar persistem sem decisão cirúrgica oportuna.",
                "desfecho": "Mantém-se risco de edema pulmonar, extensão perivalvar e embolização.",
                "reavaliacao": [
                    _vital("Temperatura", "39,1 °C", "38,3 °C", "melhora"),
                    _vital("Frequência cardíaca", "118 bpm", "108 bpm", "estavel"),
                    _vital("SpO2", "89%", "91% com suporte", "estavel"),
                    _vital("Frequência respiratória", "30 irpm", "28 irpm", "estavel"),
                    _vital("Creatinina", "1,8 mg/dL", "2,0 mg/dL", "piora"),
                ],
            },
            "insegura": {
                "reacao": "Sem antimicrobiano e controle da lesão valvar, aumentam febre, congestão e hipoperfusão.",
                "desfecho": "O paciente evolui para choque misto, edema pulmonar grave e possível abscesso perivalvar.",
                "reavaliacao": [
                    _vital("Pressão arterial", "102/58 mmHg", "76/44 mmHg", "piora"),
                    _vital("Frequência cardíaca", "118 bpm", "134 bpm", "piora"),
                    _vital("SpO2", "89%", "82%", "piora"),
                    _vital("Lactato", "2,4 mmol/L", "5,8 mmol/L", "piora"),
                    _vital("Consciência", "orientado", "confuso", "piora"),
                ],
            },
        },
        "reacao_paciente_referencia": "A infecção e a congestão só melhoram de forma sustentada com antimicrobiano apropriado e controle oportuno da complicação valvar.",
        "desfecho_referencia": "Insuficiência cardíaca por destruição valvar define alto risco e necessidade de decisão cirúrgica multidisciplinar urgente.",
        "temas_estudo": [
            "Endocardite infecciosa",
            "Hemoculturas e ecocardiografia",
            "Indicações cirúrgicas na endocardite",
        ],
        "fontes_clinicas": [ENDOCARDITIS_SOURCE],
    },
    60: {
        "diagnostico_referencia": "Tamponamento cardíaco por derrame pericárdico neoplásico, causando choque obstrutivo.",
        "diagnostico_termos": [
            "tamponamento cardiaco neoplasico",
            "tamponamento cardiaco por derrame pericardico",
            "choque obstrutivo por tamponamento",
            "derrame pericardico com tamponamento",
        ],
        "diagnostico_parcial": [
            "tamponamento cardiaco",
            "derrame pericardico",
            "choque obstrutivo",
        ],
        "exames_essenciais": [
            "ecocardiograma_beira_leito",
            "ecg_12_derivacoes",
            "ultrassom_pulmonar",
            "hemograma_coagulacao",
            "funcao_renal_eletrólitos",
            "gasometria_lactato",
        ],
        "exames_opcionais": ["radiografia_torax", "analise_liquido_pericardico"],
        "exames_desnecessarios": ["tomografia_torax", "peptideos_natriureticos"],
        "justificativa_exames": {
            "ecocardiograma_beira_leito": "Confirma derrame com colapso de câmaras direitas e repercussão hemodinâmica sem transportar a paciente instável.",
            "ecg_12_derivacoes": "Baixa voltagem e alternância elétrica apoiam o diagnóstico e avaliam o ritmo.",
            "ultrassom_pulmonar": "A ausência de congestão ajuda a diferenciar choque obstrutivo de edema cardiogênico.",
            "hemograma_coagulacao": "Avalia anemia, plaquetas e risco hemorrágico antes da drenagem sem impedir procedimento salvador.",
            "funcao_renal_eletrólitos": "Caracteriza hipoperfusão e fatores corrigíveis durante a estabilização.",
            "gasometria_lactato": "Quantifica choque e fornece parâmetro de resposta após drenagem.",
            "radiografia_torax": "Pode mostrar cardiomegalia, mas não determina tamponamento e não deve atrasar ecocardiografia.",
            "analise_liquido_pericardico": "Após a drenagem, auxilia a definir etiologia e planejamento oncológico.",
            "tomografia_torax": "O transporte da paciente instável atrasa a drenagem e acrescenta pouco ao eco diagnóstico.",
            "peptideos_natriureticos": "Não distinguem nem tratam a causa do choque neste cenário.",
        },
        "conduta_criterios": [
            _criterion(
                "Estabilização como ponte",
                7,
                "abc",
                "monitorizacao",
                "acesso venoso",
                "oxigenio",
                "cristaloide cauteloso",
            ),
            _criterion(
                "Drenagem pericárdica imediata",
                12,
                "pericardiocentese urgente",
                "drenagem pericardica",
                "eco guiada",
                "dreno pericardico",
            ),
            _criterion(
                "Evitar redução do retorno venoso",
                6,
                "evitar intubacao",
                "evitar pressao positiva",
                "evitar diuretico",
                "evitar nitrato",
            ),
            _criterion(
                "Investigar causa e recorrência",
                5,
                "citologia",
                "janela pericardica",
                "oncologia",
                "recorrencia",
            ),
        ],
        "conduta_referencia": "Monitorizar, ofertar oxigênio, obter acessos e usar pequeno volume de cristaloide apenas como ponte reavaliada. Realizar pericardiocentese ecoguiada urgente com drenagem contínua. Evitar diuréticos, nitratos e ventilação com pressão positiva antes do alívio, sempre que possível. Após estabilização, analisar o líquido e discutir oncologia e janela pericárdica conforme recorrência.",
        "feedback_hipotese_parcial": "Reconhecer apenas derrame pericárdico não basta: hipotensão, turgência jugular, pulso paradoxal e colapso de câmaras direitas definem tamponamento com choque.",
        "feedback_hipotese_incorreta": "A combinação de choque, jugulares ingurgitadas, pulmões limpos e ecocardiograma com colapso direito caracteriza tamponamento cardíaco.",
        "feedback_seguranca": "Tomografia, diurético ou intubação antes da drenagem podem agravar ou prolongar o choque; o tratamento definitivo é aliviar o pericárdio.",
        "objetivos_aprendizagem": [
            "Reconhecer tamponamento e choque obstrutivo",
            "Interpretar ecocardiografia focada",
            "Priorizar drenagem e evitar redução do retorno venoso",
        ],
        "criterios_seguranca": [
            _safety(
                "Drenagem imediata",
                "Choque por tamponamento exige drenagem pericárdica sem atraso por exames não essenciais.",
                "pericardiocentese",
                "drenagem pericardica",
                "eco guiada",
            ),
            _safety(
                "Preservar retorno venoso",
                "Pressão positiva, nitratos e diuréticos podem reduzir ainda mais o débito cardíaco antes da drenagem.",
                "evitar intubacao",
                "evitar pressao positiva",
                "evitar diuretico",
                "evitar nitrato",
            ),
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Após drenagem, a pressão sobe, a taquicardia reduz e a dispneia melhora em minutos.",
                "desfecho": "A paciente sai do choque e permanece com dreno e investigação da etiologia neoplásica e recorrência.",
                "reavaliacao": [
                    _vital("Pressão arterial", "78/52 mmHg", "108/68 mmHg", "melhora"),
                    _vital("Frequência cardíaca", "128 bpm", "94 bpm", "melhora"),
                    _vital("SpO2", "91%", "97%", "melhora"),
                    _vital("Frequência respiratória", "30 irpm", "20 irpm", "melhora"),
                    _vital("Lactato", "4,7 mmol/L", "2,0 mmol/L", "melhora"),
                ],
            },
            "parcial": {
                "reacao": "Medidas de ponte trazem melhora transitória, mas o líquido continua limitando o enchimento cardíaco.",
                "desfecho": "A paciente permanece dependente de suporte e pode deteriorar até a drenagem.",
                "reavaliacao": [
                    _vital("Pressão arterial", "78/52 mmHg", "84/56 mmHg", "estavel"),
                    _vital("Frequência cardíaca", "128 bpm", "120 bpm", "estavel"),
                    _vital("SpO2", "91%", "93%", "estavel"),
                    _vital("Frequência respiratória", "30 irpm", "28 irpm", "estavel"),
                    _vital("Lactato", "4,7 mmol/L", "4,5 mmol/L", "estavel"),
                ],
            },
            "insegura": {
                "reacao": "Sem drenagem ou após redução brusca do retorno venoso, a pressão e a perfusão entram em colapso.",
                "desfecho": "A paciente evolui para choque obstrutivo refratário e atividade elétrica sem pulso.",
                "reavaliacao": [
                    _vital("Pressão arterial", "78/52 mmHg", "não mensurável", "piora"),
                    _vital(
                        "Frequência cardíaca",
                        "128 bpm",
                        "142 bpm, depois bradicardia",
                        "piora",
                    ),
                    _vital("SpO2", "91%", "80%", "piora"),
                    _vital("Consciência", "orientada", "inconsciente", "piora"),
                    _vital("Pulso central", "presente e fino", "ausente", "piora"),
                ],
            },
        },
        "reacao_paciente_referencia": "A melhora hemodinâmica esperada ocorre após alívio efetivo da pressão intrapericárdica.",
        "desfecho_referencia": "A drenagem trata a emergência; etiologia, recorrência e estratégia definitiva exigem seguimento multidisciplinar.",
        "temas_estudo": [
            "Tamponamento cardíaco",
            "Choque obstrutivo",
            "Pericardiocentese",
        ],
        "fontes_clinicas": [TAMPONADE_SOURCE],
    },
}
