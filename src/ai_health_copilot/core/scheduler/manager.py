import logging
import os
import subprocess  # nosec B404
import sys

logger = logging.getLogger(__name__)


class TaskSchedulerManager:
    """Manages Windows Task Scheduler integration for automated maintenance."""

    def __init__(self, task_name: str = "AIPoweredWindowsCleaner"):
        self.task_name = task_name
        # Use pythonw to run without console, but for simplicity here we just use the current executable
        self.executable_path = sys.executable
        # Assume our app.py is in the current working directory or a compiled binary
        self.script_path = os.path.abspath("app.py")

    def schedule_daily(self, time_str: str = "12:00") -> bool:
        """Schedules the cleaner to run daily at the specified time (HH:MM)."""
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
