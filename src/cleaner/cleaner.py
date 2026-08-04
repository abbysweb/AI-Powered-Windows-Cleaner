from typing import List
from src.cleaner.targets.base import CleanResult, CleanerTarget
from src.cleaner.targets.user_temp import UserTempCleaner
from src.cleaner.targets.windows_temp import WindowsTempCleaner
from src.cleaner.targets.recycle_bin import RecycleBinCleaner
from src.cleaner.targets.thumbnail_cache import ThumbnailCacheCleaner
from src.cleaner.targets.browser_cache import BrowserCacheCleaner
from src.cleaner.targets.delivery_optimization import DeliveryOptimizationCleaner
from src.cleaner.targets.shader_cache import ShaderCacheCleaner
from src.utils.logger import logger
from src.utils.config import Config, Profile

class CleanerOrchestrator:
    def __init__(self):
        self.config = Config()
        all_targets = [
            UserTempCleaner(),
            RecycleBinCleaner(),
            ThumbnailCacheCleaner(),
            BrowserCacheCleaner()
        ]
        
        if self.config.profile in (Profile.STANDARD, Profile.DEEP):
            all_targets.extend([
                WindowsTempCleaner(),
                DeliveryOptimizationCleaner()
            ])
            
        if self.config.profile == Profile.DEEP:
            all_targets.extend([
                ShaderCacheCleaner()
            ])
            
        self.targets = all_targets

    def clean_all(self, callback=None) -> List[CleanResult]:
        """
        Runs all cleaners. 
        callback: function(target_name: str, result: CleanResult)
        """
        results = []
        for target in self.targets:
            logger.info(f"Starting clean for {target.name}")
            result = target.clean()
            results.append(result)
            logger.info(f"Finished clean for {target.name}: Freed {result.space_freed_bytes} bytes")
            if callback:
                callback(target.name, result)
        return results
