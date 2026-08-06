import json
import sys
import types
from pathlib import Path

import pytest
import requests
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ai_health_copilot.gui.views import ai_chat as ai_chat_module
from ai_health_copilot.gui.views.ai_chat import (
    REQUEST_TIMEOUT,
    AIChatWidget,
    StreamingWorker,
    VisionAnalysisService,
    VisionWorker,
    collect_system_context,
)


@pytest.fixture(scope="session")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


# ── Helpers ──────────────────────────────────────────────────────────────────
class _FakeStreamingResponse:
    def __init__(self, data=None):
        self._data = data or [
            b"data: " + json.dumps({"type": "token", "content": "All", "done": False}).encode(),
            b"data: " + json.dumps({"type": "token", "content": " good", "done": False}).encode(),
            b"data: " + json.dumps({"type": "complete", "content": "", "done": True}).encode(),
        ]
        self.closed = False

    def raise_for_status(self):
        return None

    def iter_lines(self):
        return self._data

    def close(self):
        self.closed = True


def _patch_requests(monkeypatch, resp=None, exc=None, capture=None):
    def fake_post(url, **kwargs):
        if capture is not None:
            capture["timeout"] = kwargs.get("timeout")
            capture["url"] = url
            capture["stream"] = kwargs.get("stream")
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


def _run_worker(worker):
    tokens, completes, errors = [], [], []
    worker.token_received.connect(tokens.append)
    worker.stream_complete.connect(completes.append)
    worker.error_received.connect(errors.append)
    worker.run()
    return tokens, completes, errors


# ── collect_system_context ───────────────────────────────────────────────────
def test_collect_system_context(app, monkeypatch):
    monkeypatch.setattr(ai_chat_module.psutil, "cpu_percent", lambda interval=1: 42.0)
    monkeypatch.setattr(ai_chat_module.psutil, "cpu_count", lambda logical=True: 8)
    ram = types.SimpleNamespace(total=16 * 1024**3, used=8 * 1024**3, percent=50)
    monkeypatch.setattr(ai_chat_module.psutil, "virtual_memory", lambda: ram)
    disk = types.SimpleNamespace(
        device="C:\\", mountpoint="C:\\", used=100 * 1024**3,
        total=200 * 1024**3, percent=50,
    )
    monkeypatch.setattr(ai_chat_module.psutil, "disk_partitions", lambda all=False: [disk])
    monkeypatch.setattr(ai_chat_module.psutil, "disk_usage", lambda mountpoint: disk)

    text = collect_system_context()

    assert "42.0%" in text
    assert "8 logical cores" in text
    assert "8.0GB" in text
    assert "16.0GB" in text
    assert "C:\\" in text


def test_collect_system_context_skips_unreadable_disk(app, monkeypatch):
    monkeypatch.setattr(ai_chat_module.psutil, "cpu_percent", lambda interval=1: 10.0)
    monkeypatch.setattr(ai_chat_module.psutil, "cpu_count", lambda logical=True: 4)
    ram = types.SimpleNamespace(total=8 * 1024**3, used=2 * 1024**3, percent=25)
    monkeypatch.setattr(ai_chat_module.psutil, "virtual_memory", lambda: ram)
    disk = types.SimpleNamespace(device="Z:\\", mountpoint="Z:\\")
    monkeypatch.setattr(ai_chat_module.psutil, "disk_partitions", lambda all=False: [disk])
    monkeypatch.setattr(
        ai_chat_module.psutil, "disk_usage", lambda mountpoint: (_ for _ in ()).throw(PermissionError())
    )

    text = collect_system_context()

    assert "No disk info available" in text


# ── Widget construction ──────────────────────────────────────────────────────
def test_ai_chat_creation(app, qtbot):
    chat = AIChatWidget()
    qtbot.addWidget(chat)
    assert chat.layout() is not None


# ── StreamingWorker behaviour ────────────────────────────────────────────────
def test_streaming_worker_success(app, qtbot, monkeypatch):
    _patch_requests(monkeypatch, resp=_FakeStreamingResponse())
    worker = StreamingWorker("hi")
    tokens, completes, errors = _run_worker(worker)
    assert tokens == ["All", " good"]
    assert len(completes) == 1
    assert completes[0]["done"] is True
    assert errors == []


