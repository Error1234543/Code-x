import sqlite3
from datetime import datetime
from typing import Optional, List, Dict
import os

DB_PATH = os.getenv("DB_PATH", "bot_data.db")

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                joined_at   TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS accesses (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER NOT NULL,
                channel_id   TEXT NOT NULL,
                channel_name TEXT,
                invite_link  TEXT,
                created_at   TEXT DEFAULT (datetime('now')),
                expires_at   TEXT NOT NULL,
                removed      INTEGER DEFAULT 0
            );
        """)
        self.conn.commit()

    # ── Users ──────────────────────────────────────────────────────────────────
    def ensure_user(self, user_id: int, username: str):
        self.conn.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        self.conn.commit()

    # ── Access records ─────────────────────────────────────────────────────────
    def create_access(self, user_id: int, channel_id: str, channel_name: str,
                      invite_link: str, expires_at: datetime):
        self.conn.execute(
            """INSERT INTO accesses (user_id, channel_id, channel_name, invite_link, expires_at)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, channel_id, channel_name, invite_link, expires_at.isoformat())
        )
        self.conn.commit()

    def get_active_access(self, user_id: int, channel_id: str) -> Optional[Dict]:
        now = datetime.now().isoformat()
        row = self.conn.execute(
            """SELECT *, expires_at FROM accesses
               WHERE user_id=? AND channel_id=? AND removed=0 AND expires_at > ?
               ORDER BY created_at DESC LIMIT 1""",
            (user_id, channel_id, now)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["expires_at"] = datetime.fromisoformat(d["expires_at"])
        return d

    def get_expired_accesses(self) -> List[Dict]:
        now = datetime.now().isoformat()
        rows = self.conn.execute(
            "SELECT * FROM accesses WHERE removed=0 AND expires_at <= ?",
            (now,)
        ).fetchall()
        return [dict(r) for r in rows]

    def mark_access_removed(self, access_id: int):
        self.conn.execute(
            "UPDATE accesses SET removed=1 WHERE id=?",
            (access_id,)
        )
        self.conn.commit()

    # ── Stats (admin use) ──────────────────────────────────────────────────────
    def total_users(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    def active_accesses(self) -> int:
        now = datetime.now().isoformat()
        return self.conn.execute(
            "SELECT COUNT(*) FROM accesses WHERE removed=0 AND expires_at > ?", (now,)
        ).fetchone()[0]
