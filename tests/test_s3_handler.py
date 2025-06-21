import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from aws_service import s3_handler
import tempfile
import pytest

def test_s3_upload_download(monkeypatch):
    # Mock s3.upload_file and s3.download_file
    monkeypatch.setattr(s3_handler.s3, "upload_file", lambda *args, **kwargs: None)
    monkeypatch.setattr(s3_handler.s3, "download_file", lambda *args, **kwargs: open(args[2], "w").write("test"))

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test")
        f_path = f.name

    s3_handler.upload_to_s3(f_path, "test.pdf")
    out_path = f"{f_path}_out"
    s3_handler.download_from_s3("test.pdf", out_path)
    assert os.path.exists(out_path)

def test_download_nonexistent_file(monkeypatch):
    def mock_download(*args, **kwargs):
        raise FileNotFoundError("No such file")

    monkeypatch.setattr(s3_handler.s3, "download_file", mock_download)

    with pytest.raises(FileNotFoundError):
        s3_handler.download_from_s3("nonexistent.pdf", "out.pdf")
