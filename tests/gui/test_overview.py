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


def test_overview_creation(app, qtbot):
    overview = OverviewWidget()
    qtbot.addWidget(overview)

    # Assert layout and basic properties
    assert overview.layout() is not None
    assert overview.storage_plot is not None

    # Test card creation method
    card = overview.create_card("Test Card")
    assert card is not None
    assert card.layout() is not None
