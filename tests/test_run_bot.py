from unittest.mock import MagicMock, patch

import requests

import run_bot


def test_is_backend_healthy_true():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    with patch("run_bot.requests.get", return_value=mock_resp):
        assert run_bot.is_backend_healthy() is True


def test_is_backend_healthy_wrong_status():
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    with patch("run_bot.requests.get", return_value=mock_resp):
        assert run_bot.is_backend_healthy() is False


def test_is_backend_healthy_connection_error():
    with patch(
        "run_bot.requests.get",
        side_effect=requests.exceptions.ConnectionError("refused"),
    ):
        assert run_bot.is_backend_healthy() is False


@patch("run_bot.is_backend_healthy", return_value=True)
@patch("run_bot.start_backend")
def test_ensure_backend_skips_start_when_healthy(mock_start, mock_healthy):
    assert run_bot.ensure_backend() is True
    mock_start.assert_not_called()


@patch(
    "run_bot.is_backend_healthy",
    side_effect=[False, False, True],
)
@patch("run_bot.start_backend", return_value=0)
@patch("run_bot.time.sleep")
def test_ensure_backend_starts_and_waits(mock_sleep, mock_start, mock_healthy):
    assert run_bot.ensure_backend() is True
    mock_start.assert_called_once()
    assert mock_sleep.call_count >= 1


@patch("run_bot.is_backend_healthy", return_value=False)
@patch("run_bot.start_backend", return_value=0)
@patch("run_bot.time.sleep")
def test_ensure_backend_timeout(mock_sleep, mock_start, mock_healthy):
    original_timeout = run_bot.HEALTH_TIMEOUT_SECONDS
    run_bot.HEALTH_TIMEOUT_SECONDS = 0.05
    try:
        assert run_bot.ensure_backend() is False
    finally:
        run_bot.HEALTH_TIMEOUT_SECONDS = original_timeout


@patch(
    "run_bot.subprocess.Popen",
    side_effect=FileNotFoundError("podman-compose not found"),
)
def test_start_backend_missing_podman(mock_popen):
    assert run_bot.start_backend() == 1


@patch("run_bot.ensure_backend", return_value=True)
@patch("run_bot.launch_app", return_value=0)
def test_main_launches_app(mock_launch, mock_ensure):
    assert run_bot.main() == 0
    mock_launch.assert_called_once()


@patch("run_bot.ensure_backend", return_value=False)
@patch("run_bot.launch_app", return_value=0)
def test_main_launches_app_even_if_backend_down(mock_launch, mock_ensure):
    assert run_bot.main() == 0
    mock_launch.assert_called_once()
