import shutil

import pytest

from core.rollback.manager import QuarantineManager


@pytest.fixture
def qm(tmp_path):
    q_dir = tmp_path / "quarantine"
    yield QuarantineManager(quarantine_dir=str(q_dir))
    if q_dir.exists():
        shutil.rmtree(q_dir)


def test_backup_and_restore(qm, tmp_path):
    # Setup dummy file
    dummy_file = tmp_path / "dummy.txt"
    dummy_file.write_text("Hello World")

    # Backup
    backup_path = qm.backup_file(dummy_file)
    assert backup_path is not None
    assert backup_path.exists()
    assert backup_path.read_text() == "Hello World"

    # Simulate deletion
    dummy_file.unlink()
    assert not dummy_file.exists()

    # Restore
    success = qm.restore_file(backup_path, dummy_file)
    assert success is True
    assert dummy_file.exists()
    assert dummy_file.read_text() == "Hello World"
    assert not backup_path.exists()


def test_backup_nonexistent_file(qm, tmp_path):
    nonexistent = tmp_path / "doesnotexist.txt"
    assert qm.backup_file(nonexistent) is None
