from pathlib import Path
import importlib

from algo_royale.clients.db.migrations.migration_manager import MigrationManager
from algo_royale.logging.loggable import Loggable


class DummyLogger(Loggable):
    def debug(self, *a, **k):
        pass

    def info(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass

    def error(self, *a, **k):
        pass


class MockCursor:
    def __init__(self, applied_versions):
        # applied_versions: list of version strings (stems)
        self._applied = applied_versions
        self._last_query = None

    def execute(self, query, params=None):
        self._last_query = (query or "").strip()

    def fetchone(self):
        # to_regclass('public.schema_migrations') call -> return non-null to indicate table exists
        if 'to_regclass' in (self._last_query or ''):
            return ('schema_migrations',)
        # other one-off fetchone usages return simple markers
        return None

    def fetchall(self):
        # SELECT version FROM schema_migrations;
        return [(v,) for v in self._applied]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class MockConn:
    def __init__(self, applied_versions):
        self._applied = applied_versions

    def cursor(self):
        return MockCursor(self._applied)

    def close(self):
        # mimic real connection close
        pass


def test_verify_migrations_all_and_missing(tmp_path):
    """Test verify_migrations returns True when all migration files are applied and False when missing."""
    mm = MigrationManager(DummyLogger())

    # locate the migrations folder used by the module and create two test migration files
    mod = importlib.import_module('algo_royale.clients.db.migrations.migration_manager')
    migrations_folder = Path(mod.__file__).parent / 'migrations'
    migrations_folder.mkdir(parents=True, exist_ok=True)

    f1 = migrations_folder / 'zz_test_001.sql'
    f2 = migrations_folder / 'zz_test_002.sql'
    # write small contents (these are only used for discovery by verify_migrations)
    f1.write_text('-- test migration 1')
    f2.write_text('-- test migration 2')

    try:
        # Case 1: both files applied
        conn_ok = MockConn(['zz_test_001', 'zz_test_002'])
        assert mm.verify_migrations(conn_ok) is True

        # Case 2: only first applied -> should be considered not initialized
        conn_missing = MockConn(['zz_test_001'])
        assert mm.verify_migrations(conn_missing) is False
    finally:
        # cleanup test files
        try:
            f1.unlink()
        except Exception:
            pass
        try:
            f2.unlink()
        except Exception:
            pass
