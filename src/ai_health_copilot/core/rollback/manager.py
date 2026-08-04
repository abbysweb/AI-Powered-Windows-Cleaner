import shutil
import time
from pathlib import Path


class QuarantineManager:
    """Manages backing up files before deletion so they can be rolled back."""

    def __init__(self, quarantine_dir: str = "cache/quarantine"):
        self.q_dir = Path(quarantine_dir)
        self.q_dir.mkdir(parents=True, exist_ok=True)

    def backup_file(self, original_path: Path) -> Path | None:
        """Copies a file to the quarantine directory and returns the backup path."""
        if not original_path.exists() or not original_path.is_file():
            return None

        try:
            timestamp = int(time.time())
            # Create a unique name to avoid collisions
            safe_name = f"{timestamp}_{original_path.name}"
            backup_path = self.q_dir / safe_name
            shutil.copy2(original_path, backup_path)
            return backup_path
        except Exception:  # pragma: no cover
            return None

    def restore_file(self, backup_path: Path, original_path: Path) -> bool:
        """Restores a quarantined file back to its original location."""
        if not backup_path.exists():
            return False

        try:
            original_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(backup_path), str(original_path))
            return True
        except Exception:  # pragma: no cover
            return False
