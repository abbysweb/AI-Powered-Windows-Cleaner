import ctypes
from src.cleaner.targets.base import CleanerTarget, CleanResult
from src.scanner.targets.recycle_bin import RecycleBinScanner
from src.utils.logger import logger

class RecycleBinCleaner(CleanerTarget):
    @property
    def name(self) -> str:
        return "Recycle Bin"

    def clean(self) -> CleanResult:
        # First scan to know how much we are freeing
        scanner = RecycleBinScanner()
        scan_res = scanner.scan()
        
        if scan_res.size_bytes == 0 and scan_res.file_count == 0:
            return CleanResult(self.name, 0, 0, [])
            
        try:
            # SHERB_NOCONFIRMATION = 1, SHERB_NOPROGRESSUI = 2, SHERB_NOSOUND = 4
            flags = 1 | 2 | 4
            res = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags)
            
            if res == 0:
                return CleanResult(self.name, scan_res.file_count, scan_res.size_bytes, [])
            else:
                return CleanResult(self.name, 0, 0, [f"API Error Code: {res}"], False)
        except Exception as e:
            logger.error(f"Failed to empty Recycle Bin: {e}")
            return CleanResult(self.name, 0, 0, [str(e)], False)
