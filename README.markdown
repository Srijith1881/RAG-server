                                                                                       # 👋🏻 Hello, this is Srijith

                                                                              # PDF Based RAG (Retrieval-Augmented Generation)

A robust, hybrid RAG backend for PDF querying with a microservice architecture. Seamlessly blending AWS and LocalStack, it features perfectly separated sections, ensuring scalability and maintainability.

## 📋 Table of Contents

- Introduction
- Key Features
- Architecture
- Quick Start
- API Endpoints
- Testing
- RAG Server - Postman API Snippets
- Frontend Repo
- Thank You

## 📝 Introduction

This is production-grade backend of a RAG system designed for intelligent PDF processing, persistent vector storage, and precise domain-specific responses. Its hybrid nature supports AWS and LocalStack, driven by a microservice architecture with robust error handling and modular design. Built to scale, it’s interview-ready and constraint-respecting.

## 🌟 Key Features You Can’t Ignore

- 📦 **Persistent Chroma Vector Store**: Documents chunked and embedded at upload, stored persistently—no reprocessing per query.
- 🧠 **Per-Document Query Logging (Audit Trail)**: Stores query text, LLM response, confidence, and file ID in DynamoDB.
- 🚦 **Rate Limiting**: Per-IP limits with slowapi to prevent abuse and stabilize traffic.
- 📈 **Metrics Logging to AWS Lambda**: Logs tokens, confidence, and latency asynchronously into LLM_Metrics.
- 📊 **/metrics/summary API**: Delivers total queries, avg response time, and usage trends from DynamoDB.
- 📄 **/query-log/export API**: Exports full logs as CSV/JSON for audits or analysis.
- 📂 **/list with Pagination**: Lists PDFs with pagination (e.g., `/list?page=1&limit=10`).
- 🔐 **PDF Type & Encryption Guardrail**: Rejects non-PDFs, encrypted, or corrupt files with clear errors.
- 🧪 **Full Unit Testing Suite**: Covers all modules with pytest, including edge cases.
- 🚧 **Graceful Error Logging**: Uses `traceback.print_exc()` and detailed `HTTPException` messages.
- 🔁 **Query Reusability**: Leverages stored vectors for simultaneous multi-PDF queries.

## 🏗️ Architecture

A microservice architecture with:

- **PDF Service**: Manages uploads and text extraction.
- **RAG Module**: Handles indexing and querying.
- **AWS Service**: Interfaces with S3 and DynamoDB.
- **Metrics & Logs**: Tracks and exports metrics/logs.
- **Hybrid Toggle**: `USE_LOCALSTACK=true` switches between AWS and LocalStack.

## 🚀 Quick Start

### Prerequisites

- Docker Desktop, Python 3.10+
- API Key (see API Key Guide)
- AWS credentials (for cloud deployment)

### Commands for Localstack Implementation:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
# Configure AWS CLI (see below)
docker-compose -f docker-compose.yml up -d
docker ps
curl http://localhost:4566/health  # For LocalStack verification, optional
uvicorn pdf_services.main:app --host 0.0.0.0 --port 8001 --reload
uvicorn rag_module.main:app --host 0.0.0.0 --port 8002 --reload
uvicorn aws_service.router:app --host 0.0.0.0 --port 8003 --reload
uvicorn metrics_lambda.metrics_summary:app --host 0.0.0.0 --port 8004 --reload
uvicorn metrics_lambda.query_log_api:app --host 0.0.0.0 --port 8005 --reload
python -m scripts.deploy_lambda
python -m scripts.setup_aws  # Updated script for AWS
python -m scripts.verify_aws  # Updated script for AWS
```

### Environment Variables

```plaintext
#For localstack
GOOGLE_API_KEY=<google-api>
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
REGION=us-east-1
UPLOAD_LIMIT=5/minute
QUERY_LIMIT=20/minute
BUCKET_NAME=pdf-storage-local
USE_LOCALSTACK=true

#For AWS
GOOGLE_API_KEY=<google-api>
AWS_ACCESS_KEY_ID=<access-id>
AWS_SECRET_ACCESS_KEY=<secret-key>
REGION=<region>
UPLOAD_LIMIT=5/minute
QUERY_LIMIT=20/minute
BUCKET_NAME=<s3 bucket name>
USE_LOCALSTACK=false
```

### Commands for AWS Implementation:

### AWS CLI Configuration

1. **Install AWS CLI**:

   - Follow AWS CLI Installation Guide.

2. **Configure Credentials**:

   ```bash
   aws configure
   ```

   - Enter `AWS Access Key ID`, `AWS Secret Access Key`, `Region` (e.g., `ap-south-1`), and `Output Format` (e.g., `json`).

3. **Verify Credentials**:

   ```bash
   aws sts get-caller-identity
   ```

   - Expect a JSON response with your account details.

### Create DynamoDB Tables

```bash
aws dynamodb create-table \
  --table-name PDF_Metadata \
  --attribute-definitions AttributeName=file_id,AttributeType=S \
  --key-schema AttributeName=file_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region ap-south-1

aws dynamodb create-table \
  --table-name LLM_Metrics \
  --attribute-definitions AttributeName=run_id,AttributeType=S \
  --key-schema AttributeName=run_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region ap-south-1

aws dynamodb create-table \
  --table-name QueryLog \
  --attribute-definitions AttributeName=file_id,AttributeType=S \
  --key-schema AttributeName=file_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region ap-south-1

