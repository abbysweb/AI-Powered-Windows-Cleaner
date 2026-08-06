import logging
import os
import time
from pathlib import Path
from typing import Any

from .base import BaseCleaner

logger = logging.getLogger(__name__)

_LOCAL_APPDATA = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
_WINDIR = Path(os.environ.get("WINDIR", r"C:\Windows"))


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


class ShaderCacheCleaner(BaseCleaner):
    def __init__(self) -> None:
        super().__init__()
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 30
        self._targets = [
            _LOCAL_APPDATA / "D3DSCache",
            _LOCAL_APPDATA / "NVIDIA" / "DXCache",
            _LOCAL_APPDATA / "NVIDIA" / "GLCache",
            _LOCAL_APPDATA / "AMD" / "DXCache",
            _LOCAL_APPDATA / "AMD" / "GLCache",
            _LOCAL_APPDATA / "Intel" / "ShaderCache",
            _LOCAL_APPDATA / "NVIDIA Corporation" / "NV_Cache",
        ]

    @property
    def name(self) -> str:
        return "GPU Shader Cache"

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
            "GPU shader caches (D3DSCache, NVIDIA, AMD, Intel). "
            "Safe to delete - shaders recompile on next run; "
            "the first launch after cleaning may be slightly slower."
        )


class CrashDumpCleaner(BaseCleaner):
    def __init__(self) -> None:
        super().__init__()
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 25
        self._targets = [_WINDIR / "Minidump", _WINDIR / "LiveKernelReports"]
        self._memory_dump = _WINDIR / "MEMORY.DMP"

    @property
    def name(self) -> str:
        return "Crash Dumps"

    def scan(self) -> dict[str, Any]:
        self._files = []
        self._size = 0
        for target in self._targets:
            self._files, self._size = _scan_folder(target, self._files, self._size)
        if self._memory_dump.exists():
            try:
                self._size += self._memory_dump.stat().st_size
                self._files.append(self._memory_dump)
            except (OSError, PermissionError):
                pass
        return {
            "file_count": len(self._files),
            "size_bytes": self._size,
            "risk_score": self._risk_score,
        }

    def explain(self) -> str:
        return (
            "Crash dump files (Minidump, MEMORY.DMP, LiveKernelReports). "
            "Safe to delete unless you need them for debugging a crash."
        )


class EmptyFoldersCleaner(BaseCleaner):
    def __init__(self) -> None:
        super().__init__()
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 5
        self._roots = [
            Path(os.environ.get("USERPROFILE", Path.home())) / "Downloads",
            Path(os.environ.get("TEMP", Path.home() / "AppData" / "Local" / "Temp")),
            Path(os.environ.get("WINDIR", r"C:\Windows")) / "Temp",
        ]

    @property
    def name(self) -> str:
        return "Empty Folders"

    def scan(self) -> dict[str, Any]:
        self._files = []
        self._size = 0
        for root in self._roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                try:
                    if path.is_dir() and not any(path.iterdir()):
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
            "Empty folders left behind in Downloads and temp directories. "
            "Completely safe to remove."
        )


class WindowsOldCleaner(BaseCleaner):
    def __init__(self) -> None:
        super().__init__()
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 50
        self._target = Path(os.environ.get("SystemDrive", "C:")) / "Windows.old"

    @property
    def name(self) -> str:
        return "Windows.old"

    def scan(self) -> dict[str, Any]:
        self._files = []
        self._size = 0
        if self._target.exists():
            try:
                self._size = sum(
                    p.stat().st_size
                    for p in self._target.rglob("*")
                    if p.is_file()
                )
            except (OSError, PermissionError):
                self._size = 0
            self._files.append(self._target)
        return {
            "file_count": len(self._files),
            "size_bytes": self._size,
            "risk_score": self._risk_score,
        }

    def explain(self) -> str:
        return (
            "Previous Windows installation kept for rollback after a major "
            "upgrade. Safe to delete once your new version is stable - "
            "this can free many gigabytes, but requires administrator rights."
        )


class StaleLargeFilesCleaner(BaseCleaner):
    def __init__(self, min_size_mb: int | None = None, max_age_days: int | None = None):
        super().__init__()
        self._files: list[Path] = []
        self._size: int = 0
        self._risk_score: int = 60
        self.min_size_mb = min_size_mb or int(
            os.environ.get("STALE_MIN_SIZE_MB", "100")
        )
        self.max_age_days = max_age_days or int(
            os.environ.get("STALE_MAX_AGE_DAYS", "30")
        )
        self._roots = [
            Path(os.environ.get("USERPROFILE", Path.home())) / "Downloads"
        ]

    @property
    def name(self) -> str:
        return "Stale Large Files"

    def scan(self) -> dict[str, Any]:
        self._files = []
        self._size = 0
        cutoff = time.time() - self.max_age_days * 86400
        min_bytes = self.min_size_mb * 1024 * 1024
        for root in self._roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                try:
                    st = path.stat()
                except (OSError, PermissionError):
                    continue
                if st.st_size >= min_bytes and st.st_mtime < cutoff:
                    self._files.append(path)
                    self._size += st.st_size
        return {
            "file_count": len(self._files),
            "size_bytes": self._size,
            "risk_score": self._risk_score,
        }

    def explain(self) -> str:
        return (
            f"Large files over {self.min_size_mb} MB that have not been "
            f"modified in over {self.max_age_days} days. Only files in your "
            "Downloads folder are considered. Review carefully before deleting."
        )
