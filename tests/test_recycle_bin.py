from unittest.mock import patch

from core.cleaner.recycle_bin import RecycleBinCleaner


def test_recycle_bin_scan():
    cleaner = RecycleBinCleaner()
    result = cleaner.scan()
    assert result["size_bytes"] == 0
    assert result["file_count"] == -1
    assert result["risk_score"] == 5
    assert cleaner.name == "Recycle Bin"


@patch("core.cleaner.recycle_bin.os.name", "nt")
@patch("core.cleaner.recycle_bin.ctypes.windll.shell32")
def test_recycle_bin_delete_windows(mock_shell32):
    mock_shell32.SHEmptyRecycleBinW.return_value = 0
    cleaner = RecycleBinCleaner()

    success = cleaner.delete()
    assert success is True
    mock_shell32.SHEmptyRecycleBinW.assert_called_once()


@patch("core.cleaner.recycle_bin.os.name", "posix")
def test_recycle_bin_delete_non_windows():
    cleaner = RecycleBinCleaner()
    success = cleaner.delete()
    assert success is False
