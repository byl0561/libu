"""Lightweight, Alembic-free schema migrations for SQLite.

The on-disk schema is tracked with SQLite's ``PRAGMA user_version``. On every
startup :func:`migrate` brings an older database up to :data:`CURRENT_VERSION`,
running each step in order inside a transaction.

Steps are written to be idempotent (guarded by table/column checks), so a brand
new database — created by ``create_all()`` with the latest models — is simply
stamped to ``CURRENT_VERSION`` without altering anything. Run :func:`migrate`
*before* ``create_all()`` so an existing DB is upgraded in place.
"""
from sqlalchemy import text

from app.db.base import engine

# Bump this whenever the schema changes and add a matching MIGRATIONS entry.
CURRENT_VERSION = 1


def _table_exists(conn, table: str) -> bool:
    return conn.execute(
        text("SELECT 1 FROM sqlite_master WHERE type='table' AND name=:n"),
        {"n": table},
    ).first() is not None


def _columns(conn, table: str) -> set[str]:
    return {row[1] for row in conn.execute(text(f"PRAGMA table_info({table})")).all()}


def _drop_column(conn, table: str, column: str) -> None:
    if _table_exists(conn, table) and column in _columns(conn, table):
        conn.execute(text(f"ALTER TABLE {table} DROP COLUMN {column}"))


def _migrate_to_1(conn) -> None:
    """所见即所得: drop soft-delete + hide/archive flags, hard-delete only.

    - purge any soft-deleted records before the column disappears
    - drop records.deleted_at, members.is_active, counterparties.is_active,
      events.is_closed
    """
    if _table_exists(conn, "records") and "deleted_at" in _columns(conn, "records"):
        conn.execute(text("DELETE FROM records WHERE deleted_at IS NOT NULL"))
    _drop_column(conn, "records", "deleted_at")
    _drop_column(conn, "members", "is_active")
    _drop_column(conn, "counterparties", "is_active")
    _drop_column(conn, "events", "is_closed")


# version -> step that upgrades the DB from (version-1) to version
MIGRATIONS = {
    1: _migrate_to_1,
}


def migrate() -> None:
    """Upgrade the database to CURRENT_VERSION, a no-op if already current."""
    with engine.begin() as conn:
        current = conn.execute(text("PRAGMA user_version")).scalar() or 0
        if current >= CURRENT_VERSION:
            return
        for version in range(current + 1, CURRENT_VERSION + 1):
            step = MIGRATIONS.get(version)
            if step is not None:
                step(conn)
            # PRAGMA can't be parametrized; the value is our own int constant.
            conn.execute(text(f"PRAGMA user_version = {version}"))
