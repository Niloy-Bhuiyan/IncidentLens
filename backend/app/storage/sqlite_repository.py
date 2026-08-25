from __future__ import annotations

import sqlite3
from pathlib import Path


class SQLiteRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def migrate(self) -> int:
        migration_root = Path(__file__).resolve().parent / "migrations"
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations "
            "(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)"
        )
        applied = {row[0] for row in self.connection.execute("SELECT version FROM schema_migrations")}
        count = 0
        for path in sorted(migration_root.glob("*.sql")):
            version = int(path.name.split("_", 1)[0])
            if version in applied:
                continue
            self.connection.executescript(path.read_text(encoding="utf-8"))
            self.connection.execute(
                "INSERT INTO schema_migrations(version, applied_at) VALUES (?, datetime('now'))", (version,)
            )
            self.connection.commit()
            count += 1
        return count

    def table_names(self) -> set[str]:
        rows = self.connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return {str(row[0]) for row in rows}

    def close(self) -> None:
        self.connection.close()
