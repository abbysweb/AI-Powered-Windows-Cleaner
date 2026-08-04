from typing import List
from src.scanner.targets.base import ScanResult, ScannerTarget
from src.scanner.targets.user_temp import UserTempScanner
from src.scanner.targets.windows_temp import WindowsTempScanner
from src.scanner.targets.recycle_bin import RecycleBinScanner
from src.scanner.targets.thumbnail_cache import ThumbnailCacheScanner
from src.scanner.targets.browser_cache import BrowserCacheScanner
from src.scanner.targets.delivery_optimization import DeliveryOptimizationScanner
from src.scanner.targets.shader_cache import ShaderCacheScanner
from src.utils.config import Config, Profile

class ScannerOrchestrator:
    def __init__(self):
        self.config = Config()
        all_targets = [
            UserTempScanner(),
            RecycleBinScanner(),
            ThumbnailCacheScanner(),
            BrowserCacheScanner()
        ]
        
        if self.config.profile in (Profile.STANDARD, Profile.DEEP):
            all_targets.extend([
                WindowsTempScanner(),
                DeliveryOptimizationScanner()
            ])
            
        if self.config.profile == Profile.DEEP:
            all_targets.extend([
                ShaderCacheScanner()
            ])
            
        self.targets = all_targets

    def scan_all(self) -> List[ScanResult]:
        results = []
        for target in self.targets:
            result = target.scan()
            results.append(result)
        return results
