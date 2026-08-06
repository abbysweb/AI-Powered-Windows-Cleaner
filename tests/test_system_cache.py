from ai_health_copilot.core.cleaner import system_cache as sc


def _make(root, relpath, data=b"data"):
    p = root / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)


def test_thumbnail_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "_LOCAL_APPDATA", tmp_path / "Local")
    explorer = tmp_path / "Local" / "Microsoft" / "Windows" / "Explorer"
    _make(explorer, "thumbcache_32.db", b"a" * 10)
    _make(explorer, "thumbcache_256.db", b"b" * 20)
    _make(explorer, "iconcache_16.db", b"c" * 5)

    cleaner = sc.ThumbnailCacheCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 2
    assert result["size_bytes"] == 30


def test_windows_update_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "_WINDIR", tmp_path / "Windows")
    target = tmp_path / "Windows" / "SoftwareDistribution" / "Download"
    _make(target, "w1.cab", b"x" * 64)

    cleaner = sc.WindowsUpdateCacheCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 1
    assert result["size_bytes"] == 64


def test_delivery_optimization_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "_WINDIR", tmp_path / "Windows")
    cleaner = sc.DeliveryOptimizationCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 0


def test_error_report(tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "_PROGRAMDATA", tmp_path / "ProgramData")
    wer = tmp_path / "ProgramData" / "Microsoft" / "Windows" / "WER" / "ReportQueue"
    _make(wer, "report1.txt", b"r" * 40)

    cleaner = sc.ErrorReportCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 1
    assert result["size_bytes"] == 40


def test_prefetch(tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "_WINDIR", tmp_path / "Windows")
    _make(tmp_path / "Windows" / "Prefetch", "APP.EXE-1A2B3C.pf", b"p" * 88)

    cleaner = sc.PrefetchCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 1
    assert result["size_bytes"] == 88


def test_log_files(tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "_WINDIR", tmp_path / "Windows")
    _make(tmp_path / "Windows" / "Logs" / "CBS", "CBS.log", b"l" * 100)

    cleaner = sc.LogFilesCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 1
    assert result["size_bytes"] == 100


def test_winsxs_temp(tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "_WINDIR", tmp_path / "Windows")
    _make(tmp_path / "Windows" / "WinSxS" / "Temp", "pending_1", b"s" * 12)

    cleaner = sc.WinSxSTempCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 1
    assert result["size_bytes"] == 12


def test_font_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "_WINDIR", tmp_path / "Windows")
    target = (
        tmp_path / "Windows" / "ServiceProfiles" / "LocalService" / "AppData" / "Local"
    )
    _make(target, "FontCache.dat", b"f" * 33)

    cleaner = sc.FontCacheCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 1
    assert result["size_bytes"] == 33
