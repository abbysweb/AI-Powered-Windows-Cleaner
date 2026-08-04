from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTreeWidget, QTreeWidgetItem, QLabel, QProgressBar, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, QThread, Signal
from src.scanner.scanner import ScannerOrchestrator
from src.cleaner.cleaner import CleanerOrchestrator
from src.analyzer.analyzer import Analyzer
from src.utils.config import Config, Profile

class ScanWorker(QThread):
    finished_scan = Signal(list)
    
    def run(self):
        orchestrator = ScannerOrchestrator()
        results = orchestrator.scan_all()
        self.finished_scan.emit(results)

class CleanWorker(QThread):
    finished_clean = Signal(list)
    
    def run(self):
        orchestrator = CleanerOrchestrator()
        results = orchestrator.clean_all()
        self.finished_clean.emit(results)

class ScanView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.layout = QVBoxLayout(self)
        
        # Header layout
        header_layout = QHBoxLayout()
        self.header_label = QLabel("Scanner")
        self.header_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        self.profile_combo = QComboBox()
        self.profile_combo.addItems([Profile.QUICK.value, Profile.STANDARD.value, Profile.DEEP.value])
        self.profile_combo.setCurrentText(self.config.profile.value)
        self.profile_combo.currentTextChanged.connect(self.change_profile)
        
        header_layout.addWidget(self.header_label)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Profile:"))
        header_layout.addWidget(self.profile_combo)
        self.layout.addLayout(header_layout)
        
        # Results Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Target", "Size", "Files", "Status"])
        self.tree.setColumnWidth(0, 200)
        self.layout.addWidget(self.tree)
        
        # Summary
        self.summary_label = QLabel("Total Recoverable: 0 B")
        self.summary_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.summary_label.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.summary_label)
        
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.layout.addWidget(self.progress)
        
        # Controls
        controls_layout = QHBoxLayout()
        self.scan_btn = QPushButton("Start Scan")
        self.scan_btn.clicked.connect(self.start_scan)
        
        self.clean_btn = QPushButton("Clean Selected")
        self.clean_btn.clicked.connect(self.start_clean)
        self.clean_btn.setEnabled(False)
        
        controls_layout.addWidget(self.scan_btn)
        controls_layout.addWidget(self.clean_btn)
        self.layout.addLayout(controls_layout)
        
        self.scan_worker = None
        self.clean_worker = None

    def start_scan(self):
        self.scan_btn.setEnabled(False)
        self.clean_btn.setEnabled(False)
        self.tree.clear()
        self.progress.setRange(0, 0)
        
        self.scan_worker = ScanWorker()
        self.scan_worker.finished_scan.connect(self.on_scan_finished)
        self.scan_worker.start()

    def change_profile(self, text):
        self.config.profile = Profile(text)
        self.config.save()
        self.tree.clear()
        self.summary_label.setText("Total Recoverable: 0 B")
        self.clean_btn.setEnabled(False)

    def on_scan_finished(self, results):
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.scan_btn.setEnabled(True)
        
        total_size = 0
        has_cleanable = False
        
        for res in results:
            item = QTreeWidgetItem(self.tree)
            item.setText(0, res.name)
            item.setText(1, Analyzer.format_size(res.size_bytes))
            item.setText(2, str(res.file_count))
            
            if res.error:
                item.setText(3, f"Error: {res.error}")
                item.setForeground(3, Qt.GlobalColor.red)
            else:
                item.setText(3, "Ready to clean")
                item.setForeground(3, Qt.GlobalColor.green)
                if res.size_bytes > 0:
                    has_cleanable = True
                
            total_size += res.size_bytes
            
        self.summary_label.setText(f"Total Recoverable: {Analyzer.format_size(total_size)}")
        if has_cleanable:
            self.clean_btn.setEnabled(True)

    def start_clean(self):
        self.scan_btn.setEnabled(False)
        self.clean_btn.setEnabled(False)
        self.progress.setRange(0, 0)
        self.summary_label.setText("Cleaning in progress...")
        
        self.clean_worker = CleanWorker()
        self.clean_worker.finished_clean.connect(self.on_clean_finished)
        self.clean_worker.start()

    def on_clean_finished(self, results):
        freed = sum(res.space_freed_bytes for res in results)
        deleted = sum(res.files_deleted for res in results)
        
        QMessageBox.information(
            self, "Clean Complete", 
            f"Successfully deleted {deleted} files and freed {Analyzer.format_size(freed)}."
        )
        
        # Re-run scan to update UI
        self.start_scan()
