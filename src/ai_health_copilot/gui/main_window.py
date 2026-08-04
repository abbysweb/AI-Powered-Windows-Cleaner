import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ai_health_copilot.gui.views.ai_chat import AIChatWidget
from ai_health_copilot.gui.views.history import HistoryWidget
from ai_health_copilot.gui.views.overview import OverviewWidget
from ai_health_copilot.gui.views.scanner_results import ScannerResultsWidget

try:
    from win32mica import ApplyMica, MicaStyle, MicaTheme
    MICA_AVAILABLE = True
except ImportError:
    MICA_AVAILABLE = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Windows Health Copilot")
        self.resize(1200, 800)
        
        # Enable translucent background for Mica
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        if MICA_AVAILABLE and sys.platform == "win32":
            try:
                # Apply Mica backdrop to the window handle
                hwnd = int(self.winId())
                ApplyMica(hwnd, MicaTheme.LIGHT, MicaStyle.DEFAULT)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to apply Mica: {e}")

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar Navigation
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet(
            "QFrame { background-color: rgba(255, 255, 255, 0.6); border-right: 1px solid rgba(0, 0, 0, 0.1); border-top-right-radius: 12px; border-bottom-right-radius: 12px; }"
            "QPushButton { "
            "   text-align: left; padding: 12px 20px; font-size: 15px; margin: 4px 10px; border-radius: 6px; "
            "   background-color: transparent; color: #333333; border: none; "
            "}"
            "QPushButton:hover { background-color: rgba(0, 0, 0, 0.05); color: #000000; }"
            "QPushButton:checked { background-color: rgba(33, 150, 243, 0.1); color: #2196F3; font-weight: bold; border-left: 4px solid #2196F3; }"
        )
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(5)

        # App Title in Sidebar
        title_label = QLabel("Health Copilot")
        title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #1A1A1A; padding-left: 20px; padding-bottom: 20px; border: none;"
        )
        sidebar_layout.addWidget(title_label)

        # Navigation Buttons
        self.btn_overview = self.create_nav_button("Dashboard")
        self.btn_scanner = self.create_nav_button("Scan Results")
        self.btn_ai_chat = self.create_nav_button("AI Advisor")
        self.btn_history = self.create_nav_button("History / Rollback")
        self.btn_settings = self.create_nav_button("Settings")

        sidebar_layout.addWidget(self.btn_overview)
        sidebar_layout.addWidget(self.btn_scanner)
        sidebar_layout.addWidget(self.btn_ai_chat)
        sidebar_layout.addWidget(self.btn_history)

        spacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        sidebar_layout.addItem(spacer)
        sidebar_layout.addWidget(self.btn_settings)

        main_layout.addWidget(self.sidebar)

        # 2. Stacked Widget (Views)
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Initialize Views
        self.view_overview = OverviewWidget()
        self.view_scanner = ScannerResultsWidget()
        self.view_ai_chat = AIChatWidget()
        self.view_history = HistoryWidget()
        self.view_settings = QWidget()  # Placeholder for settings

        self.stacked_widget.addWidget(self.view_overview)
        self.stacked_widget.addWidget(self.view_scanner)
        self.stacked_widget.addWidget(self.view_ai_chat)
        self.stacked_widget.addWidget(self.view_history)
        self.stacked_widget.addWidget(self.view_settings)

        # Connections
        self.btn_overview.clicked.connect(lambda: self.switch_view(0))
        self.btn_scanner.clicked.connect(lambda: self.switch_view(1))
        self.btn_ai_chat.clicked.connect(lambda: self.switch_view(2))
        self.btn_history.clicked.connect(lambda: self.switch_view(3))
        self.btn_settings.clicked.connect(lambda: self.switch_view(4))
        
        # Dashboard Action Connections
        self.view_overview.btn_scan.clicked.connect(self.btn_scanner.click)
        self.view_overview.btn_clean.clicked.connect(self.btn_scanner.click)

        # Refresh history when user navigates to it
        self.btn_history.clicked.connect(self.view_history.load_history)

        # Initial state
        self.btn_overview.setChecked(True)
        self.switch_view(0)

    def create_nav_button(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def switch_view(self, index: int):
        self.stacked_widget.setCurrentIndex(index)
