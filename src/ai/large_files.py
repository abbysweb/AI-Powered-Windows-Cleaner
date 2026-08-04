from pathlib import Path
import os
from typing import List, Dict

class LargeFileAnalyzer:
    def __init__(self, target_dirs: List[Path], min_size_mb: int = 500):
        self.target_dirs = target_dirs
        self.min_size_bytes = min_size_mb * 1024 * 1024

    def analyze(self) -> List[Dict]:
        results = []
        for d in self.target_dirs:
            if not d.exists():
                continue
            for path in d.rglob("*"):
                try:
                    if path.is_file():
                        size = path.stat().st_size
                        if size >= self.min_size_bytes:
                            results.append({
                                "path": str(path),
                                "size": size,
                                "type": "Large File"
                            })
                except Exception:
                    pass
        return sorted(results, key=lambda x: x["size"], reverse=True)
