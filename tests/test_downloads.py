from pathlib import Path
from unittest.mock import MagicMock, patch

from core.cleaner.downloads import DownloadsCleaner
from core.rollback.manager import QuarantineManager


@patch("core.cleaner.downloads.Path.home")
def test_downloads_scan(mock_home):
    mock_downloads = MagicMock()
    mock_home.return_value = mock_downloads
    mock_downloads.__truediv__.return_value = mock_downloads
    mock_downloads.exists.return_value = True

    mock_file1 = MagicMock(spec=Path)
    mock_file1.is_file.return_value = True
    mock_file1.stat.return_value.st_size = 100

    mock_downloads.rglob.return_value = [mock_file1]

    cleaner = DownloadsCleaner(quarantine_manager=MagicMock(spec=QuarantineManager))
    result = cleaner.scan()

    assert result["file_count"] == 1
    assert result["size_bytes"] == 100
    assert result["risk_score"] == 80
    assert cleaner.name == "Downloads"


@patch("core.cleaner.downloads.Path.home")
def test_downloads_delete(mock_home):
    mock_downloads = MagicMock()
    mock_home.return_value = mock_downloads
    mock_downloads.__truediv__.return_value = mock_downloads
    mock_downloads.exists.return_value = True

    mock_file = MagicMock(spec=Path)
    mock_file.is_file.return_value = True
    mock_file.stat.return_value.st_size = 100
    mock_downloads.rglob.return_value = [mock_file]

    mock_qm = MagicMock(spec=QuarantineManager)

    cleaner = DownloadsCleaner(quarantine_manager=mock_qm)
    cleaner.scan()

    success = cleaner.delete()
    assert success is True
    mock_qm.backup_file.assert_called_once_with(mock_file)
    mock_file.unlink.assert_called_once_with(missing_ok=True)
