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

from ai_health_copilot.core.rollback.manager import QuarantineManager
from ai_health_copilot.database import DB_PATH, QUARANTINE_DIR, SCHEMA_PATH
from ai_health_copilot.database.manager import DatabaseManager

logger = logging.getLogger(__name__)


class RestoreWorker(QThread):
    """Restores a quarantined file/directory back to its original location."""

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
        self._db = DatabaseManager(db_path=str(DB_PATH), schema_path=str(SCHEMA_PATH))
        self._quarantine = QuarantineManager(quarantine_dir=str(QUARANTINE_DIR))
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["#", "Action", "File / Target", "Size Recovered", "Backup", "Timestamp"]
        )
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 45)
        self.table.setColumnWidth(1, 90)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 70)
        self.table.setColumnWidth(5, 160)
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

        self.btn_restore = QPushButton("↩  Restore Selected")
        self.btn_restore.setStyleSheet(
            "padding: 9px 18px; background-color: #4CAF50; color: white; border-radius: 6px; font-weight: bold;"
        )
        self.btn_restore.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restore.setEnabled(False)
        self.btn_restore.clicked.connect(self.restore_selected)

        self.btn_empty_quarantine = QPushButton("🧹  Empty Quarantine")
        self.btn_empty_quarantine.setStyleSheet(
            "padding: 9px 18px; background-color: #FF9800; color: white; border-radius: 6px; font-weight: bold;"
        )
        self.btn_empty_quarantine.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_empty_quarantine.clicked.connect(self.empty_quarantine)

        self.btn_clear_all = QPushButton("🗑  Clear History")
        self.btn_clear_all.setStyleSheet(
            "padding: 9px 18px; background-color: #607D8B; color: white; border-radius: 6px; font-weight: bold;"
        )
        self.btn_clear_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_all.clicked.connect(self.clear_history)

        btn_row.addWidget(self.btn_restore)
        btn_row.addWidget(self.btn_empty_quarantine)
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
        restoreable = 0

        for row_idx, record in enumerate(self._history):
            size_bytes = int(record.get("size_bytes", 0))
            total_recovered += size_bytes

            self.table.insertRow(row_idx)

            id_item = QTableWidgetItem(str(record.get("id", "")))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            id_item.setData(Qt.ItemDataRole.UserRole, record)

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

            backup = record.get("backup_path") or ""
            backup_item = QTableWidgetItem("✓" if backup else "—")
            backup_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            backup_item.setToolTip(str(backup))
            if backup:
                restoreable += 1

            ts_item = QTableWidgetItem(str(record.get("timestamp", "")))
            ts_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setItem(row_idx, 0, id_item)
            self.table.setItem(row_idx, 1, action_item)
            self.table.setItem(row_idx, 2, target_item)
            self.table.setItem(row_idx, 3, size_item)
            self.table.setItem(row_idx, 4, backup_item)
            self.table.setItem(row_idx, 5, ts_item)

        count = len(self._history)
        quarantined = self._quarantine.total_size()
        if count > 0:
            self.lbl_summary.setText(
                f"{count} record(s)  |  {restoreable} restore-able  |  "
                f"Space recovered: {self._fmt_size(total_recovered)}  |  "
                f"Quarantine holds: {self._fmt_size(quarantined)}"
            )
        else:
            self.lbl_summary.setText(
                "No history found. Delete some files first using the Scanner."
            )
        self._update_restore_button()

    # ── Restore ─────────────────────────────────────────────────────────────
    def restore_selected(self) -> None:
        record = self._selected_record()
        if record is None:
            return
        backup_path = record.get("backup_path") or ""
        target = str(record.get("target", ""))
        if not backup_path or not Path(backup_path).exists():
            QMessageBox.warning(
                self,
                "Cannot Restore",
                "This record has no backup in quarantine. It was deleted before "
                "rollback support was added, or the backup was already purged.",
            )
            return
        if not target:
            return

        self.btn_restore.setEnabled(False)
        self._restore_worker = RestoreWorker(backup_path, target)
        self._restore_worker.finished.connect(self._on_restore_finished)
        self._restore_worker.start()

    def _on_restore_finished(self, success: bool, message: str) -> None:
        record = self._selected_record()
        if success:
            if record is not None:
                self._db.delete_history(int(record["id"]))
            self.load_history()
            QMessageBox.information(self, "Restore", f"✅ {message}")
        else:
            self.btn_restore.setEnabled(True)
            QMessageBox.warning(self, "Restore Failed", message)

    # ── Quarantine ──────────────────────────────────────────────────────────
    def empty_quarantine(self) -> None:
        size = self._quarantine.total_size()
        reply = QMessageBox.question(
            self,
            "Empty Quarantine",
            f"Permanently delete all {self._fmt_size(size)} of quarantined backups?\n"
            "This frees disk space but removes the ability to restore those files.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        freed = self._quarantine.clear()
        self.load_history()
        QMessageBox.information(
            self, "Quarantine", f"🧹 Freed {self._fmt_size(freed)} of quarantine."
        )

    # ── Clear history ───────────────────────────────────────────────────────
    def clear_history(self) -> None:
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Clear all deletion history records?\n"
            "This does not delete any files or quarantine backups.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            import sqlite3

            with sqlite3.connect(str(DB_PATH)) as conn:
                conn.execute("DELETE FROM History")
                conn.commit()
            self.load_history()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to clear history: {exc}")

    # ── Selection ────────────────────────────────────────────────────────────
    def _selected_record(self) -> dict[str, Any] | None:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        item = self.table.item(rows[0].row(), 0)
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def _on_selection_changed(self) -> None:
        self._update_restore_button()

    def _update_restore_button(self) -> None:
        record = self._selected_record()
        if record is None:
            self.btn_restore.setEnabled(False)
            self.lbl_selected.setText("Select a row to restore it.")
            return
        backup = record.get("backup_path") or ""
        if backup and Path(backup).exists():
            self.btn_restore.setEnabled(True)
            self.lbl_selected.setText(
                f"Selected: {record.get('target', '')}  —  ready to restore."
            )
        else:
            self.btn_restore.setEnabled(False)
            self.lbl_selected.setText(
                "Selected record has no backup available to restore."
            )

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
