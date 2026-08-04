import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class OverviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Header
        header = QLabel("Dashboard Overview")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #1A1A1A;")
        main_layout.addWidget(header)

        grid = QGridLayout()
        grid.setSpacing(20)

        # Storage Pie Chart
        storage_card = self.create_card("System Storage")
        storage_layout = storage_card.layout()
        assert storage_layout is not None

        self.storage_plot = pg.PlotWidget()
        self.storage_plot.setBackground("transparent")
        self.storage_plot.setMouseEnabled(x=False, y=False)
        self.storage_plot.hideAxis("left")
        self.storage_plot.hideAxis("bottom")

        # Add a dummy bar graph representing space for now (PyQtGraph pie charts are complex to set up quickly, bar chart is cleaner)
        x = [1, 2]
        y = [438, 74]  # Used vs Free
        bg1 = pg.BarGraphItem(x=x, height=y, width=0.6, brushes=["#E53935", "#4CAF50"])
        self.storage_plot.addItem(bg1)

        storage_layout.addWidget(self.storage_plot)
        grid.addWidget(storage_card, 0, 0, 2, 1)

        # Health Score Card
        health_card = self.create_card("System Health")
        health_layout = health_card.layout()
        assert health_layout is not None
        score_label = QLabel("98 / 100")
        score_label.setStyleSheet("font-size: 48px; color: #4CAF50; font-weight: bold;")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        health_layout.addWidget(score_label)
        grid.addWidget(health_card, 0, 1)

        # Quick Actions Card
        actions_card = self.create_card("Quick Actions")
        actions_layout = actions_card.layout()
        assert actions_layout is not None
        self.btn_scan = QPushButton("Start Deep Scan")
        self.btn_clean = QPushButton("Quick Clean")
        self.btn_scan.setStyleSheet(
            "padding: 12px; font-size: 14px; background-color: #2196F3; color: white; border-radius: 6px; font-weight: bold;"
        )
        self.btn_clean.setStyleSheet(
            "padding: 12px; font-size: 14px; background-color: #FF9800; color: white; border-radius: 6px; font-weight: bold;"
        )
        self.btn_scan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clean.setCursor(Qt.CursorShape.PointingHandCursor)
        actions_layout.addWidget(self.btn_scan)
        actions_layout.addWidget(self.btn_clean)
        grid.addWidget(actions_card, 1, 1)

        main_layout.addLayout(grid)

    def create_card(self, title: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { "
            "background-color: rgba(255, 255, 255, 0.7); "
            "border-radius: 12px; "
            "border: 1px solid rgba(0, 0, 0, 0.1); "
            "}"
        )
        
        # Add a subtle drop shadow for depth
        from PySide6.QtGui import QColor
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #555555; border: none; margin-bottom: 10px; background: transparent;"
        )
        layout.addWidget(title_label)
        return card
