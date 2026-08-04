import sys

import pytest
from PySide6.QtWidgets import QApplication

from gui.dashboard import DashboardWidget


@pytest.fixture(scope="session")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_dashboard_creation(app):
    dashboard = DashboardWidget()
    assert dashboard is not None
    assert dashboard.storage_plot is not None
    assert dashboard.layout() is not None
