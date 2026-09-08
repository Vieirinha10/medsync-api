"""Explicit, disabled-by-default execution of the fixed backed-up repair batch."""
import hashlib
import json
import os
from pathlib import Path

from sqlalchemy import select


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), default=str).encode()).hexdigest()


def run_requested_repair():
    mode = os.getenv('QUESTION_QUALITY_REPAIR_MODE', '')
    if mode not in {'dry-run', 'apply'}:
        return
    from database import engine
    from models import ExamQuestion
    from scripts.analyze_quality_snapshot import analyze
    from scripts.apply_question_quality_repairs import execute_plan

    path = Path(__file__).resolve().parents[1] / 'data/question_quality_repair_manifest.json'
    manifest = json.loads(path.read_text())
    if os.getenv('QUESTION_QUALITY_REPAIR_PLAN_SHA256') != manifest['plan_sha256']:
        raise ValueError('Repair plan acknowledgement missing')
    if not manifest.get('backup_library_id') or len(manifest['items']) != 1304:
        raise ValueError('Unexpected repair manifest')
    table = ExamQuestion.__table__
    plan = []
    at_target = 0
    with engine.connect() as conn:
        for item in manifest['items']:
            row = conn.execute(select(*(table.c[k] for k in manifest['columns'])).where(
                table.c.id == item['id'])).mappings().one()
            # Same serialization as the verified exported snapshot.
            record = json.loads(json.dumps(dict(row), default=str))
            current = digest(record)
            if current == item['after']:
                at_target += 1
                continue
            if current != item['before']:
                raise ValueError(f'Stale snapshot ID {item["id"]}')
            proposal = analyze(record)['proposal']
            if not proposal or digest(proposal['set']) != item['patch']:
                raise ValueError(f'Unexpected generated repair ID {item["id"]}')
            plan.append(proposal)
    if at_target:
        if plan:
            raise ValueError('Mixed state; manual investigation required')
        result = {'requested': 1304, 'changed': 0, 'already_at_target': at_target,
                  'committed': False}
    else:
        result = execute_plan(engine, table, plan, manifest['applied_at'], apply=mode == 'apply')
    print('QUESTION_QUALITY_REPAIR_DONE ' + json.dumps({
        'mode': mode, 'plan_sha256': manifest['plan_sha256'], **result}), flush=True)
