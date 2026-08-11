"""Gabaritos dos desafios nativos mantidos somente no servidor."""

BUILTIN_CHALLENGE_ANSWERS = {
    "desafio-visual-001": {
        "correct_option_id": "pneumotorax",
        "diagnosis": "Pneumotórax hipertensivo à esquerda",
        "explanation": "A radiografia mostra hipertransparência do hemitórax esquerdo, ausência de trama vascular periférica e desvio do mediastino para o lado oposto. Esse conjunto indica ar sob pressão no espaço pleural.",
        "key_findings": ["Linha pleural visível com ausência de vasos além dela", "Hemitórax esquerdo hipertransparente", "Desvio traqueal e mediastinal contralateral"],
    },
    "desafio-visual-002": {
        "correct_option_id": "fibrilacao",
        "diagnosis": "Fibrilação atrial",
        "explanation": "O traçado apresenta intervalos RR irregularmente irregulares e não mostra ondas P organizadas antes dos complexos QRS, padrão característico da fibrilação atrial.",
        "key_findings": ["Ritmo irregularmente irregular", "Ausência de ondas P organizadas", "Atividade fibrilatória na linha de base"],
    },
    "desafio-visual-003": {
        "correct_option_id": "epidural",
        "diagnosis": "Hematoma epidural",
        "explanation": "A coleção extra-axial hiperdensa tem formato biconvexo ou lentiforme e causa efeito de massa. Esse formato ocorre porque o sangue epidural costuma ser limitado pelas suturas cranianas.",
        "key_findings": ["Coleção hiperdensa extra-axial", "Formato biconvexo ou lentiforme", "Desvio da linha média e compressão ventricular"],
    },
    "desafio-visual-004": {
        "correct_option_id": "psoriase",
        "diagnosis": "Psoríase em placas",
        "explanation": "A presença de placas eritematosas bem delimitadas recobertas por escamas esbranquiçadas ou prateadas é típica da psoríase em placas, especialmente em superfícies extensoras.",
        "key_findings": ["Placas eritematosas bem delimitadas", "Escamas espessas esbranquiçadas", "Distribuição em superfície extensora"],
    },
    "desafio-visual-005": {
        "correct_option_id": "diabetica",
        "diagnosis": "Retinopatia diabética",
        "explanation": "Microaneurismas, pequenas hemorragias intrarretinianas e exsudatos duros são achados clássicos da lesão microvascular provocada pelo diabetes.",
        "key_findings": ["Microaneurismas", "Hemorragias puntiformes", "Exsudatos duros amarelados"],
    },
    "desafio-visual-006": {
        "correct_option_id": "falciforme",
        "diagnosis": "Doença falciforme",
        "explanation": "O esfregaço mostra drepanócitos, hemácias alongadas em formato de foice produzidas pela polimerização da hemoglobina S, além de células-alvo.",
        "key_findings": ["Drepanócitos ou células em foice", "Células-alvo", "Poquilocitose acentuada"],
    },
    "desafio-visual-007": {
        "correct_option_id": "pneumonia-lobar",
        "diagnosis": "Pneumonia lobar",
        "explanation": "A radiografia apresenta uma opacidade alveolar relativamente homogênea no campo pulmonar direito, com distribuição lobar. Esse padrão de consolidação é compatível com pneumonia lobar no contexto clínico adequado.",
        "key_findings": ["Opacidade alveolar focal no pulmão direito", "Distribuição respeitando limites lobares", "Broncogramas aéreos no interior da consolidação"],
    },
    "desafio-visual-008": {
        "correct_option_id": "apendicite",
        "diagnosis": "Apendicite aguda",
        "explanation": "A imagem demonstra estrutura tubular em fundo cego, espessada e não compressível, com aspecto em alvo no corte transversal. Esses achados sustentam o diagnóstico de apendicite aguda.",
        "key_findings": ["Estrutura tubular em fundo cego", "Diâmetro externo aumentado e parede espessada", "Aspecto em alvo no corte transversal"],
    },
    "desafio-visual-009": {
        "correct_option_id": "calculo-ureteral",
        "diagnosis": "Cálculo ureteral proximal",
        "explanation": "A tomografia sem contraste evidencia um foco hiperdenso no ureter proximal direito, acompanhado de dilatação discreta do sistema coletor a montante. O conjunto caracteriza ureterolitíase obstrutiva.",
        "key_findings": ["Foco hiperdenso no trajeto do ureter proximal", "Dilatação do sistema pielocalicial direito", "Sinal de obstrução urinária a montante"],
    },
    "desafio-visual-010": {
        "correct_option_id": "melanoma",
        "diagnosis": "Melanoma cutâneo",
        "explanation": "A assimetria, as bordas irregulares e a variação de cores dentro da mesma lesão são sinais de alerta para melanoma. A confirmação depende de avaliação dermatológica e exame histopatológico.",
        "key_findings": ["Assimetria entre as metades da lesão", "Bordas irregulares e mal delimitadas", "Variação de tonalidades na mesma lesão"],
    },
}

BUILTIN_CHALLENGE_SOURCES = {
    "desafio-visual-001": ("Clinical Cases / Wikimedia Commons", "CC BY-SA 2.5", "https://commons.wikimedia.org/wiki/File:Pneumothorax_CXR.jpg"),
    "desafio-visual-002": ("Ewingdo / Wikimedia Commons", "CC BY-SA 4.0", "https://commons.wikimedia.org/wiki/File:ECG_Atrial_Fibrillation.jpg"),
    "desafio-visual-003": ("Jfdwolff / Wikimedia Commons", "CC BY-SA 3.0", "https://commons.wikimedia.org/wiki/File:Epidural_hematoma.png"),
    "desafio-visual-004": ("paul-hat-schuppenflechte.de / Wikimedia Commons", "CC BY-SA 3.0", "https://commons.wikimedia.org/wiki/File:Psoriasis_am_Unterschenkel.JPG"),
    "desafio-visual-005": ("Hao et al., PLOS ONE / Wikimedia Commons", "CC BY 4.0", "https://commons.wikimedia.org/wiki/File:Fundus_-_diabetic_retinopathy.png"),
    "desafio-visual-006": ("Keith Chambers / Wikimedia Commons", "CC BY-SA 3.0", "https://commons.wikimedia.org/wiki/File:Sickle_Cell_Blood_Smear.JPG"),
    "desafio-visual-007": ("Mikael Häggström, M.D. / Wikimedia Commons", "CC0 1.0", "https://commons.wikimedia.org/wiki/File:X-ray_of_lobar_pneumonia.jpg"),
    "desafio-visual-008": ("Borbély Márton / Wikimedia Commons", "CC BY-SA 4.0", "https://commons.wikimedia.org/wiki/File:Appendicitis_ultrasound.png"),
    "desafio-visual-009": ("James Heilman, MD / Wikimedia Commons", "CC BY-SA 3.0", "https://commons.wikimedia.org/wiki/File:KidneyStone.JPG"),
    "desafio-visual-010": ("National Cancer Institute / Wikimedia Commons", "Domínio público", "https://commons.wikimedia.org/wiki/File:Melanoma_(2).jpg"),
}
