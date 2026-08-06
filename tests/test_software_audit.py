from pathlib import Path

from ai_health_copilot.core.audit.software import (
    SoftwareAudit,
    SoftwareCacheEntry,
    is_cache_dir,
)


def _write(root: Path, relpath: str, data: bytes = b"x") -> Path:
    p = root / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return p


def test_is_cache_dir():
    assert is_cache_dir("Cache")
    assert is_cache_dir("Code Cache")
    assert is_cache_dir("DXCache")
    assert is_cache_dir("GPUCache")
    assert is_cache_dir("shader-cache")
    assert not is_cache_dir("User Data")
    assert not is_cache_dir("Application Data")


def test_scan_groups_by_vendor_and_filters_min(tmp_path, monkeypatch):
    local = tmp_path / "Local"
    _write(local / "Google" / "Chrome" / "User Data" / "Default" / "Cache", "f_1", b"a" * 200)
    _write(local / "Google" / "Chrome" / "User Data" / "Default" / "GPUCache", "g_1", b"b" * 100)
    _write(local / "NVIDIA" / "DXCache", "shader.bin", b"c" * 50)
    _write(local / "TinyApp" / "Cache", "tiny.dat", b"d" * 10)

    audit = SoftwareAudit(min_cache_mb=0, max_age_days=60)
    audit._appdata_roots = [local]
    entries = audit.scan()

    by_vendor = {e.vendor: e for e in entries}
    assert "Google" in by_vendor
    assert by_vendor["Google"].cache_size == 300
    assert "NVIDIA" in by_vendor
    assert "TinyApp" in by_vendor

    audit2 = SoftwareAudit(min_cache_mb=100, max_age_days=60)
    audit2._appdata_roots = [local]
    filtered = audit2.scan()
    vendors = {e.vendor for e in filtered}
    assert "TinyApp" not in vendors


def test_unused_filter(monkeypatch, tmp_path):
    import time

    local = tmp_path / "Local"
    new_cache = local / "NewApp" / "Cache"
    _write(new_cache, "recent.dat", b"z")
    old_cache = local / "OldApp" / "Cache"
    old_file = _write(old_cache, "old.dat", b"q")
    old_ts = time.time() - 200 * 86400
    import os

    os.utime(old_file, (old_ts, old_ts))

    audit = SoftwareAudit(min_cache_mb=0, max_age_days=30)
    audit._appdata_roots = [local]
    entries = audit.scan()

    unused = audit.unused(entries)
    names = {e.vendor for e in unused}
    assert "OldApp" in names
    assert "NewApp" not in names


def test_installed_name_matching():
    from ai_health_copilot.core.audit.software import InstalledProgram

    by_name = {
        "google chrome": InstalledProgram(name="Google Chrome"),
        "nvidia graphics driver": InstalledProgram(name="NVIDIA Graphics Driver"),
    }
    audit = SoftwareAudit()
    assert audit._match_program("Google", by_name) == "Google Chrome"
    assert audit._match_program("NVIDIA", by_name) == "NVIDIA Graphics Driver"
    assert audit._match_program("Unknown", by_name) == ""


def test_remove_caches_deletes_and_skips_sensitive(monkeypatch, tmp_path):
    local = tmp_path / "Local"
    cache_dir = _write(local / "App" / "Cache", "f.dat", b"y" * 100)
    cache_dir = cache_dir.parent

    audit = SoftwareAudit(min_cache_mb=0, max_age_days=30)
    audit._appdata_roots = [local]
    entries = audit.scan()

    freed, removed = audit.remove_caches(entries)
    assert removed == 1
    assert freed == 100
    assert not cache_dir.exists()


def test_remove_caches_skips_protected_dir(monkeypatch, tmp_path):
    sensitive_dir = tmp_path / "App" / "passwords"
    sensitive_dir.mkdir(parents=True)
    (sensitive_dir / "file").write_bytes(b"q" * 50)
    entry = SoftwareCacheEntry(
        vendor="App",
        cache_size=50,
        last_used=0.0,
        cache_dirs=[str(sensitive_dir)],
    )
    audit = SoftwareAudit()
    freed, removed = audit.remove_caches([entry])
    assert removed == 0
    assert freed == 0
    assert sensitive_dir.exists()


def test_scan_with_missing_roots(tmp_path, monkeypatch):
    missing = tmp_path / "does-not-exist"
    audit = SoftwareAudit(min_cache_mb=0, max_age_days=30)
    audit._appdata_roots = [missing]
    assert audit.scan() == []