def test_streaming_worker_uses_long_timeout_and_stream(app, qtbot, monkeypatch):
    captured = {}
    _patch_requests(monkeypatch, resp=_FakeStreamingResponse(), capture=captured)
    worker = StreamingWorker("hi")
    _run_worker(worker)
    assert captured["timeout"] == REQUEST_TIMEOUT
    assert captured["url"].endswith("/api/chat/stream")
    assert captured["stream"] is True
    assert REQUEST_TIMEOUT >= 60


def test_streaming_worker_ignores_malformed_sse(app, qtbot, monkeypatch):
    resp = _FakeStreamingResponse(
        [
            b"data: {not valid json",
            b"data: " + json.dumps({"type": "token", "content": "ok", "done": False}).encode(),
        ]
    )
    _patch_requests(monkeypatch, resp=resp)
    worker = StreamingWorker("hi")
    tokens, completes, errors = _run_worker(worker)
    assert tokens == ["ok"]
    assert len(completes) == 1
    assert errors == []


def test_streaming_worker_cancelled_emits_complete_without_tokens(app, qtbot, monkeypatch):
    _patch_requests(monkeypatch, resp=_FakeStreamingResponse())
    worker = StreamingWorker("hi")
    worker.cancel()
    tokens, completes, errors = _run_worker(worker)
    assert tokens == []
    assert len(completes) == 1
    assert completes[0]["cancelled"] is True
    assert errors == []


def test_streaming_worker_cancel_closes_response(app, qtbot, monkeypatch):
    resp = _FakeStreamingResponse([])
    _patch_requests(monkeypatch, resp=resp)
    worker = StreamingWorker("hi")
    _run_worker(worker)
    assert worker._cancelled is False
    assert not resp.closed
    worker.cancel()
    assert worker._cancelled is True
    assert resp.closed is True


def test_streaming_worker_timeout_helpful_message(app, qtbot, monkeypatch):
    _patch_requests(monkeypatch, exc=requests.exceptions.ReadTimeout("Read timed out"))
    worker = StreamingWorker("hi")
    tokens, completes, errors = _run_worker(worker)
    assert tokens == []
    assert len(completes) == 0
    assert len(errors) == 1
    assert "did not respond" in errors[0]


def test_streaming_worker_connection_error_helpful_message(app, qtbot, monkeypatch):
    _patch_requests(
        monkeypatch, exc=requests.exceptions.ConnectionError("Connection refused")
    )
    worker = StreamingWorker("hi")
    _, _, errors = _run_worker(worker)
    assert len(errors) == 1
    assert "Could not connect" in errors[0]


def test_streaming_worker_generic_request_error(app, qtbot, monkeypatch):
    _patch_requests(monkeypatch, exc=requests.exceptions.RequestException("boom"))
    worker = StreamingWorker("hi")
    _, completes, errors = _run_worker(worker)
    assert len(completes) == 0
    assert len(errors) == 1
    assert "Backend error" in errors[0]


# ── AIChatWidget handler behaviour ───────────────────────────────────────────
def _widget_with_thinking(app, qtbot):
    chat = AIChatWidget()
    qtbot.addWidget(chat)
    chat._thinking_pos = chat.chat_area.document().characterCount()
    chat.chat_area.append("<i>AI is thinking...</i>")
    return chat


def test_handle_token_replaces_thinking_and_appends(app, qtbot):
    chat = _widget_with_thinking(app, qtbot)
    chat.handle_token("hello")
    text = chat.chat_area.toPlainText()
    assert "thinking" not in text
    assert "hello" in text


def test_handle_token_no_thinking_still_appends(app, qtbot):
    chat = AIChatWidget()
    qtbot.addWidget(chat)
    chat.handle_token("world")
    assert "world" in chat.chat_area.toPlainText()


def test_handle_stream_complete_clears_thinking_and_enables_input(app, qtbot):
    chat = _widget_with_thinking(app, qtbot)
    chat.input_field.setDisabled(True)
    chat.handle_stream_complete({"done": True})
    assert "thinking" not in chat.chat_area.toPlainText()
    assert chat.input_field.isEnabled() is True
    assert chat.btn_send.isEnabled() is True


