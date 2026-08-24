"""Segundo lote de rubricas estruturadas para casos clínicos legados."""

from typing import Any


def _source(title: str, organization: str, year: int, url: str) -> dict[str, Any]:
    return {
        "titulo": title,
        "organizacao": organization,
        "ano": year,
        "url": url,
    }


NICE_HMB_SOURCE = _source(
    "Heavy menstrual bleeding: assessment and management (NG88)",
    "National Institute for Health and Care Excellence",
    2018,
    "https://www.nice.org.uk/guidance/ng88/chapter/recommendations",
)


SECOND_FEEDBACK_BATCH_RUBRICS: dict[int, dict[str, Any]] = {
    2: {
        "diagnostico_referencia": "Hipertensão arterial mascarada com lesão de órgão-alvo cardíaca, renal e retiniana.",
        "diagnostico_termos": [
            "hipertensão mascarada",
            "hipertensao mascarada",
            "hipertensão arterial mascarada",
            "hipertensao arterial mascarada",
        ],
        "diagnostico_parcial": [
            "hipertensão arterial",
            "hipertensao arterial",
            "hipertensão sistêmica",
            "hipertensao sistemica",
        ],
        "exames_essenciais": ["mapa", "lab_renal", "urina_albumina", "risco_cv"],
        "exames_opcionais": ["ecg", "eco"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "mapa": "A MAPA confirma pressão elevada fora do consultório apesar da medida clínica normal, caracterizando hipertensão mascarada.",
            "lab_renal": "Creatinina, eletrólitos e glicemia avaliam lesão renal, fatores de risco e segurança do tratamento.",
            "urina_albumina": "A relação albumina/creatinina urinária pesquisa lesão renal mediada pela hipertensão.",
            "risco_cv": "Perfil lipídico e avaliação global de risco ajudam a definir intensidade terapêutica e prevenção cardiovascular.",
            "ecg": "O ECG já demonstra sobrecarga ventricular esquerda e contribui para documentar lesão de órgão-alvo.",
            "eco": "O ecocardiograma confirma hipertrofia ventricular esquerda, mas não substitui a confirmação da pressão fora do consultório.",
        },
        "conduta_criterios": [
            {
                "nome": "Reconhecer lesão de órgão-alvo e estratificar risco",
                "pontos": 8,
                "termos": [
                    "lesão de órgão-alvo",
                    "lesao de orgao-alvo",
                    "retinopatia hipertensiva",
                    "hipertrofia ventricular",
                    "risco cardiovascular",
                ],
            },
            {
                "nome": "Iniciar tratamento anti-hipertensivo individualizado",
                "pontos": 9,
                "termos": [
                    "iniciar anti-hipertensivo",
                    "iniciar antihipertensivo",
                    "tratamento farmacológico",
                    "tratamento farmacologico",
                    "bloqueador do receptor de angiotensina",
                    "inibidor da eca",
                    "bra",
                ],
            },
            {
                "nome": "Orientar mudanças sustentáveis de estilo de vida",
                "pontos": 5,
                "termos": [
                    "redução de sal",
                    "reducao de sal",
                    "atividade física",
                    "atividade fisica",
                    "perda de peso",
                    "mudança de estilo de vida",
                    "mudancas de estilo de vida",
                ],
            },
            {
                "nome": "Acompanhar pressão fora do consultório e função renal",
                "pontos": 8,
                "termos": [
                    "repetir mapa",
                    "monitorização residencial",
                    "monitorizacao residencial",
                    "mrpa",
                    "pressão domiciliar",
                    "pressao domiciliar",
                    "reavaliar função renal",
                    "reavaliar funcao renal",
                ],
            },
        ],
        "conduta_referencia": (
            "Explicar que a pressão normal no consultório não exclui hipertensão e integrar MAPA, retinopatia, "
            "hipertrofia ventricular e alteração renal na estratificação de risco. Iniciar mudanças de estilo de "
            "vida e tratamento anti-hipertensivo individualizado, com atenção à função renal e aos eletrólitos, "
            "e acompanhar a resposta com medidas domiciliares ou nova MAPA."
        ),
        "feedback_hipotese_parcial": "Você reconheceu hipertensão, mas faltou nomear o fenótipo mascarado: pressão normal no consultório e elevada na MAPA, já com lesão de órgão-alvo.",
        "feedback_hipotese_incorreta": "A MAPA média de 154/88 mmHg, apesar de PA de 110/70 mmHg no consultório, caracteriza hipertensão mascarada; retinopatia, hipertrofia ventricular e creatinina elevada indicam repercussão crônica.",
        "feedback_seguranca": "Não tranquilize a paciente apenas pela pressão de consultório. A lesão cardíaca, renal e retiniana exige tratamento e seguimento, com controle de função renal e eletrólitos.",
        "objetivos_aprendizagem": [
            "Reconhecer hipertensão mascarada pela MAPA",
            "Identificar lesão de órgão-alvo e estratificar risco cardiovascular",
            "Planejar tratamento e monitorização fora do consultório",
        ],
        "criterios_seguranca": [
            {
                "nome": "Não ignorar lesão de órgão-alvo",
                "termos": [
                    "lesão de órgão-alvo",
                    "lesao de orgao-alvo",
                    "retinopatia",
                    "hipertrofia ventricular",
                    "função renal",
                    "funcao renal",
                ],
                "feedback_omissao": "Ignorar retinopatia, hipertrofia ventricular e disfunção renal subestima o risco cardiovascular da paciente.",
            },
            {
                "nome": "Confirmar controle fora do consultório",
                "termos": [
                    "mapa",
                    "mrpa",
                    "pressão domiciliar",
                    "pressao domiciliar",
                    "monitorização residencial",
                    "monitorizacao residencial",
                ],
                "feedback_omissao": "Sem medidas fora do consultório, o controle da hipertensão mascarada não pode ser avaliado com segurança.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "A paciente compreende por que a pressão do consultório era enganosa e inicia controle domiciliar e tratamento sem sinais de hipotensão.",
                "desfecho": "O controle sustentado reduz progressão da lesão renal, da hipertrofia ventricular e do risco de AVC e eventos cardiovasculares.",
            },
            "parcial": {
                "reacao": "A cefaleia pode persistir e as medidas fora do consultório continuam elevadas, apesar de orientações incompletas.",
                "desfecho": "Sem ajuste terapêutico e seguimento objetivo, a lesão de órgão-alvo pode progredir silenciosamente.",
            },
            "insegura": {
                "reacao": "A paciente é falsamente tranquilizada pela PA de consultório enquanto mantém hipertensão ao longo do dia.",
                "desfecho": "A ausência de tratamento eleva o risco de piora renal, AVC e doença cardiovascular.",
            },
        },
        "reacao_paciente_referencia": "A resposta deve ser acompanhada por MAPA ou medidas domiciliares, sintomas, creatinina, potássio e tolerância ao tratamento.",
        "desfecho_referencia": "A meta é controlar a pressão dentro e fora do consultório e reduzir risco cardiovascular e progressão de lesão de órgão-alvo.",
        "temas_estudo": [
            "Fenótipos de hipertensão e MAPA",
            "Lesão de órgão-alvo na hipertensão",
            "Tratamento e monitorização da pressão arterial",
        ],
        "fontes_clinicas": [
            _source(
                "2024 ESC Guidelines for the management of elevated blood pressure and hypertension",
                "European Society of Cardiology",
                2024,
                "https://doi.org/10.1093/eurheartj/ehae178",
            )
        ],
    },
    5: {
        "diagnostico_referencia": "Sangramento uterino anormal associado a leiomiomas, com anemia ferropriva.",
        "diagnostico_termos": [
            "sangramento uterino anormal por leiomioma",
            "sangramento uterino anormal associado a leiomioma",
            "leiomioma uterino",
            "mioma uterino",
            "sangramento por mioma",
        ],
        "diagnostico_parcial": [
            "sangramento uterino anormal",
            "menorragia",
            "anemia ferropriva",
        ],
        "exames_essenciais": ["beta_hcg", "hemo", "ferritina", "usg_tv"],
        "exames_opcionais": ["biopsia_endometrio_indicada"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "beta_hcg": "Gestação deve ser excluída em pessoa em idade reprodutiva com sangramento uterino anormal.",
            "hemo": "O hemograma quantifica a anemia causada pelo sangramento intenso e ajuda a definir urgência e reposição.",
            "ferritina": "A ferritina avalia deficiência de ferro associada ao sangramento prolongado.",
            "usg_tv": "A ultrassonografia pélvica, preferencialmente transvaginal quando apropriada, é imagem de primeira linha para avaliar miomas e anatomia uterina.",
            "biopsia_endometrio_indicada": "A amostragem endometrial é indicada conforme risco e evolução, como sangramento persistente, falha terapêutica ou fatores de risco para patologia endometrial; não é automática para toda paciente jovem.",
        },
        "conduta_criterios": [
            {
                "nome": "Avaliar estabilidade e gravidade do sangramento",
                "pontos": 8,
                "termos": [
                    "estabilidade hemodinâmica",
                    "estabilidade hemodinamica",
                    "sinais vitais",
                    "choque",
                    "sangramento ativo",
                    "avaliar gravidade",
                ],
            },
            {
                "nome": "Controlar o sangramento conforme perfil clínico",
                "pontos": 8,
                "termos": [
                    "ácido tranexâmico",
                    "acido tranexamico",
                    "progestagênio",
                    "progestagenio",
                    "contraceptivo combinado",
                    "sistema intrauterino com levonorgestrel",
                    "siu-lng",
                ],
            },
            {
                "nome": "Tratar deficiência de ferro e anemia",
                "pontos": 6,
                "termos": [
                    "reposição de ferro",
                    "reposicao de ferro",
                    "ferro oral",
                    "ferro intravenoso",
                    "tratar anemia",
                ],
            },
            {
                "nome": "Individualizar tratamento do mioma e desejo reprodutivo",
                "pontos": 8,
                "termos": [
                    "desejo reprodutivo",
                    "preservar fertilidade",
                    "miomectomia",
                    "histeroscopia",
                    "encaminhar ginecologia",
                    "avaliação ginecológica",
                    "avaliacao ginecologica",
                ],
            },
        ],
        "conduta_referencia": (
            "Avaliar imediatamente estabilidade hemodinâmica e intensidade do sangramento, excluir gestação e "
            "quantificar anemia/deficiência de ferro. Controlar o sangramento com opção medicamentosa adequada "
            "às contraindicações e preferências, repor ferro e definir com a ginecologia o manejo do mioma "
            "conforme tamanho, localização, sintomas e desejo reprodutivo."
        ),
        "feedback_hipotese_parcial": "Você reconheceu o sangramento uterino anormal, mas faltou relacioná-lo ao útero aumentado e irregular compatível com leiomiomas e à anemia por perda crônica.",
        "feedback_hipotese_incorreta": "Sangramento intenso, dor pélvica e útero móvel, aumentado e irregular sugerem leiomioma como causa estrutural do sangramento uterino anormal.",
        "feedback_seguranca": "Antes de discutir tratamento definitivo, confirme estabilidade, exclua gestação e dimensione a anemia. Sangramento ativo com instabilidade exige atendimento urgente.",
        "objetivos_aprendizagem": [
            "Investigar sangramento uterino anormal com segurança",
            "Reconhecer leiomioma como causa estrutural",
            "Controlar sangramento e anemia preservando preferências reprodutivas",
        ],
        "criterios_seguranca": [
            {
                "nome": "Avaliar estabilidade hemodinâmica",
                "termos": [
                    "estabilidade hemodinâmica",
                    "estabilidade hemodinamica",
                    "sinais vitais",
                    "choque",
                ],
                "feedback_omissao": "Sangramento intenso pode causar instabilidade; sinais vitais e repercussão clínica devem vir antes do manejo eletivo.",
            },
            {
                "nome": "Excluir gestação",
                "termos": ["beta-hcg", "beta hcg", "gestação", "gestacao"],
                "feedback_omissao": "Não excluir gestação pode atrasar o reconhecimento de causas obstétricas potencialmente graves de sangramento.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "O fluxo começa a reduzir, a paciente permanece estável e recebe tratamento para a deficiência de ferro.",
                "desfecho": "Com controle do sangramento e plano individualizado para o mioma, a anemia melhora e o risco de novas perdas intensas diminui.",
            },
            "parcial": {
                "reacao": "O sangramento reduz pouco ou recorre, mantendo fadiga, dor e limitação funcional.",
                "desfecho": "Sem tratar anemia e causa estrutural, podem ocorrer novas consultas de urgência e piora da qualidade de vida.",
            },
            "insegura": {
                "reacao": "A perda sanguínea continua sem avaliação adequada de estabilidade ou de gestação.",
                "desfecho": "Há risco de anemia grave, síncope, instabilidade hemodinâmica e atraso de uma causa obstétrica.",
            },
        },
        "reacao_paciente_referencia": "Monitorar volume do sangramento, sinais vitais, sintomas de anemia, hemoglobina e resposta ao tratamento.",
        "desfecho_referencia": "O objetivo é controlar o sangramento, corrigir deficiência de ferro e oferecer manejo do mioma alinhado ao desejo reprodutivo.",
        "temas_estudo": [
            "Classificação e investigação do sangramento uterino anormal",
            "Leiomiomas e ultrassonografia de primeira linha",
            "Tratamento do sangramento e da deficiência de ferro",
        ],
        "fontes_clinicas": [NICE_HMB_SOURCE],
    },
    15: {
        "diagnostico_referencia": "Adenomiose sintomática com sangramento menstrual intenso, dor pélvica e anemia ferropriva.",
        "diagnostico_termos": [
            "adenomiose",
            "adenomiose uterina",
            "sangramento por adenomiose",
        ],
        "diagnostico_parcial": [
            "sangramento uterino anormal",
            "menorragia",
            "dismenorreia secundária",
            "dismenorreia secundaria",
        ],
        "exames_essenciais": ["beta_hcg", "hemo", "ferritina", "usg_tv_adenomiose"],
        "exames_opcionais": ["rm_pelvica"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "beta_hcg": "O teste de gestação integra a avaliação inicial de sangramento em idade reprodutiva.",
            "hemo": "A hemoglobina de 8,7 g/dL confirma anemia clinicamente relevante associada à perda menstrual.",
            "ferritina": "A ferritina documenta deficiência de ferro e orienta reposição.",
            "usg_tv_adenomiose": "A ultrassonografia transvaginal é a imagem de primeira linha quando há dismenorreia importante, útero aumentado e suspeita de adenomiose.",
            "rm_pelvica": "A ressonância pode esclarecer ou mapear achados quando a ultrassonografia é inconclusiva, mas não é obrigatória após ultrassom típico de boa qualidade.",
        },
        "conduta_criterios": [
            {
                "nome": "Tratar sangramento e dor com opção individualizada",
                "pontos": 10,
                "termos": [
                    "siu-lng",
                    "levonorgestrel",
                    "progestagênio",
                    "progestagenio",
                    "contraceptivo combinado",
                    "ácido tranexâmico",
                    "acido tranexamico",
                    "anti-inflamatório",
                    "anti-inflamatorio",
                ],
            },
            {
                "nome": "Corrigir anemia ferropriva",
                "pontos": 7,
                "termos": [
                    "reposição de ferro",
                    "reposicao de ferro",
                    "ferro oral",
                    "ferro intravenoso",
                    "tratar anemia",
                ],
            },
            {
                "nome": "Considerar preferências e fertilidade",
                "pontos": 6,
                "termos": [
                    "desejo reprodutivo",
                    "fertilidade",
                    "preferência da paciente",
                    "preferencia da paciente",
                    "decisão compartilhada",
                    "decisao compartilhada",
                ],
            },
            {
                "nome": "Encaminhar e reavaliar resposta ou gravidade",
                "pontos": 7,
                "termos": [
                    "encaminhar ginecologia",
                    "avaliação ginecológica",
                    "avaliacao ginecologica",
                    "reavaliar hemoglobina",
                    "histerectomia",
                    "falha do tratamento",
                ],
            },
        ],
        "conduta_referencia": (
            "Discutir tratamento do sangramento e da dor, priorizando opção hormonal compatível com preferências "
            "e contraindicações, frequentemente SIU com levonorgestrel, além de alternativas não hormonais. "
            "Corrigir a anemia ferropriva, considerar desejo reprodutivo e reavaliar sintomas e hemoglobina; "
            "encaminhar à ginecologia diante de anemia importante, falha terapêutica ou necessidade de procedimento."
        ),
        "feedback_hipotese_parcial": "Você reconheceu sangramento uterino e dismenorreia, mas faltou integrar o útero aumentado, os cistos miometriais e a textura heterogênea típicos de adenomiose.",
        "feedback_hipotese_incorreta": "Menorragia, cólica incapacitante, dispareunia e achados miometriais típicos na ultrassonografia sustentam adenomiose.",
        "feedback_seguranca": "A hemoglobina de 8,7 g/dL exige abordagem ativa da anemia e avaliação clínica; não deixe o tratamento da dor ocultar a repercussão do sangramento.",
        "objetivos_aprendizagem": [
            "Reconhecer apresentação e imagem da adenomiose",
            "Usar ultrassonografia como primeira linha e MRI de forma seletiva",
            "Tratar dor, sangramento e anemia com decisão compartilhada",
        ],
        "criterios_seguranca": [
            {
                "nome": "Abordar anemia clinicamente relevante",
                "termos": [
                    "reposição de ferro",
                    "reposicao de ferro",
                    "ferro oral",
                    "ferro intravenoso",
                    "tratar anemia",
                    "reavaliar hemoglobina",
                ],
                "feedback_omissao": "Com hemoglobina de 8,7 g/dL, omitir tratamento e seguimento da anemia mantém risco de piora sintomática.",
            },
            {
                "nome": "Considerar desejo reprodutivo",
                "termos": [
                    "desejo reprodutivo",
                    "fertilidade",
                    "preferência da paciente",
                    "preferencia da paciente",
                    "decisão compartilhada",
                    "decisao compartilhada",
                ],
                "feedback_omissao": "A escolha entre tratamento clínico e procedimento depende das preferências e dos planos reprodutivos.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "O sangramento e as cólicas diminuem progressivamente, enquanto a reposição de ferro melhora fadiga e tolerância aos esforços.",
                "desfecho": "O controle dos sintomas e da anemia preserva qualidade de vida e permite decidir com calma sobre terapias de longo prazo.",
            },
            "parcial": {
                "reacao": "A dor pode melhorar, mas o fluxo intenso e a fadiga persistem se anemia e preferências não forem abordadas.",
                "desfecho": "Persistência dos sintomas leva a novas perdas sanguíneas, piora funcional e necessidade de escalonamento do tratamento.",
            },
            "insegura": {
                "reacao": "A paciente mantém sangramento intenso, cansaço e possível tontura sem correção da anemia.",
                "desfecho": "A anemia pode se agravar e um procedimento incompatível com o desejo reprodutivo pode ser indicado sem decisão adequada.",
            },
        },
        "reacao_paciente_referencia": "Acompanhar sangramento, intensidade da dor, hemoglobina, ferritina, efeitos adversos e preferência da paciente.",
        "desfecho_referencia": "O tratamento busca reduzir dor e sangramento, corrigir anemia e respeitar planos reprodutivos.",
        "temas_estudo": [
            "Diagnóstico ultrassonográfico da adenomiose",
            "Tratamento clínico da dor e do sangramento",
            "Anemia ferropriva e decisão reprodutiva",
        ],
        "fontes_clinicas": [NICE_HMB_SOURCE],
    },
    16: {
        "diagnostico_referencia": "Síndrome de Turner 45,X com insuficiência ovariana hipergonadotrófica e puberdade incompleta.",
        "diagnostico_termos": [
            "síndrome de turner",
            "sindrome de turner",
            "monossomia x",
            "turner 45 x",
            "45,x",
        ],
        "diagnostico_parcial": [
            "insuficiência ovariana primária",
            "insuficiencia ovariana primaria",
            "hipogonadismo hipergonadotrófico",
            "hipogonadismo hipergonadotrofico",
            "amenorreia primária",
            "amenorreia primaria",
        ],
        "exames_essenciais": [
            "cariotipo",
            "hormonios",
            "imagem_cardio_aorta",
            "usg_renal",
            "tireoide_metabolico",
        ],
        "exames_opcionais": ["avaliacao_auditiva"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "cariotipo": "O cariótipo 45,X confirma a alteração cromossômica e orienta avaliação adicional quando houver material do cromossomo Y.",
            "hormonios": "FSH e LH elevados documentam insuficiência ovariana hipergonadotrófica.",
            "imagem_cardio_aorta": "Ecocardiograma e, conforme disponibilidade/idade, ressonância cardiovascular avaliam válvula aórtica, coarctação e dimensões da aorta, causas importantes de morbidade em Turner.",
            "usg_renal": "A ultrassonografia renal pesquisa malformações congênitas associadas.",
            "tireoide_metabolico": "TSH, função hepática, glicemia/HbA1c e lipídios rastreiam comorbidades frequentes e orientam tratamento hormonal seguro.",
            "avaliacao_auditiva": "A audiometria identifica perda auditiva, que pode ser silenciosa e progressiva.",
        },
        "conduta_criterios": [
            {
                "nome": "Iniciar reposição estrogênica e planejar progestagênio",
                "pontos": 9,
                "termos": [
                    "reposição estrogênica",
                    "reposicao estrogenica",
                    "estradiol",
                    "terapia hormonal",
                    "adicionar progesterona",
                    "adicionar progestagênio",
                    "adicionar progestagenio",
                ],
            },
            {
                "nome": "Realizar avaliação cardiovascular e da aorta",
                "pontos": 8,
                "termos": [
                    "ecocardiograma",
                    "ressonância cardíaca",
                    "ressonancia cardiaca",
                    "avaliar aorta",
                    "coarctação",
                    "coarctacao",
                    "válvula aórtica",
                    "valvula aortica",
                ],
            },
            {
                "nome": "Organizar seguimento multidisciplinar de comorbidades",
                "pontos": 7,
                "termos": [
                    "seguimento multidisciplinar",
                    "acompanhamento multidisciplinar",
                    "função tireoidiana",
                    "funcao tireoidiana",
                    "saúde óssea",
                    "saude ossea",
                    "audiometria",
                    "ultrassom renal",
                ],
            },
            {
                "nome": "Aconselhar fertilidade e risco gestacional",
                "pontos": 6,
                "termos": [
                    "aconselhamento reprodutivo",
                    "aconselhamento de fertilidade",
                    "fertilidade",
                    "risco gestacional",
                    "gestação de alto risco",
                    "gestacao de alto risco",
                ],
            },
        ],
        "conduta_referencia": (
            "Confirmar o cariótipo e iniciar reposição com estradiol sob endocrinologia/ginecologia, acrescentando "
            "progestagênio após exposição estrogênica adequada ou sangramento. Antes de gestação ou técnicas de "
            "reprodução, realizar avaliação cardiovascular detalhada da aorta. Organizar seguimento multidisciplinar "
            "com rastreio renal, tireoidiano, metabólico, ósseo e auditivo e aconselhamento sobre fertilidade."
        ),
        "feedback_hipotese_parcial": "Você identificou insuficiência ovariana, mas a associação de baixa estatura, puberdade incompleta, amenorreia primária e cariótipo 45,X define síndrome de Turner.",
        "feedback_hipotese_incorreta": "Baixa estatura, pouco desenvolvimento puberal, FSH/LH elevados e cariótipo 45,X confirmam síndrome de Turner com insuficiência ovariana.",
        "feedback_seguranca": "O diagnóstico não termina no cariótipo: alterações da aorta podem ser assintomáticas e tornar a gestação de alto risco. Avaliação cardiovascular deve preceder aconselhamento reprodutivo.",
        "objetivos_aprendizagem": [
            "Reconhecer Turner como causa de amenorreia primária",
            "Planejar reposição hormonal e proteção óssea/uterina",
            "Rastrear alterações cardiovasculares e comorbidades sistêmicas",
        ],
        "criterios_seguranca": [
            {
                "nome": "Avaliar aorta e cardiopatias associadas",
                "termos": [
                    "ecocardiograma",
                    "ressonância cardíaca",
                    "ressonancia cardiaca",
                    "avaliar aorta",
                    "coarctação",
                    "coarctacao",
                ],
                "feedback_omissao": "Aortopatia e cardiopatias congênitas podem ser silenciosas e aumentar risco de dissecção, especialmente na gestação.",
            },
            {
                "nome": "Evitar gestação sem estratificação especializada",
                "termos": [
                    "risco gestacional",
                    "gestação de alto risco",
                    "gestacao de alto risco",
                    "avaliação antes da gestação",
                    "avaliacao antes da gestacao",
                    "aconselhamento reprodutivo",
                ],
                "feedback_omissao": "Fertilidade assistida ou gestação não devem ser planejadas antes de avaliação cardiovascular e aconselhamento especializado.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "A paciente entende o diagnóstico, inicia reposição hormonal supervisionada e recebe um plano organizado para os diferentes sistemas afetados.",
                "desfecho": "O acompanhamento reduz perda óssea e risco cardiometabólico e permite decisões reprodutivas mais seguras.",
            },
            "parcial": {
                "reacao": "A amenorreia é tratada, mas riscos cardiovasculares ou outras comorbidades permanecem sem avaliação completa.",
                "desfecho": "O cuidado fragmentado pode atrasar o diagnóstico de aortopatia, hipertensão, tireoidopatia ou perda auditiva.",
            },
            "insegura": {
                "reacao": "A paciente recebe orientação reprodutiva ou hormonal sem avaliação cardiovascular e sistêmica adequada.",
                "desfecho": "Aortopatia não reconhecida pode representar risco grave, especialmente diante de uma futura gestação.",
            },
        },
        "reacao_paciente_referencia": "Acompanhar desenvolvimento sexual, sangramento uterino, pressão arterial, saúde óssea, metabolismo e achados cardiovasculares.",
        "desfecho_referencia": "O cuidado longitudinal multidisciplinar reduz morbidade e sustenta qualidade de vida e escolhas reprodutivas informadas.",
        "temas_estudo": [
            "Amenorreia primária e insuficiência ovariana",
            "Reposição hormonal na síndrome de Turner",
            "Vigilância cardiovascular e multissistêmica",
        ],
        "fontes_clinicas": [
            _source(
                "Clinical practice guidelines for the care of girls and women with Turner syndrome",
                "International Turner Syndrome Guideline Group",
                2024,
                "https://academic.oup.com/ejendo/article/190/6/G53/7674241",
            )
        ],
    },
    17: {
        "diagnostico_referencia": "Endometriose profunda sintomática, com dor pélvica crônica, dismenorreia e dispareunia profunda.",
        "diagnostico_termos": [
            "endometriose profunda",
            "endometriose pélvica",
            "endometriose pelvica",
            "endometriose",
        ],
        "diagnostico_parcial": [
            "dor pélvica crônica",
            "dor pelvica cronica",
            "dismenorreia secundária",
            "dismenorreia secundaria",
        ],
        "exames_essenciais": ["usg_tv_preparo"],
        "exames_opcionais": ["rm_mapeamento", "avaliacao_fertilidade"],
        "exames_desnecessarios": ["ca125"],
        "justificativa_exames": {
            "usg_tv_preparo": "Ultrassonografia transvaginal realizada por profissional experiente é exame de imagem de primeira linha e pode mapear doença profunda.",
            "rm_mapeamento": "A ressonância pode complementar o mapeamento de doença profunda ou esclarecer ultrassom inconclusivo, especialmente antes de cirurgia.",
            "avaliacao_fertilidade": "O desejo reprodutivo e eventual dificuldade para engravidar influenciam escolha entre tratamento hormonal, cirurgia e reprodução assistida.",
            "ca125": "CA-125 não deve ser usado para confirmar ou excluir endometriose por baixa acurácia e falta de especificidade.",
        },
        "conduta_criterios": [
            {
                "nome": "Controlar dor com tratamento clínico individualizado",
                "pontos": 9,
                "termos": [
                    "contraceptivo combinado",
                    "progestagênio",
                    "progestagenio",
                    "dienogeste",
                    "levonorgestrel",
                    "anti-inflamatório",
                    "anti-inflamatorio",
                    "analgesia",
                ],
            },
            {
                "nome": "Integrar preferências e desejo reprodutivo",
                "pontos": 7,
                "termos": [
                    "desejo reprodutivo",
                    "fertilidade",
                    "preferência da paciente",
                    "preferencia da paciente",
                    "decisão compartilhada",
                    "decisao compartilhada",
                ],
            },
            {
                "nome": "Encaminhar para cuidado ginecológico especializado",
                "pontos": 7,
                "termos": [
                    "encaminhar ginecologia",
                    "ginecologia especializada",
                    "ginecologista",
                    "centro especializado",
                    "equipe especializada",
                    "avaliação cirúrgica",
                    "avaliacao cirurgica",
                ],
            },
            {
                "nome": "Reavaliar resposta sem exigir laparoscopia rotineira",
                "pontos": 7,
                "termos": [
                    "tratamento empírico",
                    "tratamento empirico",
                    "reavaliar dor",
                    "reavaliar sintomas",
                    "laparoscopia se falha",
                    "imagem negativa",
                ],
            },
        ],
        "conduta_referencia": (
            "Explicar a hipótese de endometriose profunda e iniciar tratamento da dor individualizado, incluindo "
            "opção hormonal quando não houver contraindicação e quando gestação não for desejada de imediato. "
            "Considerar preferências e fertilidade, encaminhar para ginecologia especializada devido à dor intensa "
            "e doença profunda e reservar laparoscopia para imagem negativa com falha/inadequação do tratamento "
            "empírico ou quando houver indicação terapêutica."
        ),
        "feedback_hipotese_parcial": "Você reconheceu dor pélvica crônica, mas a combinação de dismenorreia progressiva, dispareunia profunda, nodulações e ultrassom positivo caracteriza endometriose profunda.",
        "feedback_hipotese_incorreta": "Dor cíclica progressiva, dispareunia profunda e nódulos no fundo de saco, associados a focos na ultrassonografia, sustentam endometriose profunda.",
        "feedback_seguranca": "CA-125 não confirma nem exclui a doença. Dor incapacitante e suspeita de acometimento profundo exigem plano terapêutico e encaminhamento, sem obrigar laparoscopia diagnóstica de rotina.",
        "objetivos_aprendizagem": [
            "Reconhecer endometriose pela história, exame e imagem",
            "Evitar biomarcadores de baixa acurácia e laparoscopia automática",
            "Individualizar tratamento conforme dor, fertilidade e preferência",
        ],
        "criterios_seguranca": [
            {
                "nome": "Não usar CA-125 como teste diagnóstico",
                "termos": [
                    "ca-125 não confirma",
                    "ca125 não confirma",
                    "ca-125 inespecífico",
                    "ca125 inespecífico",
                    "não solicitar ca-125",
                    "nao solicitar ca125",
                ],
                "feedback_omissao": "CA-125 tem desempenho insuficiente para confirmar ou excluir endometriose e pode gerar falsa segurança ou investigação desnecessária.",
            },
            {
                "nome": "Considerar desejo reprodutivo",
                "termos": [
                    "desejo reprodutivo",
                    "fertilidade",
                    "pretende engravidar",
                    "planejamento reprodutivo",
                ],
                "feedback_omissao": "Tratamento hormonal, cirurgia e estratégias de fertilidade dependem dos planos reprodutivos da paciente.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "A dor começa a reduzir, a paciente entende as opções e participa da escolha conforme seus planos reprodutivos.",
                "desfecho": "O seguimento especializado melhora controle da dor, função e planejamento de fertilidade, com cirurgia reservada a indicações claras.",
            },
            "parcial": {
                "reacao": "A analgesia alivia apenas parte dos sintomas e a incapacidade persiste sem plano hormonal ou especializado.",
                "desfecho": "A dor crônica pode continuar afetando estudo, trabalho, sexualidade e saúde emocional.",
            },
            "insegura": {
                "reacao": "A paciente permanece com dor 10/10 e pode receber falsa tranquilização por um biomarcador inespecífico.",
                "desfecho": "Atraso terapêutico favorece persistência da dor e decisões invasivas ou reprodutivas sem informação adequada.",
            },
        },
        "reacao_paciente_referencia": "Acompanhar intensidade e frequência da dor, função diária, tolerância ao tratamento e objetivos reprodutivos.",
        "desfecho_referencia": "O manejo busca controle sustentável da dor e qualidade de vida, preservando escolhas reprodutivas e evitando exames invasivos desnecessários.",
        "temas_estudo": [
            "Diagnóstico clínico e por imagem da endometriose",
            "Tratamento hormonal e analgesia",
            "Indicações de laparoscopia e planejamento de fertilidade",
        ],
        "fontes_clinicas": [
            _source(
                "ESHRE Guideline: Endometriosis",
                "European Society of Human Reproduction and Embryology",
                2022,
                "https://www.eshre.eu/guideline/endometriosis",
            )
        ],
    },
}


