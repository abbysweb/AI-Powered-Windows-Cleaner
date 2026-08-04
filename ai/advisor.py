import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


class AIAdvisor:
    def __init__(self, endpoint_url: str = "http://localhost:8000"):
        self.endpoint_url = endpoint_url

    def get_explanation(
        self, file_path: str, cleaner_type: str, context: dict[str, Any]
    ) -> str:
        """
        Sends context to the AI backend and retrieves a natural language explanation
        of why a file/folder is safe or unsafe to delete.
        """
        payload = {
            "prompt": f"Explain why it is safe or unsafe to delete this file: {file_path}. Context: {context}"
        }
        try:
            response = requests.post(
                f"{self.endpoint_url}/api/advisor", json=payload, timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("recommendation", "No explanation provided by AI.")
            else:
                logger.error(
                    f"AI Backend returned status {response.status_code}: {response.text}"
                )
                return "Could not retrieve AI explanation due to server error."
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to AI Backend at {self.endpoint_url}: {e}")
            return "Could not connect to AI backend. Is the Podman container running?"

    def get_risk_assessment(self, file_path: str) -> dict[str, Any]:
        """
        Requests a risk assessment for a particular file.
        """
        # Placeholder for future dynamic risk assessment endpoint
        return {"risk_score": 50, "reason": "Default fallback risk score."}
