from unittest.mock import patch

from ai_health_copilot.main import main


@patch("ai_health_copilot.main.QApplication")
def test_main_execution(mock_qapp):
    mock_qapp.return_value.exec.return_value = 0
    assert main() == 0
    mock_qapp.assert_called_once()


def test_main_silent_runs_headless_scan():
    with patch("ai_health_copilot.main.run_silent_scan") as mock_scan:
        mock_scan.return_value = 0
        with patch("sys.argv", ["main.py", "--silent"]):
            assert main() == 0
        mock_scan.assert_called_once()
