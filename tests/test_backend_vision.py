import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

# Backend is a standalone FastAPI+Ollama container. These tests run inside the
# container (or a dev env with the backend deps) and skip gracefully elsewhere.
pytest.importorskip("ollama")

from fastapi import HTTPException

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from main import (
    MAX_IMAGE_BYTES,
    PNG_MAGIC,
    VisionRequest,
    app,
    validate_image,
)

JPEG_MAGIC = b"\xff\xd8\xff"
WEBP_HEADER = b"RIFF" + b"\x00" * 4 + b"WEBP"


def test_vision_request_defaults():
    req = VisionRequest(image_base64="QUFBQQ==")
    assert req.prompt == "Analyze this image."
    assert req.model == "llava:7b"
    assert req.temperature == 0.2


def test_vision_request_requires_image_base64():
    with pytest.raises(ValidationError):
        VisionRequest()


def test_vision_route_registered():
    paths = {getattr(r, "path", None) for r in app.routes}
    assert "/api/vision/analyze" in paths


def test_validate_image_accepts_png():
    validate_image(PNG_MAGIC + b"rest")


def test_validate_image_accepts_jpeg():
    validate_image(JPEG_MAGIC + b"\xe0" * 10)


def test_validate_image_accepts_webp():
    validate_image(WEBP_HEADER + b"rest")


def test_validate_image_rejects_empty():
    with pytest.raises(HTTPException) as exc_info:
        validate_image(b"")
    assert exc_info.value.status_code == 400


def test_validate_image_rejects_oversized():
    with pytest.raises(HTTPException) as exc_info:
        validate_image(b"\x89PNG" + b"x" * (MAX_IMAGE_BYTES + 1))
    assert exc_info.value.status_code == 413


def test_validate_image_rejects_unknown_format():
    with pytest.raises(HTTPException) as exc_info:
        validate_image(b"\x00\x01\x02\x03 not an image")
    assert exc_info.value.status_code == 415
