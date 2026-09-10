"""Taxonomia pública navegável do catálogo de questões.

Os campos de origem são preservados. Este módulo apenas projeta a hierarquia
que o aluno enxerga: especialidade -> tema -> assunto.
"""

from __future__ import annotations

import re
import unicodedata

INTERNAL_CLINICAL_MACRO = "Clínica Médica"
INTERNAL_OTHER_MACRO = "Outros"
MULTIDISCIPLINARY_SPECIALTY = "Conteúdo multidisciplinar"
GENERAL_THEME = "Conteúdos gerais"
GENERAL_SUBJECT = "Geral"


def _normalized(value: str | None) -> str:
    text = unicodedata.normalize("NFKD", (value or "").strip())
    return re.sub(r"\s+", " ", "".join(c for c in text if not unicodedata.combining(c))).casefold()


# Regras amplas e determinísticas. O assunto de origem continua sendo exibido
# no terceiro nível, portanto nenhuma granularidade do catálogo é descartada.
CLINICAL_THEME_RULES: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
    "Hematologia": (
        ("Anemias", ("anemia",)),
        ("Neoplasias hematológicas", ("leucem", "linfom", "gamopatia", "mielodisplasia", "mieloprolifera", "oncohemat")),
        ("Hemostasia e trombose", ("hemostasia", "coagul", "trombo")),
        ("Hemoglobinopatias", ("hemoglobinopatia",)),
        ("Medicina transfusional", ("transfusion",)),
        ("Fundamentos hematológicos", ("hematopo", "baco", "esplen", "neutropenia", "porfiria")),
    ),
    "Cardiologia": (
        ("Doença cardiovascular aterosclerótica", ("ateroscler", "coronarian", "isquem")),
        ("Arritmias e eletrofisiologia", ("arritm", "eletrocard", "fisiologia cardi")),
        ("Insuficiência cardíaca e cardiomiopatias", ("insuficiencia cardi", "cardiomiop")),
        ("Hipertensão arterial", ("hipertens",)),
        ("Valvopatias", ("valvopat",)),
        ("Emergências cardiovasculares", ("choque", "aortic",)),
        ("Pericárdio", ("pericard",)),
    ),
    "Endocrinologia": (
        ("Diabetes e hipoglicemia", ("diabetes", "hipoglic")),
        ("Tireoide", ("tireo", "tireotox")),
        ("Adrenal", ("adrenal",)),
        ("Metabolismo ósseo e mineral", ("osseo", "mineral")),
        ("Obesidade e metabolismo", ("obesidade", "metabolic")),
        ("Hipófise", ("hipofis",)),
        ("Endocrinologia reprodutiva", ("sexual", "genero")),
        ("Neoplasias endócrinas", ("neoplasia",)),
    ),
    "Gastroenterologia": (
        ("Trato gastrointestinal alto", ("esofag", "estomag")),
        ("Intestinos", ("intestin",)),
        ("Hemorragia digestiva", ("hemorragia digest",)),
        ("Oncologia digestiva", ("neoplasia", "tumor")),
        ("Pâncreas", ("pancre",)),
        ("Endoscopia", ("endoscop",)),
    ),
    "Hepatologia": (
        ("Hepatites", ("hepatite",)),
        ("Cirrose e insuficiência hepática", ("cirrose", "insuficiencia hepat",)),
        ("Tumores hepáticos", ("tumor", "neoplas")),
        ("Transplante e cirurgia hepática", ("transplante", "hepatect")),
        ("Síndromes hepatobiliares", ("icter", "hepatopatia")),
        ("Fundamentos de hepatologia", ("introducao",)),
    ),
    "Infectologia": (
        ("Infecções virais", ("arbov", "covid", "influenza", "herpes")),
        ("HIV e imunossupressão", ("hiv", "aids", "imunossuprim")),
        ("Infecções bacterianas e antimicrobianos", ("bacter", "antimicrob", "microbiol")),
        ("Tuberculose", ("tubercul",)),
        ("Infecções do sistema nervoso", ("sistema nervoso", "mening")),
        ("Infecções fúngicas e parasitárias", ("fung", "parasitos")),
        ("IST", ("sexual", "dst")),
        ("Sepse e síndromes febris", ("sepse", "febr")),
        ("Infecções respiratórias", ("pneumonia",)),
        ("Infecções relacionadas à assistência", ("iras", "assistencia")),
        ("Zoonoses e acidentes", ("peconh", "animal")),
    ),
    "Nefrologia": (
        ("Glomerulopatias", ("glomer",)),
        ("Doença renal aguda e crônica", ("renal aguda", "renal cronica", "lra", "drc")),
        ("Distúrbios hidroeletrolíticos", ("sodio", "natrem", "potass", "agua corporal")),
        ("Distúrbios acidobásicos", ("acido", "acidob")),
        ("Infecção urinária", ("infeccao urin", "itu")),
        ("Nefrolitíase", ("litias", "calculo")),
        ("Doenças tubulointersticiais", ("tubul", "interstic")),
    ),
    "Neurologia": (
        ("Doenças cerebrovasculares", ("avc", "vascular")),
        ("Consciência e coma", ("coma", "consciencia")),
        ("Epilepsias", ("epilep", "convuls")),
        ("Cefaleias", ("cefale",)),
        ("Demências", ("demenc",)),
        ("Doenças neuromusculares", ("neuromuscular",)),
        ("Distúrbios do movimento", ("movimento", "parkinson")),
        ("Neurotrauma", ("traumatismo", "tce")),
        ("Neuroimunologia", ("imune", "esclerose multipla")),
        ("Neuro-oncologia", ("tumor", "neoplas")),
        ("Sono", ("sono",)),
        ("Fundamentos de neurologia", ("anatom", "fisiolog", "semiolog")),
    ),
    "Pneumologia": (
        ("Doenças obstrutivas", ("asma", "dpoc", "obstrut")),
        ("Circulação pulmonar", ("embolia", "tromboembol", "hipertensao pulmonar")),
        ("Pleura", ("pleur", "pneumotor")),
        ("Oncologia pulmonar", ("cancer", "tumor", "neoplas")),
        ("Doenças intersticiais", ("interstic",)),
        ("Bronquiectasias", ("bronquiect" ,)),
        ("Terapia intensiva respiratória", ("intensiv", "ventila", "insuficiencia respir")),
        ("Fundamentos de pneumologia", ("introducao", "fisiolog")),
    ),
    "Dermatologia": (
        ("Dermatoses inflamatórias", ("eczem", "papuloescamos", "vesicobolh")),
        ("Infecções cutâneas e hanseníase", ("infecc", "hanseniase")),
        ("Oncologia dermatológica", ("cancer", "neoplas", "tumor")),
        ("Farmacodermias", ("farmacoderm",)),
        ("Fundamentos dermatológicos", ("anatom", "fisiolog", "lesoes elementares")),
        ("Revisão e temas diversos", ("miscel", "prova de titulo", "r+")),
    ),
    "Reumatologia": (
        ("Doenças autoimunes sistêmicas", ("lupus", "esclerod", "sjogren", "vascul", "autoimune", "tecido conjuntivo")),
        ("Artrites inflamatórias", ("artrite", "espondilo", "reumatoide")),
        ("Doenças por cristais", ("gota", "cristal")),
        ("Dor e doenças periarticulares", ("fibromial", "periart", "dor")),
        ("Osteoartrite", ("osteoartr", "artrose")),
    ),
}

