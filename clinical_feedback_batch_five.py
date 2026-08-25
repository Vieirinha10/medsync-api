"""Quinto lote de rubricas estruturadas para casos clínicos legados."""

from typing import Any


def _source(title: str, organization: str, year: int, url: str) -> dict[str, Any]:
    return {"titulo": title, "organizacao": organization, "ano": year, "url": url}


def _outcomes(
    adequate_reaction: str,
    adequate_outcome: str,
    partial_reaction: str,
    partial_outcome: str,
    unsafe_reaction: str,
    unsafe_outcome: str,
) -> dict[str, dict[str, str]]:
    return {
        "adequada": {"reacao": adequate_reaction, "desfecho": adequate_outcome},
        "parcial": {"reacao": partial_reaction, "desfecho": partial_outcome},
        "insegura": {"reacao": unsafe_reaction, "desfecho": unsafe_outcome},
    }


STROKE_SOURCE = _source(
    "2026 Guideline for the Early Management of Patients With Acute Ischemic Stroke",
    "American Heart Association and American Stroke Association",
    2026,
    "https://www.ahajournals.org/doi/10.1161/STR.0000000000000513",
)

RHEUMATIC_FEVER_SOURCE = _source(
    "WHO guideline on the prevention and diagnosis of rheumatic fever and rheumatic heart disease",
    "World Health Organization",
    2024,
    "https://www.ncbi.nlm.nih.gov/books/NBK609692/",
)


