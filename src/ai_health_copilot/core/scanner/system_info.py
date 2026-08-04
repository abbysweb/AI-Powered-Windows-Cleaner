import os
import platform
from typing import Any

import psutil


def get_disk_usage() -> list[dict[str, Any]]:
    """Returns disk usage information for all physical drives."""
    drives = []
    for part in psutil.disk_partitions(all=False):
        if os.name == "nt" and ("cdrom" in part.opts or part.fstype == ""):
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            drives.append(
                {
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                }
            )
        except PermissionError:
            continue
    return drives


def get_ram_usage() -> dict[str, Any]:
    """Returns system RAM usage."""
    vm = psutil.virtual_memory()
    return {
        "total": vm.total,
        "available": vm.available,
        "percent": vm.percent,
        "used": vm.used,
        "free": vm.free,
    }


def get_cpu_info() -> dict[str, Any]:
    """Returns CPU usage and information."""
    return {
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": psutil.cpu_count(logical=True),
        "percent": psutil.cpu_percent(interval=1),
        "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
    }


def get_os_info() -> dict[str, Any]:
    """Returns basic OS information."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }


def get_system_overview() -> dict[str, Any]:
    """Combines all system metrics into a single overview."""
    return {
        "os": get_os_info(),
        "cpu": get_cpu_info(),
        "ram": get_ram_usage(),
        "disks": get_disk_usage(),
    }
