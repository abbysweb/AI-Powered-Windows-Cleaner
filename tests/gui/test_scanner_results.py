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
    assert results.progress_bar is not None

    # Delete button is disabled until a scan completes
    assert not results.btn_delete.isEnabled()
