import psutil
import requests
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


def collect_system_context() -> str:
    """Collect real-time system metrics and return as a formatted string."""
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count(logical=True)
    ram = psutil.virtual_memory()
    ram_total_gb = ram.total / (1024**3)
    ram_used_gb = ram.used / (1024**3)
    ram_percent = ram.percent

    disk_lines = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            disk_lines.append(
                f"  {part.device}: {usage.used / (1024**3):.1f}GB used "
                f"/ {usage.total / (1024**3):.1f}GB total ({usage.percent}%)"
            )
        except (PermissionError, OSError):
            continue

    disks_summary = "\n".join(disk_lines) if disk_lines else "  No disk info available"

    return (
        f"[LIVE SYSTEM METRICS]\n"
        f"CPU Usage: {cpu_percent}% ({cpu_count} logical cores)\n"
        f"RAM Usage: {ram_used_gb:.1f}GB / {ram_total_gb:.1f}GB ({ram_percent}%)\n"
        f"Disk Usage:\n{disks_summary}\n"
        f"[END METRICS]\n\n"
    )


class ChatThread(QThread):
    response_received = Signal(str)
    error_received = Signal(str)

    def __init__(self, prompt: str, parent=None):
        super().__init__(parent)
        self.prompt = prompt

    def run(self) -> None:
        try:
            # Collect real system metrics and prepend to the user prompt
            context = collect_system_context()
            enriched_prompt = f"{context}User question: {self.prompt}"

            res = requests.post(
                "http://localhost:8000/api/advisor",
                json={"prompt": enriched_prompt},
                timeout=60,
            )
            res.raise_for_status()
            data = res.json()
            self.response_received.emit(data.get("recommendation", "No response."))
        except requests.exceptions.RequestException as e:
            self.error_received.emit(f"Backend error: {e!s}")


class AIChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
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
            "QTextEdit { background-color: rgba(255, 255, 255, 0.6); color: #333333; "
            "border: 1px solid rgba(0, 0, 0, 0.1); border-radius: 8px; padding: 10px; font-size: 14px; }"
            "QScrollBar:vertical { background: transparent; width: 10px; }"
            "QScrollBar::handle:vertical { background: rgba(0, 0, 0, 0.2); border-radius: 5px; min-height: 20px; }"
        )
        self.chat_area.append(
            "<b>AI Advisor:</b> Hello! I'm your Windows Health Copilot. "
            "I have access to your live CPU, RAM and disk metrics. "
            "Ask me anything about your system — I'll give you real, data-driven advice!"
        )
        layout.addWidget(self.chat_area)

        # Input Area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask about your system health...")
        self.input_field.setStyleSheet(
            "QLineEdit { background-color: rgba(255, 255, 255, 0.7); color: #1A1A1A; "
            "border: 1px solid rgba(0, 0, 0, 0.1); border-bottom: 2px solid #2196F3; "
            "border-radius: 8px; padding: 10px 15px; font-size: 14px; }"
            "QLineEdit:focus { background-color: rgba(255, 255, 255, 0.9); }"
        )
        self.input_field.returnPressed.connect(self.send_message)

        self.btn_send = QPushButton("Send")
        self.btn_send.setStyleSheet(
            "padding: 10px 20px; background-color: #2196F3; color: white; "
            "border-radius: 20px; font-weight: bold;"
        )
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.btn_send)
        layout.addLayout(input_layout)

    def send_message(self) -> None:
        text = self.input_field.text().strip()
        if not text:
            return

        self.input_field.clear()
        self.input_field.setDisabled(True)
        self.btn_send.setDisabled(True)

        self.chat_area.append(f"<br><b>You:</b> {text}")
        self.chat_area.append("<i>AI is thinking...</i>")

        self._chat_thread = ChatThread(text)
        self._chat_thread.response_received.connect(self.handle_response)
        self._chat_thread.error_received.connect(self.handle_error)
        self._chat_thread.start()

    def handle_response(self, text: str) -> None:
        self._replace_thinking_text()
        self.chat_area.append(f"<b>AI Advisor:</b> {text}")
        self._enable_input()

    def handle_error(self, error: str) -> None:
        self._replace_thinking_text()
        self.chat_area.append(f"<b style='color: red;'>Error:</b> {error}")
        self._enable_input()

    def _replace_thinking_text(self) -> None:
        html = self.chat_area.toHtml()
        html = html.replace("<i>AI is thinking...</i>", "")
        self.chat_area.setHtml(html)
        self.chat_area.moveCursor(self.chat_area.textCursor().MoveOperation.End)

    def _enable_input(self) -> None:
        self.input_field.setDisabled(False)
        self.btn_send.setDisabled(False)
        self.input_field.setFocus()
