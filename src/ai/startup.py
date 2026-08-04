import winreg
from typing import List, Dict

class StartupAnalyzer:
    def analyze(self) -> List[Dict]:
        results = []
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    
                    impact = "Low"
                    if "update" in name.lower() or "cloud" in name.lower():
                        impact = "Medium"
                    if "discord" in name.lower() or "spotify" in name.lower() or "steam" in name.lower():
                        impact = "High"
                        
                    results.append({
                        "name": name,
                        "command": value,
                        "impact": impact,
                        "type": "Startup Item"
                    })
                    i += 1
                except OSError:
                    break
        except Exception:
            pass
        return results
