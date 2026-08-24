"""Terceiro lote de rubricas estruturadas para casos clínicos legados."""

from typing import Any


def _source(title: str, organization: str, year: int, url: str) -> dict[str, Any]:
    return {
        "titulo": title,
        "organizacao": organization,
        "ano": year,
        "url": url,
    }


THIRD_FEEDBACK_BATCH_RUBRICS: dict[int, dict[str, Any]] = {
    1: {
        "diagnostico_referencia": "Massa mediastinal suspeita de recidiva metastática de seminoma, associada a dor torácica de padrão inflamatório/pericárdico.",
        "diagnostico_termos": [
            "recidiva de seminoma",
            "recorrência de seminoma",
            "recorrencia de seminoma",
            "metástase mediastinal de seminoma",
            "metastase mediastinal de seminoma",
            "massa mediastinal por tumor germinativo",
        ],
        "diagnostico_parcial": [
            "massa mediastinal",
            "tumor mediastinal",
            "pericardite",
            "dor torácica inflamatória",
            "dor toracica inflamatoria",
        ],
        "exames_essenciais": [
            "tc_torax",
            "marcadores_tumorais",
            "tc_abdome_pelve",
            "confirmacao_histologica",
        ],
        "exames_opcionais": ["ecg", "marcadores", "pcr", "eco_pericardio"],
        "exames_desnecessarios": ["pet_ct_rotina"],
        "justificativa_exames": {
            "tc_torax": "A tomografia caracteriza localização, extensão e relações da massa mediastinal e orienta a via mais segura para confirmação.",
            "marcadores_tumorais": "AFP, beta-hCG e LDH ajudam na classificação e no estadiamento, mas marcadores normais não excluem recidiva de seminoma.",
            "tc_abdome_pelve": "O estadiamento deve incluir abdome e pelve para pesquisar doença retroperitoneal ou visceral associada.",
            "confirmacao_histologica": "Uma nova massa tardia não deve ser rotulada definitivamente como recidiva sem revisão do histórico e confirmação tecidual quando indicada e segura.",
            "ecg": "ECG normal reduz a probabilidade de algumas causas cardíacas agudas, mas não exclui pericardite nem explica a massa.",
            "marcadores": "Troponina normal reduz suspeita de lesão miocárdica aguda, sem encerrar a investigação da dor ou da massa.",
            "pcr": "PCR elevada apoia inflamação, mas é inespecífica e não define a etiologia da massa.",
            "eco_pericardio": "Ecocardiograma é útil se houver suspeita de derrame, comprometimento pericárdico ou instabilidade.",
            "pet_ct_rotina": "PET/CT não substitui tomografia de estadiamento nem confirmação histológica e não é exame inicial rotineiro para toda suspeita de recidiva.",
        },
        "conduta_criterios": [
            {
                "nome": "Excluir causas torácicas imediatamente ameaçadoras",
                "pontos": 7,
                "termos": [
                    "avaliar estabilidade",
                    "sinais vitais",
                    "síndrome coronariana",
                    "sindrome coronariana",
                    "embolia pulmonar",
                    "dissecção de aorta",
                    "disseccao de aorta",
                ],
            },
            {
                "nome": "Estadiar a suspeita de recidiva",
                "pontos": 8,
                "termos": [
                    "afp",
                    "beta-hcg",
                    "beta hcg",
                    "ldh",
                    "tomografia de abdome",
                    "tc de abdome",
                    "estadiamento",
                ],
            },
            {
                "nome": "Obter confirmação diagnóstica especializada",
                "pontos": 8,
                "termos": [
                    "biópsia",
                    "biopsia",
                    "confirmação histológica",
                    "confirmacao histologica",
                    "oncologia",
                    "cirurgia torácica",
                    "cirurgia toracica",
                ],
            },
            {
                "nome": "Tratar sintomas sem atrasar investigação",
                "pontos": 7,
                "termos": [
                    "analgesia",
                    "anti-inflamatório",
                    "anti-inflamatorio",
                    "ecocardiograma",
                    "avaliar pericárdio",
                    "avaliar pericardio",
                    "seguimento urgente",
                ],
            },
        ],
        "conduta_referencia": (
            "Avaliar estabilidade e excluir causas imediatamente ameaçadoras de dor torácica. Caracterizar a massa "
            "com tomografia, dosar AFP, beta-hCG e LDH, completar estadiamento de abdome/pelve e revisar o tumor "
            "original. Encaminhar rapidamente à oncologia e cirurgia torácica para confirmação histológica segura "
            "e definição terapêutica. Avaliar pericárdio por ecocardiograma se houver suspeita de acometimento."
        ),
        "feedback_hipotese_parcial": "Você reconheceu a massa ou o padrão pericárdico da dor, mas faltou integrar o antecedente de seminoma e formular suspeita de recidiva que ainda exige confirmação.",
        "feedback_hipotese_incorreta": "A dor inflamatória merece investigação cardíaca, porém a massa mediastinal em paciente com seminoma prévio torna recidiva tumoral uma hipótese prioritária, sem dispensar diagnóstico tecidual.",
        "feedback_seguranca": "Não trate a PCR elevada como diagnóstico e não assuma que a massa é recidiva sem estadiamento e confirmação. Antes, exclua causas agudas de dor torácica e sinais de compressão mediastinal ou derrame pericárdico.",
        "objetivos_aprendizagem": [
            "Integrar antecedente oncológico ao diagnóstico diferencial da dor torácica",
            "Estadiar adequadamente suspeita de recidiva de tumor germinativo",
            "Evitar diagnóstico definitivo de massa mediastinal sem confirmação",
        ],
        "criterios_seguranca": [
            {
                "nome": "Excluir emergência torácica",
                "termos": [
                    "avaliar estabilidade",
                    "sinais vitais",
                    "síndrome coronariana",
                    "sindrome coronariana",
                    "embolia pulmonar",
                    "dissecção",
                    "disseccao",
                ],
                "feedback_omissao": "A presença de uma massa não elimina causas agudas e potencialmente fatais de dor torácica.",
            },
            {
                "nome": "Não presumir histologia da massa",
                "termos": [
                    "biópsia",
                    "biopsia",
                    "confirmação histológica",
                    "confirmacao histologica",
                    "confirmar diagnóstico",
                    "confirmar diagnostico",
                ],
                "feedback_omissao": "Uma massa mediastinal tardia pode ter diferentes etiologias; rotulá-la sem confirmação pode levar a tratamento incorreto.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "A dor é controlada, não surgem sinais de instabilidade e o paciente entende a necessidade de investigação oncológica rápida.",
                "desfecho": "O estadiamento e a confirmação tecidual permitem diferenciar recidiva de outro tumor mediastinal e iniciar tratamento específico sem atraso indevido.",
            },
            "parcial": {
                "reacao": "A dor melhora, mas a natureza e a extensão da massa permanecem indefinidas.",
                "desfecho": "Sem estadiamento ou confirmação, o diagnóstico pode atrasar e a massa pode progredir ou comprimir estruturas mediastinais.",
            },
            "insegura": {
                "reacao": "O paciente recebe falsa tranquilização ou tratamento empírico enquanto uma emergência ou progressão tumoral não é avaliada.",
                "desfecho": "Pode ocorrer atraso no reconhecimento de doença metastática, derrame pericárdico ou outra causa torácica grave.",
            },
        },
        "reacao_paciente_referencia": "Monitorar dor, sinais vitais, dispneia, sinais compressivos e achados pericárdicos enquanto o diagnóstico é definido.",
        "desfecho_referencia": "O prognóstico depende da etiologia e do estadiamento; recidivas de tumores germinativos ainda podem ser tratáveis com abordagem especializada.",
        "temas_estudo": [
            "Diagnóstico diferencial da dor torácica",
            "Massa mediastinal e confirmação histológica",
            "Recidiva e estadiamento do câncer de testículo",
        ],
        "fontes_clinicas": [
            _source(
                "EAU Guidelines on Testicular Cancer",
                "European Association of Urology",
                2025,
                "https://uroweb.org/guidelines/testicular-cancer/chapter/diagnostic-evaluation",
            )
        ],
    },
    3: {
        "diagnostico_referencia": "Amiloidose AL cardíaca associada a neoplasia de plasmócitos, com insuficiência cardíaca restritiva e anemia grave.",
        "diagnostico_termos": [
            "amiloidose al cardíaca",
            "amiloidose al cardiaca",
            "amiloidose cardíaca por cadeias leves",
            "amiloidose cardiaca por cadeias leves",
            "amiloidose cardíaca associada a mieloma",
            "amiloidose cardiaca associada a mieloma",
        ],
        "diagnostico_parcial": [
            "amiloidose cardíaca",
            "amiloidose cardiaca",
            "mieloma múltiplo",
            "mieloma multiplo",
            "cardiomiopatia restritiva",
        ],
        "exames_essenciais": [
            "imunofixacao_cadeias_leves",
            "biopsia_mo",
            "biopsia_amiloide",
            "biomarcadores_cardiorrenais",
        ],
        "exames_opcionais": ["hemo", "eletroforese", "eco", "ecg", "rm_cardiaca"],
        "exames_desnecessarios": ["cintilografia_isolada"],
        "justificativa_exames": {
            "imunofixacao_cadeias_leves": "Imunofixação sérica/urinária e cadeias leves livres detectam a proteína monoclonal e são essenciais para investigar amiloidose AL.",
            "biopsia_mo": "A medula quantifica o clone plasmocitário e permite caracterizar a discrasia associada.",
            "biopsia_amiloide": "Depósito de amiloide com tipagem por método validado confirma o diagnóstico e evita tratar AL apenas com base no pico monoclonal.",
            "biomarcadores_cardiorrenais": "Troponina, NT-proBNP, creatinina e proteinúria estadiam comprometimento cardíaco/renal e risco terapêutico.",
            "hemo": "Hemoglobina de 6,7 g/dL exige avaliação urgente e pode contribuir para dispneia e síncope.",
            "eletroforese": "O pico monoclonal sugere discrasia, mas a eletroforese isolada não caracteriza cadeias leves nem prova amiloidose AL.",
            "eco": "Padrão restritivo sustenta cardiomiopatia infiltrativa e ajuda a avaliar congestão e prognóstico.",
            "ecg": "Baixa voltagem discordante do espessamento cardíaco é uma pista de amiloidose.",
            "rm_cardiaca": "A ressonância auxilia na caracterização do padrão infiltrativo, mas não define sozinha o tipo de proteína amiloide.",
            "cintilografia_isolada": "Cintilografia positiva não deve estabelecer ATTR quando existe proteína monoclonal; amiloidose AL precisa ser excluída e o depósito tipado.",
        },
        "conduta_criterios": [
            {
                "nome": "Internar e estabilizar congestão/anemia",
                "pontos": 8,
                "termos": [
                    "internação",
                    "internacao",
                    "diurético",
                    "diuretico",
                    "avaliar transfusão",
                    "avaliar transfusao",
                    "concentrado de hemácias",
                    "concentrado de hemacias",
                ],
            },
            {
                "nome": "Confirmar e tipar a amiloidose",
                "pontos": 7,
                "termos": [
                    "vermelho congo",
                    "biópsia",
                    "biopsia",
                    "tipagem do amiloide",
                    "tipar amiloide",
                    "cadeias leves livres",
                ],
            },
            {
                "nome": "Encaminhar urgentemente à hematologia/cardio-oncologia",
                "pontos": 8,
                "termos": [
                    "hematologia",
                    "cardio-oncologia",
                    "cardiologia especializada",
                    "equipe multidisciplinar",
                    "tratamento do clone plasmocitário",
                    "tratamento do clone plasmocitario",
                ],
            },
            {
                "nome": "Planejar terapia do clone conforme risco",
                "pontos": 7,
                "termos": [
                    "daratumumabe",
                    "bortezomibe",
                    "quimioterapia",
                    "transplante autólogo",
                    "transplante autologo",
                    "estratificação cardíaca",
                    "estratificacao cardiaca",
                ],
            },
        ],
        "conduta_referencia": (
            "Internar pela insuficiência cardíaca, síncope e anemia grave; manejar congestão cuidadosamente e avaliar "
            "necessidade de transfusão conforme sintomas e estabilidade. Confirmar depósito e tipar a proteína, "
            "completar estudo monoclonal e estadiamento cardíaco/renal. Acionar hematologia e cardiologia especializada "
            "para terapia rápida do clone plasmocitário, individualizada pelo alto risco cardíaco."
        ),
        "feedback_hipotese_parcial": "Você reconheceu amiloidose ou mieloma, mas faltou ligar o pico monoclonal e a cardiomiopatia restritiva à amiloidose AL cardíaca, que exige confirmação e tipagem.",
        "feedback_hipotese_incorreta": "Insuficiência cardíaca restritiva, baixa voltagem, túnel do carpo, rouleaux e pico monoclonal tornam amiloidose AL associada a neoplasia plasmocitária a hipótese central.",
        "feedback_seguranca": "Não conclua ATTR por cintilografia isolada diante de componente monoclonal. Síncope, congestão e Hb 6,7 g/dL indicam alto risco e exigem avaliação hospitalar e especializada rápida.",
        "objetivos_aprendizagem": [
            "Reconhecer pistas cardíacas e hematológicas de amiloidose AL",
            "Confirmar e tipar o depósito amiloide",
            "Priorizar suporte e tratamento rápido do clone plasmocitário",
        ],
        "criterios_seguranca": [
            {
                "nome": "Reconhecer alto risco clínico",
                "termos": [
                    "internação",
                    "internacao",
                    "síncope",
                    "sincope",
                    "anemia grave",
                    "avaliar transfusão",
                    "avaliar transfusao",
                ],
                "feedback_omissao": "Síncope, insuficiência cardíaca e anemia grave podem deteriorar rapidamente e não devem ser conduzidas apenas ambulatorialmente.",
            },
            {
                "nome": "Confirmar AL antes de terapia específica",
                "termos": [
                    "tipagem do amiloide",
                    "tipar amiloide",
                    "vermelho congo",
                    "biópsia",
                    "biopsia",
                    "cadeias leves livres",
                ],
                "feedback_omissao": "Proteína monoclonal e imagem cardíaca sugerem AL, mas confirmação e tipagem evitam terapia específica incorreta.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "A congestão e a dispneia começam a reduzir sob monitorização, enquanto anemia e risco arrítmico são avaliados.",
                "desfecho": "A confirmação rápida permite iniciar tratamento do clone e limitar nova deposição amiloide, embora o comprometimento cardíaco determine o prognóstico.",
            },
            "parcial": {
                "reacao": "Há melhora incompleta da falta de ar, mas a produção de cadeias leves e o risco cardíaco permanecem ativos.",
                "desfecho": "Atraso na tipagem ou na hematologia favorece progressão da insuficiência cardíaca e perda de elegibilidade terapêutica.",
            },
            "insegura": {
                "reacao": "Congestão, síncope ou anemia podem piorar sem monitorização, e terapia dirigida ao tipo errado de amiloidose pode ser iniciada.",
                "desfecho": "Há risco de arritmia, choque, falência de órgãos e morte por atraso no tratamento da amiloidose AL.",
            },
        },
        "reacao_paciente_referencia": "Monitorar congestão, pressão, ritmo, síncope, hemoglobina, função renal, troponina e NT-proBNP.",
        "desfecho_referencia": "Resposta hematológica rápida e suporte cardíaco especializado são determinantes para estabilizar a doença.",
        "temas_estudo": [
            "Amiloidose AL e discrasias plasmocitárias",
            "Diagnóstico e tipagem da amiloidose cardíaca",
            "Manejo da insuficiência cardíaca restritiva",
        ],
        "fontes_clinicas": [
            _source(
                "Diagnosis and treatment of cardiac amyloidosis: a position statement of the ESC Working Group",
                "European Society of Cardiology",
                2021,
                "https://doi.org/10.1093/eurheartj/ehab072",
            )
        ],
    },
    4: {
        "diagnostico_referencia": "Miopericardite associada a lúpus eritematoso sistêmico ativo, com insuficiência cardíaca de fração de ejeção reduzida.",
        "diagnostico_termos": [
            "miocardite lúpica",
            "miocardite lupica",
            "miopericardite lúpica",
            "miopericardite lupica",
            "miocardite por lúpus",
            "miocardite por lupus",
        ],
        "diagnostico_parcial": [
            "lúpus eritematoso sistêmico",
            "lupus eritematoso sistemico",
            "insuficiência cardíaca com fração reduzida",
            "insuficiencia cardiaca com fracao reduzida",
            "pericardite lúpica",
            "pericardite lupica",
        ],
        "exames_essenciais": [
            "eco",
            "troponina_bnp",
            "rm_cardiaca",
            "atividade_les_renal",
            "investigacao_infecciosa",
        ],
        "exames_opcionais": ["les", "raiox", "hemo", "biopsia_endomiocardica_seletiva"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "eco": "O ecocardiograma documenta FEVE de 33%, derrame pericárdico, valvopatias e repercussão hemodinâmica.",
            "troponina_bnp": "Troponina avalia lesão miocárdica e BNP/NT-proBNP quantifica repercussão da insuficiência cardíaca.",
            "rm_cardiaca": "Ressonância cardíaca caracteriza edema e lesão não isquêmica e reforça o diagnóstico clínico de miocardite.",
            "atividade_les_renal": "Complemento, anti-DNA, urina, proteinúria e função renal avaliam atividade sistêmica e nefrite associada.",
            "investigacao_infecciosa": "Febre exige culturas e investigação guiada pelo contexto antes de intensificar imunossupressão.",
            "les": "FAN, anti-DNA e anti-Sm sustentam LES, mas devem ser integrados a manifestações clínicas e complemento.",
            "raiox": "Cardiomegalia apoia repercussão cardíaca, mas não define a causa.",
            "hemo": "Anemia importante exige investigação e influencia tolerância à insuficiência cardíaca.",
            "biopsia_endomiocardica_seletiva": "Biópsia é reservada para apresentações de alto risco ou diagnóstico incerto em que o resultado mude a terapia.",
        },
        "conduta_criterios": [
            {
                "nome": "Internar e monitorar insuficiência cardíaca/arrítmica",
                "pontos": 8,
                "termos": [
                    "internação",
                    "internacao",
                    "monitorização cardíaca",
                    "monitorizacao cardiaca",
                    "telemetria",
                    "monitorar arritmia",
                    "avaliar choque",
                ],
            },
            {
                "nome": "Tratar congestão e ICFER conforme tolerância",
                "pontos": 7,
                "termos": [
                    "diurético",
                    "diuretico",
                    "tratamento da insuficiência cardíaca",
                    "tratamento da insuficiencia cardiaca",
                    "terapia para icfer",
                    "oxigênio se hipoxemia",
                    "oxigenio se hipoxemia",
                ],
            },
            {
                "nome": "Excluir infecção antes de imunossupressão intensa",
                "pontos": 7,
                "termos": [
                    "excluir infecção",
                    "excluir infeccao",
                    "hemoculturas",
                    "culturas",
                    "investigação infecciosa",
                    "investigacao infecciosa",
                ],
            },
            {
                "nome": "Tratar LES grave com equipe especializada",
                "pontos": 8,
                "termos": [
                    "corticosteroide em alta dose",
                    "corticoide em alta dose",
                    "metilprednisolona",
                    "imunossupressão",
                    "imunossupressao",
                    "reumatologia",
                    "cardiologia",
                ],
            },
        ],
        "conduta_referencia": (
            "Internar, monitorar ritmo e perfusão e tratar congestão/ICFER conforme pressão e função renal. Realizar "
            "ressonância cardíaca e avaliar atividade sistêmica do LES. Como há febre, investigar infecção antes de "
            "imunossupressão intensa. Com miocardite lúpica grave sustentada, discutir prontamente corticosteroide em "
            "alta dose e agente imunossupressor com reumatologia e cardiologia."
        ),
        "feedback_hipotese_parcial": "Você reconheceu LES ou insuficiência cardíaca, mas faltou explicar a disfunção ventricular e o derrame como miopericardite lúpica ativa.",
        "feedback_hipotese_incorreta": "Febre, artralgias, eritema malar, autoanticorpos de LES, derrame pericárdico e FEVE de 33% sustentam miopericardite associada a LES ativo.",
        "feedback_seguranca": "Febre não deve ser automaticamente atribuída ao lúpus: infecção precisa ser investigada antes de imunossupressão intensa. FEVE de 33% e taquipneia exigem internação e vigilância de arritmia, choque e tamponamento.",
        "objetivos_aprendizagem": [
            "Reconhecer envolvimento miocárdico e pericárdico no LES",
            "Usar ressonância e biomarcadores para avaliar miocardite",
            "Equilibrar tratamento da ICFER, investigação infecciosa e imunossupressão",
        ],
        "criterios_seguranca": [
            {
                "nome": "Investigar infecção antes de intensificar imunossupressão",
                "termos": [
                    "excluir infecção",
                    "excluir infeccao",
                    "hemoculturas",
                    "culturas",
                    "investigação infecciosa",
                    "investigacao infecciosa",
                ],
                "feedback_omissao": "Imunossupressão em infecção não reconhecida pode provocar deterioração grave.",
            },
            {
                "nome": "Monitorar deterioração cardíaca",
                "termos": [
                    "internação",
                    "internacao",
                    "telemetria",
                    "monitorização cardíaca",
                    "monitorizacao cardiaca",
                    "avaliar choque",
                    "tamponamento",
                ],
                "feedback_omissao": "Disfunção ventricular e derrame podem evoluir com arritmia, choque ou tamponamento e exigem vigilância hospitalar.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Dispneia e congestão começam a reduzir, perfusão permanece estável e a atividade inflamatória é tratada após avaliação infecciosa.",
                "desfecho": "Controle precoce da inflamação e terapia cardíaca podem permitir recuperação parcial ou completa da função ventricular.",
            },
            "parcial": {
                "reacao": "Edema e dispneia melhoram pouco, enquanto inflamação ou causa infecciosa permanecem sem definição.",
                "desfecho": "Persistem risco de remodelamento ventricular, recorrência e internação prolongada.",
            },
            "insegura": {
                "reacao": "A paciente pode desenvolver piora respiratória, arritmia, hipotensão ou infecção agravada pela imunossupressão.",
                "desfecho": "O quadro pode evoluir para choque cardiogênico, tamponamento, sepse ou necessidade de terapia intensiva.",
            },
        },
        "reacao_paciente_referencia": "Monitorar dispneia, congestão, pressão, ritmo, troponina, função renal e tamanho do derrame.",
        "desfecho_referencia": "A recuperação depende do controle da inflamação, do suporte cardíaco e da exclusão de causas infecciosas ou alternativas.",
        "temas_estudo": [
            "Miocardite e pericardite no LES",
            "Ressonância cardíaca e estratificação de risco",
            "Imunossupressão e tratamento da ICFER",
        ],
        "fontes_clinicas": [
            _source(
                "2025 ESC Guidelines for the management of myocarditis and pericarditis",
                "European Society of Cardiology",
                2025,
                "https://doi.org/10.1093/eurheartj/ehaf192",
            ),
            _source(
                "2023 EULAR recommendations for the management of systemic lupus erythematosus",
                "European Alliance of Associations for Rheumatology",
                2023,
                "https://doi.org/10.1136/ard-2023-224762",
            ),
        ],
    },
    9: {
        "diagnostico_referencia": "Síndrome de Ramsay Hunt (herpes-zóster ótico com paralisia facial periférica e comprometimento vestibulococlear).",
        "diagnostico_termos": [
            "síndrome de ramsay hunt",
            "sindrome de ramsay hunt",
            "ramsay hunt",
            "herpes zóster ótico",
            "herpes zoster otico",
            "zoster oticus",
        ],
        "diagnostico_parcial": [
            "herpes zóster",
            "herpes zoster",
            "paralisia facial periférica",
            "paralisia facial periferica",
            "paralisia de bell",
        ],
        "exames_essenciais": ["clinico", "avaliacao_ocular_neurologica", "audiometria"],
        "exames_opcionais": ["pcr_vzv"],
        "exames_desnecessarios": ["rm_rotina_ramsay"],
        "justificativa_exames": {
            "clinico": "Otalgia/vesículas auriculares associadas a paralisia facial periférica definem o quadro clínico típico.",
            "avaliacao_ocular_neurologica": "Avaliar fechamento palpebral, córnea e exame neurológico identifica risco ocular e sinais que sugerem diagnóstico alternativo.",
            "audiometria": "Perda auditiva e vertigem exigem documentação da função auditiva/vestibular e acompanhamento otorrinolaringológico.",
            "pcr_vzv": "PCR de vesícula pode ajudar em apresentações atípicas ou sem erupção, mas não é necessária na tríade clássica.",
            "rm_rotina_ramsay": "Neuroimagem não é obrigatória na apresentação clássica; fica reservada a sinais centrais, evolução atípica ou dúvida diagnóstica.",
        },
        "conduta_criterios": [
            {
                "nome": "Iniciar antiviral prontamente",
                "pontos": 8,
                "termos": [
                    "aciclovir",
                    "valaciclovir",
                    "famciclovir",
                    "antiviral",
                    "sete dias",
                    "7 dias",
                ],
            },
            {
                "nome": "Associar corticosteroide após avaliar riscos",
                "pontos": 7,
                "termos": [
                    "prednisona",
                    "prednisolona",
                    "corticosteroide",
                    "corticoide",
                    "avaliar contraindicações",
                    "avaliar contraindicacoes",
                ],
            },
            {
                "nome": "Proteger o olho exposto",
                "pontos": 8,
                "termos": [
                    "lágrima artificial",
                    "lagrima artificial",
                    "lubrificação ocular",
                    "lubrificacao ocular",
                    "oclusão noturna",
                    "oclusao noturna",
                    "proteção ocular",
                    "protecao ocular",
                ],
            },
            {
                "nome": "Tratar sintomas e encaminhar otorrino",
                "pontos": 7,
                "termos": [
                    "analgesia",
                    "antiemético",
                    "antiemetico",
                    "vertigem",
                    "otorrinolaringologia",
                    "otorrino",
                    "audiometria",
                ],
            },
        ],
        "conduta_referencia": (
            "Iniciar antiviral o mais cedo possível e associar corticosteroide se não houver contraindicação, "
            "explicando que a evidência específica é limitada, mas o tratamento combinado é prática aceita. Proteger "
            "a córnea com lubrificação e oclusão noturna se o fechamento for incompleto, controlar dor/vertigem e "
            "encaminhar ao otorrino para avaliação auditiva e seguimento."
        ),
        "feedback_hipotese_parcial": "Você reconheceu zóster ou paralisia facial, mas faltou integrar vesículas auriculares, otalgia, vertigem e perda auditiva como síndrome de Ramsay Hunt.",
        "feedback_hipotese_incorreta": "Vesículas no pavilhão auditivo, paralisia facial ipsilateral, vertigem e hipoacusia formam o quadro clássico de herpes-zóster ótico/Ramsay Hunt.",
        "feedback_seguranca": "A prioridade prática é iniciar tratamento sem atraso e proteger a córnea se o olho não fechar. Em idosa com vertigem e perda auditiva, documente exame neurológico e encaminhe ao otorrino.",
        "objetivos_aprendizagem": [
            "Diferenciar Ramsay Hunt de paralisia de Bell",
            "Iniciar tratamento precoce e proteção ocular",
            "Avaliar comprometimento auditivo, vestibular e neurológico",
        ],
        "criterios_seguranca": [
            {
                "nome": "Proteger a córnea",
                "termos": [
                    "lágrima artificial",
                    "lagrima artificial",
                    "lubrificação ocular",
                    "lubrificacao ocular",
                    "oclusão noturna",
                    "oclusao noturna",
                    "proteção ocular",
                    "protecao ocular",
                ],
                "feedback_omissao": "Fechamento palpebral incompleto pode causar ceratite de exposição, ulceração e perda visual.",
            },
            {
                "nome": "Não atrasar antiviral",
                "termos": ["aciclovir", "valaciclovir", "famciclovir", "antiviral"],
                "feedback_omissao": "A chance de recuperação facial é maior quando o tratamento é iniciado precocemente.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "A dor e as novas vesículas diminuem, o olho permanece protegido e vertigem/náusea tornam-se mais controláveis.",
                "desfecho": "A recuperação facial ocorre ao longo de semanas ou meses; idade, vertigem e perda auditiva tornam o prognóstico mais reservado.",
            },
            "parcial": {
                "reacao": "As lesões melhoram, mas dor, fraqueza facial ou vertigem persistem por falta de medidas complementares.",
                "desfecho": "Há maior risco de recuperação facial incompleta, neuralgia e perda auditiva residual.",
            },
            "insegura": {
                "reacao": "A córnea resseca e a dor/vertigem pioram enquanto a replicação viral não é tratada adequadamente.",
                "desfecho": "Podem ocorrer lesão ocular, paralisia facial permanente e déficit auditivo/vestibular duradouro.",
            },
        },
        "reacao_paciente_referencia": "Acompanhar dor, fechamento ocular, força facial, surgimento de vesículas, audição e vertigem.",
        "desfecho_referencia": "Tratamento precoce e proteção ocular reduzem complicações, embora a recuperação possa ser incompleta em idosos.",
        "temas_estudo": [
            "Herpes-zóster ótico e nervos cranianos",
            "Tratamento da paralisia facial periférica",
            "Proteção ocular e avaliação auditiva",
        ],
        "fontes_clinicas": [
            _source(
                "Treatment and Prognosis of Facial Palsy on Ramsay Hunt Syndrome",
                "International Archives of Otorhinolaryngology",
                2016,
                "https://pmc.ncbi.nlm.nih.gov/articles/PMC5063726/",
            ),
            _source(
                "Corticosteroids as adjuvant to antiviral treatment in Ramsay Hunt syndrome",
                "Cochrane Ear, Nose and Throat Disorders Group",
                2008,
                "https://pubmed.ncbi.nlm.nih.gov/18646170/",
            ),
        ],
    },
    10: {
        "diagnostico_referencia": "Reação hansênica tipo 1 com neurite aguda, devendo excluir reação de hipersensibilidade à dapsona pela eosinofilia e hepatite.",
        "diagnostico_termos": [
            "reação hansênica tipo 1",
            "reacao hansenica tipo 1",
            "reação reversa com neurite",
            "reacao reversa com neurite",
            "neurite hansênica",
            "neurite hansenica",
        ],
        "diagnostico_parcial": [
            "reação hansênica",
            "reacao hansenica",
            "reação tipo 2",
            "reacao tipo 2",
            "eritema nodoso hansênico",
            "eritema nodoso hansenico",
            "dress por dapsona",
            "síndrome da dapsona",
            "sindrome da dapsona",
        ],
        "exames_essenciais": [
            "avaliacao_funcao_neural",
            "hemo",
            "funcao_hepatica",
            "revisao_medicamentos_renal",
        ],
        "exames_opcionais": [],
        "exames_desnecessarios": ["baciloscopia"],
        "justificativa_exames": {
            "avaliacao_funcao_neural": "Dor em nervos exige avaliação sensitiva, motora e autonômica documentada para detectar dano neural e acompanhar resposta.",
            "hemo": "Anemia e eosinofilia podem sinalizar toxicidade/hipersensibilidade medicamentosa, além da resposta inflamatória.",
            "funcao_hepatica": "Transaminases elevadas, febre e exantema após início da poliquimioterapia exigem excluir hepatite por fármaco e síndrome de hipersensibilidade à dapsona.",
            "revisao_medicamentos_renal": "Confirmar os componentes e datas da poliquimioterapia e avaliar função renal ajuda a diferenciar reação hansênica de evento adverso medicamentoso.",
            "baciloscopia": "Baciloscopia não confirma reação hansênica nem mede atividade aguda e não deve atrasar proteção da função neural.",
        },
        "conduta_criterios": [
            {
                "nome": "Avaliar e proteger função neural urgentemente",
                "pontos": 8,
                "termos": [
                    "avaliação neurológica simplificada",
                    "avaliacao neurologica simplificada",
                    "função neural",
                    "funcao neural",
                    "sensibilidade",
                    "força muscular",
                    "forca muscular",
                    "imobilizar membro",
                ],
            },
            {
                "nome": "Tratar neurite/reação tipo 1 com corticosteroide supervisionado",
                "pontos": 8,
                "termos": [
                    "prednisona",
                    "prednisolona",
                    "corticosteroide",
                    "corticoide",
                    "tratamento supervisionado",
                    "desmame gradual",
                ],
            },
            {
                "nome": "Excluir hipersensibilidade grave à dapsona",
                "pontos": 8,
                "termos": [
                    "hipersensibilidade à dapsona",
                    "hipersensibilidade a dapsona",
                    "síndrome da dapsona",
                    "sindrome da dapsona",
                    "dress",
                    "suspender dapsona",
                    "hepatite medicamentosa",
                ],
            },
            {
                "nome": "Manter cuidado especializado e ajustar PQT com segurança",
                "pontos": 6,
                "termos": [
                    "serviço de referência",
                    "servico de referencia",
                    "encaminhar dermatologia",
                    "encaminhamento urgente",
                    "manter poliquimioterapia",
                    "ajustar poliquimioterapia",
                    "pqt",
                ],
            },
        ],
        "conduta_referencia": (
            "Documentar imediatamente função sensitiva e motora dos nervos dolorosos e iniciar corticosteroide "
            "supervisionado para neurite/reação tipo 1, com proteção do membro e desmame orientado. Entretanto, "
            "febre, exantema, eosinofilia, anemia e transaminases elevadas após dois meses de PQT exigem avaliação "
            "urgente para hipersensibilidade à dapsona/DRESS; se suspeita forte, suspender o fármaco implicado e "
            "encaminhar ao serviço de referência. A PQT não deve ser interrompida automaticamente por reação hansênica, "
            "mas precisa ser ajustada se houver toxicidade medicamentosa."
        ),
        "feedback_hipotese_parcial": "Você reconheceu uma reação hansênica, mas faltou classificar a neurite e enfrentar a possibilidade de hipersensibilidade à dapsona sugerida por eosinofilia e hepatite.",
        "feedback_hipotese_incorreta": "Placas eritemoinfiltradas e nervos dolorosos durante tratamento de hanseníase dimorfa sugerem reação tipo 1 com neurite; eosinofilia e transaminases elevadas exigem excluir reação medicamentosa grave.",
        "feedback_seguranca": "Não use baciloscopia para decidir a urgência. Dano neural pode se tornar permanente, e febre com eosinofilia/hepatite após dapsona pode representar DRESS potencialmente fatal.",
        "objetivos_aprendizagem": [
            "Reconhecer e classificar reações hansênicas",
            "Avaliar neurite e prevenir incapacidade permanente",
            "Diferenciar reação hansênica de hipersensibilidade medicamentosa",
        ],
        "criterios_seguranca": [
            {
                "nome": "Proteger função neural",
                "termos": [
                    "função neural",
                    "funcao neural",
                    "sensibilidade",
                    "força muscular",
                    "forca muscular",
                    "prednisona",
                    "corticosteroide",
                ],
                "feedback_omissao": "Neurite não tratada precocemente pode causar perda sensitiva, motora e incapacidade permanente.",
            },
            {
                "nome": "Excluir DRESS/hipersensibilidade à dapsona",
                "termos": [
                    "hipersensibilidade à dapsona",
                    "hipersensibilidade a dapsona",
                    "síndrome da dapsona",
                    "sindrome da dapsona",
                    "dress",
                    "hepatite medicamentosa",
                ],
                "feedback_omissao": "Eosinofilia e lesão hepática com febre/exantema podem indicar reação medicamentosa sistêmica grave.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Dor e edema começam a reduzir, a função neural é preservada e a possível toxicidade medicamentosa é investigada sem atraso.",
                "desfecho": "O tratamento precoce reduz incapacidade; se houver hipersensibilidade, a retirada do fármaco e suporte evitam progressão sistêmica.",
            },
            "parcial": {
                "reacao": "As lesões cutâneas melhoram parcialmente, mas dor neural ou alterações laboratoriais persistem.",
                "desfecho": "Sem diferenciar reação imune de toxicidade, pode haver dano neural ou exposição continuada ao fármaco causador.",
            },
            "insegura": {
                "reacao": "A dor neural progride, surge perda de força/sensibilidade ou a hepatite/exantema piora.",
                "desfecho": "O paciente pode desenvolver incapacidade permanente ou reação medicamentosa sistêmica grave com falência hepática.",
            },
        },
        "reacao_paciente_referencia": "Acompanhar dor neural, força, sensibilidade, extensão das lesões, febre, hemograma, transaminases e função renal.",
        "desfecho_referencia": "A prioridade é preservar nervos e reconhecer precocemente toxicidade medicamentosa, mantendo tratamento da hanseníase com esquema seguro.",
        "temas_estudo": [
            "Reações hansênicas tipo 1 e tipo 2",
            "Neurite aguda e prevenção de incapacidades",
            "Dapsona, DRESS e hepatotoxicidade",
        ],
        "fontes_clinicas": [
            _source(
                "Protocolo Clínico e Diretrizes Terapêuticas da Hanseníase",
                "Ministério da Saúde do Brasil",
                2022,
                "https://www.gov.br/conitec/pt-br/midias/protocolos/20220818_pcdt_hanseniase.pdf",
            )
        ],
    },
}


