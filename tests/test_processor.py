import sys
import os
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pdf_services.processor import extract_text

def test_text_extraction_valid_pdf():
    path = r"C:\Users\LEGION\OneDrive\Desktop\Apple_fruit_company.pdf"
    docs = extract_text(path)
    assert len(docs) > 0
    assert hasattr(docs[0], "page_content")

def test_invalid_pdf_extraction():
    with pytest.raises(RuntimeError):
        extract_text("tests/not_a_pdf.txt")

