import sqlite3
from pathlib import Path
from typing import Any
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "database/storage.db", schema_path: str = "database/schema.sql"):
        self.db_path = Path(db_path)
        self.schema_path = Path(schema_path)
        self._init_db()

    def _init_db(self):
        """Initializes the database schema if it doesn't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.schema_path.exists():
            logger.error(f"Schema file not found at {self.schema_path}")
            return
            
        with sqlite3.connect(self.db_path) as conn:
            with open(self.schema_path, "r") as f:
                conn.executescript(f.read())

    def get_preference(self, key: str, default: str = "") -> str:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM Preferences WHERE key = ?", (key,))
            row = cur.fetchone()
            return row[0] if row else default

    def set_preference(self, key: str, value: str):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO Preferences (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, str(value))
            )
            conn.commit()

    def add_ignored_folder(self, path: str):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("INSERT OR IGNORE INTO IgnoredFolders (path) VALUES (?)", (path,))
            conn.commit()

    def remove_ignored_folder(self, path: str):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM IgnoredFolders WHERE path = ?", (path,))
            conn.commit()

    def get_ignored_folders(self) -> list[str]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT path FROM IgnoredFolders")
            return [row[0] for row in cur.fetchall()]

    def log_history(self, action_type: str, target: str, size_bytes: int):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO History (action_type, target, size_bytes) VALUES (?, ?, ?)",
                (action_type, target, size_bytes)
            )
            conn.commit()

    def get_history(self) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM History ORDER BY timestamp DESC")
            return [dict(row) for row in cur.fetchall()]
