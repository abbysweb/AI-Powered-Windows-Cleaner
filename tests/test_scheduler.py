import subprocess
from unittest.mock import MagicMock, patch

from core.scheduler.manager import TaskSchedulerManager


def test_schedule_daily():
    manager = TaskSchedulerManager("TestTask")

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            stdout="SUCCESS: The scheduled task has successfully been created.",
            returncode=0,
        )
        result = manager.schedule_daily("12:00")
        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "schtasks" in args
        assert "/Create" in args


def test_remove_schedule():
    manager = TaskSchedulerManager("TestTask")

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(
            stdout="SUCCESS: The scheduled task was successfully deleted.", returncode=0
        )
        result = manager.remove_schedule()
        assert result is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "/Delete" in args


def test_is_scheduled():
    manager = TaskSchedulerManager("TestTask")

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = manager.is_scheduled()
        assert result is True

    with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "cmd")):
        result = manager.is_scheduled()
        assert result is False
