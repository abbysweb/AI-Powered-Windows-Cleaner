import sys

import pytest
from PySide6.QtWidgets import QApplication

from ai_health_copilot.gui.views.scanner_results import ScannerResultsWidget


@pytest.fixture(scope="session")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_scanner_results_creation(app, qtbot):
    results = ScannerResultsWidget()
    qtbot.addWidget(results)

    # Widget and layout exist
    assert results.layout() is not None
    assert results.tree is not None

    # Tree starts empty — data is populated after the user clicks Start Scan
    assert results.tree.topLevelItemCount() == 0

    # Core controls are present
    assert results.btn_scan is not None
    assert results.btn_delete is not None
    assert results.btn_recycle is not None
    assert results.progress_bar is not None

    # Delete button is disabled until a scan completes
    assert not results.btn_delete.isEnabled()


def test_delete_worker_removes_files_dirs_and_empty_folders(
    app, qtbot, tmp_path, monkeypatch
):
    from ai_health_copilot.gui.views import scanner_results as sr

    monkeypatch.setattr(sr, "DB_PATH", str(tmp_path / "test.db"))

    plain_file = tmp_path / "file.txt"
    plain_file.write_text("x")

    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    (cache_dir / "x.dat").write_text("y")

    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    worker = sr.DeleteWorker([str(plain_file), str(cache_dir), str(empty_dir)])
    summary = []
    worker.finished.connect(
        lambda deleted, failed, skipped: summary.append((deleted, failed, skipped))
    )
    worker.run()

    assert not plain_file.exists()
    assert not cache_dir.exists()
    assert not empty_dir.exists()
    assert summary == [(3, 0, 0)]


def test_delete_worker_skips_protected_files(app, qtbot, tmp_path, monkeypatch):
    from ai_health_copilot.gui.views import scanner_results as sr

    monkeypatch.setattr(sr, "DB_PATH", str(tmp_path / "test.db"))

    sensitive = tmp_path / "passwords.txt"
    sensitive.write_text("secret")
    normal = tmp_path / "file.dat"
    normal.write_text("x")

    worker = sr.DeleteWorker([str(sensitive), str(normal)])
    summary = []
    worker.finished.connect(
        lambda deleted, failed, skipped: summary.append((deleted, failed, skipped))
    )
    worker.run()

    assert sensitive.exists()
    assert not normal.exists()
    assert summary == [(1, 0, 1)]


def test_delete_worker_logs_history(app, qtbot, tmp_path, monkeypatch):
    from ai_health_copilot.gui.views import scanner_results as sr

    monkeypatch.setattr(sr, "DB_PATH", str(tmp_path / "test.db"))

    target = tmp_path / "file.txt"
    target.write_text("data")

    worker = sr.DeleteWorker([str(target)])
    worker.finished.connect(lambda *_: None)
    worker.run()

    assert not target.exists()

    db = sr.DatabaseManager(db_path=str(tmp_path / "test.db"))
    history = db.get_history()
    assert len(history) == 1
    assert history[0]["action_type"] == "DELETE"
    assert not history[0]["backup_path"]


def test_delete_worker_missing_path_is_skipped(app, qtbot, tmp_path, monkeypatch):
    from ai_health_copilot.gui.views import scanner_results as sr

    monkeypatch.setattr(sr, "DB_PATH", str(tmp_path / "test.db"))

    worker = sr.DeleteWorker([str(tmp_path / "ghost.bin")])
    summary = []
    worker.finished.connect(
        lambda deleted, failed, skipped: summary.append((deleted, failed, skipped))
    )
    worker.run()

    assert summary == [(0, 0, 1)]
