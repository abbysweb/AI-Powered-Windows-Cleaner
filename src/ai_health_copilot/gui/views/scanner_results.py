import os
import logging
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ai_health_copilot.core.cleaner.downloads import DownloadsCleaner
from ai_health_copilot.core.cleaner.windows_temp import WindowsTempCleaner

logger = logging.getLogger(__name__)

USER_TEMP = Path(os.environ.get("TEMP", Path.home() / "AppData" / "Local" / "Temp"))


# ──────────────────────────────────────────────────────────────────────────────
# Background scan worker
# ──────────────────────────────────────────────────────────────────────────────
class ScanWorker(QThread):
    """Runs all cleaners in a background thread and reports results."""

    progress = Signal(int, str)           # (percent, status text)
    scan_complete = Signal(list)          # list[dict]
    error_occurred = Signal(str)

    def run(self) -> None:  # noqa: PLR0912
        results: list[dict[str, Any]] = []
        cleaners = [
            WindowsTempCleaner(),
            DownloadsCleaner(),
        ]
        total = len(cleaners)

        for idx, cleaner in enumerate(cleaners):
            self.progress.emit(
                int((idx / total) * 80),
                f"Scanning: {cleaner.name}…",
            )
            try:
                cleaner.scan()
                for file_path in cleaner._files:  # noqa: SLF001
                    try:
                        size_bytes = file_path.stat().st_size
                    except OSError:
                        size_bytes = 0
                    results.append(
                        {
                            "name": file_path.name,
                            "path": str(file_path.parent),
                            "full_path": str(file_path),
                            "category": cleaner.name,
                            "size_bytes": size_bytes,
                            "risk_score": cleaner._risk_score,  # noqa: SLF001
                            "_cleaner": cleaner,
                        }
                    )
            except Exception as exc:  # pragma: no cover
                logger.warning("Scan error in %s: %s", cleaner.name, exc)

        # Also scan User Temp folder
        self.progress.emit(85, "Scanning: User Temp…")
        if USER_TEMP.exists():
            for file_path in USER_TEMP.rglob("*"):
                if file_path.is_file():
                    try:
                        size_bytes = file_path.stat().st_size
                    except OSError:
                        size_bytes = 0
                    results.append(
                        {
                            "name": file_path.name,
                            "path": str(file_path.parent),
                            "full_path": str(file_path),
                            "category": "User Temp",
                            "size_bytes": size_bytes,
                            "risk_score": 15,
                            "_cleaner": None,
                        }
                    )

        # Sort by size desc
        results.sort(key=lambda r: r["size_bytes"], reverse=True)
        self.progress.emit(100, f"Scan complete — {len(results)} files found.")
        self.scan_complete.emit(results)


# ──────────────────────────────────────────────────────────────────────────────
# Delete worker
# ──────────────────────────────────────────────────────────────────────────────
class DeleteWorker(QThread):
    """Safely deletes selected files in a background thread."""

    progress = Signal(int, str)
    finished = Signal(int, int)    # (deleted_count, failed_count)

    def __init__(self, paths: list[str], parent=None):
        super().__init__(parent)
        self.paths = paths

    def run(self) -> None:
        deleted = 0
        failed = 0
        total = len(self.paths)
        for idx, file_path_str in enumerate(self.paths):
            self.progress.emit(
                int((idx / total) * 100),
                f"Deleting {Path(file_path_str).name}…",
            )
            try:
                Path(file_path_str).unlink(missing_ok=True)
                deleted += 1
            except Exception as exc:
                logger.warning("Failed to delete %s: %s", file_path_str, exc)
                failed += 1
        self.finished.emit(deleted, failed)


