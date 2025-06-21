# receive metrics from the query API

from fastapi import FastAPI
from pydantic import BaseModel
import boto3
import os
from dotenv import load_dotenv
from decimal import Decimal
from aws_service.aws_client import get_resource

load_dotenv()

app = FastAPI()

class Metric(BaseModel):
    run_id: str
    tokens_used: int
    confidence_score: float
    response_time: float
    file_id: str = "unknown"


dynamodb = get_resource("dynamodb")

@app.post("/metrics")
async def receive_metrics(metric: Metric):
    # Accepts metrics from query response and stores into DynamoDB
    try:
        table = dynamodb.Table("LLM_Metrics")
        
        item = {
            "run_id": metric.run_id,
            "tokens_used": metric.tokens_used,
            "confidence_score": Decimal(str(metric.confidence_score)),
            "response_time": Decimal(str(metric.response_time)),
            "file_id": metric.file_id
        }
        
        table.put_item(Item=item)
        return {"status": "Metric stored."}
    except Exception as e:
        return {"status": "Error", "message": str(e)}