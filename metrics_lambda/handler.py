'''AWS Lambda handler to receive and store LLM query metrics
into the LLM_Metrics DynamoDB table. Expects a JSON payload
with keys like run_id, tokens_used, confidence_score'''

import boto3
import os
import json
from decimal import Decimal
from dotenv import load_dotenv
import botocore.exceptions
from aws_service.aws_client import get_resource

load_dotenv()
dynamodb = get_resource("dynamodb")


def lambda_handler(event, context):
    # stores the extracted metric into DynamoDB table
    try:
        table = dynamodb.Table("LLM_Metrics")

        # Parse input from API Gateway or Lambda test event
        body = event.get("body")
        if isinstance(body, str):
            body = json.loads(body)

        item = {
            "run_id": body["run_id"],
            "tokens_used": body["tokens_used"],
            "confidence_score": Decimal(str(body["confidence_score"])),
            "response_time": Decimal(str(body["response_time"])),
            "file_id": body.get("file_id", "unknown")
        }

        table.put_item(Item=item)
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "Metric stored."})
        }

    except botocore.exceptions.ClientError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"DynamoDB error: {str(e)}"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Unexpected error: {str(e)}"})
        }
