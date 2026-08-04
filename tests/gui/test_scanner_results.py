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

    # Assert layout and basic properties
    assert results.layout() is not None
    assert results.tree is not None
    assert results.tree.topLevelItemCount() >= 2
