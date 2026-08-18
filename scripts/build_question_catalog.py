"""Converte um HTML de questões em um catálogo limpo e auditável do MedSync.

O arquivo de origem é usado apenas para validar estrutura e gabarito. Comentários
editoriais, vídeos e qualquer mídia externa não são incluídos no catálogo final.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import html
import json
import re
from pathlib import Path
from typing import Any

QUESTION_START = "const allQuestions = "
QUESTION_END = "const STORAGE_KEY"
MEDIA_NOUN = (
    r"(?:imagem|imagens|figura|figuras|ilustra(?:ção|ções)|fotografia|foto|"
    r"radiografia|tomografia|ultrassonografia|ecografia|uretrocistografia|"
    r"cintilografia|eletrocardiograma|traçado|gráfico|tabela|quadro)"
)
EXPLICIT_IMAGE_PATTERN = re.compile(
    rf"\b{MEDIA_NOUN}\b.{{0,55}}\b(?:abaixo|acima|a seguir|ao lado|anex[ao]|"
    rf"apresentad[ao]|demonstrad[ao]|reproduzid[ao]|ilustrad[ao]|fornecid[ao]|"
    rf"representad[ao])\b|"
    rf"\b(?:abaixo|acima|a seguir)\b.{{0,35}}\b{MEDIA_NOUN}\b|"
    rf"\b(?:segue|observe|analise|considere|veja)\b.{{0,45}}\b{MEDIA_NOUN}\b|"
    r"\b(?:mostra|evidencia|apresenta|com)\s+(?:a\s+)?seguinte\s+imagem\b|"
    r"\b(?:pela|conforme)\s+(?:a\s+)?imagem\b|"
    r"\bde\s+acordo\s+com.{0,35}\bimagem\b|"
    r"\b(?:figura|figuras|ilustração|ilustrações)\b|"
    r"\bimagem\s+(?:do\s+caderno|tomográfica\s+apresentada|demonstrada|"
    r"apresentada|reproduzida)\b|"
    r"\b(?:achado|alterações|diagnóstico|lesão|conduta)\b.{0,35}\bna\s+imagem\b",
    re.IGNORECASE,
)
ALTERNATIVE_MEDIA_PLACEHOLDER = re.compile(
    r"\b(?:ver|vide|consultar)\s+(?:a\s+)?(?:imagem|figura)\b", re.IGNORECASE
)
UNSUPPORTED_MARKUP = re.compile(
    r"<(img|table|svg|math|iframe|object|embed)\b", re.IGNORECASE
)
ANSWER_PATTERN = re.compile(
    r"(?:resposta|gabarito)\s*[:\-]?\s*(?:letra|alternativa)?\s*([A-E])\b",
    re.IGNORECASE,
)

TOPIC_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Trauma e emergência",
        (
            "trauma", "politrauma", "ferimento", "arma de fogo", "arma branca",
            "atls", "fast", "choque hemorrágico", "queimadura", "acidente",
        ),
    ),
    (
        "Ortopedia",
        (
            "fratura", "luxação", "ortop", "osteomielite", "ligamento",
            "menisco", "joelho", "quadril", "coluna", "membro inferior",
        ),
    ),
    (
        "Urologia",
        (
            "uretra", "bexiga", "próstata", "renal", "rim", "ureter",
            "urolitíase", "testículo", "escroto", "hematúria", "urolog",
        ),
    ),
    (
        "Neurocirurgia",
        (
            "traumatismo cran", "hematoma epidural", "hematoma subdural",
            "hemorragia subarac", "hipertensão intracran", "herniação cerebral",
            "neurocir", "lesão medular",
        ),
    ),
    (
        "Cirurgia vascular",
        (
            "aneurisma", "isquemia de membro", "trombose arterial", "carótida",
            "aorta", "vascular", "varizes", "pé diabético",
        ),
    ),
    (
        "Cirurgia torácica",
        (
            "tórax", "torác", "pneumotórax", "hemotórax", "dreno de tórax",
            "mediastino", "pulmão", "pleura",
        ),
    ),
    (
        "Cabeça e pescoço",
        (
            "tireoide", "paratireoide", "pescoço", "glândula salivar", "laringe",
            "traqueostomia",
        ),
    ),
    (
        "Cirurgia pediátrica",
        (
            "recém-nascido", "lactente", "criança", "pediátr", "invaginação",
            "onfalocele", "gastrosquise", "estenose hipertrófica",
        ),
    ),
    (
        "Transplantes",
        ("transplante", "doador", "rejeição", "morte encefálica"),
    ),
    (
        "Perioperatório",
        (
            "pré-operatório", "pós-operatório", "perioperatório", "anestesia",
            "risco cirúrgico", "profilaxia cirúrgica", "infecção de sítio",
        ),
    ),
    (
        "Aparelho digestivo",
        (
            "abdome", "abdominal", "apendic", "colecist", "pâncreas", "hepát",
            "fígado", "intestin", "cólon", "reto", "esôfago", "estômago",
            "hérnia", "obstrução intestinal", "doença inflamatória intestinal",
        ),
    ),
)


def plain_text(value: str) -> str:
    value = re.sub(r"<br\s*/?>", "\n", value or "", flags=re.IGNORECASE)
    value = re.sub(r"</?(p|div|ul|ol|li|tr|h[1-6])\b[^>]*>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value).replace("\x00", "")
    lines = [re.sub(r"\s+", " ", line).strip() for line in value.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def normalize(value: str) -> str:
    return re.sub(r"\W+", " ", plain_text(value).casefold()).strip()


def load_questions(path: Path) -> list[dict[str, Any]]:
    source = path.read_text(encoding="utf-8")
    start = source.index(QUESTION_START) + len(QUESTION_START)
    storage = source.index(QUESTION_END, start)
    end = source.rfind("];", start, storage) + 1
    return json.loads(source[start:end])


def classify_topic(statement: str, alternatives: list[dict[str, Any]]) -> str:
    content = normalize(
        f"{statement} {' '.join(str(item.get('texto', '')) for item in alternatives)}"
    )
    scores = [
        (sum(term in content for term in terms), topic)
        for topic, terms in TOPIC_RULES
    ]
    score, topic = max(scores, key=lambda item: item[0])
    return topic if score else "Cirurgia geral"


def validated_records(questions: list[dict[str, Any]]) -> tuple[list[dict], dict]:
    first_by_id: dict[int, dict[str, Any]] = {}
    for question in questions:
        first_by_id.setdefault(int(question["id"]), question)

    seen_statements: set[str] = set()
    records: list[dict[str, Any]] = []
    rejected = {
        "duplicada": len(questions) - len(first_by_id),
        "enunciado_repetido": 0,
        "anulada": 0,
        "alternativas_invalidas": 0,
        "alternativas_repetidas": 0,
        "gabarito_inconsistente": 0,
        "midia_ausente": 0,
        "marcacao_complexa": 0,
    }

    for question in first_by_id.values():
        statement_key = normalize(question.get("enunciado", ""))
        if not statement_key:
            rejected["enunciado_repetido"] += 1
            continue
        if statement_key in seen_statements:
            rejected["enunciado_repetido"] += 1
            continue

        if question.get("anulada"):
            rejected["anulada"] += 1
            continue

        alternatives = question.get("alternativas") or []
        correct = [item for item in alternatives if item.get("correta")]
        letters = [str(item.get("letra", "")).strip() for item in alternatives]
        valid_letters = all(letter in {"A", "B", "C", "D", "E"} for letter in letters)
        has_text = all(plain_text(str(item.get("texto", ""))) for item in alternatives)
        if (
            len(alternatives) < 2
            or len(correct) != 1
            or not valid_letters
            or len(set(letters)) != len(letters)
            or not has_text
        ):
            rejected["alternativas_invalidas"] += 1
            continue

        normalized_alternatives = [
            normalize(str(item.get("texto", ""))) for item in alternatives
        ]
        if len(set(normalized_alternatives)) != len(normalized_alternatives):
            rejected["alternativas_repetidas"] += 1
            continue

        combined_markup = " ".join(
            [question.get("enunciado", "")]
            + [str(item.get("texto", "")) for item in alternatives]
        )
        statement = plain_text(question.get("enunciado", ""))
        if EXPLICIT_IMAGE_PATTERN.search(statement) or any(
            ALTERNATIVE_MEDIA_PLACEHOLDER.search(str(item.get("texto", "")))
            for item in alternatives
        ):
            rejected["midia_ausente"] += 1
            continue
        if UNSUPPORTED_MARKUP.search(combined_markup):
            rejected["marcacao_complexa"] += 1
            continue

        answers_in_comment = ANSWER_PATTERN.findall(plain_text(question.get("comentario", "")))
        marked_answer = str(correct[0]["letra"]).upper()
        if not answers_in_comment or answers_in_comment[-1].upper() != marked_answer:
            rejected["gabarito_inconsistente"] += 1
            continue

        clean_alternatives = [
            {"id": str(item["letra"]).upper(), "texto": plain_text(item["texto"])}
            for item in alternatives
        ]
        year = int(question["ano"])
        header = plain_text(question["cabecalho"])
        institution = re.sub(r"^\d{4}\s*", "", header).strip()
        fingerprint = hashlib.sha256(statement_key.encode("utf-8")).hexdigest()
        seen_statements.add(statement_key)
        records.append(
            {
                "id": int(question["id"]),
                "ano": year,
                "instituicao": institution,
                "cabecalho": header,
                "especialidade": "Cirurgia",
                "assunto": classify_topic(statement, clean_alternatives),
                "enunciado": statement,
                "alternativas": clean_alternatives,
                "alternativa_correta_id": marked_answer,
                "fingerprint": fingerprint,
                "status": "publicada",
            }
        )

    report = {
        "registros_origem": len(questions),
        "ids_unicos": len(first_by_id),
        "publicaveis": len(records),
        "rejeitados": rejected,
    }
    return records, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    records, report = validated_records(load_questions(args.source))
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    encoder = json.JSONEncoder(ensure_ascii=False, separators=(",", ":"))
    with args.destination.open("wb") as raw_handle:
        with gzip.GzipFile(
            filename="question_catalog.json",
            mode="wb",
            fileobj=raw_handle,
            mtime=0,
        ) as compressed_handle:
            for chunk in encoder.iterencode(records):
                compressed_handle.write(chunk.encode("utf-8"))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
