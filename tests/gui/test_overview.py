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

    # Key widgets present
    assert overview.disk_plot is not None
    assert overview.tile_cpu is not None
    assert overview.tile_ram is not None
    assert overview.tile_health is not None

    # Action buttons present
    assert overview.btn_scan is not None
    assert overview.btn_clean is not None

    # Metric tiles display non-empty values
    assert overview.tile_cpu.lbl_value.text() != ""
    assert overview.tile_ram.lbl_value.text() != ""