CLINICAL_SPECIALTIES = frozenset(
    {
        *CLINICAL_THEME_RULES,
        "Alergia e Imunologia",
        "Nutrologia",
        "Oncologia",
    }
)

OTHER_PROMOTED_SPECIALTIES = frozenset(
    {
        "Medicina Legal",
        "Oftalmologia",
        "Ortopedia",
        "Otorrinolaringologia",
        "Psiquiatria",
    }
)


def clinical_theme(specialty: str, source_subject: str | None) -> str:
    if not (source_subject or "").strip():
        return GENERAL_THEME
    normalized_subject = _normalized(source_subject)
    for label, keywords in CLINICAL_THEME_RULES.get(specialty, ()):
        if any(_normalized(keyword) in normalized_subject for keyword in keywords):
            return label
    return "Outros conteúdos"


def derive_public_taxonomy(
    macro_area: str | None,
    source_topic: str | None,
    source_subject: str | None,
) -> dict[str, str | bool]:
    macro = (macro_area or "").strip()
    topic = (source_topic or "").strip()
    subject = (source_subject or "").strip()

    if macro in {INTERNAL_CLINICAL_MACRO, INTERNAL_OTHER_MACRO}:
        is_generic = not topic or topic == macro
        is_non_specialty_other = (
            macro == INTERNAL_OTHER_MACRO
            and topic not in OTHER_PROMOTED_SPECIALTIES
        )
        if is_generic or is_non_specialty_other:
            return {
                "especialidade": MULTIDISCIPLINARY_SPECIALTY,
                "tema": GENERAL_THEME,
                "assunto": subject or GENERAL_SUBJECT,
                "filtravel": False,
            }
        return {
            "especialidade": topic,
            "tema": clinical_theme(topic, subject),
            "assunto": subject or GENERAL_SUBJECT,
            "filtravel": True,
        }

    return {
        "especialidade": macro or MULTIDISCIPLINARY_SPECIALTY,
        "tema": topic if topic and topic != macro else GENERAL_THEME,
        "assunto": subject or GENERAL_SUBJECT,
        "filtravel": bool(macro),
    }
