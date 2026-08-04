from src.utils.config import Config
from pathlib import Path
from src.scanner.targets.base import ScannerTarget, ScanResult
from src.utils.paths import THUMBNAIL_CACHE
from src.utils.logger import logger

class ThumbnailCacheScanner(ScannerTarget):
    @property
    def name(self) -> str:
        return "Thumbnail Cache"

    def scan(self) -> ScanResult:
        config = Config()
        size = 0
        count = 0
        
        if not THUMBNAIL_CACHE.exists():
            return ScanResult(name=self.name, size_bytes=0, file_count=0)
            
        for path in THUMBNAIL_CACHE.glob("thumbcache_*.db"):
            try:
                if path.is_file():
                    if not config.is_file_eligible(path):
                        continue
                    size += path.stat().st_size
                    count += 1
            except Exception as e:
                logger.debug(f"Error accessing {path}: {e}")
                
        return ScanResult(name=self.name, size_bytes=size, file_count=count)
