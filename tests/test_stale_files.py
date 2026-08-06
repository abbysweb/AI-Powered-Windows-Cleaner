import time

from ai_health_copilot.core.cleaner.system_cleanup import StaleLargeFilesCleaner


def test_stale_large_files_scan(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    old_big = downloads / "old_big.bin"
    old_big.write_bytes(b"x" * (2 * 1024 * 1024))
    old = time.time() - 90 * 86400
    import os

    os.utime(old_big, (old, old))

    recent_big = downloads / "recent_big.bin"
    recent_big.write_bytes(b"y" * (2 * 1024 * 1024))
    os.utime(recent_big, (time.time() - 3600, time.time() - 3600))

    old_small = downloads / "old_small.txt"
    old_small.write_text("z")
    os.utime(old_small, (old, old))

    cleaner = StaleLargeFilesCleaner(min_size_mb=1, max_age_days=30)
    result = cleaner.scan()

    assert result["file_count"] == 1
    assert result["size_bytes"] == 2 * 1024 * 1024
    assert cleaner._files == [old_big]


def test_stale_large_files_missing_downloads(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    cleaner = StaleLargeFilesCleaner(min_size_mb=1, max_age_days=30)
    result = cleaner.scan()
    assert result["file_count"] == 0