THIRD_FEEDBACK_BATCH_EXAM_UPDATES: dict[int, list[dict[str, Any]]] = {
    1: [
        {
            "id": "marcadores_tumorais",
            "nome": "Marcadores de tumor germinativo (AFP, beta-hCG e LDH)",
            "resultado": "AFP normal, beta-hCG discretamente elevado e LDH elevado; resultados devem ser integrados à imagem e à histologia.",
            "correto": True,
        },
        {
            "id": "tc_abdome_pelve",
            "nome": "TC de abdome e pelve para estadiamento",
            "resultado": "Linfonodos retroperitoneais aumentados, reforçando suspeita de doença germinativa recorrente.",
            "correto": True,
        },
        {
            "id": "confirmacao_histologica",
            "nome": "Biópsia da massa em planejamento multidisciplinar",
            "resultado": "Amostra compatível com tumor germinativo seminomatoso recorrente.",
            "correto": True,
        },
        {
            "id": "eco_pericardio",
            "nome": "Ecocardiograma",
            "resultado": "Pequeno derrame pericárdico, sem sinais de tamponamento.",
            "correto": True,
        },
        {
            "id": "pet_ct_rotina",
            "nome": "PET/CT como primeiro exame isolado",
            "resultado": "Não substitui o estadiamento tomográfico e a confirmação histológica nesta apresentação.",
            "correto": False,
        },
    ],
    3: [
        {
            "id": "biopsia_mo",
            "nome": "Biópsia de medula óssea",
            "resultado": "Infiltração clonal por plasmócitos, compatível com neoplasia de células plasmocitárias.",
            "correto": True,
        },
        {
            "id": "imunofixacao_cadeias_leves",
            "nome": "Imunofixação sérica/urinária e cadeias leves livres",
            "resultado": "Componente monoclonal lambda e relação de cadeias leves livres muito alterada.",
            "correto": True,
        },
        {
            "id": "biopsia_amiloide",
            "nome": "Biópsia com pesquisa e tipagem de amiloide",
            "resultado": "Vermelho Congo positivo com birrefringência verde-maçã; tipagem compatível com amiloide AL lambda.",
            "correto": True,
        },
        {
            "id": "biomarcadores_cardiorrenais",
            "nome": "Troponina, NT-proBNP, função renal e proteinúria",
            "resultado": "NT-proBNP e troponina elevados, creatinina aumentada e proteinúria, indicando comprometimento multissistêmico de alto risco.",
            "correto": True,
        },
        {
            "id": "rm_cardiaca",
            "nome": "Ressonância magnética cardíaca",
            "resultado": "Realce tardio difuso e dificuldade de anular o miocárdio, padrão compatível com infiltração amiloide.",
            "correto": True,
        },
        {
            "id": "cintilografia_isolada",
            "nome": "Cintilografia óssea interpretada isoladamente",
            "resultado": "Não pode estabelecer ATTR na presença de proteína monoclonal sem excluir e tipar amiloidose AL.",
            "correto": False,
        },
    ],
    4: [
        {
            "id": "troponina_bnp",
            "nome": "Troponina e BNP/NT-proBNP",
            "resultado": "Troponina e NT-proBNP elevados, compatíveis com lesão miocárdica e insuficiência cardíaca.",
            "correto": True,
        },
        {
            "id": "rm_cardiaca",
            "nome": "Ressonância magnética cardíaca",
            "resultado": "Edema miocárdico e realce tardio não isquêmico, sustentando miocardite ativa.",
            "correto": True,
        },
        {
            "id": "atividade_les_renal",
            "nome": "Complemento, anti-DNA, urina e função renal",
            "resultado": "C3/C4 consumidos, anti-DNA elevado e proteinúria, indicando LES sistemicamente ativo com possível acometimento renal.",
            "correto": True,
        },
        {
            "id": "investigacao_infecciosa",
            "nome": "Investigação infecciosa dirigida",
            "resultado": "Hemoculturas sem crescimento e investigação inicial sem foco bacteriano, permitindo decisão imunossupressora mais segura.",
            "correto": True,
        },
        {
            "id": "biopsia_endomiocardica_seletiva",
            "nome": "Biópsia endomiocárdica se indicada por alto risco ou incerteza",
            "resultado": "Reservada para evolução fulminante, arritmia grave ou dúvida diagnóstica capaz de mudar a terapia.",
            "correto": True,
        },
    ],
    9: [
        {
            "id": "avaliacao_ocular_neurologica",
            "nome": "Exame neurológico e avaliação do fechamento ocular/córnea",
            "resultado": "Paralisia periférica completa da hemiface esquerda, fechamento palpebral incompleto e córnea ainda íntegra; sem déficit de membros.",
            "correto": True,
        },
        {
            "id": "audiometria",
            "nome": "Audiometria e avaliação vestibular",
            "resultado": "Perda auditiva neurossensorial esquerda e hipofunção vestibular ipsilateral.",
            "correto": True,
        },
        {
            "id": "pcr_vzv",
            "nome": "PCR para VZV em conteúdo vesicular",
            "resultado": "VZV detectado; exame opcional porque a apresentação clínica já é típica.",
            "correto": True,
        },
        {
            "id": "rm_rotina_ramsay",
            "nome": "RM de crânio de rotina",
            "resultado": "Não indicada inicialmente na apresentação clássica sem sinais neurológicos centrais.",
            "correto": False,
        },
    ],
    10: [
        {
            "id": "avaliacao_funcao_neural",
            "nome": "Avaliação neurológica simplificada",
            "resultado": "Dor e espessamento de nervos ulnar e fibular, com redução sensitiva e discreta perda de força nos territórios correspondentes.",
            "correto": True,
        },
        {
            "id": "revisao_medicamentos_renal",
            "nome": "Revisão da PQT, função renal e avaliação de reação medicamentosa",
            "resultado": "Sintomas iniciados após exposição à dapsona, com função renal preservada; conjunto exige excluir síndrome de hipersensibilidade/DRESS.",
            "correto": True,
        },
        {
            "id": "baciloscopia",
            "nome": "Baciloscopia de linfa para avaliar a reação",
            "resultado": "Não confirma nem classifica reação hansênica e não deve atrasar avaliação e tratamento da neurite.",
            "correto": False,
        },
    ],
}
