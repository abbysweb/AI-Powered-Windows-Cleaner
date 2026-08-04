import sys
import logging
from PySide6.QtWidgets import QApplication
from gui.dashboard import DashboardWidget

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AIHealthCopilot")

def main():
    logger.info("Starting AI Windows Health Copilot...")
    app = QApplication(sys.argv)
    
    # Global stylesheet for dark mode
    app.setStyleSheet("""
        QWidget { background-color: #1E1E1E; color: #FFFFFF; font-family: 'Segoe UI', sans-serif; }
    """)
    
    window = DashboardWidget()
    window.resize(1024, 768)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
