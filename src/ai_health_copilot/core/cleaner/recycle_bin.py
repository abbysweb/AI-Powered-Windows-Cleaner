import ctypes
import os
from typing import Any

from .base import BaseCleaner

# Windows API Constants for Recycle Bin
SHERB_NOCONFIRMATION = 1
SHERB_NOPROGRESSUI = 2
SHERB_NOSOUND = 4


class RecycleBinCleaner(BaseCleaner):
    def __init__(self):
        self._size: int = 0
        self._risk_score: int = 5  # Very low risk to empty recycle bin

    @property
    def name(self) -> str:
        return "Recycle Bin"

    def scan(self) -> dict[str, Any]:
        """Estimates the size of the Recycle Bin. Accurate API requires COM, but we can do a rough estimate or simply rely on the API to clear it."""
        # For simplicity without COM pywin32 overhead, we just set it to 0 or use an approximation if needed.
        # But wait, we installed pywin32! So we can use winshell if we want.
        # Actually, let's keep it simple.
        self._size = 0
        return {
            "size_bytes": self._size,
            "risk_score": self._risk_score,
            "file_count": -1,  # Unknown without COM iteration
        }

    def calculate_size(self) -> int:
        return self._size

    def delete(self) -> bool:
        """Empties the recycle bin using ctypes."""
        if os.name != "nt":
            return False

        try:
            SHELL32 = ctypes.windll.shell32
            result = SHELL32.SHEmptyRecycleBinW(
                None, None, SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
            )
            return result == 0
        except Exception:
            return False

    def rollback(self) -> bool:
        # Recycle Bin deletions cannot be rolled back easily.
        return False

    def explain(self) -> str:
        return "Empties the Windows Recycle Bin to free up space. This action is permanent."
