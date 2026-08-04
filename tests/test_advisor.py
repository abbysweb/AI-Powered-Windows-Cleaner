from unittest.mock import MagicMock, patch

from ai.advisor import AIAdvisor


def test_get_explanation_success():
    advisor = AIAdvisor()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "recommendation": "It is safe because it is a temp file."
    }

    with patch("requests.post", return_value=mock_response):
        explanation = advisor.get_explanation(
            "C:\\temp\\file.txt", "Temp", {"size": 100}
        )
        assert explanation == "It is safe because it is a temp file."


def test_get_explanation_failure():
    advisor = AIAdvisor()
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    with patch("requests.post", return_value=mock_response):
        explanation = advisor.get_explanation(
            "C:\\temp\\file.txt", "Temp", {"size": 100}
        )
        assert explanation == "Could not retrieve AI explanation due to server error."


def test_get_explanation_connection_error():
    import requests

    advisor = AIAdvisor()

    with patch(
        "requests.post",
        side_effect=requests.exceptions.ConnectionError("No connection"),
    ):
        explanation = advisor.get_explanation(
            "C:\\temp\\file.txt", "Temp", {"size": 100}
        )
        assert "Could not connect to AI backend" in explanation


def test_get_risk_assessment():
    advisor = AIAdvisor()
    risk = advisor.get_risk_assessment("C:\\temp\\file.txt")
    assert "risk_score" in risk
    assert risk["risk_score"] == 50
