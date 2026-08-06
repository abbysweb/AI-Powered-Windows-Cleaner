import json
import os
from html import escape
from pathlib import Path

import psutil
import requests
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QTextCursor
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ai_health_copilot.ai.vision import VisionAnalysisService

BACKEND_URL = "http://localhost:8000"
REQUEST_TIMEOUT = int(os.environ.get("AI_BACKEND_TIMEOUT", "300"))
IMAGE_FILE_FILTER = "Images (*.png *.jpg *.jpeg *.webp)"


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


class StreamingWorker(QThread):
    token_received = Signal(str)
    stream_complete = Signal(dict)
    error_received = Signal(str)

    def __init__(self, prompt: str, parent=None):
        super().__init__(parent)
        self.prompt = prompt
        self._cancelled = False
        self._completed = False
        self._response: requests.Response | None = None

    def run(self) -> None:
        try:
            context = collect_system_context()
            enriched_prompt = f"{context}User question: {self.prompt}"

            payload = {
                "messages": [{"role": "user", "content": enriched_prompt}],
                "stream": True,
            }

            res = requests.post(
                f"{BACKEND_URL}/api/chat/stream",
                json=payload,
                timeout=REQUEST_TIMEOUT,
                stream=True,
            )
            res.raise_for_status()
            self._response = res

            for line in res.iter_lines():
                if self._cancelled:
                    break
                if line:
                    decoded_line = line.decode("utf-8")
                    if decoded_line.startswith("data: "):
                        data_str = decoded_line[6:]
                        try:
                            data = json.loads(data_str)
                            if data.get("type") == "token":
                                self.token_received.emit(data.get("content", ""))
                            elif data.get("type") == "complete":
                                self.stream_complete.emit(data)
                                self._completed = True
                        except json.JSONDecodeError:
                            pass

            if not self._completed:
                self.stream_complete.emit(
                    {"done": True, "cancelled": self._cancelled}
                )
        except requests.exceptions.ConnectionError:
            self.error_received.emit(
                f"Could not connect to the AI backend at {BACKEND_URL}. "
                "Is the backend running? (podman-compose up -d --build)"
            )
        except requests.exceptions.Timeout:
            self.error_received.emit(
                f"The AI backend did not respond within {REQUEST_TIMEOUT} seconds. "
                "The model may still be loading (cold start) on slow hardware. "
                "Please wait a moment and try again."
            )
        except requests.exceptions.RequestException as e:
            self.error_received.emit(f"Backend error: {e!s}")

    def cancel(self):
        """Requests cancellation and closes the underlying HTTP stream.

        Safe to call from the main (GUI) thread; it interrupts the worker's
        blocking read so it can finish promptly.
        """
        self._cancelled = True
        if self._response is not None:
            try:
                self._response.close()
            except requests.exceptions.RequestException:  # pragma: no cover
                pass


