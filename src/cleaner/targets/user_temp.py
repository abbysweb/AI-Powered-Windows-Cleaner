from src.utils.config import Config
import os
from src.cleaner.targets.base import CleanerTarget, CleanResult
from src.utils.paths import USER_TEMP
from src.utils.logger import logger

class UserTempCleaner(CleanerTarget):
    @property
    def name(self) -> str:
        return "User Temp"

    def clean(self) -> CleanResult:
        config = Config()
        deleted = 0
        freed = 0
        errors = []
        
        if not USER_TEMP.exists():
            return CleanResult(self.name, 0, 0, [])
            
        for path in USER_TEMP.rglob("*"):
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
