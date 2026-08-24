"""Primeiro lote de rubricas estruturadas para casos clínicos legados."""

from typing import Any


def _source(title: str, organization: str, year: int, url: str) -> dict[str, Any]:
    return {
        "titulo": title,
        "organizacao": organization,
        "ano": year,
        "url": url,
    }


FIRST_FEEDBACK_BATCH_RUBRICS: dict[int, dict[str, Any]] = {
    14: {
        "diagnostico_referencia": "Pancreatite aguda biliar.",
        "diagnostico_termos": [
            "pancreatite aguda biliar",
            "pancreatite biliar",
            "pancreatite aguda por calculo",
            "pancreatite aguda por colelitíase",
            "pancreatite aguda por colelitiase",
        ],
        "diagnostico_parcial": [
            "pancreatite aguda",
            "pancreatite",
            "abdome agudo",
        ],
        "exames_essenciais": [
            "amilase_lipase",
            "usg_abdome",
            "funcao_renal_hepatica_eletrolitos",
        ],
        "exames_opcionais": ["hemo"],
        "exames_desnecessarios": ["tc_abdome_imediata"],
        "justificativa_exames": {
            "amilase_lipase": "Lipase ou amilase acima de três vezes o limite superior, junto à dor típica, completa os critérios diagnósticos sem exigir tomografia imediata.",
            "usg_abdome": "A ultrassonografia pesquisa cálculos e dilatação biliar e ajuda a definir a etiologia biliar.",
            "funcao_renal_hepatica_eletrolitos": "Ureia, creatinina, eletrólitos e provas hepáticas ajudam a estimar repercussão sistêmica e possível obstrução biliar.",
            "hemo": "Hemograma auxilia na avaliação inicial, mas leucocitose isolada não confirma infecção nem indica antibiótico.",
            "tc_abdome_imediata": "A tomografia não é rotineira quando dor e enzimas confirmam o diagnóstico; fica reservada para dúvida diagnóstica ou ausência de melhora após 48–72 horas.",
        },
        "conduta_criterios": [
            {
                "nome": "Avaliação de gravidade e monitorização",
                "pontos": 7,
                "termos": [
                    "avaliar gravidade",
                    "falencia organica",
                    "falência orgânica",
                    "sirs",
                    "monitorizacao",
                    "monitorização",
                    "diurese",
                    "internacao",
                    "internação",
                ],
            },
            {
                "nome": "Reposição volêmica moderada e analgesia",
                "pontos": 8,
                "termos": [
                    "ringer lactato",
                    "ringer lactato",
                    "cristaloide",
                    "hidratação venosa",
                    "hidratacao venosa",
                    "reposição volêmica",
                    "reposicao volemica",
                    "analgesia",
                    "antiemetico",
                    "antiemético",
                ],
            },
            {
                "nome": "Nutrição enteral ou oral precoce conforme tolerância",
                "pontos": 6,
                "termos": [
                    "alimentacao precoce",
                    "alimentação precoce",
                    "dieta precoce",
                    "dieta oral",
                    "via oral conforme tolerancia",
                    "via oral conforme tolerância",
                    "nutricao enteral",
                    "nutrição enteral",
                ],
            },
            {
                "nome": "Tratamento da causa biliar",
                "pontos": 9,
                "termos": [
                    "colecistectomia na mesma internacao",
                    "colecistectomia na mesma internação",
                    "colecistectomia precoce",
                    "avaliacao cirurgica",
                    "avaliação cirúrgica",
                    "cirurgia geral",
                    "colangite",
                    "obstrucao biliar",
                    "obstrução biliar",
                    "ercp",
                    "cpre",
                ],
            },
        ],
        "conduta_referencia": (
            "Internar, avaliar gravidade e falência orgânica, monitorar diurese e parâmetros clínicos, "
            "oferecer reposição com cristaloide de forma moderada e reavaliada, preferindo Ringer lactato, "
            "além de analgesia e antiemético. Iniciar alimentação oral pobre em gordura precocemente quando "
            "tolerada ou nutrição enteral se necessária. Na pancreatite biliar leve, programar colecistectomia "
            "na mesma internação; CPRE urgente fica reservada à colangite ou obstrução biliar persistente."
        ),
        "feedback_hipotese_parcial": "Você reconheceu a pancreatite, mas faltou relacioná-la à etiologia biliar sugerida pela colelitíase e pela ultrassonografia.",
        "feedback_hipotese_incorreta": "Dor epigástrica irradiada para o dorso e enzimas pancreáticas acima de três vezes o limite, associadas a cálculos, sustentam pancreatite aguda biliar.",
        "feedback_seguranca": "Evite hidratação excessivamente agressiva, antibiótico profilático e tomografia imediata sem indicação. Procure falência orgânica, colangite e obstrução biliar, que mudam a prioridade do manejo.",
        "objetivos_aprendizagem": [
            "Aplicar os critérios diagnósticos da pancreatite aguda",
            "Reconhecer etiologia biliar e sinais de gravidade",
            "Planejar suporte inicial, alimentação precoce e prevenção de recorrência",
        ],
        "criterios_seguranca": [
            {
                "nome": "Suporte e reavaliação hemodinâmica",
                "termos": [
                    "ringer lactato",
                    "cristaloide",
                    "hidratação",
                    "hidratacao",
                    "monitorização",
                    "monitorizacao",
                ],
                "feedback_omissao": "Sem reposição individualizada e reavaliação, hipovolemia e falência orgânica podem passar despercebidas.",
            },
            {
                "nome": "Reconhecimento de colangite ou obstrução",
                "termos": [
                    "colangite",
                    "obstrucao biliar",
                    "obstrução biliar",
                    "bilirrubina",
                    "provas hepaticas",
                    "provas hepáticas",
                ],
                "feedback_omissao": "A presença de colangite ou obstrução persistente exige avaliação urgente para descompressão biliar.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "A dor e os vômitos começam a ceder, a perfusão se mantém e a paciente tolera progressivamente a via oral.",
                "desfecho": "Com suporte adequado e tratamento da causa biliar na mesma internação, reduz-se o risco de falência orgânica e recorrência.",
            },
            "parcial": {
                "reacao": "Há alívio incompleto da dor, mas a paciente permanece vulnerável a desidratação, intolerância alimentar ou nova crise biliar.",
                "desfecho": "Sem monitorização e plano para a etiologia, a internação pode se prolongar e a pancreatite pode recorrer.",
            },
            "insegura": {
                "reacao": "A hipovolemia ou a sobrecarga podem piorar, e sinais de falência orgânica ou colangite podem surgir sem reconhecimento oportuno.",
                "desfecho": "Atraso no suporte ou em uma descompressão biliar indicada aumenta o risco de complicações graves e terapia intensiva.",
            },
        },
        "reacao_paciente_referencia": "A evolução deve ser acompanhada por dor, tolerância oral, perfusão, diurese, função renal e sinais de falência orgânica.",
        "desfecho_referencia": "A maioria dos quadros leves melhora com suporte; na etiologia biliar, tratar a causa reduz recorrências.",
        "temas_estudo": [
            "Diagnóstico e gravidade da pancreatite aguda",
            "Reposição volêmica e nutrição precoce",
            "Pancreatite biliar, CPRE e colecistectomia",
        ],
        "fontes_clinicas": [
            _source(
                "American College of Gastroenterology Guidelines: Management of Acute Pancreatitis",
                "American College of Gastroenterology",
                2024,
                "https://doi.org/10.14309/ajg.0000000000002645",
            )
        ],
    },
    18: {
        "diagnostico_referencia": "Primeiro episódio clínico de herpes genital, com necessidade de avaliar coinfecção ou complicação.",
        "diagnostico_termos": [
            "herpes genital",
            "herpes simples genital",
            "infeccao genital por hsv",
            "infecção genital por hsv",
            "primoinfeccao herpetica genital",
            "primoinfecção herpética genital",
        ],
        "diagnostico_parcial": [
            "ulcera genital",
            "úlceras genitais",
            "ist ulcerativa",
            "vulvovaginite",
        ],
        "exames_essenciais": ["pcr_hsv_lesao", "hiv_sifilis"],
        "exames_opcionais": ["sorologia"],
        "exames_desnecessarios": ["raspado"],
        "justificativa_exames": {
            "pcr_hsv_lesao": "NAAT/PCR da lesão é o teste mais sensível para confirmar HSV e deve permitir tipagem quando disponível.",
            "hiv_sifilis": "Úlcera genital exige avaliação para outras ISTs; pessoas com herpes genital devem realizar testagem para HIV e investigação de sífilis conforme o contexto.",
            "sorologia": "Sorologia tipo-específica pode ajudar em cenários selecionados, mas IgM não é recomendada e IgG isolada não confirma que a lesão atual seja herpética.",
            "raspado": "Citologia com células gigantes é inespecífica e pouco sensível; não substitui NAAT ou cultura da lesão.",
        },
        "conduta_criterios": [
            {
                "nome": "Antiviral sistêmico no primeiro episódio",
                "pontos": 10,
                "termos": [
                    "aciclovir",
                    "valaciclovir",
                    "famciclovir",
                    "antiviral oral",
                    "tratamento antiviral",
                    "sete a dez dias",
                    "7 a 10 dias",
                ],
            },
            {
                "nome": "Controle de dor e avaliação de gravidade",
                "pontos": 7,
                "termos": [
                    "analgesia",
                    "banho de assento",
                    "lidocaina",
                    "lidocaína",
                    "retenção urinária",
                    "retencao urinaria",
                    "hidratacao",
                    "hidratação",
                    "internacao",
                    "internação",
                ],
            },
            {
                "nome": "Rastreio de IST e avaliação de secreção associada",
                "pontos": 6,
                "termos": [
                    "teste hiv",
                    "hiv",
                    "sifilis",
                    "sífilis",
                    "gonorreia",
                    "clamidia",
                    "clamídia",
                    "investigar corrimento",
                    "coinfeccao",
                    "coinfecção",
                ],
            },
            {
                "nome": "Aconselhamento e prevenção de transmissão",
                "pontos": 7,
                "termos": [
                    "orientar parceria",
                    "orientar parceiro",
                    "avaliar parceiro",
                    "avaliar parceria",
                    "abstinencia durante lesoes",
                    "abstinência durante lesões",
                    "preservativo",
                    "transmissao assintomatica",
                    "transmissão assintomática",
                    "recorrencia",
                    "recorrência",
                ],
            },
        ],
        "conduta_referencia": (
            "Tratar o primeiro episódio com antiviral sistêmico por 7–10 dias, oferecendo analgesia e medidas "
            "locais e prolongando o curso se a cicatrização estiver incompleta. Confirmar por NAAT/PCR da lesão "
            "quando disponível, testar HIV e sífilis e investigar a secreção para coinfecções. Orientar recorrência, "
            "eliminação viral assintomática, redução de transmissão e avaliação das parcerias; avaliar gestação, "
            "retenção urinária, doença disseminada ou neurológica."
        ),
        "feedback_hipotese_parcial": "Você reconheceu uma síndrome de úlcera genital, mas faltou identificar o padrão doloroso e múltiplo compatível com herpes genital e considerar coinfecções.",
        "feedback_hipotese_incorreta": "Úlceras genitais dolorosas e múltiplas, disúria e edema são compatíveis com herpes genital; a confirmação preferencial é feita diretamente na lesão.",
        "feedback_seguranca": "IgM para HSV e citologia não devem sustentar isoladamente o diagnóstico. Febre, secreção fétida, retenção urinária, gestação ou sinais neurológicos exigem avaliação adicional e podem indicar coinfecção ou doença grave.",
        "objetivos_aprendizagem": [
            "Reconhecer apresentação de herpes genital e seus diferenciais",
            "Selecionar teste virológico adequado e rastrear outras ISTs",
            "Tratar o primeiro episódio e orientar prevenção de transmissão",
        ],
        "criterios_seguranca": [
            {
                "nome": "Antiviral sistêmico oportuno",
                "termos": ["aciclovir", "valaciclovir", "famciclovir", "antiviral"],
                "feedback_omissao": "Todo primeiro episódio clínico deve receber antiviral sistêmico para reduzir duração e intensidade dos sintomas.",
            },
            {
                "nome": "Busca de complicação ou coinfecção",
                "termos": [
                    "hiv",
                    "sifilis",
                    "sífilis",
                    "coinfeccao",
                    "coinfecção",
                    "retenção urinária",
                    "retencao urinaria",
                    "gestacao",
                    "gestação",
                ],
                "feedback_omissao": "A secreção e a febre não devem ser automaticamente atribuídas ao HSV; avalie outras ISTs, gestação e complicações.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Dor, ardor e edema começam a reduzir nos dias seguintes, enquanto as lesões cicatrizam progressivamente.",
                "desfecho": "O episódio é controlado, coinfecções são identificadas quando presentes e a paciente recebe orientação para reconhecer recorrências e reduzir transmissão.",
            },
            "parcial": {
                "reacao": "A dor pode persistir e a cicatrização ser mais lenta; dúvidas sobre transmissão e recorrência permanecem.",
                "desfecho": "Sem rastreio e aconselhamento, coinfecções ou necessidades das parcerias podem ficar sem abordagem.",
            },
            "insegura": {
                "reacao": "Lesões, dor e dificuldade para urinar podem piorar, com risco de desidratação ou evolução de complicações não reconhecidas.",
                "desfecho": "A ausência de antiviral e de avaliação de gravidade pode levar a atendimento de urgência e prolongar sofrimento e transmissão.",
            },
        },
        "reacao_paciente_referencia": "A resposta é acompanhada pela intensidade da dor, capacidade de urinar, regressão das lesões, febre e surgimento de sinais neurológicos.",
        "desfecho_referencia": "O antiviral controla o episódio, mas não erradica a latência; educação sobre recorrência e transmissão integra o tratamento.",
        "temas_estudo": [
            "Diagnóstico virológico do herpes genital",
            "Tratamento do primeiro episódio e das recorrências",
            "Aconselhamento, parcerias e rastreio de IST",
        ],
        "fontes_clinicas": [
            _source(
                "Sexually Transmitted Infections Treatment Guidelines: Genital Herpes",
                "Centers for Disease Control and Prevention",
                2021,
                "https://www.cdc.gov/std/treatment-guidelines/herpes.htm",
            )
        ],
    },
    19: {
        "diagnostico_referencia": "Cervicite gonocócica não complicada, com necessidade de excluir clamídia e doença inflamatória pélvica.",
        "diagnostico_termos": [
            "gonorreia",
            "cervicite gonococica",
            "cervicite gonocócica",
            "infeccao por neisseria gonorrhoeae",
            "infecção por neisseria gonorrhoeae",
        ],
        "diagnostico_parcial": [
            "cervicite",
            "uretrite",
            "ist bacteriana",
            "doença inflamatoria pelvica",
            "doença inflamatória pélvica",
        ],
        "exames_essenciais": ["pcr_gonococo", "pcr_clamidia", "hiv_sifilis"],
        "exames_opcionais": ["gram"],
        "exames_desnecessarios": [],
        "justificativa_exames": {
            "pcr_gonococo": "NAAT/PCR em amostra vaginal, endocervical ou urina é o método preferencial para detectar N. gonorrhoeae em mulheres.",
            "pcr_clamidia": "A pesquisa simultânea de C. trachomatis define se é necessário tratamento anticlâmidia e reconhece coinfecção frequente.",
            "hiv_sifilis": "Toda pessoa diagnosticada com gonorreia deve ser testada para HIV, sífilis e outras ISTs conforme exposição.",
            "gram": "Diplococos Gram-negativos intracelulares apoiam a suspeita, mas o Gram endocervical tem sensibilidade insuficiente para ser o único teste em mulheres.",
        },
        "conduta_criterios": [
            {
                "nome": "Ceftriaxona em dose recomendada",
                "pontos": 10,
                "termos": [
                    "ceftriaxona 500",
                    "ceftriaxone 500",
                    "ceftriaxona intramuscular",
                    "ceftriaxona im",
                    "ceftriaxona dose unica",
                    "ceftriaxona dose única",
                    "ceftriaxona 1 g",
                ],
            },
            {
                "nome": "Cobertura para clamídia quando não excluída",
                "pontos": 6,
                "termos": [
                    "doxiciclina",
                    "tratar clamidia",
                    "tratar clamídia",
                    "clamidia nao excluida",
                    "clamídia não excluída",
                    "pcr clamidia",
                    "pcr clamídia",
                ],
            },
            {
                "nome": "Avaliação de IST e doença inflamatória pélvica",
                "pontos": 7,
                "termos": [
                    "hiv",
                    "sifilis",
                    "sífilis",
                    "doenca inflamatoria pelvica",
                    "doença inflamatória pélvica",
                    "dip",
                    "dor pelvica",
                    "dor pélvica",
                    "gravidez",
                    "gestacao",
                    "gestação",
                ],
            },
            {
                "nome": "Parcerias, abstinência e reteste",
                "pontos": 7,
                "termos": [
                    "tratar parceiro",
                    "tratar parceria",
                    "avaliar parceiro",
                    "avaliar parceria",
                    "ultimos 60 dias",
                    "últimos 60 dias",
                    "abstinencia 7 dias",
                    "abstinência 7 dias",
                    "reteste em 3 meses",
                    "retestar em 3 meses",
                ],
            },
        ],
        "conduta_referencia": (
            "Tratar gonorreia cervical não complicada com ceftriaxona 500 mg IM em dose única se peso abaixo "
            "de 150 kg, ou 1 g se peso igual ou superior a 150 kg. Se clamídia não foi excluída e não houver "
            "contraindicação, acrescentar doxiciclina por 7 dias, adequando a opção à gestação. Testar HIV e "
            "sífilis, avaliar DIP e gestação, orientar abstinência por 7 dias após o tratamento e até as parcerias "
            "serem tratadas, manejar contatos dos últimos 60 dias e retestar em cerca de 3 meses."
        ),
        "feedback_hipotese_parcial": "Você reconheceu cervicite infecciosa, mas faltou identificar a etiologia gonocócica e abordar a possibilidade de coinfecção por clamídia.",
        "feedback_hipotese_incorreta": "Secreção endocervical purulenta, colo friável, disúria e diplococos Gram-negativos intracelulares apontam para cervicite gonocócica.",
        "feedback_seguranca": "Não confie apenas no Gram em mulheres e não use azitromicina isolada. Avalie DIP, gestação, outras ISTs e parcerias para evitar complicações e reinfecção.",
        "objetivos_aprendizagem": [
            "Diagnosticar cervicite gonocócica com teste molecular",
            "Aplicar tratamento recomendado e cobertura anticlâmidia quando indicada",
            "Interromper transmissão por rastreio, manejo de parcerias e reteste",
        ],
        "criterios_seguranca": [
            {
                "nome": "Tratamento efetivo com ceftriaxona",
                "termos": ["ceftriaxona", "ceftriaxone"],
                "feedback_omissao": "Sem ceftriaxona em regime apropriado, persistem risco de transmissão, doença ascendente e seleção de resistência.",
            },
            {
                "nome": "Exclusão de DIP e gestação",
                "termos": [
                    "dip",
                    "doença inflamatória pélvica",
                    "doenca inflamatoria pelvica",
                    "dor pélvica",
                    "dor pelvica",
                    "gestação",
                    "gestacao",
                    "gravidez",
                ],
                "feedback_omissao": "Em mulheres com cervicite, sintomas pélvicos e possibilidade de gestação mudam investigação e tratamento.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "Disúria e secreção começam a regredir, e o risco imediato de transmissão cai após o tratamento correto e a pausa sexual orientada.",
                "desfecho": "A infecção é tratada, coinfecções e DIP são avaliadas e o manejo das parcerias reduz reinfecção e complicações reprodutivas.",
            },
            "parcial": {
                "reacao": "Os sintomas podem melhorar, mas uma clamídia não reconhecida ou parceria não tratada mantém inflamação e risco de retorno.",
                "desfecho": "Reinfecção e progressão para doença inflamatória pélvica permanecem possíveis sem abordagem completa.",
            },
            "insegura": {
                "reacao": "A cervicite persiste ou piora, podendo surgir dor pélvica e sinais de infecção ascendente.",
                "desfecho": "Tratamento inadequado aumenta risco de DIP, infertilidade, gravidez ectópica, transmissão e resistência antimicrobiana.",
            },
        },
        "reacao_paciente_referencia": "A resposta é acompanhada por redução da secreção e da disúria e ausência de dor pélvica, febre ou persistência após 3–5 dias.",
        "desfecho_referencia": "Tratamento efetivo e manejo das parcerias costumam resolver o quadro; reteste em três meses identifica reinfecção frequente.",
        "temas_estudo": [
            "Diagnóstico molecular da gonorreia",
            "Resistência e tratamento da cervicite gonocócica",
            "DIP, parcerias sexuais e prevenção de reinfecção",
        ],
        "fontes_clinicas": [
            _source(
                "Sexually Transmitted Infections Treatment Guidelines: Gonococcal Infections Among Adolescents and Adults",
                "Centers for Disease Control and Prevention",
                2021,
                "https://www.cdc.gov/std/treatment-guidelines/gonorrhea-adults.htm",
            )
        ],
    },
    21: {
        "diagnostico_referencia": "Paralisia facial periférica idiopática aguda (paralisia de Bell) à esquerda.",
        "diagnostico_termos": [
            "paralisia de bell",
            "paralisia facial periferica idiopatica",
            "paralisia facial periférica idiopática",
            "neuropatia facial idiopatica",
            "neuropatia facial idiopática",
        ],
        "diagnostico_parcial": [
            "paralisia facial periferica",
            "paralisia facial periférica",
            "paresia facial periferica",
            "paresia facial periférica",
        ],
        "exames_essenciais": ["avaliacao_clinica_bell"],
        "exames_opcionais": ["eletroneuro"],
        "exames_desnecessarios": ["rm_cranio"],
        "justificativa_exames": {
            "avaliacao_clinica_bell": "História e exame neurológico demonstrando acometimento de fronte e metade inferior da face, sem outros déficits, sustentam diagnóstico periférico e excluem sinais de causa identificável.",
            "eletroneuro": "Teste eletrodiagnóstico não é rotineiro em paresia incompleta; pode ser considerado para prognóstico em paralisia completa.",
            "rm_cranio": "Imagem não é indicada rotineiramente em início agudo típico; é reservada a progressão atípica, recorrência, outros déficits ou ausência de recuperação esperada.",
        },
        "conduta_criterios": [
            {
                "nome": "Corticoide oral dentro de 72 horas",
                "pontos": 10,
                "termos": [
                    "prednisona",
                    "prednisolona",
                    "corticoide oral",
                    "corticosteroide oral",
                    "dentro de 72 horas",
                    "nas primeiras 72 horas",
                ],
            },
            {
                "nome": "Proteção ocular",
                "pontos": 9,
                "termos": [
                    "lagrima artificial",
                    "lágrima artificial",
                    "lubrificante ocular",
                    "pomada oftalmica",
                    "pomada oftálmica",
                    "oclusao ocular",
                    "oclusão ocular",
                    "proteção ocular",
                    "protecao ocular",
                ],
            },
            {
                "nome": "Exclusão de causas alternativas",
                "pontos": 6,
                "termos": [
                    "exame neurologico",
                    "exame neurológico",
                    "forca de membros",
                    "força de membros",
                    "avc",
                    "vesiculas no ouvido",
                    "vesículas no ouvido",
                    "ramsay hunt",
                    "otite",
                    "lyme",
                ],
            },
            {
                "nome": "Seguimento e critérios de reavaliação",
                "pontos": 5,
                "termos": [
                    "reavaliar",
                    "seguimento",
                    "encaminhar",
                    "oftalmologia",
                    "novos sintomas neurologicos",
                    "novos sintomas neurológicos",
                    "tres meses",
                    "três meses",
                ],
            },
        ],
        "conduta_referencia": (
            "Confirmar padrão periférico e excluir causas identificáveis pela história e exame. Iniciar corticoide "
            "oral em adulto dentro de 72 horas, salvo contraindicação, e proteger rigorosamente o olho que não "
            "fecha com lubrificação e medidas noturnas. Antiviral nunca deve ser usado isoladamente e pode ser "
            "discutido apenas como adjuvante ao corticoide. Reavaliar imediatamente se surgirem novos déficits, "
            "sintomas oculares ou evolução atípica e encaminhar se a recuperação permanecer incompleta em três meses."
        ),
        "feedback_hipotese_parcial": "Você reconheceu a paralisia facial periférica, mas faltou caracterizar o quadro idiopático agudo e excluir causas como Ramsay Hunt, otite, trauma ou outros déficits neurológicos.",
        "feedback_hipotese_incorreta": "O comprometimento da testa e do fechamento ocular junto ao desvio da boca localiza a lesão no nervo facial periférico, compatível com paralisia de Bell no contexto apresentado.",
        "feedback_seguranca": "A proteção ocular é imediata para evitar lesão de córnea. Não atrase corticoide nas primeiras 72 horas por exames rotineiros, mas investigue se houver padrão atípico, recorrência ou outros déficits.",
        "objetivos_aprendizagem": [
            "Diferenciar paralisia facial periférica de lesão central",
            "Indicar corticoide precoce e proteção ocular",
            "Reconhecer quando exames, encaminhamento ou reavaliação são necessários",
        ],
        "criterios_seguranca": [
            {
                "nome": "Proteção imediata da córnea",
                "termos": [
                    "lágrima artificial",
                    "lagrima artificial",
                    "lubrificante ocular",
                    "pomada oftálmica",
                    "pomada oftalmica",
                    "proteção ocular",
                    "protecao ocular",
                ],
                "feedback_omissao": "O fechamento palpebral incompleto expõe a córnea a abrasão, ceratite e perda visual evitável.",
            },
            {
                "nome": "Triagem de sinais neurológicos atípicos",
                "termos": [
                    "exame neurológico",
                    "exame neurologico",
                    "força de membros",
                    "forca de membros",
                    "avc",
                    "outros déficits",
                    "outros deficits",
                ],
                "feedback_omissao": "Outros déficits neurológicos ou preservação da testa exigem investigação urgente de causa central.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "O olho permanece protegido e a fraqueza facial tende a começar a melhorar ao longo das semanas.",
                "desfecho": "A maioria recupera função facial satisfatória, com seguimento para sintomas oculares ou recuperação incompleta.",
            },
            "parcial": {
                "reacao": "A paresia pode evoluir lentamente, e desconforto ocular persiste se a proteção for irregular.",
                "desfecho": "O benefício do tratamento precoce pode ser reduzido e sequelas funcionais tornam-se mais prováveis.",
            },
            "insegura": {
                "reacao": "O olho exposto desenvolve ressecamento, dor ou vermelhidão, enquanto uma causa alternativa pode passar despercebida.",
                "desfecho": "Há risco de lesão corneana e atraso no diagnóstico de doença neurológica ou otológica relevante.",
            },
        },
        "reacao_paciente_referencia": "Acompanhar fechamento ocular, sintomas de córnea, força facial e surgimento de outros sinais neurológicos.",
        "desfecho_referencia": "A recuperação costuma ocorrer em semanas a meses; evolução atípica ou incompleta exige reavaliação especializada.",
        "temas_estudo": [
            "Topografia central e periférica da paralisia facial",
            "Corticoide e cuidado ocular na paralisia de Bell",
            "Diagnósticos diferenciais e sinais de alarme",
        ],
        "fontes_clinicas": [
            _source(
                "Clinical Practice Guideline: Bell's Palsy",
                "American Academy of Otolaryngology—Head and Neck Surgery Foundation",
                2013,
                "https://www.entnet.org/quality-practice/quality-products/clinical-practice-guidelines/bells-palsy/",
            )
        ],
    },
    22: {
        "diagnostico_referencia": "Migrânea sem aura, com padrão relacionado ao período menstrual.",
        "diagnostico_termos": [
            "migranea sem aura",
            "migrânea sem aura",
            "enxaqueca sem aura",
            "migranea menstrual sem aura",
            "migrânea menstrual sem aura",
        ],
        "diagnostico_parcial": [
            "migranea",
            "migrânea",
            "enxaqueca",
            "cefaleia primaria",
            "cefaleia primária",
        ],
        "exames_essenciais": ["clinico"],
        "exames_opcionais": ["diario_cefaleia"],
        "exames_desnecessarios": ["imagem_cranio_rotina"],
        "justificativa_exames": {
            "clinico": "História compatível, recorrência desde a adolescência e exame neurológico normal permitem aplicar critérios clínicos da ICHD-3.",
            "diario_cefaleia": "Um diário registra frequência, relação menstrual, uso de analgésicos e resposta ao tratamento, ajudando no seguimento.",
            "imagem_cranio_rotina": "Neuroimagem não é indicada apenas para tranquilização em cefaleia primária típica, recorrente e sem sinais de alarme.",
        },
        "conduta_criterios": [
            {
                "nome": "Tratamento precoce da crise",
                "pontos": 9,
                "termos": [
                    "triptano",
                    "sumatriptana",
                    "naratriptana",
                    "anti-inflamatorio",
                    "anti-inflamatório",
                    "aine",
                    "ibuprofeno",
                    "naproxeno",
                    "paracetamol",
                    "tratamento no inicio",
                    "tratamento no início",
                ],
            },
            {
                "nome": "Controle de náusea e ambiente",
                "pontos": 5,
                "termos": [
                    "antiemetico",
                    "antiemético",
                    "metoclopramida",
                    "domperidona",
                    "ambiente escuro",
                    "repouso",
                    "hidratação",
                    "hidratacao",
                ],
            },
            {
                "nome": "Triagem de sinais de alarme",
                "pontos": 8,
                "termos": [
                    "sinais de alarme",
                    "red flags",
                    "cefaleia subita",
                    "cefaleia súbita",
                    "déficit neurológico",
                    "deficit neurologico",
                    "febre",
                    "papiledema",
                    "gestação",
                    "gestacao",
                    "cancer",
                    "imunossupressao",
                    "imunossupressão",
                ],
            },
            {
                "nome": "Educação, diário e prevenção",
                "pontos": 8,
                "termos": [
                    "diario de cefaleia",
                    "diário de cefaleia",
                    "gatilhos",
                    "sono",
                    "exercicio",
                    "exercício",
                    "profilaxia",
                    "preventivo",
                    "uso excessivo de analgesico",
                    "uso excessivo de analgésico",
                    "limitar analgesicos",
                    "limitar analgésicos",
                ],
            },
        ],
        "conduta_referencia": (
            "Confirmar critérios clínicos e ausência de sinais de alarme. Tratar a crise precocemente com um "
            "triptano associado a AINE ou paracetamol, ou monoterapia conforme preferência, contraindicações e "
            "resposta prévia, acrescentando antiemético quando necessário. Orientar repouso, hidratação, diário "
            "de cefaleia e prevenção de uso excessivo de medicação. Avaliar estratégia preventiva se as crises "
            "forem frequentes ou incapacitantes e documentar a relação com o ciclo menstrual."
        ),
        "feedback_hipotese_parcial": "Você reconheceu uma cefaleia primária, mas faltou identificar o padrão pulsátil, a foto e fonofobia, a recorrência e a ausência de aura que caracterizam migrânea sem aura.",
        "feedback_hipotese_incorreta": "Cefaleia pulsátil unilateral de 12 horas, com foto e fonofobia, episódios prévios e exame neurológico normal é típica de migrânea sem aura.",
        "feedback_seguranca": "Não solicite imagem apenas para tranquilização em um padrão típico sem sinais de alarme. Antes de concluir, procure início súbito, déficit neurológico, febre, papiledema, gestação, câncer ou imunossupressão.",
        "objetivos_aprendizagem": [
            "Aplicar critérios da ICHD-3 para migrânea sem aura",
            "Selecionar tratamento agudo individualizado",
            "Reconhecer sinais de alarme e prevenir uso excessivo de medicação",
        ],
        "criterios_seguranca": [
            {
                "nome": "Exclusão de cefaleia secundária",
                "termos": [
                    "sinais de alarme",
                    "red flags",
                    "cefaleia súbita",
                    "cefaleia subita",
                    "déficit neurológico",
                    "deficit neurologico",
                    "papiledema",
                    "febre",
                ],
                "feedback_omissao": "Sinais de alarme mudam a hipótese e podem exigir investigação urgente de cefaleia secundária.",
            },
            {
                "nome": "Evitar opioide e abuso de medicação",
                "termos": [
                    "evitar opioide",
                    "não usar opioide",
                    "nao usar opioide",
                    "uso excessivo",
                    "limitar analgésico",
                    "limitar analgesico",
                ],
                "feedback_omissao": "Opioides não são tratamento rotineiro da migrânea, e uso frequente de medicação aguda pode perpetuar cefaleia.",
            },
        ],
        "desfechos_conduta": {
            "adequada": {
                "reacao": "A dor, a fotofobia e a fonofobia reduzem nas horas seguintes, permitindo retorno gradual às atividades.",
                "desfecho": "A paciente sai com plano para próximas crises, diário de cefaleia e critérios claros para procurar reavaliação.",
            },
            "parcial": {
                "reacao": "A crise melhora lentamente ou recorre, e o impacto funcional permanece maior que o necessário.",
                "desfecho": "Sem plano individualizado e prevenção, novos episódios podem continuar frequentes e gerar uso excessivo de analgésicos.",
            },
            "insegura": {
                "reacao": "A dor persiste e um possível sinal de alarme ou contraindicação medicamentosa pode não ser reconhecido.",
                "desfecho": "Há risco de atraso em cefaleia secundária ou de cronificação por tratamento inadequado e abuso de medicação.",
            },
        },
        "reacao_paciente_referencia": "Monitorar intensidade da dor, náusea, foto e fonofobia, retorno funcional e resposta ao tratamento nas horas seguintes.",
        "desfecho_referencia": "Crises típicas costumam responder ao tratamento agudo; frequência e incapacidade determinam necessidade de prevenção.",
        "temas_estudo": [
            "Critérios ICHD-3 e sinais de alarme",
            "Tratamento agudo da migrânea",
            "Migrânea menstrual e cefaleia por uso excessivo de medicação",
        ],
        "fontes_clinicas": [
            _source(
                "1.1 Migraine without aura",
                "International Headache Society",
                2018,
                "https://ichd-3.org/1-migraine/1-1-migraine-without-aura/",
            ),
            _source(
                "Headaches in over 12s: diagnosis and management",
                "National Institute for Health and Care Excellence",
                2012,
                "https://www.nice.org.uk/guidance/cg150/chapter/recommendations",
            ),
        ],
    },
}


