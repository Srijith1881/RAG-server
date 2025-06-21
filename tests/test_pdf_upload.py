import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_upload_endpoint(upload_client):
    test_file_path = r"C:\Users\LEGION\OneDrive\Desktop\Apple_fruit_company.pdf"
    with open(test_file_path, "rb") as f:
        response = upload_client.post("/upload", files={"file": ("sample.pdf", f, "application/pdf")})
    assert response.status_code == 200
    assert "file_id" in response.json()

def test_upload_with_no_file(upload_client):
    response = upload_client.post("/upload")
    assert response.status_code == 422  # FastAPI validation error

def test_upload_with_wrong_file_type(upload_client):
    response = upload_client.post("/upload", files={"file": ("not_a_pdf.txt", "text data", "text/plain")})
    assert response.status_code in [400, 422]
