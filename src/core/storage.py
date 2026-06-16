"""
Storage abstraction supporting SQLite and PostgreSQL backends.

Priority:
1) DATABASE_URL -> PostgreSQL
2) SQLITE_PATH  -> SQLite (defaults to data/data.db when DATABASE_URL is empty)
3) No file fallback
"""

import asyncio
import json
import logging
import os
import sqlite3
import threading
import time
from typing import Any, Optional
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_db_pools: dict[int, Any] = {}
_db_pool_locks: dict[int, asyncio.Lock] = {}
_db_pool_registry_lock = threading.Lock()
_db_loop = None
_db_thread = None
_db_loop_lock = threading.Lock()

_sqlite_conn = None
_sqlite_lock = threading.Lock()


def _get_database_url() -> str:
    return os.environ.get("DATABASE_URL", "").strip()


def _default_sqlite_path() -> str:
    return os.path.join("data", "data.db")


def _get_sqlite_path() -> str:
    env_path = os.environ.get("SQLITE_PATH", "").strip()
    if env_path:
        return env_path
    return _default_sqlite_path()


def _get_backend() -> str:
    if _get_database_url():
        return "postgres"
    if _get_sqlite_path():
        return "sqlite"
    return ""


def is_database_enabled() -> bool:
    return bool(_get_backend())


def _ensure_db_loop() -> asyncio.AbstractEventLoop:
    global _db_loop, _db_thread
    if _db_loop and _db_thread and _db_thread.is_alive():
        return _db_loop
    with _db_loop_lock:
        if _db_loop and _db_thread and _db_thread.is_alive():
            return _db_loop
        loop = asyncio.new_event_loop()

        def _runner() -> None:
            asyncio.set_event_loop(loop)
            loop.run_forever()

        thread = threading.Thread(target=_runner, name="storage-db-loop", daemon=True)
        thread.start()
        _db_loop = loop
        _db_thread = thread
        return _db_loop


def _run_in_db_loop(coro):
    loop = _ensure_db_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()


