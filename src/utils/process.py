import psutil

def is_process_running(process_name: str) -> bool:
    """Check if there is any running process that contains the given name."""
    process_name = process_name.lower()
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and process_name in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False
