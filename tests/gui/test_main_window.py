import sys

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ai_health_copilot.gui.main_window import MainWindow


@pytest.fixture(scope="session")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_main_window_creation(app, qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.windowTitle() == "AI Windows Health Copilot"
    assert window.stacked_widget.count() == 5


def test_main_window_navigation(app, qtbot):
    window = MainWindow()
    qtbot.addWidget(window)

    # Click Scanner button
    qtbot.mouseClick(window.btn_scanner, Qt.MouseButton.LeftButton)
    assert window.stacked_widget.currentIndex() == 1

    # Click AI Chat button
    qtbot.mouseClick(window.btn_ai_chat, Qt.MouseButton.LeftButton)
    assert window.stacked_widget.currentIndex() == 2