SECOND_FEEDBACK_BATCH_EXAM_UPDATES: dict[int, list[dict[str, Any]]] = {
    2: [
        {
            "id": "urina_albumina",
            "nome": "Relação albumina/creatinina urinária e urina tipo 1",
            "resultado": "Albuminúria moderadamente aumentada, compatível com lesão renal mediada pela hipertensão.",
            "correto": True,
        },
        {
            "id": "risco_cv",
            "nome": "Perfil lipídico e avaliação de risco cardiovascular",
            "resultado": "LDL-colesterol elevado; risco cardiovascular aumentado pela presença de lesão de órgão-alvo.",
            "correto": True,
        },
    ],
    5: [
        {
            "id": "usg_tv",
            "nome": "Ultrassonografia pélvica transvaginal",
            "resultado": "Útero aumentado e de contorno irregular, com múltiplos leiomiomas; exame de imagem de primeira linha neste contexto.",
            "correto": True,
        },
        {
            "id": "ferritina",
            "nome": "Ferritina sérica",
            "resultado": "Ferritina reduzida, confirmando deficiência de ferro associada à perda sanguínea.",
            "correto": True,
        },
        {
            "id": "biopsia_endometrio_indicada",
            "nome": "Amostragem endometrial se clinicamente indicada",
            "resultado": "Deve ser considerada conforme persistência, falha terapêutica e fatores de risco endometrial; não é automática para toda paciente de 37 anos.",
            "correto": True,
        },
    ],
    15: [
        {
            "id": "usg_tv_adenomiose",
            "nome": "Ultrassonografia transvaginal direcionada ao miométrio",
            "resultado": "Útero globoso e aumentado, miométrio heterogêneo e cistos miometriais, achados típicos de adenomiose.",
            "correto": True,
        },
        {
            "id": "rm_pelvica",
            "nome": "Ressonância magnética pélvica",
            "resultado": "Espessamento da zona juncional compatível com adenomiose; exame complementar quando o ultrassom é inconclusivo ou para melhor caracterização.",
            "correto": True,
        },
        {
            "id": "beta_hcg",
            "nome": "Beta-HCG",
            "resultado": "Negativo.",
            "correto": True,
        },
        {
            "id": "ferritina",
            "nome": "Ferritina sérica",
            "resultado": "Ferritina reduzida, compatível com deficiência de ferro.",
            "correto": True,
        },
    ],
    16: [
        {
            "id": "imagem_cardio_aorta",
            "nome": "Ecocardiograma e imagem da aorta",
            "resultado": "Válvula aórtica bicúspide sem estenose importante; avaliação da aorta necessária para estratificação e seguimento.",
            "correto": True,
        },
        {
            "id": "usg_renal",
            "nome": "Ultrassonografia renal",
            "resultado": "Rins sem obstrução; discreta alteração de rotação renal, sem repercussão funcional atual.",
            "correto": True,
        },
        {
            "id": "tireoide_metabolico",
            "nome": "Rastreio tireoidiano e metabólico",
            "resultado": "TSH discretamente elevado; glicemia, enzimas hepáticas e perfil lipídico disponíveis para seguimento.",
            "correto": True,
        },
        {
            "id": "avaliacao_auditiva",
            "nome": "Audiometria",
            "resultado": "Perda auditiva neurossensorial leve em altas frequências.",
            "correto": True,
        },
    ],
    17: [
        {
            "id": "ca125",
            "nome": "CA-125",
            "resultado": "Pode estar elevado, mas não possui acurácia suficiente para confirmar ou excluir endometriose.",
            "correto": False,
        },
        {
            "id": "rm_mapeamento",
            "nome": "Ressonância magnética pélvica para mapeamento",
            "resultado": "Pode complementar o mapeamento da doença profunda quando necessário ao planejamento terapêutico.",
            "correto": True,
        },
        {
            "id": "avaliacao_fertilidade",
            "nome": "Avaliação de objetivos reprodutivos e fertilidade",
            "resultado": "A paciente não deseja gestação imediata; aconselhamento reprodutivo deve integrar o plano de tratamento.",
            "correto": True,
        },
    ],
}
