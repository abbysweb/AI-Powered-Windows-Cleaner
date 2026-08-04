import logging
import os
from pathlib import Path
from typing import Any

from core.rollback.manager import QuarantineManager

from .base import BaseCleaner

logger = logging.getLogger(__name__)


class DownloadsCleaner(BaseCleaner):
    def __init__(self, quarantine_manager: QuarantineManager | None = None):
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 80  # High risk - user files
        self.qm = quarantine_manager or QuarantineManager()

        # Determine downloads path
        if os.name == "nt":
            self.downloads_dir = Path.home() / "Downloads"
        else:
            self.downloads_dir = Path.home() / "Downloads"

    @property
    def name(self) -> str:
        return "Downloads"

    def scan(self) -> dict[str, Any]:
        self._files = []
        self._size = 0

        if not self.downloads_dir.exists():
            return {"file_count": 0, "size_bytes": 0, "risk_score": self._risk_score}

        # Fetch ignored paths dynamically
        ignored_paths = set()
        try:
            from database.manager import DatabaseManager

            db = DatabaseManager()
            ignored_paths = set(db.get_ignored_folders())
        except Exception:
            pass

        try:
            for path in self.downloads_dir.rglob("*"):
                if path.is_file():

                    # Check if file is inside an ignored folder
                    is_ignored = False
                    for ignored in ignored_paths:
                        if path.is_relative_to(Path(ignored)):
                            is_ignored = True
                            break

                    if is_ignored:
                        continue

                    try:
                        self._size += path.stat().st_size
                        self._files.append(path)
                    except Exception as e:
                        logger.warning(f"Could not stat {path}: {e}")
        except PermissionError:
            return {"error": "Permission denied accessing Downloads"}

        return {
            "file_count": len(self._files),
            "size_bytes": self._size,
            "risk_score": self._risk_score,
        }

    def calculate_size(self) -> int:
        return self._size

    def delete(self) -> bool:
        success = True
        for path in self._files:
            try:
                # Quarantine the file first
                self.qm.backup_file(path)
                path.unlink(missing_ok=True)
            except Exception as e:
                logger.error(f"Failed to delete {path}: {e}")
                success = False
        return success

    def rollback(self) -> bool:
        # Full rollback relies on QuarantineManager tracking which files it moved.
        # For this prototype, we would need to store mappings.
        return False

    def explain(self) -> str:
        return "Clears the current user's Downloads folder. High risk as it contains downloaded user files."
