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
        header.setStyleSheet("font-size: 28px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(header)

        # Chat Area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet(
            "QTextEdit { background-color: #242424; color: #E0E0E0; border: 1px solid #333333; border-radius: 8px; padding: 10px; font-size: 14px; }"
        )
        self.chat_area.append("<b>AI Advisor:</b> Hello! I'm your Windows Health Copilot. I can explain any cleanup recommendations or system health issues. How can I help you today?")
        layout.addWidget(self.chat_area)

        # Input Area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask about your system health...")
        self.input_field.setStyleSheet(
            "QLineEdit { background-color: #1A1A1A; color: #FFFFFF; border: 1px solid #333333; border-radius: 20px; padding: 10px 15px; font-size: 14px; }"
        )
        
        btn_send = QPushButton("Send")
        btn_send.setStyleSheet("padding: 10px 20px; background-color: #2196F3; color: white; border-radius: 20px; font-weight: bold;")
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(btn_send)
        layout.addLayout(input_layout)
