import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rag_module.metrics_client import send_metrics
from unittest.mock import patch, MagicMock
import pytest

@patch("rag_module.metrics_client.lambda_client")
def test_send_metrics(mock_lambda_client):
    mock_lambda_client.invoke = MagicMock()
    send_metrics("123", 100, 0.9, 2.3)
    mock_lambda_client.invoke.assert_called_once()


@patch("rag_module.metrics_client.lambda_client")
def test_lambda_invoke_fails(mock_lambda_client):
    mock_lambda_client.invoke.side_effect = Exception("Lambda error")
    # Function should handle it internally and not crash
    send_metrics("1", 100, 0.95, 2.0)  # Should print error, not raise
