from core.scanner.large_files import scan_large_files


def test_scan_large_files(tmp_path):
    # Create a small file
    small = tmp_path / "small.txt"
    small.write_bytes(b"A" * 1024)  # 1 KB

    # Create a 'large' file (mocking size isn't trivial without patch, so let's just make one of 2 MB for this test and pass min_size_mb = 1)
    large = tmp_path / "large.txt"
    large.write_bytes(b"A" * (2 * 1024 * 1024))  # 2 MB

    results = scan_large_files(tmp_path, min_size_mb=1)

    assert len(results) == 1
    assert results[0]["name"] == "large.txt"
    assert results[0]["size_bytes"] == 2 * 1024 * 1024


def test_scan_invalid_directory():
    results = scan_large_files("does_not_exist_xyz123")
    assert results == []
