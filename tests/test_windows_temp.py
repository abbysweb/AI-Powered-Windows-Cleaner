from pathlib import Path
from unittest.mock import MagicMock, patch

from core.cleaner.windows_temp import WindowsTempCleaner


@patch("core.cleaner.windows_temp.WINDOWS_TEMP")
def test_windows_temp_scan(mock_temp_dir):
    # Setup mock
    mock_temp_dir.exists.return_value = True

    mock_file1 = MagicMock(spec=Path)
    mock_file1.is_file.return_value = True
    mock_file1.stat.return_value.st_size = 1024

    mock_file2 = MagicMock(spec=Path)
    mock_file2.is_file.return_value = True
    mock_file2.stat.return_value.st_size = 2048

    mock_temp_dir.rglob.return_value = [mock_file1, mock_file2]

    cleaner = WindowsTempCleaner()
    result = cleaner.scan()

    assert result["file_count"] == 2
    assert result["size_bytes"] == 3072
    assert result["risk_score"] == 20
    assert cleaner.calculate_size() == 3072
    assert cleaner.name == "Windows Temp"


@patch("core.cleaner.windows_temp.WINDOWS_TEMP")
def test_windows_temp_delete(mock_temp_dir):
    # Setup mock
    mock_temp_dir.exists.return_value = True
    mock_file = MagicMock(spec=Path)
    mock_file.is_file.return_value = True
    mock_file.stat.return_value.st_size = 100
    mock_temp_dir.rglob.return_value = [mock_file]

    cleaner = WindowsTempCleaner()
    cleaner.scan()

    success = cleaner.delete()
    assert success is True
    mock_file.unlink.assert_called_once_with(missing_ok=True)
