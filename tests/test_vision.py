import base64
import sys
from pathlib import Path

import pytest
import requests

from ai_health_copilot.ai.vision import (
    BACKEND_URL,
    MAX_IMAGE_BYTES,
    SUPPORTED_EXTENSIONS,
    VisionAnalysisService,
)

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


@pytest.fixture(scope="session")
def app():
    from PySide6.QtWidgets import QApplication

    instance = QApplication.instance()
    if instance is None:
        instance = QApplication(sys.argv)
    yield instance


def _make_png(path: Path, size: int = 16) -> Path:
    from PySide6.QtGui import QImage

    img = QImage(size, size, QImage.Format.Format_RGB32)
    img.fill(0xFFFFFFFF)
    assert img.save(str(path), "PNG")
    return path


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def _patch_post(monkeypatch, payload=None, exc=None, capture=None):
    def fake_post(url, **kwargs):
        if capture is not None:
            capture["url"] = url
            capture["json"] = kwargs.get("json")
            capture["timeout"] = kwargs.get("timeout")
        if exc is not None:
            raise exc
        return _FakeResponse(payload)

    monkeypatch.setattr(
        "ai_health_copilot.ai.vision.requests.post", fake_post
    )


# ── encode_image ─────────────────────────────────────────────────────────────
def test_encode_image_returns_valid_base64(app, tmp_path):
    path = _make_png(tmp_path / "shot.png")
    encoded = VisionAnalysisService().encode_image(path)
    raw = base64.b64decode(encoded)
    assert raw.startswith(PNG_MAGIC)


def test_encode_image_rejects_oversized(app, tmp_path):
    path = tmp_path / "big.png"
    path.write_bytes(b"\0" * (MAX_IMAGE_BYTES + 1))
    with pytest.raises(ValueError, match="10MB"):
        VisionAnalysisService().encode_image(path)


def test_encode_image_rejects_unsupported_extension(app, tmp_path):
    path = tmp_path / "note.txt"
    path.write_text("hello")
    with pytest.raises(ValueError, match="Unsupported"):
        VisionAnalysisService().encode_image(path)


def test_encode_image_rejects_missing_file(app, tmp_path):
    with pytest.raises(ValueError, match="does not exist"):
        VisionAnalysisService().encode_image(tmp_path / "nope.png")


def test_supported_extensions():
    assert {".png", ".jpg", ".jpeg", ".webp"} == SUPPORTED_EXTENSIONS


# ── analyze_image ────────────────────────────────────────────────────────────
def test_analyze_image_sends_payload(app, tmp_path, monkeypatch):
    path = _make_png(tmp_path / "shot.png")
    capture = {}
    _patch_post(
        monkeypatch,
        payload={"analysis": "A result", "model": "llava:7b"},
        capture=capture,
    )
    result = VisionAnalysisService().analyze_image(path, "What is this?")

    assert result["analysis"] == "A result"
    assert capture["url"] == f"{BACKEND_URL}/api/vision/analyze"
    assert capture["timeout"] == 60
    payload = capture["json"]
    assert payload["prompt"] == "What is this?"
    assert payload["model"] == "llava:7b"
    assert base64.b64decode(payload["image_base64"]).startswith(PNG_MAGIC)


def test_analyze_image_accepts_str_path(app, tmp_path, monkeypatch):
    path = _make_png(tmp_path / "shot.png")
    capture = {}
    _patch_post(monkeypatch, payload={"analysis": "ok"}, capture=capture)
    VisionAnalysisService().analyze_image(str(path), "Prompt")
    assert capture["json"]["prompt"] == "Prompt"


def test_analyze_image_raises_connection_error(app, tmp_path, monkeypatch):
    path = _make_png(tmp_path / "shot.png")
    _patch_post(monkeypatch, exc=requests.exceptions.ConnectionError("down"))
    with pytest.raises(requests.exceptions.ConnectionError):
        VisionAnalysisService().analyze_image(path, "Prompt")
