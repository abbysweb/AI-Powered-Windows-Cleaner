from pathlib import Path

# Fix downloads.py risk score override
dl = Path("src/ai_health_copilot/core/cleaner/downloads.py")
dl_content = dl.read_text(encoding="utf-8")
dl_content = dl_content.replace(
    "self._risk_score: int = 80  # High risk - user files\n        super().__init__(quarantine_manager)",
    "super().__init__(quarantine_manager)\n        self._risk_score = 80  # High risk - user files"
)
dl.write_text(dl_content, encoding="utf-8")

# Fix test_main.py
tm = Path("tests/test_main.py")
tm_content = tm.read_text(encoding="utf-8")
tm_content = tm_content.replace(
    "with patch(\"sys.exit\") as mock_exit:",
    "with patch(\"sys.exit\") as mock_exit:\n        with patch(\"ai_health_copilot.main.QApplication\") as mock_app:"
)
tm_content = tm_content.replace(
    "try:\n                main()\n            except RuntimeError:\n                pass # Ignore PySide6 QApplication singleton error in tests\n            mock_exit.assert_called_once_with(0)",
    "main()\n            mock_exit.assert_called_once_with(0)"
)
tm.write_text(tm_content, encoding="utf-8")
