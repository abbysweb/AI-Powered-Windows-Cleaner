import subprocess
from unittest.mock import MagicMock, patch

from ai_health_copilot.core.scheduler.manager import (
    TaskSchedulerManager,
    _validate_time,
)


def test_validate_time():
    assert _validate_time("12:00")
    assert _validate_time("0:05")
    assert _validate_time("23:59")
    assert not _validate_time("24:00")
    assert not _validate_time("12:60")
    assert not _validate_time("noon")
    assert not _validate_time("")


def test_schedule_daily_rejects_bad_time():
    manager = TaskSchedulerManager("TestTask")
    with patch("subprocess.run") as mock_run:
        assert manager.schedule_daily("25:99") is False
        mock_run.assert_not_called()


def test_schedule_daily_uses_main_script():
    manager = TaskSchedulerManager("TestTask")
    assert manager.script_path.endswith("main.py")


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
        assert any("--silent" in str(a) for a in args)


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
