import hashlib
import logging
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)


def _get_file_hash(
    path: Path, chunk_size: int = 8192, first_chunk_only: bool = False
) -> str:
    """Calculates MD5 hash of a file or its first chunk."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            if first_chunk_only:
                chunk = f.read(chunk_size)
                h.update(chunk)
            else:
                while chunk := f.read(chunk_size):
                    h.update(chunk)
    except (PermissionError, FileNotFoundError):
        return ""
    return h.hexdigest()


def find_duplicates(directory: str | Path) -> list[list[str]]:
    """
    Finds exact duplicate files in a directory using a 3-step heuristic:
    1. Group by file size.
    2. Group by partial hash (first 8KB).
    3. Group by full hash.
    Returns a list of duplicate groups (each group is a list of file paths).
    """
    target_dir = Path(directory)
    if not target_dir.exists() or not target_dir.is_dir():
        logger.warning(f"Invalid directory provided to find_duplicates: {directory}")
        return []

    # Step 1: Group by size
    size_map: dict[int, list[Path]] = defaultdict(list)
    try:
        for path in target_dir.rglob("*"):
            if path.is_file():
                try:
                    size = path.stat().st_size
                    # Ignore 0-byte files
                    if size > 0:
                        size_map[size].append(path)
                except (PermissionError, FileNotFoundError):
                    pass
    except PermissionError:  # pragma: no cover
        pass

    # Filter out unique sizes
    potential_dupes = [paths for paths in size_map.values() if len(paths) > 1]

    duplicates: list[list[str]] = []

    # Step 2 & 3: Hashing
    for group in potential_dupes:
        # Partial hash
        partial_map: dict[str, list[Path]] = defaultdict(list)
        for p in group:
            h = _get_file_hash(p, first_chunk_only=True)
            if h:
                partial_map[h].append(p)

        # Full hash for partial collisions
        for partial_group in partial_map.values():
            if len(partial_group) > 1:
                full_map: dict[str, list[str]] = defaultdict(list)
                for p in partial_group:
                    full_h = _get_file_hash(p, first_chunk_only=False)
                    if full_h:
                        full_map[full_h].append(str(p))

                for exact_group in full_map.values():
                    if len(exact_group) > 1:
                        duplicates.append(exact_group)

    return duplicates
