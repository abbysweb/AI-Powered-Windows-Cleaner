import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ai_health_copilot.core.rollback.manager import QuarantineManager

logger = logging.getLogger(__name__)


class BaseCleaner(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the cleaning target"""

    @abstractmethod
    def scan(self) -> dict[str, Any]:
        """Scan the target and return list of files/items."""

    @abstractmethod
    def explain(self) -> str:
        """Return a natural language explanation of what this target is."""

    def __init__(self, quarantine_manager: QuarantineManager | None = None):
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 50
        self.qm = quarantine_manager or QuarantineManager()

    def calculate_size(self) -> int:
        return self._size

    def delete(self) -> bool:
        success = True
        for path in self._files:
            try:
                self.qm.backup_file(path)
                path.unlink(missing_ok=True)
            except Exception as e:  # pragma: no cover
                logger.error(f"Failed to delete {path}: {e}")
                success = False
        return success

    def rollback(self) -> bool:
        return False
