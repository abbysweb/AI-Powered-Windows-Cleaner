import logging
import os
import re
import subprocess  # nosec B404
import sys

from ai_health_copilot.database import PROJECT_ROOT

logger = logging.getLogger(__name__)

_TIME_PATTERN = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")


def _validate_time(time_str: str) -> bool:
    return bool(_TIME_PATTERN.match(time_str))


class TaskSchedulerManager:
    """Manages Windows Task Scheduler integration for automated maintenance."""

    def __init__(self, task_name: str = "AIPoweredWindowsCleaner"):
        self.task_name = task_name
        self.executable_path = self._gui_executable()
        self.script_path = str(PROJECT_ROOT / "src" / "ai_health_copilot" / "main.py")

    @staticmethod
    def _gui_executable() -> str:
        """Returns pythonw.exe when available so scheduled runs do not flash a console."""
        if os.name != "nt":
            return sys.executable
        exe = sys.executable
        if os.path.basename(exe).lower() == "python.exe":
            candidate = exe[:-len("python.exe")] + "pythonw.exe"
            if os.path.exists(candidate):
                return candidate
        return exe

    def schedule_daily(self, time_str: str = "12:00") -> bool:
        """Schedules the cleaner to run daily at the specified time (HH:MM)."""
        if not _validate_time(time_str):
            logger.error(f"Invalid time format: {time_str!r}. Expected HH:MM.")
            return False

        cmd = [
            "schtasks",
            "/Create",
            "/TN",
            self.task_name,
            "/TR",
            f'"{self.executable_path}" "{self.script_path}" --silent',
            "/SC",
            "DAILY",
            "/ST",
            time_str,
            "/F",  # Force overwrite if exists
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)  # nosec B603
            logger.info(f"Successfully scheduled daily task: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to schedule task: {e.stderr}")
            return False

    def remove_schedule(self) -> bool:
        """Removes the scheduled task."""
        cmd = ["schtasks", "/Delete", "/TN", self.task_name, "/F"]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)  # nosec B603
            logger.info(f"Successfully removed scheduled task {self.task_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to remove scheduled task: {e.stderr}")
            return False

    def is_scheduled(self) -> bool:
        """Checks if the task is currently scheduled."""
        cmd = ["schtasks", "/Query", "/TN", self.task_name]
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)  # nosec B603
            return True
        except subprocess.CalledProcessError:
            return False
