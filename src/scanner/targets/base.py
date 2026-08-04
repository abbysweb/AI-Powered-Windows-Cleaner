from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class ScanResult:
    name: str
    size_bytes: int
    file_count: int
    error: str | None = None
    is_safe: bool = True

class ScannerTarget(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def scan(self) -> ScanResult:
        """Scan the target and return size and count of cleanable files."""
        pass
