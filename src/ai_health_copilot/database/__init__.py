"""Database module.

Defines the canonical on-disk locations for the application database and
quarantine, resolved relative to the project root so results do not depend on
the current working directory.
"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "database" / "storage.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"
QUARANTINE_DIR = DB_PATH.parent / "quarantine"
