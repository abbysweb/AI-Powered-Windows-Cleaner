import os
from pathlib import Path
import ctypes

# Common paths
USER_TEMP = Path(os.environ.get("TEMP", r"C:\Users\Default\AppData\Local\Temp"))
WINDOWS_TEMP = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Temp"
LOCAL_APPDATA = Path(os.environ.get("LOCALAPPDATA", r"C:\Users\Default\AppData\Local"))
THUMBNAIL_CACHE = LOCAL_APPDATA / "Microsoft" / "Windows" / "Explorer"
PROGRAM_DATA = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData"))

# Phase 3 paths
CHROME_CACHE = LOCAL_APPDATA / "Google" / "Chrome" / "User Data" / "Default" / "Cache" / "Cache_Data"
EDGE_CACHE = LOCAL_APPDATA / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache" / "Cache_Data"
BRAVE_CACHE = LOCAL_APPDATA / "BraveSoftware" / "Brave-Browser" / "User Data" / "Default" / "Cache" / "Cache_Data"
FIREFOX_PROFILES = LOCAL_APPDATA / "Mozilla" / "Firefox" / "Profiles"
WATERFOX_PROFILES = LOCAL_APPDATA / "Waterfox" / "Profiles"
DELIVERY_OPTIMIZATION = PROGRAM_DATA / "Microsoft" / "Windows" / "DeliveryOptimization"
SHADER_CACHE = LOCAL_APPDATA / "D3DSCache"

def is_admin() -> bool:
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False
