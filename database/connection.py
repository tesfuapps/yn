# database/connection.py — Database connection management.
# SQLite (aiosqlite) is the default; optional PostgreSQL via asyncpg when
# DATABASE_URL or DB_HOST is set in the environment / .env.

import contextlib
from contextlib import asynccontextmanager
import logging
from typing import Union, Optional
import aiosqlite

logger = logging.getLogger(__name__)

DB_PATH = "yene_lottery.db"


def _get_cfg():
    import config
    return config.cfg


def _pg_dsn(cfg) -> str:
    dsn = (getattr(cfg, "database_url", "") or "").strip()
    if dsn:
        return dsn
    host = (getattr(cfg, "db_host", "") or "").strip()
    if not host:
        return ""
    port = getattr(cfg, "db_port", 5432) or 5432
    name = getattr(cfg, "db_name", "yene_lottery") or "yene_lottery"
    user = getattr(cfg, "db_user", "postgres") or "postgres"
    password = getattr(cfg, "db_password", "") or ""
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


def _pg_enabled(cfg) -> bool:
    dsn = _pg_dsn(cfg)
    return dsn.startswith(("postgresql://", "postgres://"))


async def _get_pg_pool():
    import asyncpg

    cfg = _get_cfg()
    dsn = _pg_dsn(cfg)
    logger.warning(
        "PostgreSQL mode: aiosqlite-style '?' placeholders in queries.py/models.py "
        "are NOT compatible with asyncpg; use asyncpg-style '$1, $2...' placeholders "
        "for Postgres-only queries."
    )
    return await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=10)


@asynccontextmanager
async def get_conn() -> Union[aiosqlite.Connection, "asyncpg.Pool"]:
    """Return a DB connection or pool.

    SQLite (default): returns an aiosqlite Connection (async context manager).
    PostgreSQL (DATABASE_URL or DB_HOST set): returns an asyncpg Pool; use
    `async with pool.acquire() as conn:` for per-request connections.
    """
    cfg = _get_cfg()
    if _pg_enabled(cfg):
        yield await _get_pg_pool()
        return
    yield await aiosqlite.connect(DB_PATH)


async def close_pool() -> None:
    """Close the PostgreSQL pool if open; no-op for SQLite (connections are per-request)."""
    cfg = _get_cfg()
    if _pg_enabled(cfg):
        # Pool lifetime is tied to the process; asyncpg pools are garbage-collected
        # on exit. Explicit close is handled by the caller holding the pool reference.
        logger.debug("PostgreSQL pool close requested (managed by caller).")
        return
    logger.debug("SQLite finished (no persistent pool).")
