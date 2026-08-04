import logging
from datetime import datetime
from pathlib import Path

# Setup basic logging
LOG_DIR = Path.cwd() / "logs"
LOG_DIR.mkdir(exist_ok=True)

log_file = LOG_DIR / f"cleaner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("WindowsCleaner")
