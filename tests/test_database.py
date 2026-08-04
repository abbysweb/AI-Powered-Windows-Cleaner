from pathlib import Path

import pytest

from ai_health_copilot.database.manager import DatabaseManager


@pytest.fixture
def db_manager(tmp_path):
    db_file = tmp_path / "test.db"

    # We need the real schema file for initialization
    schema_path = Path("src/ai_health_copilot/database/schema.sql")

    manager = DatabaseManager(db_path=str(db_file), schema_path=str(schema_path))
    yield manager


def test_preferences(db_manager):
    assert db_manager.get_preference("theme", "dark") == "dark"
    db_manager.set_preference("theme", "light")
    assert db_manager.get_preference("theme", "dark") == "light"

    # Update existing
    db_manager.set_preference("theme", "system")
    assert db_manager.get_preference("theme") == "system"


def test_ignored_folders(db_manager):
    assert len(db_manager.get_ignored_folders()) == 0

    db_manager.add_ignored_folder("C:\\Windows\\System32")
    db_manager.add_ignored_folder("C:\\Users\\Public")

    # Duplicate insert should be ignored
    db_manager.add_ignored_folder("C:\\Windows\\System32")

    ignored = db_manager.get_ignored_folders()
    assert len(ignored) == 2
    assert "C:\\Windows\\System32" in ignored

    db_manager.remove_ignored_folder("C:\\Windows\\System32")
    assert len(db_manager.get_ignored_folders()) == 1


def test_history(db_manager):
    assert len(db_manager.get_history()) == 0

    db_manager.log_history("CLEAN", "Windows Temp", 1024)
    db_manager.log_history("QUARANTINE", "Downloads", 2048)

    history = db_manager.get_history()
    assert len(history) == 2
    # Ordered by timestamp desc, so QUARANTINE should be first or second depending on execution speed,
    # but generally just check content.
    actions = [h["action_type"] for h in history]
    assert "CLEAN" in actions
    assert "QUARANTINE" in actions
