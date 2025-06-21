import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from pdf_services.main import app as upload_app
from rag_module.main import app as rag_app

@pytest.fixture
def upload_client():
    return TestClient(upload_app)

@pytest.fixture
def rag_client():
    return TestClient(rag_app)
