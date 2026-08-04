import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def scan_large_files(
    directory: str | Path, min_size_mb: int = 100
) -> list[dict[str, Any]]:
    """
    Scans the given directory recursively for files larger than `min_size_mb`.
    Returns a list of dictionaries with file information.
    """
    large_files: list[dict[str, Any]] = []
    min_size_bytes = min_size_mb * 1024 * 1024

    target_dir = Path(directory)
    if not target_dir.exists() or not target_dir.is_dir():
        logger.warning(f"Invalid directory provided to scan_large_files: {directory}")
        return large_files

    try:
        for path in target_dir.rglob("*"):
            if path.is_file():
                try:
                    size = path.stat().st_size
                    if size >= min_size_bytes:
                        large_files.append(
                            {
                                "path": str(path),
                                "size_bytes": size,
                                "name": path.name,
                                "extension": path.suffix,
                            }
                        )
                except (PermissionError, FileNotFoundError):
                    pass  # Ignore files we can't access
    except PermissionError:  # pragma: no cover
        logger.warning(f"Permission denied accessing {directory}")

    # Sort by size descending
    large_files.sort(key=lambda x: float(str(x["size_bytes"])), reverse=True)
    return large_files
