import argparse
import logging
import sys
from pathlib import Path

# Ensure the 'src' directory is in sys.path so we can import 'ai_health_copilot'
src_dir = str(Path(__file__).parent.parent.resolve())
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from PySide6.QtWidgets import QApplication

from ai_health_copilot.gui.main_window import MainWindow

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("AIHealthCopilot")


def run_silent_scan() -> int:
    """Headless deep scan (no GUI). Logs a summary and exits.

    Never deletes anything: this is used by the scheduled task and only
    reports how much space could be recovered.
    """
    from ai_health_copilot.core.cleaner.browser_cache import (
        ChromeCacheCleaner,
        EdgeCacheCleaner,
        FirefoxCacheCleaner,
    )
    from ai_health_copilot.core.cleaner.downloads import DownloadsCleaner
    from ai_health_copilot.core.cleaner.system_cache import (
        DeliveryOptimizationCleaner,
        ErrorReportCleaner,
        FontCacheCleaner,
        LogFilesCleaner,
        PrefetchCleaner,
        ThumbnailCacheCleaner,
        WindowsUpdateCacheCleaner,
        WinSxSTempCleaner,
    )
    from ai_health_copilot.core.cleaner.system_cleanup import (
        CrashDumpCleaner,
        EmptyFoldersCleaner,
        ShaderCacheCleaner,
        StaleLargeFilesCleaner,
        WindowsOldCleaner,
    )
    from ai_health_copilot.core.cleaner.windows_temp import WindowsTempCleaner

    cleaners = [
        WindowsTempCleaner(),
        DownloadsCleaner(),
        ChromeCacheCleaner(),
        EdgeCacheCleaner(),
        FirefoxCacheCleaner(),
        ThumbnailCacheCleaner(),
        WindowsUpdateCacheCleaner(),
        DeliveryOptimizationCleaner(),
        ErrorReportCleaner(),
        PrefetchCleaner(),
        LogFilesCleaner(),
        WinSxSTempCleaner(),
        FontCacheCleaner(),
        ShaderCacheCleaner(),
        CrashDumpCleaner(),
        EmptyFoldersCleaner(),
        StaleLargeFilesCleaner(),
        WindowsOldCleaner(),
    ]

    total_files = 0
    total_size = 0
    for cleaner in cleaners:
        try:
            result = cleaner.scan()
            total_files += result.get("file_count", 0)
            total_size += result.get("size_bytes", 0)
        except Exception as exc:  # pragma: no cover
            logger.warning("Scan error in %s: %s", cleaner.name, exc)

    logger.info(
        "Silent scan complete: %d item(s), %.1f MB potentially recoverable.",
        total_files,
        total_size / (1024 * 1024),
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="ai_health_copilot")
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Run a headless scan (no GUI) and exit. Deletes nothing.",
    )
    args, _unknown = parser.parse_known_args()

    if args.silent:
        return run_silent_scan()

    logger.info("Starting AI Windows Health Copilot...")
    app = QApplication(sys.argv)

    # Global stylesheet for light mode glassmorphism
    app.setStyleSheet("""
        QMainWindow, QStackedWidget { background-color: transparent; }
        QWidget { color: #1A1A1A; font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif; }
    """)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
