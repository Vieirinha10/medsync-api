import pathlib
import sys
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

API_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from services import question_catalog_audit as audit


def test_json_value_normalizes_postgres_decimal():
    assert audit._json_value(Decimal("12")) == 12
    assert audit._json_value(Decimal("1.25")) == 1.25


class _Result:
    def __init__(self, rows=None):
        self.rows = rows or [{"questions": 10}]

    def mappings(self):
        return self

    def all(self):
        return self.rows

    def one(self):
        return self.rows[0]


class _Transaction:
    def __init__(self):
        self.rolled_back = False

    def rollback(self):
        self.rolled_back = True


class _Connection:
    dialect = SimpleNamespace(name="postgresql")

    def __init__(self):
        self.statements = []
        self.transaction = _Transaction()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def begin(self):
        return self.transaction

    def execute(self, statement):
        self.statements.append(str(statement))
        if "MIN(id) AS min_id" in str(statement):
            return _Result([{"min_id": None, "max_id": None}])
        return _Result()


def test_audit_enforces_read_only_transaction_and_emits_sections():
    connection = _Connection()
    messages = []

    audit.run_question_catalog_audit(
        "test-run", connect=lambda: connection, emit=messages.append
    )

    assert connection.statements[0] == "SET TRANSACTION READ ONLY"
    assert connection.transaction.rolled_back is True
    assert len([item for item in messages if "_SECTION " in item]) == (
        len(audit._QUERIES) + 1
    )
    sql = " ".join(connection.statements).upper()
    assert not any(token in sql for token in (" INSERT ", " UPDATE ", " DELETE "))


def test_start_requested_audit_is_disabled_without_run_id(monkeypatch):
    monkeypatch.delenv(audit.AUDIT_ENV, raising=False)
    assert audit.start_requested_audit() is False


def test_start_requested_audit_claims_one_lock(monkeypatch, tmp_path):
    monkeypatch.setenv(audit.AUDIT_ENV, "quality-2026")
    monkeypatch.setattr(audit, "Path", lambda _: Path(tmp_path / "audit.lock"))

    started = []

    class ImmediateThread:
        def __init__(self, target, args, **_):
            self.target = target
            self.args = args

        def start(self):
            started.append(self.args)

    monkeypatch.setattr(audit.threading, "Thread", ImmediateThread)

    assert audit.start_requested_audit() is True
    assert audit.start_requested_audit() is False
    assert started == [("quality-2026",)]
