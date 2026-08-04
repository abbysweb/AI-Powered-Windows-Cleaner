from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ScannerResultsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header = QLabel("Deep Scan Results")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(header)

        # Tree Widget for files
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(
            ["File Name", "Location", "Category", "Size", "Risk Score"]
        )
        self.tree.setStyleSheet(
            "QTreeWidget { background-color: rgba(40, 40, 40, 0.5); color: #E0E0E0; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; outline: 0; }"
            "QTreeWidget::item:hover { background-color: rgba(255, 255, 255, 0.05); }"
            "QTreeWidget::item:selected { background-color: rgba(33, 150, 243, 0.3); border-radius: 4px; }"
            "QHeaderView::section { background-color: transparent; color: #BDBDBD; padding: 5px; border: none; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }"
            "QScrollBar:vertical { background: transparent; width: 10px; }"
            "QScrollBar::handle:vertical { background: rgba(255, 255, 255, 0.2); border-radius: 5px; min-height: 20px; }"
        )

        # Add dummy data
        item1 = QTreeWidgetItem(
            ["temp_cache.bin", "C:\\Windows\\Temp", "Windows Temp", "15 MB", "Low"]
        )
        item2 = QTreeWidgetItem(
            [
                "old_installer.exe",
                "C:\\Users\\PC\\Downloads",
                "Downloads",
                "120 MB",
                "Medium",
            ]
        )
        item1.setCheckState(0, Qt.CheckState.Checked)
        item2.setCheckState(0, Qt.CheckState.Checked)

        self.tree.addTopLevelItem(item1)
        self.tree.addTopLevelItem(item2)
        layout.addWidget(self.tree)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_clean = QPushButton("Clean Selected")
        btn_clean.setStyleSheet(
            "padding: 10px 20px; background-color: #F44336; color: white; border-radius: 6px; font-weight: bold;"
        )
        btn_quarantine = QPushButton("Quarantine Selected")
        btn_quarantine.setStyleSheet(
            "padding: 10px 20px; background-color: #FF9800; color: white; border-radius: 6px; font-weight: bold;"
        )

        btn_layout.addStretch()
        btn_layout.addWidget(btn_quarantine)
        btn_layout.addWidget(btn_clean)
        layout.addLayout(btn_layout)