def test_handle_error_clears_thinking_shows_error_and_enables(app, qtbot):
    chat = _widget_with_thinking(app, qtbot)
    chat.input_field.setDisabled(True)
    chat.handle_error("something broke")
    text = chat.chat_area.toPlainText()
    assert "thinking" not in text
    assert "Error:" in text
    assert "something broke" in text
    assert chat.input_field.isEnabled() is True


def test_handle_error_escapes_user_input(app, qtbot):
    chat = _widget_with_thinking(app, qtbot)
    chat.handle_error("<script>alert(1)</script>")
    html = chat.chat_area.toHtml()
    assert "<script>" not in html


# ── End-to-end widget streaming flow ─────────────────────────────────────────
def test_send_message_streams_tokens_in_chat(app, qtbot, monkeypatch):
    _patch_requests(monkeypatch, resp=_FakeStreamingResponse())
    chat = AIChatWidget()
    qtbot.addWidget(chat)
    chat.input_field.setText("hello")
    chat.send_message()
    qtbot.waitUntil(lambda: chat.input_field.isEnabled(), timeout=5000)
    text = chat.chat_area.toPlainText()
    assert "You:" in text
    assert "All" in text
    assert " good" in text
    assert "thinking" not in text


def test_send_message_ignores_blank_input(app, qtbot, monkeypatch):
    _patch_requests(monkeypatch, resp=_FakeStreamingResponse())
    chat = AIChatWidget()
    qtbot.addWidget(chat)
    chat.input_field.setText("   ")
    chat.send_message()
    assert chat.input_field.isEnabled() is True


def test_send_message_stream_error_re_enables_input(app, qtbot, monkeypatch):
    _patch_requests(
        monkeypatch, exc=requests.exceptions.ConnectionError("refused")
    )
    chat = AIChatWidget()
    qtbot.addWidget(chat)
    chat.input_field.setText("hello")
    chat.send_message()
    qtbot.waitUntil(lambda: chat.input_field.isEnabled(), timeout=5000)
    assert "Error:" in chat.chat_area.toPlainText()


# ── Vision / image analysis ──────────────────────────────────────────────────
def _make_png(path: Path, size: int = 16) -> Path:
    from PySide6.QtGui import QImage

    img = QImage(size, size, QImage.Format.Format_RGB32)
    img.fill(Qt.GlobalColor.white)
    assert img.save(str(path), "PNG")
    return path


def _patch_file_dialog(monkeypatch, path):
    monkeypatch.setattr(
        ai_chat_module.QFileDialog,
        "getOpenFileName",
        lambda *a, **k: (str(path), ""),
    )


class _FakeVisionService:
    def __init__(self, result=None, exc=None):
        self.calls = []
        self.result = result or {"analysis": "VISION_RESULT"}
        self.exc = exc

    def analyze_image(self, image_path, prompt, model="llava:7b", timeout=60):
        self.calls.append((Path(image_path), prompt))
        if self.exc is not None:
            raise self.exc
        return self.result


def test_attach_image_sets_preview(app, qtbot, tmp_path, monkeypatch):
    path = _make_png(tmp_path / "shot.png")
    _patch_file_dialog(monkeypatch, path)
    chat = AIChatWidget()
    qtbot.addWidget(chat)
    chat.attach_image()
    assert chat._attached_image_path == path
    assert not chat.preview_label.isHidden()
    assert not chat.btn_remove_image.isHidden()


def test_attach_image_invalid_file_shows_error(app, qtbot, tmp_path, monkeypatch):
    path = tmp_path / "note.txt"
    path.write_text("not an image")
    _patch_file_dialog(monkeypatch, path)
    chat = AIChatWidget()
    qtbot.addWidget(chat)
    chat.attach_image()
    assert chat._attached_image_path is None
    assert chat.preview_label.isHidden()
    assert "not a readable image" in chat.chat_area.toPlainText()


def test_remove_image_clears_attachment(app, qtbot, tmp_path, monkeypatch):
    path = _make_png(tmp_path / "shot.png")
    _patch_file_dialog(monkeypatch, path)
    chat = AIChatWidget()
    qtbot.addWidget(chat)
    chat.attach_image()
    chat.remove_image()
    assert chat._attached_image_path is None
    assert chat.preview_label.isHidden()
    assert chat.btn_remove_image.isHidden()


