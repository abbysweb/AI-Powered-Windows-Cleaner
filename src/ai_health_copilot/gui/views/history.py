import logging
import shutil
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ai_health_copilot.database.manager import DatabaseManager

logger = logging.getLogger(__name__)

DB_PATH = "database/storage.db"
SCHEMA_PATH = "src/ai_health_copilot/database/schema.sql"


class RestoreWorker(QThread):
    """Restores a quarantined file back to its original location."""

    finished = Signal(bool, str)  # (success, message)

    def __init__(self, backup_path: str, original_path: str, parent=None):
        super().__init__(parent)
        self.backup_path = Path(backup_path)
        self.original_path = Path(original_path)

    def run(self) -> None:
        try:
            if not self.backup_path.exists():
                self.finished.emit(False, "Backup file no longer exists in quarantine.")
                return
            self.original_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(self.backup_path), str(self.original_path))
            self.finished.emit(True, f"Restored to: {self.original_path}")
        except Exception as exc:
            self.finished.emit(False, f"Restore failed: {exc}")


class HistoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._history: list[dict[str, Any]] = []
        self._db = DatabaseManager(db_path=DB_PATH, schema_path=SCHEMA_PATH)
        self.setup_ui()

    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        # ── Header row ──────────────────────────────────────────────────────
        header_row = QHBoxLayout()
        header = QLabel("History & Rollback")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #1A1A1A;")
        header_row.addWidget(header)
        header_row.addStretch()

        self.btn_refresh = QPushButton("↻  Refresh")
        self.btn_refresh.setStyleSheet(
            "padding: 9px 20px; background-color: #2196F3; color: white; "
            "border-radius: 6px; font-size: 13px; font-weight: bold;"
        )
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.load_history)
        header_row.addWidget(self.btn_refresh)
        layout.addLayout(header_row)

        # ── Summary label ────────────────────────────────────────────────────
        self.lbl_summary = QLabel("Loading deletion history from database…")
        self.lbl_summary.setStyleSheet("color: #555555; font-size: 13px;")
        layout.addWidget(self.lbl_summary)

        # ── Table ────────────────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["#", "Action", "File / Target", "Size Recovered", "Timestamp"]
        )
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 45)
        self.table.setColumnWidth(1, 90)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 160)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(
            "QTableWidget { background-color: rgba(255,255,255,0.6); color: #333333; "
            "border: 1px solid rgba(0,0,0,0.1); border-radius: 8px; outline: 0; "
            "alternate-background-color: rgba(33,150,243,0.05); gridline-color: rgba(0,0,0,0.06); }"
            "QTableWidget::item { padding: 6px; }"
            "QTableWidget::item:selected { background-color: rgba(33,150,243,0.15); color: #1A1A1A; }"
            "QHeaderView::section { background-color: transparent; color: #555; font-weight: bold; "
            "padding: 8px; border: none; border-bottom: 1px solid rgba(0,0,0,0.1); }"
            "QScrollBar:vertical { background: transparent; width: 10px; }"
            "QScrollBar::handle:vertical { background: rgba(0,0,0,0.18); border-radius: 5px; min-height: 20px; }"
        )
        layout.addWidget(self.table)

        # ── Actions ──────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        self.lbl_selected = QLabel("Select a row to restore it.")
        self.lbl_selected.setStyleSheet("color: #777; font-size: 13px;")
        btn_row.addWidget(self.lbl_selected)
        btn_row.addStretch()

        self.btn_clear_all = QPushButton("🗑  Clear History")
        self.btn_clear_all.setStyleSheet(
            "padding: 9px 18px; background-color: #607D8B; color: white; border-radius: 6px; font-weight: bold;"
        )
        self.btn_clear_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_all.clicked.connect(self.clear_history)

        btn_row.addWidget(self.btn_clear_all)
        layout.addLayout(btn_row)

        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        # Auto-load on creation
        self.load_history()

    # ── Load ────────────────────────────────────────────────────────────────
    def load_history(self) -> None:
        """Fetch all history records from SQLite and populate the table."""
        try:
            self._history = self._db.get_history()
        except Exception as exc:
            logger.error("Failed to load history: %s", exc)
            self._history = []

        self.table.setRowCount(0)
        total_recovered = 0

        for row_idx, record in enumerate(self._history):
            size_bytes = int(record.get("size_bytes", 0))
            total_recovered += size_bytes

            self.table.insertRow(row_idx)

            id_item = QTableWidgetItem(str(record.get("id", "")))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            action = str(record.get("action_type", ""))
            action_item = QTableWidgetItem(action)
            action_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if action.upper() == "DELETE":
                action_item.setForeground(Qt.GlobalColor.red)
            elif action.upper() == "RESTORE":
                action_item.setForeground(Qt.GlobalColor.darkGreen)

            target_item = QTableWidgetItem(str(record.get("target", "")))
            target_item.setToolTip(str(record.get("target", "")))

            size_item = QTableWidgetItem(self._fmt_size(size_bytes))
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            ts_item = QTableWidgetItem(str(record.get("timestamp", "")))
            ts_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setItem(row_idx, 0, id_item)
            self.table.setItem(row_idx, 1, action_item)
            self.table.setItem(row_idx, 2, target_item)
            self.table.setItem(row_idx, 3, size_item)
            self.table.setItem(row_idx, 4, ts_item)

        count = len(self._history)
        self.lbl_summary.setText(
            f"{count} record(s) found  |  Total space recovered: {self._fmt_size(total_recovered)}"
            if count > 0 else "No history found. Delete some files first using the Scanner."
        )

    # ── Clear ────────────────────────────────────────────────────────────────
    def clear_history(self) -> None:
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Clear all deletion history records?\nThis does not delete any files.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            import sqlite3
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("DELETE FROM History")
                conn.commit()
            self.load_history()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to clear history: {exc}")

    # ── Selection ────────────────────────────────────────────────────────────
    def _on_selection_changed(self) -> None:
        rows = self.table.selectedItems()
        if rows:
            self.lbl_selected.setText("Row selected. History view is read-only.")
        else:
            self.lbl_selected.setText("Select a row to view details.")

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _fmt_size(size_bytes: int) -> str:
        if size_bytes >= 1024 ** 3:
            return f"{size_bytes / 1024**3:.1f} GB"
        if size_bytes >= 1024 ** 2:
            return f"{size_bytes / 1024**2:.1f} MB"
        if size_bytes >= 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes} B"
