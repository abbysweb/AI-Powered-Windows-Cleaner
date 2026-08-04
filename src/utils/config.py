from enum import Enum
from typing import List
import json
from pathlib import Path
import time

class Profile(Enum):
    QUICK = "Quick"
    STANDARD = "Standard"
    DEEP = "Deep"

class Config:
    def __init__(self):
        self.profile: Profile = Profile.QUICK
        self.max_age_days: int = 0  # 0 means disabled
        self.exclusions: List[str] = []
        self.config_path = Path.cwd() / "settings.json"
        self.load()

    def save(self):
        data = {
            "profile": self.profile.value,
            "max_age_days": self.max_age_days,
            "exclusions": self.exclusions
        }
        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=4)

    def load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    self.profile = Profile(data.get("profile", Profile.QUICK.value))
                    self.max_age_days = data.get("max_age_days", 0)
                    self.exclusions = data.get("exclusions", [])
            except Exception:
                pass

    def is_file_eligible(self, path: Path) -> bool:
        """Check if file matches age filters and exclusions."""
        path_str = str(path).lower()
        for ext in self.exclusions:
            if ext.lower() in path_str:
                return False
                
        if self.max_age_days > 0:
            try:
                # Check modification time
                mtime = path.stat().st_mtime
                age_days = (time.time() - mtime) / (24 * 3600)
                if age_days < self.max_age_days:
                    return False
            except Exception:
                pass
                
        return True
