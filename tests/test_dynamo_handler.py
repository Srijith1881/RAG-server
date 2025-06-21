import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from aws_service import dynamo_handler
from unittest.mock import MagicMock, patch

@patch("aws_service.dynamo_handler.table")
def test_save_metadata(mock_table):
    mock_table.put_item = MagicMock()
    dynamo_handler.save_metadata("abc", "file.pdf")
    mock_table.put_item.assert_called_once()

