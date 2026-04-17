"""Unit tests for DuckDBStore -- skipped when duckdb is not installed."""

import pytest

duckdb = pytest.importorskip("duckdb", reason="duckdb not installed")

from matadore.state.duckdb import DuckDBStore
from matadore.state.store import AssetSnapshot, StateStore


def make_store() -> DuckDBStore:
    return DuckDBStore(path=":memory:")


def make_snapshot(asset: str = "example.com", engagement_id: str = "eng-001", raw: str = "data") -> AssetSnapshot:
    return AssetSnapshot(
        engagement_id=engagement_id,
        asset=asset,
        asset_type="domain",
        checksum=DuckDBStore.checksum(raw),
        raw=raw,
    )


class TestDuckDBStore:
    def test_is_state_store(self):
        assert issubclass(DuckDBStore, StateStore)

    def test_save_and_get(self):
        store = make_store()
        snap = make_snapshot()
        store.save_snapshot(snap)
        result = store.get_snapshot("eng-001", "example.com")
        assert result is not None
        assert result.asset == "example.com"

    def test_get_missing_returns_none(self):
        store = make_store()
        assert store.get_snapshot("eng-999", "ghost.com") is None

    def test_list_snapshots_empty(self):
        store = make_store()
        assert store.list_snapshots("eng-001") == []

    def test_list_snapshots(self):
        store = make_store()
        store.save_snapshot(make_snapshot("a.com"))
        store.save_snapshot(make_snapshot("b.com"))
        results = store.list_snapshots("eng-001")
        assert len(results) == 2

    def test_delete_engagement(self):
        store = make_store()
        store.save_snapshot(make_snapshot("a.com"))
        store.delete_engagement("eng-001")
        assert store.list_snapshots("eng-001") == []

    def test_has_changed_new_asset(self):
        store = make_store()
        assert store.has_changed(make_snapshot()) is True

    def test_has_changed_identical(self):
        store = make_store()
        snap = make_snapshot(raw="stable")
        store.save_snapshot(snap)
        assert store.has_changed(make_snapshot(raw="stable")) is False

    def test_has_changed_different(self):
        store = make_store()
        store.save_snapshot(make_snapshot(raw="old"))
        assert store.has_changed(make_snapshot(raw="new")) is True

    def test_close_does_not_raise(self):
        store = make_store()
        store.close()


class TestDuckDBImportError:
    def test_import_error_message(self, monkeypatch):
        import sys
        monkeypatch.setitem(sys.modules, "duckdb", None)  # type: ignore[arg-type]
        with pytest.raises(ImportError, match="pip install duckdb"):
            DuckDBStore(path=":memory:")
