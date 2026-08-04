from unittest.mock import patch

from ai_health_copilot.main import main


@patch("ai_health_copilot.main.QApplication.exec")
def test_main_execution(mock_exec):
    mock_exec.return_value = 0
    with patch("sys.exit") as mock_exit, patch(
        "ai_health_copilot.main.QApplication"
    ):
        main()
        mock_exit.assert_called_once()
