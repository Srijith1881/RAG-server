# Send metrices for either AWS lambda or Localstack

import boto3
import json
import os
import requests
from dotenv import load_dotenv
from aws_service.aws_client import get_client

load_dotenv()

lambda_client = get_client("lambda")

def send_metrics(run_id, tokens_used, confidence, response_time, file_id="unknown"):
    payload = {
        "run_id": run_id,
        "tokens_used": tokens_used,
        "confidence_score": confidence,
        "response_time": response_time,
        "file_id": file_id
    }
    try:
        response = lambda_client.invoke(
            FunctionName="logMetricsFunction",
            InvocationType="Event",
            Payload=json.dumps(payload)
        )
        print("✅ Metrics sent to AWS Lambda.")
    except Exception as e:
        print(f"❌ Failed to send metrics to AWS Lambda: {e}")
