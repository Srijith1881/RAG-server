from fastapi import FastAPI, UploadFile, File, HTTPException, Request
import uuid, os, shutil, traceback
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import fitz

from pdf_services.processor import extract_text
from aws_service.s3_handler import upload_to_s3
from aws_service.dynamo_handler import save_metadata, get_metadata, list_metadata
from rag_module.indexing import index_document

# Rate limiter
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware


# Set up app + limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom rate limit exception
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

import fitz

@app.post("/upload")
@limiter.limit("5/minute")
async def upload_file(request: Request, file: UploadFile = File(...)):
    try:
        # Check file type
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        # Save uploaded file locally
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.pdf"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Check if PDF is encrypted
        doc = fitz.open(file_path)
        if doc.is_encrypted:
            raise HTTPException(status_code=400, detail="Encrypted PDFs are not supported.")

        # Process and store
        upload_to_s3(file_path, filename)
        docs = extract_text(file_path)
        save_metadata(file_id=file_id, filename=file.filename)
        index_document(docs)

        return {"file_id": file_id, "message": "Uploaded and indexed successfully"}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")



@app.get("/retrieve/{file_id}")
@limiter.limit("20/minute")
def retrieve_file_metadata(request: Request, file_id: str):
    #Retrieve metadata for a specific file_id from DynamoDB.
    try:
        metadata = get_metadata(file_id)
        if metadata:
            return metadata
        raise HTTPException(status_code=404, detail="File not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/list")
@limiter.limit("10/minute")
def list_files(request: Request, page: int = 1, limit: int = 10):
    #Paginated list of all uploaded files from DynamoDB.
    try:
        all_items = list_metadata()
        start = (page - 1) * limit
        end = start + limit
        return {
            "total": len(all_items),
            "page": page,
            "limit": limit,
            "files": all_items[start:end]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
