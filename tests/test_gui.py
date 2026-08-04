import sys

import pytest
from PySide6.QtWidgets import QApplication

from ai_health_copilot.gui.views.overview import OverviewWidget


@pytest.fixture(scope="session")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_overview_creation(app):
    overview = OverviewWidget()
    assert overview is not None
    assert overview.disk_plot is not None
    assert overview.layout() is not None
