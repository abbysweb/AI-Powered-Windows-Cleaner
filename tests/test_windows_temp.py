from pathlib import Path
from unittest.mock import MagicMock, patch

from ai_health_copilot.core.cleaner.windows_temp import WindowsTempCleaner


@patch("ai_health_copilot.core.cleaner.windows_temp.WINDOWS_TEMP")
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


def test_windows_temp_delete(tmp_path, monkeypatch):
    from ai_health_copilot.core.cleaner import windows_temp as wt

    target_dir = tmp_path / "WindowsTemp"
    target_dir.mkdir()
    monkeypatch.setattr(wt, "WINDOWS_TEMP", target_dir)
    target = target_dir / "junk.tmp"
    target.write_text("data")

    cleaner = WindowsTempCleaner()
    cleaner.scan()

    success = cleaner.delete()
    assert success is True
    assert not target.exists()
