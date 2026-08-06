import logging
import os
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path

from ai_health_copilot.core.cleaner.safety import is_sensitive_path

try:
    import winreg  # type: ignore[attr-defined]
except ImportError:  # pragma: no cover
    winreg = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

CACHE_MARKERS = (
    "cache",
    "gpu",
    "shader",
    "dxcache",
    "glcache",
    "nvcache",
    "kernelcache",
)


def is_cache_dir(name: str) -> bool:
    """Returns True when a folder name looks like a cache directory."""
    lowered = name.lower()
    return any(marker in lowered for marker in CACHE_MARKERS)

_UNINSTALL_HIVES = (
    (
        "HKLM",
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    ),
    (
        "HKLM",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ),
    (
        "HKCU",
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    ),
)


@dataclass
class InstalledProgram:
    name: str
    publisher: str = ""
    install_date: str = ""


@dataclass
class SoftwareCacheEntry:
    vendor: str
    cache_size: int = 0
    last_used: float = 0.0
    cache_dirs: list[str] = field(default_factory=list)
    installed_name: str = ""


class SoftwareAudit:
    def __init__(self, min_cache_mb: int = 100, max_age_days: int = 60):
        self.min_cache_bytes = min_cache_mb * 1024 * 1024
        self.max_age_days = max_age_days
        self._appdata_roots = [
            Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")),
            Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")),
            Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")),
        ]

    # ── Registry (installed programs) ────────────────────────────────────────
    def installed_programs(self) -> list[InstalledProgram]:
        if winreg is None:
            return []
        programs: list[InstalledProgram] = []
        for hive_name, key_path in _UNINSTALL_HIVES:
            hive = self._resolve_hive(hive_name)
            try:
                key = winreg.OpenKey(hive, key_path)
            except OSError:
                continue
            i = 0
            while True:
                try:
                    sub = winreg.EnumKey(key, i)
                    i += 1
                except OSError:
                    break
                try:
                    skey = winreg.OpenKey(key, sub)
                except OSError:
                    continue
                name = self._reg_value(skey, "DisplayName")
                if name:
                    programs.append(
                        InstalledProgram(
                            name=name,
                            publisher=self._reg_value(skey, "Publisher"),
                            install_date=self._reg_value(skey, "InstallDate"),
                        )
                    )
                winreg.CloseKey(skey)
            winreg.CloseKey(key)
        return programs

    @staticmethod
    def _resolve_hive(name: str):
        if winreg is None:
            return None
        return {
            "HKLM": winreg.HKEY_LOCAL_MACHINE,
            "HKCU": winreg.HKEY_CURRENT_USER,
        }[name]

    @staticmethod
    def _reg_value(key, value_name: str) -> str:
        try:
            value, _ = winreg.QueryValueEx(key, value_name)
            return str(value or "")
        except OSError:
            return ""

    # ── Cache discovery ──────────────────────────────────────────────────────
    @staticmethod
    def _is_cache_dir(name: str) -> bool:
        return is_cache_dir(name)

    def _find_cache_dirs(self, root: Path, max_depth: int = 6) -> list[Path]:
        if self._is_cache_dir(root.name):
            return [root]
        if max_depth <= 0:
            return []
        found: list[Path] = []
        try:
            for child in root.iterdir():
                if child.is_dir() and not child.is_symlink():
                    found.extend(self._find_cache_dirs(child, max_depth - 1))
        except (OSError, PermissionError):
            pass
        return found

    @staticmethod
    def _dir_size(root: Path) -> int:
        total = 0
        try:
            for path in root.rglob("*"):
                if path.is_file() and not path.is_symlink():
                    try:
                        total += path.stat().st_size
                    except (OSError, PermissionError):
                        continue
        except (OSError, PermissionError):
            pass
        return total

    @staticmethod
    def _newest_mtime(root: Path) -> float:
        newest = 0.0
        try:
            for path in root.rglob("*"):
                if path.is_file() and not path.is_symlink():
                    try:
                        newest = max(newest, path.stat().st_mtime)
                    except (OSError, PermissionError):
                        continue
        except (OSError, PermissionError):
            pass
        return newest

    @staticmethod
    def _match_program(vendor: str, by_name: dict[str, InstalledProgram]) -> str:
        lowered = vendor.lower()
        if lowered in by_name:
            return by_name[lowered].name
        for name, program in by_name.items():
            if lowered in name or name in lowered:
                return program.name
        return ""

    # ── Public API ───────────────────────────────────────────────────────────
    def scan(self) -> list[SoftwareCacheEntry]:
        entries: dict[str, SoftwareCacheEntry] = {}
        for root in self._appdata_roots:
            self._scan_root(root, entries)
        return self._finalize(entries)

    def _scan_root(self, root: Path, entries: dict[str, SoftwareCacheEntry]) -> None:
        if not root.exists():
            return
        try:
            top_levels = list(root.iterdir())
        except (OSError, PermissionError):
            return
        for top in top_levels:
            if top.is_dir() and not top.is_symlink():
                self._scan_top(top, entries)

    def _scan_top(self, top: Path, entries: dict[str, SoftwareCacheEntry]) -> None:
        for cache_dir in self._find_cache_dirs(top):
            size = self._dir_size(cache_dir)
            if size == 0:
                continue
            entry = entries.setdefault(top.name, SoftwareCacheEntry(vendor=top.name))
            entry.cache_size += size
            entry.cache_dirs.append(str(cache_dir))
            entry.last_used = max(entry.last_used, self._newest_mtime(cache_dir))

    def _finalize(
        self, entries: dict[str, SoftwareCacheEntry]
    ) -> list[SoftwareCacheEntry]:
        installed = {p.name.lower(): p for p in self.installed_programs()}
        result = [
            entry
            for entry in entries.values()
            if entry.cache_size >= self.min_cache_bytes
        ]
        for entry in result:
            entry.installed_name = self._match_program(entry.vendor, installed)
        result.sort(key=lambda e: e.cache_size, reverse=True)
        return result

    def unused(self, entries: list[SoftwareCacheEntry]) -> list[SoftwareCacheEntry]:
        cutoff = time.time() - self.max_age_days * 86400
        return [e for e in entries if e.last_used == 0 or e.last_used < cutoff]

    def remove_caches(self, entries: list[SoftwareCacheEntry]) -> tuple[int, int]:
        freed = 0
        removed = 0
        for entry in entries:
            for cache_dir in entry.cache_dirs:
                path = Path(cache_dir)
                if is_sensitive_path(path):
                    logger.warning("Skipping protected cache dir %s", path)
                    continue
                try:
                    freed += self._dir_size(path)
                    shutil.rmtree(path)
                    removed += 1
                except Exception as exc:  # pragma: no cover
                    logger.warning("Failed to remove cache %s: %s", path, exc)
        return freed, removed
