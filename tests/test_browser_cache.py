from ai_health_copilot.core.cleaner import browser_cache as bc


def test_chrome_scan_finds_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(bc, "_LOCAL_APPDATA", tmp_path / "Local")
    cache = (
        tmp_path / "Local" / "Google" / "Chrome" / "User Data" / "Default" / "Cache"
    )
    cache.mkdir(parents=True)
    (cache / "a.dat").write_bytes(b"x" * 100)

    cleaner = bc.ChromeCacheCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 1
    assert result["size_bytes"] == 100
    assert result["risk_score"] == 15
    assert cleaner.name == "Chrome Cache"


def test_chrome_scan_missing_profile(tmp_path, monkeypatch):
    monkeypatch.setattr(bc, "_LOCAL_APPDATA", tmp_path / "Local")
    cleaner = bc.ChromeCacheCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 0
    assert result["size_bytes"] == 0


def test_edge_scan_finds_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(bc, "_LOCAL_APPDATA", tmp_path / "Local")
    cache = (
        tmp_path / "Local" / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache"
    )
    cache.mkdir(parents=True)
    (cache / "f_1").write_bytes(b"y" * 50)

    cleaner = bc.EdgeCacheCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 1
    assert result["size_bytes"] == 50
    assert cleaner.name == "Edge Cache"


def test_firefox_scan_finds_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(bc, "_APPDATA", tmp_path / "Roaming")
    cache2 = tmp_path / "Roaming" / "Mozilla" / "Firefox" / "Profiles" / "abc" / "cache2"
    cache2.mkdir(parents=True)
    (cache2 / "c_1").write_bytes(b"z" * 75)

    cleaner = bc.FirefoxCacheCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 1
    assert result["size_bytes"] == 75
    assert cleaner.name == "Firefox Cache"


def test_firefox_scan_missing_profiles(tmp_path, monkeypatch):
    monkeypatch.setattr(bc, "_APPDATA", tmp_path / "Roaming")
    cleaner = bc.FirefoxCacheCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 0
