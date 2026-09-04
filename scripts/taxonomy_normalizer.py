"""
scripts/taxonomy_normalizer.py
Módulo canônico e centralizado de normalização de taxonomia médica para o MedSync.
Garante que tópicos em formato de dicionário ou com delimitadores [$$] sejam
sempre convertidos nas Grandes Áreas e Subespecialidades padronizadas.
"""

import json
import re
from typing import Optional, Tuple

MAIN_SPECIALTIES = {
    "Clínica Médica", "Cirurgia", "Pediatria", "Ginecologia",
    "Obstetrícia", "Medicina Preventiva"
}

VALID_OTHER_SPECIALTIES = {
    "Psiquiatria", "Ortopedia", "Oftalmologia", "Otorrinolaringologia",
    "Dermatologia", "Medicina Legal", "Radiologia", "Anestesiologia"
}

def clean_taxonomy_string(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    cleaned = str(s).strip()
    cleaned = re.sub(r"^\{['\"]n['\"]\s*:\s*['\"]", "", cleaned)
    cleaned = re.sub(r"['\"].*$", "", cleaned)
    cleaned = cleaned.strip()
    return cleaned if cleaned else None

def parse_canonical_taxonomy(topics_raw) -> Tuple[str, Optional[str], Optional[str], str]:
    """
    Retorna:
    (especialidade, tema, subtema, assunto)
    Todos 100% limpos, sem delimitadores [$$] e sem estruturas de dicionário serializado.
    """
    if not topics_raw:
        return "Clínica Médica", None, None, "Clínica Médica"

    data = None
    if isinstance(topics_raw, str):
        try:
            data = json.loads(topics_raw)
        except Exception:
            try:
                import ast
                data = ast.literal_eval(topics_raw)
            except Exception:
                pass
    elif isinstance(topics_raw, (list, dict)):
        data = topics_raw

    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list) or not data:
        return "Clínica Médica", None, None, "Clínica Médica"

    paths = []
    for item in data:
        if isinstance(item, dict):
            p = item.get("p") or ""
            if p:
                parts = [x.strip() for x in p.split("[$$]") if x.strip()]
                if parts:
                    paths.append((len(parts), parts))
        elif isinstance(item, str):
            parts = [x.strip() for x in item.split("[$$]") if x.strip()]
            if parts:
                paths.append((len(parts), parts))

    if not paths:
        return "Clínica Médica", None, None, "Clínica Médica"

    # Seleciona o caminho mais profundo para maior especificidade
    paths.sort(key=lambda x: x[0], reverse=True)
    best_parts = paths[0][1]

    raw_root = best_parts[0]
    low_root = raw_root.lower()

    if "clínica" in low_root or "clinica" in low_root:
        spec = "Clínica Médica"
    elif "cirurg" in low_root:
        spec = "Cirurgia"
    elif "pediatr" in low_root:
        spec = "Pediatria"
    elif "gineco" in low_root:
        spec = "Ginecologia"
    elif "obstetr" in low_root:
        spec = "Obstetrícia"
    elif "preventiv" in low_root or "saúde coletiva" in low_root or "sus" in low_root or "epidemiol" in low_root:
        spec = "Medicina Preventiva"
    elif raw_root == "Outros":
        if len(best_parts) > 1 and best_parts[1] in VALID_OTHER_SPECIALTIES:
            spec = best_parts[1]
        else:
            spec = "Outros"
    elif raw_root in MAIN_SPECIALTIES or raw_root in VALID_OTHER_SPECIALTIES:
        spec = raw_root
    else:
        spec = "Outros"

    tema = None
    subtema = None

    if len(best_parts) > 1:
        tema = clean_taxonomy_string(best_parts[1])
    if len(best_parts) > 2:
        subtema = clean_taxonomy_string(best_parts[2])

    assunto = tema if tema else spec

    return spec, tema, subtema, assunto
