from src.utils.config import Config
from pathlib import Path
from typing import List
from src.scanner.targets.base import ScannerTarget, ScanResult
from src.utils.paths import CHROME_CACHE, EDGE_CACHE, BRAVE_CACHE, FIREFOX_PROFILES, WATERFOX_PROFILES
from src.utils.process import is_process_running
from src.utils.logger import logger

class BrowserCacheScanner(ScannerTarget):
    @property
    def name(self) -> str:
        return "Browser Caches (Chrome, Edge, Brave, Firefox, Waterfox)"

    def _get_firefox_based_cache_paths(self) -> List[Path]:
        paths = []
        for profiles_dir in [FIREFOX_PROFILES, WATERFOX_PROFILES]:
            if profiles_dir.exists():
                for profile in profiles_dir.iterdir():
                    if profile.is_dir():
                        cache_dir = profile / "cache2"
                        if cache_dir.exists():
                            paths.append(cache_dir)
        return paths

    def scan(self) -> ScanResult:
        config = Config()
        size = 0
        count = 0
        
        running_browsers = [
            "chrome.exe", "msedge.exe", "brave.exe", "firefox.exe", "waterfox.exe"
        ]
        if any(is_process_running(proc) for proc in running_browsers):
            return ScanResult(
                name=self.name, 
                size_bytes=0, 
                file_count=0, 
                error="Browser is running. Close all browsers first."
            )
            
        targets = [CHROME_CACHE, EDGE_CACHE, BRAVE_CACHE] + self._get_firefox_based_cache_paths()
        
        for cache_dir in targets:
            if not cache_dir.exists():
                continue
                
            for path in cache_dir.rglob("*"):
                try:
                    if path.is_file():
                        if not config.is_file_eligible(path):
                            continue
                        size += path.stat().st_size
                        count += 1
                except Exception as e:
                    logger.debug(f"Error accessing {path}: {e}")
                    
        return ScanResult(name=self.name, size_bytes=size, file_count=count)
