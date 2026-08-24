"""Quarto lote de rubricas estruturadas para casos clínicos legados."""

from typing import Any


def _source(title: str, organization: str, year: int, url: str) -> dict[str, Any]:
    return {
        "titulo": title,
        "organizacao": organization,
        "ano": year,
        "url": url,
    }


NICE_EPILEPSY_SOURCE = _source(
    "Epilepsies in children, young people and adults (NG217)",
    "National Institute for Health and Care Excellence",
    2022,
    "https://www.nice.org.uk/guidance/ng217",
)


FOURTH_FEEDBACK_BATCH_RUBRICS: dict[int, dict[str, Any]] = {
    13: {
        "diagnostico_referencia": "Colangite bacteriana aguda sobreposta à colangite esclerosante primária associada à retocolite ulcerativa.",
        "diagnostico_termos": [
            "colangite bacteriana aguda em colangite esclerosante primária",
            "colangite bacteriana aguda em colangite esclerosante primaria",
            "colangite aguda em colangite esclerosante primária",
            "colangite aguda em colangite esclerosante primaria",
            "colangite bacteriana em cep",
            "colangite esclerosante primária com colangite aguda",
            "colangite esclerosante primaria com colangite aguda",
        ],
        "diagnostico_parcial": [
            "colangite esclerosante primária",
            "colangite esclerosante primaria",
            "colangite aguda",
            "obstrução biliar",
            "obstrucao biliar",
        ],
        "exames_essenciais": [
            "funcao_hepatica",
            "hemoculturas_lactato",
            "usg_abdome",
            "colangio_rm",
        ],
        "exames_opcionais": ["cpre", "ca19_9_imagem_dominante"],
        "exames_desnecessarios": ["anticorpos"],
        "justificativa_exames": {
            "funcao_hepatica": "Padrão colestático, bilirrubina e função sintética ajudam a avaliar obstrução e gravidade hepática.",
            "hemoculturas_lactato": "Febre e calafrios exigem culturas, hemograma, função renal e lactato antes do antibiótico quando isso não atrasar o tratamento.",
            "usg_abdome": "Ultrassonografia avalia dilatação biliar, vesícula e outras causas de obstrução no atendimento agudo.",
            "colangio_rm": "Colangiorressonância é o exame diagnóstico não invasivo preferencial para mapear estenoses e dilatações da CEP.",
            "cpre": "CPRE é invasiva e deve ser dirigida principalmente à drenagem, dilatação/coleta de estenose relevante ou colangite que não melhora, não como exame diagnóstico inicial rotineiro.",
            "ca19_9_imagem_dominante": "Estenose nova ou dominante e piora clínica exigem investigação de colangiocarcinoma com imagem e amostragem; CA 19-9 isolado não confirma câncer.",
            "anticorpos": "p-ANCA não confirma CEP nem muda a conduta aguda e não deve substituir a imagem biliar.",
        },
        "conduta_criterios": [
            {
                "nome": "Reconhecer sepse e estabilizar",
                "pontos": 8,
                "termos": [
                    "avaliar sepse",
                    "sinais vitais",
                    "lactato",
                    "hemoculturas",
                    "reposição volêmica",
                    "reposicao volemica",
                    "monitorização",
                    "monitorizacao",
                ],
            },
            {
                "nome": "Iniciar antibiótico para colangite",
                "pontos": 7,
                "termos": [
                    "antibiótico",
                    "antibiotico",
                    "ceftriaxona",
                    "piperacilina",
                    "cobertura biliar",
                ],
            },
            {
                "nome": "Avaliar drenagem biliar urgente",
                "pontos": 8,
                "termos": [
                    "drenagem biliar",
                    "cpre terapêutica",
                    "cpre terapeutica",
                    "descompressão biliar",
                    "descompressao biliar",
                    "estenose dominante",
                ],
            },
            {
                "nome": "Organizar seguimento especializado da CEP",
                "pontos": 7,
                "termos": [
                    "hepatologia",
                    "transplante hepático",
                    "transplante hepatico",
                    "colangiocarcinoma",
                    "colonoscopia",
                    "retocolite",
                ],
            },
        ],
        "conduta_referencia": (
            "Internar, colher culturas e avaliar sepse, iniciar antibiótico com cobertura biliar e oferecer suporte "
            "hemodinâmico. Realizar ultrassom e colangiorressonância quando a estabilidade permitir. Acionar endoscopia "
            "para CPRE terapêutica e drenagem se houver obstrução relevante, instabilidade ou ausência de melhora. Após "
            "a fase aguda, manter seguimento com hepatologia para estenoses dominantes, colangiocarcinoma, doença "
            "inflamatória intestinal e eventual transplante."
        ),
        "feedback_hipotese_parcial": "Você reconheceu CEP ou colangite, mas faltou combinar febre, icterícia e piora recente como infecção biliar aguda sobreposta à doença crônica.",
        "feedback_hipotese_incorreta": "Retocolite, prurido crônico, colestase e estenoses multifocais sustentam CEP; febre, calafrios e piora da icterícia indicam colangite aguda associada.",
        "feedback_seguranca": "Não espere p-ANCA ou colangiorressonância para tratar sepse. Antibiótico e avaliação de drenagem são prioritários; CPRE diagnóstica rotineira expõe o paciente a risco sem benefício.",
        "objetivos_aprendizagem": [
            "Reconhecer CEP e colangite bacteriana sobreposta",
            "Diferenciar papel da colangiorressonância e da CPRE",
            "Planejar drenagem, seguimento oncológico e avaliação para transplante",
        ],
        "criterios_seguranca": [
            {
                "nome": "Tratar infecção biliar e sepse",
                "termos": [
                    "antibiótico",
                    "antibiotico",
                    "hemoculturas",
                    "avaliar sepse",
                    "lactato",
                ],
                "feedback_omissao": "Colangite pode evoluir rapidamente para bacteremia, choque e disfunção de órgãos.",
            },
            {
                "nome": "Avaliar necessidade de drenagem",
                "termos": [
                    "drenagem biliar",
                    "cpre terapêutica",
                    "cpre terapeutica",
                    "descompressão biliar",
                    "descompressao biliar",
                ],
                "feedback_omissao": "Antibiótico isolado pode falhar se uma estenose obstrutiva mantiver a infecção.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Febre e calafrios cedem, bilirrubina começa a cair e a perfusão permanece estável após antibiótico e drenagem quando indicada.",
                "desfecho": "A infecção é controlada e o paciente segue para vigilância de estenoses, colangiocarcinoma, colite e progressão hepática.",
            },
            "parcial": {
                "reacao": "Há melhora transitória da febre, mas icterícia e colestase persistem se a obstrução não for resolvida.",
                "desfecho": "Podem ocorrer recorrência da colangite, nova internação e progressão da doença hepática.",
            },
            "insegura": {
                "reacao": "A febre, hipotensão e alteração do estado mental podem surgir enquanto a via biliar permanece infectada e obstruída.",
                "desfecho": "A evolução pode ser para choque séptico, abscesso hepático, falência de órgãos ou morte.",
            },
        },
        "reacao_paciente_referencia": "Monitorar temperatura, perfusão, estado mental, diurese, bilirrubina, função renal e resposta à drenagem.",
        "desfecho_referencia": "Controlar a colangite é a prioridade imediata; a CEP exige seguimento longitudinal especializado e avaliação de complicações.",
        "temas_estudo": [
            "Diagnóstico e história natural da CEP",
            "Colangite aguda e drenagem biliar",
            "Colangiocarcinoma, DII e transplante hepático",
        ],
        "fontes_clinicas": [
            _source(
                "EASL Clinical Practice Guidelines on sclerosing cholangitis",
                "European Association for the Study of the Liver",
                2022,
                "https://www.journal-of-hepatology.eu/article/S0168-8278(22)00326-9/fulltext",
            )
        ],
    },
    20: {
        "diagnostico_referencia": "Síndrome do encarceramento por AVC isquêmico de ponte ventral secundário à oclusão da artéria basilar.",
        "diagnostico_termos": [
            "síndrome do encarceramento por oclusão da artéria basilar",
            "sindrome do encarceramento por oclusao da arteria basilar",
            "síndrome do encarceramento por oclusão basilar",
            "sindrome do encarceramento por oclusao basilar",
            "locked-in por trombose basilar",
            "locked in por trombose basilar",
            "infarto pontino ventral por artéria basilar",
            "infarto pontino ventral por arteria basilar",
        ],
        "diagnostico_parcial": [
            "síndrome do encarceramento",
            "sindrome do encarceramento",
            "locked-in syndrome",
            "trombose da artéria basilar",
            "trombose da arteria basilar",
            "avc de circulação posterior",
            "avc de circulacao posterior",
        ],
        "exames_essenciais": ["glicemia_abc", "tc_cranio", "angio_tc_basilar"],
        "exames_opcionais": ["angiografia", "rm_difusao", "ecg_laboratorio_avc"],
        "exames_desnecessarios": ["puncao_lombar"],
        "justificativa_exames": {
            "glicemia_abc": "Glicemia deve ser verificada imediatamente e via aérea/respiração avaliadas sem atrasar imagem e reperfusão.",
            "tc_cranio": "TC sem contraste exclui hemorragia, embora possa ser normal ou pouco sensível no início do infarto de fossa posterior.",
            "angio_tc_basilar": "AngioTC confirma oclusão basilar e deve ser obtida rapidamente para decidir trombectomia.",
            "angiografia": "Angiografia por cateter confirma a oclusão durante planejamento/tratamento endovascular, mas não deve atrasar a transferência.",
            "rm_difusao": "RM com difusão caracteriza infarto pontino quando disponível sem atrasar reperfusão.",
            "ecg_laboratorio_avc": "ECG, hemograma, coagulação, eletrólitos e função renal apoiam reperfusão e investigação etiológica.",
            "puncao_lombar": "Punção lombar não diagnostica infarto basilar e pode atrasar reperfusão; líquor hemorrágico neste contexto é um achado legado incoerente.",
        },
        "conduta_criterios": [
            {
                "nome": "Ativar protocolo de AVC e estabilizar ABC",
                "pontos": 8,
                "termos": [
                    "protocolo de avc",
                    "código avc",
                    "codigo avc",
                    "via aérea",
                    "via aerea",
                    "glicemia",
                    "monitorização",
                    "monitorizacao",
                ],
            },
            {
                "nome": "Avaliar trombectomia mecânica urgentemente",
                "pontos": 9,
                "termos": [
                    "trombectomia mecânica",
                    "trombectomia mecanica",
                    "tratamento endovascular",
                    "neurorradiologia intervencionista",
                    "transferência para centro de AVC",
                    "transferencia para centro de avc",
                ],
            },
            {
                "nome": "Avaliar trombólise intravenosa se elegível",
                "pontos": 6,
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
                "nome": "Preservar comunicação e prevenir complicações",
                "pontos": 7,
                "termos": [
                    "movimentos oculares verticais",
                    "comunicação ocular",
                    "comunicacao ocular",
                    "fisioterapia respiratória",
                    "fisioterapia respiratoria",
                    "prevenir broncoaspiração",
                    "prevenir broncoaspiracao",
                ],
            },
        ],
        "conduta_referencia": (
            "Ativar imediatamente protocolo de AVC, registrar último momento bem, estabilizar via aérea e verificar "
            "glicemia. Obter TC e angioTC sem atraso, discutir trombólise IV se elegível e transferir/acionar centro "
            "endovascular para trombectomia da oclusão basilar. Após reperfusão, manter terapia intensiva neurológica, "
            "prevenir broncoaspiração e trombose e estabelecer comunicação por movimentos oculares verticais."
        ),
        "feedback_hipotese_parcial": "Você reconheceu locked-in ou AVC posterior, mas faltou ligar tetraplegia, perda do olhar horizontal e consciência preservada à oclusão basilar com infarto pontino ventral.",
        "feedback_hipotese_incorreta": "Tetraplegia e paralisia facial com comunicação ocular vertical preservada caracterizam síndrome do encarceramento; a angiografia demonstra a causa basilar.",
        "feedback_seguranca": "Não confunda ausência de fala e movimento com coma. Punção lombar não tem papel e pode atrasar reperfusão; a prioridade é angioTC e avaliação imediata para trombectomia/trombólise.",
        "objetivos_aprendizagem": [
            "Reconhecer consciência preservada na síndrome do encarceramento",
            "Diagnosticar oclusão basilar com angiografia não invasiva rápida",
            "Priorizar reperfusão e comunicação assistida",
        ],
        "criterios_seguranca": [
            {
                "nome": "Não atrasar reperfusão",
                "termos": [
                    "trombectomia",
                    "tratamento endovascular",
                    "trombólise",
                    "trombolise",
                    "centro de avc",
                ],
                "feedback_omissao": "Oclusão basilar é uma emergência com alta mortalidade; atrasar reperfusão amplia o infarto pontino.",
            },
            {
                "nome": "Reconhecer consciência e comunicação",
                "termos": [
                    "consciência preservada",
                    "consciencia preservada",
                    "movimentos oculares verticais",
                    "comunicação ocular",
                    "comunicacao ocular",
                ],
                "feedback_omissao": "Presumir inconsciência pode privar o paciente de comunicação, consentimento e cuidado humanizado.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "A perfusão cerebral é restaurada quando possível, a consciência permanece reconhecida e a comunicação ocular é estabelecida.",
                "desfecho": "Reperfusão precoce pode reduzir incapacidade e mortalidade; reabilitação intensiva define a recuperação funcional subsequente.",
            },
            "parcial": {
                "reacao": "O paciente permanece estável, porém tetraplégico e sem via de comunicação organizada.",
                "desfecho": "Sem reperfusão ou prevenção completa de complicações, aumentam pneumonia, trombose, desnutrição e incapacidade permanente.",
            },
            "insegura": {
                "reacao": "A oclusão persiste, o infarto se amplia e respiração/proteção de via aérea podem deteriorar.",
                "desfecho": "Há risco elevado de coma, falência respiratória, síndrome locked-in permanente ou morte.",
            },
        },
        "reacao_paciente_referencia": "Monitorar consciência, movimentos oculares, respiração, deglutição, pressão e sinais de progressão do AVC.",
        "desfecho_referencia": "O prognóstico depende principalmente da rapidez da reperfusão, extensão do infarto e prevenção de complicações.",
        "temas_estudo": [
            "Síndrome do encarceramento e neuroanatomia da ponte",
            "Oclusão basilar e trombectomia",
            "Comunicação e reabilitação no AVC grave",
        ],
        "fontes_clinicas": [
            _source(
                "ESO-ESMINT guideline on acute management of basilar artery occlusion",
                "European Stroke Organisation and ESMINT",
                2024,
                "https://eso-stroke.org/guidelines/eso-guideline-directory/",
            )
        ],
    },
    23: {
        "diagnostico_referencia": "Síndrome de West (espasmos infantis com hipsarritmia e regressão/atraso do desenvolvimento).",
        "diagnostico_termos": [
            "síndrome de west",
            "sindrome de west",
            "espasmos infantis com hipsarritmia",
            "epileptic spasms syndrome",
        ],
        "diagnostico_parcial": [
            "espasmos infantis",
            "epilepsia infantil",
            "crises epilépticas",
            "crises epilepticas",
        ],
        "exames_essenciais": ["video_eeg_sono", "rm_encefalo", "avaliacao_etiologica"],
        "exames_opcionais": ["eeg"],
        "exames_desnecessarios": ["tc_cranio"],
        "justificativa_exames": {
            "video_eeg_sono": "Vídeo-EEG incluindo sono confirma espasmos e hipsarritmia, documenta resposta e não deve ser atrasado.",
            "rm_encefalo": "RM de encéfalo é a imagem preferencial para pesquisar malformações, lesões estruturais e esclerose tuberosa.",
            "avaliacao_etiologica": "Avaliação genética/metabólica e exame para sinais de esclerose tuberosa são guiados pela história, exame e RM.",
            "eeg": "O EEG mostra hipsarritmia, mas vídeo-EEG com sono oferece correlação eletroclínica mais completa.",
            "tc_cranio": "TC é menos sensível para etiologias estruturais e expõe o lactente à radiação; não é a imagem preferencial quando a RM está disponível.",
        },
        "conduta_criterios": [
            {
                "nome": "Encaminhar com urgência à neurologia pediátrica",
                "pontos": 7,
                "termos": [
                    "neurologia pediátrica",
                    "neurologia pediatrica",
                    "neuropediatria",
                    "tratamento urgente",
                    "internação",
                    "internacao",
                ],
            },
            {
                "nome": "Iniciar tratamento de primeira linha",
                "pontos": 9,
                "termos": [
                    "prednisolona em alta dose",
                    "prednisona em alta dose",
                    "acth",
                    "vigabatrina",
                    "tratamento hormonal",
                ],
            },
            {
                "nome": "Investigar esclerose tuberosa e etiologia",
                "pontos": 7,
                "termos": [
                    "esclerose tuberosa",
                    "ressonância de encéfalo",
                    "ressonancia de encefalo",
                    "teste genético",
                    "teste genetico",
                    "investigação metabólica",
                    "investigacao metabolica",
                ],
            },
            {
                "nome": "Confirmar resposta clínica e eletroencefalográfica",
                "pontos": 7,
                "termos": [
                    "repetir eeg",
                    "vídeo-eeg",
                    "video-eeg",
                    "cessação dos espasmos",
                    "cessacao dos espasmos",
                    "reavaliar em 14 dias",
                    "desenvolvimento",
                ],
            },
        ],
        "conduta_referencia": (
            "Encaminhar urgentemente à neuropediatria e obter vídeo-EEG com sono e RM sem atrasar tratamento. Na ausência "
            "de esclerose tuberosa, discutir terapia hormonal em alta dose associada a vigabatrina conforme protocolo; "
            "na esclerose tuberosa, vigabatrina é opção prioritária. Monitorar efeitos adversos e confirmar rapidamente "
            "cessação clínica e eletroencefalográfica, além de iniciar suporte ao desenvolvimento."
        ),
        "feedback_hipotese_parcial": "Você reconheceu espasmos infantis, mas faltou integrar crises em salvas ao despertar, atraso/regressão e hipsarritmia como síndrome de West.",
        "feedback_hipotese_incorreta": "Espasmos em salvas, hipotonia e atraso do desenvolvimento com hipsarritmia no EEG formam a tríade clássica da síndrome de West.",
        "feedback_seguranca": "Espasmos infantis são emergência neurológica do desenvolvimento. Não aguarde TC ou investigação etiológica completa para iniciar terapia e confirmar resposta por vídeo-EEG.",
        "objetivos_aprendizagem": [
            "Reconhecer espasmos infantis e hipsarritmia",
            "Selecionar RM e investigação etiológica apropriadas",
            "Iniciar tratamento precoce e documentar resposta",
        ],
        "criterios_seguranca": [
            {
                "nome": "Não atrasar tratamento específico",
                "termos": [
                    "prednisolona",
                    "prednisona",
                    "acth",
                    "vigabatrina",
                    "tratamento hormonal",
                ],
                "feedback_omissao": "Cada período sem controle dos espasmos pode agravar o impacto no desenvolvimento neuropsicomotor.",
            },
            {
                "nome": "Confirmar resposta com EEG",
                "termos": [
                    "repetir eeg",
                    "vídeo-eeg",
                    "video-eeg",
                    "cessação dos espasmos",
                    "cessacao dos espasmos",
                ],
                "feedback_omissao": "Redução aparente dos movimentos não garante resolução eletrográfica da hipsarritmia.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Os espasmos cessam e o vídeo-EEG mostra desaparecimento da hipsarritmia, com vigilância dos efeitos adversos.",
                "desfecho": "Controle rápido e tratamento etiológico oferecem a melhor chance de preservar desenvolvimento, embora o prognóstico dependa da causa.",
            },
            "parcial": {
                "reacao": "As crises diminuem, mas persistem espasmos sutis ou atividade eletrográfica anormal.",
                "desfecho": "A exposição epiléptica contínua pode ampliar atraso do desenvolvimento e exigir mudança rápida de terapia.",
            },
            "insegura": {
                "reacao": "As salvas continuam frequentes, a criança fica mais letárgica e perde novas habilidades.",
                "desfecho": "Atraso terapêutico aumenta risco de epilepsia refratária e prejuízo neuropsicomotor permanente.",
            },
        },
        "reacao_paciente_referencia": "Acompanhar número de salvas, vigília, alimentação, eventos adversos, vídeo-EEG e marcos do desenvolvimento.",
        "desfecho_referencia": "O objetivo é cessar rapidamente espasmos e hipsarritmia e tratar a etiologia quando identificada.",
        "temas_estudo": [
            "Espasmos infantis e hipsarritmia",
            "Terapia hormonal e vigabatrina",
            "Etiologias estruturais, genéticas e metabólicas",
        ],
        "fontes_clinicas": [NICE_EPILEPSY_SOURCE],
    },
    24: {
        "diagnostico_referencia": "Migrânea com aura de linguagem, após exclusão de AVC/TIA e outras causas secundárias de déficit focal.",
        "diagnostico_termos": [
            "migrânea com aura de linguagem",
            "migranea com aura de linguagem",
            "enxaqueca com aura afásica",
            "enxaqueca com aura afasica",
            "migrânea com aura",
            "migranea com aura",
            "enxaqueca com aura",
        ],
        "diagnostico_parcial": [
            "migrânea",
            "migranea",
            "enxaqueca",
            "avc isquêmico",
            "avc isquemico",
            "ataque isquêmico transitório",
            "ataque isquemico transitorio",
        ],
        "exames_essenciais": ["avaliacao_tempo_neuro_glicemia", "tc_cranio"],
        "exames_opcionais": ["angio_rm_se_atipica", "clinico"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "avaliacao_tempo_neuro_glicemia": "Déficit de linguagem exige horário de início, exame neurológico seriado e glicemia para distinguir aura típica de AVC e mimetizadores.",
            "tc_cranio": "Na primeira apresentação focal intensa, TC ajuda a excluir hemorragia; resultado normal não exclui isquemia inicial.",
            "angio_rm_se_atipica": "AngioTC/RM é indicada se início súbito, aura prolongada ou atípica, déficit persistente ou dúvida com AVC/TIA.",
            "clinico": "Aura típica evolui gradualmente, é totalmente reversível e dura 5–60 minutos; esses detalhes são essenciais ao diagnóstico clínico.",
        },
        "conduta_criterios": [
            {
                "nome": "Excluir AVC antes de rotular aura",
                "pontos": 8,
                "termos": [
                    "protocolo de avc",
                    "excluir avc",
                    "início súbito",
                    "inicio subito",
                    "tempo de início",
                    "tempo de inicio",
                    "déficit persistente",
                    "deficit persistente",
                ],
            },
            {
                "nome": "Tratar crise de migrânea",
                "pontos": 7,
                "termos": [
                    "triptano",
                    "sumatriptana",
                    "anti-inflamatório",
                    "anti-inflamatorio",
                    "naproxeno",
                    "antiemético",
                    "antiemetico",
                ],
            },
            {
                "nome": "Suspender contraceptivo combinado com estrogênio",
                "pontos": 8,
                "termos": [
                    "suspender contraceptivo combinado",
                    "suspender aco combinado",
                    "evitar estrogênio",
                    "evitar estrogenio",
                    "método sem estrogênio",
                    "metodo sem estrogenio",
                    "progestagênio isolado",
                    "progestagenio isolado",
                ],
            },
            {
                "nome": "Orientar diário, prevenção e sinais de alarme",
                "pontos": 7,
                "termos": [
                    "diário de cefaleia",
                    "diario de cefaleia",
                    "sinais de alarme",
                    "retornar se déficit",
                    "retornar se deficit",
                    "tratamento preventivo",
                    "neurologia",
                ],
            },
        ],
        "conduta_referencia": (
            "Tratar inicialmente como possível evento vascular até confirmar aura gradual, reversível e com exame "
            "normal após resolução. Excluir hemorragia/isquemia conforme tempo e características; depois oferecer "
            "tratamento agudo da migrânea. Suspender contraceptivo combinado com estrogênio e discutir método sem "
            "estrogênio, pois migrânea com aura torna o combinado contraindicado. Orientar diário, prevenção e retorno "
            "imediato se déficit persistir ou mudar de padrão."
        ),
        "feedback_hipotese_parcial": "Você reconheceu migrânea ou AVC, mas faltou explicar que afasia reversível pode ser aura de linguagem somente após excluir evento vascular e confirmar evolução típica.",
        "feedback_hipotese_incorreta": "Cefaleia pulsátil com náuseas e déficit de linguagem reversível pode representar migrânea com aura, mas o diagnóstico requer cronologia típica e exclusão de AVC na apresentação focal.",
        "feedback_seguranca": "Afasia não deve ser automaticamente atribuída à migrânea. Além disso, contraceptivo combinado com estrogênio é contraindicado na migrânea com aura devido ao risco vascular.",
        "objetivos_aprendizagem": [
            "Distinguir aura de linguagem de AVC/TIA",
            "Tratar a crise após avaliação de segurança",
            "Rever contracepção combinada em migrânea com aura",
        ],
        "criterios_seguranca": [
            {
                "nome": "Excluir evento vascular",
                "termos": [
                    "excluir avc",
                    "protocolo de avc",
                    "tempo de início",
                    "tempo de inicio",
                    "déficit persistente",
                    "deficit persistente",
                ],
                "feedback_omissao": "Rotular afasia como aura sem avaliar AVC pode perder uma janela de reperfusão.",
            },
            {
                "nome": "Evitar estrogênio combinado",
                "termos": [
                    "suspender contraceptivo combinado",
                    "suspender aco combinado",
                    "evitar estrogênio",
                    "evitar estrogenio",
                    "método sem estrogênio",
                    "metodo sem estrogenio",
                ],
                "feedback_omissao": "Migrânea com aura e contracepção combinada somam risco de AVC isquêmico.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "A afasia regride completamente, a dor e a náusea melhoram e nenhum déficit focal permanece.",
                "desfecho": "A paciente recebe plano para crises e prevenção, além de contracepção mais segura sem estrogênio.",
            },
            "parcial": {
                "reacao": "A dor melhora, mas permanece insegurança sobre a natureza do déficit ou sobre o contraceptivo atual.",
                "desfecho": "Novas crises podem gerar repetidas urgências e o risco vascular evitável permanece.",
            },
            "insegura": {
                "reacao": "Um déficit vascular pode persistir enquanto é tratado como migrânea, ou a paciente continua exposta ao estrogênio.",
                "desfecho": "Há risco de atraso em AVC e de evento isquêmico futuro potencialmente incapacitante.",
            },
        },
        "reacao_paciente_referencia": "Monitorar resolução completa da afasia, exame neurológico, intensidade da dor, vômitos e surgimento de novos déficits.",
        "desfecho_referencia": "Aura típica é reversível; qualquer déficit persistente ou atípico exige reavaliação vascular imediata.",
        "temas_estudo": [
            "Critérios de migrânea com aura",
            "Diferencial entre aura, TIA e AVC",
            "Contracepção segura em migrânea com aura",
        ],
        "fontes_clinicas": [
            _source(
                "Headaches in over 12s: diagnosis and management",
                "National Institute for Health and Care Excellence",
                2012,
                "https://www.nice.org.uk/guidance/cg150/chapter/recommendations",
            ),
            _source(
                "U.S. Medical Eligibility Criteria for Contraceptive Use, 2024",
                "Centers for Disease Control and Prevention",
                2024,
                "https://www.cdc.gov/contraception/hcp/usmec/combined-hormonal-contraceptives.html",
            ),
        ],
    },
    25: {
        "diagnostico_referencia": "Estado de mal epiléptico convulsivo generalizado.",
        "diagnostico_termos": [
            "estado de mal epiléptico convulsivo",
            "estado de mal epileptico convulsivo",
            "status epilepticus convulsivo",
            "estado de mal epiléptico",
            "estado de mal epileptico",
            "status epilepticus",
        ],
        "diagnostico_parcial": [
            "crise tônico-clônica generalizada",
            "crise tonico-clonica generalizada",
            "crise convulsiva prolongada",
            "epilepsia descompensada",
        ],
        "exames_essenciais": ["glicemia_capilar", "laboratorio_causa_status"],
        "exames_opcionais": ["eeg", "tc_pos_estabilizacao", "nivel_anticonvulsivante"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "glicemia_capilar": "Glicemia é verificada imediatamente e hipoglicemia tratada, mas o resultado não deve atrasar benzodiazepínico.",
            "laboratorio_causa_status": "Eletrólitos, cálcio, magnésio, função renal/hepática, hemograma e investigação infecciosa/toxicológica guiada procuram causas reversíveis.",
            "eeg": "EEG é essencial se não houver recuperação da consciência ou houver suspeita de estado não convulsivo, mas não deve atrasar tratamento inicial.",
            "tc_pos_estabilizacao": "TC é realizada após estabilização quando há déficit focal, trauma, primeira crise, imunossupressão ou suspeita estrutural.",
            "nivel_anticonvulsivante": "Nível sérico pode identificar baixa adesão/subdose de alguns fármacos, sem atrasar as medicações de emergência.",
        },
        "conduta_criterios": [
            {
                "nome": "Estabilizar ABC e tratar causas imediatas",
                "pontos": 8,
                "termos": [
                    "via aérea",
                    "via aerea",
                    "oxigênio",
                    "oxigenio",
                    "monitorização",
                    "monitorizacao",
                    "acesso venoso",
                    "glicemia",
                    "tiamina",
                ],
            },
            {
                "nome": "Administrar benzodiazepínico em dose adequada",
                "pontos": 8,
                "termos": [
                    "lorazepam",
                    "midazolam",
                    "diazepam",
                    "benzodiazepínico",
                    "benzodiazepinico",
                ],
            },
            {
                "nome": "Administrar segunda linha rapidamente",
                "pontos": 7,
                "termos": [
                    "levetiracetam",
                    "fosfenitoína",
                    "fosfenitoina",
                    "fenitoína",
                    "fenitoina",
                    "valproato",
                ],
            },
            {
                "nome": "Tratar estado refratário em UTI com EEG",
                "pontos": 7,
                "termos": [
                    "estado refratário",
                    "estado refratario",
                    "intubação",
                    "intubacao",
                    "anestésico contínuo",
                    "anestesico continuo",
                    "eeg contínuo",
                    "eeg continuo",
                    "uti",
                ],
            },
        ],
        "conduta_referencia": (
            "Iniciar cronômetro e estabilização ABC, oxigênio/ventilação conforme necessidade, monitorização, acesso "
            "venoso e glicemia. Administrar benzodiazepínico em dose plena imediatamente; se a crise persistir, carregar "
            "levetiracetam, fosfenitoína/fenitoína ou valproato conforme contraindicações. Investigar e tratar a causa "
            "sem atrasar anticonvulsivantes. Se refratário, intubar, transferir à UTI, usar anestésico contínuo e EEG."
        ),
        "feedback_hipotese_parcial": "Você reconheceu uma convulsão, mas duração acima de 5 minutos — neste caso, mais de 20 — define estado de mal e exige algoritmo imediato em etapas.",
        "feedback_hipotese_incorreta": "Abalos bilaterais com perda de consciência contínuos por mais de 20 minutos caracterizam estado de mal epiléptico convulsivo.",
        "feedback_seguranca": "Não aguarde EEG, TC ou exames laboratoriais para administrar benzodiazepínico. Subdose e demora são causas frequentes de falha; depressão respiratória também decorre do próprio estado de mal não tratado.",
        "objetivos_aprendizagem": [
            "Reconhecer estado de mal a partir de 5 minutos",
            "Executar tratamento em fases sem atrasos",
            "Investigar causas e manejar refratariedade com EEG/UTI",
        ],
        "criterios_seguranca": [
            {
                "nome": "Administrar benzodiazepínico sem atraso",
                "termos": [
                    "lorazepam",
                    "midazolam",
                    "diazepam",
                    "benzodiazepínico",
                    "benzodiazepinico",
                ],
                "feedback_omissao": "Cada minuto de crise prolongada reduz a chance de resposta e aumenta lesão neuronal e complicações sistêmicas.",
            },
            {
                "nome": "Proteger ventilação e preparar refratariedade",
                "termos": [
                    "via aérea",
                    "via aerea",
                    "ventilação",
                    "ventilacao",
                    "intubação",
                    "intubacao",
                    "uti",
                ],
                "feedback_omissao": "Estado de mal e sedativos podem comprometer ventilação; suporte de via aérea deve acompanhar o tratamento.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Os abalos cessam, oxigenação e circulação se estabilizam e a paciente começa a recuperar a consciência sob monitorização.",
                "desfecho": "Com término precoce da crise e tratamento da causa, reduz-se o risco de lesão neurológica, aspiração, rabdomiólise e morte.",
            },
            "parcial": {
                "reacao": "A crise cessa tardiamente ou recorre porque a segunda linha e a investigação causal foram incompletas.",
                "desfecho": "A internação se prolonga e cresce o risco de estado não convulsivo, aspiração e recorrência.",
            },
            "insegura": {
                "reacao": "A convulsão continua, com hipóxia, acidose, hipertermia e instabilidade cardiovascular progressivas.",
                "desfecho": "Pode haver lesão cerebral permanente, rabdomiólise, insuficiência renal, arritmia, aspiração ou morte.",
            },
        },
        "reacao_paciente_referencia": "Monitorar cessação clínica/eletrográfica, oxigenação, pressão, temperatura, consciência e complicações metabólicas.",
        "desfecho_referencia": "O fator modificável mais importante é interromper rapidamente a crise e corrigir a causa precipitante.",
        "temas_estudo": [
            "Algoritmo temporal do estado de mal convulsivo",
            "Benzodiazepínicos e fármacos de segunda linha",
            "Estado refratário, EEG contínuo e causas reversíveis",
        ],
        "fontes_clinicas": [
            _source(
                "Evidence-Based Guideline: Treatment of Convulsive Status Epilepticus",
                "American Epilepsy Society",
                2016,
                "https://pmc.ncbi.nlm.nih.gov/articles/PMC4749120/",
            ),
            NICE_EPILEPSY_SOURCE,
        ],
    },
}


