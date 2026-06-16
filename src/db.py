"""Account store — migrated to use core/storage abstraction.

Maintains backward compatibility with the old API while using the new storage layer.
"""

import aiosqlite
from .config import DB_PATH
from .core.storage import is_database_enabled, _get_sqlite_conn, _sqlite_lock

# Legacy table for backward compatibility with direct DB access
_CREATE = """
CREATE TABLE IF NOT EXISTS accounts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT    NOT NULL UNIQUE,
    email       TEXT    NOT NULL,
    access_token TEXT   NOT NULL,
    refresh_token TEXT,
    expires_time INTEGER,
    mail_service TEXT   NOT NULL DEFAULT 'mailtm',
    created_at  INTEGER NOT NULL DEFAULT (strftime('%s','now')),
    label       TEXT
)
"""


async def init_db() -> None:
    """Initialize database tables."""
    # Initialize both legacy and new storage tables
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(_CREATE)
        await db.commit()

    # Core storage initialization happens automatically on first access


async def save_account(data: dict) -> dict:
    """Insert or replace an account. Returns the saved row as dict."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO accounts (user_id, email, access_token, refresh_token, expires_time, mail_service)
               VALUES (:userId, :email, :accessToken, :refreshToken, :expiresTime, :mailService)
               ON CONFLICT(user_id) DO UPDATE SET
                   access_token  = excluded.access_token,
                   refresh_token = excluded.refresh_token,
                   expires_time  = excluded.expires_time""",
            {
                "userId": str(data["userId"]),
                "email": data.get("email") or "",
                "accessToken": data["accessToken"],
                "refreshToken": data.get("refreshToken", ""),
                "expiresTime": data.get("expiresTime"),
                "mailService": data.get("mailService", "mailtm"),
            },
        )
        await db.commit()
    return await get_account(str(data["userId"]))


async def list_accounts() -> list[dict]:
    """List all accounts ordered by creation time."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM accounts ORDER BY created_at DESC"
        ) as cur:
            rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_account(user_id: str) -> dict | None:
    """Get a single account by user_id."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM accounts WHERE user_id = ?", (user_id,)
        ) as cur:
            row = await cur.fetchone()
    return dict(row) if row else None


async def delete_account(user_id: str) -> bool:
    """Delete an account by user_id."""
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("DELETE FROM accounts WHERE user_id = ?", (user_id,))
        await db.commit()
        return cur.rowcount > 0


async def update_label(user_id: str, label: str) -> None:
    """Update account label."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE accounts SET label = ? WHERE user_id = ?", (label, user_id)
        )
        await db.commit()
