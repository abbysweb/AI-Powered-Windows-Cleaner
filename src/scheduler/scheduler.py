import subprocess
import sys
from pathlib import Path
from src.utils.logger import logger
from src.utils.paths import is_admin

class Scheduler:
    TASK_NAME = "WindowsCleanerBotAuto"

    @classmethod
    def get_executable_path(cls) -> str:
        if getattr(sys, 'frozen', False):
            return f'"{sys.executable}" --auto-clean'
        else:
            main_py = Path.cwd() / "main.py"
            return f'"{sys.executable}" "{main_py}" --auto-clean'

    @classmethod
    def create_task(cls, frequency: str = "WEEKLY") -> bool:
        """Create a scheduled task. Frequency can be DAILY, WEEKLY, or ONSTART."""
        if not is_admin():
            logger.error("Admin rights required to create scheduled tasks.")
            return False
            
        cls.delete_task() # Clear existing
        
        cmd = cls.get_executable_path()
        
        sch_cmd = [
            "schtasks", "/create",
            "/tn", cls.TASK_NAME,
            "/tr", cmd,
            "/sc", frequency,
            "/f", "/rl", "HIGHEST"
        ]
        
        try:
            result = subprocess.run(sch_cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                logger.info(f"Task scheduled successfully: {frequency}")
                return True
            else:
                logger.error(f"Failed to schedule task: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return False

    @classmethod
    def delete_task(cls) -> bool:
        if not is_admin():
            return False
            
        sch_cmd = ["schtasks", "/delete", "/tn", cls.TASK_NAME, "/f"]
        try:
            subprocess.run(sch_cmd, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except:
            return False

    @classmethod
    def is_task_scheduled(cls) -> bool:
        sch_cmd = ["schtasks", "/query", "/tn", cls.TASK_NAME]
        try:
            result = subprocess.run(sch_cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return result.returncode == 0
        except:
            return False
