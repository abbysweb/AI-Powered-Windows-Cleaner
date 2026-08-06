import logging
import os
from pathlib import Path
from typing import Any

from .base import BaseCleaner

logger = logging.getLogger(__name__)

_LOCAL_APPDATA = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
_WINDIR = Path(os.environ.get("WINDIR", r"C:\Windows"))
_PROGRAMDATA = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData"))


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


class ThumbnailCacheCleaner(BaseCleaner):
    def __init__(self) -> None:
        super().__init__()
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 10
        self._targets = [
            _LOCAL_APPDATA / "Microsoft" / "Windows" / "Explorer",
            _WINDIR / "ServiceProfiles" / "LocalService" / "AppData" / "Local"
            / "Microsoft" / "Windows" / "Explorer",
        ]

    @property
    def name(self) -> str:
        return "Thumbnail Cache"

    def scan(self) -> dict[str, Any]:
        self._files = []
        self._size = 0
        for target in self._targets:
            if not target.exists():
                continue
            for path in target.glob("thumbcache_*.db"):
                try:
                    self._size += path.stat().st_size
                    self._files.append(path)
                except (OSError, PermissionError):
                    continue
        return {
            "file_count": len(self._files),
            "size_bytes": self._size,
            "risk_score": self._risk_score,
        }

    def explain(self) -> str:
        return (
            "Windows Explorer thumbnail cache (thumbcache_*.db). "
            "Safe to delete - thumbnails are rebuilt automatically."
        )


class WindowsUpdateCacheCleaner(BaseCleaner):
    def __init__(self) -> None:
        super().__init__()
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 10
        self._target = _WINDIR / "SoftwareDistribution" / "Download"

    @property
    def name(self) -> str:
        return "Windows Update Cache"

    def scan(self) -> dict[str, Any]:
        self._files = []
        self._size = 0
        self._files, self._size = _scan_folder(self._target, self._files, self._size)
        return {
            "file_count": len(self._files),
            "size_bytes": self._size,
            "risk_score": self._risk_score,
        }

    def explain(self) -> str:
        return (
            "Downloaded Windows Update packages. Safe to delete - "
            "updates are re-downloaded if ever needed again."
        )


class DeliveryOptimizationCleaner(BaseCleaner):
    def __init__(self) -> None:
        super().__init__()
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 10
        self._target = _WINDIR / "SoftwareDistribution" / "DeliveryOptimization"

    @property
    def name(self) -> str:
        return "Delivery Optimization"

    def scan(self) -> dict[str, Any]:
        self._files = []
        self._size = 0
        self._files, self._size = _scan_folder(self._target, self._files, self._size)
        return {
            "file_count": len(self._files),
            "size_bytes": self._size,
            "risk_score": self._risk_score,
        }

    def explain(self) -> str:
        return (
            "Stale update payloads cached for peer-to-peer delivery. "
            "Safe to delete."
        )


class ErrorReportCleaner(BaseCleaner):
    def __init__(self) -> None:
        super().__init__()
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 10
        self._targets = [
            _PROGRAMDATA / "Microsoft" / "Windows" / "WER",
            _LOCAL_APPDATA / "Microsoft" / "Windows" / "WER",
        ]

    @property
    def name(self) -> str:
        return "Error Reports"

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
            "Windows Error Reporting (WER) reports and crash queues. "
            "Safe to delete - diagnostics only, no system files."
        )


class PrefetchCleaner(BaseCleaner):
    def __init__(self) -> None:
        super().__init__()
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 20
        self._target = _WINDIR / "Prefetch"

    @property
    def name(self) -> str:
        return "Prefetch"

    def scan(self) -> dict[str, Any]:
        self._files = []
        self._size = 0
        self._files, self._size = _scan_folder(self._target, self._files, self._size)
        return {
            "file_count": len(self._files),
            "size_bytes": self._size,
            "risk_score": self._risk_score,
        }

    def explain(self) -> str:
        return (
            "Windows prefetch files that track application startup. "
            "Safe to delete - Windows rebuilds them on next launch."
        )


class LogFilesCleaner(BaseCleaner):
    def __init__(self) -> None:
        super().__init__()
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 20
        self._targets = [
            _WINDIR / "Logs",
            _WINDIR / "Panther",
            _WINDIR / "inf" / "setupapi.dev.log",
        ]

    @property
    def name(self) -> str:
        return "Log Files"

    def scan(self) -> dict[str, Any]:
        self._files = []
        self._size = 0
        for target in self._targets:
            if target.is_file():
                try:
                    self._size += target.stat().st_size
                    self._files.append(target)
                except (OSError, PermissionError):
                    continue
            else:
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
            "Windows log and setup log files. Safe to delete - "
            "they are purely diagnostic text."
        )


class WinSxSTempCleaner(BaseCleaner):
    def __init__(self) -> None:
        super().__init__()
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 15
        self._target = _WINDIR / "WinSxS" / "Temp"

    @property
    def name(self) -> str:
        return "Installer Temp"

    def scan(self) -> dict[str, Any]:
        self._files = []
        self._size = 0
        self._files, self._size = _scan_folder(self._target, self._files, self._size)
        return {
            "file_count": len(self._files),
            "size_bytes": self._size,
            "risk_score": self._risk_score,
        }

    def explain(self) -> str:
        return (
            "Pending component store (WinSxS) temporary operations. "
            "Safe to delete - left over from previous servicing."
        )


class FontCacheCleaner(BaseCleaner):
    def __init__(self) -> None:
        super().__init__()
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 40
        self._target = _WINDIR / "ServiceProfiles" / "LocalService" / "AppData" / "Local"

    @property
    def name(self) -> str:
        return "Font Cache"

    def scan(self) -> dict[str, Any]:
        self._files = []
        self._size = 0
        if not self._target.exists():
            return {"file_count": 0, "size_bytes": 0, "risk_score": self._risk_score}
        for path in self._target.glob("FontCache*"):
            try:
                self._size += path.stat().st_size
                self._files.append(path)
            except (OSError, PermissionError):
                continue
        return {
            "file_count": len(self._files),
            "size_bytes": self._size,
            "risk_score": self._risk_score,
        }

    def explain(self) -> str:
        return (
            "Windows font cache files. Rebuilt automatically, but they are "
            "often locked while Windows is running."
        )
