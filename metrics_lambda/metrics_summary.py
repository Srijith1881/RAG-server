# Exposes a FastAPI endpoint to summarize stored metrics(Total queries,Average response time,Average tokens used)

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key
import os
from aws_service.aws_client import get_resource

load_dotenv()

app = FastAPI()


dynamodb = get_resource("dynamodb")

@app.get("/metrics/summary")
def get_metrics_summary():
    # Returns summary statistics from LLM_Metrics DynamoDB table
    try:
        table = dynamodb.Table("LLM_Metrics")
        response = table.scan()

        items = response.get("Items", [])
        if not items:
            return {
                "total_queries": 0,
                "avg_response_time": 0,
                "avg_tokens_used": 0,
                "notes": "No metrics available yet"
            }

        total_queries = len(items)
        total_tokens = sum(int(item.get("tokens_used", 0)) for item in items)
        total_response_time = sum(float(item.get("response_time", 0)) for item in items)

        avg_tokens = round(total_tokens / total_queries, 2)
        avg_latency = round(total_response_time / total_queries, 2)

        return {
            "total_queries": total_queries,
            "avg_response_time": avg_latency,
            "avg_tokens_used": avg_tokens
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))