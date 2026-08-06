from pathlib import Path

from ai_health_copilot.core.cleaner.delete import (
    DELETED,
    FAILED,
    SKIPPED,
    permanent_delete,
    safe_delete,
)
from ai_health_copilot.core.rollback.manager import QuarantineManager


def test_permanent_delete_file(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("x")
    assert permanent_delete(f) == DELETED
    assert not f.exists()


def test_permanent_delete_directory(tmp_path):
    d = tmp_path / "cache"
    d.mkdir()
    (d / "x.dat").write_text("y")
    assert permanent_delete(d) == DELETED
    assert not d.exists()


def test_permanent_delete_skips_sensitive(tmp_path):
    f = tmp_path / "passwords.txt"
    f.write_text("secret")
    assert permanent_delete(f) == SKIPPED
    assert f.exists()


def test_permanent_delete_missing_is_skipped(tmp_path):
    assert permanent_delete(tmp_path / "ghost.bin") == SKIPPED


def test_permanent_delete_failure_is_reported(tmp_path, monkeypatch):
    import shutil

    d = tmp_path / "cache"
    d.mkdir()
    (d / "x.dat").write_text("y")
    monkeypatch.setattr(
        shutil, "rmtree", lambda *a, **k: (_ for _ in ()).throw(OSError)
    )
    assert permanent_delete(d) == FAILED
    assert d.exists()


def test_safe_delete_with_quarantine(tmp_path):
    f = tmp_path / "b.txt"
    f.write_text("data")
    qm = QuarantineManager(str(tmp_path / "quarantine"))

    outcome, backup = safe_delete(f, qm)
    assert outcome == DELETED
    assert backup
    assert not f.exists()
    assert Path(backup).read_text() == "data"