def _get_sqlite_conn():
    global _sqlite_conn
    if _sqlite_conn is not None:
        return _sqlite_conn
    with _sqlite_lock:
        if _sqlite_conn is not None:
            return _sqlite_conn
        sqlite_path = _get_sqlite_path()
        if not sqlite_path:
            raise ValueError("SQLITE_PATH is not set")
        os.makedirs(os.path.dirname(sqlite_path) or ".", exist_ok=True)
        conn = sqlite3.connect(sqlite_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        _init_sqlite_tables(conn)
        _sqlite_conn = conn
        logger.info(f"[STORAGE] SQLite initialized at {sqlite_path}")
        return _sqlite_conn


async def _get_pool():
    current_loop = asyncio.get_running_loop()
    loop_key = id(current_loop)

    with _db_pool_registry_lock:
        pool = _db_pools.get(loop_key)
        if pool is not None:
            return pool
        lock = _db_pool_locks.get(loop_key)
        if lock is None:
            lock = asyncio.Lock()
            _db_pool_locks[loop_key] = lock

    async with lock:
        with _db_pool_registry_lock:
            pool = _db_pools.get(loop_key)
            if pool is not None:
                return pool

        db_url = _get_database_url()
        if not db_url:
            raise ValueError("DATABASE_URL is not set")
        try:
            import asyncpg
            pool = await asyncpg.create_pool(
                db_url,
                min_size=0,
                max_size=10,
                command_timeout=30,
            )
            await _init_tables(pool)
            with _db_pool_registry_lock:
                _db_pools[loop_key] = pool
            logger.info(f"[STORAGE] PostgreSQL pool initialized (loop={loop_key})")
        except ImportError:
            logger.error("[STORAGE] asyncpg is required for database storage")
            raise
        except Exception as e:
            logger.error(f"[STORAGE] Database connection failed: {e}")
            raise
    return pool


async def _reset_pool():
    loop_key = id(asyncio.get_running_loop())
    with _db_pool_registry_lock:
        pool = _db_pools.pop(loop_key, None)
        _db_pool_locks.pop(loop_key, None)

    if pool is not None:
        try:
            await pool.close()
        except Exception:
            pass

    return await _get_pool()


@asynccontextmanager
async def _pg_acquire():
    import asyncpg
    pool = await _get_pool()
    try:
        async with pool.acquire() as conn:
            yield conn
    except (asyncpg.ConnectionDoesNotExistError,
            asyncpg.InterfaceError,
            OSError) as e:
        logger.warning(f"[STORAGE] Connection lost, resetting pool: {e}")
        await _reset_pool()
        raise


async def _init_tables(pool) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                account_id TEXT PRIMARY KEY,
                position INTEGER NOT NULL,
                data JSONB NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await conn.execute(
            """
            CREATE INDEX IF NOT EXISTS accounts_position_idx
            ON accounts(position)
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS kv_settings (
                key TEXT PRIMARY KEY,
                value JSONB NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS kv_stats (
                key TEXT PRIMARY KEY,
                value JSONB NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS request_logs (
                id SERIAL PRIMARY KEY,
                timestamp BIGINT NOT NULL,
                model TEXT NOT NULL,
                ttfb_ms INTEGER,
                total_ms INTEGER,
                status TEXT NOT NULL,
                status_code INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await conn.execute("CREATE INDEX IF NOT EXISTS request_logs_timestamp_idx ON request_logs(timestamp)")
        await conn.execute("CREATE INDEX IF NOT EXISTS request_logs_model_idx ON request_logs(model)")
        await conn.execute("CREATE INDEX IF NOT EXISTS request_logs_status_idx ON request_logs(status)")
        logger.info("[STORAGE] Database tables initialized")


def _init_sqlite_tables(conn: sqlite3.Connection) -> None:
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                account_id TEXT PRIMARY KEY,
                position INTEGER NOT NULL,
                data TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS accounts_position_idx
            ON accounts(position)
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS kv_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS kv_stats (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                model TEXT NOT NULL,
                ttfb_ms INTEGER,
                total_ms INTEGER,
                status TEXT NOT NULL,
                status_code INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS request_logs_timestamp_idx ON request_logs(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS request_logs_model_idx ON request_logs(model)")
        conn.execute("CREATE INDEX IF NOT EXISTS request_logs_status_idx ON request_logs(status)")


# ==================== Accounts storage ====================

def _normalize_accounts(accounts: list) -> list:
    normalized = []
    for index, acc in enumerate(accounts, 1):
        if not isinstance(acc, dict):
            continue
        account_id = acc.get("id") or acc.get("user_id") or f"account_{index}"
        next_acc = dict(acc)
        next_acc.setdefault("id", account_id)
        normalized.append(next_acc)
    return normalized


def _parse_account_value(value) -> Optional[dict]:
    if value is None:
        return None
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception:
            return None
    if isinstance(value, dict):
        return value
    return None


async def _load_accounts_from_table() -> Optional[list]:
    backend = _get_backend()
    if backend == "postgres":
        async with _pg_acquire() as conn:
            rows = await conn.fetch("SELECT data FROM accounts ORDER BY position ASC")
        if not rows:
            return []
        accounts = []
        for row in rows:
            value = _parse_account_value(row["data"])
            if value is not None:
                accounts.append(value)
        return accounts
    if backend == "sqlite":
        conn = _get_sqlite_conn()
        with _sqlite_lock:
            rows = conn.execute("SELECT data FROM accounts ORDER BY position ASC").fetchall()
        if not rows:
            return []
        accounts = []
        for row in rows:
            value = _parse_account_value(row["data"])
            if value is not None:
                accounts.append(value)
        return accounts
    return None


async def _save_accounts_to_table(accounts: list) -> bool:
    backend = _get_backend()
    if backend == "postgres":
        normalized = _normalize_accounts(accounts)
        async with _pg_acquire() as conn:
            async with conn.transaction():
                await conn.execute("DELETE FROM accounts")
                for index, acc in enumerate(normalized, 1):
                    await conn.execute(
                        """
                        INSERT INTO accounts (account_id, position, data, updated_at)
                        VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
                        """,
                        acc["id"],
                        index,
                        json.dumps(acc, ensure_ascii=False),
                    )
        logger.info(f"[STORAGE] Saved {len(normalized)} accounts to database")
        return True
    if backend == "sqlite":
        conn = _get_sqlite_conn()
        normalized = _normalize_accounts(accounts)
        with _sqlite_lock, conn:
            conn.execute("DELETE FROM accounts")
            for index, acc in enumerate(normalized, 1):
                conn.execute(
                    """
                    INSERT INTO accounts (account_id, position, data, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (acc["id"], index, json.dumps(acc, ensure_ascii=False)),
                )
        logger.info(f"[STORAGE] Saved {len(normalized)} accounts to database")
        return True
    return False


async def load_accounts() -> Optional[list]:
    if not is_database_enabled():
        return None
    try:
        data = await _load_accounts_from_table()
        if data is None:
            return None
        if data:
            logger.info(f"[STORAGE] Loaded {len(data)} accounts from database")
        else:
            logger.info("[STORAGE] No accounts found in database")
        return data
    except Exception as e:
        logger.error(f"[STORAGE] Database read failed: {e}")
    return None


async def save_accounts(accounts: list) -> bool:
    if not is_database_enabled():
        return False
    try:
        return await _save_accounts_to_table(accounts)
    except Exception as e:
        logger.error(f"[STORAGE] Database write failed: {e}")
    return False


def load_accounts_sync() -> Optional[list]:
    return _run_in_db_loop(load_accounts())


def save_accounts_sync(accounts: list) -> bool:
    return _run_in_db_loop(save_accounts(accounts))


# ==================== Settings storage ====================

async def _load_kv(table_name: str, key: str) -> Optional[dict]:
    backend = _get_backend()
    if backend == "postgres":
        async with _pg_acquire() as conn:
            row = await conn.fetchrow(f"SELECT value FROM {table_name} WHERE key = $1", key)
        if not row:
            return None
        value = row["value"]
        if isinstance(value, str):
            return json.loads(value)
        return value
    if backend == "sqlite":
        conn = _get_sqlite_conn()
        with _sqlite_lock:
            row = conn.execute(f"SELECT value FROM {table_name} WHERE key = ?", (key,)).fetchone()
        if not row:
            return None
        value = row["value"]
        if isinstance(value, str):
            return json.loads(value)
        return value
    return None


async def _save_kv(table_name: str, key: str, value: dict) -> bool:
    backend = _get_backend()
    payload = json.dumps(value, ensure_ascii=False)
    if backend == "postgres":
        async with _pg_acquire() as conn:
            await conn.execute(
                f"""
                INSERT INTO {table_name} (key, value, updated_at)
                VALUES ($1, $2, CURRENT_TIMESTAMP)
                ON CONFLICT (key) DO UPDATE SET
                    value = EXCLUDED.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                key, payload,
            )
        return True
    if backend == "sqlite":
        conn = _get_sqlite_conn()
        with _sqlite_lock, conn:
            conn.execute(
                f"""
                INSERT INTO {table_name} (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key, payload),
            )
        return True
    return False


async def load_settings() -> Optional[dict]:
    if not is_database_enabled():
        return None
    try:
        return await _load_kv("kv_settings", "settings")
    except Exception as e:
        logger.error(f"[STORAGE] Settings read failed: {e}")
    return None


async def save_settings(settings: dict) -> bool:
    if not is_database_enabled():
        return False
    try:
        saved = await _save_kv("kv_settings", "settings", settings)
        if saved:
            logger.info("[STORAGE] Settings saved to database")
        return saved
    except Exception as e:
        logger.error(f"[STORAGE] Settings write failed: {e}")
    return False


async def load_stats() -> Optional[dict]:
    if not is_database_enabled():
        return None
    try:
        return await _load_kv("kv_stats", "stats")
    except Exception as e:
        logger.error(f"[STORAGE] Stats read failed: {e}")
    return None


async def save_stats(stats: dict) -> bool:
    if not is_database_enabled():
        return False
    try:
        return await _save_kv("kv_stats", "stats", stats)
    except Exception as e:
        logger.error(f"[STORAGE] Stats write failed: {e}")
    return False


def load_settings_sync() -> Optional[dict]:
    return _run_in_db_loop(load_settings())


def save_settings_sync(settings: dict) -> bool:
    return _run_in_db_loop(save_settings(settings))


def load_stats_sync() -> Optional[dict]:
    return _run_in_db_loop(load_stats())


def save_stats_sync(stats: dict) -> bool:
    return _run_in_db_loop(save_stats(stats))
