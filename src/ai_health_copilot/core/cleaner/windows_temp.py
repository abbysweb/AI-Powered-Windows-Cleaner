import logging
import os
from pathlib import Path
from typing import Any

from .base import BaseCleaner

logger = logging.getLogger(__name__)

WINDOWS_TEMP = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Temp"


class WindowsTempCleaner(BaseCleaner):
    def __init__(self) -> None:
        super().__init__()
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 20

    @property
    def name(self) -> str:
        return "Windows Temp"

    def scan(self) -> dict[str, Any]:
        self._files = []
        self._size = 0

        if not WINDOWS_TEMP.exists():
            return {"file_count": 0, "size_bytes": 0}

        try:
            for path in WINDOWS_TEMP.rglob("*"):
                if path.is_file():
                    try:
                        self._size += path.stat().st_size
                        self._files.append(path)
                    except Exception as e:  # pragma: no cover
                        logger.debug(f"Scan error: {e}")
        except PermissionError:  # pragma: no cover
            return {
                "error": "Administrator privileges required to scan full Windows Temp"
            }

        return {
            "file_count": len(self._files),
            "size_bytes": self._size,
            "risk_score": self._risk_score,
        }

    def explain(self) -> str:
        return (
            "Windows Temp contains temporary files created by the operating system "
            "and application installers. These files are typically safe to delete, "
            "but files currently in use will be skipped."
        )