def test_analyze_error_dialog_sets_attachment_and_prompt(app, qtbot, tmp_path, monkeypatch):
    path = _make_png(tmp_path / "err.png")
    _patch_file_dialog(monkeypatch, path)
    chat = AIChatWidget()
    qtbot.addWidget(chat)
    chat.analyze_error_dialog()
    assert chat._attached_image_path == path
    assert "error dialog" in chat.input_field.text().lower()


def test_send_vision_shows_result_and_clears_attachment(app, qtbot, tmp_path):
    path = _make_png(tmp_path / "shot.png")
    chat = AIChatWidget()
    qtbot.addWidget(chat)
    chat._vision_service = _FakeVisionService(result={"analysis": "VISION_RESULT"})
    chat._set_attached_image(path)
    chat.input_field.setText("what is shown")
    chat.send_message()
    qtbot.waitUntil(lambda: chat.input_field.isEnabled(), timeout=5000)
    text = chat.chat_area.toPlainText()
    assert "VISION_RESULT" in text
    assert "analyzing image" in text
    assert chat._attached_image_path is None


def test_send_vision_blank_text_uses_default_prompt(app, qtbot, tmp_path):
    path = _make_png(tmp_path / "shot.png")
    fake = _FakeVisionService()
    chat = AIChatWidget()
    qtbot.addWidget(chat)
    chat._vision_service = fake
    chat._set_attached_image(path)
    chat.send_message()
    qtbot.waitUntil(lambda: chat.input_field.isEnabled(), timeout=5000)
    assert fake.calls
    assert fake.calls[0][1] == "Analyze this image."


def test_send_vision_error_re_enables_input(app, qtbot, tmp_path):
    path = _make_png(tmp_path / "shot.png")
    chat = AIChatWidget()
    qtbot.addWidget(chat)
    chat._vision_service = _FakeVisionService(
        exc=requests.exceptions.ConnectionError("refused")
    )
    chat._set_attached_image(path)
    chat.input_field.setText("describe")
    chat.send_message()
    qtbot.waitUntil(lambda: chat.input_field.isEnabled(), timeout=5000)
    assert "Error:" in chat.chat_area.toPlainText()


def test_vision_worker_emits_result(app, qtbot, tmp_path):
    path = _make_png(tmp_path / "shot.png")
    service = _FakeVisionService(result={"analysis": "ANALYZED"})
    worker = VisionWorker(path, "prompt", service=service)
    results, errors = [], []
    worker.result_received.connect(results.append)
    worker.error_received.connect(errors.append)
    worker.run()
    assert results == ["ANALYZED"]
    assert errors == []


def test_vision_worker_emits_error_on_value_error(app, qtbot, tmp_path):
    path = tmp_path / "shot.gif"
    path.write_bytes(b"GIF89a")
    worker = VisionWorker(path, "prompt", service=VisionAnalysisService())
    results, errors = [], []
    worker.result_received.connect(results.append)
    worker.error_received.connect(errors.append)
    worker.run()
    assert results == []
    assert len(errors) == 1
    assert "Image error" in errors[0]


@pytest.mark.parametrize(
    "exc,expected",
    [
        (requests.exceptions.ConnectionError("down"), "Could not connect"),
        (requests.exceptions.ReadTimeout("slow"), "did not respond"),
        (requests.exceptions.RequestException("boom"), "Backend error"),
    ],
)
def test_vision_worker_error_messages(app, qtbot, tmp_path, exc, expected):
    path = _make_png(tmp_path / "shot.png")
    worker = VisionWorker(
        path, "prompt", service=_FakeVisionService(exc=exc)
    )
    errors = []
    worker.error_received.connect(errors.append)
    worker.run()
    assert len(errors) == 1
    assert expected in errors[0]


def test_analyze_error_dialog_no_file_returns_early(app, qtbot, tmp_path, monkeypatch):
    monkeypatch.setattr(
        ai_chat_module.QFileDialog,
        "getOpenFileName",
        lambda *a, **k: ("", ""),
    )
    chat = AIChatWidget()
    qtbot.addWidget(chat)
    chat.analyze_error_dialog()
    assert chat._attached_image_path is None
    assert chat.input_field.text() == ""