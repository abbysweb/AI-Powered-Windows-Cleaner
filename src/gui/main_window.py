from PySide6.QtWidgets import QMainWindow, QTabWidget
from src.gui.views.scan_view import ScanView
from src.gui.views.settings_view import SettingsView
from src.gui.views.ai_view import AiOptimizerView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Powered Windows Cleaner")
        self.resize(900, 650)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.scan_view = ScanView()
        self.ai_view = AiOptimizerView()
        self.settings_view = SettingsView()
        
        self.tabs.addTab(self.scan_view, "Scan & Clean")
        self.tabs.addTab(self.ai_view, "AI Optimizer")
        self.tabs.addTab(self.settings_view, "Settings")
