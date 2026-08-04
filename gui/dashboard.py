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


class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header = QLabel("AI Windows Health Copilot")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #E0E0E0;")
        main_layout.addWidget(header)

        # Grid for stats and actions
        grid = QGridLayout()
        grid.setSpacing(15)

        # Storage Overview Card
        storage_card = self.create_card("System Storage")
        storage_layout = QVBoxLayout(storage_card)

        # Simple pie chart representation for Storage
        self.storage_plot = pg.PlotWidget()
        self.storage_plot.setBackground("transparent")
        # We will populate this with real data in Phase 7
        storage_layout.addWidget(QLabel("Analyzing disk usage..."))
        storage_layout.addWidget(self.storage_plot)
        grid.addWidget(storage_card, 0, 0, 2, 1)

        # Health Score Card
        health_card = self.create_card("System Health")
        health_layout = QVBoxLayout(health_card)
        score_label = QLabel("98 / 100")
        score_label.setStyleSheet("font-size: 36px; color: #4CAF50; font-weight: bold;")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        health_layout.addWidget(score_label)
        grid.addWidget(health_card, 0, 1)

        # Actions Card
        actions_card = self.create_card("Quick Actions")
        actions_layout = QVBoxLayout(actions_card)
        btn_scan = QPushButton("Deep Scan")
        btn_clean = QPushButton("Quick Clean")
        btn_scan.setStyleSheet(
            "padding: 10px; background-color: #2196F3; color: white; border-radius: 5px;"
        )
        btn_clean.setStyleSheet(
            "padding: 10px; background-color: #FF9800; color: white; border-radius: 5px;"
        )
        actions_layout.addWidget(btn_scan)
        actions_layout.addWidget(btn_clean)
        grid.addWidget(actions_card, 1, 1)

        main_layout.addLayout(grid)

    def create_card(self, title: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { "
            "background-color: #2C2C2C; "
            "border-radius: 10px; "
            "border: 1px solid #3D3D3D; "
            "}"
        )
        layout = QVBoxLayout(card)
        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #BDBDBD; border: none;"
        )
        layout.addWidget(title_label)
        return card
