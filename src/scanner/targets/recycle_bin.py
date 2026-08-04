import ctypes
from ctypes import wintypes
from src.scanner.targets.base import ScannerTarget, ScanResult
from src.utils.logger import logger

class SHQUERYRBINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("i64Size", ctypes.c_int64),
        ("i64NumItems", ctypes.c_int64),
    ]

class RecycleBinScanner(ScannerTarget):
    @property
    def name(self) -> str:
        return "Recycle Bin"

    def scan(self) -> ScanResult:
        try:
            shell32 = ctypes.windll.shell32
            info = SHQUERYRBINFO()
            info.cbSize = ctypes.sizeof(SHQUERYRBINFO)
            
            # 0 = S_OK
            res = shell32.SHQueryRecycleBinW(None, ctypes.byref(info))
            if res == 0:
                return ScanResult(
                    name=self.name, 
                    size_bytes=info.i64Size, 
                    file_count=info.i64NumItems
                )
            else:
                return ScanResult(
                    name=self.name, 
                    size_bytes=0, 
                    file_count=0, 
                    error=f"API Error Code: {res}"
                )
        except Exception as e:
            logger.error(f"Failed to scan Recycle Bin: {e}")
            return ScanResult(name=self.name, size_bytes=0, file_count=0, error=str(e))