FIFTH_FEEDBACK_BATCH_RUBRICS: dict[int, dict[str, Any]] = {
    26: {
        "diagnostico_referencia": (
            "AVC isquêmico agudo de circulação posterior, em território da artéria cerebral posterior, "
            "com crise epiléptica na apresentação."
        ),
        "diagnostico_termos": [
            "avc isquêmico de circulação posterior",
            "avc isquemico de circulacao posterior",
            "avc isquêmico em território de cerebral posterior",
            "avc isquemico em territorio de cerebral posterior",
            "infarto de artéria cerebral posterior",
            "infarto de arteria cerebral posterior",
        ],
        "diagnostico_parcial": [
            "avc isquêmico",
            "avc isquemico",
            "acidente vascular cerebral isquêmico",
            "acidente vascular cerebral isquemico",
            "crise convulsiva",
        ],
        "exames_essenciais": ["glicemia_abc", "nihss_tempo", "tc_cranio", "angio_tc"],
        "exames_opcionais": ["rm_difusao", "ecg_laboratorio_avc"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "glicemia_abc": "Glicemia e avaliação ABC identificam mimetizadores e instabilidade sem atrasar a reperfusão.",
            "nihss_tempo": "Último momento bem e exame neurológico estruturado definem elegibilidade e permitem acompanhar evolução.",
            "tc_cranio": "TC sem contraste exclui hemorragia; não é o exame que demonstra diretamente uma obstrução arterial.",
            "angio_tc": "AngioTC localiza a oclusão e orienta avaliação endovascular.",
            "rm_difusao": "RM com difusão aumenta a sensibilidade para infarto posterior quando disponível sem atraso terapêutico.",
            "ecg_laboratorio_avc": "ECG e exames básicos apoiam reperfusão, segurança e investigação etiológica.",
        },
        "conduta_criterios": [
            {
                "nome": "Ativar protocolo de AVC e estabilizar",
                "pontos": 8,
                "termos": [
                    "protocolo de avc",
                    "código avc",
                    "codigo avc",
                    "via aérea",
                    "via aerea",
                    "glicemia",
                ],
            },
            {
                "nome": "Avaliar trombólise intravenosa",
                "pontos": 7,
                "termos": [
                    "trombólise",
                    "trombolise",
                    "alteplase",
                    "tenecteplase",
                    "janela terapêutica",
                    "janela terapeutica",
                ],
            },
            {
                "nome": "Avaliar terapia endovascular",
                "pontos": 7,
                "termos": [
                    "trombectomia",
                    "tratamento endovascular",
                    "neurorradiologia",
                    "centro de avc",
                ],
            },
            {
                "nome": "Prevenir complicações e recorrência",
                "pontos": 8,
                "termos": [
                    "avaliação da deglutição",
                    "avaliacao da degluticao",
                    "antiagregante",
                    "estatina",
                    "tratar convulsão",
                    "tratar convulsao",
                ],
            },
        ],
        "conduta_referencia": (
            "Ativar código AVC, registrar o último momento bem, estabilizar ABC, verificar glicemia e obter TC/angioTC sem atraso. "
            "Avaliar trombólise IV e tratamento endovascular conforme tempo, vaso e imagem. Tratar convulsão ativa, sem atrasar "
            "reperfusão, e após excluir hemorragia organizar deglutição, prevenção de aspiração, antiagregação, estatina e investigação etiológica."
        ),
        "feedback_hipotese_parcial": "Você reconheceu AVC, mas faltou localizar a circulação posterior e separar o déficit vascular da crise epiléptica associada.",
        "feedback_hipotese_incorreta": "Déficit focal visual e sensitivo-motor persistente em paciente vascular deve ser tratado como AVC agudo, mesmo com convulsão na apresentação.",
        "feedback_seguranca": "Convulsão não exclui AVC. Não aguarde RM ou exames laboratoriais completos para discutir reperfusão após TC e angioTC.",
        "objetivos_aprendizagem": [
            "Reconhecer AVC posterior",
            "Selecionar imagem de reperfusão",
            "Manejar convulsão sem perder a janela terapêutica",
        ],
        "criterios_seguranca": [
            {
                "nome": "Não atrasar reperfusão",
                "termos": [
                    "trombólise",
                    "trombolise",
                    "trombectomia",
                    "tratamento endovascular",
                ],
                "feedback_omissao": "Atraso reduz a chance de recuperação do tecido cerebral ainda viável.",
            },
            {
                "nome": "Proteger via aérea e deglutição",
                "termos": [
                    "via aérea",
                    "via aerea",
                    "avaliação da deglutição",
                    "avaliacao da degluticao",
                    "aspiração",
                    "aspiracao",
                ],
                "feedback_omissao": "Convulsão e AVC aumentam o risco de broncoaspiração e insuficiência respiratória.",
            },
        ],
        "desfechos_conduta": _outcomes(
            "O déficit estabiliza ou melhora após reperfusão, sem nova crise ou broncoaspiração.",
            "O paciente segue para unidade de AVC e prevenção secundária com menor incapacidade possível.",
            "A progressão é contida, mas déficits visuais e motores persistem e a investigação fica incompleta.",
            "Há maior dependência funcional e risco de recorrência.",
            "O infarto se amplia enquanto a janela de reperfusão é perdida ou a via aérea deteriora.",
            "Pode ocorrer edema cerebral, aspiração, incapacidade grave ou morte.",
        ),
        "reacao_paciente_referencia": "Monitorar NIHSS, consciência, oxigenação, deglutição, pressão e recorrência de crises.",
        "desfecho_referencia": "O prognóstico depende da rapidez da reperfusão e da prevenção de complicações neurológicas e respiratórias.",
        "temas_estudo": [
            "AVC de circulação posterior",
            "Trombólise e trombectomia",
            "Crise epiléptica no AVC",
        ],
        "fontes_clinicas": [STROKE_SOURCE],
    },
    27: {
        "diagnostico_referencia": "Forma digestiva crônica da doença de Chagas com megaesôfago e provável megacólon, associada a desnutrição grave.",
        "diagnostico_termos": [
            "doença de chagas digestiva com megaesôfago e megacólon",
            "doenca de chagas digestiva com megaesofago e megacolon",
            "forma digestiva da doença de chagas",
            "forma digestiva da doenca de chagas",
            "megaesôfago e megacólon chagásicos",
            "megaesofago e megacolon chagasicos",
        ],
        "diagnostico_parcial": [
            "megaesôfago chagásico",
            "megaesofago chagasico",
            "megacólon chagásico",
            "megacolon chagasico",
            "desnutrição",
            "desnutricao",
        ],
        "exames_essenciais": [
            "avaliacao_nutricional",
            "esofagograma",
            "avaliacao_degluticao",
            "laboratorio_refeeding",
        ],
        "exames_opcionais": ["endoscopia", "enema_opaco", "albumina"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "avaliacao_nutricional": "Perda ponderal, ingestão, massa muscular, força e exame físico diagnosticam e graduam desnutrição; albumina isolada não faz isso.",
            "esofagograma": "Esofagograma caracteriza dilatação, retenção e esvaziamento do megaesôfago.",
            "avaliacao_degluticao": "Disfagia e vômitos exigem avaliação de segurança alimentar e risco de aspiração.",
            "laboratorio_refeeding": "Eletrólitos, fósforo, magnésio, potássio e função renal orientam reposição e risco de síndrome de realimentação.",
            "endoscopia": "Endoscopia exclui obstrução mecânica, neoplasia e lesões mucosas, mas não mede adequadamente a motilidade.",
            "enema_opaco": "Imagem do cólon ajuda a confirmar megacólon e complicações em constipação grave.",
            "albumina": "Albumina reflete inflamação e prognóstico, não reserva proteica corporal nem diagnóstico nutricional isolado.",
        },
        "conduta_criterios": [
            {
                "nome": "Estabilizar desnutrição e risco de realimentação",
                "pontos": 8,
                "termos": [
                    "realimentação",
                    "realimentacao",
                    "tiamina",
                    "fósforo",
                    "fosforo",
                    "eletrólitos",
                    "eletrolitos",
                ],
            },
            {
                "nome": "Adaptar alimentação e proteger de aspiração",
                "pontos": 7,
                "termos": [
                    "consistência",
                    "consistencia",
                    "pequenas refeições",
                    "pequenas refeicoes",
                    "fonoaudiologia",
                    "aspiração",
                    "aspiracao",
                ],
            },
            {
                "nome": "Tratar megaesôfago e megacólon",
                "pontos": 8,
                "termos": [
                    "gastroenterologia",
                    "dilatação",
                    "dilatacao",
                    "miotomia",
                    "laxativo",
                    "megacólon",
                    "megacolon",
                ],
            },
            {
                "nome": "Planejar suporte nutricional e seguimento",
                "pontos": 7,
                "termos": [
                    "nutricionista",
                    "suplementação",
                    "suplementacao",
                    "nutrição enteral",
                    "nutricao enteral",
                    "peso semanal",
                ],
            },
        ],
        "conduta_referencia": (
            "Internar se a ingestão for insegura ou houver distúrbio metabólico, iniciar realimentação cautelosa com tiamina e monitorização de fósforo, "
            "magnésio e potássio. Adaptar consistência e volume com nutrição/fonoaudiologia, prevenir aspiração e constipação e discutir tratamento "
            "endoscópico ou cirúrgico do megaesôfago/megacólon com equipe especializada."
        ),
        "feedback_hipotese_parcial": "Você reconheceu desnutrição ou um dos megas, mas faltou integrar disfagia, vômitos e constipação à forma digestiva chagásica combinada.",
        "feedback_hipotese_incorreta": "Na doença de Chagas crônica, disfagia e regurgitação sugerem megaesôfago, enquanto constipação e distensão sugerem megacólon; a perda ponderal indica complicação nutricional grave.",
        "feedback_seguranca": "Não use albumina como diagnóstico isolado de desnutrição. Reintrodução rápida de calorias em paciente caquético pode causar síndrome de realimentação.",
        "objetivos_aprendizagem": [
            "Reconhecer a forma digestiva chagásica",
            "Avaliar desnutrição sem depender de albumina",
            "Prevenir aspiração e realimentação inadequada",
        ],
        "criterios_seguranca": [
            {
                "nome": "Prevenir síndrome de realimentação",
                "termos": [
                    "realimentação",
                    "realimentacao",
                    "tiamina",
                    "fósforo",
                    "fosforo",
                ],
                "feedback_omissao": "Realimentação rápida pode provocar hipofosfatemia, arritmia, insuficiência respiratória e morte.",
            },
            {
                "nome": "Avaliar deglutição e aspiração",
                "termos": [
                    "fonoaudiologia",
                    "aspiração",
                    "aspiracao",
                    "consistência",
                    "consistencia",
                ],
                "feedback_omissao": "Megaesôfago avançado aumenta risco de regurgitação, pneumonia aspirativa e impossibilidade de alimentação segura.",
            },
        ],
        "desfechos_conduta": _outcomes(
            "A ingestão torna-se segura, eletrólitos permanecem estáveis e o peso começa a se recuperar.",
            "O paciente ganha força e segue para tratamento definitivo da dismotilidade digestiva.",
            "A ingestão melhora pouco, mas disfagia, constipação ou perda muscular persistem.",
            "Continuam internações, quedas e complicações digestivas.",
            "Realimentação abrupta ou alimentação insegura causa distúrbios eletrolíticos ou aspiração.",
            "Pode ocorrer arritmia, insuficiência respiratória, pneumonia ou morte.",
        ),
        "reacao_paciente_referencia": "Monitorar ingestão, peso, força, hidratação, fósforo, magnésio, potássio, evacuações e sinais de aspiração.",
        "desfecho_referencia": "Recuperação nutricional segura depende do tratamento conjunto do megaesôfago e do megacólon.",
        "temas_estudo": [
            "Forma digestiva da doença de Chagas",
            "Avaliação nutricional",
            "Síndrome de realimentação",
        ],
        "fontes_clinicas": [
            _source(
                "2nd Brazilian Consensus on Chagas Disease",
                "Brazilian Society of Tropical Medicine and Ministry of Health",
                2016,
                "https://www.scielo.br/j/rsbmt/a/mNgRbrGjpwwc9dSF73PdMHt",
            ),
            _source(
                "The Use of Visceral Proteins as Nutrition Markers",
                "American Society for Parenteral and Enteral Nutrition",
                2021,
                "https://aspenjournals.onlinelibrary.wiley.com/doi/10.1002/ncp.10588",
            ),
        ],
    },
    28: {
        "diagnostico_referencia": "Doença celíaca pediátrica com repercussão nutricional e anemia provável por deficiência de ferro.",
        "diagnostico_termos": [
            "doença celíaca",
            "doenca celiaca",
            "enteropatia por glúten",
            "enteropatia por gluten",
        ],
        "diagnostico_parcial": [
            "síndrome de má absorção",
            "sindrome de ma absorcao",
            "intolerância ao glúten",
            "intolerancia ao gluten",
        ],
        "exames_essenciais": ["anti_ttg", "iga_total", "hemo_ferritina"],
        "exames_opcionais": ["ema_segunda_amostra", "biopsia_duodeno"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "anti_ttg": "tTG-IgA quantitativo é o teste inicial preferencial enquanto a criança consome glúten.",
            "iga_total": "IgA total identifica deficiência que pode tornar o tTG-IgA falsamente negativo e indicar teste IgG.",
            "hemo_ferritina": "Hemograma e ferritina documentam anemia e deficiência de ferro associadas à má absorção.",
            "ema_segunda_amostra": "EMA-IgA positivo em segunda amostra permite via sem biópsia se tTG-IgA for pelo menos 10 vezes o limite superior.",
            "biopsia_duodeno": "Biópsias de bulbo e duodeno distal são necessárias quando tTG-IgA é menor que 10 vezes o limite, IgA é deficiente ou há discordância.",
        },
        "conduta_criterios": [
            {
                "nome": "Manter glúten até confirmar diagnóstico",
                "pontos": 7,
                "termos": [
                    "manter glúten",
                    "manter gluten",
                    "não retirar glúten",
                    "nao retirar gluten",
                    "antes da biópsia",
                    "antes da biopsia",
                ],
            },
            {
                "nome": "Confirmar pelo algoritmo pediátrico",
                "pontos": 8,
                "termos": [
                    "gastroenterologia pediátrica",
                    "gastroenterologia pediatrica",
                    "ema",
                    "10 vezes",
                    "biópsia duodenal",
                    "biopsia duodenal",
                ],
            },
            {
                "nome": "Iniciar dieta sem glúten após confirmação",
                "pontos": 8,
                "termos": [
                    "dieta sem glúten",
                    "dieta sem gluten",
                    "contaminação cruzada",
                    "contaminacao cruzada",
                    "nutricionista",
                ],
            },
            {
                "nome": "Corrigir deficiências e acompanhar crescimento",
                "pontos": 7,
                "termos": [
                    "ferro",
                    "ferritina",
                    "crescimento",
                    "peso",
                    "vitamina d",
                    "vacinação",
                ],
            },
        ],
        "conduta_referencia": (
            "Manter dieta com glúten durante a investigação e encaminhar à gastroenterologia pediátrica. Interpretar tTG-IgA com IgA total; usar EMA em "
            "segunda amostra na via sem biópsia ou realizar biópsias adequadas quando indicado. Após confirmação, instituir dieta sem glúten com nutricionista, "
            "prevenir contaminação cruzada, repor ferro e outras deficiências e acompanhar crescimento e sorologia."
        ),
        "feedback_hipotese_parcial": "Você reconheceu má absorção, mas faltou ligar diarreia, baixo crescimento e anemia à doença celíaca e ao algoritmo sorológico pediátrico.",
        "feedback_hipotese_incorreta": "Diarreia crônica, dor abdominal, baixa estatura/peso e anemia em criança que consome glúten exigem investigação de doença celíaca.",
        "feedback_seguranca": "Não retire glúten antes de concluir a investigação: isso pode normalizar sorologia e mucosa e tornar o diagnóstico inconclusivo.",
        "objetivos_aprendizagem": [
            "Solicitar tTG-IgA com IgA total",
            "Aplicar critérios com ou sem biópsia",
            "Planejar dieta e seguimento nutricional",
        ],
        "criterios_seguranca": [
            {
                "nome": "Preservar validade diagnóstica",
                "termos": [
                    "manter glúten",
                    "manter gluten",
                    "não retirar glúten",
                    "nao retirar gluten",
                ],
                "feedback_omissao": "Dieta sem glúten antes da confirmação pode gerar falso-negativo e exigir nova exposição prolongada.",
            },
            {
                "nome": "Tratar repercussão nutricional",
                "termos": ["ferro", "ferritina", "crescimento", "nutricionista"],
                "feedback_omissao": "Anemia e falha de crescimento precisam ser medidas e corrigidas, não apenas observar melhora da diarreia.",
            },
        ],
        "desfechos_conduta": _outcomes(
            "A diarreia e a dor diminuem, o apetite melhora e o crescimento retoma após confirmação e dieta correta.",
            "A anemia corrige e a sorologia cai progressivamente com adesão adequada.",
            "Há melhora incompleta por contaminação cruzada ou deficiência não reposta.",
            "Persistem anemia, baixo crescimento e sintomas recorrentes.",
            "A dieta é iniciada antes da confirmação ou o glúten permanece após o diagnóstico.",
            "O diagnóstico torna-se inconclusivo ou a má absorção continua com repercussão óssea e nutricional.",
        ),
        "reacao_paciente_referencia": "Acompanhar sintomas, peso, estatura, hemoglobina, ferritina e queda do tTG-IgA.",
        "desfecho_referencia": "Dieta estrita e acompanhamento especializado permitem recuperação clínica e do crescimento na maioria das crianças.",
        "temas_estudo": [
            "Diagnóstico pediátrico da doença celíaca",
            "Dieta sem glúten",
            "Deficiências nutricionais",
        ],
        "fontes_clinicas": [
            _source(
                "ESPGHAN Guidelines for Diagnosing Coeliac Disease",
                "European Society for Paediatric Gastroenterology, Hepatology and Nutrition",
                2020,
                "https://www.espghan.org/knowledge-center/publications/Gastroenterology/2019_ESPGHAN_guidelines_for_diagnosing_coeliac_disease",
            )
        ],
    },
    29: {
        "diagnostico_referencia": (
            "Escarlatina por Streptococcus do grupo A, condicionada à presença de exantema escarlatiniforme; "
            "dispneia, edema e taquicardia exigem exclusão imediata de complicação cardíaca ou renal."
        ),
        "diagnostico_termos": [
            "escarlatina",
            "scarlatina",
            "faringite estreptocócica com exantema",
            "faringite estreptococica com exantema",
        ],
        "diagnostico_parcial": [
            "faringite estreptocócica",
            "faringite estreptococica",
            "estreptococo do grupo a",
            "febre reumática",
            "febre reumatica",
        ],
        "exames_essenciais": [
            "avaliacao_exantema",
            "teste_rapido_strepto",
            "avaliacao_cardio_renal",
        ],
        "exames_opcionais": ["cultura_orofaringe"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "avaliacao_exantema": "Escarlatina requer exantema eritematoso áspero, linhas de Pastia e distribuição típica; língua em framboesa isolada não basta.",
            "teste_rapido_strepto": "Teste rápido positivo confirma infecção por GAS no contexto compatível.",
            "avaliacao_cardio_renal": "Dispneia, edema e taquicardia são sinais de alarme e exigem oximetria, pressão, ausculta, urina/função renal e ECG/eco conforme achados.",
            "cultura_orofaringe": "Cultura é indicada após teste rápido negativo em criança sintomática; não é necessária para confirmar um teste rápido positivo.",
        },
        "conduta_criterios": [
            {
                "nome": "Avaliar e estabilizar sinais de alarme",
                "pontos": 8,
                "termos": [
                    "oximetria",
                    "dispneia",
                    "edema",
                    "insuficiência cardíaca",
                    "insuficiencia cardiaca",
                    "função renal",
                    "funcao renal",
                ],
            },
            {
                "nome": "Tratar GAS com antibiótico adequado",
                "pontos": 8,
                "termos": [
                    "penicilina",
                    "amoxicilina",
                    "antibiótico",
                    "antibiotico",
                    "10 dias",
                ],
            },
            {
                "nome": "Oferecer suporte sintomático seguro",
                "pontos": 6,
                "termos": [
                    "hidratação",
                    "hidratacao",
                    "paracetamol",
                    "antitérmico",
                    "antitermico",
                    "evitar aspirina",
                ],
            },
            {
                "nome": "Orientar transmissão e retorno",
                "pontos": 8,
                "termos": [
                    "12 horas",
                    "24 horas",
                    "afebril",
                    "higiene",
                    "retorno",
                    "escola",
                ],
            },
        ],
        "conduta_referencia": (
            "Confirmar o padrão de exantema e o teste para GAS, mas avaliar imediatamente dispneia, edema e taquicardia para cardite, insuficiência cardíaca "
            "ou comprometimento renal. Se o quadro for escarlatina confirmada, tratar com penicilina ou amoxicilina, hidratação e antitérmico, orientar higiene "
            "e afastamento até estar afebril e completar pelo menos 12–24 horas de antibiótico."
        ),
        "feedback_hipotese_parcial": "Você reconheceu infecção estreptocócica, mas faltou documentar o exantema típico e explicar os sinais de alarme cardiorrenais.",
        "feedback_hipotese_incorreta": "Língua em framboesa sugere escarlatina apenas junto de faringite e exantema áspero típico; dispneia e edema não devem ser atribuídos automaticamente a um quadro simples.",
        "feedback_seguranca": "Dispneia, edema e taquicardia exigem avaliação urgente. Um teste rápido positivo confirma GAS, mas não explica sozinho possível insuficiência cardíaca ou renal.",
        "objetivos_aprendizagem": [
            "Reconhecer o exantema da escarlatina",
            "Interpretar teste rápido e cultura",
            "Identificar complicações pós-estreptocócicas",
        ],
        "criterios_seguranca": [
            {
                "nome": "Investigar sinais cardiorrenais",
                "termos": [
                    "oximetria",
                    "insuficiência cardíaca",
                    "insuficiencia cardiaca",
                    "função renal",
                    "funcao renal",
                    "urina",
                ],
                "feedback_omissao": "Edema e dispneia podem indicar complicação grave e não pertencem à evolução simples da escarlatina.",
            },
            {
                "nome": "Tratar infecção confirmada",
                "termos": ["penicilina", "amoxicilina", "antibiótico", "antibiotico"],
                "feedback_omissao": "Antibiótico reduz transmissão e complicações supurativas da infecção por GAS.",
            },
        ],
        "desfechos_conduta": _outcomes(
            "Febre, odinofagia e exantema regridem, enquanto sinais cardiorrenais são esclarecidos e tratados.",
            "A criança retorna com segurança após redução da transmissibilidade e sem complicações.",
            "A infecção melhora, mas a origem de edema e dispneia permanece pouco definida.",
            "Pode haver retorno precoce por piora respiratória ou renal.",
            "Os sinais de alarme são ignorados ou a infecção confirmada não é tratada.",
            "Pode evoluir com insuficiência cardíaca, glomerulonefrite, infecção invasiva ou outras complicações.",
        ),
        "reacao_paciente_referencia": "Monitorar febre, exantema, respiração, edema, diurese, pressão e tolerância oral.",
        "desfecho_referencia": "Escarlatina costuma responder rapidamente ao antibiótico, mas os sinais atípicos deste caso exigem investigação paralela.",
        "temas_estudo": [
            "Escarlatina",
            "Diagnóstico de GAS",
            "Complicações pós-estreptocócicas",
        ],
        "fontes_clinicas": [
            _source(
                "Clinical Guidance for Scarlet Fever",
                "Centers for Disease Control and Prevention",
                2026,
                "https://www.cdc.gov/group-a-strep/hcp/clinical-guidance/scarlet-fever.html",
            )
        ],
    },
    30: {
        "diagnostico_referencia": "Febre reumática aguda com cardite clínica e poliartrite migratória, causando insuficiência cardíaca e doença valvar multivalvar.",
        "diagnostico_termos": [
            "febre reumática aguda com cardite",
            "febre reumatica aguda com cardite",
            "cardite reumática com poliartrite",
            "cardite reumatica com poliartrite",
        ],
        "diagnostico_parcial": [
            "febre reumática",
            "febre reumatica",
            "cardite reumática",
            "cardite reumatica",
            "doença cardíaca reumática",
            "doenca cardiaca reumatica",
        ],
        "exames_essenciais": ["eco", "aslo_anti_dnase", "vhs_pcr", "ecg"],
        "exames_opcionais": ["raiox_bnp_funcao_renal"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "eco": "Ecocardiograma Doppler confirma cardite clínica ou subclínica, quantifica regurgitação e avalia função ventricular.",
            "aslo_anti_dnase": "ASLO ou anti-DNase B em elevação documentam infecção estreptocócica recente; título isolado não mede gravidade da cardite.",
            "vhs_pcr": "Marcadores inflamatórios compõem critérios menores e ajudam a acompanhar atividade.",
            "ecg": "ECG avalia intervalo PR, arritmias e repercussão da cardite.",
            "raiox_bnp_funcao_renal": "Radiografia, BNP e função renal ajudam a graduar congestão e orientar diurético quando há insuficiência cardíaca.",
        },
        "conduta_criterios": [
            {
                "nome": "Internar e tratar insuficiência cardíaca",
                "pontos": 8,
                "termos": [
                    "internação",
                    "internacao",
                    "diurético",
                    "diuretico",
                    "insuficiência cardíaca",
                    "insuficiencia cardiaca",
                    "cardiologia",
                ],
            },
            {
                "nome": "Erradicar GAS",
                "pontos": 7,
                "termos": [
                    "penicilina benzatina",
                    "penicilina",
                    "erradicar estreptococo",
                    "amoxicilina",
                ],
            },
            {
                "nome": "Controlar inflamação e artrite",
                "pontos": 7,
                "termos": [
                    "naproxeno",
                    "aspirina",
                    "anti-inflamatório",
                    "anti-inflamatorio",
                    "corticosteroide",
                ],
            },
            {
                "nome": "Iniciar profilaxia secundária",
                "pontos": 8,
                "termos": [
                    "profilaxia secundária",
                    "profilaxia secundaria",
                    "penicilina benzatina a cada",
                    "longo prazo",
                    "prevenir recorrência",
                    "prevenir recorrencia",
                ],
            },
        ],
        "conduta_referencia": (
            "Internar pela cardite com sinais de congestão, realizar ecocardiograma/ECG e tratar insuficiência cardíaca com cardiologia. Erradicar GAS com "
            "penicilina mesmo sem faringite ativa, controlar artrite e inflamação conforme gravidade e iniciar profilaxia secundária regular e prolongada com "
            "penicilina benzatina. Planejar seguimento valvar e eventual intervenção."
        ),
        "feedback_hipotese_parcial": "Você reconheceu cardite ou febre reumática, mas faltou integrar poliartrite migratória, evidência estreptocócica e insuficiência multivalvar pelos critérios de Jones.",
        "feedback_hipotese_incorreta": "Poliartrite migratória e cardite após faringites estreptocócicas sustentam febre reumática aguda; o sopro multivalvar e a estase jugular indicam repercussão cardíaca importante.",
        "feedback_seguranca": "ASLO elevado isoladamente não fecha o diagnóstico. Estase jugular e múltiplas insuficiências valvares exigem internação e tratamento da insuficiência cardíaca.",
        "objetivos_aprendizagem": [
            "Aplicar critérios de Jones",
            "Avaliar cardite com ecocardiograma",
            "Instituir erradicação e profilaxia secundária",
        ],
        "criterios_seguranca": [
            {
                "nome": "Tratar congestão cardíaca",
                "termos": [
                    "diurético",
                    "diuretico",
                    "insuficiência cardíaca",
                    "insuficiencia cardiaca",
                    "internação",
                    "internacao",
                ],
                "feedback_omissao": "Cardite grave pode evoluir rapidamente com edema pulmonar, baixo débito e arritmia.",
            },
            {
                "nome": "Prevenir recorrência reumática",
                "termos": [
                    "profilaxia secundária",
                    "profilaxia secundaria",
                    "penicilina benzatina a cada",
                    "prevenir recorrência",
                    "prevenir recorrencia",
                ],
                "feedback_omissao": "Cada recorrência pode acrescentar dano valvar permanente.",
            },
        ],
        "desfechos_conduta": _outcomes(
            "Congestão e artrite melhoram, a inflamação cai e não surgem novas lesões valvares.",
            "O paciente recebe seguimento cardiológico e profilaxia para reduzir recorrências.",
            "A artrite melhora, mas congestão ou adesão à profilaxia permanecem inadequadas.",
            "A valvopatia progride e novas internações tornam-se prováveis.",
            "A insuficiência cardíaca não é tratada ou a profilaxia é omitida.",
            "Pode ocorrer edema pulmonar, arritmia, choque ou dano valvar progressivo irreversível.",
        ),
        "reacao_paciente_referencia": "Monitorar dispneia, edema, pressão de pulso, frequência, diurese, inflamação e função valvar.",
        "desfecho_referencia": "Controle da cardite e profilaxia secundária consistente são decisivos para preservar a função valvar.",
        "temas_estudo": [
            "Critérios de Jones",
            "Cardite reumática",
            "Profilaxia secundária",
        ],
        "fontes_clinicas": [RHEUMATIC_FEVER_SOURCE],
    },
}


