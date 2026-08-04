from src.utils.config import Config
import os
from pathlib import Path
from typing import List
from src.cleaner.targets.base import CleanerTarget, CleanResult
from src.utils.paths import CHROME_CACHE, EDGE_CACHE, BRAVE_CACHE, FIREFOX_PROFILES, WATERFOX_PROFILES
from src.utils.process import is_process_running
from src.utils.logger import logger

class BrowserCacheCleaner(CleanerTarget):
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

    def clean(self) -> CleanResult:
        config = Config()
        running_browsers = [
            "chrome.exe", "msedge.exe", "brave.exe", "firefox.exe", "waterfox.exe"
        ]
        if any(is_process_running(proc) for proc in running_browsers):
            return CleanResult(self.name, 0, 0, ["Browser is running. Close all browsers first."], False)
            
        deleted = 0
        freed = 0
        errors = []
        
        targets = [CHROME_CACHE, EDGE_CACHE, BRAVE_CACHE] + self._get_firefox_based_cache_paths()
        
        for cache_dir in targets:
            if not cache_dir.exists():
                continue
                
            for path in cache_dir.rglob("*"):
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
