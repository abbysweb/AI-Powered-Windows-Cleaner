from ai_health_copilot.core.cleaner import system_cleanup as scn


def _make(root, relpath, data=b"data"):
    p = root / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)


def test_shader_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(scn, "_LOCAL_APPDATA", tmp_path / "Local")
    _make(tmp_path / "Local" / "D3DSCache", "x.dat", b"d" * 22)
    _make(tmp_path / "Local" / "NVIDIA" / "DXCache", "y.dat", b"n" * 11)

    cleaner = scn.ShaderCacheCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 2
    assert result["size_bytes"] == 33


def test_crash_dumps(tmp_path, monkeypatch):
    monkeypatch.setattr(scn, "_WINDIR", tmp_path / "Windows")
    _make(tmp_path / "Windows" / "Minidump", "mini.dmp", b"m" * 9)
    _make(tmp_path / "Windows", "MEMORY.DMP", b"m" * 500)

    cleaner = scn.CrashDumpCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 2
    assert result["size_bytes"] == 509


def test_empty_folders(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("TEMP", str(tmp_path / "Temp"))
    monkeypatch.setenv("WINDIR", str(tmp_path / "Windows"))
    empty = tmp_path / "Downloads" / "sub"
    empty.mkdir(parents=True)
    (tmp_path / "Downloads" / "keep.txt").write_text("x")

    cleaner = scn.EmptyFoldersCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 1
    assert result["size_bytes"] == 0


def test_windows_old(tmp_path, monkeypatch):
    monkeypatch.setenv("SystemDrive", str(tmp_path))
    winold = tmp_path / "Windows.old"
    _make(winold / "Windows" / "System32", "sys.dat", b"w" * 250)
    _make(winold / "Users", "user.dat", b"u" * 50)

    cleaner = scn.WindowsOldCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 1
    assert result["size_bytes"] == 300
    assert cleaner._files == [winold]


def test_windows_old_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("SystemDrive", str(tmp_path))
    cleaner = scn.WindowsOldCleaner()
    result = cleaner.scan()
    assert result["file_count"] == 0
    assert result["size_bytes"] == 0


def test_windows_old_delete_permanent(tmp_path, monkeypatch):
    monkeypatch.setenv("SystemDrive", str(tmp_path))
    winold = tmp_path / "Windows.old"
    _make(winold / "Windows" / "System32", "sys.dat", b"w" * 250)

    cleaner = scn.WindowsOldCleaner()
    cleaner.scan()

    assert cleaner.delete() is True
    assert not winold.exists()


def test_empty_folder_delete_permanent(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("TEMP", str(tmp_path / "Temp"))
    monkeypatch.setenv("WINDIR", str(tmp_path / "Windows"))
    empty = tmp_path / "Downloads" / "empty_sub"
    empty.mkdir(parents=True)

    cleaner = scn.EmptyFoldersCleaner()
    cleaner.scan()

    assert cleaner.delete() is True
    assert not empty.exists()


def test_cleaners_expose_delete():
    for cleaner in [
        scn.ShaderCacheCleaner(),
        scn.CrashDumpCleaner(),
        scn.EmptyFoldersCleaner(),
        scn.WindowsOldCleaner(),
    ]:
        assert hasattr(cleaner, "delete")
        assert callable(cleaner.explain)