FIFTH_FEEDBACK_BATCH_EXAM_UPDATES: dict[int, list[dict[str, Any]]] = {
    26: [
        {
            "id": "tc_cranio",
            "nome": "TC de crânio sem contraste",
            "resultado": "Sem hemorragia; discreta hipodensidade occipital direita, sem obstrução arterial diretamente visível.",
            "correto": True,
        },
        {
            "id": "angio_tc",
            "nome": "AngioTC de crânio e pescoço",
            "resultado": "Oclusão da artéria cerebral posterior direita, orientando avaliação de reperfusão.",
            "correto": True,
        },
        {
            "id": "glicemia_abc",
            "nome": "Glicemia capilar e avaliação ABC",
            "resultado": "Glicemia normal; via aérea protegida após a crise, com oxigenação preservada.",
            "correto": True,
        },
        {
            "id": "nihss_tempo",
            "nome": "Último momento bem e NIHSS",
            "resultado": "Déficit focal persistente, com horário de início dentro da janela de reperfusão.",
            "correto": True,
        },
        {
            "id": "rm_difusao",
            "nome": "RM de encéfalo com difusão",
            "resultado": "Restrição à difusão em território occipital e temporal medial direito.",
            "correto": True,
        },
        {
            "id": "ecg_laboratorio_avc",
            "nome": "ECG e laboratório para AVC",
            "resultado": "Sem contraindicação laboratorial imediata; investigação etiológica cardiovascular iniciada.",
            "correto": True,
        },
    ],
    27: [
        {
            "id": "albumina",
            "nome": "Albumina sérica",
            "resultado": "Reduzida, refletindo risco clínico e possível inflamação; não diagnostica nem quantifica desnutrição isoladamente.",
            "correto": True,
        },
        {
            "id": "endoscopia",
            "nome": "Endoscopia digestiva alta",
            "resultado": "Esôfago dilatado com retenção alimentar, sem tumor ou estenose mecânica; exame não quantifica motilidade.",
            "correto": True,
        },
        {
            "id": "avaliacao_nutricional",
            "nome": "Avaliação nutricional clínica completa",
            "resultado": "Perda de 16% do peso em 6 meses, baixa ingestão e perda muscular importante, compatíveis com desnutrição grave.",
            "correto": True,
        },
        {
            "id": "esofagograma",
            "nome": "Esofagograma contrastado",
            "resultado": "Megaesôfago com dilatação, retenção e esvaziamento distal muito lento.",
            "correto": True,
        },
        {
            "id": "avaliacao_degluticao",
            "nome": "Avaliação clínica/instrumental da deglutição",
            "resultado": "Alto risco de regurgitação e aspiração com sólidos e grandes volumes.",
            "correto": True,
        },
        {
            "id": "laboratorio_refeeding",
            "nome": "Eletrólitos e risco de realimentação",
            "resultado": "Fósforo e magnésio limítrofes, exigindo reposição e monitorização durante realimentação.",
            "correto": True,
        },
        {
            "id": "enema_opaco",
            "nome": "Imagem contrastada do cólon",
            "resultado": "Dilatação importante de sigmoide e reto, compatível com megacólon chagásico.",
            "correto": True,
        },
    ],
    28: [
        {
            "id": "anti_ttg",
            "nome": "Anti-transglutaminase tecidual IgA quantitativo",
            "resultado": "Positivo, 6 vezes o limite superior; requer interpretação com IgA total e confirmação histológica.",
            "correto": True,
        },
        {
            "id": "biopsia_duodeno",
            "nome": "Endoscopia com biópsias de bulbo e duodeno distal",
            "resultado": "Atrofia vilositária e hiperplasia de criptas compatíveis com doença celíaca.",
            "correto": True,
        },
        {
            "id": "hemo",
            "nome": "Hemograma",
            "resultado": "Anemia microcítica e hipocrômica, sugerindo deficiência de ferro.",
            "correto": True,
        },
        {
            "id": "iga_total",
            "nome": "IgA total",
            "resultado": "Normal para a idade, tornando o tTG-IgA interpretável.",
            "correto": True,
        },
        {
            "id": "hemo_ferritina",
            "nome": "Hemograma, ferritina e perfil de ferro",
            "resultado": "Anemia ferropriva com ferritina reduzida.",
            "correto": True,
        },
        {
            "id": "ema_segunda_amostra",
            "nome": "Antiendomísio IgA em segunda amostra",
            "resultado": "Positivo; como tTG-IgA é inferior a 10 vezes o limite, não dispensa biópsia.",
            "correto": True,
        },
    ],
    29: [
        {
            "id": "teste_rapido_strepto",
            "nome": "Teste rápido para Streptococcus do grupo A",
            "resultado": "Positivo, confirmando GAS no contexto clínico compatível.",
            "correto": True,
        },
        {
            "id": "cultura_orofaringe",
            "nome": "Cultura de orofaringe",
            "resultado": "Reservada para teste rápido negativo em criança sintomática; desnecessária após este teste positivo.",
            "correto": False,
        },
        {
            "id": "avaliacao_exantema",
            "nome": "Exame de pele e orofaringe",
            "resultado": "Exantema eritematoso áspero, linhas de Pastia e palidez perioral, além de língua em framboesa.",
            "correto": True,
        },
        {
            "id": "avaliacao_cardio_renal",
            "nome": "Avaliação cardiorrenal dos sinais de alarme",
            "resultado": "Taquicardia e edema exigem ECG/eco, oximetria, pressão, urina e função renal; sem choque na avaliação inicial.",
            "correto": True,
        },
    ],
    30: [
        {
            "id": "aslo",
            "nome": "ASLO",
            "resultado": "Título elevado, evidenciando contato estreptocócico recente; isoladamente não confirma febre reumática.",
            "correto": True,
        },
        {
            "id": "eco",
            "nome": "Ecocardiograma com Doppler",
            "resultado": "Cardite com regurgitação mitral e aórtica, congestão e disfunção ventricular; estenose mitral sugere dano reumático prévio.",
            "correto": True,
        },
        {
            "id": "vhs_pcr",
            "nome": "VHS e PCR",
            "resultado": "Elevados, preenchendo critério inflamatório menor e permitindo seguimento.",
            "correto": True,
        },
        {
            "id": "aslo_anti_dnase",
            "nome": "ASLO e anti-DNase B",
            "resultado": "Títulos elevados e em ascensão, documentando infecção recente por GAS.",
            "correto": True,
        },
        {
            "id": "ecg",
            "nome": "Eletrocardiograma",
            "resultado": "Intervalo PR prolongado, sem arritmia sustentada.",
            "correto": True,
        },
        {
            "id": "raiox_bnp_funcao_renal",
            "nome": "Radiografia, BNP e função renal",
            "resultado": "Cardiomegalia e congestão pulmonar, BNP elevado e função renal preservada.",
            "correto": True,
        },
    ],
}
