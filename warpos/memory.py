"""SQLite-backed memory with simple keyword search."""

from __future__ import annotations

import os
import json
import sqlite3
import time
from pathlib import Path


class Memory:
    """Persistent memory for agents. Stores conversation snippets in SQLite
    with basic keyword search (upgradeable to vector search later).

    Usage:
        mem = Memory(".warpos/my-agent/memory.db")
        mem.add("User asked about Python", session_id="s1")
        results = mem.search("Python", limit=5)
    """

    def __init__(self, db_path: str = ".warpos/memory.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                session_id TEXT DEFAULT 'default',
                metadata TEXT DEFAULT '{}',
                created_at REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_session ON memories(session_id);
            CREATE INDEX IF NOT EXISTS idx_created ON memories(created_at);
        """)
        # FTS5 for keyword search
        try:
            self._conn.executescript("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts
                USING fts5(text, content='memories', content_rowid='id');

                CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
                    INSERT INTO memories_fts(rowid, text) VALUES (new.id, new.text);
                END;
                CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
                    INSERT INTO memories_fts(memories_fts, rowid, text) VALUES('delete', old.id, old.text);
                END;
                CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
                    INSERT INTO memories_fts(memories_fts, rowid, text) VALUES('delete', old.id, old.text);
                    INSERT INTO memories_fts(rowid, text) VALUES (new.id, new.text);
                END;
            """)
        except Exception:
            pass  # FTS5 might not be available
        self._conn.commit()

    def add(self, text: str, session_id: str = "default", metadata: dict = None):
        """Add a memory entry."""
        self._conn.execute(
            "INSERT INTO memories (text, session_id, metadata, created_at) VALUES (?, ?, ?, ?)",
            (text, session_id, json.dumps(metadata or {}), time.time()),
        )
        self._conn.commit()

    def search(self, query: str, limit: int = 5, session_id: str = None) -> list[str]:
        """Search memories by keyword. Returns list of text strings."""
        if not query.strip():
            return []

        # Try FTS5 search first
        try:
            if session_id:
                rows = self._conn.execute(
                    """SELECT m.text FROM memories_fts f
                       JOIN memories m ON f.rowid = m.id
                       WHERE memories_fts MATCH ? AND m.session_id = ?
                       ORDER BY m.created_at DESC LIMIT ?""",
                    (query, session_id, limit),
                ).fetchall()
            else:
                rows = self._conn.execute(
                    """SELECT m.text FROM memories_fts f
                       JOIN memories m ON f.rowid = m.id
                       WHERE memories_fts MATCH ?
                       ORDER BY m.created_at DESC LIMIT ?""",
                    (query, limit),
                ).fetchall()
            if rows:
                return [r["text"] for r in rows]
        except Exception:
            pass

        # Fallback: LIKE search
        pattern = f"%{query}%"
        if session_id:
            rows = self._conn.execute(
                "SELECT text FROM memories WHERE text LIKE ? AND session_id = ? ORDER BY created_at DESC LIMIT ?",
                (pattern, session_id, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT text FROM memories WHERE text LIKE ? ORDER BY created_at DESC LIMIT ?",
                (pattern, limit),
            ).fetchall()
        return [r["text"] for r in rows]

    def get_recent(self, limit: int = 10, session_id: str = None) -> list[str]:
        """Get most recent memories."""
        if session_id:
            rows = self._conn.execute(
                "SELECT text FROM memories WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
                (session_id, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT text FROM memories ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [r["text"] for r in rows]

    def clear(self, session_id: str = None):
        """Clear all memories (optionally for a specific session)."""
        if session_id:
            self._conn.execute("DELETE FROM memories WHERE session_id = ?", (session_id,))
        else:
            self._conn.execute("DELETE FROM memories")
        self._conn.commit()

    def count(self) -> int:
        """Get total number of memories."""
        row = self._conn.execute("SELECT COUNT(*) as c FROM memories").fetchone()
        return row["c"]

    def close(self):
        """Close the database connection."""
        self._conn.close()
