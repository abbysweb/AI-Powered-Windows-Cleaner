from src.utils.config import Config
import os
from src.cleaner.targets.base import CleanerTarget, CleanResult
from src.utils.paths import THUMBNAIL_CACHE
from src.utils.logger import logger

class ThumbnailCacheCleaner(CleanerTarget):
    @property
    def name(self) -> str:
        return "Thumbnail Cache"

    def clean(self) -> CleanResult:
        config = Config()
        deleted = 0
        freed = 0
        errors = []
        
        if not THUMBNAIL_CACHE.exists():
            return CleanResult(self.name, 0, 0, [])
            
        for path in THUMBNAIL_CACHE.glob("thumbcache_*.db"):
            if path.is_file():
                if not config.is_file_eligible(path):
                    continue
                try:
                    size = path.stat().st_size
                    os.remove(path)
                    deleted += 1
                    freed += size
                except Exception as e:
                    errors.append(f"Failed to delete {path.name}: {e}")
                    logger.debug(f"Delete failed: {path}: {e}")
                    
        return CleanResult(self.name, deleted, freed, errors)
