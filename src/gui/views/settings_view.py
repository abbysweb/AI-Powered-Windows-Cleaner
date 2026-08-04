from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QComboBox, QLineEdit, QListWidget, QMessageBox, QGroupBox
)
from src.utils.config import Config, Profile
from src.scheduler.scheduler import Scheduler
from src.utils.paths import is_admin

class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        self.layout = QVBoxLayout(self)
        
        self.header = QLabel("Settings & Automation")
        self.header.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.header)
        
        # Filters Group
        self.filter_group = QGroupBox("Age Filters")
        filter_layout = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Disable (Clean everything)", "Older than 7 days", "Older than 30 days", "Older than 90 days"])
        
        if self.config.max_age_days == 7:
            self.filter_combo.setCurrentIndex(1)
        elif self.config.max_age_days == 30:
            self.filter_combo.setCurrentIndex(2)
        elif self.config.max_age_days == 90:
            self.filter_combo.setCurrentIndex(3)
            
        self.filter_combo.currentIndexChanged.connect(self.save_config)
        filter_layout.addWidget(QLabel("Only delete files:"))
        filter_layout.addWidget(self.filter_combo)
        self.filter_group.setLayout(filter_layout)
        self.layout.addWidget(self.filter_group)
        
        # Exclusions Group
        self.exc_group = QGroupBox("Exclusions (e.g., .pdf, important_file.txt)")
        exc_layout = QVBoxLayout()
        self.exc_list = QListWidget()
        self.exc_list.addItems(self.config.exclusions)
        
        add_layout = QHBoxLayout()
        self.exc_input = QLineEdit()
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_exclusion)
        self.del_btn = QPushButton("Remove Selected")
        self.del_btn.clicked.connect(self.remove_exclusion)
        
        add_layout.addWidget(self.exc_input)
        add_layout.addWidget(self.add_btn)
        
        exc_layout.addWidget(self.exc_list)
        exc_layout.addLayout(add_layout)
        exc_layout.addWidget(self.del_btn)
        self.exc_group.setLayout(exc_layout)
        self.layout.addWidget(self.exc_group)
        
        # Scheduler Group
        self.sch_group = QGroupBox("Automation")
        sch_layout = QHBoxLayout()
        
        if not is_admin():
            sch_layout.addWidget(QLabel("Administrator privileges required for scheduling."))
        else:
            self.sch_combo = QComboBox()
            self.sch_combo.addItems(["DAILY", "WEEKLY", "ONSTART"])
            self.sch_btn = QPushButton("Create Task")
            self.sch_btn.clicked.connect(self.create_task)
            self.del_sch_btn = QPushButton("Remove Task")
            self.del_sch_btn.clicked.connect(self.delete_task)
            
            sch_layout.addWidget(QLabel("Schedule:"))
            sch_layout.addWidget(self.sch_combo)
            sch_layout.addWidget(self.sch_btn)
            sch_layout.addWidget(self.del_sch_btn)
            
        self.sch_group.setLayout(sch_layout)
        self.layout.addWidget(self.sch_group)
        
    def add_exclusion(self):
        text = self.exc_input.text().strip()
        if text and text not in self.config.exclusions:
            self.config.exclusions.append(text)
            self.exc_list.addItem(text)
            self.exc_input.clear()
            self.config.save()
            
    def remove_exclusion(self):
        item = self.exc_list.currentItem()
        if item:
            text = item.text()
            self.config.exclusions.remove(text)
            self.exc_list.takeItem(self.exc_list.row(item))
            self.config.save()

    def save_config(self):
        idx = self.filter_combo.currentIndex()
        if idx == 0: self.config.max_age_days = 0
        elif idx == 1: self.config.max_age_days = 7
        elif idx == 2: self.config.max_age_days = 30
        elif idx == 3: self.config.max_age_days = 90
        self.config.save()

    def create_task(self):
        freq = self.sch_combo.currentText()
        if Scheduler.create_task(freq):
            QMessageBox.information(self, "Success", f"Task scheduled for {freq}.")
        else:
            QMessageBox.critical(self, "Error", "Failed to schedule task.")
            
    def delete_task(self):
        if Scheduler.delete_task():
            QMessageBox.information(self, "Success", "Scheduled task removed.")
