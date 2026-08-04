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


def main():
    logger.info("Starting AI Windows Health Copilot...")
    app = QApplication(sys.argv)

    # Global stylesheet for light mode glassmorphism
    app.setStyleSheet("""
        QMainWindow, QStackedWidget { background-color: transparent; }
        QWidget { color: #1A1A1A; font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif; }
    """)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
