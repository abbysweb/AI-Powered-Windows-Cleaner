from pathlib import Path
from unittest.mock import MagicMock, patch

from ai_health_copilot.core.cleaner.downloads import DownloadsCleaner


@patch("ai_health_copilot.core.cleaner.downloads.Path.home")
def test_downloads_scan(mock_home):
    mock_downloads = MagicMock()
    mock_home.return_value = mock_downloads
    mock_downloads.__truediv__.return_value = mock_downloads
    mock_downloads.exists.return_value = True

    mock_file1 = MagicMock(spec=Path)
    mock_file1.is_file.return_value = True
    mock_file1.stat.return_value.st_size = 100

    mock_downloads.rglob.return_value = [mock_file1]

    cleaner = DownloadsCleaner()
    result = cleaner.scan()

    assert result["file_count"] == 1
    assert result["size_bytes"] == 100
    assert result["risk_score"] == 80
    assert cleaner.name == "Downloads"


@patch("ai_health_copilot.core.cleaner.downloads.Path.home")
def test_downloads_delete(mock_home, tmp_path):
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    target = downloads / "file.txt"
    target.write_text("x")
    mock_home.return_value = tmp_path

    class _FakeDb:
        def get_ignored_folders(self):
            return []

    with patch(
        "ai_health_copilot.database.manager.DatabaseManager",
        return_value=_FakeDb(),
    ):
        cleaner = DownloadsCleaner()
        cleaner.scan()

        success = cleaner.delete()
        assert success is True
        assert not target.exists()