# Verify Tables
aws dynamodb scan --table-name PDF_Metadata --region ap-south-1
aws dynamodb scan --table-name LLM_Metrics --region ap-south-1
aws dynamodb scan --table-name QueryLog --region ap-south-1
```

### Setup Lambda Function

1. **Build ZIP**:

   ```bash
   cd metrics_lambda
   mkdir -p lambda_build
   cp handler.py lambda_build/
   pip install -r requirements.txt -t lambda_build/
   cd lambda_build && zip -r9 ../lambda.zip . && cd ..
   rm -rf lambda_build
   ```

2. **Upload Lambda**:

   ```bash
   aws lambda update-function-code \
     --function-name logMetricsFunction \
     --zip-file fileb://lambda.zip \
     --region ap-south-1
   ```

### IAM Policy for User

Attach this policy to your IAM user:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:GetItem",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:ap-south-1:<account-id>:table/LLM_Metrics"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

Replace `<account-id>` with your AWS account ID.

## 📡 API Endpoints

| Method | API Endpoint | Query Example | Response Example |
| --- | --- | --- | --- |
| POST | `/upload` | `curl -X POST -F "file=@sample.pdf" http://localhost:8001/upload` | `{"file_id": "uuid", "message": "Uploaded"}` |
| GET | `/retrieve/{file_id}` | `curl http://localhost:8001/retrieve/uuid` | `{"file_id": "uuid", "filename": "sample.pdf"}` |
| GET | `/list` | `curl "http://localhost:8001/list?page=1&limit=10"` | `{"total": 2, "files": [...]}` |
| POST | `/query` | `curl -X POST -d '{"query": "Topic?"}' http://localhost:8002/query` | `{"run_id": "uuid", "reply": "Topic is..."}` |
| POST | `/metrics` | `curl -X POST -d '{"run_id": "uuid", "tokens": 150,"confidence_score":"0.92"}' http://localhost:8003/metrics` | `{"status": "Metric stored"}` |
| GET | `/metrics/summary` | `curl http://localhost:8004/metrics/summary` | `{"total_queries": 10, "avg_response_time": 1.25}` |
| GET | `/query-log` | `curl "http://localhost:8005/query-log?limit=5"` | `[{"run_id": "uuid", "query_text": "..."}]` |
| GET | `/query-log/{file_id}` | `curl http://localhost:8005/query-log/uuid` | `[{"run_id": "uuid", "query_text": "..."}]` |
| GET | `/query-log/export` | `curl "http://localhost:8005/query-log/export?format=csv"` | `CSV file download` |

## 🧪 Testing

- **Why Test?**: Ensures reliability with a comprehensive pytest suite.

- **Modules Tested**:

  | Module | Tested (AWS & Localstack) ✅ |
  | --- | --- |
  | `/upload` endpoint | ✅ |
  | PDF text extraction | ✅ |
  | Vector embedding + persistence | ✅ |
  | `/query` endpoint | ✅ |
  | S3 & DynamoDB handlers | ✅ |
  | Lambda invocation | ✅ |
  | Bad file uploads / inputs | ✅ |
  | Local FastAPI servers | ✅ |

- **Run Tests**: `pip install -r tests/requirements.txt` then `pytest tests/`

## 💻 RAG Server - Postman API Snippets

| **Section** | **Details** |
| --- | --- |
| **Base URLs** | \- PDF Services: http://localhost:8001<br>- RAG Module: http://localhost:8002<br>- AWS Service: http://localhost:8003<br>- Metrics Summary: http://localhost:8004<br>- Query Log API: http://localhost:8005 |
| **PDF Services (8001)** | 1\. **Upload PDF**: POST /upload (Form-data: file)<br>2. **Retrieve Metadata**: GET /retrieve/{file_id}<br>3. **List Files**: GET /list?page=1&limit=10 |
| **RAG Module (8002)** | 4\. **Query Docs**: POST /query (JSON: {"query": "Question", "file_key": "uuid"}) |
| **AWS Service (8003)** | 5\. **Receive Metrics**: POST /metrics (JSON: {"run_id","tokens_used","confidence score","responsetime","file_id"}) |
| **Metrics Summary (8004)** | 6\. **Get Summary**: GET /metrics/summary |
| **Query Log API (8005)** | 7\. **Get Logs**: GET /query-log?limit=10<br>8. **Get File Logs**: GET /query-log/{file_id}<br>9. **Export Logs**: GET /query-log/export?format=csv |
| **Example Requests** | \- Upload: POST /upload with file=@document.pdf<br>- Query: POST /query with {"query": "Topic?"}<br>- Metrics: POST /metrics with {"run_id": "uuid", ...} |
| **Rate Limits** | \- Upload: 5/min<br>- Retrieve: 20/min<br>- List: 10/min<br>- Query: 10/min |
| **Response Formats** | \- Success: {"status": "success", "data": {...}}<br>- Error: {"detail": "Error message"}<br>- Rate Limit: {"detail": "Rate limit exceeded"} |
| **Notes** | \- CORS: allow_origins=\["\*"\]<br>- Only PDFs accepted<br>- No encrypted PDFs<br>- Timestamps in ISO format |

## 🌐 Frontend Repo

https://github.com/Srijith1881/pdf-rag-client

steps:

     -git clone

     -npm i

     -npm run dev

## **☎️CONTACT**

<u>srijithvy@gmail.com</u>

## 🙏 Thank You

Thanks for the opportunity! Happy coding ❤️
