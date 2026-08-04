from pathlib import Path
import hashlib
from typing import List, Dict

class DuplicateFinder:
    def __init__(self, target_dirs: List[Path]):
        self.target_dirs = target_dirs

    def _hash_file(self, filepath: Path) -> str:
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()

    def analyze(self) -> List[Dict]:
        hashes = {}
        duplicates = []
        for d in self.target_dirs:
            if not d.exists():
                continue
            for path in d.rglob("*"):
                try:
                    if path.is_file():
                        # Only hash files over 10MB to save time
                        size = path.stat().st_size
                        if size > 10 * 1024 * 1024:
                            file_hash = self._hash_file(path)
                            if file_hash in hashes:
                                duplicates.append({
                                    "path": str(path),
                                    "original": hashes[file_hash],
                                    "size": size,
                                    "type": "Duplicate"
                                })
                            else:
                                hashes[file_hash] = str(path)
                except Exception:
                    pass
        return duplicates
