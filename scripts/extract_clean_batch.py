#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_clean_batch.py
Extrator canônico de lotes de questões limpas para o catálogo MedSync v2.
Cruza clean-review-candidates-v2.1.csv.gz com questoes.db, aplica sanitização
estrita, gera hashes SHA-256 e produz JSONL pronto para ingestão atômica.
"""

import argparse
import collections
import csv
import gzip
import hashlib
import html
from html.parser import HTMLParser
import json
import os
import pathlib
import re
import sqlite3
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

ALLOWED_TAGS = {
    'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'sub', 'sup',
    'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td',
    'blockquote', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
}

ALLOWED_ATTRIBUTES = {
    'th': {'colspan', 'rowspan', 'scope', 'align'},
    'td': {'colspan', 'rowspan', 'align'},
    'ol': {'start', 'type'},
    'ul': {'type'}
}

DROP_CONTENTS_TAGS = {
    'script', 'style', 'iframe', 'video', 'audio', 'object', 'embed',
    'form', 'input', 'button', 'textarea', 'select', 'option',
    'frame', 'frameset', 'applet', 'meta', 'link'
}

class MedicalHTMLSanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.result: List[str] = []
        self.drop_depth = 0

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]):
        tag_lower = tag.lower()
        if tag_lower in DROP_CONTENTS_TAGS:
            self.drop_depth += 1
            return
        if self.drop_depth > 0:
            return

        if tag_lower in ALLOWED_TAGS:
            clean_attrs = []
            allowed_for_tag = ALLOWED_ATTRIBUTES.get(tag_lower, set())
            for attr_name, attr_val in attrs:
                attr_name_lower = attr_name.lower()
                if attr_name_lower.startswith('on') or 'javascript:' in (attr_val or '').lower():
                    continue
                if attr_name_lower in allowed_for_tag:
                    escaped_val = html.escape(str(attr_val), quote=True)
                    clean_attrs.append(f'{attr_name_lower}="{escaped_val}"')

            attrs_str = f" {' '.join(clean_attrs)}" if clean_attrs else ""
            if tag_lower == 'br':
                self.result.append("<br />")
            else:
                self.result.append(f"<{tag_lower}{attrs_str}>")

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        if tag_lower in DROP_CONTENTS_TAGS:
            if self.drop_depth > 0:
                self.drop_depth -= 1
            return
        if self.drop_depth > 0:
            return

        if tag_lower in ALLOWED_TAGS and tag_lower != 'br':
            self.result.append(f"</{tag_lower}>")

    def handle_data(self, data: str):
        if self.drop_depth == 0 and data:
            self.result.append(html.escape(data, quote=False))

    def get_sanitized_html(self) -> str:
        raw_out = "".join(self.result)
        raw_out = re.sub(r'[ \t]+', ' ', raw_out)
        raw_out = re.sub(r'(\s*<br />\s*){3,}', '<br /><br />', raw_out)
        return raw_out.strip()

def sanitize_to_rich_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    sanitizer = MedicalHTMLSanitizer()
    sanitizer.feed(raw_html)
    return sanitizer.get_sanitized_html()

def sanitize_to_plain_text(raw_html: str) -> str:
    if not raw_html:
        return ""
    text = html.unescape(raw_html)
    text = text.replace('\xa0', ' ').replace('\u200b', '').replace('\ufeff', '')
    text = re.sub(r'</(?:p|div|li|tr|h\d)>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<(?:br|hr)[\s/>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.split('\n')]
    cleaned = '\n'.join(lines)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned).strip()
    return cleaned

def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def is_safe_html(html_str: str) -> bool:
    if not html_str:
        return True
    lower = html_str.lower()
    for forbidden in ['<script', '<iframe', '<video', '<audio', '<object', '<embed', 'onclick', 'javascript:', '<form', '<input']:
        if forbidden in lower:
            return False
    return True

def parse_topics_metadata(topics_json: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    if not topics_json:
        return None, None, None
    try:
        data = json.loads(topics_json)
        if isinstance(data, list) and data and isinstance(data[0], dict) and data[0].get("p"):
            parts = [p.strip() for p in data[0]["p"].split("[$$]") if p.strip()]
            spec = parts[0] if len(parts) > 0 else None
            tema = parts[1] if len(parts) > 1 else None
            subtema = parts[2] if len(parts) > 2 else None
            return spec, tema, subtema
    except Exception:
        pass
    return None, None, None

EXCLUDED_TOPICS = {
    "Direito",
    "Língua Portuguesa (Português)",
    "USMLE",
    "Informática",
    "Outros",
    "Raciocínio Lógico",
    "Inglês",
    "Maus tratos à crianças e adolescentes",
    "Matemática",
    "Atualidades",
    "Sexualidade",
    "Formação Geral - ENADE"
}

def extract_batch(
    clean_csv_gz: pathlib.Path,
    db_path: pathlib.Path,
    output_jsonl: pathlib.Path,
    years: Optional[List[int]] = None,
    limit: Optional[int] = None
) -> int:
    t0 = time.time()
    target_ids: List[str] = []
    years_set = {str(y) for y in years} if years else None
    years_label = ", ".join(str(y) for y in sorted(years)) if years else "Todos"
    print(f"Lendo candidatos limpos de: {clean_csv_gz}")
    with gzip.open(clean_csv_gz, "rt", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if years_set is not None and str(row.get("year")) not in years_set:
                continue
            if row.get("topic") in EXCLUDED_TOPICS:
                continue
            target_ids.append(row["question_id"])

    if limit:
        target_ids = target_ids[:limit]

    total_target = len(target_ids)
    print(f"Total de questões selecionadas para extração: {total_target:,} (Anos: {years_label})")

    if total_target == 0:
        print("Nenhuma questão encontrada para os critérios informados.")
        return 0

    print(f"Conectando ao banco de dados SQLite: {db_path}")
    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro&immutable=1", uri=True)
    cur = conn.cursor()

    # 1. Carregar alternativas dos IDs alvo
    print("Carregando alternativas...")
    alts_map: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)
    chunk_size = 990
    for i in range(0, total_target, chunk_size):
        chunk = target_ids[i:i + chunk_size]
        placeholders = ",".join("?" for _ in chunk)
        cur.execute(
            f"SELECT question_id, letter, body, correct, answer_pct FROM alternatives WHERE question_id IN ({placeholders}) ORDER BY question_id, rowid",
            chunk
        )
        for qid, letter, body, correct, answer_pct in cur.fetchall():
            alts_map[str(qid)].append({
                "letter": str(letter or "").strip(),
                "body": body or "",
                "correct": bool(correct),
                "answer_pct": answer_pct
            })

    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    written_count = 0
    skipped_count = 0

    print("Processando e gerando registros canônicos JSONL...")
    with open(output_jsonl, "w", encoding="utf-8") as out_f:
        for i in range(0, total_target, chunk_size):
            chunk = target_ids[i:i + chunk_size]
            placeholders = ",".join("?" for _ in chunk)
            cur.execute(
                f"""
                SELECT id, statement, answer_type, year, institution, banca, finalidade, region, topics, correct_letter, has_video, video_url
                FROM questions
                WHERE id IN ({placeholders})
                ORDER BY id
                """,
                chunk
            )
            rows = cur.fetchall()
            for row in rows:
                (
                    qid, statement, ans_type, yr, inst, banca, fin, reg,
                    topics_json, corr_letter, has_vid, vid_url
                ) = row
                qid_str = str(qid)
                stmt_raw = statement or ""
                stmt_plain = sanitize_to_plain_text(stmt_raw)
                stmt_rich = sanitize_to_rich_html(stmt_raw)

                if not stmt_plain or len(stmt_plain.strip()) < 5:
                    skipped_count += 1
                    continue

                if not is_safe_html(stmt_rich):
                    skipped_count += 1
                    continue

                raw_alts = alts_map.get(qid_str, [])
                if len(raw_alts) < 2:
                    skipped_count += 1
                    continue

                norm_alts = []
                correct_letters = []
                letters_seen = set()

                for a in raw_alts:
                    let = a["letter"]
                    if not let or let in letters_seen:
                        continue
                    letters_seen.add(let)

                    b_plain = sanitize_to_plain_text(a["body"])
                    b_rich = sanitize_to_rich_html(a["body"])

                    if not is_safe_html(b_rich):
                        continue

                    is_corr = a["correct"]
                    if is_corr:
                        correct_letters.append(let)

                    norm_alts.append({
                        "letter": let,
                        "body_plain": b_plain,
                        "body_rich_html": b_rich,
                        "is_correct": is_corr,
                        "answer_pct": a["answer_pct"],
                        "sha256_plain": compute_sha256(b_plain),
                        "sha256_rich": compute_sha256(b_rich)
                    })

                corr_letter_str = str(corr_letter or "").strip()
                if len(correct_letters) != 1 or correct_letters[0] != corr_letter_str or corr_letter_str not in letters_seen:
                    skipped_count += 1
                    continue

                # Hashes canônicos obrigatórios
                sorted_alts = sorted(norm_alts, key=lambda x: x["letter"])
                alts_plain_payload = "|".join(f"{a['letter']}:{a['body_plain']}" for a in sorted_alts)
                alts_rich_payload = "|".join(f"{a['letter']}:{a['body_rich_html']}" for a in sorted_alts)
                content_hash_plain = compute_sha256(f"{stmt_plain}||{alts_plain_payload}")
                content_hash_rich = compute_sha256(f"{stmt_rich}||{alts_rich_payload}")

                alts_binding_payload = "|".join(f"{a['letter']}:{1 if a['is_correct'] else 0}" for a in sorted_alts)
                answer_binding_hash = compute_sha256(f"{content_hash_plain}||{corr_letter_str}||{alts_binding_payload}")

                spec, tema, subtema = parse_topics_metadata(topics_json)
                had_vid = bool(has_vid == 1 or (vid_url and vid_url.strip()))

                record = {
                    "source_id": qid_str,
                    "tipo_prova": ans_type.strip() if ans_type else None,
                    "ano": int(yr) if yr is not None else None,
                    "instituicao": inst.strip() if inst else None,
                    "banca": banca.strip() if banca else None,
                    "finalidade": fin.strip() if fin else None,
                    "regiao": reg.strip() if reg else None,
                    "especialidade": spec,
                    "tema": tema,
                    "subtema": subtema,
                    "statement_plain": stmt_plain,
                    "statement_rich_html": stmt_rich,
                    "alternatives": norm_alts,
                    "correct_letter": corr_letter_str,
                    "content_hash_plain": content_hash_plain,
                    "content_hash_rich": content_hash_rich,
                    "answer_binding_hash": answer_binding_hash,
                    "explanation_status": "PENDING",
                    "publication_status": "ACTIVE",
                    "quarantine_reasons": [],
                    "media_classification": "NO_VISUAL_DEPENDENCY",
                    "image_rights_status": "NONE_REQUIRED",
                    "image_urls": [],
                    "source_had_video": had_vid,
                    "has_video": False
                }

                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                written_count += 1

    conn.close()
    elapsed = time.time() - t0
    print(f"\nExtração concluída em {elapsed:.2f}s:")
    print(f"  Gravados: {written_count:,} registros em {output_jsonl}")
    print(f"  Ignorados: {skipped_count:,}")
    return written_count

def main():
    parser = argparse.ArgumentParser(description="Extrator de lotes de questões limpas para o MedSync v2")
    parser.add_argument("--clean-candidates-csv", type=str, required=True, help="Caminho do CSV.GZ de candidatos limpos")
    parser.add_argument("--db-path", type=str, required=True, help="Caminho do banco SQLite questoes.db")
    parser.add_argument("--output-jsonl", type=str, required=True, help="Arquivo de destino JSONL")
    parser.add_argument("--year", type=int, default=None, help="Filtrar por ano específico (ex.: 2026)")
    parser.add_argument("--years", type=int, nargs="+", default=None, help="Filtrar por múltiplos anos (ex.: 2025 2024)")
    parser.add_argument("--limit", type=int, default=None, help="Limite de questões a extrair")

    args = parser.parse_args()
    selected_years = args.years if args.years else ([args.year] if args.year is not None else None)

    extract_batch(
        clean_csv_gz=pathlib.Path(args.clean_candidates_csv),
        db_path=pathlib.Path(args.db_path),
        output_jsonl=pathlib.Path(args.output_jsonl),
        years=selected_years,
        limit=args.limit
    )

if __name__ == "__main__":
    main()