# ──────────────────────────────────────────────────────────────────────────────
# Main widget
# ──────────────────────────────────────────────────────────────────────────────
class ScannerResultsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scan_results: list[dict[str, Any]] = []
        self.setup_ui()

    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        # ── Header row ──────────────────────────────────────────────────────
        header_row = QHBoxLayout()
        header = QLabel("Deep Scan Results")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #1A1A1A;")
        header_row.addWidget(header)
        header_row.addStretch()

        self.btn_scan = QPushButton("▶  Start Scan")
        self.btn_scan.setStyleSheet(
            "padding: 10px 22px; background-color: #2196F3; color: white; "
            "border-radius: 6px; font-size: 14px; font-weight: bold;"
        )
        self.btn_scan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_scan.clicked.connect(self.start_scan)
        header_row.addWidget(self.btn_scan)
        layout.addLayout(header_row)

        # ── Summary label ────────────────────────────────────────────────────
        self.lbl_summary = QLabel("Click 'Start Scan' to find junk files on your PC.")
        self.lbl_summary.setStyleSheet("color: #555555; font-size: 13px;")
        layout.addWidget(self.lbl_summary)

        # ── Progress bar ─────────────────────────────────────────────────────
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet(
            "QProgressBar { background: rgba(0,0,0,0.06); border-radius: 6px; height: 12px; }"
            "QProgressBar::chunk { background-color: #2196F3; border-radius: 6px; }"
        )
        layout.addWidget(self.progress_bar)

        # ── Tree Widget ───────────────────────────────────────────────────────
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(
            ["✓", "File Name", "Location", "Category", "Size", "Risk"]
        )
        self.tree.setColumnWidth(0, 30)
        self.tree.setColumnWidth(1, 220)
        self.tree.setColumnWidth(2, 280)
        self.tree.setColumnWidth(3, 120)
        self.tree.setColumnWidth(4, 90)
        self.tree.setColumnWidth(5, 70)
        self.tree.setSortingEnabled(True)
        self.tree.setStyleSheet(
            "QTreeWidget { background-color: rgba(255,255,255,0.6); color: #333333; "
            "border: 1px solid rgba(0,0,0,0.1); border-radius: 8px; outline: 0; }"
            "QTreeWidget::item { padding: 4px; }"
            "QTreeWidget::item:hover { background-color: rgba(0,0,0,0.04); }"
            "QTreeWidget::item:selected { background-color: rgba(33,150,243,0.15); color: #1A1A1A; }"
            "QHeaderView::section { background-color: transparent; color: #555; font-weight: bold; "
            "padding: 6px; border: none; border-bottom: 1px solid rgba(0,0,0,0.1); }"
            "QScrollBar:vertical { background: transparent; width: 10px; }"
            "QScrollBar::handle:vertical { background: rgba(0,0,0,0.18); border-radius: 5px; min-height: 20px; }"
        )
        layout.addWidget(self.tree)

        # ── Action Buttons ────────────────────────────────────────────────────
        btn_layout = QHBoxLayout()

        self.lbl_selected = QLabel("0 files selected  |  0 B")
        self.lbl_selected.setStyleSheet("color: #777; font-size: 13px;")
        btn_layout.addWidget(self.lbl_selected)
        btn_layout.addStretch()

        btn_select_all = QPushButton("Select All")
        btn_select_all.setStyleSheet(
            "padding: 9px 18px; background-color: #607D8B; color: white; border-radius: 6px; font-weight: bold;"
        )
        btn_select_all.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_select_all.clicked.connect(self._select_all)

        self.btn_delete = QPushButton("🗑  Delete Selected")
        self.btn_delete.setStyleSheet(
            "padding: 9px 18px; background-color: #F44336; color: white; border-radius: 6px; font-weight: bold;"
        )
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setEnabled(False)
        self.btn_delete.clicked.connect(self.delete_selected)

        btn_layout.addWidget(btn_select_all)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)

        # Connect tree changes to update selection count
        self.tree.itemChanged.connect(self._update_selection_label)

    # ── Scan ─────────────────────────────────────────────────────────────────
    def start_scan(self) -> None:
        self.tree.clear()
        self._scan_results.clear()
        self.btn_scan.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self._worker = ScanWorker()
        self._worker.progress.connect(self._on_scan_progress)
        self._worker.scan_complete.connect(self._on_scan_complete)
        self._worker.start()

    def _on_scan_progress(self, percent: int, text: str) -> None:
        self.progress_bar.setValue(percent)
        self.lbl_summary.setText(text)

    def _on_scan_complete(self, results: list[dict[str, Any]]) -> None:
        self._scan_results = results
        self.tree.blockSignals(True)

        total_size = 0
        for r in results:
            size_bytes = r["size_bytes"]
            total_size += size_bytes
            size_str = self._fmt_size(size_bytes)
            risk = r["risk_score"]
            risk_str = "🟢 Low" if risk < 30 else ("🟡 Medium" if risk < 60 else "🔴 High")

            item = QTreeWidgetItem([
                "",
                r["name"],
                r["path"],
                r["category"],
                size_str,
                risk_str,
            ])
            item.setCheckState(0, Qt.CheckState.Unchecked)
            item.setData(0, Qt.ItemDataRole.UserRole, r["full_path"])
            item.setToolTip(1, r["full_path"])
            self.tree.addTopLevelItem(item)

        self.tree.blockSignals(False)
        self.lbl_summary.setText(
            f"Found {len(results)} files  |  Total size: {self._fmt_size(total_size)}"
        )
        self.btn_scan.setEnabled(True)
        self.btn_delete.setEnabled(len(results) > 0)
        self.progress_bar.setVisible(False)
        self._update_selection_label()

    # ── Delete ───────────────────────────────────────────────────────────────
    def delete_selected(self) -> None:
        selected_paths = self._get_checked_paths()
        if not selected_paths:
            QMessageBox.information(self, "Nothing Selected", "Please check at least one file to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Permanently delete {len(selected_paths)} file(s)?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.btn_delete.setEnabled(False)
        self.btn_scan.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self._delete_worker = DeleteWorker(selected_paths)
        self._delete_worker.progress.connect(self._on_delete_progress)
        self._delete_worker.finished.connect(self._on_delete_finished)
        self._delete_worker.start()

    def _on_delete_progress(self, percent: int, text: str) -> None:
        self.progress_bar.setValue(percent)
        self.lbl_summary.setText(text)

    def _on_delete_finished(self, deleted: int, failed: int) -> None:
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)
        msg = f"✅ Deleted {deleted} file(s) successfully."
        if failed:
            msg += f"  ⚠ {failed} file(s) could not be deleted (in use or access denied)."
        QMessageBox.information(self, "Cleanup Complete", msg)
        # Re-scan to refresh the list
        self.start_scan()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _get_checked_paths(self) -> list[str]:
        paths = []
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item and item.checkState(0) == Qt.CheckState.Checked:
                path = item.data(0, Qt.ItemDataRole.UserRole)
                if path:
                    paths.append(path)
        return paths

    def _select_all(self) -> None:
        self.tree.blockSignals(True)
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item:
                item.setCheckState(0, Qt.CheckState.Checked)
        self.tree.blockSignals(False)
        self._update_selection_label()

    def _update_selection_label(self) -> None:
        paths = self._get_checked_paths()
        count = len(paths)
        # Sum sizes from stored results
        total = 0
        for r in self._scan_results:
            if r["full_path"] in paths:
                total += r["size_bytes"]
        self.lbl_selected.setText(f"{count} file(s) selected  |  {self._fmt_size(total)}")
        self.btn_delete.setEnabled(count > 0)

    @staticmethod
    def _fmt_size(size_bytes: int) -> str:
        if size_bytes >= 1024 ** 3:
            return f"{size_bytes / 1024**3:.1f} GB"
        if size_bytes >= 1024 ** 2:
            return f"{size_bytes / 1024**2:.1f} MB"
        if size_bytes >= 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes} B"
