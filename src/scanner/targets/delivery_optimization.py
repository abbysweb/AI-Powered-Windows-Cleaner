from src.utils.config import Config
from pathlib import Path
from src.scanner.targets.base import ScannerTarget, ScanResult
from src.utils.paths import DELIVERY_OPTIMIZATION, is_admin
from src.utils.logger import logger

class DeliveryOptimizationScanner(ScannerTarget):
    @property
    def name(self) -> str:
        return "Delivery Optimization Cache"

    def scan(self) -> ScanResult:
        config = Config()
        if not is_admin():
            return ScanResult(
                name=self.name, 
                size_bytes=0, 
                file_count=0, 
                error="Requires Administrator privileges"
            )
            
        size = 0
        count = 0
        
        if not DELIVERY_OPTIMIZATION.exists():
            return ScanResult(name=self.name, size_bytes=0, file_count=0)
            
        for path in DELIVERY_OPTIMIZATION.rglob("*"):
            try:
                if path.is_file():
                    if not config.is_file_eligible(path):
                        continue
                    size += path.stat().st_size
                    count += 1
            except Exception as e:
                logger.debug(f"Error accessing DO cache {path}: {e}")
                
        return ScanResult(name=self.name, size_bytes=size, file_count=count)
