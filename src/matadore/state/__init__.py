"""Matadore state persistence layer.

Provides caching of engagement results so repeated scans only re-process
assets that have changed since the last run.

Two backends are available:

- :class:`~matadore.state.sqlite.SQLiteStore` -- local, zero-dependency,
  single-user.  Default backend.
- :class:`~matadore.state.duckdb.DuckDBStore` -- team-shared, requires the
  ``duckdb`` package.

Usage::

    from matadore.state import SQLiteStore, DuckDBStore, AssetSnapshot

    store = SQLiteStore()                    # default local store
    store = SQLiteStore(path=":memory:")     # in-memory (tests)
    store = DuckDBStore(path="/shared/...")  # team-shared
"""

from matadore.state.duckdb import DuckDBStore
from matadore.state.sqlite import SQLiteStore
from matadore.state.store import AssetSnapshot, StateStore

__all__ = [
    "AssetSnapshot",
    "DuckDBStore",
    "SQLiteStore",
    "StateStore",
]
