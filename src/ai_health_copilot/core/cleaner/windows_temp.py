import logging
import os
from pathlib import Path
from typing import Any

from .base import BaseCleaner

logger = logging.getLogger(__name__)

WINDOWS_TEMP = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Temp"


class WindowsTempCleaner(BaseCleaner):
    def __init__(self):
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
                    except Exception:
                        pass
        except PermissionError:
            return {
                "error": "Administrator privileges required to scan full Windows Temp"
            }

        return {
            "file_count": len(self._files),
            "size_bytes": self._size,
            "risk_score": self._risk_score,
        }

    def calculate_size(self) -> int:
        return self._size

    def delete(self) -> bool:
        if not hasattr(self, "qm"):
            from ai_health_copilot.core.rollback.manager import QuarantineManager

            self.qm = QuarantineManager()

        success = True
        for path in self._files:
            try:
                self.qm.backup_file(path)
                path.unlink(missing_ok=True)
            except Exception as e:
                logger.error(f"Failed to delete {path}: {e}")
                success = False
        return success

    def rollback(self) -> bool:
        # Placeholder for phase 4 rollback feature
        return False

    def explain(self) -> str:
        return (
            "Windows Temp contains temporary files created by the operating system "
            "and application installers. These files are typically safe to delete, "
            "but files currently in use will be skipped."
        )
