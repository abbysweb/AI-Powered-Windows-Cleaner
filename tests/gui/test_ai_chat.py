import sys

import pytest
from PySide6.QtWidgets import QApplication

from ai_health_copilot.gui.views.ai_chat import AIChatWidget


@pytest.fixture(scope="session")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_ai_chat_creation(app, qtbot):
    chat = AIChatWidget()
    qtbot.addWidget(chat)

    # Assert layout and basic properties
    assert chat.layout() is not None
