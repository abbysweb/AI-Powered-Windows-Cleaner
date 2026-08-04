import os
import subprocess
import sys
import time

import requests

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_URL = "http://localhost:8000"
HEALTH_TIMEOUT_SECONDS = 120
POLL_INTERVAL_SECONDS = 2
MAIN_SCRIPT = os.path.join(ROOT_DIR, "src", "ai_health_copilot", "main.py")


def is_backend_healthy(url: str = BACKEND_URL) -> bool:
    try:
        resp = requests.get(f"{url}/health", timeout=3)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


def start_backend() -> int:
    try:
        proc = subprocess.Popen(
            ["podman-compose", "up", "-d", "--build"], cwd=ROOT_DIR
        )
        return proc.wait()
    except FileNotFoundError:
        print(
            "[Run Bot] ERROR: 'podman-compose' was not found on PATH.",
            file=sys.stderr,
        )
        return 1


def ensure_backend(url: str = BACKEND_URL) -> bool:
    if is_backend_healthy(url):
        print(f"[Run Bot] AI backend already healthy at {url}")
        return True

    print(
        "[Run Bot] AI backend not running. "
        "Starting containers (podman-compose up -d --build)..."
    )
    rc = start_backend()
    if rc != 0:
        print(f"[Run Bot] podman-compose exited with code {rc}")

    deadline = time.monotonic() + HEALTH_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if is_backend_healthy(url):
            print(f"[Run Bot] AI backend is healthy at {url}")
            return True
        time.sleep(POLL_INTERVAL_SECONDS)

    print(
        f"[Run Bot] AI backend did not become healthy within "
        f"{HEALTH_TIMEOUT_SECONDS} seconds.",
        file=sys.stderr,
    )
    return False


def launch_app() -> int:
    return subprocess.run(
        [sys.executable, MAIN_SCRIPT], cwd=ROOT_DIR, check=False
    ).returncode


def main() -> int:
    healthy = ensure_backend()
    if not healthy:
        print(
            "[Run Bot] WARNING: AI backend unavailable. "
            "The app will still launch, but the AI Advisor may not work."
        )
    print("[Run Bot] Launching AI Windows Health Copilot...")
    return launch_app()


if __name__ == "__main__":
    sys.exit(main())
