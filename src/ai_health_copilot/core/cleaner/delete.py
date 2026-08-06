import logging
import shutil
from pathlib import Path

from ai_health_copilot.core.rollback.manager import QuarantineManager

from .safety import is_sensitive_path

logger = logging.getLogger(__name__)

# Outcome strings returned by the delete helpers
DELETED = "deleted"
SKIPPED = "skipped"
FAILED = "failed"


def permanent_delete(path: str | Path) -> str:
    """Permanently removes a file or directory with no backup.

    Protected (sensitive) paths and missing paths are skipped. Returns one of
    ``DELETED``, ``SKIPPED`` or ``FAILED``.
    """
    target = Path(path)
    if is_sensitive_path(target):
        logger.warning("Skipping protected path: %s", target)
        return SKIPPED
    if not target.exists():
        logger.warning("Path no longer exists: %s", target)
        return SKIPPED
    try:
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink(missing_ok=True)
        return DELETED
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to delete %s: %s", target, exc)
        return FAILED


def safe_delete(
    path: str | Path, quarantine_manager: QuarantineManager
) -> tuple[str, str | None]:
    """Removes a file or directory while keeping a recoverable copy.

    Returns ``(outcome, backup_path)`` where ``outcome`` is one of
    ``DELETED``, ``SKIPPED`` or ``FAILED``. Nothing is ever deleted without a
    successful quarantine backup, and protected (sensitive) paths are skipped.
    """
    target = Path(path)
    if is_sensitive_path(target):
        logger.warning("Skipping protected path: %s", target)
        return SKIPPED, None
    if not target.exists():
        logger.warning("Path no longer exists: %s", target)
        return SKIPPED, None

    try:
        backup_path = quarantine_manager.backup_path(target)
        if backup_path is None:
            logger.error("Quarantine backup failed for %s", target)
            return FAILED, None
        if not target.is_dir():
            target.unlink(missing_ok=True)
        return DELETED, str(backup_path)
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to delete %s: %s", target, exc)
        return FAILED, None
