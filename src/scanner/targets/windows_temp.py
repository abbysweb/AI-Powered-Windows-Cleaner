from src.utils.config import Config
from pathlib import Path
from src.scanner.targets.base import ScannerTarget, ScanResult
from src.utils.paths import WINDOWS_TEMP, is_admin
from src.utils.logger import logger

class WindowsTempScanner(ScannerTarget):
    @property
    def name(self) -> str:
        return "Windows Temp"

    def scan(self) -> ScanResult:
        config = Config()
        size = 0
        count = 0
        
        if not is_admin():
            return ScanResult(
                name=self.name, 
                size_bytes=0, 
                file_count=0, 
                error="Requires Administrator privileges"
            )

        if not WINDOWS_TEMP.exists():
            return ScanResult(name=self.name, size_bytes=0, file_count=0)
            
        for path in WINDOWS_TEMP.rglob("*"):
            try:
                if path.is_file():
                    if not config.is_file_eligible(path):
                        continue
                    size += path.stat().st_size
                    count += 1
            except Exception as e:
                logger.debug(f"Error accessing {path}: {e}")
                
        return ScanResult(name=self.name, size_bytes=size, file_count=count)
