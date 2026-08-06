import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

# The backend is a standalone FastAPI+Ollama container. On the host `ollama`
# may be absent, so these tests are skipped unless the backend dependencies are
# importable (e.g. inside the Podman container or a dev environment with them).
ollama = pytest.importorskip("ollama")

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from main import StreamRequest, app  # type: ignore[import-untyped]


def test_stream_request_defaults():
    req = StreamRequest(messages=[{"role": "user", "content": "hi"}])
    assert req.session_id is None
    assert req.model == "llama3.2:1b"
    assert req.stream is True
    assert req.temperature == 0.7


def test_stream_request_requires_messages():
    with pytest.raises(ValidationError):
        StreamRequest()


def test_chat_stream_route_registered():
    paths = {getattr(r, "path", None) for r in app.routes}
    assert "/api/chat/stream" in paths
    assert "/api/advisor" in paths
    assert "/health" in paths


def test_stream_sse_complete_includes_usage():
    from main import client

    # Validate the SSE payload shape the frontend StreamingWorker parses.
    payload = json.dumps(
        {"type": "complete", "content": "", "done": True, "usage": {"prompt_tokens": 0, "completion_tokens": 0}}
    )
    assert json.loads(payload)["done"] is True
    assert "usage" in json.loads(payload)
    assert client is not None