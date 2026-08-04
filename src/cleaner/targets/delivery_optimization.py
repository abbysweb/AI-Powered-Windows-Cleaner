from src.utils.config import Config
import os
from src.cleaner.targets.base import CleanerTarget, CleanResult
from src.utils.paths import DELIVERY_OPTIMIZATION, is_admin
from src.utils.logger import logger

class DeliveryOptimizationCleaner(CleanerTarget):
    @property
    def name(self) -> str:
        return "Delivery Optimization Cache"

    def clean(self) -> CleanResult:
        config = Config()
        if not is_admin():
            return CleanResult(self.name, 0, 0, ["Requires Administrator privileges"], False)
            
        deleted = 0
        freed = 0
        errors = []
        
        if not DELIVERY_OPTIMIZATION.exists():
            return CleanResult(self.name, 0, 0, [])
            
        for path in DELIVERY_OPTIMIZATION.rglob("*"):
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
