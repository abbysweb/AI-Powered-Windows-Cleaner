import shutil
import time
from pathlib import Path


class QuarantineManager:
    """Manages backing up files and directories before deletion so they can be
    rolled back.

    Files are copied into quarantine and the originals deleted (space is freed
    immediately, a recoverable copy remains). Directories are moved whole into
    quarantine (fast, fully restorable; space is freed when quarantine is
    cleared).
    """

    def __init__(self, quarantine_dir: str = "cache/quarantine"):
        self.q_dir = Path(quarantine_dir)
        self.q_dir.mkdir(parents=True, exist_ok=True)

    # ── Backup ───────────────────────────────────────────────────────────────
    def _unique_path(self, name: str) -> Path:
        base = self.q_dir / f"{int(time.time() * 1000)}_{name}"
        candidate = base
        counter = 1
        while candidate.exists():
            candidate = self.q_dir / f"{int(time.time() * 1000)}_{counter}_{name}"
            counter += 1
        return candidate

    def backup_file(self, original_path: Path) -> Path | None:
        """Copies a single file to quarantine and returns the backup path."""
        if not original_path.exists() or not original_path.is_file():
            return None
        try:
            backup_path = self._unique_path(original_path.name)
            shutil.copy2(original_path, backup_path)
            return backup_path
        except Exception:  # pragma: no cover
            return None

    def backup_path(self, original_path: Path) -> Path | None:
        """Moves a directory, or copies a file, into quarantine.

        Returns the quarantine path, or None on failure.
        """
        if not original_path.exists():
            return None
        try:
            backup_path = self._unique_path(original_path.name)
            if original_path.is_dir():
                shutil.move(str(original_path), str(backup_path))
            else:
                shutil.copy2(original_path, backup_path)
            return backup_path
        except Exception:  # pragma: no cover
            return None

    # ── Restore ──────────────────────────────────────────────────────────────
    def restore_file(self, backup_path: Path, original_path: Path) -> bool:
        """Restores a quarantined file or directory to its original location."""
        return self.restore_path(backup_path, original_path)

    def restore_path(self, backup_path: Path, original_path: Path) -> bool:
        """Restores a quarantined file or directory to its original location."""
        backup = Path(backup_path)
        if not backup.exists():
            return False
        try:
            original_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(backup), str(original_path))
            return True
        except Exception:  # pragma: no cover
            return False

    # ── Inventory / maintenance ──────────────────────────────────────────────
    def list_backups(self) -> list[Path]:
        if not self.q_dir.exists():
            return []
        return [
            p
            for p in self.q_dir.iterdir()
            if p.is_file() or p.is_dir()
        ]

    def total_size(self) -> int:
        total = 0
        for backup in self.list_backups():
            if backup.is_file():
                try:
                    total += backup.stat().st_size
                except OSError:
                    continue
            else:
                try:
                    total += sum(
                        f.stat().st_size for f in backup.rglob("*") if f.is_file()
                    )
                except OSError:
                    continue
        return total

    def clear(self) -> int:
        """Permanently deletes all quarantined backups.

        Returns the number of bytes freed.
        """
        freed = 0
        for backup in self.list_backups():
            try:
                if backup.is_dir():
                    freed += sum(
                        f.stat().st_size for f in backup.rglob("*") if f.is_file()
                    )
                    shutil.rmtree(backup)
                else:
                    freed += backup.stat().st_size
                    backup.unlink(missing_ok=True)
            except OSError:  # pragma: no cover
                continue
        return freed
