"""Atomic, guarded CLI for the reviewed repair plan; defaults to rollback dry-run."""
import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select, text, update

from scripts.question_quality_review import inspect_row

ALLOWED = {'statement_plain', 'enunciado', 'alternativas', 'content_hash_plain',
           'content_hash_rich', 'answer_binding_hash', 'random_rank'}


def normalized(value):
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat()
    return value


def matches(row, expected):
    for key, value in expected.items():
        actual = row.get(key)
        if key == 'updated_at' and value is not None:
            value = normalized(datetime.fromisoformat(value))
        if normalized(actual) != value:
            return False
    return True


def validate_plan(plan):
    if not plan or len({p['id'] for p in plan}) != len(plan):
        raise ValueError('Empty plan or duplicate IDs')
    for p in plan:
        before = p['expected']
        if (before['id'] != p['id'] or before['catalog_version'] != 'v2'
                or before['status'] != 'publicada' or not before.get('updated_at')):
            raise ValueError('Invalid scope or missing timestamp guard')
        if not p['set'] or not set(p['set']) <= ALLOWED:
            raise ValueError('Forbidden write fields')
        after = {**before, **p['set']}
        if inspect_row(after):
            raise ValueError('Repair does not pass integrity validation')
        if before['content_hash_rich'] != after['content_hash_rich']:
            raise ValueError('Rich content must remain unchanged')
        for old, new in zip(before['alternativas'], after['alternativas'], strict=True):
            for key in set(old) | set(new):
                if key not in {'body_plain', 'texto'} and old.get(key) != new.get(key):
                    raise ValueError('Alternative identity, answer or HTML changed')


def execute_plan(engine, table, plan, applied_at, *, apply=False, reverse=False,
                 validator=validate_plan):
    """Validate every locked row before writes; rollback whole batch on any error."""
    validator(plan)
    timestamp = datetime.fromisoformat(applied_at)
    if timestamp.tzinfo is None:
        raise ValueError('Timezone required')
    keys = set(plan[0]['expected'])
    if any(set(p['expected']) != keys for p in plan):
        raise ValueError('Inconsistent guard fields')
    ids = sorted(p['id'] for p in plan)
    planned = {p['id']: p for p in plan}
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            if conn.dialect.name == 'postgresql':
                conn.execute(text("SET LOCAL lock_timeout = '5s'"))
                conn.execute(text("SET LOCAL statement_timeout = '180s'"))
            rows = {}
            for offset in range(0, len(ids), 100):
                query = select(*(table.c[k] for k in sorted(keys))).where(
                    table.c.id.in_(ids[offset:offset + 100])).order_by(table.c.id).with_for_update()
                rows.update({r['id']: dict(r) for r in conn.execute(query).mappings()})
            if set(rows) != set(ids):
                raise ValueError('Missing records; no changes applied')
            operations = []
            for id in ids:
                p = planned[id]
                before = p['expected']
                after = {**before, **p['set'], 'updated_at': timestamp.isoformat()}
                expected, target = (after, before) if reverse else (before, after)
                if matches(rows[id], target):
                    continue
                if not matches(rows[id], expected):
                    raise ValueError(f'Concurrent or unexpected changes: ID {id}')
                changes = {k: target[k] for k in p['set']}
                changes['updated_at'] = datetime.fromisoformat(target['updated_at'])
                operations.append((id, changes, target))
            for id, changes, _ in operations:
                result = conn.execute(update(table).where(table.c.id == id).values(**changes))
                if result.rowcount != 1:
                    raise ValueError(f'Unexpected updated row count: ID {id}')
            for id, _, target in operations:
                actual = conn.execute(select(*(table.c[k] for k in sorted(keys))).where(
                    table.c.id == id)).mappings().one()
                if not matches(actual, target):
                    raise ValueError(f'Post-write verification failed: ID {id}')
            if apply:
                transaction.commit()
            else:
                transaction.rollback()
            return {'requested': len(ids), 'changed': len(operations),
                    'already_at_target': len(ids) - len(operations),
                    'committed': apply, 'reverse': reverse, 'applied_at': applied_at}
        except BaseException:
            if transaction.is_active:
                transaction.rollback()
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--applied-at', required=True)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--reverse', action='store_true')
    parser.add_argument('--encoding', action='store_true')
    args = parser.parse_args()
    raw = args.plan.read_bytes()
    if hashlib.sha256(raw).hexdigest() != args.sha256:
        raise ValueError('Plan checksum mismatch')
    from database import engine
    from models import ExamQuestion
    from scripts.repair_question_encoding import validate_encoding_plan

    result = execute_plan(engine, ExamQuestion.__table__, json.loads(raw), args.applied_at,
                          apply=args.apply, reverse=args.reverse,
                          validator=validate_encoding_plan if args.encoding else validate_plan)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
