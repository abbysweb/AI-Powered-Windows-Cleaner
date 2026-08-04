from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class CleanResult:
    name: str
    files_deleted: int
    space_freed_bytes: int
    errors: list[str]
    success: bool = True

class CleanerTarget(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def clean(self) -> CleanResult:
        """Perform the cleaning operation and return the results."""
        pass
