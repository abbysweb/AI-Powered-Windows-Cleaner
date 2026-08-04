import sys

import pytest
import requests
from PySide6.QtWidgets import QApplication

from ai_health_copilot.gui.views.ai_chat import (
    REQUEST_TIMEOUT,
    AIChatWidget,
    ChatThread,
)


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


class _FakeResponse:
    def __init__(self, data=None):
        self._data = data or {"recommendation": "All good"}

    def raise_for_status(self):
        return None

    def json(self):
        return self._data


def _patch_requests(monkeypatch, resp=None, exc=None, capture=None):
    def fake_post(url, **kwargs):
        if capture is not None:
            capture["timeout"] = kwargs.get("timeout")
            capture["url"] = url
        if exc is not None:
            raise exc
        return resp

    monkeypatch.setattr(
        "ai_health_copilot.gui.views.ai_chat.requests.post", fake_post
    )
    monkeypatch.setattr(
        "ai_health_copilot.gui.views.ai_chat.collect_system_context",
        lambda: "",
    )


def test_chat_thread_success(app, qtbot, monkeypatch):
    _patch_requests(monkeypatch, resp=_FakeResponse())
    thread = ChatThread("hi")
    responses, errors = [], []
    thread.response_received.connect(responses.append)
    thread.error_received.connect(errors.append)
    thread.run()
    assert responses == ["All good"]
    assert errors == []


def test_chat_thread_uses_long_timeout(app, qtbot, monkeypatch):
    captured = {}
    _patch_requests(monkeypatch, resp=_FakeResponse(), capture=captured)
    thread = ChatThread("hi")
    thread.run()
    assert captured["timeout"] == REQUEST_TIMEOUT
    assert captured["url"].endswith("/api/advisor")
    assert REQUEST_TIMEOUT >= 60


def test_chat_thread_timeout_helpful_message(app, qtbot, monkeypatch):
    _patch_requests(monkeypatch, exc=requests.exceptions.ReadTimeout("Read timed out"))
    thread = ChatThread("hi")
    responses, errors = [], []
    thread.response_received.connect(responses.append)
    thread.error_received.connect(errors.append)
    thread.run()
    assert responses == []
    assert len(errors) == 1
    assert "did not respond" in errors[0]


def test_chat_thread_connection_error_helpful_message(app, qtbot, monkeypatch):
    _patch_requests(
        monkeypatch, exc=requests.exceptions.ConnectionError("Connection refused")
    )
    thread = ChatThread("hi")
    errors = []
    thread.error_received.connect(errors.append)
    thread.run()
    assert len(errors) == 1
    assert "Could not connect" in errors[0]

