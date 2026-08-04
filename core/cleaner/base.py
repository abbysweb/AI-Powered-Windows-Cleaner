from abc import ABC, abstractmethod
from typing import Any


class BaseCleaner(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the cleaning target"""

    @abstractmethod
    def scan(self) -> dict[str, Any]:
        """Scan the target and return list of files/items."""

    @abstractmethod
    def calculate_size(self) -> int:
        """Calculate the total recoverable size in bytes."""

    @abstractmethod
    def delete(self) -> bool:
        """Perform the actual deletion."""

    @abstractmethod
    def rollback(self) -> bool:
        """Restore files if they were quarantined/backed up."""

    @abstractmethod
    def explain(self) -> str:
        """Return a natural language explanation of what this target is."""