FIRST_FEEDBACK_BATCH_EXAM_UPDATES: dict[int, list[dict[str, Any]]] = {
    14: [
        {
            "id": "funcao_renal_hepatica_eletrolitos",
            "nome": "Função renal, eletrólitos e provas hepáticas",
            "resultado": "Ureia e creatinina discretamente elevadas por hipovolemia; ALT e bilirrubina elevadas, reforçando etiologia biliar; sem distúrbio eletrolítico crítico.",
            "correto": True,
        },
        {
            "id": "tc_abdome_imediata",
            "nome": "TC de abdome com contraste imediatamente",
            "resultado": "Não indicada de rotina neste momento, pois dor típica e enzimas acima de três vezes o limite já estabelecem o diagnóstico.",
            "correto": False,
        },
    ],
    18: [
        {
            "id": "raspado",
            "nome": "Citologia do fundo da lesão",
            "resultado": "Células gigantes multinucleadas; achado pouco sensível e inespecífico, que não substitui teste virológico.",
            "correto": False,
        },
        {
            "id": "sorologia",
            "nome": "Sorologia tipo-específica para HSV",
            "resultado": "HSV-2 IgG reagente; IgM não deve ser usada para definir infecção recente nem atribuir a lesão atual ao HSV.",
            "correto": True,
        },
        {
            "id": "pcr_hsv_lesao",
            "nome": "NAAT/PCR da lesão com tipagem para HSV-1 e HSV-2",
            "resultado": "HSV-2 detectado na amostra da úlcera.",
            "correto": True,
        },
        {
            "id": "hiv_sifilis",
            "nome": "Testagem para HIV e sífilis",
            "resultado": "Teste para HIV não reagente; testes treponêmico e não treponêmico para sífilis não reagentes neste atendimento.",
            "correto": True,
        },
    ],
    19: [
        {
            "id": "gram",
            "nome": "Bacterioscopia da secreção endocervical",
            "resultado": "Diplococos Gram-negativos intracelulares; achado sugestivo, mas insuficiente como teste único em mulheres.",
            "correto": True,
        },
        {
            "id": "pcr_clamidia",
            "nome": "NAAT/PCR para Chlamydia trachomatis",
            "resultado": "Não detectado.",
            "correto": True,
        },
        {
            "id": "pcr_gonococo",
            "nome": "NAAT/PCR para Neisseria gonorrhoeae",
            "resultado": "Neisseria gonorrhoeae detectada em amostra vaginal/endocervical.",
            "correto": True,
        },
        {
            "id": "hiv_sifilis",
            "nome": "Testagem para HIV e sífilis",
            "resultado": "Testes para HIV e sífilis não reagentes neste atendimento.",
            "correto": True,
        },
    ],
    21: [
        {
            "id": "eletroneuro",
            "nome": "Eletroneurografia",
            "resultado": "Não é indicada rotineiramente na paresia incompleta; pode auxiliar o prognóstico quando a paralisia é completa.",
            "correto": True,
        },
        {
            "id": "rm_cranio",
            "nome": "RM de crânio",
            "resultado": "Não indicada de rotina em paralisia facial periférica aguda típica, sem outros déficits neurológicos.",
            "correto": False,
        },
        {
            "id": "avaliacao_clinica_bell",
            "nome": "Avaliação clínica e exame neurológico completo",
            "resultado": "Paresia de toda a hemiface esquerda, inclusive fronte e fechamento palpebral, sem déficit de membros, alteração de fala, vesículas auriculares ou outros sinais focais.",
            "correto": True,
        },
    ],
    22: [
        {
            "id": "diario_cefaleia",
            "nome": "Diário de cefaleia",
            "resultado": "Episódios recorrentes de 8–24 horas, frequentemente perimenstruais, sem sintomas focais prévios e com uso esporádico de analgésicos.",
            "correto": True,
        },
        {
            "id": "imagem_cranio_rotina",
            "nome": "Neuroimagem apenas para tranquilização",
            "resultado": "Não indicada no padrão típico recorrente, com exame neurológico normal e ausência de sinais de alarme.",
            "correto": False,
        },
    ],
}
