from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class AIChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header = QLabel("AI Health Advisor")
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #1A1A1A;")
        layout.addWidget(header)

        # Chat Area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet(
            "QTextEdit { background-color: rgba(255, 255, 255, 0.6); color: #333333; border: 1px solid rgba(0, 0, 0, 0.1); border-radius: 8px; padding: 10px; font-size: 14px; }"
            "QScrollBar:vertical { background: transparent; width: 10px; }"
            "QScrollBar::handle:vertical { background: rgba(0, 0, 0, 0.2); border-radius: 5px; min-height: 20px; }"
        )
        self.chat_area.append(
            "<b>AI Advisor:</b> Hello! I'm your Windows Health Copilot. I can explain any cleanup recommendations or system health issues. How can I help you today?"
        )
        layout.addWidget(self.chat_area)

        # Input Area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask about your system health...")
        self.input_field.setStyleSheet(
            "QLineEdit { background-color: rgba(255, 255, 255, 0.7); color: #1A1A1A; border: 1px solid rgba(0, 0, 0, 0.1); border-bottom: 2px solid #2196F3; border-radius: 8px; padding: 10px 15px; font-size: 14px; }"
            "QLineEdit:focus { background-color: rgba(255, 255, 255, 0.9); }"
        )

        btn_send = QPushButton("Send")
        btn_send.setStyleSheet(
            "padding: 10px 20px; background-color: #2196F3; color: white; border-radius: 20px; font-weight: bold;"
        )

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(btn_send)
        layout.addLayout(input_layout)
