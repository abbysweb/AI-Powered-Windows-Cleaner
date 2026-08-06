import logging
import os
from pathlib import Path
from typing import Any

from .base import BaseCleaner

logger = logging.getLogger(__name__)

_LOCAL_APPDATA = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
_APPDATA = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))


def _scan_folder(root: Path, files: list[Path], size: int) -> tuple[list[Path], int]:
    if not root.exists():
        return files, size
    for path in root.rglob("*"):
        if path.is_file():
            try:
                size += path.stat().st_size
                files.append(path)
            except (OSError, PermissionError):
                continue
    return files, size


class ChromeCacheCleaner(BaseCleaner):
    def __init__(self) -> None:
        super().__init__()
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 15
        profile = _LOCAL_APPDATA / "Google" / "Chrome" / "User Data" / "Default"
        self._targets = [
            profile / "Cache",
            profile / "Code Cache",
            profile / "GPUCache",
            profile / "GrShaderCache",
        ]

    @property
    def name(self) -> str:
        return "Chrome Cache"

    def scan(self) -> dict[str, Any]:
        self._files = []
        self._size = 0
        for target in self._targets:
            self._files, self._size = _scan_folder(target, self._files, self._size)
        return {
            "file_count": len(self._files),
            "size_bytes": self._size,
            "risk_score": self._risk_score,
        }

    def explain(self) -> str:
        return (
            "Chrome browser cache, code cache and GPU shader cache. "
            "Safe to delete - pages just re-download assets on next visit."
        )


class EdgeCacheCleaner(BaseCleaner):
    def __init__(self) -> None:
        super().__init__()
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 15
        profile = _LOCAL_APPDATA / "Microsoft" / "Edge" / "User Data" / "Default"
        self._targets = [
            profile / "Cache",
            profile / "Code Cache",
            profile / "GPUCache",
        ]

    @property
    def name(self) -> str:
        return "Edge Cache"

    def scan(self) -> dict[str, Any]:
        self._files = []
        self._size = 0
        for target in self._targets:
            self._files, self._size = _scan_folder(target, self._files, self._size)
        return {
            "file_count": len(self._files),
            "size_bytes": self._size,
            "risk_score": self._risk_score,
        }

    def explain(self) -> str:
        return (
            "Microsoft Edge browser cache and GPU cache. "
            "Safe to delete - assets are re-downloaded on demand."
        )


class FirefoxCacheCleaner(BaseCleaner):
    def __init__(self) -> None:
        super().__init__()
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 15
        self._profiles = _APPDATA / "Mozilla" / "Firefox" / "Profiles"

    @property
    def name(self) -> str:
        return "Firefox Cache"

    def scan(self) -> dict[str, Any]:
        self._files = []
        self._size = 0
        if not self._profiles.exists():
            return {"file_count": 0, "size_bytes": 0, "risk_score": self._risk_score}
        for profile in self._profiles.glob("*"):
            for target in (profile / "cache2", profile / "startupCache"):
                self._files, self._size = _scan_folder(
                    target, self._files, self._size
                )
        return {
            "file_count": len(self._files),
            "size_bytes": self._size,
            "risk_score": self._risk_score,
        }

    def explain(self) -> str:
        return (
            "Firefox disk cache and startup cache. "
            "Safe to delete - pages re-fetch assets on demand."
        )
