import sys
import os
import pytest
import shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag_module.indexing import index_document
from pdf_services.processor import extract_text

def test_vectorstore_persistence():
    path = r"C:\Users\LEGION\OneDrive\Desktop\Apple_fruit_company.pdf"
    docs = extract_text(path)
    index_document(docs)

    persist_dir = "./chroma_db"
    persisted_files = os.listdir(persist_dir)
    assert len(persisted_files) > 0

