"""Unit tests for the abstract StateStore interface (via SQLiteStore)."""

from matadore.state.sqlite import SQLiteStore
from matadore.state.store import AssetSnapshot, StateStore


def make_store() -> SQLiteStore:
    return SQLiteStore(path=":memory:")


def make_snapshot(asset: str = "example.com", engagement_id: str = "eng-001", raw: str = "data") -> AssetSnapshot:
    return AssetSnapshot(
        engagement_id=engagement_id,
        asset=asset,
        asset_type="domain",
        checksum=SQLiteStore.checksum(raw),
        raw=raw,
    )


class TestStateStoreInterface:
    def test_sqlite_is_state_store(self):
        assert issubclass(SQLiteStore, StateStore)

    def test_save_and_get(self):
        store = make_store()
        snap = make_snapshot()
        store.save_snapshot(snap)
        result = store.get_snapshot("eng-001", "example.com")
        assert result is not None
        assert result.asset == "example.com"
        assert result.checksum == snap.checksum

    def test_get_missing_returns_none(self):
        store = make_store()
        assert store.get_snapshot("eng-999", "ghost.com") is None

    def test_list_snapshots_empty(self):
        store = make_store()
        assert store.list_snapshots("eng-001") == []

    def test_list_snapshots_returns_all(self):
        store = make_store()
        store.save_snapshot(make_snapshot("a.com"))
        store.save_snapshot(make_snapshot("b.com"))
        results = store.list_snapshots("eng-001")
        assets = {r.asset for r in results}
        assert "a.com" in assets
        assert "b.com" in assets

    def test_save_overwrites_existing(self):
        store = make_store()
        store.save_snapshot(make_snapshot("a.com", raw="v1"))
        store.save_snapshot(make_snapshot("a.com", raw="v2"))
        result = store.get_snapshot("eng-001", "a.com")
        assert result is not None
        assert result.raw == "v2"

    def test_delete_engagement(self):
        store = make_store()
        store.save_snapshot(make_snapshot("a.com"))
        store.save_snapshot(make_snapshot("b.com"))
        store.delete_engagement("eng-001")
        assert store.list_snapshots("eng-001") == []

    def test_delete_only_removes_target_engagement(self):
        store = make_store()
        store.save_snapshot(make_snapshot("a.com", engagement_id="eng-001"))
        store.save_snapshot(make_snapshot("b.com", engagement_id="eng-002"))
        store.delete_engagement("eng-001")
        assert store.list_snapshots("eng-001") == []
        assert len(store.list_snapshots("eng-002")) == 1

    def test_has_changed_new_asset(self):
        store = make_store()
        snap = make_snapshot()
        assert store.has_changed(snap) is True

    def test_has_changed_identical_checksum(self):
        store = make_store()
        snap = make_snapshot(raw="same data")
        store.save_snapshot(snap)
        snap2 = make_snapshot(raw="same data")
        assert store.has_changed(snap2) is False

    def test_has_changed_different_checksum(self):
        store = make_store()
        store.save_snapshot(make_snapshot(raw="old data"))
        snap2 = make_snapshot(raw="new data")
        assert store.has_changed(snap2) is True

    def test_has_changed_empty_checksum_always_true(self):
        store = make_store()
        snap = AssetSnapshot(engagement_id="eng-001", asset="x.com", asset_type="domain", checksum="", raw="")
        store.save_snapshot(snap)
        snap2 = AssetSnapshot(engagement_id="eng-001", asset="x.com", asset_type="domain", checksum="", raw="")
        assert store.has_changed(snap2) is True

    def test_close_does_not_raise(self):
        store = make_store()
        store.close()


class TestSQLiteChecksum:
    def test_checksum_returns_hex_string(self):
        result = SQLiteStore.checksum("hello")
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)

    def test_checksum_deterministic(self):
        assert SQLiteStore.checksum("data") == SQLiteStore.checksum("data")

    def test_checksum_different_inputs(self):
        assert SQLiteStore.checksum("a") != SQLiteStore.checksum("b")
