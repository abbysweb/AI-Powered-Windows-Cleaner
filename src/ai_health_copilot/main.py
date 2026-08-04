import logging
import sys

from PySide6.QtWidgets import QApplication

from ai_health_copilot.gui.main_window import MainWindow

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("AIHealthCopilot")


def main():
    logger.info("Starting AI Windows Health Copilot...")
    app = QApplication(sys.argv)

    # Global stylesheet for dark mode
    app.setStyleSheet("""
        QWidget { background-color: #1E1E1E; color: #FFFFFF; font-family: 'Segoe UI', sans-serif; }
    """)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
