import sys
import argparse
from PySide6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.cleaner.cleaner import CleanerOrchestrator
from src.utils.logger import logger

def silent_clean():
    logger.info("Starting silent auto-clean via Task Scheduler...")
    orchestrator = CleanerOrchestrator()
    results = orchestrator.clean_all()
    freed = sum(res.space_freed_bytes for res in results)
    deleted = sum(res.files_deleted for res in results)
    logger.info(f"Silent auto-clean finished. Deleted {deleted} files, freed {freed} bytes.")

def main():
    parser = argparse.ArgumentParser(description="AI Powered Windows Cleaner")
    parser.add_argument('--auto-clean', action='store_true', help="Run silently and clean based on current settings")
    args, unknown = parser.parse_known_args()
    
    if args.auto_clean:
        silent_clean()
        sys.exit(0)
        
    app = QApplication(sys.argv)
    
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