FOURTH_FEEDBACK_BATCH_EXAM_UPDATES: dict[int, list[dict[str, Any]]] = {
    13: [
        {
            "id": "cpre",
            "nome": "CPRE terapêutica com coleta de material",
            "resultado": "Estenose biliar relevante com drenagem de secreção purulenta; realizada descompressão e coleta para citologia/cultura.",
            "correto": True,
        },
        {
            "id": "anticorpos",
            "nome": "p-ANCA",
            "resultado": "Positivo, porém inespecífico e sem utilidade para confirmar CEP ou orientar a emergência atual.",
            "correto": False,
        },
        {
            "id": "hemoculturas_lactato",
            "nome": "Hemoculturas, hemograma, função renal e lactato",
            "resultado": "Leucocitose, lactato elevado e hemoculturas coletadas antes do antibiótico; crescimento posterior de enterobactéria sensível.",
            "correto": True,
        },
        {
            "id": "usg_abdome",
            "nome": "Ultrassonografia de abdome",
            "resultado": "Dilatação biliar segmentar sem cálculo vesicular obstrutivo.",
            "correto": True,
        },
        {
            "id": "colangio_rm",
            "nome": "Colangiorressonância",
            "resultado": "Estenoses e dilatações multifocais intra e extra-hepáticas, com estenose hilar dominante.",
            "correto": True,
        },
        {
            "id": "ca19_9_imagem_dominante",
            "nome": "Investigação de estenose dominante/colangiocarcinoma",
            "resultado": "CA 19-9 discretamente elevado durante a colangite; resultado isolado não confirma câncer e requer reavaliação após controle da infecção e amostragem dirigida.",
            "correto": True,
        },
    ],
    20: [
        {
            "id": "puncao_lombar",
            "nome": "Punção lombar",
            "resultado": "Não indicada: não diagnostica oclusão basilar e atrasaria tratamento de reperfusão.",
            "correto": False,
        },
        {
            "id": "glicemia_abc",
            "nome": "Glicemia capilar e avaliação ABC",
            "resultado": "Glicemia normal; ventilação comprometida por fraqueza bulbar, exigindo vigilância de via aérea.",
            "correto": True,
        },
        {
            "id": "angio_tc_basilar",
            "nome": "AngioTC de crânio e pescoço",
            "resultado": "Oclusão da artéria basilar, com circulação colateral limitada.",
            "correto": True,
        },
        {
            "id": "rm_difusao",
            "nome": "RM de encéfalo com difusão",
            "resultado": "Restrição à difusão na ponte ventral, compatível com infarto agudo.",
            "correto": True,
        },
        {
            "id": "ecg_laboratorio_avc",
            "nome": "ECG e laboratório para reperfusão/etiologia",
            "resultado": "Sem contraindicação laboratorial imediata à reperfusão; investigação etiológica cardiovascular iniciada.",
            "correto": True,
        },
    ],
    23: [
        {
            "id": "eeg",
            "nome": "EEG",
            "resultado": "Hipsarritmia, fortemente sugestiva de síndrome de West.",
            "correto": True,
        },
        {
            "id": "tc_cranio",
            "nome": "TC de crânio como imagem etiológica de rotina",
            "resultado": "Menos sensível que a RM para causas estruturais e não é a imagem preferencial quando a criança está estável.",
            "correto": False,
        },
        {
            "id": "video_eeg_sono",
            "nome": "Vídeo-EEG incluindo sono",
            "resultado": "Espasmos em salvas com correlato eletrográfico e hipsarritmia durante o sono.",
            "correto": True,
        },
        {
            "id": "rm_encefalo",
            "nome": "RM de encéfalo",
            "resultado": "Lesões corticais sugestivas de esclerose tuberosa, orientando tratamento e investigação.",
            "correto": True,
        },
        {
            "id": "avaliacao_etiologica",
            "nome": "Avaliação etiológica genética/metabólica",
            "resultado": "Achados clínicos e moleculares compatíveis com complexo da esclerose tuberosa.",
            "correto": True,
        },
    ],
    24: [
        {
            "id": "avaliacao_tempo_neuro_glicemia",
            "nome": "Cronologia, exame neurológico seriado e glicemia",
            "resultado": "Afasia de instalação gradual em 10 minutos, duração de 35 minutos e reversão completa antes da cefaleia; glicemia normal.",
            "correto": True,
        },
        {
            "id": "tc_cranio",
            "nome": "TC de crânio sem contraste",
            "resultado": "Sem hemorragia ou lesão expansiva; exame normal não exclui isquemia muito precoce.",
            "correto": True,
        },
        {
            "id": "angio_rm_se_atipica",
            "nome": "AngioTC/RM se aura atípica ou déficit persistente",
            "resultado": "Sem oclusão vascular ou lesão aguda; indicada conforme cronologia e dúvida diagnóstica.",
            "correto": True,
        },
    ],
    25: [
        {
            "id": "eeg",
            "nome": "EEG após tratamento inicial",
            "resultado": "Atividade epileptiforme contínua; útil para confirmar persistência não convulsiva, sem atrasar benzodiazepínico.",
            "correto": True,
        },
        {
            "id": "glicemia_capilar",
            "nome": "Glicemia capilar imediata",
            "resultado": "92 mg/dL; hipoglicemia excluída sem atraso do tratamento anticonvulsivante.",
            "correto": True,
        },
        {
            "id": "laboratorio_causa_status",
            "nome": "Eletrólitos, função renal/hepática, hemograma e toxicologia dirigida",
            "resultado": "Hiponatremia moderada, provável fator precipitante; demais resultados sem alteração crítica imediata.",
            "correto": True,
        },
        {
            "id": "tc_pos_estabilizacao",
            "nome": "TC de crânio após estabilização",
            "resultado": "Sem hemorragia ou lesão expansiva aguda.",
            "correto": True,
        },
        {
            "id": "nivel_anticonvulsivante",
            "nome": "Nível sérico do anticonvulsivante em uso",
            "resultado": "Nível abaixo da faixa terapêutica, sugerindo baixa adesão ou dose insuficiente.",
            "correto": True,
        },
    ],
}
