import shutil

import pytest

from ai_health_copilot.core.rollback.manager import QuarantineManager


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


def test_backup_path_moves_directory(qm, tmp_path):
    src = tmp_path / "app"
    src.mkdir()
    (src / "cache.dat").write_text("x" * 10)

    backup = qm.backup_path(src)
    assert backup is not None
    assert backup.exists()
    assert not src.exists()
    assert (backup / "cache.dat").read_text() == "x" * 10

    assert qm.restore_path(backup, src)
    assert src.exists()
    assert (src / "cache.dat").read_text() == "x" * 10
    assert not backup.exists()


def test_backup_path_copies_file(qm, tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("hello")

    backup = qm.backup_path(f)
    assert backup is not None
    assert backup.exists()
    assert f.exists()
    assert backup.read_text() == "hello"

    f.unlink()
    assert qm.restore_path(backup, f)
    assert f.read_text() == "hello"


def test_total_size_and_clear(qm, tmp_path):
    f = tmp_path / "b.bin"
    f.write_bytes(b"x" * 100)
    qm.backup_path(f)
    assert qm.total_size() == 100

    freed = qm.clear()
    assert freed == 100
    assert not qm.list_backups()
    assert qm.total_size() == 0
