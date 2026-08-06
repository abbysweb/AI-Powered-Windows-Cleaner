import base64
import logging
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

BACKEND_URL = "http://localhost:8000"
MAX_IMAGE_BYTES = 10 * 1024 * 1024
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


class VisionAnalysisService:
    """Client-side helper that sends an image to the AI backend for analysis.

    Enforces the same safety constraints as the backend (size + format) before
    anything is uploaded.
    """

    def __init__(self, endpoint_url: str = BACKEND_URL):
        self.endpoint_url = endpoint_url

    def encode_image(self, image_path: Path) -> str:
        if not image_path.is_file():
            raise ValueError(f"Image does not exist: {image_path}")
        if image_path.stat().st_size > MAX_IMAGE_BYTES:
            raise ValueError("Image exceeds the 10MB size limit.")
        if image_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported image type: {image_path.suffix}")
        return base64.b64encode(image_path.read_bytes()).decode("ascii")

    def analyze_image(
        self,
        image_path: Path | str,
        prompt: str,
        model: str = "llava:7b",
        timeout: int = 60,
    ) -> dict:
        """Sends the image for analysis and returns the backend JSON payload."""
        path = Path(image_path)
        payload = {
            "image_base64": self.encode_image(path),
            "prompt": prompt,
            "model": model,
        }
        resp = requests.post(
            f"{self.endpoint_url}/api/vision/analyze",
            json=payload,
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()