class VisionWorker(QThread):
    """Runs an image-analysis request off the GUI thread."""

    result_received = Signal(str)
    error_received = Signal(str)

    def __init__(
        self,
        image_path: str | Path,
        prompt: str,
        service: VisionAnalysisService | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.image_path = image_path
        self.prompt = prompt
        self.service = service or VisionAnalysisService()

    def run(self) -> None:
        try:
            data = self.service.analyze_image(self.image_path, self.prompt)
            self.result_received.emit(data.get("analysis", "No analysis returned."))
        except requests.exceptions.ConnectionError:
            self.error_received.emit(
                f"Could not connect to the AI backend at {BACKEND_URL}. "
                "Is the backend running? (podman-compose up -d --build)"
            )
        except requests.exceptions.Timeout:
            self.error_received.emit(
                f"The AI backend did not respond within {REQUEST_TIMEOUT} seconds. "
                "The vision model may still be loading (cold start) on slow hardware. "
                "Please wait a moment and try again."
            )
        except requests.exceptions.RequestException as e:
            self.error_received.emit(f"Backend error: {e!s}")
        except ValueError as e:
            self.error_received.emit(f"Image error: {e!s}")


class AIChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._attached_image_path: Path | None = None
        self._vision_service = VisionAnalysisService()
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

        # Image attachment toolbar + preview
        toolbar = QHBoxLayout()
        self.btn_attach = QPushButton("Attach Image")
        self.btn_attach.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_attach.clicked.connect(self.attach_image)
        toolbar.addWidget(self.btn_attach)

        self.btn_analyze_error = QPushButton("Analyze Error Dialog")
        self.btn_analyze_error.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_analyze_error.clicked.connect(self.analyze_error_dialog)
        toolbar.addWidget(self.btn_analyze_error)

        toolbar.addStretch(1)

        self.preview_label = QLabel()
        self.preview_label.setFixedSize(96, 96)
        self.preview_label.setStyleSheet(
            "border: 1px solid rgba(0, 0, 0, 0.2); border-radius: 6px; background: white;"
        )
        self.preview_label.hide()
        toolbar.addWidget(self.preview_label)

        self.btn_remove_image = QPushButton("✕")
        self.btn_remove_image.setToolTip("Remove attached image")
        self.btn_remove_image.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_remove_image.clicked.connect(self.remove_image)
        self.btn_remove_image.hide()
        toolbar.addWidget(self.btn_remove_image)
        layout.addLayout(toolbar)

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
        if not text and self._attached_image_path is None:
            return

        if self._attached_image_path is not None:
            self._send_vision(self._attached_image_path, text or "Analyze this image.")
            return

        self.input_field.clear()
        self.input_field.setDisabled(True)
        self.btn_send.setDisabled(True)

        self.chat_area.append(f"<br><b>You:</b> {escape(text)}")
        self._thinking_pos = self.chat_area.document().characterCount()
        self.chat_area.append("<i>AI is thinking...</i>")

        self._streaming_worker = StreamingWorker(text)
        self._streaming_worker.token_received.connect(self.handle_token)
        self._streaming_worker.stream_complete.connect(self.handle_stream_complete)
        self._streaming_worker.error_received.connect(self.handle_error)
        self._streaming_worker.start()

    # ── Image analysis ───────────────────────────────────────────────────────
    def attach_image(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select an image to analyze", "", IMAGE_FILE_FILTER
        )
        if file_path:
            self._set_attached_image(Path(file_path))

    def analyze_error_dialog(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select an error dialog screenshot",
            "",
            IMAGE_FILE_FILTER,
        )
        if not file_path:
            return
        self._set_attached_image(Path(file_path))
        self.input_field.setText(
            "Analyze this Windows error dialog screenshot. Identify the error "
            "message, explain what it means, and give step-by-step advice to fix it."
        )

    def _set_attached_image(self, path: Path) -> None:
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            self.chat_area.append(
                f"<br><b style='color: red;'>Error:</b> {escape(str(path))} "
                "is not a readable image."
            )
            return
        self._attached_image_path = path
        self.preview_label.setPixmap(
            pixmap.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )
        self.preview_label.show()
        self.btn_remove_image.show()

    def remove_image(self) -> None:
        self._attached_image_path = None
        self.preview_label.clear()
        self.preview_label.hide()
        self.btn_remove_image.hide()

    def _send_vision(self, path: Path, prompt: str) -> None:
        self.input_field.clear()
        self.input_field.setDisabled(True)
        self.btn_send.setDisabled(True)
        self.chat_area.append(
            f"<br><b>You:</b> [analyzing image] {escape(path.name)} — {escape(prompt)}"
        )
        self._thinking_pos = self.chat_area.document().characterCount()
        self.chat_area.append("<i>AI is analyzing the image...</i>")

        self._vision_worker = VisionWorker(path, prompt, service=self._vision_service)
        self._vision_worker.result_received.connect(self.handle_vision_result)
        self._vision_worker.error_received.connect(self.handle_error)
        self._vision_worker.start()

    def handle_vision_result(self, analysis: str) -> None:
        self._clear_thinking()
        self.chat_area.append("<b>AI Advisor:</b> ")
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(analysis)
        self.chat_area.setTextCursor(cursor)
        self.chat_area.moveCursor(QTextCursor.MoveOperation.End)
        self.chat_area.append("<br>")
        self.remove_image()
        self._enable_input()

    def handle_token(self, token: str) -> None:
        if hasattr(self, "_thinking_pos"):
            self._clear_thinking()
            self.chat_area.append("<b>AI Advisor:</b> ")

        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(token)
        self.chat_area.setTextCursor(cursor)
        self.chat_area.moveCursor(QTextCursor.MoveOperation.End)

    def handle_stream_complete(self, data: dict) -> None:
        self._clear_thinking()
        self.chat_area.append("<br>")
        self._enable_input()

    def handle_error(self, error: str) -> None:
        self._clear_thinking()
        self.chat_area.append(f"<br><b style='color: red;'>Error:</b> {escape(error)}")
        self._enable_input()

    def _clear_thinking(self) -> None:
        if hasattr(self, "_thinking_pos"):
            self._replace_thinking_text()
            delattr(self, "_thinking_pos")

    def _replace_thinking_text(self) -> None:
        cursor = self.chat_area.textCursor()
        cursor.setPosition(getattr(self, "_thinking_pos", 0))
        cursor.movePosition(
            QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor
        )
        cursor.removeSelectedText()
        self.chat_area.setTextCursor(cursor)
        self.chat_area.moveCursor(QTextCursor.MoveOperation.End)

    def _enable_input(self) -> None:
        self.input_field.setDisabled(False)
        self.btn_send.setDisabled(False)
        self.input_field.setFocus()
