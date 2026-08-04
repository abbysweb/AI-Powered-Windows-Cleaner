from ai_health_copilot.core.scanner.system_info import (
    get_cpu_info,
    get_disk_usage,
    get_os_info,
    get_ram_usage,
    get_system_overview,
)


def test_get_disk_usage():
    drives = get_disk_usage()
    assert isinstance(drives, list)
    if len(drives) > 0:
        drive = drives[0]
        assert "device" in drive
        assert "total" in drive
        assert "used" in drive
        assert "free" in drive


def test_get_ram_usage():
    ram = get_ram_usage()
    assert isinstance(ram, dict)
    assert "total" in ram
    assert "available" in ram
    assert "percent" in ram


def test_get_cpu_info():
    cpu = get_cpu_info()
    assert isinstance(cpu, dict)
    assert "physical_cores" in cpu
    assert "total_cores" in cpu
    assert "percent" in cpu


def test_get_os_info():
    os_info = get_os_info()
    assert isinstance(os_info, dict)
    assert "system" in os_info
    assert "release" in os_info
    assert "version" in os_info


def test_get_system_overview():
    overview = get_system_overview()
    assert isinstance(overview, dict)
    assert "os" in overview
    assert "cpu" in overview
    assert "ram" in overview
    assert "disks" in overview
