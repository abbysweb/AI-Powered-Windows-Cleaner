from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTreeWidget, QTreeWidgetItem, QLabel, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from pathlib import Path
from src.ai.large_files import LargeFileAnalyzer
from src.ai.duplicates import DuplicateFinder
from src.ai.startup import StartupAnalyzer

class AIWorker(QThread):
    finished_analysis = Signal(list, list, list)

    def run(self):
        target_dirs = [
            Path.home() / "Downloads",
            Path.home() / "Documents"
        ]
        
        large_files = LargeFileAnalyzer(target_dirs).analyze()
        duplicates = DuplicateFinder(target_dirs).analyze()
        startup = StartupAnalyzer().analyze()
        
        self.finished_analysis.emit(large_files, duplicates, startup)

class AiOptimizerView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.header_label = QLabel("AI PC Optimizer")
        self.header_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.header_label)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Recommendation", "Type", "Details"])
        self.tree.setColumnWidth(0, 350)
        self.tree.setColumnWidth(1, 150)
        self.layout.addWidget(self.tree)
        
        bottom_layout = QHBoxLayout()
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        
        self.analyze_btn = QPushButton("Run Smart Analysis")
        self.analyze_btn.setMinimumHeight(40)
        self.analyze_btn.setStyleSheet("background-color: #6a0dad; color: white; font-weight: bold;")
        self.analyze_btn.clicked.connect(self.start_analysis)
        
        bottom_layout.addWidget(self.progress)
        bottom_layout.addWidget(self.analyze_btn)
        self.layout.addLayout(bottom_layout)
        
    def start_analysis(self):
        self.tree.clear()
        self.analyze_btn.setEnabled(False)
        self.progress.setRange(0, 0)
        
        self.worker = AIWorker()
        self.worker.finished_analysis.connect(self.on_analysis_finished)
        self.worker.start()
        
    def on_analysis_finished(self, large_files, duplicates, startup):
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.analyze_btn.setEnabled(True)
        
        startup_root = QTreeWidgetItem(self.tree, ["Startup Impact Analysis", "", ""])
        for item in startup:
            child = QTreeWidgetItem(startup_root, [item["name"], item["type"], f"Impact: {item['impact']} | {item['command']}"])
            if item['impact'] == 'High':
                child.setForeground(2, Qt.red)
        startup_root.setExpanded(True)
        
        large_root = QTreeWidgetItem(self.tree, ["Large Files (>500MB)", "", ""])
        for item in large_files:
            mb = item["size"] / (1024*1024)
            QTreeWidgetItem(large_root, [Path(item["path"]).name, item["type"], f"{mb:.2f} MB | {item['path']}"])
        large_root.setExpanded(True)
        
        dup_root = QTreeWidgetItem(self.tree, ["Duplicate Files", "", ""])
        for item in duplicates:
            mb = item["size"] / (1024*1024)
            QTreeWidgetItem(dup_root, [Path(item["path"]).name, item["type"], f"{mb:.2f} MB | Orig: {item['original']}"])
        dup_root.setExpanded(True)
